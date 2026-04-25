# 审核确认机制说明

## 目标

phase-05 在现有 `pending_review` 审核目录基础上，补齐人工审核写回机制，让任务进入以下审核状态之一：

- `pending_review`
- `approved`
- `rejected`
- `needs_edit`

当前阶段仍然：

- 不接自动发布
- 仅生成双平台分发准备包
- 保持飞书链路与视频 mock/real 链路兼容

## 审核状态流转

允许的流转：

- `pending_review -> approved`
- `pending_review -> rejected`
- `pending_review -> needs_edit`
- `needs_edit -> approved`
- `needs_edit -> rejected`
- `needs_edit -> needs_edit`

不允许的流转：

- `approved -> needs_edit`
- `approved -> rejected`
- `rejected -> approved`

## 审核写回命令

Windows：

```powershell
python .\services\orchestrator\src\review.py --task-id "task_xxx" --review-status approved --reviewed-by "alice" --review-note "内容通过，进入分发准备"
```

WSL2 / Linux：

```bash
python ./services/orchestrator/src/review.py --task-id "task_xxx" --review-status approved --reviewed-by "alice" --review-note "内容通过，进入分发准备"
```

可选审核结果：

- `approved`
- `rejected`
- `needs_edit`

## 审核命令模板

每个 `pending_review` 任务目录会自动生成：

- `approve.cmd.txt`
- `reject.cmd.txt`
- `needs_edit.cmd.txt`

模板内同时包含：

- Windows 命令
- Linux / WSL2 命令
- `task_id`
- `reviewed_by` 占位
- `review_note` 占位

## 查询待审核任务

Windows：

```powershell
python .\services\orchestrator\src\list_review_tasks.py --review-status pending_review
```

Linux / WSL2：

```bash
python ./services/orchestrator/src/list_review_tasks.py --review-status pending_review
```

支持筛选：

- `pending_review`
- `needs_edit`
- `approved`
- `rejected`

## 审核结果落盘

每个任务目录会新增：

- `review_decision.json`
- `review_note.txt`

审核状态也会同步写回：

- `data/state/tasks/<task_id>.json`
- `data/state/task_index.json`
- 若该任务是最新任务，也会同步更新 `data/state/workflow_state.json`

## approved 后的分发准备包

仅当审核结果为 `approved` 时生成：

- `distribution/douyin/title.txt`
- `distribution/douyin/caption.txt`
- `distribution/douyin/hashtags.json`
- `distribution/douyin/publish_payload.json`
- `distribution/wechat_channels/title.txt`
- `distribution/wechat_channels/caption.txt`
- `distribution/wechat_channels/hashtags.json`
- `distribution/wechat_channels/publish_payload.json`

说明：

- 只生成人工发布准备数据
- `publish_payload.json` 仅为后续平台适配保留结构
- 当前不会执行自动发布

## 飞书审核联动

当前飞书审核消息仍保留：

- `task_id`
- 审核目录

审核写回后会在任务目录 `summary.txt` 末尾追加审核结果摘要，方便再次查看。

phase-06 起，飞书审核消息还会补充：

- `review_status`
- 可复制审核命令摘要

## 排错建议

任务不存在：

- 检查 `data/state/task_index.json`

非法状态流转：

- 检查当前任务的 `review_status`

approved 后未生成分发包：

- 检查 `topic_list.json`
- 检查 `scripts.json`
- 检查任务目录 `distribution/`

待发布队列未更新：

- 检查 `data/state/publish_queue.json`
- 检查 `distribution/ready_to_publish.json`
