import time

import httpx
import structlog
from fastapi import APIRouter, HTTPException, Request

from app.config import settings
from app.models.schemas import HumanizeRequest, HumanizeResponse
from app.services.humanize_loop import (
    humanize_single,
    humanize_with_detector_gate,
)

logger = structlog.get_logger()

router = APIRouter()


@router.post("/humanize", response_model=HumanizeResponse)
async def humanize_text(request: Request, body: HumanizeRequest):
    humanizer = request.app.state.humanizer

    if humanizer is None or not humanizer.is_loaded:
        raise HTTPException(status_code=503, detail="Humanizer model is not available")

    options = body.options
    temperature = options.temperature if options else settings.TEMPERATURE
    max_tokens = options.max_tokens if options else settings.MAX_OUTPUT_TOKENS
    enable_gate = options.enable_detector_gate if options else True
    max_attempts = (
        options.max_attempts
        if options and options.max_attempts is not None
        else settings.HUMANIZE_MAX_ATTEMPTS
    )

    registry = getattr(request.app.state, "detector_registry", None)

    start = time.perf_counter()
    try:
        if not enable_gate or registry is None:
            loop_result = await humanize_single(
                humanizer=humanizer,
                text=body.text,
                temperature=temperature,
                max_tokens=max_tokens,
                threshold=settings.HUMANIZE_AI_SCORE_THRESHOLD,
            )
        else:
            async with httpx.AsyncClient() as http_client:
                loop_result = await humanize_with_detector_gate(
                    humanizer=humanizer,
                    registry=registry,
                    http_client=http_client,
                    text=body.text,
                    base_temperature=temperature,
                    max_tokens=max_tokens,
                    max_attempts=max_attempts,
                    threshold=settings.HUMANIZE_AI_SCORE_THRESHOLD,
                    detector_name=settings.HUMANIZE_DETECTOR_NAME,
                    temp_bump_per_retry=settings.HUMANIZE_TEMP_BUMP_PER_RETRY,
                    detector_timeout_seconds=settings.HUMANIZE_DETECTOR_TIMEOUT_SECONDS,
                )
    except Exception as exc:
        logger.error("Model inference failed", error=str(exc))
        raise HTTPException(
            status_code=503, detail="Model inference failed"
        ) from exc

    processing_time_ms = int((time.perf_counter() - start) * 1000)

    try:
        from app.db.crud import create_request
        from app.db.session import async_session_factory
        from app.models.database import RequestStatus, RequestType

        async with async_session_factory() as session:
            await create_request(
                session,
                request_type=RequestType.humanize,
                input_text=body.text,
                output_text=loop_result.humanized_text,
                status=RequestStatus.completed,
                processing_time_ms=processing_time_ms,
                ai_score=loop_result.ai_score,
                attempts_count=len(loop_result.attempts),
                threshold_met=loop_result.threshold_met,
            )
    except Exception as db_exc:
        logger.warning("Failed to log humanization to DB", error=str(db_exc))

    return HumanizeResponse(
        humanized_text=loop_result.humanized_text,
        input_length=len(body.text),
        output_length=len(loop_result.humanized_text),
        processing_time_ms=processing_time_ms,
        ai_score=loop_result.ai_score,
        threshold_met=loop_result.threshold_met,
        attempts=loop_result.attempts,
        threshold=loop_result.threshold,
        warning=loop_result.warning,
    )
