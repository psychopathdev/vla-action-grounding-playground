from __future__ import annotations

import io
import wave
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WavInfo:
    sample_rate: int
    channels: int
    sample_width: int
    frames: int

    @property
    def duration_seconds(self) -> float:
        return self.frames / float(self.sample_rate)


def pcm16(samples: list[float]) -> bytes:
    """Convert normalized float samples to little-endian signed 16-bit PCM."""
    out = bytearray()
    for sample in samples:
        clipped = max(-1.0, min(1.0, sample))
        value = int(clipped * 32767)
        out.extend(value.to_bytes(2, "little", signed=True))
    return bytes(out)


def write_wav_bytes(samples: list[float], sample_rate: int, channels: int = 1) -> bytes:
    """Return a WAV file as bytes."""
    if channels != 1:
        raise ValueError("Only mono synthetic generation is currently supported")
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm16(samples))
    return buf.getvalue()


def read_wav_info(data: bytes) -> WavInfo:
    """Read basic metadata from WAV bytes."""
    with wave.open(io.BytesIO(data), "rb") as wf:
        return WavInfo(
            sample_rate=wf.getframerate(),
            channels=wf.getnchannels(),
            sample_width=wf.getsampwidth(),
            frames=wf.getnframes(),
        )
