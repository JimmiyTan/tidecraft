"""视频网关应用层。"""

import argparse
import json
from datetime import datetime

from lobster_farm.common.config import load_app_config
from lobster_farm.common.logging_utils import setup_logger
from lobster_farm.video_gateway.exporter import build_export_summary
from lobster_farm.video_gateway.providers.registry import get_video_provider
from lobster_farm.video_gateway.schemas import VideoJobRequest


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数。"""
    parser = argparse.ArgumentParser(description="视频网关占位服务")
    parser.add_argument("--topic", required=True, help="输入主题")
    parser.add_argument(
        "--task-id",
        default="video_gateway_" + datetime.now().strftime("%Y%m%d_%H%M%S"),
        help="任务 ID",
    )
    parser.add_argument(
        "--review-items-json",
        default='[{"title":"占位选题 1","script_text":"占位脚本 1"}]',
        help="审核条目 JSON 数组",
    )
    return parser


def main() -> int:
    """执行配置指定的视频 provider。"""
    args = build_parser().parse_args()
    config = load_app_config()
    logger = setup_logger(
        "lobster_farm.video_gateway",
        config.log_level,
        config.log_dir / "services" / "video_gateway.log",
    )
    task_output_dir = config.video_output_dir / args.task_id
    request = VideoJobRequest(
        task_id=args.task_id,
        topic=args.topic,
        review_items=json.loads(args.review_items_json),
        output_dir=task_output_dir,
    )
    result = get_video_provider(config).generate(request)
    logger.info("视频 provider=%s status=%s", result.provider, result.status)
    print(build_export_summary(result))
    return 0 if result.ok else 1
