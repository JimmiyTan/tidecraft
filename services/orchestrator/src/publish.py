"""人工发布队列与回执 CLI。"""

import argparse
import json
import sys
from pathlib import Path

PROJECT_SRC = Path(__file__).resolve().parents[3] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from lobster_farm.common.config import load_app_config
from lobster_farm.publishing.service import (
    archive_task,
    get_task_publish_status,
    list_publish_queue,
    write_publish_result,
)


def build_parser() -> argparse.ArgumentParser:
    """构建发布管理参数。"""
    parser = argparse.ArgumentParser(description="lobster-farm 人工发布管理工具")
    parser.add_argument("--list", action="store_true", help="查询发布队列")
    parser.add_argument("--task-id", default="", help="任务 ID")
    parser.add_argument(
        "--platform",
        default="",
        choices=["", "douyin", "wechat_channels"],
        help="发布平台",
    )
    parser.add_argument(
        "--status",
        default="",
        choices=[
            "",
            "ready_to_publish",
            "manually_published",
            "publish_failed",
            "archived",
        ],
        help="查询用发布状态",
    )
    parser.add_argument(
        "--publish-status",
        default="",
        choices=["", "manually_published", "publish_failed"],
        help="写回用发布状态",
    )
    parser.add_argument("--publish-url", default="", help="人工发布后的链接")
    parser.add_argument("--published-by", default="", help="发布人")
    parser.add_argument("--publish-note", default="", help="发布备注")
    parser.add_argument("--archive", action="store_true", help="归档已完成发布任务")
    return parser


def main() -> int:
    """执行发布队列查询、回写或归档。"""
    args = build_parser().parse_args()
    config = load_app_config()

    if args.list:
        result = list_publish_queue(
            config=config,
            status=args.status,
            platform=args.platform,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if args.archive:
        if not args.task_id:
            raise SystemExit("归档必须提供 --task-id")
        result = archive_task(config=config, task_id=args.task_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if args.task_id and not args.publish_status:
        result = get_task_publish_status(config=config, task_id=args.task_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if args.publish_status:
        if not args.task_id or not args.platform:
            raise SystemExit("发布回写必须提供 --task-id 与 --platform")
        if not args.published_by:
            raise SystemExit("发布回写必须提供 --published-by")
        result = write_publish_result(
            config=config,
            task_id=args.task_id,
            platform=args.platform,
            publish_status=args.publish_status,
            published_by=args.published_by,
            publish_url=args.publish_url,
            publish_note=args.publish_note,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    raise SystemExit("请提供 --list、--task-id、--publish-status 或 --archive")


if __name__ == "__main__":
    raise SystemExit(main())
