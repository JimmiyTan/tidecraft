"""飞书桥接应用层。"""

import argparse
import json

from lobster_farm.common.config import load_app_config
from lobster_farm.common.logging_utils import setup_logger
from lobster_farm.feishu_bridge.formatter import (
    build_review_items,
    format_review_message,
)
from lobster_farm.feishu_bridge.schemas import ReviewMessageRequest
from lobster_farm.feishu_bridge.sender import send_message


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数。"""
    parser = argparse.ArgumentParser(description="飞书桥接占位服务")
    parser.add_argument("--topic", required=True, help="输入主题")
    parser.add_argument(
        "--titles-json",
        default='["占位选题 1","占位选题 2","占位选题 3","占位选题 4","占位选题 5"]',
        help="选题 JSON 数组",
    )
    parser.add_argument(
        "--scripts-json",
        default='["占位脚本 1","占位脚本 2","占位脚本 3","占位脚本 4","占位脚本 5"]',
        help="脚本 JSON 数组",
    )
    return parser


def main() -> int:
    """执行消息格式化与发送 adapter。"""
    args = build_parser().parse_args()
    config = load_app_config()
    logger = setup_logger(
        "lobster_farm.feishu_bridge",
        config.log_level,
        config.log_dir / "services" / "feishu_bridge.log",
    )
    titles = json.loads(args.titles_json)
    scripts = json.loads(args.scripts_json)
    request = ReviewMessageRequest(
        topic=args.topic,
        review_items=build_review_items(titles, scripts),
    )
    response = format_review_message(request)
    send_result = send_message(config, response)
    logger.info("飞书 adapter=%s status=%s", send_result.adapter, send_result.status)
    print(response.message)
    print(send_result.message)
    return 0 if send_result.adapter == "dry-run" or send_result.ok else 1
