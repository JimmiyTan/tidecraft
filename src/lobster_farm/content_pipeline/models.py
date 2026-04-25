"""内容流水线数据结构。"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CandidateContent:
    """候选热点内容线索。"""

    title: str
    link: str
    heat_signal: str
    published_at: str
    account_name: str
    keywords: list[str]


@dataclass
class ViralAnalysis:
    """爆款结构拆解结果。"""

    hook_type: str
    first_three_seconds_conflict: str
    emotion_curve: str
    reversal_point: str
    shot_rhythm: str
    cta_type: str
    reusable_structure: str
    compliance_note: str = "仅复用结构，不复刻原视频逐字脚本。"


@dataclass
class RewriteVersion:
    """原创改写版本。"""

    version_name: str
    title: str
    storyboard: list[str]
    lines: list[str]
    cover_text: str
    hashtags: list[str]


@dataclass
class PipelineResult:
    """内容流水线执行结果。"""

    task_id: str
    topic: str
    candidate: CandidateContent
    analysis: ViralAnalysis
    rewrites: list[RewriteVersion]
    task_dir: Path
    review_message: str
    send_status: str
    files: dict[str, str] = field(default_factory=dict)
    status: str = "completed"
    error_message: str = ""


def dataclass_to_dict(value: Any) -> Any:
    """递归转换 dataclass 为 JSON 友好结构。"""
    if hasattr(value, "__dataclass_fields__"):
        return {
            field_name: dataclass_to_dict(getattr(value, field_name))
            for field_name in value.__dataclass_fields__
        }
    if isinstance(value, list):
        return [dataclass_to_dict(item) for item in value]
    if isinstance(value, dict):
        return {key: dataclass_to_dict(item) for key, item in value.items()}
    if isinstance(value, Path):
        return value.as_posix()
    return value
