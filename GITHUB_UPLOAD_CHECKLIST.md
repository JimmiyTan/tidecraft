# GitHub 上传前检查清单

## 自动检查

- [ ] 双击 `一键GitHub上传前检查.cmd`
- [ ] 隐私检查显示高风险为 0
- [ ] 完整验证全部通过
- [ ] `git diff --check` 通过
- [ ] `.env`、`data/`、`exports/`、`logs/` 保持 ignored

## 人工隐私复核

- [ ] `.env`、`.env.local`、真实配置和凭据文件未进入候选文件
- [ ] App Secret、API Key、Token、Webhook、Cookie、密码和私钥未出现
- [ ] 客户名称、真实任务主题、手机号、邮箱和内部链接未出现
- [ ] 截图、日志、导出文件和运行数据未进入候选文件
- [ ] 文档示例全部为占位值、保留域名或模拟数据
- [ ] Git 历史没有曾经提交的有效密钥；如曾出现，已经轮换并清理历史

## 代码与范围复核

- [ ] Phase 07 是最终范围，没有启用自动正式发布
- [ ] 发布适配器仍是占位实现
- [ ] 客户演示只监听 `127.0.0.1`
- [ ] 没有新增未经批准的依赖、部署配置或系统设置
- [ ] Windows 与 WSL2 脚本用途和失败处理已写入说明书

## 精确暂存

- [ ] 使用 `git status --short` 获取候选文件
- [ ] 逐个检查 `git diff -- <file>`
- [ ] 使用精确文件列表执行 `git add -- <file1> <file2> ...`
- [ ] 不使用 `git add .`
- [ ] 暂存后执行 `git diff --cached --check`
- [ ] 暂存后再次运行隐私检查
- [ ] 使用 `git diff --cached --stat` 和 `git diff --cached` 完成人工复核

## 提交与上传

- [x] 已确认目标 GitHub 仓库地址为 `JimmiyTan/tidecraft`
- [x] 项目负责人已明确批准改为公开仓库
- [x] 已确认当前不添加开源许可证，仓库公开可见但未授予明确的开源使用许可
- [x] 项目负责人明确批准提交
- [ ] 提交信息说明 Phase 07、客户 Demo 和安全边界
- [ ] 提交后再次执行 `git status --short`
- [x] 项目负责人明确批准推送
- [x] 远程仓库可见性和目标分支已确认
- [ ] 推送后在 GitHub 页面确认 `.env` 和运行数据不存在

## 建议提交信息

```text
feat: finalize phase 07 customer demo and safe release tooling
```

本清单只用于准备，不构成提交或推送授权。
