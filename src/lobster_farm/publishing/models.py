"""发布状态与回执数据结构。"""

from dataclasses import asdict, dataclass
from enum import StrEnum


class PublishStatus(StrEnum):
    """人工发布状态。"""

    READY_TO_PUBLISH = "ready_to_publish"
    MANUALLY_PUBLISHED = "manually_published"
    PUBLISH_FAILED = "publish_failed"
    ARCHIVED = "archived"


class PublishPlatform(StrEnum):
    """当前支持管理回执的平台。"""

    DOUYIN = "douyin"
    WECHAT_CHANNELS = "wechat_channels"


ALLOWED_PUBLISH_TRANSITIONS: dict[PublishStatus, set[PublishStatus]] = {
    PublishStatus.READY_TO_PUBLISH: {
        PublishStatus.MANUALLY_PUBLISHED,
        PublishStatus.PUBLISH_FAILED,
    },
    PublishStatus.PUBLISH_FAILED: {
        PublishStatus.MANUALLY_PUBLISHED,
        PublishStatus.ARCHIVED,
    },
    PublishStatus.MANUALLY_PUBLISHED: {
        PublishStatus.ARCHIVED,
    },
    PublishStatus.ARCHIVED: set(),
}


def assert_publish_transition(current: str, target: str) -> None:
    """校验发布状态流转是否合法。"""
    current_state = PublishStatus(current)
    target_state = PublishStatus(target)
    if target_state not in ALLOWED_PUBLISH_TRANSITIONS[current_state]:
        raise ValueError(f"非法发布状态切换：{current} -> {target}")


@dataclass
class PublishReceipt:
    """单个平台的人工发布回执。"""

    task_id: str
    platform: str
    publish_status: str
    published_by: str
    published_at: str
    publish_url: str
    publish_note: str

    def to_dict(self) -> dict[str, str]:
        """转换为可落盘字典。"""
        return asdict(self)
