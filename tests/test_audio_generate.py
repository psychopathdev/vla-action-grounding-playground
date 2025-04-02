from voicebench_load.audio.generate import generate_audio
from voicebench_load.config import AudioSourceConfig


def test_generate_speech_like_wav() -> None:
    clip = generate_audio(AudioSourceConfig(duration_seconds=0.1, sample_rate=8000), seed=3)
    assert clip.data.startswith(b"RIFF")
    assert clip.sample_rate == 8000
    assert clip.duration_seconds > 0


def test_generation_is_deterministic() -> None:
    cfg = AudioSourceConfig(waveform="noise", duration_seconds=0.1)
    assert generate_audio(cfg, seed=9).digest == generate_audio(cfg, seed=9).digest
