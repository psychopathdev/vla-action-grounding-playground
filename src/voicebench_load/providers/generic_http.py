from __future__ import annotations

import asyncio
import base64
import json
import time
import urllib.error
import urllib.request
from uuid import uuid4

from voicebench_load.config import ProviderConfig, interpolate_env

from .base import ProviderResponse, RequestContext


def _render(value: object, context: RequestContext) -> object:
    if isinstance(value, str):
        rendered = value.replace("{{audio_base64}}", base64.b64encode(context.audio.data).decode("ascii"))
        rendered = rendered.replace("{{audio_filename}}", context.audio.filename)
        rendered = rendered.replace("{{audio_duration_ms}}", str(int(context.audio.duration_seconds * 1000)))
        rendered = rendered.replace("{{request_id}}", context.request_id)
        return rendered
    if isinstance(value, dict):
        return {key: _render(item, context) for key, item in value.items()}
    if isinstance(value, list):
        return [_render(item, context) for item in value]
    return value


class GenericHTTPAdapter:
    """Generic HTTP adapter for JSON, multipart, and raw audio payloads."""

    def __init__(self, config: ProviderConfig) -> None:
        if not config.url:
            raise ValueError("generic_http provider requires url")
        self.config = config

    async def send(self, context: RequestContext) -> ProviderResponse:
        return await asyncio.to_thread(self._send_sync, context)

    def _send_sync(self, context: RequestContext) -> ProviderResponse:
        start = time.perf_counter()
        try:
            body, content_type = self._build_body(context)
            headers = {str(k): str(v) for k, v in interpolate_env(self.config.headers).items()}
            if content_type and "content-type" not in {h.lower() for h in headers}:
                headers["Content-Type"] = content_type
            request = urllib.request.Request(
                self.config.url,
                data=body,
                headers=headers,
                method=self.config.method.upper(),
            )
            with urllib.request.urlopen(request, timeout=self.config.timeout_seconds) as response:
                raw = response.read()
                json_data = _loads_json(raw)
                elapsed = (time.perf_counter() - start) * 1000
                return ProviderResponse(
                    status_code=response.status,
                    elapsed_ms=elapsed,
                    body=raw,
                    json_data=json_data,
                    headers=dict(response.headers.items()),
                    bytes_sent=len(body or b""),
                    bytes_received=len(raw),
                )
        except urllib.error.HTTPError as exc:
            raw = exc.read()
            elapsed = (time.perf_counter() - start) * 1000
            return ProviderResponse(exc.code, elapsed, raw, _loads_json(raw), dict(exc.headers.items()), bytes_sent=context.audio.size_bytes, bytes_received=len(raw), error=f"http_{exc.code}")
        except Exception as exc:
            elapsed = (time.perf_counter() - start) * 1000
            return ProviderResponse(0, elapsed, error=exc.__class__.__name__, bytes_sent=context.audio.size_bytes)

    def _build_body(self, context: RequestContext) -> tuple[bytes | None, str | None]:
        request = self.config.request or {"kind": "json", "body": {"audio": "{{audio_base64}}"}}
        kind = request.get("kind", "json")
        if kind == "json":
            body = _render(request.get("body", {"audio": "{{audio_base64}}"}), context)
            return json.dumps(body).encode("utf-8"), "application/json"
        if kind == "raw":
            return context.audio.data, request.get("content_type", "audio/wav")
        if kind == "multipart":
            return self._multipart_body(context, request)
        raise ValueError(f"Unsupported request kind: {kind}")

    def _multipart_body(self, context: RequestContext, request: dict[str, object]) -> tuple[bytes, str]:
        boundary = f"voicebench-{uuid4().hex}"
        file_field = str(request.get("file_field", "audio"))
        parts: list[bytes] = []
        for key, value in dict(request.get("fields", {})).items():
            rendered = _render(value, context)
            parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{key}\"\r\n\r\n{rendered}\r\n".encode())
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{file_field}\"; filename=\"{context.audio.filename}\"\r\nContent-Type: audio/wav\r\n\r\n".encode()
            + context.audio.data
            + b"\r\n"
        )
        parts.append(f"--{boundary}--\r\n".encode())
        return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def _loads_json(data: bytes) -> object | None:
    try:
        return json.loads(data.decode("utf-8"))
    except Exception:
        return None
