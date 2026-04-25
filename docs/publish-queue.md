# 待发布队列说明

## 目标

phase-06 在审核通过后整理人工发布资产，但仍然：

- 不执行自动发布
- 不接入短视频平台自动发稿
- 只生成待发布队列与人工检查清单

## 队列索引位置

项目级索引：

- `data/state/publish_queue.json`
- `data/state/ready_to_publish.json`

任务级索引：

- `exports/pending_review/<task_id>/distribution/ready_to_publish.json`
- `exports/pending_review/<task_id>/distribution/publish_checklist.txt`

## 队列字段

每条待发布记录至少包含：

- `task_id`
- `platform`
- `title_file`
- `caption_file`
- `hashtags_file`
- `payload_file`
- `approved_at`

## 人工发布前建议顺序

1. 查看 `publish_queue.json`
2. 找到目标 `task_id`
3. 打开对应平台的 `title.txt`、`caption.txt`、`hashtags.json`
4. 对照 `publish_checklist.txt` 逐项确认
5. 人工登录平台完成发布

## 说明

`publish_payload.json` 仅作为后续平台适配保留结构。

当前阶段：

- 允许人工复制其中内容
- 不允许系统自动提交到任何平台
