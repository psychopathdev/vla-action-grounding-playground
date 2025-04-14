from voicebench_load.config import ThresholdConfig
from voicebench_load.metrics import RequestSample, summarize
from voicebench_load.thresholds import evaluate_thresholds


def test_threshold_failure() -> None:
    summary = summarize([RequestSample("1", "s", 100, 500, False, "x")], duration_seconds=1)
    result = evaluate_thresholds(summary, ThresholdConfig(max_error_rate=0.1))
    assert not result.passed
