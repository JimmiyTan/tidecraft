"""审核导出文件生成。"""

import json
from pathlib import Path

from lobster_farm.feishu_bridge.schemas import MessageSendResult, ReviewMessageResponse
from lobster_farm.review_workflow.command_templates import export_review_command_templates
from lobster_farm.video_gateway.schemas import VideoJobResult


def write_json(file_path: Path, payload: object) -> None:
    """写入 JSON 文件。"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def export_review_package(
    task_dir: Path,
    task_id: str,
    topic: str,
    candidate_titles: list[str],
    scripts: list[str],
    review_response: ReviewMessageResponse,
    send_result: MessageSendResult,
    video_result: VideoJobResult,
) -> None:
    """导出人工审核所需文件。"""
    task_dir.mkdir(parents=True, exist_ok=True)
    write_json(
        task_dir / "topic_list.json",
        {
            "task_id": task_id,
            "topic": topic,
            "candidate_titles": candidate_titles,
        },
    )
    write_json(
        task_dir / "scripts.json",
        {
            "task_id": task_id,
            "scripts": [
                {"title": title, "script_text": script}
                for title, script in zip(candidate_titles, scripts)
            ],
        },
    )
    write_json(
        task_dir / "review_message.json",
        {
            "task_id": task_id,
            "review_dir": review_response.review_dir,
            "message": review_response.message,
            "payload": review_response.payload,
            "send_result": {
                "ok": send_result.ok,
                "adapter": send_result.adapter,
                "status": send_result.status,
                "message": send_result.message,
                "request_payload": send_result.request_payload,
                "response_payload": send_result.response_payload,
                "error_category": send_result.error_category,
                "error_message": send_result.error_message,
                "attempts": send_result.attempts,
            },
        },
    )
    write_json(
        task_dir / "video_result.json",
        {
            "task_id": task_id,
            "ok": video_result.ok,
            "status": video_result.status,
            "provider": video_result.provider,
            "remote_task_id": video_result.remote_task_id,
            "provider_status": video_result.provider_status,
            "provider_payload": video_result.provider_payload,
            "output_file": video_result.output_file.as_posix()
            if video_result.output_file
            else "",
            "error_category": video_result.error_category,
            "error_message": video_result.error_message,
        },
    )
    write_json(
        task_dir / "review_decision.json",
        {
            "task_id": task_id,
            "review_status": "pending_review",
            "reviewed_at": "",
            "reviewed_by": "",
            "review_note": "",
        },
    )
    (task_dir / "review_note.txt").write_text("", encoding="utf-8")
    export_review_command_templates(task_dir, task_id)
    if video_result.provider_request_file and video_result.provider_request_file.exists():
        target_request = task_dir / "provider_request.json"
        if video_result.provider_request_file != target_request:
            target_request.write_text(
                video_result.provider_request_file.read_text(encoding="utf-8"),
                encoding="utf-8",
            )
    if video_result.provider_response_file and video_result.provider_response_file.exists():
        target_response = task_dir / "provider_response.json"
        if video_result.provider_response_file != target_response:
            target_response.write_text(
                video_result.provider_response_file.read_text(encoding="utf-8"),
                encoding="utf-8",
            )
    summary_lines = [
        f"任务 ID：{task_id}",
        f"审核目录：{review_response.review_dir}",
        f"主题：{topic}",
        "",
        "候选选题与脚本：",
    ]
    for index, (title, script) in enumerate(zip(candidate_titles, scripts), start=1):
        summary_lines.append(f"{index}. {title}")
        summary_lines.append(f"   {script}")
    summary_lines.extend(
        [
            "",
            "飞书消息状态：",
            f"- adapter：{send_result.adapter}",
            f"- status：{send_result.status}",
            "",
            "视频生成状态：",
            f"- provider：{video_result.provider}",
            f"- status：{video_result.status}",
            f"- remote_task_id：{video_result.remote_task_id or '无'}",
            f"- provider_status：{video_result.provider_status or '无'}",
            "",
            "审核状态：",
            "- review_status：pending_review",
            "",
            "审核建议：",
            "请人工确认选题、脚本和视频占位结果后，再决定是否进入后续真实生成阶段。",
        ]
    )
    (task_dir / "summary.txt").write_text("\n".join(summary_lines), encoding="utf-8")
