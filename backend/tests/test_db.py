"""Unit tests for the database layer using async SQLite in-memory."""

import uuid

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.db.crud import create_request, get_request, list_requests
from app.models.database import RequestRecord, RequestStatus, RequestType


@pytest_asyncio.fixture()
async def session():
    """Create an in-memory SQLite async engine and yield a session."""
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as s:
        yield s

    await engine.dispose()


@pytest.mark.asyncio
async def test_create_humanize_request(session: AsyncSession):
    record = await create_request(
        session,
        request_type=RequestType.humanize,
        input_text="AI generated text here",
        output_text="Humanized text here",
        status=RequestStatus.completed,
        processing_time_ms=150,
    )
    assert record.id is not None
    assert record.request_type == "humanize"
    assert record.input_text == "AI generated text here"
    assert record.output_text == "Humanized text here"
    assert record.status == "completed"
    assert record.processing_time_ms == 150
    assert record.created_at is not None


@pytest.mark.asyncio
async def test_create_detect_request(session: AsyncSession):
    results = {"gptzero": {"score": 0.95, "label": "ai"}}
    record = await create_request(
        session,
        request_type=RequestType.detect,
        input_text="Check this text",
        detector_results=results,
        status=RequestStatus.completed,
        processing_time_ms=300,
    )
    assert record.request_type == "detect"
    assert record.detector_results == results
    assert record.output_text is None


@pytest.mark.asyncio
async def test_get_request(session: AsyncSession):
    record = await create_request(
        session,
        request_type=RequestType.humanize,
        input_text="Some input",
    )
    fetched = await get_request(session, record.id)
    assert fetched is not None
    assert fetched.id == record.id
    assert fetched.input_text == "Some input"
    assert fetched.status == "pending"


@pytest.mark.asyncio
async def test_get_not_found(session: AsyncSession):
    result = await get_request(session, uuid.uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_list_requests(session: AsyncSession):
    for i in range(3):
        await create_request(
            session,
            request_type=RequestType.humanize,
            input_text=f"Text {i}",
        )
    records = await list_requests(session)
    assert len(records) == 3


@pytest.mark.asyncio
async def test_list_filter_by_type(session: AsyncSession):
    await create_request(
        session, request_type=RequestType.humanize, input_text="h1"
    )
    await create_request(
        session, request_type=RequestType.humanize, input_text="h2"
    )
    await create_request(
        session, request_type=RequestType.detect, input_text="d1"
    )

    humanize_only = await list_requests(session, request_type=RequestType.humanize)
    assert len(humanize_only) == 2

    detect_only = await list_requests(session, request_type=RequestType.detect)
    assert len(detect_only) == 1


@pytest.mark.asyncio
async def test_list_pagination(session: AsyncSession):
    for i in range(5):
        await create_request(
            session,
            request_type=RequestType.humanize,
            input_text=f"Text {i}",
        )

    page1 = await list_requests(session, limit=2, offset=0)
    assert len(page1) == 2

    page2 = await list_requests(session, limit=2, offset=2)
    assert len(page2) == 2

    page3 = await list_requests(session, limit=2, offset=4)
    assert len(page3) == 1
