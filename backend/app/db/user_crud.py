"""CRUD operations for the users table."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_google_id(session: AsyncSession, google_id: str) -> User | None:
    result = await session.execute(select(User).where(User.google_id == google_id))
    return result.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, user_id: str) -> User | None:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_google_user(
    session: AsyncSession,
    email: str,
    name: str | None,
    picture_url: str | None,
    google_id: str,
) -> User:
    user = User(
        email=email,
        name=name,
        picture_url=picture_url,
        google_id=google_id,
        auth_provider="google",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def create_email_user(
    session: AsyncSession,
    email: str,
    hashed_password: str,
    name: str | None = None,
) -> User:
    """Create a new user with email + password credentials."""
    user = User(
        email=email,
        hashed_password=hashed_password,
        name=name,
        auth_provider="email",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_google_user(
    session: AsyncSession,
    user: User,
    name: str | None,
    picture_url: str | None,
) -> User:
    if name:
        user.name = name
    if picture_url:
        user.picture_url = picture_url
    user.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def link_google_to_user(
    session: AsyncSession,
    user: User,
    google_id: str,
    name: str | None,
    picture_url: str | None,
) -> User:
    """Link a Google account to an existing email/password user."""
    user.google_id = google_id
    user.auth_provider = "both"
    if not user.picture_url and picture_url:
        user.picture_url = picture_url
    if not user.name and name:
        user.name = name
    user.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
