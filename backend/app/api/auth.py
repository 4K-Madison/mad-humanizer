"""Authentication API endpoints (Google OAuth + email/password + session management)."""

import re
from datetime import datetime, timedelta, timezone

import structlog
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.config import settings
from app.db.session import get_session
from app.db.user_crud import (
    create_email_user,
    create_google_user,
    get_user_by_email,
    get_user_by_google_id,
    update_google_user,
)
from app.db.verification_crud import (
    create_verification,
    get_valid_verification,
    invalidate_existing_codes,
    mark_verification_used,
)
from app.models.user import User
from app.models.verification import EmailVerification
from app.services.auth import (
    create_access_token,
    exchange_google_code,
    generate_verification_code,
    hash_password,
    verify_google_id_token,
    verify_password,
)
from app.services.email import send_verification_email

logger = structlog.get_logger()

router = APIRouter(prefix="/auth", tags=["Auth"])


# --- Schemas ---


class GoogleLoginRequest(BaseModel):
    code: str
    code_verifier: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: str | None
    picture_url: str | None
    auth_provider: str


class EmailSignupRequest(BaseModel):
    email: str
    password: str
    name: str | None = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid email format")
        return v.lower().strip()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class VerifyCodeRequest(BaseModel):
    email: str
    code: str

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        if not re.match(r"^\d{6}$", v):
            raise ValueError("Code must be 6 digits")
        return v


class EmailLoginRequest(BaseModel):
    email: str
    password: str


class ResendCodeRequest(BaseModel):
    email: str


# --- Endpoints ---


@router.post("/google/login")
async def google_login(
    body: GoogleLoginRequest,
    response: Response,
    session: AsyncSession = Depends(get_session),
):
    """Exchange Google authorization code for session."""
    # 1. Exchange code for tokens
    try:
        token_data = await exchange_google_code(body.code, body.code_verifier)
    except Exception as exc:
        logger.error("Google code exchange failed", error=str(exc))
        raise HTTPException(
            status_code=400, detail="Failed to exchange authorization code"
        )

    # 2. Verify the ID token
    try:
        id_info = verify_google_id_token(token_data["id_token"])
    except Exception as exc:
        logger.error("Google ID token verification failed", error=str(exc))
        raise HTTPException(status_code=400, detail="Invalid Google ID token")

    # 3. Extract user info
    google_id = id_info["sub"]
    email = id_info["email"]
    name = id_info.get("name")
    picture = id_info.get("picture")

    # 4. Find or create user
    user = await get_user_by_google_id(session, google_id)
    if user:
        user = await update_google_user(session, user, name, picture)
        logger.info("Existing user logged in", user_id=str(user.id), email=email)
    else:
        user = await create_google_user(session, email, name, picture, google_id)
        logger.info("New user created via Google", user_id=str(user.id), email=email)

    # 5. Create JWT and set httpOnly cookie
    access_token = create_access_token(str(user.id), user.email)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # Set True in production (HTTPS)
        samesite="lax",
        max_age=settings.JWT_EXPIRATION_MINUTES * 60,
        path="/",
    )

    return {
        "user": UserResponse(
            id=str(user.id),
            email=user.email,
            name=user.name,
            picture_url=user.picture_url,
            auth_provider=user.auth_provider,
        ),
        "message": "Login successful",
    }


@router.post("/email/signup")
async def email_signup(
    body: EmailSignupRequest,
    session: AsyncSession = Depends(get_session),
):
    """Initiate email signup — sends verification code."""
    # 1. Check if email already in use
    existing_user = await get_user_by_email(session, body.email)
    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists",
        )

    # 2. Invalidate any previous pending codes for this email
    await invalidate_existing_codes(session, body.email)

    # 3. Hash password and generate code
    hashed_pw = hash_password(body.password)
    code = generate_verification_code()
    expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(
        minutes=settings.VERIFICATION_CODE_EXPIRY_MINUTES
    )

    # 4. Store verification record
    await create_verification(
        session,
        email=body.email,
        code=code,
        hashed_password=hashed_pw,
        name=body.name,
        expires_at=expires_at,
    )

    # 5. Send verification email
    sent = await send_verification_email(body.email, code)
    if not sent:
        raise HTTPException(
            status_code=503,
            detail="Failed to send verification email. Please try again.",
        )

    logger.info("Verification code sent", email=body.email)
    return {"message": "Verification code sent to your email"}


@router.post("/email/verify")
async def verify_email_code(
    body: VerifyCodeRequest,
    response: Response,
    session: AsyncSession = Depends(get_session),
):
    """Verify email code and create the account."""
    # 1. Find valid verification
    verification = await get_valid_verification(session, body.email, body.code)
    if not verification:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired verification code",
        )

    # 2. Double-check email isn't taken (race condition guard)
    existing_user = await get_user_by_email(session, body.email)
    if existing_user:
        await mark_verification_used(session, verification)
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists",
        )

    # 3. Create user
    user = await create_email_user(
        session,
        email=verification.email,
        hashed_password=verification.hashed_password,
        name=verification.name,
    )

    # 4. Mark code as used
    await mark_verification_used(session, verification)

    # 5. Auto-login: create JWT + set cookie
    access_token = create_access_token(str(user.id), user.email)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.JWT_EXPIRATION_MINUTES * 60,
        path="/",
    )

    logger.info("Email user created and verified", user_id=str(user.id), email=user.email)
    return {
        "user": UserResponse(
            id=str(user.id),
            email=user.email,
            name=user.name,
            picture_url=user.picture_url,
            auth_provider=user.auth_provider,
        ),
        "message": "Account created successfully",
    }


@router.post("/email/login")
async def email_login(
    body: EmailLoginRequest,
    response: Response,
    session: AsyncSession = Depends(get_session),
):
    """Log in with email + password."""
    user = await get_user_by_email(session, body.email)
    if not user or not user.hashed_password:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    access_token = create_access_token(str(user.id), user.email)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.JWT_EXPIRATION_MINUTES * 60,
        path="/",
    )

    logger.info("Email user logged in", user_id=str(user.id), email=user.email)
    return {
        "user": UserResponse(
            id=str(user.id),
            email=user.email,
            name=user.name,
            picture_url=user.picture_url,
            auth_provider=user.auth_provider,
        ),
        "message": "Login successful",
    }


@router.post("/email/resend")
async def resend_verification_code(
    body: ResendCodeRequest,
    session: AsyncSession = Depends(get_session),
):
    """Resend a verification code (invalidates previous codes)."""
    existing_user = await get_user_by_email(session, body.email)
    if existing_user:
        raise HTTPException(status_code=409, detail="Account already exists")

    result = await session.execute(
        select(EmailVerification)
        .where(EmailVerification.email == body.email)
        .order_by(EmailVerification.created_at.desc())
        .limit(1)
    )
    last_verification = result.scalar_one_or_none()
    if not last_verification:
        raise HTTPException(
            status_code=400, detail="No pending signup found. Please sign up again."
        )

    await invalidate_existing_codes(session, body.email)
    code = generate_verification_code()
    expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(
        minutes=settings.VERIFICATION_CODE_EXPIRY_MINUTES
    )
    await create_verification(
        session,
        email=body.email,
        code=code,
        hashed_password=last_verification.hashed_password,
        name=last_verification.name,
        expires_at=expires_at,
    )

    sent = await send_verification_email(body.email, code)
    if not sent:
        raise HTTPException(status_code=503, detail="Failed to send email")

    return {"message": "New verification code sent"}


@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return UserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        picture_url=user.picture_url,
        auth_provider=user.auth_provider,
    )


@router.post("/logout")
async def logout(response: Response):
    """Clear the JWT cookie to log the user out."""
    response.delete_cookie(key="access_token", path="/")
    return {"message": "Logged out"}
