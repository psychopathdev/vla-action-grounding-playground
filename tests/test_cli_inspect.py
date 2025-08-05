from pathlib import Path

from voicebench_load.cli import main


def test_cli_inspect_audio(tmp_path: Path) -> None:
    wav = tmp_path / "a.wav"
    assert main(["generate-audio", str(wav), "--duration", "0.05"]) == 0
    assert main(["inspect-audio", str(wav)]) == 0
