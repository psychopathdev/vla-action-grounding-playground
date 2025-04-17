from voicebench_load.audio.generate import generate_audio
from voicebench_load.config import AudioSourceConfig, ProviderConfig
from voicebench_load.providers.base import RequestContext
from voicebench_load.providers.generic_http import GenericHTTPAdapter


def test_generic_http_builds_json_body() -> None:
    adapter = GenericHTTPAdapter(ProviderConfig(type="generic_http", url="http://example.invalid"))
    clip = generate_audio(AudioSourceConfig(duration_seconds=0.05))
    body, content_type = adapter._build_body(RequestContext("req", "s", clip))
    assert content_type == "application/json"
    assert b"audio" in body
