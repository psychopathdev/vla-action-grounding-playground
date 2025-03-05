class VoiceBenchError(Exception):
    """Base error for voicebench-load."""


class ConfigError(VoiceBenchError):
    """Raised when a run configuration is invalid."""


class ProviderError(VoiceBenchError):
    """Raised when a provider request fails before a response is available."""


class ThresholdError(VoiceBenchError):
    """Raised when configured thresholds fail."""
