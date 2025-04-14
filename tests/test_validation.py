from voicebench_load.config import ValidationConfig, ValidationRule
from voicebench_load.providers.base import ProviderResponse
from voicebench_load.validation import extract_path, validate_response


def test_extract_path() -> None:
    assert extract_path({"a": {"b": [3]}}, "$.a.b[0]") == 3


def test_validate_response() -> None:
    errors = validate_response(ProviderResponse(200, 1, json_data={"text": "ok"}), ValidationConfig(json=[ValidationRule("$.text", exists=True)]))
    assert errors == []
