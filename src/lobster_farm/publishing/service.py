"""人工发布回执写回服务。"""

import json
from datetime import datetime
from pathlib import Path

from lobster_farm.common.config import AppConfig
from lobster_farm.publishing.models import (
    PublishPlatform,
    PublishReceipt,
    PublishStatus,
    assert_publish_transition,
)
from lobster_farm.review_workflow.publish_queue import refresh_publish_queue_views


class PublishWritebackError(ValueError):
    """发布回执写回错误。"""


def _read_json(file_path: Path) -> dict[str, object]:
    return json.loads(file_path.read_text(encoding="utf-8"))


def _write_json(file_path: Path, payload: object) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _load_task_record(index_file: Path, task_id: str) -> dict[str, object]:
    if not index_file.exists():
        raise PublishWritebackError("任务索引文件不存在，无法执行发布回写。")
    payload = _read_json(index_file)
    for item in payload.get("tasks", []):
        if item.get("task_id") == task_id:
            return item
    raise PublishWritebackError(f"未找到 task_id={task_id} 对应任务。")


def _load_queue(queue_file: Path) -> dict[str, list[dict[str, object]]]:
    if not queue_file.exists():
        return {"items": []}
    return _read_json(queue_file)  # type: ignore[return-value]


def _normalize_platform(platform: str) -> str:
    try:
        return PublishPlatform(platform).value
    except ValueError as exc:
        raise PublishWritebackError(f"不支持的平台：{platform}") from exc


def _normalize_publish_status(status: str) -> str:
    try:
        return PublishStatus(status).value
    except ValueError as exc:
        raise PublishWritebackError(f"不支持的发布状态：{status}") from exc


def _find_queue_item(
    queue_items: list[dict[str, object]],
    task_id: str,
    platform: str,
) -> dict[str, object]:
    for item in queue_items:
        if item.get("task_id") == task_id and item.get("platform") == platform:
            return item
    raise PublishWritebackError(
        f"未找到 task_id={task_id} platform={platform} 的待发布记录。"
    )


def _read_publish_results(task_dir: Path, task_id: str) -> dict[str, object]:
    result_file = task_dir / "publish_result.json"
    if result_file.exists():
        return _read_json(result_file)
    return {"task_id": task_id, "platforms": {}}


def _write_publish_note(task_dir: Path, receipt: PublishReceipt) -> None:
    note_file = task_dir / "publish_note.txt"
    existing = note_file.read_text(encoding="utf-8") if note_file.exists() else ""
    block = [
        "",
        f"平台：{receipt.platform}",
        f"发布状态：{receipt.publish_status}",
        f"发布人：{receipt.published_by or '未填写'}",
        f"发布时间：{receipt.published_at}",
        f"发布链接：{receipt.publish_url or '未填写'}",
        f"发布备注：{receipt.publish_note or '无'}",
    ]
    note_file.write_text(existing.rstrip() + "\n".join(block) + "\n", encoding="utf-8")


def _update_task_publish_summary(
    config: AppConfig,
    task_id: str,
    platform: str,
    receipt: PublishReceipt,
) -> None:
    """在任务索引中保留发布摘要，方便列表查询。"""
    payload = _read_json(config.orchestrator_task_index_file)
    for item in payload.get("tasks", []):
        if item.get("task_id") != task_id:
            continue
        publish_statuses = item.setdefault("publish_statuses", {})
        if isinstance(publish_statuses, dict):
            publish_statuses[platform] = receipt.publish_status
        item["updated_at"] = datetime.now().isoformat()
        break
    _write_json(config.orchestrator_task_index_file, payload)


def list_publish_queue(
    config: AppConfig,
    status: str = "",
    platform: str = "",
) -> list[dict[str, object]]:
    """查询发布队列，支持按状态和平台筛选。"""
    queue_file = config.orchestrator_task_index_file.parent / "publish_queue.json"
    payload = _load_queue(queue_file)
    items = list(payload.get("items", []))
    if status:
        wanted_status = _normalize_publish_status(status)
        items = [item for item in items if item.get("publish_status") == wanted_status]
    if platform:
        wanted_platform = _normalize_platform(platform)
        items = [item for item in items if item.get("platform") == wanted_platform]
    items.sort(
        key=lambda item: str(
            item.get("published_at") or item.get("approved_at") or item.get("updated_at") or ""
        ),
        reverse=True,
    )
    return items


def get_task_publish_status(config: AppConfig, task_id: str) -> dict[str, object]:
    """查询单个任务的双平台发布状态。"""
    _load_task_record(config.orchestrator_task_index_file, task_id)
    queue_file = config.orchestrator_task_index_file.parent / "publish_queue.json"
    payload = _load_queue(queue_file)
    items = [
        item for item in payload.get("items", []) if item.get("task_id") == task_id
    ]
    if not items:
        raise PublishWritebackError(f"task_id={task_id} 尚未进入发布队列。")
    return {"task_id": task_id, "platforms": items}


def write_publish_result(
    config: AppConfig,
    task_id: str,
    platform: str,
    publish_status: str,
    published_by: str,
    publish_url: str,
    publish_note: str,
    published_at: str = "",
) -> dict[str, object]:
    """按 task_id 与平台写回人工发布结果。"""
    platform_value = _normalize_platform(platform)
    status_value = _normalize_publish_status(publish_status)
    record = _load_task_record(config.orchestrator_task_index_file, task_id)
    task_dir = Path(str(record.get("task_dir", "")))
    if not task_dir.exists():
        raise PublishWritebackError(f"任务目录不存在：{task_dir}")

    queue_file = config.orchestrator_task_index_file.parent / "publish_queue.json"
    queue_payload = _load_queue(queue_file)
    queue_items = queue_payload.get("items", [])
    queue_item = _find_queue_item(queue_items, task_id, platform_value)
    current_status = str(
        queue_item.get("publish_status", PublishStatus.READY_TO_PUBLISH.value)
    )
    assert_publish_transition(current_status, status_value)

    receipt = PublishReceipt(
        task_id=task_id,
        platform=platform_value,
        publish_status=status_value,
        published_by=published_by,
        published_at=published_at or datetime.now().isoformat(),
        publish_url=publish_url,
        publish_note=publish_note,
    )

    queue_item.update(receipt.to_dict())
    queue_item["updated_at"] = datetime.now().isoformat()
    _write_json(queue_file, queue_payload)
    refresh_publish_queue_views(config.orchestrator_task_index_file)

    result_payload = _read_publish_results(task_dir, task_id)
    platforms = result_payload.setdefault("platforms", {})
    if isinstance(platforms, dict):
        platforms[platform_value] = receipt.to_dict()
    _write_json(task_dir / "publish_result.json", result_payload)
    _write_publish_note(task_dir, receipt)
    _update_task_publish_summary(config, task_id, platform_value, receipt)

    return {
        "task_id": task_id,
        "platform": platform_value,
        "publish_status": status_value,
        "task_dir": task_dir.as_posix(),
        "publish_result_file": (task_dir / "publish_result.json").as_posix(),
        "publish_note_file": (task_dir / "publish_note.txt").as_posix(),
    }


def archive_task(config: AppConfig, task_id: str) -> dict[str, object]:
    """归档已完成或失败的发布任务。"""
    _load_task_record(config.orchestrator_task_index_file, task_id)
    queue_file = config.orchestrator_task_index_file.parent / "publish_queue.json"
    queue_payload = _load_queue(queue_file)
    queue_items = queue_payload.get("items", [])
    task_items = [item for item in queue_items if item.get("task_id") == task_id]
    if not task_items:
        raise PublishWritebackError(f"task_id={task_id} 尚未进入发布队列。")

    archived_at = datetime.now().isoformat()
    for item in task_items:
        current_status = str(item.get("publish_status", "ready_to_publish"))
        assert_publish_transition(current_status, PublishStatus.ARCHIVED.value)
        item["publish_status"] = PublishStatus.ARCHIVED.value
        item["archived_at"] = archived_at
        item["updated_at"] = archived_at

    _write_json(queue_file, queue_payload)
    refresh_publish_queue_views(config.orchestrator_task_index_file)

    record = _load_task_record(config.orchestrator_task_index_file, task_id)
    task_dir = Path(str(record.get("task_dir", "")))
    result_payload = _read_publish_results(task_dir, task_id)
    platforms = result_payload.setdefault("platforms", {})
    if isinstance(platforms, dict):
        for item in task_items:
            platform = str(item.get("platform", ""))
            platform_payload = platforms.setdefault(platform, {})
            if isinstance(platform_payload, dict):
                platform_payload["publish_status"] = PublishStatus.ARCHIVED.value
                platform_payload["archived_at"] = archived_at
    result_payload["archived_at"] = archived_at
    _write_json(task_dir / "publish_result.json", result_payload)

    return {
        "task_id": task_id,
        "publish_status": PublishStatus.ARCHIVED.value,
        "archived_at": archived_at,
        "task_dir": task_dir.as_posix(),
    }
