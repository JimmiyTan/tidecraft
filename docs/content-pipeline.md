# 内容流水线说明

## 阶段目标

本阶段新增“爆款结构拆解 + 原创改写 + AI 分身演绎 + 双平台分发准备”流水线。

系统不会复刻原视频逐字脚本，也不会自动发布。

## 流程

1. 热点雷达生成候选池
2. 爆款拆解输出结构化爆点
3. 原创改写生成三版 AI 分身剧情
4. 生成抖音和视频号两套分发准备包
5. 发送飞书审核消息

## 模块

- `trend_radar`：热点雷达
- `viral_analyzer`：爆款结构拆解
- `rewrite_engine`：原创改写
- `distribution`：双平台分发包
- `content_pipeline`：流水线编排

## 产物目录

每次运行会生成：

```text
exports/content_pipeline/<task_id>/
  candidate_pool.json
  viral_analysis.json
  rewrites.json
  review_message.json
  pipeline_state.json
  douyin/
    title.txt
    caption.txt
    hashtags.json
  wechat_channels/
    title.txt
    caption.txt
    hashtags.json
```

## 运行命令

```powershell
.\scripts\run-content-pipeline.ps1
```

## 验证命令

```powershell
.\scripts\verify.ps1
```

## 合规要求

- 只复用爆点结构，不复刻原脚本
- 默认不自动发布
- 所有异常必须可追踪到 `task_id`
- 真实热点抓取后续应通过可替换 source adapter 接入
