# CURRENT_STATUS

## 当前项目状态

项目名称：`lobster-farm`

最终阶段：`phase-07`

项目状态：`已完成功能收尾，冻结维护，已同步 GitHub 公开仓库`

结项日期：`2026-08-06`

当前定位：可长期运行的人工审核内容中台，已补齐人工发布回执闭环。

系统当前仍保持安全边界：

- 不支持自动发布到抖音、视频号或其他短视频平台
- 不调用抖音或视频号真实发布接口
- 不把真实密钥、Webhook、密码或服务器账号写入仓库
- 默认仍可使用 dry-run / mock 模式完成本地验证
- 真实飞书与真实视频 API 只通过 `.env` 配置启用

## 已完成内容

### 基础工程

- Python 工程基础文件已建立
- 统一配置加载已建立
- 统一路径处理已建立
- 统一日志初始化已建立
- Windows / Linux 启动脚本已建立
- Windows / Linux 验证脚本已建立

### 内容生产闭环

- 支持输入主题
- 支持生成候选选题
- 支持生成脚本占位结果
- 支持生成审核消息
- 支持视频 mock provider
- 支持真实视频 API provider 骨架与配置校验
- 支持任务状态落盘
- 支持任务索引落盘
- 支持任务审核目录导出

### 飞书审核

- 支持 Feishu dry-run adapter
- 支持 Feishu real adapter
- 支持真实飞书审核消息发送
- 支持飞书配置校验
- 日志中不输出完整密钥
- 审核消息包含 `task_id`、审核目录和审核摘要

### 审核确认机制

- 支持审核状态：`pending_review`、`approved`、`rejected`、`needs_edit`
- 支持按 `task_id` 写回审核结果
- 支持非法审核状态流转校验
- 审核结果写入 `review_decision.json`
- 审核备注写入 `review_note.txt`
- approved 后生成双平台 distribution 发布准备包

### 发布准备与回执

- 支持发布状态：`ready_to_publish`、`manually_published`、`publish_failed`、`archived`
- 支持按平台写回人工发布结果
- 支持平台：`douyin`、`wechat_channels`
- 支持发布结果写入 `publish_result.json`
- 支持发布备注写入 `publish_note.txt`
- 支持发布队列按平台和状态筛选
- 已新增发布适配器设计稿，但不执行真实发布

### 常驻运行

- 支持 Hyper-V Ubuntu 虚拟机部署
- 支持 systemd service + timer 方案
- 当前目标运行频率：每天北京时间 9 点执行一次
- 支持防重入、运行记录和失败记录

### 项目演示

- 支持 Windows / WSL2 一键离线演示
- 支持指定主题与演示操作人
- 支持逐阶段暂停讲解
- Demo 固定使用 dry-run、Feishu dry-run 和 Video mock
- 支持展示审核、分发准备、人工发布回执和归档完整闭环
- 演示结果写入 `demo_summary.json`
- 支持只监听本机地址的客户前端演示页面
- 支持一键启动浏览器客户演示

### 发布前工具

- 支持一键完整验证
- 支持一键隐私与密钥检查
- 支持一键 GitHub 上传前总检查
- 支持安全停止客户演示服务
- 已提供中文使用说明书、隐私审计报告和 GitHub 上传清单
- 所有准备工具均不执行暂存、提交或推送

## 最终限制与注意事项

- 当前没有自动发布能力，发布仍需人工登录平台完成
- 发布适配器目前是设计稿和占位实现，不调用平台真实接口
- `.env` 必须在部署环境中单独维护，不能提交到 Git
- `data/`、`exports/`、`logs/` 属于运行数据，不应提交到 Git
- 验证脚本会生成本地运行数据，这些数据应保持 ignored
- phase-07 最终变更已由项目负责人批准提交至 GitHub 公开仓库

## 结项决定

- 不启动 phase-08
- 不再扩展运营看板、飞书日报或自动发布能力
- 不接入抖音、视频号或其他平台的真实发布接口
- 后续只接受安全修复、运行故障修复和必要的兼容性维护
- 任何功能重启均应作为新项目或新立项处理，不沿用本项目阶段编号继续扩展

最终交付、验证证据、回滚方式和归档清单见 `PROJECT_CLOSURE.md`。

## 部署架构

### 宿主机

- Windows 宿主机
- Hyper-V 负责运行独立 Ubuntu 虚拟机
- 项目代码可从宿主机打包迁移到虚拟机

### 虚拟机

- Ubuntu Server
- 项目目录：`/opt/lobster-farm`
- Python 虚拟环境：`/opt/lobster-farm/.venv`
- systemd timer 每天北京时间 9 点触发

### 项目内关键目录

- `src/lobster_farm/`：核心 Python 模块
- `services/orchestrator/`：工作流入口和管理 CLI
- `services/feishu-bridge/`：飞书桥接服务骨架
- `services/video-gateway/`：视频 provider 服务骨架
- `scripts/`：Windows / Linux 启动、验证、部署脚本
- `docs/`：安装、运行、审核、发布、运维文档
- `config/`：配置模板
- `data/`：运行状态和队列数据，禁止提交
- `exports/`：任务审核和发布准备产物，禁止提交
- `logs/`：运行日志，禁止提交

### 当前主要数据流

1. systemd timer 或手动命令触发 `run-dev`
2. orchestrator 创建任务并生成内容
3. Feishu bridge 发送或模拟发送审核消息
4. Video gateway 使用 mock 或 API provider 生成视频结果
5. 任务导出到 `exports/pending_review/<task_id>/`
6. 人工审核后通过 CLI 写回审核结果
7. approved 任务生成双平台 distribution 包
8. 人工发布后通过 CLI 写回发布结果
9. 完成后通过 CLI 归档任务

## 敏感信息规则

绝对禁止写入仓库的内容：

- 真实 `.env`
- App Secret
- API Key
- Access Token
- Refresh Token
- Webhook URL
- 服务器账号
- 服务器密码
- SSH 私钥
- 平台登录 Cookie
- 个人浏览器数据

允许提交的内容：

- `.env.example`
- `config/*.example.*`
- 脚本模板
- 文档中的占位示例
- 不含真实密钥的测试数据

敏感信息只能放在：

- 本地 `.env`
- 虚拟机内 `.env`
- 受控的系统环境变量
- 不进入 Git 的部署密钥管理位置

日志规则：

- 不打印完整密钥
- 不打印完整 token
- 不打印完整 Webhook
- 错误信息必须可追踪到 `task_id`
- 对外部服务错误只记录分类、状态码和脱敏摘要

Git 规则：

- 提交前执行 `git status --short`
- 确认 `.env`、`.venv/`、`data/`、`exports/`、`logs/` 未被 staged
- 提交前执行验证脚本
- 不推送真实密钥
- 不提交运行产物

## 常用命令

### 验证

Windows：

```powershell
.\scripts\verify.ps1
```

Linux / WSL2：

```bash
./scripts/verify.sh
```

### 本地运行

Windows：

```powershell
.\scripts\run-dev.ps1
```

Linux / WSL2：

```bash
./scripts/run-dev.sh
```

### 查询待审核任务

```powershell
python .\services\orchestrator\src\list_review_tasks.py --review-status pending_review
```

### 写回审核结果

```powershell
python .\services\orchestrator\src\review.py --task-id "task_xxx" --review-status approved --reviewed-by "审核人" --review-note "审核备注"
```

### 查询待发布任务

```powershell
python .\services\orchestrator\src\publish.py --list --status ready_to_publish
```

### 写回发布结果

```powershell
python .\services\orchestrator\src\publish.py --task-id "task_xxx" --platform douyin --publish-status manually_published --publish-url "发布链接" --published-by "发布人" --publish-note "发布备注"
```

### 归档任务

```powershell
python .\services\orchestrator\src\publish.py --task-id "task_xxx" --archive
```
