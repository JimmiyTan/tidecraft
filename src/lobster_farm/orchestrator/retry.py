"""简单重试机制占位。"""

from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def run_with_retry(action: Callable[[], T], max_retries: int) -> T:
    """执行动作并在失败时做有限重试。"""
    last_error: Exception | None = None
    for _ in range(max_retries + 1):
        try:
            return action()
        except Exception as exc:  # noqa: BLE001 - 当前阶段统一落盘错误
            last_error = exc
    if last_error is None:
        raise RuntimeError("重试执行失败，但未捕获到异常")
    raise last_error
