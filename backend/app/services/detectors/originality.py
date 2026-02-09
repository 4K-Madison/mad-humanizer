import structlog
import httpx

from app.config import settings
from app.models.schemas import DetectorResult
from app.services.detectors.base import BaseDetector

logger = structlog.get_logger()

ORIGINALITY_API_URL = "https://api.originality.ai/api/v1/scan/ai"


class OriginalityDetector(BaseDetector):
    name = "originality"
    display_name = "Originality.ai"
    description = "Originality.ai AI content detector"

    def is_available(self) -> bool:
        return bool(settings.ORIGINALITY_API_KEY)

    async def detect(self, client: httpx.AsyncClient, text: str) -> DetectorResult:
        try:
            response = await client.post(
                ORIGINALITY_API_URL,
                headers={
                    "X-OAI-API-KEY": settings.ORIGINALITY_API_KEY,
                    "Content-Type": "application/json",
                },
                json={"content": text},
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()

            score = data["score"]["ai"]
            label = "ai" if score > 0.5 else "human"

            return DetectorResult(
                detector=self.name,
                score=round(score, 4),
                label=label,
                details={
                    "ai_score": score,
                    "original_score": data["score"].get("original"),
                },
                error=None,
            )
        except httpx.HTTPStatusError as exc:
            logger.error("Originality API error", status=exc.response.status_code)
            return DetectorResult(
                detector=self.name,
                score=None,
                label=None,
                details=None,
                error=f"Originality API returned {exc.response.status_code}",
            )
        except Exception as exc:
            logger.error("Originality detection failed", error=str(exc))
            return DetectorResult(
                detector=self.name,
                score=None,
                label=None,
                details=None,
                error=f"Originality detection failed: {str(exc)}",
            )
