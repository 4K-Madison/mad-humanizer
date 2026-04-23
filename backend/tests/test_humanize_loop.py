"""Unit tests for humanize_with_detector_gate retry loop."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from app.models.schemas import DetectorResult
from app.services.detectors.base import BaseDetector
from app.services.detectors.registry import DetectorRegistry
from app.services.humanize_loop import (
    humanize_single,
    humanize_with_detector_gate,
)


class _FakeHumanizer:
    def __init__(self, outputs: list[str]):
        self.outputs = list(outputs)
        self.calls: list[dict] = []

    async def humanize(self, *, text: str, temperature: float, max_tokens: int) -> str:
        self.calls.append(
            {"text": text, "temperature": temperature, "max_tokens": max_tokens}
        )
        if not self.outputs:
            raise AssertionError("Humanizer called more times than expected")
        return self.outputs.pop(0)


class _ScriptedDetector(BaseDetector):
    """Detector that returns a scripted sequence of (score, error) tuples.

    Each entry is either:
    - (score: float, error: str|None) -> returns DetectorResult
    - Exception instance -> raised when detect is called
    """

    name = "scripted"
    display_name = "Scripted"
    description = "Test detector with scripted responses"

    def __init__(self, script: list, available: bool = True):
        self.script = list(script)
        self._available = available
        self.calls = 0

    def is_available(self) -> bool:
        return self._available

    async def detect(self, client, text: str) -> DetectorResult:
        self.calls += 1
        if not self.script:
            raise AssertionError("Detector called more times than scripted")
        entry = self.script.pop(0)
        if isinstance(entry, BaseException):
            raise entry
        score, error = entry
        return DetectorResult(
            detector=self.name,
            score=score,
            label=("ai" if score is not None and score > 0.5 else "human"),
            details=None,
            error=error,
        )


def _registry_with(detector: BaseDetector) -> DetectorRegistry:
    reg = DetectorRegistry()
    reg.register(detector)
    return reg


@pytest.fixture
def http_client():
    return AsyncMock(spec=httpx.AsyncClient)


# ---------------------------------------------------------------------------
# Case 1: first attempt ≤ threshold → returns immediately
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_first_attempt_meets_threshold(http_client):
    humanizer = _FakeHumanizer(outputs=["clean output"])
    detector = _ScriptedDetector(script=[(0.20, None)])
    registry = _registry_with(detector)

    result = await humanize_with_detector_gate(
        humanizer=humanizer,
        registry=registry,
        http_client=http_client,
        text="input",
        base_temperature=0.95,
        max_tokens=1024,
        max_attempts=3,
        threshold=0.35,
        detector_name="scripted",
    )

    assert result.threshold_met is True
    assert result.humanized_text == "clean output"
    assert result.ai_score == 0.20
    assert len(result.attempts) == 1
    assert result.warning is None
    assert len(humanizer.calls) == 1
    assert detector.calls == 1


# ---------------------------------------------------------------------------
# Case 2: first two > threshold, third ≤ → returns attempt 3
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_third_attempt_meets_threshold(http_client):
    humanizer = _FakeHumanizer(outputs=["bad1", "bad2", "good3"])
    detector = _ScriptedDetector(
        script=[(0.80, None), (0.55, None), (0.30, None)]
    )
    registry = _registry_with(detector)

    result = await humanize_with_detector_gate(
        humanizer=humanizer,
        registry=registry,
        http_client=http_client,
        text="input",
        base_temperature=0.95,
        max_tokens=1024,
        max_attempts=3,
        threshold=0.35,
        detector_name="scripted",
        temp_bump_per_retry=0.05,
    )

    assert result.threshold_met is True
    assert result.humanized_text == "good3"
    assert result.ai_score == 0.30
    assert len(result.attempts) == 3
    assert result.warning is None
    # Temperatures ramp 0.95, 1.00, 1.05
    assert humanizer.calls[0]["temperature"] == pytest.approx(0.95)
    assert humanizer.calls[1]["temperature"] == pytest.approx(1.00)
    assert humanizer.calls[2]["temperature"] == pytest.approx(1.05)
    # Each retry uses the ORIGINAL input, not the previous output
    assert all(c["text"] == "input" for c in humanizer.calls)


# ---------------------------------------------------------------------------
# Case 3: all three > threshold → returns lowest-score attempt, warning set
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_all_attempts_fail_returns_best(http_client):
    humanizer = _FakeHumanizer(outputs=["a1", "a2", "a3"])
    detector = _ScriptedDetector(
        script=[(0.80, None), (0.45, None), (0.60, None)]
    )
    registry = _registry_with(detector)

    result = await humanize_with_detector_gate(
        humanizer=humanizer,
        registry=registry,
        http_client=http_client,
        text="input",
        base_temperature=0.95,
        max_tokens=1024,
        max_attempts=3,
        threshold=0.35,
        detector_name="scripted",
    )

    assert result.threshold_met is False
    # Lowest score was 0.45 on attempt 2
    assert result.humanized_text == "a2"
    assert result.ai_score == 0.45
    assert len(result.attempts) == 3
    assert result.warning is not None
    assert "45" in result.warning or "45.0" in result.warning


# ---------------------------------------------------------------------------
# Case 4: detector unavailable → single attempt, no loop, warning set
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_detector_unavailable(http_client):
    humanizer = _FakeHumanizer(outputs=["single output"])
    detector = _ScriptedDetector(script=[], available=False)
    registry = _registry_with(detector)

    result = await humanize_with_detector_gate(
        humanizer=humanizer,
        registry=registry,
        http_client=http_client,
        text="input",
        base_temperature=0.95,
        max_tokens=1024,
        max_attempts=3,
        threshold=0.35,
        detector_name="scripted",
    )

    assert result.threshold_met is False
    assert result.humanized_text == "single output"
    assert result.ai_score is None
    assert len(result.attempts) == 1
    assert result.warning is not None
    assert "not configured" in result.warning
    assert len(humanizer.calls) == 1
    assert detector.calls == 0


# ---------------------------------------------------------------------------
# Case 4b: detector name not in registry → same as unavailable
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_detector_not_registered(http_client):
    humanizer = _FakeHumanizer(outputs=["single output"])
    registry = DetectorRegistry()  # empty

    result = await humanize_with_detector_gate(
        humanizer=humanizer,
        registry=registry,
        http_client=http_client,
        text="input",
        base_temperature=0.95,
        max_tokens=1024,
        max_attempts=3,
        threshold=0.35,
        detector_name="nonexistent",
    )

    assert result.threshold_met is False
    assert result.humanized_text == "single output"
    assert result.ai_score is None
    assert len(result.attempts) == 1
    assert len(humanizer.calls) == 1


# ---------------------------------------------------------------------------
# Case 5: detector returns error (score=None) every attempt → returns
# attempt 1 with warning
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_detector_errors_every_attempt(http_client):
    humanizer = _FakeHumanizer(outputs=["a1", "a2", "a3"])
    detector = _ScriptedDetector(
        script=[
            (None, "API returned 500"),
            (None, "API returned 500"),
            (None, "API returned 500"),
        ]
    )
    registry = _registry_with(detector)

    result = await humanize_with_detector_gate(
        humanizer=humanizer,
        registry=registry,
        http_client=http_client,
        text="input",
        base_temperature=0.95,
        max_tokens=1024,
        max_attempts=3,
        threshold=0.35,
        detector_name="scripted",
    )

    assert result.threshold_met is False
    assert len(result.attempts) == 3
    # _argmin_score falls back to attempt 0 when all scores are None
    assert result.humanized_text == "a1"
    assert result.ai_score is None
    assert result.warning is not None
    assert "failed on all attempts" in result.warning


# ---------------------------------------------------------------------------
# Case 6: detector raises transport error (timeout) → fail-fast, warning set
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_detector_timeout_fails_fast(http_client):
    humanizer = _FakeHumanizer(outputs=["a1", "a2", "a3"])
    detector = _ScriptedDetector(
        script=[httpx.ReadTimeout("timed out")]
    )
    registry = _registry_with(detector)

    result = await humanize_with_detector_gate(
        humanizer=humanizer,
        registry=registry,
        http_client=http_client,
        text="input",
        base_temperature=0.95,
        max_tokens=1024,
        max_attempts=3,
        threshold=0.35,
        detector_name="scripted",
        detector_timeout_seconds=5.0,
    )

    assert result.threshold_met is False
    assert result.humanized_text == "a1"
    assert result.ai_score is None
    assert len(result.attempts) == 1  # fail-fast, no retries
    assert len(humanizer.calls) == 1
    assert result.warning is not None
    assert "unavailable" in result.warning.lower()


# ---------------------------------------------------------------------------
# Case 6b: detector blocks past asyncio.wait_for timeout → fail-fast
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_detector_hang_triggers_timeout(http_client):
    humanizer = _FakeHumanizer(outputs=["a1", "a2", "a3"])

    class HangingDetector(BaseDetector):
        name = "hang"
        display_name = "Hang"
        description = "Hangs forever"

        def is_available(self):
            return True

        async def detect(self, client, text):
            await asyncio.sleep(10)
            raise AssertionError("should have been cancelled by timeout")

    detector = HangingDetector()
    registry = _registry_with(detector)

    result = await humanize_with_detector_gate(
        humanizer=humanizer,
        registry=registry,
        http_client=http_client,
        text="input",
        base_temperature=0.95,
        max_tokens=1024,
        max_attempts=3,
        threshold=0.35,
        detector_name="hang",
        detector_timeout_seconds=0.05,
    )

    assert result.threshold_met is False
    assert len(result.attempts) == 1
    assert result.ai_score is None
    assert result.warning is not None
    assert "unavailable" in result.warning.lower()


# ---------------------------------------------------------------------------
# Case 7: humanize_single bypasses detector entirely
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_humanize_single_no_detector():
    humanizer = _FakeHumanizer(outputs=["direct output"])

    result = await humanize_single(
        humanizer=humanizer,
        text="input",
        temperature=0.7,
        max_tokens=512,
        threshold=0.35,
    )

    assert result.humanized_text == "direct output"
    assert result.ai_score is None
    assert result.threshold_met is False
    assert result.warning is None
    assert len(result.attempts) == 1
    assert len(humanizer.calls) == 1


# ---------------------------------------------------------------------------
# Case 8: max_attempts=1 → single attempt only even when score fails
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_max_attempts_cap(http_client):
    humanizer = _FakeHumanizer(outputs=["only"])
    detector = _ScriptedDetector(script=[(0.90, None)])
    registry = _registry_with(detector)

    result = await humanize_with_detector_gate(
        humanizer=humanizer,
        registry=registry,
        http_client=http_client,
        text="input",
        base_temperature=0.95,
        max_tokens=1024,
        max_attempts=1,
        threshold=0.35,
        detector_name="scripted",
    )

    assert result.threshold_met is False
    assert result.humanized_text == "only"
    assert result.ai_score == 0.90
    assert len(result.attempts) == 1
    assert len(humanizer.calls) == 1


# ---------------------------------------------------------------------------
# Case 9: temperature is clamped at 2.0
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_temperature_clamped_at_2(http_client):
    humanizer = _FakeHumanizer(outputs=["a1", "a2", "a3"])
    detector = _ScriptedDetector(
        script=[(0.80, None), (0.80, None), (0.80, None)]
    )
    registry = _registry_with(detector)

    await humanize_with_detector_gate(
        humanizer=humanizer,
        registry=registry,
        http_client=http_client,
        text="input",
        base_temperature=1.95,
        max_tokens=1024,
        max_attempts=3,
        threshold=0.35,
        detector_name="scripted",
        temp_bump_per_retry=0.10,
    )

    # Ramp would be 1.95, 2.05, 2.15 but must clamp at 2.0
    assert humanizer.calls[0]["temperature"] == pytest.approx(1.95)
    assert humanizer.calls[1]["temperature"] == pytest.approx(2.00)
    assert humanizer.calls[2]["temperature"] == pytest.approx(2.00)
