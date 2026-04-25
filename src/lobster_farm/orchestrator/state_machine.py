"""工作流状态机。"""

from enum import StrEnum


class WorkflowState(StrEnum):
    """工作流状态。"""

    CREATED = "created"
    TOPICS_GENERATED = "topics_generated"
    SCRIPTS_GENERATED = "scripts_generated"
    REVIEW_MESSAGE_GENERATED = "review_message_generated"
    VIDEO_REQUESTED = "video_requested"
    VIDEO_PROCESSING = "video_processing"
    VIDEO_READY = "video_ready"
    VIDEO_GENERATED = "video_generated"
    COMPLETED = "completed"
    FAILED = "failed"


ALLOWED_TRANSITIONS: dict[WorkflowState, set[WorkflowState]] = {
    WorkflowState.CREATED: {WorkflowState.TOPICS_GENERATED, WorkflowState.FAILED},
    WorkflowState.TOPICS_GENERATED: {WorkflowState.SCRIPTS_GENERATED, WorkflowState.FAILED},
    WorkflowState.SCRIPTS_GENERATED: {
        WorkflowState.REVIEW_MESSAGE_GENERATED,
        WorkflowState.FAILED,
    },
    WorkflowState.REVIEW_MESSAGE_GENERATED: {
        WorkflowState.VIDEO_REQUESTED,
        WorkflowState.FAILED,
    },
    WorkflowState.VIDEO_REQUESTED: {
        WorkflowState.VIDEO_PROCESSING,
        WorkflowState.VIDEO_READY,
        WorkflowState.FAILED,
    },
    WorkflowState.VIDEO_PROCESSING: {WorkflowState.VIDEO_READY, WorkflowState.FAILED},
    WorkflowState.VIDEO_READY: {WorkflowState.VIDEO_GENERATED, WorkflowState.FAILED},
    WorkflowState.VIDEO_GENERATED: {WorkflowState.COMPLETED, WorkflowState.FAILED},
    WorkflowState.COMPLETED: set(),
    WorkflowState.FAILED: set(),
}


def can_transition(current: WorkflowState, target: WorkflowState) -> bool:
    """判断是否允许状态切换。"""
    return target in ALLOWED_TRANSITIONS[current]


def assert_transition(current: WorkflowState, target: WorkflowState) -> None:
    """校验状态切换。"""
    if not can_transition(current, target):
        raise ValueError(f"非法状态切换：{current.value} -> {target.value}")
