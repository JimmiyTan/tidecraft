# Orchestrator 服务说明

## 输入

- 主题

## 输出

- 5 条选题占位结果
- 1 份脚本占位结果
- 1 条飞书消息预览
- 1 个待审核导出文件
- 1 个状态文件

## 依赖

- Feishu Bridge 占位模块
- Video Gateway 占位模块
- Python 标准库

## 失败处理

- 任一步失败后将失败状态写入 `data/state/workflow_state.json`
- 不调用真实外部服务
