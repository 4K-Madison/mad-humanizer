from fastapi import APIRouter, Request

from app.models.schemas import DetectorInfo, DetectorListResponse, HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    registry = getattr(request.app.state, "detector_registry", None)
    detectors_available = len(registry.get_available()) if registry else 0

    return HealthResponse(
        status="healthy",
        model_loaded=getattr(request.app.state, "model_loaded", False),
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
