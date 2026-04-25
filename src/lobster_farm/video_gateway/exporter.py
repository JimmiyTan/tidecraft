"""视频结果导出辅助方法。"""

from lobster_farm.video_gateway.schemas import VideoJobResult


def build_export_summary(result: VideoJobResult) -> str:
    """生成导出摘要文本。"""
    output = result.output_file.as_posix() if result.output_file else ""
    return (
        f"provider={result.provider}; status={result.status}; "
        f"output={output}; error={result.error_message}"
    )
