# Hermes 骨架说明

## 作用

Hermes 作为内容处理 worker，负责生成选题与脚本的占位结果。

## 输入

- 主题文本
- `config/hermes.example.yaml`
- `workers/hermes/skills/` 下的技能模板

## 输出

- 选题占位结果
- 脚本占位结果

## 依赖

- 本地示例配置
- 本地技能模板

## 失败处理

- 返回占位失败信息
- 不依赖真实模型或外部 API
