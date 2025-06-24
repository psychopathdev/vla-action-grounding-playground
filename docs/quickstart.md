# 快速开始

安装开发版：

```bash
python -m pip install -e ".[dev]"
```

校验示例配置：

```bash
voicebench-load validate examples/generic-json-base64.yaml
```

运行本地 mock 测试：

```bash
voicebench-load run examples/generic-json-base64.yaml
```

运行完成后默认在 `reports/` 下生成 `results.json`、`summary.md` 等文件。

如果只想使用 CLI，可以在虚拟环境中执行 `python -m pip install .`。


## 使用本地 HTTP mock

在一个终端启动：

```bash
voicebench-load mock-server
```

另一个终端运行：

```bash
voicebench-load run examples/local-http-mock.yaml
```
