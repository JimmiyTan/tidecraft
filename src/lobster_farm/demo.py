"""项目功能演示编排。

本模块只允许 dry-run/mock 配置，用于演示人工审核与人工发布回执，
不会调用真实飞书、视频或短视频平台发布接口。
"""

import json
from collections.abc import Callable
from pathlib import Path

from lobster_farm.common.config import AppConfig
from lobster_farm.orchestrator.state_store import (
    append_task_index,
    write_state,
    write_task_state,
)
from lobster_farm.orchestrator.workflow import run_workflow
from lobster_farm.publishing.service import (
    archive_task,
    get_task_publish_status,
    write_publish_result,
)
from lobster_farm.review_workflow.service import write_review_decision


class DemoSafetyError(ValueError):
    """Demo 配置不满足安全默认值。"""


DemoProgress = Callable[[str, dict[str, object]], None]


def _notify(
    progress: DemoProgress | None,
    stage: str,
    payload: dict[str, object],
) -> None:
    if progress is not None:
        progress(stage, payload)


def assert_demo_safe_config(config: AppConfig) -> None:
    """拒绝任何可能触发真实外部服务的 Demo 配置。"""
    unsafe = []
    if config.run_mode != "dry-run":
        unsafe.append(f"RUN_MODE={config.run_mode}")
    if config.feishu_adapter != "dry-run":
        unsafe.append(f"FEISHU_ADAPTER={config.feishu_adapter}")
    if config.video_provider != "mock":
        unsafe.append(f"VIDEO_PROVIDER={config.video_provider}")
    credential_fields = {
        "FEISHU_APP_ID": config.feishu_app_id,
        "FEISHU_APP_SECRET": config.feishu_app_secret,
        "FEISHU_DEFAULT_CHAT_ID": config.feishu_default_chat_id,
        "VIDEO_API_KEY": config.video_api_key,
    }
    populated_credentials = [
        name for name, value in credential_fields.items() if value
    ]
    if populated_credentials:
        unsafe.append("检测到非空凭据字段：" + ", ".join(populated_credentials))
    if unsafe:
        raise DemoSafetyError(
            "Demo 只允许 dry-run/mock，当前不安全配置：" + ", ".join(unsafe)
        )


def run_demo(
    project_root: Path,
    config: AppConfig,
    topic: str,
    operator: str = "demo-operator",
    progress: DemoProgress | None = None,
) -> dict[str, object]:
    """执行可展示的完整模拟闭环并返回摘要。"""
    assert_demo_safe_config(config)
    _notify(
        progress,
        "safe_mode",
        {
            "run_mode": config.run_mode,
            "feishu_adapter": config.feishu_adapter,
            "video_provider": config.video_provider,
        },
    )

    workflow_result = run_workflow(
        project_root=project_root,
        config=config,
        topic=topic,
    )
    write_state(config.orchestrator_state_file, workflow_result)
    task_file = write_task_state(
        config.orchestrator_task_state_dir,
        workflow_result,
    )
    append_task_index(
        config.orchestrator_task_index_file,
        workflow_result,
        task_file,
    )
    if workflow_result.status != "completed":
        raise RuntimeError(
            "Demo 内容工作流失败：" + (workflow_result.error_message or "未知错误")
        )
    task_id = workflow_result.task_id
    task_dir = workflow_result.task_dir
    if task_dir is None:
        raise RuntimeError("Demo 工作流未返回任务目录。")
    _notify(
        progress,
        "content_generated",
        {
            "task_id": task_id,
            "topic": topic,
            "candidate_count": len(workflow_result.candidate_titles),
            "task_dir": task_dir.as_posix(),
        },
    )

    review_result = write_review_decision(
        config=config,
        task_id=task_id,
        review_status="approved",
        reviewed_by=operator,
        review_note="Demo 模拟人工审核通过；未触发自动发布。",
    )
    _notify(
        progress,
        "review_approved",
        {
            "task_id": task_id,
            "review_status": review_result["review_status"],
            "distribution_file_count": len(review_result["distribution_files"]),
        },
    )

    receipt_results = []
    for platform in ("douyin", "wechat_channels"):
        receipt_results.append(
            write_publish_result(
                config=config,
                task_id=task_id,
                platform=platform,
                publish_status="manually_published",
                published_by=operator,
                publish_url=f"https://demo.invalid/{platform}/{task_id}",
                publish_note="Demo 模拟人工发布回执；未调用真实平台接口。",
            )
        )
    published_status = get_task_publish_status(config, task_id)
    _notify(
        progress,
        "receipts_written",
        {
            "task_id": task_id,
            "platform_count": len(receipt_results),
            "platforms": published_status["platforms"],
        },
    )

    archive_result = archive_task(config=config, task_id=task_id)
    final_status = get_task_publish_status(config, task_id)
    _notify(
        progress,
        "archived",
        {
            "task_id": task_id,
            "publish_status": archive_result["publish_status"],
        },
    )

    summary = {
        "demo": True,
        "safe_mode": {
            "run_mode": config.run_mode,
            "feishu_adapter": config.feishu_adapter,
            "video_provider": config.video_provider,
            "real_publish_called": False,
        },
        "task_id": task_id,
        "topic": topic,
        "operator": operator,
        "candidate_titles": workflow_result.candidate_titles,
        "workflow_status": workflow_result.status,
        "review_status": review_result["review_status"],
        "publish_status": archive_result["publish_status"],
        "platforms": final_status["platforms"],
        "task_dir": task_dir.as_posix(),
    }
    summary_file = task_dir / "demo_summary.json"
    summary["summary_file"] = summary_file.as_posix()
    summary_file.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    _notify(progress, "completed", summary)
    return summary
