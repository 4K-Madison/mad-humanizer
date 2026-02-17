"""FastAPI dependencies for authentication."""

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.db.user_crud import get_user_by_id
from app.models.user import User
from app.services.auth import verify_access_token


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> User:
    """Extract and verify JWT from httpOnly cookie. Raises 401 if invalid."""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = verify_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = await get_user_by_id(session, payload["sub"])
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    return user


async def get_optional_user(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> User | None:
    """Same as get_current_user but returns None instead of raising 401."""
    token = request.cookies.get("access_token")
    if not token:
        return None

    payload = verify_access_token(token)
    if payload is None:
        return None

    return await get_user_by_id(session, payload["sub"])
