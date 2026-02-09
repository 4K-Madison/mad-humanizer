from abc import ABC, abstractmethod

import httpx

from app.models.schemas import DetectorResult


class BaseDetector(ABC):
    """Abstract base class for all AI text detectors."""

    name: str
    display_name: str
    description: str

    @abstractmethod
    async def detect(self, client: httpx.AsyncClient, text: str) -> DetectorResult:
        """Run detection on the given text and return a DetectorResult."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if this detector is configured and ready to use."""
        ...
