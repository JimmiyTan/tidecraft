"""一键安全 Demo 测试。"""

import json
import sys
from dataclasses import replace
from pathlib import Path
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PROJECT_SRC = PROJECT_ROOT / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from lobster_farm.common.config import load_app_config
from lobster_farm.demo import DemoSafetyError, assert_demo_safe_config, run_demo


class DemoTestCase(unittest.TestCase):
    """验证 Demo 完整闭环与强制安全配置。"""

    def setUp(self) -> None:
        base_config = load_app_config(PROJECT_ROOT / ".env.example")
        demo_root = PROJECT_ROOT / "data" / "temp" / "demo-tests"
        self.config = replace(
            base_config,
            workspace_root=PROJECT_ROOT,
            data_dir=demo_root / "data",
            log_dir=demo_root / "logs",
            export_dir=demo_root / "exports",
            video_output_dir=demo_root / "exports" / "pending_review",
            orchestrator_state_file=demo_root / "data" / "state" / "workflow_state.json",
            orchestrator_queue_dir=demo_root / "data" / "queue",
            orchestrator_task_state_dir=demo_root / "data" / "state" / "tasks",
            orchestrator_task_index_file=demo_root / "data" / "state" / "task_index.json",
        )

    def test_run_demo_completes_archived_safe_flow(self) -> None:
        summary = run_demo(
            project_root=PROJECT_ROOT,
            config=self.config,
            topic="Demo 自动化测试",
            operator="demo-test",
        )

        self.assertEqual(summary["workflow_status"], "completed")
        self.assertEqual(summary["review_status"], "approved")
        self.assertEqual(summary["publish_status"], "archived")
        self.assertEqual(len(summary["candidate_titles"]), 5)
        self.assertFalse(summary["safe_mode"]["real_publish_called"])
        self.assertEqual(
            {item["publish_status"] for item in summary["platforms"]},
            {"archived"},
        )
        summary_file = Path(str(summary["summary_file"]))
        self.assertTrue(summary_file.exists())
        payload = json.loads(summary_file.read_text(encoding="utf-8"))
        self.assertEqual(payload["task_id"], summary["task_id"])

    def test_demo_rejects_unsafe_config(self) -> None:
        unsafe_config = replace(self.config, run_mode="real")
        with self.assertRaises(DemoSafetyError):
            assert_demo_safe_config(unsafe_config)

        credential_config = replace(self.config, video_api_key="demo-must-reject")
        with self.assertRaises(DemoSafetyError):
            assert_demo_safe_config(credential_config)


if __name__ == "__main__":
    unittest.main()
