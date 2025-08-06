import asyncio

from voicebench_load.config import LoadProfileConfig
from voicebench_load.scheduler import schedule


def test_arrival_rate_schedule_yields_ticks() -> None:
    async def run() -> None:
        ticks = []
        async for tick in schedule(LoadProfileConfig(mode="arrival_rate", rate_per_second=10), 0.2, 0):
            ticks.append(tick)
        assert ticks

    asyncio.run(run())
