import pytest

from voicebench_load.config import ConfigError, interpolate_env
from voicebench_load.logging import redact_mapping


def test_interpolate_env_with_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("VOICEBENCH_TEST", raising=False)
    assert interpolate_env("${VOICEBENCH_TEST:-fallback}") == "fallback"


def test_interpolate_env_missing() -> None:
    with pytest.raises(ConfigError):
        interpolate_env("${VOICEBENCH_DOES_NOT_EXIST}")


def test_redact_mapping() -> None:
    assert redact_mapping({"Authorization": "Bearer abc", "x": "y"})["Authorization"] == "***"
