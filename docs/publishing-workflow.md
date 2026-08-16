# 人工发布回执机制

## 当前边界

phase-07 只管理发布前后的状态与人工回执。

- 不支持自动发布
- 不调用抖音真实发布接口
- 不调用视频号真实发布接口
- 不读取或写入真实平台密钥
- 只记录人工发布结果，形成运营闭环

## 发布状态

支持的发布状态：

- `ready_to_publish`：审核通过，等待人工发布
- `manually_published`：已由人工发布
- `publish_failed`：人工发布失败或暂未发出
- `archived`：任务已归档

允许的状态流转：

- `ready_to_publish -> manually_published`
- `ready_to_publish -> publish_failed`
- `publish_failed -> manually_published`
- `publish_failed -> archived`
- `manually_published -> archived`

不允许直接从 `ready_to_publish` 归档，避免尚未处理的内容被误归档。

## 查看待发布任务

Windows：

```powershell
python .\services\orchestrator\src\publish.py --list --status ready_to_publish
```

Linux / WSL2：

```bash
python ./services/orchestrator/src/publish.py --list --status ready_to_publish
```

按平台筛选：

```powershell
python .\services\orchestrator\src\publish.py --list --platform douyin --status ready_to_publish
```

## 人工发布到抖音

1. 打开 `exports/pending_review/<task_id>/distribution/douyin/`
2. 查看 `title.txt`
3. 查看 `caption.txt`
4. 查看 `hashtags.json`
5. 对照 `distribution/publish_checklist.txt`
6. 人工登录抖音完成发布
7. 将发布链接写回系统

写回命令：

```powershell
python .\services\orchestrator\src\publish.py --task-id "task_xxx" --platform douyin --publish-status manually_published --publish-url "https://example.com/douyin/xxx" --published-by "你的名字" --publish-note "已人工发布"
```

## 人工同步到视频号

1. 打开 `exports/pending_review/<task_id>/distribution/wechat_channels/`
2. 查看 `title.txt`
3. 查看 `caption.txt`
4. 查看 `hashtags.json`
5. 人工登录视频号助手完成同步
6. 将发布链接或备注写回系统

写回命令：

```powershell
python .\services\orchestrator\src\publish.py --task-id "task_xxx" --platform wechat_channels --publish-status manually_published --publish-url "https://example.com/wechat/xxx" --published-by "你的名字" --publish-note "已人工同步"
```

## 发布失败写回

如果某个平台暂时发布失败：

```powershell
python .\services\orchestrator\src\publish.py --task-id "task_xxx" --platform douyin --publish-status publish_failed --published-by "你的名字" --publish-note "标题需调整后重发"
```

后续重新发布成功后，可从 `publish_failed` 写回 `manually_published`。

## 查询单个任务发布状态

```powershell
python .\services\orchestrator\src\publish.py --task-id "task_xxx"
```

## 归档任务

当任务的平台发布状态均为 `manually_published` 或 `publish_failed` 后，可归档：

```powershell
python .\services\orchestrator\src\publish.py --task-id "task_xxx" --archive
```

## 落盘文件

每个任务目录新增：

- `publish_result.json`
- `publish_note.txt`

项目级队列文件：

- `data/state/publish_queue.json`
- `data/state/ready_to_publish.json`
- `data/state/published_queue.json`
- `data/state/publish_failed_queue.json`
- `data/state/archived_publish_queue.json`

## 发布适配器设计稿

phase-07 新增 `src/lobster_farm/publishing/adapters/`：

- `base.py`：统一发布接口
- `douyin.py`：面向未来官方发布接口的占位设计
- `wechat_channels.py`：面向人工同步发布包的占位设计

这些适配器当前只返回占位结果，不执行真实平台调用。
