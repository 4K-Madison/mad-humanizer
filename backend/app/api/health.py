from fastapi import APIRouter, Request

from app.models.schemas import DetectorListResponse, HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    return HealthResponse(
        status="healthy",
        model_loaded=False,  # Updated in Plan 03
        database_connected=False,  # Updated in Plan 02
        detectors_available=0,  # Updated in Plan 04
    )


@router.get("/detectors", response_model=DetectorListResponse)
async def list_detectors(request: Request):
    return DetectorListResponse(detectors=[])
