# lobster-farm 项目结项说明

## 结项结论

`lobster-farm` 在 `phase-07` 完成功能收尾，最终交付为一个本地运行、可追踪、可审计的人工审核内容中台。

项目在此阶段结束，不启动 `phase-08`，不继续扩展自动发布、运营看板或飞书日报。

## 最终交付范围

1. 输入主题并生成候选短视频选题
2. 生成脚本占位结果和审核消息
3. 通过可替换 Feishu adapter 执行 dry-run 或真实审核消息发送
4. 通过可替换 Video provider 执行 mock 或真实 API 调用
5. 将任务状态、任务索引和审核材料落盘
6. 支持人工审核通过、拒绝和退回修改
7. 为审核通过任务生成抖音、视频号发布准备包
8. 支持人工写回发布结果、失败原因和发布链接
9. 支持按平台、状态查询发布队列并归档任务
10. 提供 Windows、WSL2 和 Hyper-V Ubuntu 运行与运维骨架
11. 提供固定 dry-run/mock 的一键功能演示入口
12. 提供仅本机访问的客户前端演示页面
13. 提供快捷按钮、中文使用说明、隐私审计和 GitHub 上传前检查工具

## 不在交付范围内

- 自动登录或控制短视频平台
- 自动正式发布内容
- 读取个人浏览器数据、Cookie 或账号密码
- 在仓库保存真实密钥、Webhook 或访问令牌
- 真实热点自动抓取
- 运营看板、飞书日报和新的业务阶段

## 最终安全默认值

- `RUN_MODE=dry-run`
- `FEISHU_ADAPTER=dry-run`
- `VIDEO_PROVIDER=mock`
- 发布适配器只返回占位结果，不调用真实平台发布接口
- `.env`、`data/`、`exports/` 和 `logs/` 不进入版本库

## 最终验证

Windows 验证命令：

```powershell
.\scripts\verify.ps1
```

WSL2 验证命令：

```bash
./scripts/verify.sh
```

2026-08-06 的 Windows 最终验证结果：

- 最小 orchestrator 工作流状态为 `completed`
- 7 个 smoke 检查通过
- 9 个 unittest 模块共 34 个测试通过
- 人工审核、发布回执、队列筛选和归档测试通过
- `git diff --check` 通过

本次未执行 WSL2、Hyper-V/systemd 和真实外部服务验证，因此不能把这些项目标记为当前运行验证通过。

## 启动顺序

1. 按 `docs/install.md` 准备 Python 环境
2. 从 `.env.example` 创建本地 `.env`，默认保持 dry-run/mock
3. 执行 `scripts/verify.ps1` 或 `scripts/verify.sh`
4. 功能演示执行 `scripts/demo.ps1` 或 `scripts/demo.sh`
5. 正常运行执行 `scripts/run-dev.ps1` 或 `scripts/run-dev.sh`
6. 在飞书或导出目录完成人工审核
7. 人工发布后使用 `services/orchestrator/src/publish.py` 写回结果

## 模块输入、输出与失败处理

| 模块 | 输入 | 输出 | 依赖 | 失败处理 |
| --- | --- | --- | --- | --- |
| `orchestrator` | 主题、运行配置 | 任务状态、任务索引、审核目录 | Feishu adapter、Video provider | 写入 `failed` 状态和错误摘要 |
| `feishu_bridge` | 审核消息、飞书配置 | dry-run 或真实发送结果 | 可替换 adapter | 分类记录配置、权限、网络和超时错误 |
| `video_gateway` | 任务与视频配置 | mock 或 API 视频结果 | 可替换 provider | 记录请求摘要、响应和错误分类 |
| `review_workflow` | `task_id`、审核决定 | 审核回执、分发准备包 | 任务索引 | 拒绝非法状态流转或未知任务 |
| `publishing` | `task_id`、平台、人工结果 | 发布回执、队列视图 | 发布准备包 | 拒绝非法平台、状态流转或未知任务 |

## 归档前检查

1. 执行最终验证
2. 执行 `git diff --check`
3. 执行 `git status --short`
4. 确认 `.env`、`.venv/`、`data/`、`exports/`、`logs/` 未被 staged
5. 复核 phase-07 源码、测试与中文文档差异
6. 项目负责人已批准创建最终提交并同步至 GitHub 私有仓库；标签仍需另行决定

Codex 不会在没有明确授权时提交、推送或创建标签。

## 回滚

源码回滚应以最终提交前的 `phase-06.5` 基线 `72f8ed0` 为参照，通过独立分支或备份恢复，不使用强制重置覆盖未提交工作。

运行数据回滚应先备份 `.env`、`data/`、`exports/` 和 `logs/`，再按 `docs/backup-and-restore.md` 执行。不得使用源码回滚覆盖运行数据。

## 结项后的维护规则

- 只处理安全、故障和必要兼容性问题
- 不改变自动发布禁用边界
- 不在没有备份的情况下修改运行数据
- 不把新功能混入最终版本维护提交
- 若要恢复功能开发，应重新立项并重新确认权限和范围
