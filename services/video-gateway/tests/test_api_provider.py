"""视频 API provider 单元测试。"""

import sys
from pathlib import Path
import unittest

PROJECT_SRC = Path(__file__).resolve().parents[3] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from lobster_farm.common.config import ConfigError, load_app_config
from lobster_farm.video_gateway.providers.api_provider import ApiVideoProvider
from lobster_farm.video_gateway.providers.http_client import HttpResponse, VideoHttpError
from lobster_farm.video_gateway.schemas import VideoJobRequest


class FakeVideoHttpClient:
    """测试用视频 HTTP 客户端。"""

    def __init__(self, post_responses=None, get_responses=None, errors=None) -> None:
        """保存响应和错误。"""
        self.post_responses = list(post_responses or [])
        self.get_responses = list(get_responses or [])
        self.errors = list(errors or [])
        self.calls = []

    def post_json(self, path, payload):
        """模拟 POST。"""
        self.calls.append({"method": "POST", "path": path, "payload": payload})
        if self.errors:
            raise self.errors.pop(0)
        return self.post_responses.pop(0)

    def get_json(self, path):
        """模拟 GET。"""
        self.calls.append({"method": "GET", "path": path})
        if self.errors:
            raise self.errors.pop(0)
        return self.get_responses.pop(0)


def build_config(tmp_env: Path, max_retries: int = 0, max_polls: int = 2):
    """构造 api provider 配置。"""
    tmp_env.parent.mkdir(parents=True, exist_ok=True)
    tmp_env.write_text(
        "\n".join(
            [
                "RUN_MODE=real",
                "FEISHU_ADAPTER=dry-run",
                "VIDEO_PROVIDER=api",
                "VIDEO_API_KEY=test_key",
                "VIDEO_PROVIDER_BASE_URL=https://video.example.test",
                "VIDEO_SUBMIT_PATH=/submit",
                "VIDEO_STATUS_PATH=/status/{remote_task_id}",
                f"VIDEO_MAX_RETRIES={max_retries}",
                f"VIDEO_MAX_POLL_ATTEMPTS={max_polls}",
                "VIDEO_POLL_INTERVAL_SECONDS=0",
            ]
        ),
        encoding="utf-8",
    )
    return load_app_config(tmp_env)


def build_request() -> VideoJobRequest:
    """构造视频任务请求。"""
    return VideoJobRequest(
        task_id="task_test",
        topic="龙虾养殖",
        review_items=[{"title": "标题一", "script_text": "脚本一"}],
        output_dir=Path("data/temp/test_api_provider/task_test"),
    )


class ApiProviderTestCase(unittest.TestCase):
    """验证 API provider 行为。"""

    def test_missing_config(self) -> None:
        tmp_env = Path("data/temp/test_api_missing.env")
        tmp_env.parent.mkdir(parents=True, exist_ok=True)
        tmp_env.write_text(
            "\n".join(["RUN_MODE=real", "VIDEO_PROVIDER=api"]),
            encoding="utf-8",
        )
        with self.assertRaises(ConfigError):
            load_app_config(tmp_env)
        tmp_env.unlink(missing_ok=True)

    def test_submit_failure(self) -> None:
        tmp_env = Path("data/temp/test_api.env")
        config = build_config(tmp_env)
        client = FakeVideoHttpClient(
            errors=[VideoHttpError("http_error", "submit failed", status_code=500)]
        )
        result = ApiVideoProvider(config, client, sleep_func=lambda _: None).generate(
            build_request()
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.error_category, "http_error")
        tmp_env.unlink(missing_ok=True)

    def test_query_failure(self) -> None:
        tmp_env = Path("data/temp/test_api.env")
        config = build_config(tmp_env)
        client = FakeVideoHttpClient(
            post_responses=[
                HttpResponse(200, {"remote_task_id": "remote_1", "status": "processing"})
            ],
            errors=[VideoHttpError("network", "query failed")],
        )
        result = ApiVideoProvider(config, client, sleep_func=lambda _: None).generate(
            build_request()
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.error_category, "network")
        tmp_env.unlink(missing_ok=True)

    def test_retry_logic(self) -> None:
        tmp_env = Path("data/temp/test_api.env")
        config = build_config(tmp_env, max_retries=1)
        client = FakeVideoHttpClient(
            post_responses=[
                HttpResponse(200, {"remote_task_id": "remote_1", "status": "ready"})
            ],
            errors=[VideoHttpError("network", "first failed")],
        )
        result = ApiVideoProvider(config, client, sleep_func=lambda _: None).generate(
            build_request()
        )
        self.assertTrue(result.ok)
        self.assertEqual(len(client.calls), 2)
        tmp_env.unlink(missing_ok=True)

    def test_result_parse_failure(self) -> None:
        tmp_env = Path("data/temp/test_api.env")
        config = build_config(tmp_env)
        client = FakeVideoHttpClient(
            post_responses=[HttpResponse(200, {"status": "ready"})]
        )
        result = ApiVideoProvider(config, client, sleep_func=lambda _: None).generate(
            build_request()
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.error_category, "response_parse")
        tmp_env.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
