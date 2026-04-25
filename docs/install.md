# 安装说明

## 目标

phase-01.5 的目标是在不联网安装项目依赖的前提下，让本项目具备本地最小可运行闭环。

## 前置条件

- Windows PowerShell 或 WSL2 Shell
- Python 3.10 及以上

## 环境变量

1. 复制 `.env.example` 为 `.env`
2. 第一阶段与 phase-01.5 可先沿用默认值
3. 不要在仓库中写入真实密钥

## Windows 如何手动准备 Python 环境

1. 打开 PowerShell
2. 运行 `python --version`
3. 如果命令不可用，再尝试 `py --version`
4. 如果两者都不可用，请手动安装 Python 3.10 或以上版本
5. 安装时勾选“Add Python to PATH”
6. 安装完成后重新打开 PowerShell
7. 再次运行 `python --version` 或 `py --version`

可选虚拟环境步骤：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

说明：
- 当前 `requirements.txt` 默认不包含第三方依赖
- 即使不执行安装，只要本机已有 Python，也可以运行当前最小闭环

## WSL2 如何手动准备 Python 环境

1. 打开 WSL2 终端
2. 运行 `python3 --version`
3. 如果命令不可用，请手动在你的 Linux 发行版中安装 Python 3.10 或以上版本
4. 安装完成后再次运行 `python3 --version`

可选虚拟环境步骤：

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

说明：
- 当前 `requirements.txt` 默认不包含第三方依赖
- 即使不执行安装，只要本机已有 Python，也可以运行当前最小闭环

## 启动顺序

1. 检查 Python 是否存在
2. 执行验证脚本，确认目录和最小闭环可运行
3. 执行开发运行脚本，生成待审核结果与状态文件
4. 查看 `exports/pending_review/` 和 `data/state/workflow_state.json`

## Windows 入口命令

```powershell
python --version
.\scripts\verify.ps1
.\scripts\run-dev.ps1
.\scripts\start-feishu-bridge.ps1
.\scripts\start-video-gateway.ps1
```

## WSL2 入口命令

```bash
python3 --version
./scripts/verify.sh
./scripts/run-dev.sh
./scripts/start-feishu-bridge.sh
./scripts/start-video-gateway.sh
```

## 失败处理

- 如果缺少 Python，请先按上文手动准备环境
- 如果脚本报路径错误，请确认当前目录为项目根目录
- 如果输出文件未生成，请先执行 `docs/verification.md` 中的步骤排查
