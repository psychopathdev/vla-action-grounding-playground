from pathlib import Path

from voicebench_load.cli import main


def test_cli_validate() -> None:
    assert main(["validate", "examples/generic-json-base64.yaml"]) == 0


def test_cli_generate_audio(tmp_path: Path) -> None:
    out = tmp_path / "sample.wav"
    assert main(["generate-audio", str(out), "--duration", "0.05"]) == 0
    assert out.read_bytes().startswith(b"RIFF")
