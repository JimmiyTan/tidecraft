"""内容流水线 smoke 验证。"""

import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    """执行内容流水线并验证产物结构。"""
    project_root = Path(__file__).resolve().parents[2]
    command = [
        sys.executable,
        str(project_root / "src" / "lobster_farm" / "content_pipeline" / "app.py"),
        "--topic",
        "AI分身内容增长",
    ]
    completed = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    task_id_line = next(
        line for line in completed.stdout.splitlines() if line.startswith("任务 ID：")
    )
    task_id = task_id_line.split("：", 1)[1].strip()
    task_dir = project_root / "exports" / "content_pipeline" / task_id
    required_files = [
        "candidate_pool.json",
        "viral_analysis.json",
        "rewrites.json",
        "review_message.json",
        "pipeline_state.json",
        "douyin/title.txt",
        "douyin/caption.txt",
        "douyin/hashtags.json",
        "wechat_channels/title.txt",
        "wechat_channels/caption.txt",
        "wechat_channels/hashtags.json",
    ]
    for file_name in required_files:
        if not (task_dir / file_name).exists():
            raise SystemExit(f"内容流水线 smoke 失败：缺少 {file_name}")
    rewrites = json.loads((task_dir / "rewrites.json").read_text(encoding="utf-8"))
    if len(rewrites) != 3:
        raise SystemExit("内容流水线 smoke 失败：改写版本不是 3 个。")
    review = json.loads((task_dir / "review_message.json").read_text(encoding="utf-8"))
    if "原始热点链接" not in review["message"]:
        raise SystemExit("内容流水线 smoke 失败：审核消息缺少原始热点链接。")
    print("smoke_content_pipeline: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
