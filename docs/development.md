# 开发说明

模块边界：

- `config` 负责配置加载和校验。
- `audio` 负责音频样本。
- `providers` 负责请求发送。
- `runner` 负责编排。
- `metrics`、`thresholds`、`reports` 负责结果处理。


提交前建议运行 `pytest -q` 和 `python -m voicebench_load validate examples/generic-json-base64.yaml`。


新增模块时，优先保持单一职责，并在 `tests/` 添加对应的最小覆盖。
