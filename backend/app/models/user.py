"""SQLModel ORM model for the users table."""

import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True)
    name: str | None = Field(default=None, max_length=255)
    picture_url: str | None = Field(default=None, max_length=1024)
    google_id: str | None = Field(default=None, max_length=255, unique=True, index=True)
    hashed_password: str | None = Field(default=None, max_length=255)
    auth_provider: str = Field(default="google", max_length=20)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
