import pytest

from voicebench_load.config import LoadProfileConfig
from voicebench_load.scheduler import schedule


@pytest.mark.asyncio
async def test_arrival_rate_schedule_yields_ticks() -> None:
    ticks = []
    async for tick in schedule(LoadProfileConfig(mode="arrival_rate", rate_per_second=10), 0.2, 0):
        ticks.append(tick)
    assert ticks
