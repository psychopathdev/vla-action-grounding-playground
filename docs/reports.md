# 报告

支持四种输出：

- `results.json`：完整样本和汇总，便于机器处理。
- `summary.csv`：每个场景一行。
- `summary.md`：中文摘要。
- `report.html`：单文件 HTML 概览。


报告不会主动写入请求头，但原始响应可能包含业务字段；共享前请检查内容。

`results.json` 的顶层包含 `summary`、`samples`、`thresholds` 和 `metadata`。
