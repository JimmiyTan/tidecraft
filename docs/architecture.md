# 架构说明

## 阶段目标

phase-04 将安全闭环升级为可接真实飞书和真实视频 API 的审核链路。系统仍不调用任何短视频平台发布能力。

## 模块结构

### common

- 输入：`.env.example`、可选 `.env`
- 输出：统一 `AppConfig`
- 依赖：Python 标准库
- 失败处理：配置不合法时抛出 `ConfigError`

### feishu_bridge

- 输入：主题、选题、脚本、运行配置
- 输出：审核消息和发送结果结构体
- 依赖：adapter 抽象层
- 失败处理：dry-run 永不真实发送；real adapter 当前只做参数校验和请求构造

### video_gateway

- 输入：任务 ID、主题、审核条目、运行配置
- 输出：统一视频任务结果结构
- 依赖：provider 注册机制
- 失败处理：mock provider 写本地文件；api provider 支持提交、轮询、超时、重试和错误分类

### orchestrator

- 输入：主题
- 输出：任务目录、状态文件、任务索引、人工审核摘要
- 依赖：Feishu adapter、Video provider、状态机
- 失败处理：失败状态写入任务文件和最新状态文件

## 数据流

1. `orchestrator` 创建任务 ID
2. 进入 `created`
3. 生成选题，进入 `topics_generated`
4. 生成脚本，进入 `scripts_generated`
5. 生成审核消息并调用 Feishu adapter，进入 `review_message_generated`
6. 调用 Video provider，进入 `video_generated`
7. 导出审核包，进入 `completed`
8. 任一步失败，进入 `failed`

## 可替换接口

- Feishu：`src/lobster_farm/feishu_bridge/adapters/`
- Video：`src/lobster_farm/video_gateway/providers/`

## 安全边界

- 默认不读取真实密钥
- 默认不发送真实飞书消息
- 默认不调用真实视频 API
- 默认不发布到任何平台
