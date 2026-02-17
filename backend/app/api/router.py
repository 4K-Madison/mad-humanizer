from fastapi import APIRouter

from app.api import auth, detect, health, humanize

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(humanize.router, tags=["Humanize"])
api_router.include_router(detect.router, tags=["Detect"])
api_router.include_router(health.router, tags=["Health"])
