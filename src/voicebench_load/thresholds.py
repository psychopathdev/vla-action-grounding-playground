from __future__ import annotations

from dataclasses import dataclass

from .config import ThresholdConfig
from .metrics import RunSummary


@dataclass(frozen=True, slots=True)
class ThresholdResult:
    passed: bool
    failures: list[str]


def evaluate_thresholds(summary: RunSummary, config: ThresholdConfig) -> ThresholdResult:
    """Evaluate configured thresholds against a run summary."""
    failures: list[str] = []
    if config.max_error_rate is not None and summary.error_rate > config.max_error_rate:
        failures.append(f"error_rate {summary.error_rate:.4f} > {config.max_error_rate:.4f}")
    if config.p95_latency_ms is not None and summary.latency.p95_ms > config.p95_latency_ms:
        failures.append(f"p95 {summary.latency.p95_ms:.1f}ms > {config.p95_latency_ms:.1f}ms")
    if config.p99_latency_ms is not None and summary.latency.p99_ms > config.p99_latency_ms:
        failures.append(f"p99 {summary.latency.p99_ms:.1f}ms > {config.p99_latency_ms:.1f}ms")
    if config.min_requests_per_second is not None and summary.requests_per_second < config.min_requests_per_second:
        failures.append(f"rps {summary.requests_per_second:.2f} < {config.min_requests_per_second:.2f}")
    return ThresholdResult(not failures, failures)
