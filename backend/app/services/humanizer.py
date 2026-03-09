import httpx
import structlog

from app.config import settings

logger = structlog.get_logger()


class HumanizerService:
    def __init__(self, base_url: str, model_name: str, api_key: str = ""):
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self.api_key = api_key
        self.client: httpx.AsyncClient | None = None
        self._available = False

    @property
    def is_loaded(self) -> bool:
        return self._available

    async def connect(self):
        """Initialize HTTP client and verify vLLM server is reachable."""
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=httpx.Timeout(120.0, connect=10.0),
        )

        try:
            resp = await self.client.get("/v1/models")
            resp.raise_for_status()
            models = resp.json()
            available_models = [m["id"] for m in models.get("data", [])]
            logger.info("vLLM server connected", available_models=available_models)

            if self.model_name not in available_models:
                logger.warning(
                    "Requested model not found on vLLM server",
                    requested=self.model_name,
                    available=available_models,
                )
            self._available = True
        except Exception as exc:
            logger.error("Failed to connect to vLLM server", error=str(exc))
            self._available = False

    async def humanize(
        self,
        text: str,
        temperature: float = settings.TEMPERATURE,
        max_tokens: int = settings.MAX_OUTPUT_TOKENS,
    ) -> str:
        """Send humanization request to vLLM server."""
        if not self._available or not self.client:
            raise RuntimeError("Humanizer service is not available")

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "user", "content": text}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 0.9,
        }

        resp = await self.client.post("/v1/chat/completions", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()

    async def disconnect(self):
        """Close HTTP client."""
        if self.client:
            await self.client.aclose()
            self.client = None
        self._available = False
        logger.info("Humanizer client disconnected")
