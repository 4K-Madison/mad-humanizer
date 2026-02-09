import asyncio
import time

import httpx
import structlog
from fastapi import APIRouter, HTTPException, Request

from app.models.schemas import DetectRequest, DetectResponse, DetectorResult

router = APIRouter()
logger = structlog.get_logger()


@router.post("/detect", response_model=DetectResponse)
async def detect_text(request: Request, body: DetectRequest):
    registry = getattr(request.app.state, "detector_registry", None)
    if registry is None:
        raise HTTPException(status_code=503, detail="Detector registry not initialized")

    # Determine which detectors to run
    if body.detectors:
        detectors = []
        for name in body.detectors:
            detector = registry.get(name)
            if detector is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unknown detector: {name}",
                )
            if not detector.is_available():
                raise HTTPException(
                    status_code=400,
                    detail=f"Detector not available: {name}",
                )
            detectors.append(detector)
    else:
        detectors = registry.get_available()

    if not detectors:
        raise HTTPException(
            status_code=400,
            detail="No detectors available. Configure at least one detector API key.",
        )

    start = time.perf_counter()

    async with httpx.AsyncClient() as client:
        tasks = [detector.detect(client, body.text) for detector in detectors]
        raw_results = await asyncio.gather(*tasks, return_exceptions=True)

    # Partial success: convert exceptions to per-detector error results
    results: list[DetectorResult] = []
    for detector, result in zip(detectors, raw_results):
        if isinstance(result, Exception):
            logger.error(
                "Detector raised unexpected exception",
                detector=detector.name,
                error=str(result),
            )
            results.append(
                DetectorResult(
                    detector=detector.name,
                    score=None,
                    label=None,
                    details=None,
                    error=f"Unexpected error: {str(result)}",
                )
            )
        else:
            results.append(result)

    elapsed_ms = int((time.perf_counter() - start) * 1000)

    # TODO: Save detection request/results to database (Plan 02 DB integration)

    return DetectResponse(results=results, processing_time_ms=elapsed_ms)
