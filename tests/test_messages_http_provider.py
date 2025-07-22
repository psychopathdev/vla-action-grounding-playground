from voicebench_load.config import ProviderConfig
from voicebench_load.providers.messages_http import MessagesHTTPAdapter


def test_messages_adapter_sets_default_body() -> None:
    adapter = MessagesHTTPAdapter(ProviderConfig(type="messages_http", url="http://example.invalid"))
    assert adapter.config.request["kind"] == "json"
    assert "messages" in adapter.config.request["body"]
