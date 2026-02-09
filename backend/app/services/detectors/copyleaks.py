import structlog
import httpx

from app.config import settings
from app.models.schemas import DetectorResult
from app.services.detectors.base import BaseDetector

logger = structlog.get_logger()

COPYLEAKS_AUTH_URL = "https://id.copyleaks.com/v3/account/login/api"
COPYLEAKS_SCAN_URL = "https://api.copyleaks.com/v2/writer-detector/{scan_id}/check"


class CopyleaksDetector(BaseDetector):
    name = "copyleaks"
    display_name = "Copyleaks"
    description = "Copyleaks AI content detector"

    def is_available(self) -> bool:
        return bool(settings.COPYLEAKS_API_KEY)

    async def _authenticate(self, client: httpx.AsyncClient) -> str:
        """Authenticate with Copyleaks and return an access token."""
        # COPYLEAKS_API_KEY is expected as "email:api_key"
        parts = settings.COPYLEAKS_API_KEY.split(":", 1)
        if len(parts) != 2:
            raise ValueError("COPYLEAKS_API_KEY must be in format 'email:api_key'")
        email, api_key = parts

        response = await client.post(
            COPYLEAKS_AUTH_URL,
            json={"email": email, "key": api_key},
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        return data["access_token"]

    async def detect(self, client: httpx.AsyncClient, text: str) -> DetectorResult:
        try:
            access_token = await self._authenticate(client)

            # Use a unique scan ID based on text hash
            import hashlib
            scan_id = hashlib.sha256(text.encode()).hexdigest()[:16]

            scan_url = COPYLEAKS_SCAN_URL.format(scan_id=scan_id)
            response = await client.post(
                scan_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                json={"text": text},
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()

            # Copyleaks returns a summary with AI probability
            score = data.get("summary", {}).get("ai", 0.0)
            label = "ai" if score > 0.5 else "human"

            return DetectorResult(
                detector=self.name,
                score=round(score, 4),
                label=label,
                details={
                    "summary": data.get("summary"),
                },
                error=None,
            )
        except httpx.HTTPStatusError as exc:
            logger.error("Copyleaks API error", status=exc.response.status_code)
            return DetectorResult(
                detector=self.name,
                score=None,
                label=None,
                details=None,
                error=f"Copyleaks API returned {exc.response.status_code}",
            )
        except Exception as exc:
            logger.error("Copyleaks detection failed", error=str(exc))
            return DetectorResult(
                detector=self.name,
                score=None,
                label=None,
                details=None,
                error=f"Copyleaks detection failed: {str(exc)}",
            )
