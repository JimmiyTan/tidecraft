"""审核写回命令入口。"""

import argparse
import json
import sys
from pathlib import Path

from lobster_farm.common.config import load_app_config
from lobster_farm.review_workflow.listing import list_review_tasks
from lobster_farm.review_workflow.service import write_review_decision


def build_parser() -> argparse.ArgumentParser:
    """构建审核写回参数。"""
    parser = argparse.ArgumentParser(description="lobster-farm 审核工具")
    subparsers = parser.add_subparsers(dest="command", required=True)

    review_parser = subparsers.add_parser("write-review", help="写回审核结果")
    review_parser.add_argument("--task-id", required=True, help="任务 ID")
    review_parser.add_argument(
        "--review-status",
        required=True,
        choices=["approved", "rejected", "needs_edit"],
        help="审核结果",
    )
    review_parser.add_argument("--reviewed-by", required=True, help="审核人")
    review_parser.add_argument("--review-note", default="", help="审核备注")

    list_parser = subparsers.add_parser("list-review-tasks", help="列出待审核任务")
    list_parser.add_argument(
        "--review-status",
        default="",
        choices=["", "pending_review", "needs_edit", "approved", "rejected"],
        help="按审核状态筛选",
    )
    return parser


def main() -> int:
    """执行审核写回。"""
    script_stem = Path(sys.argv[0]).stem
    # 兼容 list_review_tasks.py --review-status ...
    if len(sys.argv) > 1 and script_stem == "list_review_tasks":
        if sys.argv[1] != "list-review-tasks":
            sys.argv.insert(1, "list-review-tasks")
    # 兼容 phase-05 旧写法：review.py --task-id ... --review-status ...
    if len(sys.argv) > 1 and script_stem != "list_review_tasks" and sys.argv[1].startswith("--"):
        sys.argv.insert(1, "write-review")
    args = build_parser().parse_args()
    config = load_app_config()
    if args.command == "write-review":
        result = write_review_decision(
            config=config,
            task_id=args.task_id,
            review_status=args.review_status,
            reviewed_by=args.reviewed_by,
            review_note=args.review_note,
        )
        print(f"任务 ID：{result['task_id']}")
        print(f"审核状态：{result['review_status']}")
        print(f"审核人：{result['reviewed_by']}")
        print(f"任务目录：{result['task_dir']}")
        if result["distribution_files"]:
            print("分发准备包：已生成")
        else:
            print("分发准备包：未生成")
        return 0

    tasks = list_review_tasks(
        config.orchestrator_task_index_file,
        review_status=args.review_status,
    )
    print(json.dumps(tasks, ensure_ascii=False, indent=2))
    return 0
