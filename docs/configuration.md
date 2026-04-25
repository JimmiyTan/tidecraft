# 配置说明

## 配置文件优先级

1. `.env.example` 提供默认模板
2. `.env` 提供本地覆盖
3. `.env` 不应提交仓库

## 运行模式

### dev

用于本地开发。当前建议仍搭配：

```env
FEISHU_ADAPTER=dry-run
VIDEO_PROVIDER=mock
```

### dry-run

默认模式。不会发送真实飞书消息，不会调用真实视频 API。

```env
RUN_MODE=dry-run
FEISHU_ADAPTER=dry-run
VIDEO_PROVIDER=mock
```

### real

真实服务准备模式。当前只会启用参数校验和 adapter/provider 骨架，不会自动发布。

```env
RUN_MODE=real
FEISHU_ADAPTER=real
VIDEO_PROVIDER=api
```

## real 模式所需配置

飞书 real adapter 需要：

```env
FEISHU_API_BASE_URL=https://open.feishu.cn
FEISHU_APP_ID=
FEISHU_APP_SECRET=
FEISHU_DEFAULT_CHAT_ID=
FEISHU_REQUEST_TIMEOUT_SECONDS=10
FEISHU_MAX_RETRIES=2
```

视频 api provider 需要：

```env
VIDEO_API_KEY=
VIDEO_PROVIDER_BASE_URL=
VIDEO_SUBMIT_PATH=/submit
VIDEO_STATUS_PATH=/status/{remote_task_id}
VIDEO_REQUEST_TIMEOUT_SECONDS=30
VIDEO_MAX_RETRIES=2
VIDEO_POLL_INTERVAL_SECONDS=5
VIDEO_MAX_POLL_ATTEMPTS=12
```

## 安全要求

- 真实密钥只能写入 `.env`
- 不要把 `.env` 提交到仓库
- `.env.example` 只能保留空值或示例默认值
- phase-02 不启用自动正式发布
- phase-04 允许真实飞书发送和真实视频 API provider，但仍不启用自动发布
