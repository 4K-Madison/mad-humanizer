from fastapi import APIRouter, Request

from app.models.schemas import DetectRequest, DetectResponse

router = APIRouter()


@router.post("/detect", response_model=DetectResponse)
async def detect_text(request: Request, body: DetectRequest):
    # Will be implemented in Plan 04 (Detector Integration)
    raise NotImplementedError("Detector service not yet integrated")
