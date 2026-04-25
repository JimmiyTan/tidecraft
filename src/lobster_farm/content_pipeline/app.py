"""内容流水线入口。"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4

PROJECT_SRC = Path(__file__).resolve().parents[2]
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from lobster_farm.common.config import load_app_config
from lobster_farm.content_pipeline.models import dataclass_to_dict
from lobster_farm.content_pipeline.review import build_review_message
from lobster_farm.distribution.package_builder import build_distribution_packages
from lobster_farm.feishu_bridge.schemas import ReviewMessageResponse
from lobster_farm.feishu_bridge.sender import send_message
from lobster_farm.rewrite_engine.engine import generate_rewrites
from lobster_farm.trend_radar.radar import build_candidate_pool
from lobster_farm.viral_analyzer.analyzer import analyze_candidate


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数。"""
    parser = argparse.ArgumentParser(description="原创内容流水线")
    parser.add_argument("--topic", required=True, help="输入主题")
    return parser


def make_task_id() -> str:
    """生成任务 ID。"""
    return "content_" + datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid4().hex[:8]


def write_json(file_path: Path, payload: object) -> None:
    """写入 JSON 文件。"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main() -> int:
    """执行原创内容流水线。"""
    args = build_parser().parse_args()
    config = load_app_config()
    task_id = make_task_id()
    task_dir = config.export_dir / "content_pipeline" / task_id
    review_dir = task_dir.relative_to(config.workspace_root).as_posix()
    task_dir.mkdir(parents=True, exist_ok=True)

    candidate_pool_file = task_dir / "candidate_pool.json"
    candidates = build_candidate_pool(args.topic, candidate_pool_file)
    if not candidates:
        raise RuntimeError(f"task_id={task_id} 候选池为空")

    candidate = candidates[0]
    analysis = analyze_candidate(candidate)
    rewrites = generate_rewrites(args.topic, analysis)
    selected_rewrite = rewrites[0]
    distribution_files = build_distribution_packages(task_dir, selected_rewrite)
    review_message = build_review_message(
        task_id=task_id,
        candidate=candidate,
        analysis=analysis,
        rewrites=rewrites,
        review_dir=review_dir,
    )
    send_result = send_message(
        config,
        ReviewMessageResponse(
            ok=True,
            message=review_message,
            delivery_mode="content_review",
            task_id=task_id,
            review_dir=review_dir,
            payload={
                "task_id": task_id,
                "candidate_link": candidate.link,
                "review_dir": review_dir,
                "rewrite_titles": [item.title for item in rewrites],
            },
        ),
    )

    write_json(task_dir / "viral_analysis.json", dataclass_to_dict(analysis))
    write_json(task_dir / "rewrites.json", dataclass_to_dict(rewrites))
    write_json(
        task_dir / "review_message.json",
        {
            "task_id": task_id,
            "message": review_message,
            "send_result": dataclass_to_dict(send_result),
        },
    )
    write_json(
        task_dir / "pipeline_state.json",
        {
            "task_id": task_id,
            "topic": args.topic,
            "status": "review_pending",
            "candidate_link": candidate.link,
            "review_dir": review_dir,
            "distribution_files": distribution_files,
        },
    )
    print(review_message)
    print(f"任务 ID：{task_id}")
    print(f"产物目录：{review_dir}")
    print(f"飞书状态：{send_result.status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
