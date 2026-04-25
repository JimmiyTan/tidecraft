"""待审核任务查询。"""

import json
from pathlib import Path


def list_review_tasks(index_file: Path, review_status: str = "") -> list[dict[str, object]]:
    """按审核状态和时间倒序列出任务。"""
    if not index_file.exists():
        return []
    payload = json.loads(index_file.read_text(encoding="utf-8"))
    tasks = payload.get("tasks", [])
    if review_status:
        tasks = [item for item in tasks if item.get("review_status", "pending_review") == review_status]
    tasks.sort(
        key=lambda item: str(item.get("created_at") or item.get("updated_at") or ""),
        reverse=True,
    )
    return [
        {
            "task_id": item.get("task_id", ""),
            "topic": item.get("topic", ""),
            "review_status": item.get("review_status", "pending_review"),
            "created_at": item.get("created_at", item.get("updated_at", "")),
            "reviewed_at": item.get("reviewed_at", ""),
            "task_dir": item.get("task_dir", ""),
        }
        for item in tasks
    ]
