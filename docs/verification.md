# 验证说明

## 验证目标

确认 phase-04 的安全闭环可以运行，并且任务目录结构、飞书 adapter 和视频 provider 测试完整。

## 快速验证

Windows：

```powershell
.\scripts\verify.ps1
```

WSL2：

```bash
./scripts/verify.sh
```

## verify 检查项

1. Python 是否存在
2. 关键目录是否存在
3. orchestrator 是否能完成任务
4. 最新状态是否为 `completed`
5. `data/state/task_index.json` 是否生成
6. 任务目录是否包含五个审核文件
7. Feishu adapter 测试是否通过
8. Video provider 注册机制测试是否通过
9. 状态机测试是否通过
10. 视频 api 配置 smoke 是否通过
11. 失败分支 smoke 是否通过

## 预期输出

- 控制台显示任务 ID
- 控制台显示任务目录
- 状态为 `completed`
- `exports/pending_review/<task_id>/summary.txt` 可供人工审核
