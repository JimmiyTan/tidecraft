"""状态文件写入工具。"""

import json
from datetime import datetime
from pathlib import Path

from lobster_farm.orchestrator.models import WorkflowResult


def _result_to_payload(result: WorkflowResult) -> dict[str, object]:
    """将工作流结果转换为可序列化结构。"""
    return {
        "task_id": result.task_id,
        "topic": result.topic,
        "created_at": result.created_at,
        "candidate_titles": result.candidate_titles,
        "scripts": result.scripts,
        "review_message": result.review_message,
        "review_send_status": result.review_send_status,
        "video_provider": result.video_provider,
        "video_provider_status": result.video_provider_status,
        "video_remote_task_id": result.video_remote_task_id,
        "export_file": result.export_file.as_posix() if result.export_file else "",
        "task_dir": result.task_dir.as_posix() if result.task_dir else "",
        "status": result.status,
        "review_status": result.review_status,
        "reviewed_at": result.reviewed_at,
        "reviewed_by": result.reviewed_by,
        "review_note": result.review_note,
        "error_message": result.error_message,
        "updated_at": datetime.now().isoformat(),
    }


def write_state(state_file: Path, result: WorkflowResult) -> None:
    """写入兼容的最新状态文件。"""
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(
        json.dumps(_result_to_payload(result), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def write_task_state(task_state_dir: Path, result: WorkflowResult) -> Path:
    """写入单个任务状态文件。"""
    task_state_dir.mkdir(parents=True, exist_ok=True)
    task_file = task_state_dir / f"{result.task_id}.json"
    task_file.write_text(
        json.dumps(_result_to_payload(result), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return task_file


def append_task_index(index_file: Path, result: WorkflowResult, task_file: Path) -> None:
    """更新任务列表索引文件。"""
    index_file.parent.mkdir(parents=True, exist_ok=True)
    if index_file.exists():
        payload = json.loads(index_file.read_text(encoding="utf-8"))
    else:
        payload = {"tasks": []}
    existing_created_at = ""
    for task in payload.get("tasks", []):
        if task.get("task_id") == result.task_id:
            existing_created_at = str(task.get("created_at", ""))
            break
    new_item = {
        "task_id": result.task_id,
        "topic": result.topic,
        "created_at": existing_created_at or result.created_at,
        "status": result.status,
        "review_status": result.review_status,
        "reviewed_at": result.reviewed_at,
        "reviewed_by": result.reviewed_by,
        "review_note": result.review_note,
        "task_file": task_file.as_posix(),
        "task_dir": result.task_dir.as_posix() if result.task_dir else "",
        "updated_at": datetime.now().isoformat(),
    }
    tasks = payload.get("tasks", [])
    for index, task in enumerate(tasks):
        if task.get("task_id") == result.task_id:
            tasks[index] = new_item
            break
    else:
        tasks.append(new_item)
    payload["tasks"] = tasks
    index_file.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
