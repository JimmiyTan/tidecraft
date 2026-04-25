"""飞书消息格式化占位实现。"""

from lobster_farm.feishu_bridge.schemas import (
    ReviewItem,
    ReviewMessageRequest,
    ReviewMessageResponse,
)


def build_review_items(candidate_titles: list[str], scripts: list[str]) -> list[ReviewItem]:
    """将选题与脚本组合为审核条目。"""
    return [
        ReviewItem(title=title, script_text=script_text)
        for title, script_text in zip(candidate_titles, scripts)
    ]


def format_review_message(request: ReviewMessageRequest) -> ReviewMessageResponse:
    """将主题、选题和脚本格式化为人工审核消息。"""
    lines = [
        "【人工审核消息】",
        f"任务 ID：{request.task_id or '未设置'}",
        f"审核目录：{request.review_dir or '未设置'}",
        f"审核状态：{request.review_status or 'pending_review'}",
        f"主题：{request.topic}",
        f"视频结果：{request.video_summary or '待生成'}",
        "候选内容：",
    ]
    for index, item in enumerate(request.review_items, start=1):
        lines.append(f"{index}. 选题：{item.title}")
        lines.append(f"   脚本：{item.script_text}")
    if request.command_summary:
        lines.append("审核命令摘要：")
        lines.extend(request.command_summary.splitlines())
    lines.append("备注：当前消息用于人工审核，不会触发自动发布。")
    message = "\n".join(lines)
    payload = {
        "task_id": request.task_id,
        "review_dir": request.review_dir,
        "review_status": request.review_status,
        "topic": request.topic,
        "video_summary": request.video_summary,
        "command_summary": request.command_summary,
        "message": message,
        "items": [
            {"title": item.title, "script_text": item.script_text}
            for item in request.review_items
        ],
    }
    return ReviewMessageResponse(
        ok=True,
        message=message,
        delivery_mode="review",
        task_id=request.task_id,
        review_dir=request.review_dir,
        video_summary=request.video_summary,
        payload=payload,
    )
