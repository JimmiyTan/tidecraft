"""lobster-farm 一键安全演示入口。"""

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PROJECT_SRC = PROJECT_ROOT / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from lobster_farm.common.config import load_app_config
from lobster_farm.demo import DemoSafetyError, run_demo


STAGE_LABELS = {
    "safe_mode": "安全模式确认",
    "content_generated": "内容与审核包生成",
    "review_approved": "模拟人工审核",
    "receipts_written": "模拟人工发布回执",
    "archived": "任务归档",
    "completed": "Demo 完成",
}


def build_parser() -> argparse.ArgumentParser:
    """构建 Demo 命令行参数。"""
    parser = argparse.ArgumentParser(description="lobster-farm 一键离线功能演示")
    parser.add_argument(
        "--topic",
        default="AI 如何帮助本地商家提升短视频内容效率",
        help="演示主题",
    )
    parser.add_argument(
        "--operator",
        default="demo-operator",
        help="模拟审核人与发布人",
    )
    parser.add_argument(
        "--guided",
        action="store_true",
        help="每个阶段暂停，按 Enter 后继续",
    )
    return parser


def main() -> int:
    """使用固定 dry-run/mock 配置执行演示。"""
    args = build_parser().parse_args()
    config = load_app_config(PROJECT_ROOT / ".env.example")

    def show_progress(stage: str, payload: dict[str, object]) -> None:
        label = STAGE_LABELS.get(stage, stage)
        print(f"\n=== {label} ===")
        if stage == "safe_mode":
            print("配置：dry-run / Feishu dry-run / Video mock")
            print("安全边界：不会调用任何真实发布接口")
        elif stage == "content_generated":
            print(f"任务 ID：{payload['task_id']}")
            print(f"主题：{payload['topic']}")
            print(f"候选选题：{payload['candidate_count']} 条")
            print(f"审核目录：{payload['task_dir']}")
        elif stage == "review_approved":
            print("审核状态：approved（Demo 模拟人工确认）")
            print(f"分发文件：{payload['distribution_file_count']} 个")
        elif stage == "receipts_written":
            print("抖音、视频号人工发布回执已模拟写入")
            print("演示链接使用保留域名 demo.invalid，不会访问网络")
        elif stage == "archived":
            print("发布状态：archived")
        elif stage == "completed":
            print(f"演示摘要：{payload['summary_file']}")
        if args.guided and stage != "completed":
            input("按 Enter 继续下一步...")

    print("lobster-farm Phase 07 功能演示")
    print("说明：本 Demo 只模拟人工审核和人工发布回执，不执行真实发布。")
    try:
        summary = run_demo(
            project_root=PROJECT_ROOT,
            config=config,
            topic=args.topic,
            operator=args.operator,
            progress=show_progress,
        )
    except (DemoSafetyError, RuntimeError, ValueError, OSError) as exc:
        print(f"Demo 失败：{exc}", file=sys.stderr)
        return 1

    print("\n=== 最终摘要 ===")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
