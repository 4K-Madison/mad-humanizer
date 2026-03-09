import structlog
from fastapi import APIRouter, Request

from app.models.schemas import DetectorInfo, DetectorListResponse, HealthResponse

logger = structlog.get_logger()

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    registry = getattr(request.app.state, "detector_registry", None)
    detectors_available = len(registry.get_available()) if registry else 0

    # Check vLLM server connectivity
    humanizer = getattr(request.app.state, "humanizer", None)
    model_loaded = False
    if humanizer and humanizer.client:
        try:
            resp = await humanizer.client.get("/v1/models")
            resp.raise_for_status()
            model_loaded = True
        except Exception as exc:
            logger.warning("vLLM health check failed", error=str(exc))
            model_loaded = False

    return HealthResponse(
        status="healthy",
        model_loaded=model_loaded,
        database_connected=getattr(request.app.state, "database_connected", False),
        detectors_available=detectors_available,
    )


@router.get("/detectors", response_model=DetectorListResponse)
async def list_detectors(request: Request):
    registry = getattr(request.app.state, "detector_registry", None)
    if registry is None:
        return DetectorListResponse(detectors=[])

    detectors = [
        DetectorInfo(
            name=d.name,
            display_name=d.display_name,
            available=d.is_available(),
            description=d.description,
        )
        for d in registry.get_all()
    ]
    return DetectorListResponse(detectors=detectors)
