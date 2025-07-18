# Troubleshooting

## 配置提示缺少环境变量

检查 `${VAR}` 是否在当前 shell 中导出，或使用 `${VAR:-fallback}` 设置本地默认值。

## 报告里错误率为 100%

先看 `results.json` 中每个样本的 `error` 字段，再确认 provider URL、认证头和响应校验路径。
