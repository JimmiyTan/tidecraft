"""人工发布回执机制测试。"""

import json
import sys
from pathlib import Path
import unittest

PROJECT_SRC = Path(__file__).resolve().parents[3] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from lobster_farm.common.config import load_app_config
from lobster_farm.orchestrator.state_store import (
    append_task_index,
    write_state,
    write_task_state,
)
from lobster_farm.orchestrator.workflow import run_workflow
from lobster_farm.publishing.models import assert_publish_transition
from lobster_farm.publishing.service import (
    PublishWritebackError,
    archive_task,
    get_task_publish_status,
    list_publish_queue,
    write_publish_result,
)
from lobster_farm.review_workflow.service import write_review_decision


class PublishingWorkflowTestCase(unittest.TestCase):
    """验证发布队列、发布回执与归档。"""

    def setUp(self) -> None:
        self.project_root = Path(__file__).resolve().parents[3]
        self.config = load_app_config(self.project_root / ".env.example")

    def _create_approved_task(self, topic: str):
        result = run_workflow(
            project_root=self.project_root,
            config=self.config,
            topic=topic,
        )
        write_state(self.config.orchestrator_state_file, result)
        task_file = write_task_state(self.config.orchestrator_task_state_dir, result)
        append_task_index(self.config.orchestrator_task_index_file, result, task_file)
        review_result = write_review_decision(
            config=self.config,
            task_id=result.task_id,
            review_status="approved",
            reviewed_by="tester",
            review_note="审核通过，准备人工发布。",
        )
        return result, review_result

    def test_publish_transition_rejects_invalid_flow(self) -> None:
        with self.assertRaises(ValueError):
            assert_publish_transition("ready_to_publish", "archived")

    def test_single_platform_publish_writeback(self) -> None:
        result, review_result = self._create_approved_task("单平台发布回写测试")
        publish_result = write_publish_result(
            config=self.config,
            task_id=result.task_id,
            platform="douyin",
            publish_status="manually_published",
            published_by="tester",
            publish_url="https://example.com/douyin/manual",
            publish_note="抖音已人工发布。",
        )
        task_dir = Path(str(review_result["task_dir"]))
        self.assertEqual(publish_result["publish_status"], "manually_published")
        self.assertTrue((task_dir / "publish_result.json").exists())
        self.assertTrue((task_dir / "publish_note.txt").exists())
        payload = json.loads((task_dir / "publish_result.json").read_text(encoding="utf-8"))
        self.assertEqual(
            payload["platforms"]["douyin"]["publish_url"],
            "https://example.com/douyin/manual",
        )

    def test_dual_platform_publish_writeback(self) -> None:
        result, _review_result = self._create_approved_task("双平台发布回写测试")
        write_publish_result(
            config=self.config,
            task_id=result.task_id,
            platform="douyin",
            publish_status="manually_published",
            published_by="tester",
            publish_url="https://example.com/douyin/dual",
            publish_note="抖音已发布。",
        )
        write_publish_result(
            config=self.config,
            task_id=result.task_id,
            platform="wechat_channels",
            publish_status="publish_failed",
            published_by="tester",
            publish_url="",
            publish_note="视频号人工发布失败，待重试。",
        )
        status = get_task_publish_status(self.config, result.task_id)
        statuses = {
            item["platform"]: item["publish_status"]
            for item in status["platforms"]
        }
        self.assertEqual(statuses["douyin"], "manually_published")
        self.assertEqual(statuses["wechat_channels"], "publish_failed")

    def test_publish_queue_supports_status_and_platform_filter(self) -> None:
        result, _review_result = self._create_approved_task("发布队列筛选测试")
        ready_items = list_publish_queue(
            self.config,
            status="ready_to_publish",
            platform="douyin",
        )
        self.assertTrue(
            any(item["task_id"] == result.task_id for item in ready_items)
        )

    def test_publish_writeback_for_missing_task_fails(self) -> None:
        with self.assertRaises(PublishWritebackError):
            write_publish_result(
                config=self.config,
                task_id="missing_task",
                platform="douyin",
                publish_status="manually_published",
                published_by="tester",
                publish_url="https://example.com/missing",
                publish_note="missing",
            )

    def test_archive_published_task(self) -> None:
        result, _review_result = self._create_approved_task("发布归档测试")
        for platform in ("douyin", "wechat_channels"):
            write_publish_result(
                config=self.config,
                task_id=result.task_id,
                platform=platform,
                publish_status="manually_published",
                published_by="tester",
                publish_url=f"https://example.com/{platform}/archive",
                publish_note="已发布，准备归档。",
            )
        archive_result = archive_task(self.config, result.task_id)
        self.assertEqual(archive_result["publish_status"], "archived")
        archived_items = list_publish_queue(self.config, status="archived")
        self.assertTrue(
            any(item["task_id"] == result.task_id for item in archived_items)
        )


if __name__ == "__main__":
    unittest.main()
