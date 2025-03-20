from __future__ import annotations

from voicebench_load.config import ValidationConfig
from voicebench_load.providers.base import ProviderResponse

from .extractors import extract_path


def validate_response(response: ProviderResponse, validation: ValidationConfig) -> list[str]:
    """Return validation failure messages for a provider response."""
    errors: list[str] = []
    if response.status_code not in validation.status_codes:
        errors.append(f"unexpected status {response.status_code}")
    for rule in validation.json:
        try:
            value = extract_path(response.json_data, rule.path)
            exists = value is not None
        except Exception:
            value = None
            exists = False
        if rule.exists is not None and exists != rule.exists:
            errors.append(f"path {rule.path} exists={exists}, expected {rule.exists}")
        if rule.equals is not None and value != rule.equals:
            errors.append(f"path {rule.path} equals {value!r}, expected {rule.equals!r}")
    return errors
