from voicebench_load.config import load_config
from voicebench_load.reports import render_report
from voicebench_load.runner import run_load_test


def test_render_reports(tmp_path) -> None:
    cfg = load_config("examples/generic-json-base64.yaml")
    result = run_load_test(cfg)
    paths = render_report(result, ["json", "csv", "markdown", "html"], tmp_path)
    assert {p.name for p in paths} == {"results.json", "summary.csv", "summary.md", "report.html"}
