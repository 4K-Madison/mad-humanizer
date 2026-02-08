from fastapi import APIRouter, Request

from app.models.schemas import HumanizeRequest, HumanizeResponse

router = APIRouter()


@router.post("/humanize", response_model=HumanizeResponse)
async def humanize_text(request: Request, body: HumanizeRequest):
    # Will be implemented in Plan 03 (Model Integration)
    raise NotImplementedError("Humanizer service not yet integrated")
