import structlog

from app.services.detectors.base import BaseDetector

logger = structlog.get_logger()


class DetectorRegistry:
    """Registry for AI text detectors. Pluggable factory pattern."""

    def __init__(self) -> None:
        self._detectors: dict[str, BaseDetector] = {}

    def register(self, detector: BaseDetector) -> None:
        """Register a detector instance by its name."""
        self._detectors[detector.name] = detector
        logger.info(
            "Registered detector",
            name=detector.name,
            available=detector.is_available(),
        )

    def get(self, name: str) -> BaseDetector | None:
        """Get a detector by name, or None if not found."""
        return self._detectors.get(name)

    def get_available(self) -> list[BaseDetector]:
        """Return all detectors that are currently available (API key configured)."""
        return [d for d in self._detectors.values() if d.is_available()]

    def get_all(self) -> list[BaseDetector]:
        """Return all registered detectors regardless of availability."""
        return list(self._detectors.values())

    @staticmethod
    def register_defaults() -> "DetectorRegistry":
        """Create a registry with all built-in detectors registered."""
        from app.services.detectors.gptzero import GPTZeroDetector
        from app.services.detectors.originality import OriginalityDetector
        from app.services.detectors.copyleaks import CopyleaksDetector

        registry = DetectorRegistry()
        registry.register(GPTZeroDetector())
        registry.register(OriginalityDetector())
        registry.register(CopyleaksDetector())
        return registry
