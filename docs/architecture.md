# 架构说明

## 最终架构目标

phase-07 最终版本提供从主题生成、飞书审核、视频结果、人工审核、发布准备到人工发布回执的完整闭环。系统仍不调用任何短视频平台真实发布能力。

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
- 输出：任务目录、状态文件、任务索引、人工审核摘要、发布队列
- 依赖：Feishu adapter、Video provider、状态机、审核与发布服务
- 失败处理：失败状态写入任务文件和最新状态文件

### review_workflow

- 输入：任务 ID、审核状态、审核人和备注
- 输出：审核回执、双平台分发准备包、待发布队列
- 依赖：任务索引、distribution 包生成器
- 失败处理：拒绝未知任务、非法审核状态和非法状态流转

### publishing

- 输入：任务 ID、平台、人工发布状态、链接和备注
- 输出：发布回执、发布备注、按状态拆分的队列视图
- 依赖：任务索引、发布队列、占位发布适配器
- 失败处理：拒绝未知任务、不支持的平台和非法发布状态流转

### distribution

- 输入：审核通过的脚本与素材信息
- 输出：抖音、视频号发布准备包和人工检查清单
- 依赖：文件系统
- 失败处理：仅生成本地准备材料，不执行平台提交

## 数据流

1. `orchestrator` 创建任务 ID
2. 进入 `created`
3. 生成选题，进入 `topics_generated`
4. 生成脚本，进入 `scripts_generated`
5. 生成审核消息并调用 Feishu adapter，进入 `review_message_generated`
6. 调用 Video provider，进入 `video_generated`
7. 导出审核包，工作流进入 `completed`，等待人工审核
8. 人工审核写回 `approved`、`rejected` 或 `needs_edit`
9. `approved` 任务生成双平台 distribution 包并进入 `ready_to_publish`
10. 人工发布后写回 `manually_published` 或 `publish_failed`
11. 满足归档条件后写回 `archived`
12. 自动工作流任一步失败时进入 `failed`

## 可替换接口

- Feishu：`src/lobster_farm/feishu_bridge/adapters/`
- Video：`src/lobster_farm/video_gateway/providers/`
- Publishing：`src/lobster_farm/publishing/adapters/`

## 安全边界

- 默认不读取真实密钥
- 默认不发送真实飞书消息
- 默认不调用真实视频 API
- 默认不发布到任何平台
- 发布适配器固定为占位实现并返回未接受结果
- 人工审核和人工发布结果必须按 `task_id` 落盘
