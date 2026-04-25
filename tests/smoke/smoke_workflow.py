"""工作流 smoke 验证。"""

import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    """执行工作流最小验证。"""
    project_root = Path(__file__).resolve().parents[2]
    command = [
        sys.executable,
        str(project_root / "services" / "orchestrator" / "src" / "main.py"),
        "--topic",
        "龙虾养殖",
    ]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    if "状态：completed" not in completed.stdout:
        raise SystemExit("工作流 smoke 验证失败。")
    state_file = project_root / "data" / "state" / "workflow_state.json"
    if not state_file.exists():
        raise SystemExit("工作流 smoke 验证失败：未生成状态文件。")
    state = json.loads(state_file.read_text(encoding="utf-8"))
    task_dir = Path(state["task_dir"])
    required_files = [
        "topic_list.json",
        "scripts.json",
        "review_message.json",
        "video_result.json",
        "summary.txt",
    ]
    for file_name in required_files:
        if not (task_dir / file_name).exists():
            raise SystemExit(f"工作流 smoke 验证失败：缺少 {file_name}。")
    print("smoke_workflow: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
