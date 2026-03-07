"""CRUD operations for email verification codes."""

from datetime import datetime, timezone

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.verification import EmailVerification


async def create_verification(
    session: AsyncSession,
    email: str,
    code: str,
    hashed_password: str,
    name: str | None,
    expires_at: datetime,
) -> EmailVerification:
    """Create a new verification code record."""
    verification = EmailVerification(
        email=email,
        code=code,
        hashed_password=hashed_password,
        name=name,
        expires_at=expires_at,
    )
    session.add(verification)
    await session.commit()
    await session.refresh(verification)
    return verification


async def get_valid_verification(
    session: AsyncSession, email: str, code: str
) -> EmailVerification | None:
    """Find an unused, non-expired verification code for the given email."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    result = await session.execute(
        select(EmailVerification).where(
            and_(
                EmailVerification.email == email,
                EmailVerification.code == code,
                EmailVerification.is_used == False,
                EmailVerification.expires_at > now,
            )
        )
    )
    return result.scalar_one_or_none()


async def mark_verification_used(
    session: AsyncSession, verification: EmailVerification
) -> None:
    """Mark a verification code as used."""
    verification.is_used = True
    session.add(verification)
    await session.commit()


async def invalidate_existing_codes(
    session: AsyncSession, email: str
) -> None:
    """Mark all existing unused codes for an email as used (prevents reuse)."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    result = await session.execute(
        select(EmailVerification).where(
            and_(
                EmailVerification.email == email,
                EmailVerification.is_used == False,
                EmailVerification.expires_at > now,
            )
        )
    )
    for v in result.scalars().all():
        v.is_used = True
        session.add(v)
    await session.commit()
