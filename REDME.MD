# lobster-farm

> 历史入口文件：本文件保留用于兼容旧引用。当前项目说明以 `README.md`、`CURRENT_STATUS.md` 和 `PROJECT_CLOSURE.md` 为准。

本项目用于搭建一个本地运行的内容自动化系统，当前阶段目标为：

1. 输入主题
2. 生成短视频选题
3. 生成脚本
4. 格式化飞书消息
5. 生成待审核视频结果占位文件
6. 导出到待审核目录

项目已在 phase-07 完成功能收尾，不包含自动正式发布。

## 当前模块
- OpenClaw 主控骨架
- Hermes worker 骨架
- 飞书桥接服务骨架
- 视频网关服务骨架
- 工作流编排服务骨架

## 运行原则
- 仅在当前项目目录工作
- 不写入真实密钥
- 不自动发布
- 先验证骨架，再接真实服务

## 目录说明
详见 `docs/architecture.md`

## 安装说明
详见 `docs/install.md`

## 验证说明
详见 `docs/verification.md`
