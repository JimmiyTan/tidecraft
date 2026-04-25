"""飞书桥接数据结构。"""

from dataclasses import dataclass
from typing import Any


@dataclass
class ReviewItem:
    """单条审核内容。"""

    title: str
    script_text: str


@dataclass
class ReviewMessageRequest:
    """人工审核消息请求。"""

    topic: str
    review_items: list[ReviewItem]
    task_id: str = ""
    review_dir: str = ""
    video_summary: str = ""
    review_status: str = "pending_review"
    command_summary: str = ""


@dataclass
class ReviewMessageResponse:
    """人工审核消息结果。"""

    ok: bool
    message: str
    delivery_mode: str
    task_id: str = ""
    review_dir: str = ""
    video_summary: str = ""
    payload: dict[str, Any] | None = None


@dataclass
class MessageSendResult:
    """消息发送结果。"""

    ok: bool
    adapter: str
    status: str
    message: str
    request_payload: dict[str, Any] | None = None
    response_payload: dict[str, Any] | None = None
    error_category: str = ""
    error_message: str = ""
    attempts: int = 0
