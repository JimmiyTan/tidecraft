# 视频 Provider 集成说明

## 当前阶段能力

phase-04 支持通过 `VIDEO_PROVIDER=api` 调用真实视频 API provider，但仍不接入任何短视频平台自动发布能力。

默认安全模式仍可使用：

```env
VIDEO_PROVIDER=mock
```

## 配置项

真实视频 API provider 需要在 `.env` 中填写：

```env
RUN_MODE=real
VIDEO_PROVIDER=api
VIDEO_API_KEY=你的 API Key
VIDEO_PROVIDER_BASE_URL=https://你的服务地址
VIDEO_SUBMIT_PATH=/submit
VIDEO_STATUS_PATH=/status/{remote_task_id}
VIDEO_REQUEST_TIMEOUT_SECONDS=30
VIDEO_MAX_RETRIES=2
VIDEO_POLL_INTERVAL_SECONDS=5
VIDEO_MAX_POLL_ATTEMPTS=12
```

说明：

- `VIDEO_SUBMIT_PATH` 是提交视频任务接口路径
- `VIDEO_STATUS_PATH` 是查询任务状态接口路径
- `{remote_task_id}` 会被替换为远端任务 ID
- `VIDEO_API_KEY` 只允许写入 `.env`

## Provider 响应约定

提交接口响应中需要包含以下任一远端任务 ID 字段：

```json
{
  "remote_task_id": "xxx",
  "status": "processing"
}
```

或：

```json
{
  "data": {
    "task_id": "xxx",
    "status": "processing"
  }
}
```

完成状态可为：

- `ready`
- `completed`
- `succeeded`
- `success`

失败状态可为：

- `failed`
- `error`

## 输出文件

每个任务目录会包含：

- `provider_request.json`：脱敏后的 provider 请求摘要
- `provider_response.json`：provider 响应
- `video_result.json`：统一视频任务结果
- `summary.txt`：人工审核摘要

## 如何验证真实视频链路

1. 保持飞书配置可用，或临时切回 `FEISHU_ADAPTER=dry-run`
2. 在 `.env` 中设置 `VIDEO_PROVIDER=api`
3. 填写真实视频 API 配置
4. 执行：

```powershell
.\scripts\run-dev.ps1
```

5. 检查任务目录下的 `video_result.json`
6. 检查 `summary.txt` 中的视频 provider 状态

## 如何回滚到 mock

将 `.env` 改为：

```env
VIDEO_PROVIDER=mock
```

如果也要回滚飞书：

```env
RUN_MODE=dry-run
FEISHU_ADAPTER=dry-run
VIDEO_PROVIDER=mock
```

## 错误分类

- `validation_error`：缺少视频 API 配置
- `http_error`：HTTP 请求失败
- `network`：网络连接错误
- `timeout`：请求超时
- `permission`：认证或权限错误
- `not_found`：远端任务不存在
- `provider_status`：远端状态不是完成状态
- `response_parse`：响应结构不符合预期
