"""视频 API HTTP 客户端，使用标准库实现。"""

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


class VideoHttpError(RuntimeError):
    """视频 API HTTP 错误。"""

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


class VideoHttpClient:
    """视频 API HTTP 客户端。"""

    def __init__(self, base_url: str, api_key: str, timeout_seconds: int) -> None:
        """初始化基础地址、密钥和超时。"""
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds

    def post_json(self, path: str, payload: dict[str, Any]) -> HttpResponse:
        """发送 JSON POST 请求。"""
        request = urllib.request.Request(
            url=self.base_url + path,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers=self._headers(),
            method="POST",
        )
        return self._request_json(request)

    def get_json(self, path: str) -> HttpResponse:
        """发送 JSON GET 请求。"""
        request = urllib.request.Request(
            url=self.base_url + path,
            headers=self._headers(),
            method="GET",
        )
        return self._request_json(request)

    def _headers(self) -> dict[str, str]:
        """构造请求头，不在日志输出完整密钥。"""
        return {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {self.api_key}",
        }

    def _request_json(self, request: urllib.request.Request) -> HttpResponse:
        """执行请求并解析 JSON。"""
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                body = response.read().decode("utf-8")
                payload = json.loads(body) if body else {}
                return HttpResponse(status_code=response.status, payload=payload)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            try:
                payload = json.loads(body) if body else {}
            except json.JSONDecodeError:
                payload = {"raw": body}
            raise VideoHttpError(
                category="http_error",
                message=f"视频 API HTTP 错误：{exc.code}",
                status_code=exc.code,
                response_payload=payload,
            ) from exc
        except urllib.error.URLError as exc:
            raise VideoHttpError(
                category="network",
                message=f"视频 API 网络错误：{exc.reason}",
            ) from exc
        except socket.timeout as exc:
            raise VideoHttpError(
                category="timeout",
                message="视频 API 请求超时",
            ) from exc
        except json.JSONDecodeError as exc:
            raise VideoHttpError(
                category="response_parse",
                message="视频 API 响应不是合法 JSON",
            ) from exc
