"""飞书桥接服务最小测试。"""

import sys
from pathlib import Path
import unittest

PROJECT_SRC = Path(__file__).resolve().parents[3] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from lobster_farm.common.config import load_app_config
from lobster_farm.feishu_bridge.adapters import get_feishu_adapter
from lobster_farm.feishu_bridge.formatter import build_review_items, format_review_message
from lobster_farm.feishu_bridge.schemas import ReviewMessageRequest


class FeishuBridgeTestCase(unittest.TestCase):
    """验证消息格式化与 adapter。"""

    def test_format_review_message(self) -> None:
        request = ReviewMessageRequest(
            topic="龙虾养殖",
            review_items=build_review_items(["标题一", "标题二"], ["脚本一", "脚本二"]),
        )
        response = format_review_message(request)
        self.assertTrue(response.ok)
        self.assertIn("主题：龙虾养殖", response.message)
        self.assertIn("1. 选题：标题一", response.message)

    def test_default_adapter_is_dry_run(self) -> None:
        tmp_env = Path("data/temp/test_dry_run.env")
        tmp_env.parent.mkdir(parents=True, exist_ok=True)
        tmp_env.write_text(
            "\n".join(
                [
                    "RUN_MODE=dry-run",
                    "FEISHU_ADAPTER=dry-run",
                    "VIDEO_PROVIDER=mock",
                ]
            ),
            encoding="utf-8",
        )
        config = load_app_config(tmp_env)
        adapter = get_feishu_adapter(config)
        self.assertEqual(adapter.name, "dry-run")
        tmp_env.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
