from pathlib import Path

import pytest

from voicebench_load.config import ConfigError, load_config


def test_load_example_config() -> None:
    cfg = load_config("examples/generic-json-base64.yaml")
    assert cfg.provider.type == "mock"
    assert cfg.scenarios[0].name == "short_zh_audio"


def test_invalid_missing_scenarios(tmp_path: Path) -> None:
    path = tmp_path / "bad.yaml"
    path.write_text("run:\n  name: bad\n", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(path)
