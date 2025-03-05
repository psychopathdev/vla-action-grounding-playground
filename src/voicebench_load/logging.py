from __future__ import annotations

import re
from collections.abc import Mapping

_SECRET_RE = re.compile(r"(authorization|api[-_]?key|token|secret|password)", re.I)
_TOKEN_RE = re.compile(r"(Bearer\s+)[A-Za-z0-9._~+\-/=]+")


def redact_value(key: str, value: object) -> object:
    """Return a display-safe value for logs and reports."""
    if _SECRET_RE.search(key):
        return "***"
    if isinstance(value, str):
        return _TOKEN_RE.sub(r"\1***", value)
    return value


def redact_mapping(values: Mapping[str, object]) -> dict[str, object]:
    """Redact common secret-looking keys from a mapping."""
    return {key: redact_value(key, value) for key, value in values.items()}
