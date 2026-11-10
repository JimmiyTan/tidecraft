# Jerry 谭梓健 TideCraft 招聘作品集

## 作品集定位

本目录用于生成一份面向猎聘、BOSS 直聘等招聘平台的 9 页 A4 竖版完整项目作品集。

候选人是作品集主角，`TideCraft 潮生内容工场` 作为已完成 Phase 07 结项的完整项目，用于证明需求分析、架构设计、全栈开发、安全判断、测试和交付能力。

统一事实表达：

> 从需求定义到验收落地，全流程由我独立完成。

## 项目事实摘要

- 项目性质：个人独立开发并完成既定范围结项的本地短视频内容中台
- 目标用户：需要进行内容策划、人工审核和双平台交付准备的内容团队
- 最终形态：Windows / WSL2 可运行的 Python 工作流、浏览器客户演示和命令行管理入口
- 核心闭环：主题输入、候选选题与脚本、审核材料、人工审核、双平台准备、人工回执、归档
- 技术栈：Python 3.10+、HTML/CSS/JavaScript、PowerShell、Bash、JSON 文件状态
- 安全边界：默认 dry-run/mock，不读取浏览器个人数据，不自动正式发布，不在仓库保存真实密钥
- 当前状态：Phase 07 已结项并冻结维护；尚未部署生产环境
- 结项验证：2026-08-06 Windows 最小工作流、7 个 smoke 检查和 34 个单元测试通过
- 未验证：WSL2、Hyper-V/systemd、真实飞书、真实视频 API、生产环境和真实业务效果

## 个人贡献摘要

Jerry 谭梓健独立完成：

1. 需求梳理与业务流程定义
2. 技术选型与模块化架构设计
3. Python 后端、状态机、适配器与文件输出
4. 浏览器客户演示与响应脱敏
5. Windows / WSL2 启动、验证和运维脚本
6. 单元测试、Smoke 检查、隐私审计和中文交付文档

## 文件说明

- `generate_portfolio_pdf.py`：PDF 生成源文件
- `assets/cover-concept.jpg`：封面概念配图
- `assets/challenge-concept.jpg`：核心难题概念配图
- `assets/delivery-concept.jpg`：独立交付概念配图
- `assets/customer-demo-workflow.jpg`：原始客户演示截图副本，仅用于内部对照，不再进入最终 PDF
- `assets/prototype-workflow-sanitized.png`：公开展示用工作流脱敏原型
- `assets/prototype-review-sanitized.png`：公开展示用人工审核脱敏原型
- `assets/prototype-delivery-sanitized.png`：公开展示用交付归档脱敏原型
- `../output/pdf/Jerry_Tan_TideCraft_Portfolio.pdf`：最终 PDF

## 生成方式

在项目根目录运行：

```powershell
python .\portfolio\generate_portfolio_pdf.py
```

## 输入、输出、依赖与失败处理

- 输入：`portfolio/assets/` 图片和生成脚本内经项目文件核对的文案
- 输出：9 页 A4 竖版、可检索文本、无加密的 PDF
- 依赖：Python、ReportLab、Pillow、Windows 微软雅黑字体
- 失败处理：字体或任一图片缺失时中止生成，不交付缺图或乱码版本

## 安全边界

- 不读取 `.env`、`data/`、`exports/` 或 `logs/` 的业务内容
- 不调用真实飞书、视频或短视频平台接口
- 不修改现有业务代码、数据库或生产配置
- 配图为概念视觉，不冒充项目真实截图
- PDF 中的界面重绘和示例数据均有明确标注
- 脱敏原型不包含真实客户、个人信息、账号、内部路径、时间、令牌或生产任务编号
