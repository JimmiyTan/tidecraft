"""工作流编排应用层。"""

import argparse

from lobster_farm.common.config import load_app_config
from lobster_farm.common.logging_utils import setup_logger
from lobster_farm.orchestrator.state_store import (
    append_task_index,
    write_state,
    write_task_state,
)
from lobster_farm.orchestrator.workflow import run_workflow


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数。"""
    parser = argparse.ArgumentParser(description="第二阶段安全闭环工作流")
    parser.add_argument("--topic", required=True, help="输入主题")
    return parser


def main() -> int:
    """执行第二阶段安全闭环工作流。"""
    args = build_parser().parse_args()
    config = load_app_config()
    logger = setup_logger(
        "lobster_farm.orchestrator",
        config.log_level,
        config.log_dir / "services" / "orchestrator.log",
    )
    result = run_workflow(project_root=config.workspace_root, config=config, topic=args.topic)
    write_state(config.orchestrator_state_file, result)
    task_file = write_task_state(config.orchestrator_task_state_dir, result)
    append_task_index(config.orchestrator_task_index_file, result, task_file)
    logger.info("工作流执行完成，task_id=%s status=%s", result.task_id, result.status)
    print(result.review_message)
    print(f"任务 ID：{result.task_id}")
    print(f"任务目录：{result.task_dir.as_posix() if result.task_dir else ''}")
    print(f"状态：{result.status}")
    if result.error_message:
        print(f"错误：{result.error_message}")
    return 0 if result.status == "completed" else 1
