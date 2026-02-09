"""SQLModel ORM models for the requests table."""

import enum
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel

try:
    from sqlalchemy.dialects.postgresql import JSON as PG_JSON
    from sqlalchemy import JSON
except ImportError:
    from sqlalchemy import JSON

    PG_JSON = JSON


class RequestType(str, enum.Enum):
    humanize = "humanize"
    detect = "detect"


class RequestStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class RequestRecord(SQLModel, table=True):
    __tablename__ = "requests"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    request_type: str = Field(..., max_length=20)
    input_text: str = Field(sa_column=Column(Text, nullable=False))
    output_text: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    detector_results: dict[str, Any] | None = Field(
        default=None, sa_column=Column(JSON, nullable=True)
    )
    status: str = Field(default=RequestStatus.pending.value, max_length=20)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    processing_time_ms: int | None = Field(default=None)
