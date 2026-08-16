# 验证说明

## 验证目标

确认 phase-07 最终闭环可以运行，并且任务目录、飞书 adapter、视频 provider、人工审核和人工发布回执测试完整。

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
6. 任务目录是否包含审核、provider 和摘要文件
7. Feishu adapter 测试是否通过
8. Video provider 注册机制测试是否通过
9. 状态机测试是否通过
10. 视频 api 配置 smoke 是否通过
11. 失败分支 smoke 是否通过
12. 人工审核状态流转和分发包生成测试是否通过
13. 人工发布回执、队列筛选和归档测试是否通过
14. 发布适配器是否保持占位行为，不调用真实平台接口
15. 一键 Demo 是否完成安全模式、审核、回执和归档闭环
16. 客户前端服务输入校验、响应脱敏和静态文件白名单是否通过
17. GitHub 上传候选文件与 Git 历史隐私检查是否通过

## 预期输出

- 控制台显示任务 ID
- 控制台显示任务目录
- 状态为 `completed`
- `exports/pending_review/<task_id>/summary.txt` 可供人工审核
- 控制台最终显示 workflow、provider、review、publishing 测试通过

## 最终验证边界

- `verify.ps1` 与 `verify.sh` 会强制使用项目内临时 dry-run/mock 配置
- 验证会刷新被 Git 忽略的 `data/`、`exports/` 和 `logs/` 运行数据
- 配置 smoke 只验证真实飞书和视频 API 的参数结构，不执行真实外部调用
- Windows 验证通过不等同于 WSL2、Hyper-V/systemd 或真实外部服务已验证
