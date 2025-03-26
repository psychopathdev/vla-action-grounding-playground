from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .metrics import RequestSample, RunSummary
from .thresholds import ThresholdResult


@dataclass(frozen=True, slots=True)
class RunResult:
    summary: RunSummary
    samples: list[RequestSample]
    thresholds: ThresholdResult
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary.to_dict(),
            "samples": [asdict(s) for s in self.samples],
            "thresholds": asdict(self.thresholds),
            "metadata": self.metadata,
        }


def render_report(result: RunResult, formats: list[str], output_dir: str | Path) -> list[Path]:
    """Render configured report formats and return written paths."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    if "json" in formats:
        path = out / "results.json"
        path.write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        written.append(path)
    if "csv" in formats:
        written.append(_write_csv(result, out / "summary.csv"))
    if "markdown" in formats or "md" in formats:
        written.append(_write_markdown(result, out / "summary.md"))
    if "html" in formats:
        written.append(_write_html(result, out / "report.html"))
    return written


def _write_csv(result: RunResult, path: Path) -> Path:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["scenario", "count", "ok"])
        for scenario, data in sorted(result.summary.scenarios.items()):
            writer.writerow([scenario, data["count"], data["ok"]])
        writer.writerow(["TOTAL", result.summary.measured_requests, result.summary.ok_requests])
    return path


def _write_markdown(result: RunResult, path: Path) -> Path:
    s = result.summary
    lines = [
        "# 语音负载测试报告",
        "",
        "## 测试概览",
        f"- 总请求数：{s.measured_requests}",
        f"- 成功请求数：{s.ok_requests}",
        f"- 错误率：{s.error_rate:.2%}",
        f"- 吞吐量：{s.requests_per_second:.2f} req/s",
        "",
        "## 延迟分布",
        f"- p50：{s.latency.p50_ms:.1f} ms",
        f"- p95：{s.latency.p95_ms:.1f} ms",
        f"- p99：{s.latency.p99_ms:.1f} ms",
        "",
        "## 阈值判定",
        "通过" if result.thresholds.passed else "失败",
    ]
    for failure in result.thresholds.failures:
        lines.append(f"- {failure}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _write_html(result: RunResult, path: Path) -> Path:
    s = result.summary
    html = f"""<!doctype html>
<html lang=\"zh-CN\"><meta charset=\"utf-8\"><title>voicebench-load report</title>
<style>body{{font-family:system-ui,sans-serif;max-width:900px;margin:40px auto;line-height:1.6}}code{{background:#f6f8fa;padding:2px 4px}}</style>
<h1>语音负载测试报告</h1>
<p>请求：{s.measured_requests}，成功：{s.ok_requests}，错误率：{s.error_rate:.2%}，吞吐：{s.requests_per_second:.2f} req/s</p>
<h2>延迟</h2><ul><li>p50 {s.latency.p50_ms:.1f} ms</li><li>p95 {s.latency.p95_ms:.1f} ms</li><li>p99 {s.latency.p99_ms:.1f} ms</li></ul>
<h2>阈值</h2><p>{'通过' if result.thresholds.passed else '失败'}</p>
</html>"""
    path.write_text(html, encoding="utf-8")
    return path
