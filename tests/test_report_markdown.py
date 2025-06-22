from voicebench_load.config import load_config
from voicebench_load.reports import render_report
from voicebench_load.runner import run_load_test


def test_markdown_report_contains_chinese_heading(tmp_path) -> None:
    result = run_load_test(load_config("examples/generic-json-base64.yaml"))
    [path] = render_report(result, ["markdown"], tmp_path)
    assert "语音负载测试报告" in path.read_text(encoding="utf-8")
