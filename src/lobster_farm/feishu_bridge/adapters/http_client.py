"""飞书 HTTP 客户端，使用标准库实现。"""

import json
import socket
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass
class HttpResponse:
    """HTTP 响应。"""

    status_code: int
    payload: dict[str, Any]


class FeishuHttpError(RuntimeError):
    """飞书 HTTP 错误。"""

    def __init__(
        self,
        category: str,
        message: str,
        status_code: int = 0,
        response_payload: dict[str, Any] | None = None,
    ) -> None:
        """保存错误分类和响应。"""
        super().__init__(message)
        self.category = category
        self.status_code = status_code
        self.response_payload = response_payload or {}


class FeishuHttpClient:
    """飞书 HTTP 客户端。"""

    def __init__(self, base_url: str, timeout_seconds: int) -> None:
        """初始化基础地址和超时时间。"""
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def post_json(
        self,
        path: str,
        payload: dict[str, Any],
        headers: dict[str, str] | None = None,
    ) -> HttpResponse:
        """发送 JSON POST 请求。"""
        url = self.base_url + path
        request_headers = {
            "Content-Type": "application/json; charset=utf-8",
            **(headers or {}),
        }
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            url=url,
            data=body,
            headers=request_headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                response_body = response.read().decode("utf-8")
                response_payload = json.loads(response_body) if response_body else {}
                return HttpResponse(status_code=response.status, payload=response_payload)
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            try:
                error_payload = json.loads(error_body) if error_body else {}
            except json.JSONDecodeError:
                error_payload = {"raw": error_body}
            raise FeishuHttpError(
                category="http_error",
                message=f"飞书 HTTP 错误：{exc.code}",
                status_code=exc.code,
                response_payload=error_payload,
            ) from exc
        except urllib.error.URLError as exc:
            raise FeishuHttpError(
                category="network_error",
                message=f"飞书网络错误：{exc.reason}",
            ) from exc
        except socket.timeout as exc:
            raise FeishuHttpError(
                category="timeout",
                message="飞书请求超时",
            ) from exc
        except json.JSONDecodeError as exc:
            raise FeishuHttpError(
                category="invalid_response",
                message="飞书响应不是合法 JSON",
            ) from exc
