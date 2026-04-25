"""飞书 dry-run adapter。"""

from lobster_farm.feishu_bridge.adapters.base import FeishuAdapter
from lobster_farm.feishu_bridge.schemas import (
    MessageSendResult,
    ReviewMessageResponse,
)


class DryRunFeishuAdapter(FeishuAdapter):
    """只记录消息，不发送到真实飞书。"""

    name = "dry-run"

    def send(self, response: ReviewMessageResponse) -> MessageSendResult:
        """返回 dry-run 发送结果。"""
        return MessageSendResult(
            ok=response.ok,
            adapter=self.name,
            status="dry_run",
            message="已生成飞书 dry-run 消息，未执行真实发送。",
            request_payload=response.payload or {"message": response.message},
            attempts=1,
        )
