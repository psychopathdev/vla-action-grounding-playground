from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class RequestSample:
    request_id: str
    scenario: str
    latency_ms: float
    status_code: int
    ok: bool
    error: str | None = None
    measured: bool = True
    bytes_sent: int = 0
    bytes_received: int = 0


@dataclass(frozen=True, slots=True)
class LatencyStats:
    count: int
    min_ms: float
    p50_ms: float
    p90_ms: float
    p95_ms: float
    p99_ms: float
    max_ms: float


@dataclass(frozen=True, slots=True)
class RunSummary:
    total_requests: int
    measured_requests: int
    ok_requests: int
    error_rate: float
    requests_per_second: float
    latency: LatencyStats
    errors: dict[str, int] = field(default_factory=dict)
    scenarios: dict[str, dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    index = (len(values) - 1) * q
    lower = int(index)
    upper = min(lower + 1, len(values) - 1)
    frac = index - lower
    return values[lower] * (1 - frac) + values[upper] * frac


def summarize(samples: list[RequestSample], duration_seconds: float | None = None) -> RunSummary:
    measured = [s for s in samples if s.measured]
    latencies = [s.latency_ms for s in measured]
    ok = [s for s in measured if s.ok]
    errors: dict[str, int] = {}
    for sample in measured:
        if not sample.ok:
            key = sample.error or f"status_{sample.status_code}"
            errors[key] = errors.get(key, 0) + 1
    scenario_stats: dict[str, dict[str, Any]] = {}
    for sample in measured:
        bucket = scenario_stats.setdefault(sample.scenario, {"count": 0, "ok": 0})
        bucket["count"] += 1
        bucket["ok"] += int(sample.ok)
    elapsed = max(duration_seconds or 0.0, 0.001)
    return RunSummary(
        total_requests=len(samples),
        measured_requests=len(measured),
        ok_requests=len(ok),
        error_rate=0.0 if not measured else 1 - (len(ok) / len(measured)),
        requests_per_second=len(measured) / elapsed,
        latency=LatencyStats(
            count=len(latencies),
            min_ms=min(latencies) if latencies else 0.0,
            p50_ms=percentile(latencies, 0.50),
            p90_ms=percentile(latencies, 0.90),
            p95_ms=percentile(latencies, 0.95),
            p99_ms=percentile(latencies, 0.99),
            max_ms=max(latencies) if latencies else 0.0,
        ),
        errors=errors,
        scenarios=scenario_stats,
    )
