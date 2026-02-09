"""CRUD operations for the requests table."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.database import RequestRecord, RequestStatus, RequestType


async def create_request(
    session: AsyncSession,
    *,
    request_type: RequestType,
    input_text: str,
    output_text: str | None = None,
    detector_results: dict | None = None,
    status: RequestStatus = RequestStatus.pending,
    processing_time_ms: int | None = None,
) -> RequestRecord:
    """Insert a new request record and return it."""
    record = RequestRecord(
        request_type=request_type.value,
        input_text=input_text,
        output_text=output_text,
        detector_results=detector_results,
        status=status.value,
        processing_time_ms=processing_time_ms,
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record


async def get_request(
    session: AsyncSession,
    request_id: uuid.UUID,
) -> RequestRecord | None:
    """Fetch a single request by ID, or None if not found."""
    return await session.get(RequestRecord, request_id)


async def list_requests(
    session: AsyncSession,
    *,
    request_type: RequestType | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[RequestRecord]:
    """List request records with optional type filter and pagination."""
    stmt = select(RequestRecord)
    if request_type is not None:
        stmt = stmt.where(RequestRecord.request_type == request_type.value)
    stmt = stmt.order_by(RequestRecord.created_at.desc()).offset(offset).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())
