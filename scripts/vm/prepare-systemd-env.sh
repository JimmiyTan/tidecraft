#!/usr/bin/env bash
# 将项目根目录 .env 清洗为 systemd 与 bash 都可稳定加载的环境文件。
# 作用：
# 1. 去除 UTF-8 BOM。
# 2. 去除 Windows CRLF 中的 \r。
# 3. 仅保留 KEY=VALUE 形式的配置项。

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RUNTIME_DIR="${PROJECT_ROOT}/data/runtime/run-dev"
SOURCE_ENV="${PROJECT_ROOT}/.env"
TARGET_ENV="${RUNTIME_DIR}/systemd.env"

mkdir -p "${RUNTIME_DIR}"

if [[ ! -f "${SOURCE_ENV}" ]]; then
  : > "${TARGET_ENV}"
  exit 0
fi

python3 - "${SOURCE_ENV}" "${TARGET_ENV}" <<'PY'
from pathlib import Path
import sys

source_path = Path(sys.argv[1])
target_path = Path(sys.argv[2])
text = source_path.read_text(encoding="utf-8-sig")
text = text.replace("\r\n", "\n").replace("\r", "\n")
lines = []
for raw_line in text.splitlines():
    line = raw_line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    lines.append(line)
target_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
PY
