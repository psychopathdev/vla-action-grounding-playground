from pathlib import Path

from voicebench_load.audio.generate import generate_audio
from voicebench_load.audio.inspect import inspect_audio
from voicebench_load.config import AudioSourceConfig


def test_inspect_generated_wav(tmp_path: Path) -> None:
    path = tmp_path / "sample.wav"
    path.write_bytes(generate_audio(AudioSourceConfig(duration_seconds=0.1)).data)
    info = inspect_audio(path)
    assert info.sample_rate == 16000
    assert info.channels == 1
