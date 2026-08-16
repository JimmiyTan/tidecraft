# 项目功能演示说明

如需面向客户进行浏览器展示，请使用 `docs/customer-demo.md` 中的前端演示入口。

## 演示目标

用一条命令展示 `lobster-farm` 的 Phase 07 最终闭环：

1. 输入演示主题
2. 生成 5 条候选选题与脚本
3. 生成飞书 dry-run 审核消息和视频 mock 结果
4. 模拟人工审核通过
5. 生成抖音、视频号发布准备包
6. 模拟写回两个平台的人工发布结果
7. 归档任务并生成演示摘要

Demo 不会发送真实飞书消息、调用真实视频服务或执行真实平台发布。

## Windows 一键演示

最简单的方式：在项目根目录双击 `一键运行演示.cmd`。

该按键会自动运行完整演示，并在结束后保留窗口供查看结果。

从项目根目录执行：

```powershell
.\scripts\demo.ps1
```

指定主题和演示操作人：

```powershell
.\scripts\demo.ps1 -Topic "本地餐饮门店如何做短视频" -Operator "演示人"
```

逐步讲解模式：

```powershell
.\scripts\demo.ps1 -Topic "本地餐饮门店如何做短视频" -Operator "演示人" -Guided
```

`-Guided` 会在每个阶段暂停，按 Enter 后继续，适合现场讲解。

## WSL2 一键演示

```bash
./scripts/demo.sh
```

指定主题并启用逐步讲解：

```bash
./scripts/demo.sh --topic "本地餐饮门店如何做短视频" --operator "演示人" --guided
```

## 演示输出

控制台会依次显示：

- 安全模式确认
- 任务 ID、主题和候选选题数量
- 审核目录
- 模拟人工审核结果
- 双平台模拟人工发布回执
- 归档状态
- 最终 JSON 摘要

主要文件位于：

```text
exports/pending_review/<task_id>/
  summary.txt
  review_decision.json
  publish_result.json
  publish_note.txt
  demo_summary.json
  distribution/
    publish_checklist.txt
    douyin/
    wechat_channels/
```

## 安全机制

Demo 入口固定读取 `.env.example`，不会读取本地真实 `.env`，并在运行前再次校验：

- `RUN_MODE=dry-run`
- `FEISHU_ADAPTER=dry-run`
- `VIDEO_PROVIDER=mock`

任一配置不满足时，Demo 会拒绝运行。

如果 `.env.example` 意外包含非空 App ID、App Secret、Chat ID 或 Video API Key，Demo 同样会拒绝运行，并且不会打印凭据内容。

人工发布链接使用 `demo.invalid` 保留域名，只作为回执示例写入本地 JSON，不发起网络请求。发布适配器不会被调用。

## 输入、输出、依赖与失败处理

- 输入：主题、演示操作人、可选逐步讲解开关
- 输出：审核包、分发准备包、发布回执、归档队列和 `demo_summary.json`
- 依赖：项目现有 Python 环境和 Phase 07 模块
- 失败处理：不安全配置、工作流失败、非法状态流转或文件写入失败时返回非零退出码

## 演示前建议

1. 执行 `.\scripts\verify.ps1`
2. 确认验证全部通过
3. 关闭包含真实账号信息的窗口
4. 使用 `-Guided` 按阶段讲解
5. 演示完成后展示 `demo_summary.json` 和 `distribution/` 目录

## 回滚与清理

Demo 不修改源码和真实配置，只在 Git ignored 的 `data/`、`exports/`、`logs/` 中生成运行数据。

如需清理，先备份需要保留的演示任务，再按输出的 `task_id` 精确处理对应任务目录和状态记录。不要整体删除运行数据目录。
