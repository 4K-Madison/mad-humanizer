import structlog
import httpx

from app.config import settings
from app.models.schemas import DetectorResult
from app.services.detectors.base import BaseDetector

logger = structlog.get_logger()

GPTZERO_API_URL = "https://api.gptzero.me/v2/predict/text"


class GPTZeroDetector(BaseDetector):
    name = "gptzero"
    display_name = "GPTZero"
    description = "GPTZero AI content detector"

    def is_available(self) -> bool:
        return bool(settings.GPTZERO_API_KEY)

    async def detect(self, client: httpx.AsyncClient, text: str) -> DetectorResult:
        try:
            response = await client.post(
                GPTZERO_API_URL,
                headers={
                    "x-api-key": settings.GPTZERO_API_KEY,
                    "Content-Type": "application/json",
                },
                json={"document": text},
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()

            score = data["documents"][0]["completely_generated_prob"]
            label = "ai" if score > 0.5 else "human"

            return DetectorResult(
                detector=self.name,
                score=round(score, 4),
                label=label,
                details={
                    "completely_generated_prob": score,
                    "class_probabilities": data["documents"][0].get("class_probabilities"),
                },
                error=None,
            )
        except httpx.HTTPStatusError as exc:
            logger.error("GPTZero API error", status=exc.response.status_code)
            return DetectorResult(
                detector=self.name,
                score=None,
                label=None,
                details=None,
                error=f"GPTZero API returned {exc.response.status_code}",
            )
        except Exception as exc:
            logger.error("GPTZero detection failed", error=str(exc))
            return DetectorResult(
                detector=self.name,
                score=None,
                label=None,
                details=None,
                error=f"GPTZero detection failed: {str(exc)}",
            )
