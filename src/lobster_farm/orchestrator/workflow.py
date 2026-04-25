"""第二阶段安全闭环工作流。"""

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from lobster_farm.common.config import AppConfig
from lobster_farm.common.paths import get_project_root
from lobster_farm.feishu_bridge.formatter import (
    build_review_items,
    format_review_message,
)
from lobster_farm.feishu_bridge.schemas import ReviewMessageRequest
from lobster_farm.feishu_bridge.sender import send_message
from lobster_farm.orchestrator.exporter import export_review_package
from lobster_farm.orchestrator.models import WorkflowResult
from lobster_farm.orchestrator.retry import run_with_retry
from lobster_farm.orchestrator.state_machine import WorkflowState, assert_transition
from lobster_farm.video_gateway.providers.registry import get_video_provider
from lobster_farm.video_gateway.schemas import VideoJobRequest
from lobster_farm.review_workflow.command_templates import build_command_summary


def generate_task_id() -> str:
    """生成任务 ID。"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"task_{timestamp}_{uuid4().hex[:8]}"


def generate_candidate_titles(topic: str) -> list[str]:
    """生成 5 条选题占位结果。"""
    return [
        f"{topic}：新手避坑入门",
        f"{topic}：3 个常见误区",
        f"{topic}：一天流程拆解",
        f"{topic}：低成本实操建议",
        f"{topic}：人工审核演示样例",
    ]


def generate_scripts(candidate_titles: list[str]) -> list[str]:
    """为每条选题生成脚本占位结果。"""
    scripts: list[str] = []
    for title in candidate_titles:
        scripts.append(
            f"开场：今天我们聚焦《{title}》。"
            " 主体：这里是第二阶段的安全闭环占位脚本，用于验证可接真实服务的结构。"
            " 收尾：当前结果仅供人工审核，不会自动正式发布。"
        )
    return scripts


def _transition(current: WorkflowState, target: WorkflowState) -> WorkflowState:
    """执行状态切换。"""
    assert_transition(current, target)
    return target


def run_workflow(project_root: Path, config: AppConfig, topic: str) -> WorkflowResult:
    """执行第二阶段安全闭环。"""
    task_id = generate_task_id()
    task_dir = config.video_output_dir / task_id
    review_dir = task_dir.relative_to(get_project_root()).as_posix()
    state = WorkflowState.CREATED
    result = WorkflowResult(task_id=task_id, topic=topic, task_dir=task_dir)

    try:
        candidate_titles = run_with_retry(
            lambda: generate_candidate_titles(topic),
            config.orchestrator_max_retries,
        )
        state = _transition(state, WorkflowState.TOPICS_GENERATED)
        result.candidate_titles = candidate_titles
        result.status = state.value

        scripts = run_with_retry(
            lambda: generate_scripts(candidate_titles),
            config.orchestrator_max_retries,
        )
        state = _transition(state, WorkflowState.SCRIPTS_GENERATED)
        result.scripts = scripts
        result.status = state.value

        review_items = build_review_items(candidate_titles, scripts)
        state = _transition(state, WorkflowState.REVIEW_MESSAGE_GENERATED)
        result.status = state.value

        video_request = VideoJobRequest(
            task_id=task_id,
            topic=topic,
            review_items=[
                {"title": item.title, "script_text": item.script_text}
                for item in review_items
            ],
            output_dir=task_dir,
        )
        state = _transition(state, WorkflowState.VIDEO_REQUESTED)
        result.status = state.value
        video_result = get_video_provider(config).generate(video_request)
        if not video_result.ok:
            raise RuntimeError(video_result.error_message or "视频 provider 执行失败")
        state = _transition(state, WorkflowState.VIDEO_READY)
        result.status = state.value
        state = _transition(state, WorkflowState.VIDEO_GENERATED)
        result.export_file = video_result.output_file
        result.video_provider = video_result.provider
        result.video_provider_status = video_result.provider_status
        result.video_remote_task_id = video_result.remote_task_id
        result.status = state.value

        video_summary = (
            f"provider={video_result.provider}; "
            f"remote_task_id={video_result.remote_task_id or '无'}; "
            f"provider_status={video_result.provider_status or video_result.status}"
        )
        review_response = format_review_message(
            ReviewMessageRequest(
                topic=topic,
                review_items=review_items,
                task_id=task_id,
                review_dir=review_dir,
                video_summary=video_summary,
                review_status=result.review_status,
                command_summary=build_command_summary(task_id),
            )
        )
        send_result = send_message(config, review_response)
        result.review_message = review_response.message
        result.review_send_status = send_result.status

        export_review_package(
            task_dir=task_dir,
            task_id=task_id,
            topic=topic,
            candidate_titles=candidate_titles,
            scripts=scripts,
            review_response=review_response,
            send_result=send_result,
            video_result=video_result,
        )
        state = _transition(state, WorkflowState.COMPLETED)
        result.status = state.value
        return result
    except Exception as exc:  # noqa: BLE001 - 需要统一失败落盘
        if state is not WorkflowState.FAILED:
            state = WorkflowState.FAILED
        result.status = state.value
        result.error_message = str(exc)
        return result
