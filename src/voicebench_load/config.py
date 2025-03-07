from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .errors import ConfigError
from .logging import redact_mapping

_ENV_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-(.*?))?\}")


def interpolate_env(value: Any) -> Any:
    """Expand ${VAR} and ${VAR:-fallback} in nested config values."""
    if isinstance(value, str):
        def repl(match: re.Match[str]) -> str:
            name, fallback = match.group(1), match.group(2)
            if name in os.environ:
                return os.environ[name]
            if fallback is not None:
                return fallback
            raise ConfigError(f"Missing environment variable: {name}")
        return _ENV_RE.sub(repl, value)
    if isinstance(value, list):
        return [interpolate_env(item) for item in value]
    if isinstance(value, dict):
        return {key: interpolate_env(item) for key, item in value.items()}
    return value


@dataclass(slots=True)
class RunSettings:
    name: str = "voicebench-load run"
    duration_seconds: float = 30.0
    warmup_seconds: float = 0.0
    seed: int = 1


@dataclass(slots=True)
class LoadProfileConfig:
    mode: str = "fixed_concurrency"
    concurrency: int = 1
    rate_per_second: float = 1.0
    ramp_up_seconds: float = 0.0
    stages: list[dict[str, Any]] = field(default_factory=list)


@dataclass(slots=True)
class ProviderConfig:
    type: str = "mock"
    url: str | None = None
    method: str = "POST"
    timeout_seconds: float = 30.0
    headers: dict[str, str] = field(default_factory=dict)
    request: dict[str, Any] = field(default_factory=dict)
    latency_ms: float = 20.0
    error_rate: float = 0.0
    retry: dict[str, Any] = field(default_factory=dict)

    def safe_headers(self) -> dict[str, object]:
        return redact_mapping(self.headers)


@dataclass(slots=True)
class AudioSourceConfig:
    kind: str = "synthetic"
    waveform: str = "speech_like"
    duration_seconds: float = 1.0
    sample_rate: int = 16000
    channels: int = 1
    amplitude: float = 0.25
    path: str | None = None
    max_files: int | None = None
    max_duration_seconds: float | None = None


@dataclass(slots=True)
class ScenarioConfig:
    name: str
    weight: float = 1.0
    audio: AudioSourceConfig = field(default_factory=AudioSourceConfig)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ValidationRule:
    path: str
    exists: bool | None = None
    equals: Any = None


@dataclass(slots=True)
class ValidationConfig:
    status_codes: list[int] = field(default_factory=lambda: [200])
    json: list[ValidationRule] = field(default_factory=list)


@dataclass(slots=True)
class ThresholdConfig:
    max_error_rate: float | None = None
    p95_latency_ms: float | None = None
    p99_latency_ms: float | None = None
    min_requests_per_second: float | None = None


@dataclass(slots=True)
class ReportConfig:
    output_dir: str = "reports"
    formats: list[str] = field(default_factory=lambda: ["json", "markdown"])


@dataclass(slots=True)
class RunConfig:
    run: RunSettings = field(default_factory=RunSettings)
    load: LoadProfileConfig = field(default_factory=LoadProfileConfig)
    provider: ProviderConfig = field(default_factory=ProviderConfig)
    scenarios: list[ScenarioConfig] = field(default_factory=list)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    thresholds: ThresholdConfig = field(default_factory=ThresholdConfig)
    reports: ReportConfig = field(default_factory=ReportConfig)


def _audio(data: dict[str, Any] | None) -> AudioSourceConfig:
    return AudioSourceConfig(**(data or {}))


def _scenario(data: dict[str, Any]) -> ScenarioConfig:
    if "name" not in data:
        raise ConfigError("Each scenario requires a name")
    copy = dict(data)
    copy["audio"] = _audio(copy.get("audio"))
    return ScenarioConfig(**copy)


def _validation(data: dict[str, Any] | None) -> ValidationConfig:
    data = data or {}
    rules = [ValidationRule(**item) for item in data.get("json", [])]
    return ValidationConfig(status_codes=list(data.get("status_codes", [200])), json=rules)


def load_config(path: str | Path) -> RunConfig:
    """Load a YAML configuration file into typed dataclasses."""
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    raw = interpolate_env(raw)
    scenarios = [_scenario(item) for item in raw.get("scenarios", [])]
    if not scenarios:
        raise ConfigError("At least one scenario is required")
    cfg = RunConfig(
        run=RunSettings(**raw.get("run", {})),
        load=LoadProfileConfig(**raw.get("load", {})),
        provider=ProviderConfig(**raw.get("provider", {})),
        scenarios=scenarios,
        validation=_validation(raw.get("validation")),
        thresholds=ThresholdConfig(**raw.get("thresholds", {})),
        reports=ReportConfig(**raw.get("reports", {})),
    )
    validate_config(cfg)
    return cfg


def validate_config(config: RunConfig) -> None:
    """Raise ConfigError if the loaded configuration is inconsistent."""
    if config.run.duration_seconds <= 0:
        raise ConfigError("duration_seconds must be positive")
    if config.run.warmup_seconds < 0:
        raise ConfigError("warmup_seconds cannot be negative")
    if config.load.concurrency < 1:
        raise ConfigError("concurrency must be at least 1")
    if config.load.mode not in {"fixed_concurrency", "arrival_rate", "stages"}:
        raise ConfigError(f"Unsupported load mode: {config.load.mode}")
    if config.provider.type == "generic_http" and not config.provider.url:
        raise ConfigError("generic_http provider requires url")
    for scenario in config.scenarios:
        if scenario.weight <= 0:
            raise ConfigError(f"Scenario {scenario.name!r} weight must be positive")
        if scenario.audio.duration_seconds <= 0:
            raise ConfigError(f"Scenario {scenario.name!r} audio duration must be positive")
