from __future__ import annotations

from voicebench_load.config import ProviderConfig

from .generic_http import GenericHTTPAdapter


class MessagesHTTPAdapter(GenericHTTPAdapter):
    """Provider-neutral adapter for gateways that accept messages-shaped JSON.

    This is intentionally generic: it does not assume any first-party provider
    has a speech endpoint. Use it for gateways that document a messages-style
    schema with audio passed as base64 or URL fields.
    """

    def __init__(self, config: ProviderConfig) -> None:
        request = dict(config.request or {})
        request.setdefault("kind", "json")
        request.setdefault(
            "body",
            {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Transcribe or analyze this audio."},
                            {"type": "audio", "source": {"type": "base64", "data": "{{audio_base64}}"}},
                        ],
                    }
                ]
            },
        )
        config.request = request
        super().__init__(config)
