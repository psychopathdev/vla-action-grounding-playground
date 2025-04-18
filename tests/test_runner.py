from voicebench_load.config import load_config
from voicebench_load.runner import run_load_test


def test_runner_mock_example() -> None:
    cfg = load_config("examples/generic-json-base64.yaml")
    result = run_load_test(cfg)
    assert result.summary.total_requests >= 1
    assert result.thresholds.passed
