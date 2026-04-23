"""Humanize-with-detector-gate orchestrator.

Runs the humanizer in a bounded retry loop, scoring each output with a
configured AI detector. Returns the first output whose AI score is at or
below the threshold, or — if none of the attempts pass — the best-scoring
attempt along with a user-facing warning.

Fail-fast behavior: transport-level detector failures (timeout, connect
error, read error) abort the loop immediately. Retrying when the detector
is unreachable just burns humanizer compute to arrive at the same verdict.
Per-call 4xx/5xx responses are treated as score=None and can still retry,
since the next call might succeed.
"""

import asyncio
from dataclasses import dataclass

import httpx
import structlog

from app.config import settings
from app.models.schemas import HumanizeAttempt
from app.services.detectors.base import BaseDetector
from app.services.detectors.registry import DetectorRegistry

logger = structlog.get_logger()

_FATAL_DETECTOR_EXCEPTIONS: tuple[type[BaseException], ...] = (
    asyncio.TimeoutError,
    httpx.TimeoutException,
    httpx.ConnectError,
    httpx.ReadError,
    httpx.NetworkError,
)


@dataclass
class HumanizeLoopResult:
    humanized_text: str
    ai_score: float | None
    threshold_met: bool
    attempts: list[HumanizeAttempt]
    threshold: float
    warning: str | None


def _pack(
    attempts: list[HumanizeAttempt],
    *,
    best_index: int,
    threshold: float,
    threshold_met: bool,
    warning: str | None = None,
) -> HumanizeLoopResult:
    best = attempts[best_index]
    return HumanizeLoopResult(
        humanized_text=best.humanized_text,
        ai_score=best.ai_score,
        threshold_met=threshold_met,
        attempts=attempts,
        threshold=threshold,
        warning=warning,
    )


def _argmin_score(attempts: list[HumanizeAttempt]) -> int:
    """Return the index of the attempt with the lowest non-None score.

    If every attempt's score is None (detector errored on all of them),
    fall back to the first attempt.
    """
    best_index = 0
    best_score: float | None = None
    for i, a in enumerate(attempts):
        if a.ai_score is None:
            continue
        if best_score is None or a.ai_score < best_score:
            best_score = a.ai_score
            best_index = i
    return best_index


async def _run_detector_with_timeout(
    detector: BaseDetector,
    http_client: httpx.AsyncClient,
    text: str,
    timeout_seconds: float,
):
    """Wrap detector.detect in an asyncio timeout.

    Returns (detector_result, fatal_error_message):
    - On success: (DetectorResult, None)
    - On fatal transport error: (None, error_message)
    """
    try:
        result = await asyncio.wait_for(
            detector.detect(http_client, text),
            timeout=timeout_seconds,
        )
        return result, None
    except _FATAL_DETECTOR_EXCEPTIONS as exc:
        logger.warning(
            "Detector transport failure — aborting retry loop",
            detector=detector.name,
            error=str(exc) or type(exc).__name__,
        )
        return None, f"{type(exc).__name__}: {exc}" if str(exc) else type(exc).__name__


async def humanize_with_detector_gate(
    *,
    humanizer,
    registry: DetectorRegistry,
    http_client: httpx.AsyncClient,
    text: str,
    base_temperature: float,
    max_tokens: int,
    max_attempts: int,
    threshold: float,
    detector_name: str,
    temp_bump_per_retry: float = 0.05,
    detector_timeout_seconds: float = 30.0,
) -> HumanizeLoopResult:
    """Humanize + score in a loop. Returns best attempt (≤ threshold or lowest)."""

    detector = registry.get(detector_name)

    # Detector unavailable → humanize once, no loop
    if detector is None or not detector.is_available():
        humanized = await humanizer.humanize(
            text=text,
            temperature=base_temperature,
            max_tokens=max_tokens,
        )
        attempt = HumanizeAttempt(
            attempt=1,
            humanized_text=humanized,
            ai_score=None,
            detector=detector_name,
            detector_error=None,
            temperature_used=base_temperature,
        )
        return _pack(
            [attempt],
            best_index=0,
            threshold=threshold,
            threshold_met=False,
            warning="AI detector not configured; returning unverified output.",
        )

    attempts: list[HumanizeAttempt] = []

    for i in range(max_attempts):
        temp = min(base_temperature + i * temp_bump_per_retry, 2.0)

        humanized = await humanizer.humanize(
            text=text,
            temperature=temp,
            max_tokens=max_tokens,
        )

        det_result, fatal_error = await _run_detector_with_timeout(
            detector,
            http_client,
            humanized,
            timeout_seconds=detector_timeout_seconds,
        )

        if fatal_error is not None:
            # Append the current attempt with no score, fail fast.
            attempts.append(
                HumanizeAttempt(
                    attempt=i + 1,
                    humanized_text=humanized,
                    ai_score=None,
                    detector=detector.name,
                    detector_error=fatal_error,
                    temperature_used=temp,
                )
            )
            return _pack(
                attempts,
                best_index=len(attempts) - 1,
                threshold=threshold,
                threshold_met=False,
                warning=(
                    "AI detector functionality is currently unavailable; "
                    "returning unverified output."
                ),
            )

        attempts.append(
            HumanizeAttempt(
                attempt=i + 1,
                humanized_text=humanized,
                ai_score=det_result.score,
                detector=detector.name,
                detector_error=det_result.error,
                temperature_used=temp,
            )
        )

        if det_result.score is not None and det_result.score <= threshold:
            return _pack(
                attempts,
                best_index=i,
                threshold=threshold,
                threshold_met=True,
                warning=None,
            )

    # Exhausted all attempts without meeting threshold
    best_index = _argmin_score(attempts)
    best = attempts[best_index]

    if best.ai_score is None:
        warning = (
            "AI detector failed on all attempts; returning first humanization."
        )
    else:
        pct = round(best.ai_score * 100, 1)
        warning = (
            f"We couldn't get the AI-detection score below "
            f"{round(threshold * 100)}% after {len(attempts)} attempts. "
            f"Showing the best result ({pct}%). Consider manually editing "
            f"this output."
        )

    return _pack(
        attempts,
        best_index=best_index,
        threshold=threshold,
        threshold_met=False,
        warning=warning,
    )


async def humanize_single(
    *,
    humanizer,
    text: str,
    temperature: float,
    max_tokens: int,
    threshold: float,
) -> HumanizeLoopResult:
    """Single humanization with no detector gating — used when
    options.enable_detector_gate is False."""
    humanized = await humanizer.humanize(
        text=text,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    attempt = HumanizeAttempt(
        attempt=1,
        humanized_text=humanized,
        ai_score=None,
        detector="",
        detector_error=None,
        temperature_used=temperature,
    )
    return HumanizeLoopResult(
        humanized_text=humanized,
        ai_score=None,
        threshold_met=False,
        attempts=[attempt],
        threshold=threshold,
        warning=None,
    )
