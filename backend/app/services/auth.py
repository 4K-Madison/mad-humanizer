"""Google OAuth token exchange and JWT management."""

import secrets
from datetime import datetime, timedelta, timezone

import httpx
import structlog
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logger = structlog.get_logger()


# --- Google OAuth ---


async def exchange_google_code(code: str, code_verifier: str) -> dict:
    """Exchange authorization code + PKCE verifier for Google tokens."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "code": code,
                "code_verifier": code_verifier,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
        response.raise_for_status()
        return response.json()


def verify_google_id_token(token: str) -> dict:
    """Verify and decode the Google ID token. Returns user info claims."""
    return google_id_token.verify_oauth2_token(
        token,
        google_requests.Request(),
        settings.GOOGLE_CLIENT_ID,
    )


# --- JWT ---


def create_access_token(user_id: str, email: str) -> str:
    """Create a short-lived JWT access token (1 hour)."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRY_MINUTES
    )
    payload = {
        "sub": user_id,
        "email": email,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token_value() -> str:
    """Generate a cryptographically random refresh token string (not a JWT)."""
    return secrets.token_urlsafe(48)


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def generate_verification_code() -> str:
    """Generate a 6-digit numeric verification code."""
    return f"{secrets.randbelow(900000) + 100000}"


def verify_access_token(token: str) -> dict | None:
    """Verify and decode a JWT access token. Returns payload or None."""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None
