from __future__ import annotations

import math
import random
from dataclasses import dataclass
from hashlib import sha256

from voicebench_load.config import AudioSourceConfig

from .wav import read_wav_info, write_wav_bytes


@dataclass(frozen=True, slots=True)
class AudioClip:
    data: bytes
    filename: str
    sample_rate: int
    duration_seconds: float
    channels: int = 1

    @property
    def size_bytes(self) -> int:
        return len(self.data)

    @property
    def digest(self) -> str:
        return sha256(self.data).hexdigest()


def _frames(duration_seconds: float, sample_rate: int) -> int:
    return max(1, int(duration_seconds * sample_rate))


def sine_wave(duration_seconds: float, sample_rate: int, amplitude: float = 0.25) -> list[float]:
    return [amplitude * math.sin(2 * math.pi * 440.0 * i / sample_rate) for i in range(_frames(duration_seconds, sample_rate))]


def silence(duration_seconds: float, sample_rate: int, amplitude: float = 0.0) -> list[float]:
    return [amplitude for _ in range(_frames(duration_seconds, sample_rate))]


def noise(duration_seconds: float, sample_rate: int, amplitude: float = 0.15, seed: int = 1) -> list[float]:
    rng = random.Random(seed)
    return [rng.uniform(-amplitude, amplitude) for _ in range(_frames(duration_seconds, sample_rate))]


def speech_like(duration_seconds: float, sample_rate: int, amplitude: float = 0.25, seed: int = 1) -> list[float]:
    """Generate deterministic speech-ish chirps, not human speech."""
    rng = random.Random(seed)
    samples: list[float] = []
    total = _frames(duration_seconds, sample_rate)
    for i in range(total):
        t = i / sample_rate
        syllable = int(t * 6)
        gate = 0.35 + 0.65 * (syllable % 2)
        f0 = 160 + 35 * math.sin(2 * math.pi * 1.7 * t) + rng.uniform(-0.5, 0.5)
        formant = math.sin(2 * math.pi * (f0 * 2.7) * t) * 0.35
        samples.append(amplitude * gate * (math.sin(2 * math.pi * f0 * t) + formant))
    return samples


def generate_audio(config: AudioSourceConfig, seed: int = 1) -> AudioClip:
    """Generate an AudioClip from a synthetic audio config."""
    if config.kind != "synthetic":
        raise ValueError("generate_audio only handles synthetic sources; use corpus loader for files")
    generators = {
        "sine": sine_wave,
        "silence": silence,
        "noise": lambda d, sr, a: noise(d, sr, a, seed),
        "speech_like": lambda d, sr, a: speech_like(d, sr, a, seed),
    }
    if config.waveform not in generators:
        raise ValueError(f"Unsupported waveform: {config.waveform}")
    samples = generators[config.waveform](config.duration_seconds, config.sample_rate, config.amplitude)
    data = write_wav_bytes(samples, config.sample_rate, config.channels)
    info = read_wav_info(data)
    return AudioClip(
        data=data,
        filename=f"{config.waveform}-{info.sample_rate}-{int(info.duration_seconds * 1000)}ms.wav",
        sample_rate=info.sample_rate,
        duration_seconds=info.duration_seconds,
        channels=info.channels,
    )
