from __future__ import annotations

import asyncio
import random
import time

from voicebench_load.config import ProviderConfig

from .base import ProviderResponse, RequestContext


class MockProviderAdapter:
    """Deterministic in-process provider for tests and examples."""

    def __init__(self, config: ProviderConfig, seed: int = 1) -> None:
        self.config = config
        self.rng = random.Random(seed)

    async def send(self, context: RequestContext) -> ProviderResponse:
        start = time.perf_counter()
        await asyncio.sleep(max(0.0, self.config.latency_ms) / 1000.0)
        failed = self.rng.random() < self.config.error_rate
        elapsed = (time.perf_counter() - start) * 1000
        if failed:
            return ProviderResponse(status_code=503, elapsed_ms=elapsed, error="mock_error", bytes_sent=context.audio.size_bytes)
        text = f"mock transcript for {context.scenario_name}"
        body = ("{\"text\": \"" + text + "\"}").encode("utf-8")
        return ProviderResponse(
            status_code=200,
            elapsed_ms=elapsed,
            body=body,
            json_data={"text": text, "request_id": context.request_id},
            headers={"content-type": "application/json"},
            bytes_sent=context.audio.size_bytes,
            bytes_received=len(body),
        )
