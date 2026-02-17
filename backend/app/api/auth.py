"""Authentication API endpoints (Google OAuth + session management)."""

import structlog
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.config import settings
from app.db.session import get_session
from app.db.user_crud import (
    create_google_user,
    get_user_by_google_id,
    update_google_user,
)
from app.models.user import User
from app.services.auth import (
    create_access_token,
    exchange_google_code,
    verify_google_id_token,
)

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
