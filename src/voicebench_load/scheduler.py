from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from dataclasses import dataclass

from .config import LoadProfileConfig


@dataclass(frozen=True, slots=True)
class ScheduleTick:
    index: int
    measurement: bool


async def schedule(load: LoadProfileConfig, duration_seconds: float, warmup_seconds: float) -> AsyncIterator[ScheduleTick]:
    """Yield request ticks for fixed, arrival-rate, or staged profiles."""
    if load.mode == "arrival_rate":
        interval = 1.0 / max(load.rate_per_second, 0.001)
        count = int(duration_seconds / interval)
        for idx in range(count):
            yield ScheduleTick(idx, idx * interval >= warmup_seconds)
            await asyncio.sleep(interval)
        return
    if load.mode == "stages" and load.stages:
        idx = 0
        for stage in load.stages:
            rate = float(stage.get("rate_per_second", load.rate_per_second))
            seconds = float(stage.get("duration_seconds", 1))
            interval = 1.0 / max(rate, 0.001)
            for _ in range(int(seconds / interval)):
                yield ScheduleTick(idx, idx * interval >= warmup_seconds)
                idx += 1
                await asyncio.sleep(interval)
        return
    idx = 0
    # Fixed concurrency uses fast ticks; the runner enforces concurrent workers.
    while idx < max(load.concurrency, 1):
        yield ScheduleTick(idx, True)
        idx += 1
