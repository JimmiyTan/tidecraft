"""飞书 real adapter 单元测试。"""

import sys
from pathlib import Path
import unittest

PROJECT_SRC = Path(__file__).resolve().parents[3] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from lobster_farm.common.config import ConfigError, load_app_config
from lobster_farm.feishu_bridge.adapters.http_client import FeishuHttpError, HttpResponse
from lobster_farm.feishu_bridge.adapters.real import RealFeishuAdapter
from lobster_farm.feishu_bridge.formatter import build_review_items, format_review_message
from lobster_farm.feishu_bridge.schemas import ReviewMessageRequest


class FakeHttpClient:
    """测试用 HTTP 客户端。"""

    def __init__(self, responses=None, errors=None) -> None:
        """保存预设响应或错误。"""
        self.responses = list(responses or [])
        self.errors = list(errors or [])
        self.calls = []

    def post_json(self, path, payload, headers=None):
        """模拟 POST 请求。"""
        self.calls.append({"path": path, "payload": payload, "headers": headers or {}})
        if self.errors:
            raise self.errors.pop(0)
        return self.responses.pop(0)


def build_config(tmp_env: Path, max_retries: int = 2):
    """构造 real 飞书配置。"""
    tmp_env.write_text(
        "\n".join(
            [
                "RUN_MODE=real",
                "FEISHU_ADAPTER=real",
                "FEISHU_API_BASE_URL=https://example.test",
                "FEISHU_APP_ID=test_app_id",
                "FEISHU_APP_SECRET=test_secret",
                "FEISHU_DEFAULT_CHAT_ID=test_chat_id",
                "VIDEO_PROVIDER=mock",
                f"FEISHU_MAX_RETRIES={max_retries}",
            ]
        ),
        encoding="utf-8",
    )
    return load_app_config(tmp_env)


def build_message():
    """构造审核消息。"""
    return format_review_message(
        ReviewMessageRequest(
            topic="龙虾养殖",
            task_id="task_test",
            review_dir="exports/pending_review/task_test",
            review_items=build_review_items(["标题一"], ["脚本一"]),
        )
    )


class RealFeishuAdapterTestCase(unittest.TestCase):
    """验证 real adapter 行为。"""

    def test_missing_config(self) -> None:
        tmp_env = Path("data/temp/test_missing_real_feishu.env")
        tmp_env.write_text(
            "\n".join(
                [
                    "RUN_MODE=real",
                    "FEISHU_ADAPTER=real",
                    "VIDEO_PROVIDER=mock",
                ]
            ),
            encoding="utf-8",
        )
        with self.assertRaises(ConfigError):
            load_app_config(tmp_env)
        tmp_env.unlink(missing_ok=True)

    def test_token_failure(self) -> None:
        tmp_env = Path("data/temp/test_real_feishu.env")
        config = build_config(tmp_env, max_retries=0)
        client = FakeHttpClient(
            responses=[HttpResponse(status_code=200, payload={"code": 999})]
        )
        result = RealFeishuAdapter(config, client).send(build_message())
        self.assertFalse(result.ok)
        self.assertEqual(result.error_category, "token")
        tmp_env.unlink(missing_ok=True)

    def test_send_failure(self) -> None:
        tmp_env = Path("data/temp/test_real_feishu.env")
        config = build_config(tmp_env, max_retries=0)
        client = FakeHttpClient(
            responses=[
                HttpResponse(
                    status_code=200,
                    payload={"code": 0, "tenant_access_token": "token"},
                ),
                HttpResponse(status_code=200, payload={"code": 999}),
            ]
        )
        result = RealFeishuAdapter(config, client).send(build_message())
        self.assertFalse(result.ok)
        self.assertEqual(result.error_category, "send_error")
        tmp_env.unlink(missing_ok=True)

    def test_retry_logic(self) -> None:
        tmp_env = Path("data/temp/test_real_feishu.env")
        config = build_config(tmp_env)
        client = FakeHttpClient(
            errors=[
                FeishuHttpError("network_error", "first failed"),
            ],
            responses=[
                HttpResponse(
                    status_code=200,
                    payload={"code": 0, "tenant_access_token": "token"},
                ),
                HttpResponse(status_code=200, payload={"code": 0, "data": {}}),
            ],
        )
        result = RealFeishuAdapter(config, client).send(build_message())
        self.assertTrue(result.ok)
        self.assertEqual(result.attempts, 2)
        tmp_env.unlink(missing_ok=True)

    def test_message_content_is_json_string(self) -> None:
        tmp_env = Path("data/temp/test_real_feishu.env")
        config = build_config(tmp_env, max_retries=0)
        client = FakeHttpClient(
            responses=[
                HttpResponse(
                    status_code=200,
                    payload={"code": 0, "tenant_access_token": "token"},
                ),
                HttpResponse(status_code=200, payload={"code": 0, "data": {}}),
            ]
        )
        result = RealFeishuAdapter(config, client).send(build_message())
        self.assertTrue(result.ok)
        send_payload = client.calls[1]["payload"]
        self.assertIsInstance(send_payload["content"], str)
        self.assertIn("text", send_payload["content"])
        tmp_env.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
