"""待发布队列索引生成。"""

import json
from pathlib import Path


def _write_json(file_path: Path, payload: object) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def build_publish_queue(
    index_file: Path,
    task_id: str,
    reviewed_at: str,
    distribution_files: dict[str, str],
) -> list[dict[str, object]]:
    """写入项目级待发布队列与 ready_to_publish 视图。"""
    queue_items: list[dict[str, object]] = []
    for platform in ("douyin", "wechat_channels"):
        queue_items.append(
            {
                "task_id": task_id,
                "platform": platform,
                "title_file": distribution_files.get(f"{platform}/title.txt", ""),
                "caption_file": distribution_files.get(f"{platform}/caption.txt", ""),
                "hashtags_file": distribution_files.get(f"{platform}/hashtags.json", ""),
                "payload_file": distribution_files.get(
                    f"{platform}/publish_payload.json", ""
                ),
                "approved_at": reviewed_at,
            }
        )

    publish_queue_file = index_file.parent / "publish_queue.json"
    ready_file = index_file.parent / "ready_to_publish.json"
    existing_payload = {"items": []}
    if publish_queue_file.exists():
        existing_payload = json.loads(publish_queue_file.read_text(encoding="utf-8"))
    existing_items = [
        item for item in existing_payload.get("items", []) if item.get("task_id") != task_id
    ]
    existing_items.extend(queue_items)
    payload = {"items": existing_items}
    _write_json(publish_queue_file, payload)
    _write_json(ready_file, payload)
    return queue_items
