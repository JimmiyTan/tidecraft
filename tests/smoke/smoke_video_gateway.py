"""视频网关 smoke 验证。"""

import subprocess
import sys
from pathlib import Path


def main() -> int:
    """执行视频网关最小验证。"""
    project_root = Path(__file__).resolve().parents[2]
    command = [
        sys.executable,
        str(project_root / "services" / "video-gateway" / "src" / "main.py"),
        "--topic",
        "龙虾养殖",
        "--task-id",
        "smoke_video_gateway",
        "--review-items-json",
        '[{"title":"龙虾养殖：新手避坑入门","script_text":"这是一个脚本占位结果。"}]',
    ]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    if "provider=mock" not in completed.stdout:
        raise SystemExit("视频网关 smoke 验证失败。")
    output_file = (
        project_root
        / "exports"
        / "pending_review"
        / "smoke_video_gateway"
        / "video_result.json"
    )
    if not output_file.exists():
        raise SystemExit("视频网关 smoke 验证失败：未生成 video_result.json。")
    print("smoke_video_gateway: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
