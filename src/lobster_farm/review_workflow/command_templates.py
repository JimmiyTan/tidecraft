"""审核命令模板生成。"""

from pathlib import Path


def _build_windows_command(task_id: str, review_status: str) -> str:
    return (
        f'python .\\services\\orchestrator\\src\\review.py --task-id "{task_id}" '
        f'--review-status {review_status} --reviewed-by "<审核人>" --review-note "<审核备注>"'
    )


def _build_linux_command(task_id: str, review_status: str) -> str:
    return (
        f'python ./services/orchestrator/src/review.py --task-id "{task_id}" '
        f'--review-status {review_status} --reviewed-by "<审核人>" --review-note "<审核备注>"'
    )


def build_command_summary(task_id: str) -> str:
    """生成适合飞书摘要展示的审核命令说明。"""
    return "\n".join(
        [
            f'- approve：{_build_windows_command(task_id, "approved")}',
            f'- reject：{_build_windows_command(task_id, "rejected")}',
            f'- needs_edit：{_build_windows_command(task_id, "needs_edit")}',
        ]
    )


def export_review_command_templates(task_dir: Path, task_id: str) -> dict[str, str]:
    """为任务导出审核命令模板。"""
    templates = {
        "approve.cmd.txt": "approved",
        "reject.cmd.txt": "rejected",
        "needs_edit.cmd.txt": "needs_edit",
    }
    generated: dict[str, str] = {}
    for file_name, review_status in templates.items():
        content = "\n".join(
            [
                f"任务 ID：{task_id}",
                f"审核状态：{review_status}",
                "",
                "Windows：",
                _build_windows_command(task_id, review_status),
                "",
                "Linux / WSL2：",
                _build_linux_command(task_id, review_status),
                "",
                "说明：",
                "- 请将 <审核人> 替换为实际审核人",
                "- 请将 <审核备注> 替换为实际审核说明",
            ]
        )
        target = task_dir / file_name
        target.write_text(content, encoding="utf-8")
        generated[file_name] = target.as_posix()
    return generated
