from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from .wav import read_wav_info


@dataclass(frozen=True, slots=True)
class AudioInfo:
    path: str
    duration_seconds: float
    sample_rate: int
    channels: int
    size_bytes: int
    sha256: str


def inspect_audio(path: str | Path) -> AudioInfo:
    """Inspect a local WAV file."""
    p = Path(path)
    data = p.read_bytes()
    info = read_wav_info(data)
    return AudioInfo(
        path=str(p),
        duration_seconds=info.duration_seconds,
        sample_rate=info.sample_rate,
        channels=info.channels,
        size_bytes=len(data),
        sha256=sha256(data).hexdigest(),
    )
