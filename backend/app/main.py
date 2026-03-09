from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.config import settings
from app.logging_config import setup_logging

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(debug=settings.DEBUG)
    logger.info("Starting MAD-HUMANIZER", debug=settings.DEBUG)

    # Database
    from app.db.session import init_db, close_db

    await init_db()
    app.state.database_connected = True
    logger.info("Database initialized")

    # Humanizer (vLLM remote inference)
    if settings.HUMANIZER_API_URL:
        try:
            from app.services.humanizer import HumanizerService

            app.state.humanizer = HumanizerService(
                base_url=settings.HUMANIZER_API_URL,
                model_name=settings.HUMANIZER_MODEL_NAME,
                api_key=settings.HUMANIZER_API_KEY,
            )
            await app.state.humanizer.connect()
            app.state.model_loaded = app.state.humanizer.is_loaded
            logger.info("Humanizer service initialized", available=app.state.model_loaded)
        except Exception as exc:
            logger.warning("Failed to connect to humanizer service", error=str(exc))
            app.state.humanizer = None
            app.state.model_loaded = False
    else:
        logger.warning("HUMANIZER_API_URL not set — humanizer disabled")
        app.state.humanizer = None
        app.state.model_loaded = False

    # Detector registry
    from app.services.detectors.registry import DetectorRegistry

    app.state.detector_registry = DetectorRegistry.register_defaults()
    logger.info(
        "Detector registry initialized",
        available=len(app.state.detector_registry.get_available()),
    )

    yield

    # Shutdown
    if getattr(app.state, "humanizer", None):
        await app.state.humanizer.disconnect()

    await close_db()
    logger.info("Database connection closed")
    logger.info("Shutting down MAD-HUMANIZER")


app = FastAPI(
    title="MAD-HUMANIZER API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception", exc_info=exc, path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Include API routes
app.include_router(api_router, prefix="/api")
