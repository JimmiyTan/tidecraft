# lobster-farm

`lobster-farm` 是一个本地运行的内容自动化系统。当前阶段定位为：`可长期运行的人工审核内容中台`。

## 默认安全行为

- 默认 `RUN_MODE=dry-run`
- 默认 `FEISHU_ADAPTER=dry-run`
- 默认 `VIDEO_PROVIDER=mock`
- 不依赖真实密钥即可运行
- 不启用自动正式发布
- 允许按配置切换到真实飞书发送
- 允许按配置切换到真实视频 API provider
- 短视频平台自动发布仍未接入
- 当前没有自动发布能力

## 当前闭环

1. 接收主题字符串
2. 生成 5 条选题占位结果
3. 为每条选题生成脚本占位结果
4. 通过 Feishu adapter 生成 dry-run 审核消息，或在 real 模式发送真实飞书消息
5. 通过 Video provider 生成 mock 待审核结果，或在 api 模式调用真实视频 API
6. 以任务 ID 为目录导出审核包
7. 写入单任务状态文件、最新状态文件和任务索引
8. 支持按 task_id 写回审核结果并生成分发准备包
9. 支持查询待审核任务、生成审核命令模板与待发布队列
10. 支持在 Hyper-V Ubuntu 虚拟机中以 systemd timer 长期运行

## 关键输出

- 最新状态：`data/state/workflow_state.json`
- 单任务状态：`data/state/tasks/<task_id>.json`
- 任务索引：`data/state/task_index.json`
- 审核导出：`exports/pending_review/<task_id>/`
- 人工审核摘要：`exports/pending_review/<task_id>/summary.txt`
- 审核决策：`exports/pending_review/<task_id>/review_decision.json`
- approved 分发准备包：`exports/pending_review/<task_id>/distribution/`
- 待发布队列：`data/state/publish_queue.json`
- 运维状态：`data/runtime/run-dev/status.env`

## 运行命令

Windows：

```powershell
.\scripts\run-dev.ps1
```

WSL2：

```bash
./scripts/run-dev.sh
```

## 验证命令

Windows：

```powershell
.\scripts\verify.ps1
```

WSL2：

```bash
./scripts/verify.sh
```

## 文档入口

- 安装说明：`docs/install.md`
- 配置说明：`docs/configuration.md`
- 架构说明：`docs/architecture.md`
- 运行说明：`docs/runbook.md`
- 状态机说明：`docs/state-machine.md`
- 验证说明：`docs/verification.md`
- 飞书集成：`docs/feishu-integration.md`
- 视频 Provider 集成：`docs/video-provider-integration.md`
- 内容流水线：`docs/content-pipeline.md`
- 审核确认机制：`docs/review-workflow.md`
- 待发布队列：`docs/publish-queue.md`
- 备份与恢复：`docs/backup-and-restore.md`
- 运维手册：`docs/operations.md`
