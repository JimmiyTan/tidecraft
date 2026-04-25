"""审核确认机制测试。"""

import sys
import json
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
from lobster_farm.review_workflow.listing import list_review_tasks
from lobster_farm.review_workflow.review_state import assert_review_transition
from lobster_farm.review_workflow.service import (
    ReviewWritebackError,
    write_review_decision,
)


class ReviewWorkflowTestCase(unittest.TestCase):
    """验证审核状态流转、写回和分发包生成。"""

    def setUp(self) -> None:
        self.project_root = Path(__file__).resolve().parents[3]
        self.config = load_app_config(self.project_root / ".env.example")

    def _create_task(self, topic: str):
        result = run_workflow(
            project_root=self.project_root,
            config=self.config,
            topic=topic,
        )
        write_state(self.config.orchestrator_state_file, result)
        task_file = write_task_state(self.config.orchestrator_task_state_dir, result)
        append_task_index(self.config.orchestrator_task_index_file, result, task_file)
        return result, task_file

    def test_review_transition_rejects_invalid_flow(self) -> None:
        with self.assertRaises(ValueError):
            assert_review_transition("approved", "needs_edit")

    def test_review_writeback_for_missing_task_fails(self) -> None:
        with self.assertRaises(ReviewWritebackError):
            write_review_decision(
                config=self.config,
                task_id="missing_task",
                review_status="approved",
                reviewed_by="tester",
                review_note="missing",
            )

    def test_approved_generates_distribution_package(self) -> None:
        result, _task_file = self._create_task("审核通过测试")
        review_result = write_review_decision(
            config=self.config,
            task_id=result.task_id,
            review_status="approved",
            reviewed_by="tester",
            review_note="内容通过，进入分发准备。",
        )
        task_dir = Path(review_result["task_dir"])
        self.assertTrue((task_dir / "review_decision.json").exists())
        self.assertTrue((task_dir / "review_note.txt").exists())
        self.assertTrue((task_dir / "approve.cmd.txt").exists())
        self.assertTrue((task_dir / "reject.cmd.txt").exists())
        self.assertTrue((task_dir / "needs_edit.cmd.txt").exists())
        self.assertTrue((task_dir / "distribution" / "douyin" / "title.txt").exists())
        self.assertTrue(
            (task_dir / "distribution" / "wechat_channels" / "publish_payload.json").exists()
        )
        self.assertTrue((task_dir / "distribution" / "ready_to_publish.json").exists())
        self.assertTrue((task_dir / "distribution" / "publish_checklist.txt").exists())
        publish_queue_file = self.config.orchestrator_task_index_file.parent / "publish_queue.json"
        self.assertTrue(publish_queue_file.exists())
        publish_queue = json.loads(publish_queue_file.read_text(encoding="utf-8"))
        self.assertTrue(
            any(item["task_id"] == result.task_id for item in publish_queue.get("items", []))
        )

    def test_needs_edit_can_transition_to_approved(self) -> None:
        result, _task_file = self._create_task("待修改测试")
        write_review_decision(
            config=self.config,
            task_id=result.task_id,
            review_status="needs_edit",
            reviewed_by="tester",
            review_note="标题还需要再打磨。",
        )
        review_result = write_review_decision(
            config=self.config,
            task_id=result.task_id,
            review_status="approved",
            reviewed_by="tester",
            review_note="已修改完成，可以进入分发准备。",
        )
        self.assertEqual(review_result["review_status"], "approved")

    def test_list_review_tasks_supports_status_filter(self) -> None:
        result, _task_file = self._create_task("查询测试")
        tasks = list_review_tasks(
            self.config.orchestrator_task_index_file,
            review_status="pending_review",
        )
        self.assertTrue(any(item["task_id"] == result.task_id for item in tasks))


if __name__ == "__main__":
    unittest.main()
