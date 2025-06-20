from pathlib import Path

from voicebench_load.cli import main


def test_cli_init_writes_file(tmp_path: Path) -> None:
    path = tmp_path / "voicebench.yaml"
    assert main(["init", str(path)]) == 0
    assert "scenarios" in path.read_text(encoding="utf-8")
