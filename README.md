# voicebench-load

`voicebench-load` 是一个面向语音/音频模型接口的负载测试工具。它用 YAML 描述场景，生成或读取音频样本，并输出延迟、吞吐、错误率和阈值结果。

项目默认保持厂商中立：你可以测试自建服务、网关或任何你有授权访问的 HTTP 接口。


## 适用场景

- 在发布前压测自建语音识别或语音理解网关。
- 对比不同音频时长下的接口延迟。
- 在 CI 中用 mock 或内部环境验证延迟阈值。


## 快速开始

```bash
python -m pip install -e ".[dev]"
voicebench-load validate examples/generic-json-base64.yaml
voicebench-load run examples/generic-json-base64.yaml
```


## 最小配置

```yaml
provider:
  type: mock
scenarios:
  - name: short
    audio: {kind: synthetic, waveform: speech_like, duration_seconds: 0.5}
```


## 负载模型

当前支持固定并发、到达率和分阶段配置。固定并发适合快速冒烟，到达率适合容量估算，分阶段适合模拟渐进流量。


## 音频样本

合成音频用于可重复测试，不代表真实语音质量。需要评估真实业务效果时，应使用经过授权且脱敏的语料库。


## 厂商中立

工具只关心 HTTP 请求形状、响应状态、延迟和校验规则；不会假设某个供应商的私有协议。


## 报告

每次运行可以输出 JSON、CSV、Markdown 和 HTML。JSON 保留原始样本，Markdown 更适合发给团队阅读。


## 阈值

`thresholds` 可用于设置最大错误率、p95/p99 延迟和最低吞吐量。阈值失败时 CLI 返回退出码 1。


## 密钥处理

请使用环境变量传递 token，例如 `${VOICE_API_TOKEN}`。不要把真实 token 写入 YAML、报告或测试文件。
