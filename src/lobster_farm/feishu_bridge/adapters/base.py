"""飞书 adapter 抽象层。"""

from abc import ABC, abstractmethod

from lobster_farm.feishu_bridge.schemas import (
    MessageSendResult,
    ReviewMessageResponse,
)


class FeishuAdapter(ABC):
    """飞书消息 adapter 基类。"""

    name: str

    @abstractmethod
    def send(self, response: ReviewMessageResponse) -> MessageSendResult:
        """发送或模拟发送审核消息。"""
