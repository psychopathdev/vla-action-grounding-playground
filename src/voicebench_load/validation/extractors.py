from __future__ import annotations

from typing import Any


def extract_path(data: Any, path: str) -> Any:
    """Extract a simple $.a.b[0] path from JSON-like data."""
    if path == "$":
        return data
    if not path.startswith("$."):
        raise ValueError(f"Unsupported path: {path}")
    current = data
    for part in path[2:].split("."):
        if "[" in part and part.endswith("]"):
            name, idx = part[:-1].split("[", 1)
            current = current[name][int(idx)]
        else:
            current = current[part]
    return current
