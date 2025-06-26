# 适配器

`voicebench-load` 默认提供两个适配器：

- `mock`：本地测试和演示，不访问外部服务。
- `generic_http`：面向普通 HTTP 语音接口，可发送 JSON、multipart 或 raw audio。

项目不绑定具体供应商；如果某个网关使用 messages 风格 JSON，可以从 `messages_http` 作为模板扩展。


请求模板支持 `{{audio_base64}}`、`{{audio_filename}}`、`{{audio_duration_ms}}` 和 `{{request_id}}`。


## 扩展 checklist

1. 定义请求格式。
2. 明确认证来自环境变量。
3. 返回 `ProviderResponse`。
4. 为成功、超时、非 2xx 和解析失败补测试。
