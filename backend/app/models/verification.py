"""SQLModel ORM model for email verification codes."""

import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class EmailVerification(SQLModel, table=True):
    __tablename__ = "email_verifications"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(max_length=255, index=True)
    code: str = Field(max_length=6)
    hashed_password: str = Field(max_length=255)
    name: str | None = Field(default=None, max_length=255)
    is_used: bool = Field(default=False)
    expires_at: datetime = Field()
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
