import time

import structlog
from fastapi import APIRouter, HTTPException, Request

from app.models.schemas import HumanizeRequest, HumanizeResponse

logger = structlog.get_logger()

router = APIRouter()


@router.post("/humanize", response_model=HumanizeResponse)
async def humanize_text(request: Request, body: HumanizeRequest):
    humanizer = request.app.state.humanizer

    if not humanizer.is_loaded:
        raise HTTPException(status_code=503, detail="Humanizer model is not available")

    options = body.options
    temperature = options.temperature if options else 0.7
    max_tokens = options.max_tokens if options else 2048

    start = time.perf_counter()
    try:
        humanized_text = humanizer.humanize(
            text=body.text,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    except Exception as exc:
        logger.error("Model inference failed", error=str(exc))
        raise HTTPException(
            status_code=503, detail="Model inference failed"
        ) from exc

    processing_time_ms = int((time.perf_counter() - start) * 1000)

    # Best-effort DB logging — don't let DB errors block the response
    try:
        from app.db.crud import create_request
        from app.db.session import async_session_factory
        from app.models.database import RequestStatus, RequestType

        async with async_session_factory() as session:
            await create_request(
                session,
                request_type=RequestType.humanize,
                input_text=body.text,
                output_text=humanized_text,
                status=RequestStatus.completed,
                processing_time_ms=processing_time_ms,
            )
    except Exception as db_exc:
        logger.warning("Failed to log humanization to DB", error=str(db_exc))

    return HumanizeResponse(
        humanized_text=humanized_text,
        input_length=len(body.text),
        output_length=len(humanized_text),
        processing_time_ms=processing_time_ms,
    )
