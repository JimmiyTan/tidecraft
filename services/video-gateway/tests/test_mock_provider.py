"""视频网关最小测试。"""

import shutil
import sys
from pathlib import Path
import unittest

PROJECT_SRC = Path(__file__).resolve().parents[3] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from lobster_farm.common.config import load_app_config
from lobster_farm.video_gateway.providers.registry import get_video_provider
from lobster_farm.video_gateway.providers.mock_provider import MockVideoProvider
from lobster_farm.video_gateway.schemas import VideoJobRequest


class MockProviderTestCase(unittest.TestCase):
    """验证 mock provider 和注册机制。"""

    def test_generate(self) -> None:
        output_dir = Path("tests/tmp_video_output")
        if output_dir.exists():
            shutil.rmtree(output_dir)
        result = MockVideoProvider().generate(
            VideoJobRequest(
                task_id="test_task",
                topic="龙虾养殖",
                review_items=[{"title": "标题一", "script_text": "脚本内容"}],
                output_dir=output_dir,
            )
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.status, "video_ready")
        self.assertTrue(result.output_file and result.output_file.exists())
        shutil.rmtree(output_dir)

    def test_default_provider_is_mock(self) -> None:
        config = load_app_config()
        provider = get_video_provider(config)
        self.assertEqual(provider.name, "mock")


if __name__ == "__main__":
    unittest.main()
