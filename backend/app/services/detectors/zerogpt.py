import httpx
import structlog

from app.config import settings
from app.models.schemas import DetectorResult
from app.services.detectors.base import BaseDetector

logger = structlog.get_logger()

ZEROGPT_API_URL = "https://api.zerogpt.com/api/detect/detectText"


class ZeroGPTDetector(BaseDetector):
    name = "zerogpt"
    display_name = "ZeroGPT"
    description = "ZeroGPT AI content detector"

    def is_available(self) -> bool:
        return bool(settings.ZEROGPT_API_KEY)

    async def detect(self, client: httpx.AsyncClient, text: str) -> DetectorResult:
        try:
            response = await client.post(
                ZEROGPT_API_URL,
                headers={
                    "ApiKey": settings.ZEROGPT_API_KEY,
                    "Content-Type": "application/json",
                },
                json={"input_text": text},
                timeout=30.0,
            )
            response.raise_for_status()
            payload = response.json()

            data = payload.get("data") if isinstance(payload, dict) else None
            if not isinstance(data, dict):
                return DetectorResult(
                    detector=self.name,
                    score=None,
                    label=None,
                    details=None,
                    error="ZeroGPT returned unexpected response shape",
                )

            fake_pct = data.get("fakePercentage")
            if fake_pct is None:
                return DetectorResult(
                    detector=self.name,
                    score=None,
                    label=None,
                    details=data,
                    error="ZeroGPT response missing 'fakePercentage'",
                )

            score = round(float(fake_pct) / 100.0, 4)
            label = "ai" if score > 0.5 else "human"

            return DetectorResult(
                detector=self.name,
                score=score,
                label=label,
                details={
                    "fakePercentage": fake_pct,
                    "isHuman": data.get("isHuman"),
                    "textWords": data.get("textWords"),
                    "aiWords": data.get("aiWords"),
                    "feedback": data.get("feedback"),
                },
                error=None,
            )
        except httpx.HTTPStatusError as exc:
            logger.error("ZeroGPT API error", status=exc.response.status_code)
            return DetectorResult(
                detector=self.name,
                score=None,
                label=None,
                details=None,
                error=f"ZeroGPT API returned {exc.response.status_code}",
            )
        except Exception as exc:
            logger.error("ZeroGPT detection failed", error=str(exc))
            return DetectorResult(
                detector=self.name,
                score=None,
                label=None,
                details=None,
                error=f"ZeroGPT detection failed: {str(exc)}",
            )
