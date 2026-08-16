# 飞书集成说明

## 当前阶段能力

phase-07 最终版本支持真实飞书审核消息发送，并可与 mock 或真实视频 API provider 组合使用；短视频平台发布仍必须由人工完成。

默认仍是：

```env
RUN_MODE=dry-run
FEISHU_ADAPTER=dry-run
VIDEO_PROVIDER=mock
```

## 如何准备飞书应用

1. 在飞书开放平台创建企业自建应用
2. 获取应用的 `App ID`
3. 获取应用的 `App Secret`
4. 为应用开通发送消息所需权限
5. 将应用或机器人加入目标群聊
6. 获取目标群聊的 `chat_id`

建议至少开通以下权限：

- 获取群列表：`im:chat:readonly` 或 `im:chat`
- 发送消息：`im:message:send` 或 `im:message:send_as_bot`

## 需要的配置项

真实飞书发送需要在 `.env` 中填写：

```env
RUN_MODE=real
FEISHU_ADAPTER=real
FEISHU_API_BASE_URL=https://open.feishu.cn
FEISHU_APP_ID=你的 App ID
FEISHU_APP_SECRET=你的 App Secret
FEISHU_DEFAULT_CHAT_ID=目标群聊 chat_id
FEISHU_REQUEST_TIMEOUT_SECONDS=10
FEISHU_MAX_RETRIES=2
VIDEO_PROVIDER=mock
```

注意：

- `.env` 不要提交到仓库
- `.env.example` 只保留模板和空值
- 日志不会输出完整密钥

## 如何先做 dry-run

保持默认配置即可：

```powershell
.\scripts\run-dev.ps1
```

dry-run 会生成审核消息、任务状态和审核目录，但不会发送飞书。

## 如何切到 real

1. 创建 `.env`
2. 填写上文真实飞书配置
3. 保持 `VIDEO_PROVIDER=mock`
4. 执行：

```powershell
.\scripts\run-dev.ps1
```

成功后，任务状态中会记录飞书发送结果。

## 如何验证真实飞书

1. 先运行 `.\scripts\verify.ps1`
2. 确认 dry-run 测试通过
3. 切换 `.env` 到 real 飞书配置
4. 执行 `.\scripts\run-dev.ps1`
5. 查看飞书群是否收到包含 `task_id` 和审核目录的消息
6. 查看任务目录中的 `review_message.json`

## 如何回滚到 dry-run

将 `.env` 改回：

```env
RUN_MODE=dry-run
FEISHU_ADAPTER=dry-run
VIDEO_PROVIDER=mock
```

或者临时移走 `.env`，系统会回退到 `.env.example` 默认 dry-run 配置。

## 错误分类

- `validation_error`：缺少飞书配置
- `token_error`：tenant access token 获取失败
- `send_error`：消息发送接口返回失败
- `permission_message_send`：缺少飞书消息发送权限
- `permission`：缺少飞书接口权限
- `network_error`：网络连接错误
- `timeout`：请求超时
- `invalid_response`：飞书返回内容不是合法 JSON
