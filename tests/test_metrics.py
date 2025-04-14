from voicebench_load.metrics import RequestSample, percentile, summarize


def test_percentile() -> None:
    assert percentile([1, 2, 3], 0.5) == 2


def test_summarize_errors() -> None:
    summary = summarize([
        RequestSample("1", "s", 10, 200, True),
        RequestSample("2", "s", 30, 500, False, "http_500"),
    ], duration_seconds=1)
    assert summary.error_rate == 0.5
    assert summary.latency.p95_ms > 0
