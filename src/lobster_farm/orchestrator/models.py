"""工作流数据结构。"""

from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class WorkflowResult:
    """工作流执行结果。"""

    task_id: str
    topic: str
    candidate_titles: list[str] = field(default_factory=list)
    scripts: list[str] = field(default_factory=list)
    review_message: str = ""
    review_send_status: str = ""
    video_provider: str = ""
    video_provider_status: str = ""
    video_remote_task_id: str = ""
    export_file: Path | None = None
    task_dir: Path | None = None
    status: str = "created"
    review_status: str = "pending_review"
    reviewed_at: str = ""
    reviewed_by: str = ""
    review_note: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    error_message: str = ""
