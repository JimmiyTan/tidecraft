"""审核状态定义与流转校验。"""

from enum import StrEnum


class ReviewStatus(StrEnum):
    """审核状态。"""

    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_EDIT = "needs_edit"


ALLOWED_REVIEW_TRANSITIONS: dict[ReviewStatus, set[ReviewStatus]] = {
    ReviewStatus.PENDING_REVIEW: {
        ReviewStatus.APPROVED,
        ReviewStatus.REJECTED,
        ReviewStatus.NEEDS_EDIT,
    },
    ReviewStatus.NEEDS_EDIT: {
        ReviewStatus.APPROVED,
        ReviewStatus.REJECTED,
        ReviewStatus.NEEDS_EDIT,
    },
    ReviewStatus.APPROVED: set(),
    ReviewStatus.REJECTED: set(),
}


def assert_review_transition(current: str, target: str) -> None:
    """校验审核状态切换是否合法。"""
    current_state = ReviewStatus(current)
    target_state = ReviewStatus(target)
    if target_state not in ALLOWED_REVIEW_TRANSITIONS[current_state]:
        raise ValueError(f"非法审核状态切换：{current} -> {target}")
