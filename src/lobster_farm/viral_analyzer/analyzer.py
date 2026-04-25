"""爆款结构拆解实现。"""

from lobster_farm.content_pipeline.models import CandidateContent, ViralAnalysis


def analyze_candidate(candidate: CandidateContent) -> ViralAnalysis:
    """对候选内容做结构化拆解，不生成原脚本复刻。"""
    keyword_text = "、".join(candidate.keywords[:3]) if candidate.keywords else "行业痛点"
    return ViralAnalysis(
        hook_type="问题前置型钩子",
        first_three_seconds_conflict=f"围绕“{keyword_text}”提出一个用户以为简单但实际容易踩坑的问题。",
        emotion_curve="疑惑 -> 被戳中 -> 看到方法 -> 感到可执行",
        reversal_point="从常见误解切到反直觉但合理的专业建议。",
        shot_rhythm="前 3 秒强字幕抛问题，中段 3 个快切解释，结尾给审核/咨询入口。",
        cta_type="轻 CTA：引导评论区留言或内部人工审核。",
        reusable_structure="痛点提问 + 误区拆解 + 专业反转 + 可执行清单 + 轻 CTA",
    )


def build_structure_summary(analysis: ViralAnalysis) -> str:
    """生成爆点结构摘要。"""
    return (
        f"钩子：{analysis.hook_type}；"
        f"冲突：{analysis.first_three_seconds_conflict}；"
        f"反转：{analysis.reversal_point}；"
        f"复用结构：{analysis.reusable_structure}"
    )
