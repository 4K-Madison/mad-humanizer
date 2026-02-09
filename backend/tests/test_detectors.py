"""Unit tests for detector framework with mocked httpx responses."""

import asyncio
from unittest.mock import AsyncMock, patch, MagicMock

import httpx
import pytest

from app.models.schemas import DetectorResult
from app.services.detectors.base import BaseDetector
from app.services.detectors.registry import DetectorRegistry
from app.services.detectors.gptzero import GPTZeroDetector
from app.services.detectors.originality import OriginalityDetector
from app.services.detectors.copyleaks import CopyleaksDetector


# ---------------------------------------------------------------------------
# BaseDetector ABC tests
# ---------------------------------------------------------------------------

class TestBaseDetector:
    def test_cannot_instantiate_abc(self):
        with pytest.raises(TypeError):
            BaseDetector()

    def test_concrete_subclass(self):
        class FakeDetector(BaseDetector):
            name = "fake"
            display_name = "Fake"
            description = "A fake detector"

            async def detect(self, client, text):
                return DetectorResult(
                    detector=self.name, score=0.5, label="human", details=None, error=None
                )

            def is_available(self):
                return True

        d = FakeDetector()
        assert d.name == "fake"
        assert d.is_available()


# ---------------------------------------------------------------------------
# DetectorRegistry tests
# ---------------------------------------------------------------------------

class TestDetectorRegistry:
    def test_register_and_get(self):
        class FakeDetector(BaseDetector):
            name = "test"
            display_name = "Test"
            description = "Test detector"
            async def detect(self, client, text):
                pass
            def is_available(self):
                return True

        registry = DetectorRegistry()
        detector = FakeDetector()
        registry.register(detector)

        assert registry.get("test") is detector
        assert registry.get("nonexistent") is None

    def test_get_available_filters(self):
        class AvailableDetector(BaseDetector):
            name = "avail"
            display_name = "Available"
            description = "Available"
            async def detect(self, client, text):
                pass
            def is_available(self):
                return True

        class UnavailableDetector(BaseDetector):
            name = "unavail"
            display_name = "Unavailable"
            description = "Unavailable"
            async def detect(self, client, text):
                pass
            def is_available(self):
                return False

        registry = DetectorRegistry()
        registry.register(AvailableDetector())
        registry.register(UnavailableDetector())

        available = registry.get_available()
        assert len(available) == 1
        assert available[0].name == "avail"

        all_detectors = registry.get_all()
        assert len(all_detectors) == 2

    def test_register_defaults(self):
        registry = DetectorRegistry.register_defaults()
        names = {d.name for d in registry.get_all()}
        assert names == {"gptzero", "originality", "copyleaks"}


# ---------------------------------------------------------------------------
# GPTZero detector tests
# ---------------------------------------------------------------------------

class TestGPTZeroDetector:
    @patch("app.services.detectors.gptzero.settings")
    def test_is_available_with_key(self, mock_settings):
        mock_settings.GPTZERO_API_KEY = "test-key"
        d = GPTZeroDetector()
        assert d.is_available() is True

    @patch("app.services.detectors.gptzero.settings")
    def test_is_not_available_without_key(self, mock_settings):
        mock_settings.GPTZERO_API_KEY = ""
        d = GPTZeroDetector()
        assert d.is_available() is False

    @pytest.mark.asyncio
    @patch("app.services.detectors.gptzero.settings")
    async def test_detect_success(self, mock_settings):
        mock_settings.GPTZERO_API_KEY = "test-key"
        d = GPTZeroDetector()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "documents": [
                {
                    "completely_generated_prob": 0.85,
                    "class_probabilities": {"ai": 0.85, "human": 0.10, "mixed": 0.05},
                }
            ]
        }

        client = AsyncMock(spec=httpx.AsyncClient)
        client.post.return_value = mock_response

        result = await d.detect(client, "Some AI text")
        assert result.detector == "gptzero"
        assert result.score == 0.85
        assert result.label == "ai"
        assert result.error is None

    @pytest.mark.asyncio
    @patch("app.services.detectors.gptzero.settings")
    async def test_detect_api_error(self, mock_settings):
        mock_settings.GPTZERO_API_KEY = "test-key"
        d = GPTZeroDetector()

        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Rate limited", request=MagicMock(), response=mock_response
        )

        client = AsyncMock(spec=httpx.AsyncClient)
        client.post.return_value = mock_response

        result = await d.detect(client, "Some text")
        assert result.detector == "gptzero"
        assert result.score is None
        assert result.error is not None
        assert "429" in result.error


# ---------------------------------------------------------------------------
# Originality detector tests
# ---------------------------------------------------------------------------

class TestOriginalityDetector:
    @patch("app.services.detectors.originality.settings")
    def test_is_available_with_key(self, mock_settings):
        mock_settings.ORIGINALITY_API_KEY = "test-key"
        d = OriginalityDetector()
        assert d.is_available() is True

    @pytest.mark.asyncio
    @patch("app.services.detectors.originality.settings")
    async def test_detect_success(self, mock_settings):
        mock_settings.ORIGINALITY_API_KEY = "test-key"
        d = OriginalityDetector()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "score": {"ai": 0.92, "original": 0.08}
        }

        client = AsyncMock(spec=httpx.AsyncClient)
        client.post.return_value = mock_response

        result = await d.detect(client, "Some AI text")
        assert result.detector == "originality"
        assert result.score == 0.92
        assert result.label == "ai"
        assert result.error is None


# ---------------------------------------------------------------------------
# Copyleaks detector tests
# ---------------------------------------------------------------------------

class TestCopyleaksDetector:
    @patch("app.services.detectors.copyleaks.settings")
    def test_is_available_with_key(self, mock_settings):
        mock_settings.COPYLEAKS_API_KEY = "user@email.com:apikey123"
        d = CopyleaksDetector()
        assert d.is_available() is True

    @pytest.mark.asyncio
    @patch("app.services.detectors.copyleaks.settings")
    async def test_detect_success(self, mock_settings):
        mock_settings.COPYLEAKS_API_KEY = "user@email.com:apikey123"
        d = CopyleaksDetector()

        auth_response = MagicMock()
        auth_response.status_code = 200
        auth_response.raise_for_status = MagicMock()
        auth_response.json.return_value = {"access_token": "fake-token"}

        scan_response = MagicMock()
        scan_response.status_code = 200
        scan_response.raise_for_status = MagicMock()
        scan_response.json.return_value = {
            "summary": {"ai": 0.78, "human": 0.22}
        }

        client = AsyncMock(spec=httpx.AsyncClient)
        client.post.side_effect = [auth_response, scan_response]

        result = await d.detect(client, "Some AI text")
        assert result.detector == "copyleaks"
        assert result.score == 0.78
        assert result.label == "ai"
        assert result.error is None

    @pytest.mark.asyncio
    @patch("app.services.detectors.copyleaks.settings")
    async def test_detect_bad_key_format(self, mock_settings):
        mock_settings.COPYLEAKS_API_KEY = "no-colon-here"
        d = CopyleaksDetector()

        client = AsyncMock(spec=httpx.AsyncClient)
        result = await d.detect(client, "Some text")
        assert result.detector == "copyleaks"
        assert result.score is None
        assert result.error is not None
        assert "email:api_key" in result.error


# ---------------------------------------------------------------------------
# Fan-out / partial success integration test
# ---------------------------------------------------------------------------

class TestFanOut:
    @pytest.mark.asyncio
    async def test_gather_with_partial_failure(self):
        """Simulate asyncio.gather with one succeeding and one failing detector."""

        class GoodDetector(BaseDetector):
            name = "good"
            display_name = "Good"
            description = "Always succeeds"
            async def detect(self, client, text):
                return DetectorResult(
                    detector=self.name, score=0.3, label="human", details=None, error=None
                )
            def is_available(self):
                return True

        class BadDetector(BaseDetector):
            name = "bad"
            display_name = "Bad"
            description = "Always fails"
            async def detect(self, client, text):
                raise RuntimeError("API down")
            def is_available(self):
                return True

        detectors = [GoodDetector(), BadDetector()]
        client = AsyncMock(spec=httpx.AsyncClient)
        tasks = [d.detect(client, "test text") for d in detectors]
        raw = await asyncio.gather(*tasks, return_exceptions=True)

        results = []
        for det, res in zip(detectors, raw):
            if isinstance(res, Exception):
                results.append(
                    DetectorResult(
                        detector=det.name, score=None, label=None,
                        details=None, error=str(res),
                    )
                )
            else:
                results.append(res)

        assert len(results) == 2
        assert results[0].score == 0.3
        assert results[0].error is None
        assert results[1].score is None
        assert results[1].error == "API down"
