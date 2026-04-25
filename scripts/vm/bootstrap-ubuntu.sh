#!/usr/bin/env bash
# Ubuntu 虚拟机初始化脚本。
# 用途：
# 1. 安装项目运行所需的最小基础工具。
# 2. 创建 /opt/lobster-farm 目录并赋权给当前用户。
# 3. 输出后续迁移项目与初始化 Python 环境的命令提示。
# 依赖：
# - 需要在 Ubuntu Server 24.04 虚拟机内运行。
# - 需要当前用户具备 sudo 权限。
# 输入：
# - 无命令行参数，默认操作 /opt/lobster-farm。
# 输出：
# - 安装基础依赖。
# - 打印项目迁移、虚拟环境初始化和验证命令。
# 失败处理：
# - 任一步失败即退出，避免半完成状态继续执行。

set -euo pipefail

PROJECT_DIR="/opt/lobster-farm"

echo "开始初始化 Ubuntu 虚拟机基础环境..."

sudo apt-get update
sudo apt-get install -y \
  python3 \
  python3-venv \
  python3-pip \
  git \
  curl \
  unzip \
  openssh-server

sudo mkdir -p "${PROJECT_DIR}"
sudo chown -R "${USER}:${USER}" "${PROJECT_DIR}"

echo
echo "基础环境已准备完成。"
echo "项目目录：${PROJECT_DIR}"
echo
echo "后续建议顺序："
echo "1. 将项目复制到虚拟机的 ${PROJECT_DIR}"
echo "2. 进入项目目录并创建虚拟环境"
echo "3. 安装项目依赖"
echo "4. 执行 verify.sh 与 run-dev.sh"
echo
echo "可参考命令："
echo "cd ${PROJECT_DIR}"
echo "python3 -m venv .venv"
echo "source .venv/bin/activate"
echo "pip install -r requirements.txt"
echo "bash ./scripts/verify.sh"
echo "bash ./scripts/run-dev.sh"
echo
echo "若需从宿主机迁移项目，可任选一种方式："
echo "方式 A：使用 scp 上传压缩包后在虚拟机内解压"
echo "方式 B：使用 git 仓库拉取代码后再补充 .env"
echo
echo "若使用 scp，可参考："
echo "scp lobster-farm.zip <ubuntu-user>@<vm-ip>:~/"
echo "unzip ~/lobster-farm.zip -d ${PROJECT_DIR}"
