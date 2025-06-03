# 配置格式

配置文件使用 YAML，主要分为 `run`、`load`、`provider`、`scenarios`、`validation`、`thresholds` 和 `reports`。

`provider.headers` 支持 `${VAR}` 形式的环境变量插值。真实 token 不应写入配置文件。


## provider

`type: mock` 用于本地测试；`type: generic_http` 用于真实 HTTP 接口。
