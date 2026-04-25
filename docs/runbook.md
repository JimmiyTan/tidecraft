# 运行说明

## 启动顺序

1. 确认 Python 环境已准备完成
2. 确认 `.env.example` 存在
3. 如需本地覆盖配置，可创建 `.env`
4. 执行 `scripts/verify.ps1` 或 `scripts/verify.sh`
5. 执行 `scripts/run-dev.ps1` 或 `scripts/run-dev.sh`
6. 查看任务目录和状态文件

## 默认运行

```powershell
.\scripts\run-dev.ps1
```

默认行为：

- `RUN_MODE=dry-run`
- `FEISHU_ADAPTER=dry-run`
- `VIDEO_PROVIDER=mock`
- 输出任务目录到 `exports/pending_review/<task_id>/`

## 切换真实飞书发送

1. 创建 `.env`
2. 设置 `RUN_MODE=real`
3. 设置 `FEISHU_ADAPTER=real`
4. 保持 `VIDEO_PROVIDER=mock`
5. 填写飞书应用配置
6. 执行 `.\scripts\run-dev.ps1`

回滚到 dry-run：

```env
RUN_MODE=dry-run
FEISHU_ADAPTER=dry-run
VIDEO_PROVIDER=mock
```

## 切换真实视频 API

1. 保持 `.env` 中已有飞书配置
2. 设置 `RUN_MODE=real`
3. 设置 `VIDEO_PROVIDER=api`
4. 填写 `VIDEO_API_KEY` 和 `VIDEO_PROVIDER_BASE_URL`
5. 按真实 provider 文档填写 `VIDEO_SUBMIT_PATH` 和 `VIDEO_STATUS_PATH`
6. 执行 `.\scripts\run-dev.ps1`

回滚到 mock：

```env
VIDEO_PROVIDER=mock
```

## 单模块运行

### Feishu Bridge

```powershell
python .\services\feishu-bridge\src\main.py --topic "示例主题"
```

### Video Gateway

```powershell
python .\services\video-gateway\src\main.py --topic "示例主题" --task-id "demo_task" --review-items-json "[{\"title\":\"示例选题\",\"script_text\":\"示例脚本\"}]"
```

### Orchestrator

```powershell
python .\services\orchestrator\src\main.py --topic "示例主题"
```

## 输出文件

每个任务会生成：

- `topic_list.json`
- `scripts.json`
- `review_message.json`
- `video_result.json`
- `summary.txt`
- `review_decision.json`
- `review_note.txt`

审核通过后还会生成：

- `distribution/douyin/`
- `distribution/wechat_channels/`

## 审核写回

审核写回命令：

```powershell
python .\services\orchestrator\src\review.py --task-id "task_xxx" --review-status approved --reviewed-by "alice" --review-note "内容通过，进入分发准备"
```

支持的审核状态：

- `approved`
- `rejected`
- `needs_edit`

审核结果会同步写回：

- `data/state/tasks/<task_id>.json`
- `data/state/task_index.json`
- `exports/pending_review/<task_id>/review_decision.json`
- `exports/pending_review/<task_id>/review_note.txt`

## 失败排查

- 配置错误：查看 `.env` 和 `docs/configuration.md`
- 状态失败：查看 `data/state/tasks/<task_id>.json`
- 导出缺失：查看 `exports/pending_review/<task_id>/`
- 日志：查看 `logs/services/`
