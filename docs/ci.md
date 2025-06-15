# CI 集成

CI 中建议只使用 mock 或内部测试环境，不要对生产接口做默认压测。

```bash
voicebench-load run examples/thresholds.yaml
```

当阈值失败时命令返回退出码 1，可直接作为流水线门禁。


对真实服务的容量压测更适合放在受控环境的定时任务中，而不是每个 PR 自动执行。
