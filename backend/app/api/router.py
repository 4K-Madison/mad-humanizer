from fastapi import APIRouter

from app.api import detect, health, humanize

api_router = APIRouter()

api_router.include_router(humanize.router, tags=["Humanize"])
api_router.include_router(detect.router, tags=["Detect"])
api_router.include_router(health.router, tags=["Health"])
