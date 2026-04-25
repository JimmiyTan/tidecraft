"""飞书桥接 smoke 验证。"""

import subprocess
import sys
from pathlib import Path


def main() -> int:
    """执行飞书桥接最小验证。"""
    project_root = Path(__file__).resolve().parents[2]
    command = [
        sys.executable,
        str(project_root / "services" / "feishu-bridge" / "src" / "main.py"),
        "--topic",
        "龙虾养殖",
    ]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    if "人工审核消息" not in completed.stdout:
        raise SystemExit("飞书桥接 smoke 验证失败。")
    print("smoke_feishu: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
