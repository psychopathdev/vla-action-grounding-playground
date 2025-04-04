from pathlib import Path

from voicebench_load.audio.corpus import load_corpus
from voicebench_load.audio.generate import generate_audio
from voicebench_load.config import AudioSourceConfig


def test_load_corpus(tmp_path: Path) -> None:
    path = tmp_path / "a.wav"
    path.write_bytes(generate_audio(AudioSourceConfig(duration_seconds=0.1)).data)
    clips = load_corpus(AudioSourceConfig(kind="corpus", path=str(tmp_path / "*.wav")))
    assert clips[0].filename == "a.wav"
