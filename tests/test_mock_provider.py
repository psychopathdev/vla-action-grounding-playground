import pytest

from voicebench_load.audio.generate import generate_audio
from voicebench_load.config import AudioSourceConfig, ProviderConfig
from voicebench_load.providers.base import RequestContext
from voicebench_load.providers.mock import MockProviderAdapter


@pytest.mark.asyncio
async def test_mock_provider_returns_json() -> None:
    adapter = MockProviderAdapter(ProviderConfig(type="mock", latency_ms=1), seed=1)
    clip = generate_audio(AudioSourceConfig(duration_seconds=0.05))
    response = await adapter.send(RequestContext("r", "s", clip))
    assert response.status_code == 200
    assert response.json_data["text"].startswith("mock transcript")
