"""视频网关数据结构。"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class VideoJobRequest:
    """视频生成任务请求。"""

    task_id: str
    topic: str
    review_items: list[dict[str, str]]
    output_dir: Path


@dataclass
class VideoJobResult:
    """视频生成任务结果。"""

    ok: bool
    task_id: str
    status: str
    output_file: Path | None
    provider: str
    remote_task_id: str = ""
    provider_status: str = ""
    provider_payload: dict[str, Any] = field(default_factory=dict)
    error_category: str = ""
    error_message: str = ""
    provider_request_file: Path | None = None
    provider_response_file: Path | None = None
