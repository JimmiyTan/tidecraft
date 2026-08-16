"""客户演示站点的本地 HTTP 应用层。"""

import json
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from threading import Lock
from urllib.parse import urlparse

from lobster_farm.common.config import AppConfig
from lobster_farm.demo import run_demo


MAX_REQUEST_BYTES = 16 * 1024
STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
}


class CustomerDemoRequestError(ValueError):
    """客户演示请求不合法。"""


class CustomerDemoBusyError(RuntimeError):
    """已有演示正在运行。"""


def validate_customer_demo_input(payload: object) -> tuple[str, str]:
    """校验并规范化客户演示输入。"""
    if not isinstance(payload, dict):
        raise CustomerDemoRequestError("请求必须是 JSON 对象。")

    topic_value = payload.get("topic", "")
    operator_value = payload.get("operator", "客户演示")
    if not isinstance(topic_value, str) or not isinstance(operator_value, str):
        raise CustomerDemoRequestError("主题和演示人必须是文本。")

    topic = topic_value.strip()
    operator = operator_value.strip() or "客户演示"
    if len(topic) < 2:
        raise CustomerDemoRequestError("请输入至少 2 个字符的演示主题。")
    if len(topic) > 120:
        raise CustomerDemoRequestError("演示主题不能超过 120 个字符。")
    if len(operator) > 40:
        raise CustomerDemoRequestError("演示人不能超过 40 个字符。")
    return topic, operator


def build_customer_demo_payload(summary: dict[str, object]) -> dict[str, object]:
    """构建不包含本地文件路径的客户展示结果。"""
    platform_labels = {
        "douyin": "抖音",
        "wechat_channels": "视频号",
    }
    platforms = []
    for item in summary.get("platforms", []):
        if not isinstance(item, dict):
            continue
        platform = str(item.get("platform", ""))
        platforms.append(
            {
                "id": platform,
                "name": platform_labels.get(platform, platform),
                "status": item.get("publish_status", ""),
                "receipt": "模拟人工发布回执已记录",
            }
        )

    return {
        "task_id": summary.get("task_id", ""),
        "topic": summary.get("topic", ""),
        "operator": summary.get("operator", ""),
        "candidate_titles": summary.get("candidate_titles", []),
        "workflow_status": summary.get("workflow_status", ""),
        "review_status": summary.get("review_status", ""),
        "publish_status": summary.get("publish_status", ""),
        "platforms": platforms,
        "outputs": [
            "候选选题与脚本",
            "人工审核记录",
            "双平台发布准备包",
            "人工发布回执",
            "全流程审计记录",
        ],
        "safety": {
            "mode": "dry-run / mock",
            "external_publish": False,
            "message": "本次演示未调用任何真实发布接口",
        },
        "completed_at": datetime.now().isoformat(),
    }


class CustomerDemoApplication:
    """串联静态页面和安全 Demo 服务。"""

    def __init__(
        self,
        project_root: Path,
        static_dir: Path,
        config: AppConfig,
    ) -> None:
        self.project_root = project_root
        self.static_dir = static_dir
        self.config = config
        self._run_lock = Lock()

    def health_payload(self) -> dict[str, object]:
        """返回前端状态栏所需的安全运行信息。"""
        return {
            "ok": True,
            "service": "lobster-farm-customer-demo",
            "mode": "dry-run / mock",
            "real_publish": False,
        }

    def run_customer_demo(self, payload: object) -> dict[str, object]:
        """执行一次客户演示，阻止并发重复触发。"""
        topic, operator = validate_customer_demo_input(payload)
        if not self._run_lock.acquire(blocking=False):
            raise CustomerDemoBusyError("已有演示正在运行，请稍后再试。")
        try:
            summary = run_demo(
                project_root=self.project_root,
                config=self.config,
                topic=topic,
                operator=operator,
            )
            return build_customer_demo_payload(summary)
        finally:
            self._run_lock.release()

    def read_static(self, path: str) -> tuple[bytes, str] | None:
        """只读取白名单中的客户演示静态文件。"""
        static_entry = STATIC_FILES.get(path)
        if static_entry is None:
            return None
        file_name, content_type = static_entry
        file_path = self.static_dir / file_name
        return file_path.read_bytes(), content_type


def build_customer_demo_handler(
    application: CustomerDemoApplication,
) -> type[BaseHTTPRequestHandler]:
    """创建绑定具体应用实例的 HTTP Handler。"""

    class CustomerDemoHandler(BaseHTTPRequestHandler):
        server_version = "LobsterFarmCustomerDemo/1.0"

        def _send_bytes(
            self,
            status: HTTPStatus,
            body: bytes,
            content_type: str,
        ) -> None:
            self.send_response(status.value)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self'; script-src 'self'; style-src 'self'; "
                "connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'",
            )
            self.end_headers()
            self.wfile.write(body)

        def _send_json(
            self,
            status: HTTPStatus,
            payload: dict[str, object],
        ) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self._send_bytes(status, body, "application/json; charset=utf-8")

        def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
            path = urlparse(self.path).path
            if path == "/api/health":
                self._send_json(HTTPStatus.OK, application.health_payload())
                return
            static_payload = application.read_static(path)
            if static_payload is None:
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "页面不存在。"})
                return
            body, content_type = static_payload
            self._send_bytes(HTTPStatus.OK, body, content_type)

        def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
            path = urlparse(self.path).path
            if path != "/api/demo":
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "接口不存在。"})
                return

            try:
                content_length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                content_length = 0
            if content_length <= 0 or content_length > MAX_REQUEST_BYTES:
                self._send_json(
                    HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                    {"error": "请求内容为空或过大。"},
                )
                return

            try:
                raw_body = self.rfile.read(content_length)
                request_payload = json.loads(raw_body.decode("utf-8"))
                result = application.run_customer_demo(request_payload)
            except (UnicodeDecodeError, json.JSONDecodeError):
                self._send_json(
                    HTTPStatus.BAD_REQUEST,
                    {"error": "请求不是合法 JSON。"},
                )
                return
            except CustomerDemoRequestError as exc:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
                return
            except CustomerDemoBusyError as exc:
                self._send_json(HTTPStatus.CONFLICT, {"error": str(exc)})
                return
            except (RuntimeError, ValueError, OSError):
                self._send_json(
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                    {"error": "演示执行失败，请查看本地服务日志。"},
                )
                return

            self._send_json(HTTPStatus.OK, {"ok": True, "demo": result})

        def log_message(self, format: str, *args: object) -> None:
            """输出不含请求正文的最小访问日志。"""
            print(f"customer-demo | {self.address_string()} | {format % args}")

    return CustomerDemoHandler
