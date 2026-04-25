"""内容流水线飞书审核消息。"""

from lobster_farm.content_pipeline.models import CandidateContent, RewriteVersion
from lobster_farm.viral_analyzer.analyzer import build_structure_summary
from lobster_farm.content_pipeline.models import ViralAnalysis


def build_review_message(
    task_id: str,
    candidate: CandidateContent,
    analysis: ViralAnalysis,
    rewrites: list[RewriteVersion],
    review_dir: str,
) -> str:
    """生成飞书审核消息。"""
    titles = "\n".join(f"- {item.version_name}：{item.title}" for item in rewrites)
    return (
        "【原创内容流水线审核】\n"
        f"任务 ID：{task_id}\n"
        f"原始热点链接：{candidate.link}\n"
        f"爆点结构摘要：{build_structure_summary(analysis)}\n"
        f"改写版标题：\n{titles}\n"
        f"审核目录：{review_dir}\n"
        "说明：本任务只做结构拆解和原创改写，不输出原视频逐字复刻脚本，默认不自动发布。"
    )
