"""飞书发送入口。"""

from lobster_farm.common.config import AppConfig
from lobster_farm.feishu_bridge.adapters import get_feishu_adapter
from lobster_farm.feishu_bridge.schemas import (
    MessageSendResult,
    ReviewMessageResponse,
)


def send_message(config: AppConfig, response: ReviewMessageResponse) -> MessageSendResult:
    """按配置选择 adapter 发送或模拟发送消息。"""
    adapter = get_feishu_adapter(config)
    return adapter.send(response)
