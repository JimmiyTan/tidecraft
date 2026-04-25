"""工作流最小测试。"""

import sys
from pathlib import Path
import unittest

PROJECT_SRC = Path(__file__).resolve().parents[3] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from lobster_farm.common.config import load_app_config
from lobster_farm.orchestrator.state_machine import (
    WorkflowState,
    assert_transition,
    can_transition,
)
from lobster_farm.orchestrator.workflow import run_workflow


class WorkflowTestCase(unittest.TestCase):
    """验证工作流和状态机。"""

    def test_run_workflow(self) -> None:
        project_root = Path(__file__).resolve().parents[3]
        config = load_app_config(project_root / ".env.example")
        result = run_workflow(
            project_root=project_root,
            config=config,
            topic="龙虾养殖",
        )
        self.assertEqual(result.status, "completed")
        self.assertEqual(len(result.candidate_titles), 5)
        self.assertEqual(len(result.scripts), 5)
        self.assertTrue(result.task_dir and result.task_dir.exists())
        self.assertTrue((result.task_dir / "summary.txt").exists())

    def test_state_machine_allows_normal_flow(self) -> None:
        self.assertTrue(
            can_transition(WorkflowState.CREATED, WorkflowState.TOPICS_GENERATED)
        )
        self.assertTrue(
            can_transition(WorkflowState.VIDEO_GENERATED, WorkflowState.COMPLETED)
        )

    def test_state_machine_rejects_invalid_flow(self) -> None:
        with self.assertRaises(ValueError):
            assert_transition(WorkflowState.CREATED, WorkflowState.COMPLETED)


if __name__ == "__main__":
    unittest.main()
