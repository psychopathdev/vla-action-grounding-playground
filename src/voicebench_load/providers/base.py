from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from voicebench_load.audio.generate import AudioClip


@dataclass(frozen=True, slots=True)
class RequestContext:
    request_id: str
    scenario_name: str
    audio: AudioClip
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ProviderResponse:
    status_code: int
    elapsed_ms: float
    body: bytes = b""
    json_data: Any = None
    headers: dict[str, str] = field(default_factory=dict)
    bytes_sent: int = 0
    bytes_received: int = 0
    error: str | None = None
    first_event_ms: float | None = None

    @property
    def ok(self) -> bool:
        return self.error is None and 200 <= self.status_code < 400


class ProviderAdapter(Protocol):
    async def send(self, context: RequestContext) -> ProviderResponse:
        """Send one request and return a provider response."""
