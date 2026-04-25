# 状态机说明

## 状态列表

- `created`：任务已创建
- `topics_generated`：选题已生成
- `scripts_generated`：脚本已生成
- `review_message_generated`：审核消息已生成
- `video_generated`：视频占位结果已生成
- `completed`：任务已完成
- `failed`：任务失败

## 正常流转

```text
created
  -> topics_generated
  -> scripts_generated
  -> review_message_generated
  -> video_generated
  -> completed
```

## 失败流转

任一步可以进入：

```text
failed
```

失败时会写入：

- `data/state/workflow_state.json`
- `data/state/tasks/<task_id>.json`
- `data/state/task_index.json`

## 审核目录

每个任务会在 `exports/pending_review/<task_id>/` 下生成审核包：

- `topic_list.json`
- `scripts.json`
- `review_message.json`
- `video_result.json`
- `summary.txt`
