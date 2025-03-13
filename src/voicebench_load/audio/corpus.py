from __future__ import annotations

from glob import glob
from pathlib import Path

from voicebench_load.config import AudioSourceConfig

from .generate import AudioClip
from .inspect import inspect_audio


def load_corpus(config: AudioSourceConfig) -> list[AudioClip]:
    """Load WAV files from a glob pattern into AudioClip objects."""
    if not config.path:
        raise ValueError("Corpus audio source requires path")
    paths = [Path(p) for p in sorted(glob(config.path))]
    clips: list[AudioClip] = []
    for path in paths:
        info = inspect_audio(path)
        if config.max_duration_seconds is not None and info.duration_seconds > config.max_duration_seconds:
            continue
        data = path.read_bytes()
        clips.append(AudioClip(data, path.name, info.sample_rate, info.duration_seconds, info.channels))
        if config.max_files is not None and len(clips) >= config.max_files:
            break
    if not clips:
        raise ValueError(f"No audio files matched corpus pattern: {config.path}")
    return clips
