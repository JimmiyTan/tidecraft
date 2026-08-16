"""客户前端演示服务测试。"""

import json
import sys
from pathlib import Path
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PROJECT_SRC = PROJECT_ROOT / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from lobster_farm.common.config import load_app_config
from lobster_farm.customer_demo_web import (
    CustomerDemoApplication,
    CustomerDemoRequestError,
    build_customer_demo_payload,
    validate_customer_demo_input,
)


class CustomerDemoWebTestCase(unittest.TestCase):
    """验证客户演示输入、响应脱敏和静态文件白名单。"""

    def test_validate_customer_demo_input(self) -> None:
        topic, operator = validate_customer_demo_input(
            {"topic": "  餐饮短视频  ", "operator": "  客户代表  "}
        )
        self.assertEqual(topic, "餐饮短视频")
        self.assertEqual(operator, "客户代表")

    def test_validate_customer_demo_input_rejects_invalid_values(self) -> None:
        with self.assertRaises(CustomerDemoRequestError):
            validate_customer_demo_input({"topic": ""})
        with self.assertRaises(CustomerDemoRequestError):
            validate_customer_demo_input({"topic": "a" * 121})
        with self.assertRaises(CustomerDemoRequestError):
            validate_customer_demo_input({"topic": 123})

    def test_customer_payload_hides_local_paths(self) -> None:
        result = build_customer_demo_payload(
            {
                "task_id": "task_demo",
                "topic": "客户主题",
                "operator": "客户代表",
                "candidate_titles": ["选题一"],
                "workflow_status": "completed",
                "review_status": "approved",
                "publish_status": "archived",
                "task_dir": "C:/secret/local/path",
                "summary_file": "C:/secret/local/path/demo_summary.json",
                "platforms": [
                    {
                        "platform": "douyin",
                        "publish_status": "archived",
                        "publish_url": "https://demo.invalid/private",
                        "title_file": "C:/secret/title.txt",
                    }
                ],
            }
        )
        serialized = json.dumps(result, ensure_ascii=False)
        self.assertNotIn("C:/secret", serialized)
        self.assertNotIn("demo.invalid", serialized)
        self.assertEqual(result["platforms"][0]["name"], "抖音")

    def test_static_files_are_allowlisted(self) -> None:
        application = CustomerDemoApplication(
            project_root=PROJECT_ROOT,
            static_dir=PROJECT_ROOT / "apps" / "customer-demo",
            config=load_app_config(PROJECT_ROOT / ".env.example"),
        )
        static_payload = application.read_static("/")
        self.assertIsNotNone(static_payload)
        self.assertIn(b"lobster-farm", static_payload[0])
        self.assertIsNone(application.read_static("/../../.env"))


if __name__ == "__main__":
    unittest.main()
