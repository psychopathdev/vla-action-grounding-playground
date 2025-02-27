# Contributing

感谢你关注 `voicebench-load`。这个项目优先接受小而清晰的改动：配置、音频生成、调度器、报告和文档都可以独立改进。

## 本地开发

```bash
python -m pip install -e ".[dev]"
pytest
```

请为行为变化补充测试，并避免在示例或测试中提交真实密钥、真实用户音频或供应商私有返回内容。
