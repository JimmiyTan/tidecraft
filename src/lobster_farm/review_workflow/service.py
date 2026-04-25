"""审核写回服务。"""

import json
from datetime import datetime
from pathlib import Path

from lobster_farm.common.config import AppConfig
from lobster_farm.distribution.package_builder import build_review_distribution_package
from lobster_farm.review_workflow.command_templates import export_review_command_templates
from lobster_farm.review_workflow.publish_queue import build_publish_queue
from lobster_farm.review_workflow.review_state import (
    ReviewStatus,
    assert_review_transition,
)


class ReviewWritebackError(ValueError):
    """审核写回错误。"""


def _read_json(file_path: Path) -> dict[str, object]:
    return json.loads(file_path.read_text(encoding="utf-8"))


def _write_json(file_path: Path, payload: dict[str, object]) -> None:
    file_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _load_task_record(index_file: Path, task_id: str) -> dict[str, object]:
    if not index_file.exists():
        raise ReviewWritebackError("任务索引文件不存在，无法执行审核写回。")
    payload = _read_json(index_file)
    for item in payload.get("tasks", []):
        if item.get("task_id") == task_id:
            return item
    raise ReviewWritebackError(f"未找到 task_id={task_id} 对应任务。")


def _update_task_index(
    index_file: Path,
    task_id: str,
    review_status: str,
    reviewed_at: str,
    reviewed_by: str,
    review_note: str,
) -> None:
    payload = _read_json(index_file)
    updated = False
    for item in payload.get("tasks", []):
        if item.get("task_id") != task_id:
            continue
        item["review_status"] = review_status
        item["reviewed_at"] = reviewed_at
        item["reviewed_by"] = reviewed_by
        item["review_note"] = review_note
        item["updated_at"] = datetime.now().isoformat()
        updated = True
        break
    if not updated:
        raise ReviewWritebackError(f"未找到 task_id={task_id} 对应任务。")
    _write_json(index_file, payload)


def _update_task_state(
    task_file: Path,
    review_status: str,
    reviewed_at: str,
    reviewed_by: str,
    review_note: str,
) -> dict[str, object]:
    payload = _read_json(task_file)
    payload["review_status"] = review_status
    payload["reviewed_at"] = reviewed_at
    payload["reviewed_by"] = reviewed_by
    payload["review_note"] = review_note
    payload["updated_at"] = datetime.now().isoformat()
    _write_json(task_file, payload)
    return payload


def _write_review_result(
    task_dir: Path,
    task_id: str,
    review_status: str,
    reviewed_at: str,
    reviewed_by: str,
    review_note: str,
) -> None:
    _write_json(
        task_dir / "review_decision.json",
        {
            "task_id": task_id,
            "review_status": review_status,
            "reviewed_at": reviewed_at,
            "reviewed_by": reviewed_by,
            "review_note": review_note,
        },
    )
    (task_dir / "review_note.txt").write_text(review_note, encoding="utf-8")


def _build_review_summary(task_dir: Path, review_status: str, reviewed_by: str, note: str) -> str:
    summary_file = task_dir / "summary.txt"
    base = summary_file.read_text(encoding="utf-8") if summary_file.exists() else ""
    review_summary = (
        "\n\n审核确认结果：\n"
        f"- review_status：{review_status}\n"
        f"- reviewed_by：{reviewed_by or '未填写'}\n"
        f"- review_note：{note or '无'}\n"
    )
    summary_file.write_text(base.rstrip() + review_summary, encoding="utf-8")
    return review_summary


def _write_ready_to_publish_files(
    task_dir: Path,
    task_id: str,
    review_status: str,
    reviewed_at: str,
    reviewed_by: str,
    review_note: str,
    distribution_files: dict[str, str],
) -> None:
    distribution_dir = task_dir / "distribution"
    distribution_dir.mkdir(parents=True, exist_ok=True)
    ready_payload = {
        "task_id": task_id,
        "review_status": review_status,
        "reviewed_at": reviewed_at,
        "reviewed_by": reviewed_by,
        "review_note": review_note,
        "platforms": [
            {
                "platform": platform,
                "title_file": distribution_files.get(f"{platform}/title.txt", ""),
                "caption_file": distribution_files.get(f"{platform}/caption.txt", ""),
                "hashtags_file": distribution_files.get(f"{platform}/hashtags.json", ""),
                "payload_file": distribution_files.get(
                    f"{platform}/publish_payload.json", ""
                ),
            }
            for platform in ("douyin", "wechat_channels")
        ],
    }
    _write_json(distribution_dir / "ready_to_publish.json", ready_payload)
    checklist = [
        f"任务 ID：{task_id}",
        f"审核状态：{review_status}",
        f"审核通过时间：{reviewed_at}",
        f"审核人：{reviewed_by}",
        "",
        "人工发布前检查清单：",
        "1. 确认标题是否适合目标平台。",
        "2. 确认 caption 与脚本内容一致。",
        "3. 确认 hashtags 是否符合平台习惯。",
        "4. 确认视频成片与审核结论一致。",
        "5. 确认本次操作仍为人工发布，而非自动发布。",
        "",
        f"审核备注：{review_note or '无'}",
    ]
    (distribution_dir / "publish_checklist.txt").write_text(
        "\n".join(checklist),
        encoding="utf-8",
    )


def write_review_decision(
    config: AppConfig,
    task_id: str,
    review_status: str,
    reviewed_by: str,
    review_note: str,
) -> dict[str, object]:
    """按 task_id 写回审核结果。"""
    record = _load_task_record(config.orchestrator_task_index_file, task_id)
    current_status = record.get("review_status", ReviewStatus.PENDING_REVIEW.value)
    assert_review_transition(str(current_status), review_status)

    task_file = Path(str(record.get("task_file", "")))
    task_dir = Path(str(record.get("task_dir", "")))
    if not task_file.exists():
        raise ReviewWritebackError(f"任务状态文件不存在：{task_file}")
    if not task_dir.exists():
        raise ReviewWritebackError(f"任务目录不存在：{task_dir}")

    reviewed_at = datetime.now().isoformat()
    task_payload = _update_task_state(
        task_file=task_file,
        review_status=review_status,
        reviewed_at=reviewed_at,
        reviewed_by=reviewed_by,
        review_note=review_note,
    )
    _update_task_index(
        index_file=config.orchestrator_task_index_file,
        task_id=task_id,
        review_status=review_status,
        reviewed_at=reviewed_at,
        reviewed_by=reviewed_by,
        review_note=review_note,
    )
    _write_review_result(
        task_dir=task_dir,
        task_id=task_id,
        review_status=review_status,
        reviewed_at=reviewed_at,
        reviewed_by=reviewed_by,
        review_note=review_note,
    )
    review_summary = _build_review_summary(
        task_dir=task_dir,
        review_status=review_status,
        reviewed_by=reviewed_by,
        note=review_note,
    )
    export_review_command_templates(task_dir, task_id)

    distribution_files: dict[str, str] = {}
    if review_status == ReviewStatus.APPROVED.value:
        topic_payload = _read_json(task_dir / "topic_list.json")
        scripts_payload = _read_json(task_dir / "scripts.json")
        distribution_files = build_review_distribution_package(
            task_dir=task_dir,
            task_id=task_id,
            topic=str(topic_payload.get("topic", "")),
            candidate_titles=list(topic_payload.get("candidate_titles", [])),
            scripts=[
                str(item.get("script_text", ""))
                for item in scripts_payload.get("scripts", [])
            ],
            review_note=review_note,
        )
        _write_ready_to_publish_files(
            task_dir=task_dir,
            task_id=task_id,
            review_status=review_status,
            reviewed_at=reviewed_at,
            reviewed_by=reviewed_by,
            review_note=review_note,
            distribution_files=distribution_files,
        )
        build_publish_queue(
            index_file=config.orchestrator_task_index_file,
            task_id=task_id,
            reviewed_at=reviewed_at,
            distribution_files=distribution_files,
        )

    latest_state_file = config.orchestrator_state_file
    if latest_state_file.exists():
        latest = _read_json(latest_state_file)
        if latest.get("task_id") == task_id:
            latest["review_status"] = review_status
            latest["reviewed_at"] = reviewed_at
            latest["reviewed_by"] = reviewed_by
            latest["review_note"] = review_note
            _write_json(latest_state_file, latest)

    return {
        "task_id": task_id,
        "review_status": review_status,
        "reviewed_at": reviewed_at,
        "reviewed_by": reviewed_by,
        "review_note": review_note,
        "review_summary": review_summary.strip(),
        "distribution_files": distribution_files,
        "task_file": task_file.as_posix(),
        "task_dir": task_dir.as_posix(),
        "status": task_payload.get("status", ""),
    }
