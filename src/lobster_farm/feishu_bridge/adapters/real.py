"""飞书 real adapter。"""

import json
from typing import Any

from lobster_farm.common.config import AppConfig
from lobster_farm.feishu_bridge.adapters.base import FeishuAdapter
from lobster_farm.feishu_bridge.adapters.http_client import (
    FeishuHttpClient,
    FeishuHttpError,
)
from lobster_farm.feishu_bridge.schemas import (
    MessageSendResult,
    ReviewMessageResponse,
)


class RealFeishuAdapter(FeishuAdapter):
    """真实飞书 adapter，负责 token 获取与消息发送。"""

    name = "real"

    def __init__(
        self,
        config: AppConfig,
        http_client: FeishuHttpClient | None = None,
    ) -> None:
        """保存配置和 HTTP 客户端。"""
        self.config = config
        self.http_client = http_client or FeishuHttpClient(
            base_url=config.feishu_api_base_url,
            timeout_seconds=config.feishu_request_timeout_seconds,
        )

    def send(self, response: ReviewMessageResponse) -> MessageSendResult:
        """获取 token 并发送飞书消息。"""
        validation_error = self._validate_required_config()
        request_payload = self._build_message_payload(response)
        if validation_error:
            return MessageSendResult(
                ok=False,
                adapter=self.name,
                status="validation_failed",
                message="真实飞书 adapter 参数校验失败。",
                request_payload=request_payload,
                error_category="validation_error",
                error_message=validation_error,
                attempts=0,
            )

        attempts = 0
        last_error: FeishuHttpError | None = None
        response_payload: dict[str, Any] | None = None
        for attempts in range(1, self.config.feishu_max_retries + 2):
            try:
                token = self._get_access_token()
                response_payload = self._send_text_message(token, request_payload)
                return MessageSendResult(
                    ok=True,
                    adapter=self.name,
                    status="sent",
                    message="飞书消息已发送。",
                    request_payload=self._redact_request_payload(request_payload),
                    response_payload=response_payload,
                    attempts=attempts,
                )
            except FeishuHttpError as exc:
                exc.category = self._classify_feishu_error(exc)
                last_error = exc

        return MessageSendResult(
            ok=False,
            adapter=self.name,
            status="send_failed",
            message="飞书消息发送失败。",
            request_payload=self._redact_request_payload(request_payload),
            response_payload=last_error.response_payload if last_error else None,
            error_category=last_error.category if last_error else "unknown",
            error_message=str(last_error) if last_error else "未知错误",
            attempts=attempts,
        )

    def _validate_required_config(self) -> str:
        """校验真实发送所需配置。"""
        missing = [
            name
            for name, value in {
                "FEISHU_API_BASE_URL": self.config.feishu_api_base_url,
                "FEISHU_APP_ID": self.config.feishu_app_id,
                "FEISHU_APP_SECRET": self.config.feishu_app_secret,
                "FEISHU_DEFAULT_CHAT_ID": self.config.feishu_default_chat_id,
            }.items()
            if not value
        ]
        return "缺少配置：" + ", ".join(missing) if missing else ""

    def _get_access_token(self) -> str:
        """获取飞书 tenant access token。"""
        payload = {
            "app_id": self.config.feishu_app_id,
            "app_secret": self.config.feishu_app_secret,
        }
        response = self.http_client.post_json(
            "/open-apis/auth/v3/tenant_access_token/internal",
            payload,
        )
        code = response.payload.get("code")
        token = response.payload.get("tenant_access_token", "")
        if code != 0 or not token:
            raise FeishuHttpError(
                category="token_error",
                message="飞书 access token 获取失败。",
                status_code=response.status_code,
                response_payload=response.payload,
            )
        return token

    def _send_text_message(
        self,
        token: str,
        request_payload: dict[str, Any],
    ) -> dict[str, Any]:
        """发送飞书文本消息。"""
        response = self.http_client.post_json(
            "/open-apis/im/v1/messages?receive_id_type=chat_id",
            request_payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        code = response.payload.get("code")
        if code != 0:
            raise FeishuHttpError(
                category="send_error",
                message="飞书消息发送失败。",
                status_code=response.status_code,
                response_payload=response.payload,
            )
        return response.payload

    def _build_message_payload(
        self,
        response: ReviewMessageResponse,
    ) -> dict[str, Any]:
        """构造飞书发送请求。"""
        return {
            "receive_id": self.config.feishu_default_chat_id,
            "msg_type": "text",
            "content": json.dumps({"text": response.message}, ensure_ascii=False),
            "task_id": response.task_id,
            "review_dir": response.review_dir,
        }

    def _redact_request_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        """返回不含密钥的请求摘要。"""
        return {
            "receive_id": payload.get("receive_id", ""),
            "msg_type": payload.get("msg_type", ""),
            "task_id": payload.get("task_id", ""),
            "review_dir": payload.get("review_dir", ""),
        }

    def _classify_feishu_error(self, error: FeishuHttpError) -> str:
        """根据飞书响应细分错误类型。"""
        code = error.response_payload.get("code")
        message = str(error.response_payload.get("msg", ""))
        if code == 99991672 or "Access denied" in message:
            violations = (
                error.response_payload.get("error", {})
                .get("permission_violations", [])
            )
            subjects = {item.get("subject", "") for item in violations}
            if any(subject.startswith("im:message") for subject in subjects):
                return "permission_message_send"
            return "permission"
        if error.category == "token_error":
            return "token"
        if error.category == "timeout":
            return "network_timeout"
        if error.category == "network_error":
            return "network"
        if error.category == "invalid_response":
            return "response_structure"
        if code == 9499:
            return "request_payload"
        return error.category
