"""原创改写实现。"""

from lobster_farm.content_pipeline.models import ViralAnalysis, RewriteVersion


def generate_rewrites(topic: str, analysis: ViralAnalysis) -> list[RewriteVersion]:
    """基于爆点结构生成三版原创内容。"""
    base_scene = analysis.reusable_structure
    return [
        RewriteVersion(
            version_name="专业靠谱版",
            title=f"{topic}别只看热闹，真正关键的是这 3 步",
            storyboard=[
                "镜头 1：AI 分身正面出镜，抛出行业常见误区。",
                "镜头 2：切到清单字幕，逐条拆解关键判断。",
                "镜头 3：回到人物，给出人工审核提醒。",
            ],
            lines=[
                f"很多人看{topic}，第一反应是照着做，但真正重要的是先判断场景。",
                f"这条内容我不复刻原视频，只借用它的结构：{base_scene}。",
                "如果你要落地，先把条件、风险和预算列清楚，再决定下一步。",
            ],
            cover_text=f"{topic}真正关键的 3 步",
            hashtags=[topic, "专业靠谱", "行业方法"],
        ),
        RewriteVersion(
            version_name="反差搞笑版",
            title=f"{topic}看起来很简单，实际第一步就容易翻车",
            storyboard=[
                "镜头 1：AI 分身用夸张表情说出错误做法。",
                "镜头 2：快速打断，字幕提示“别急”。",
                "镜头 3：用轻松语气给出正确流程。",
            ],
            lines=[
                f"你以为{topic}就是复制一个爆款动作？先别急，第一步可能就翻车。",
                "爆点不是台词本身，而是先让人意识到反差。",
                "正确做法是先抓痛点，再讲方法，最后给一个能执行的小动作。",
            ],
            cover_text="别再照抄爆款了",
            hashtags=[topic, "反差搞笑", "避坑"],
        ),
        RewriteVersion(
            version_name="客户共鸣版",
            title=f"做{topic}的人，最怕的不是不会做，而是方向错了",
            storyboard=[
                "镜头 1：AI 分身讲客户常见焦虑。",
                "镜头 2：字幕列出 3 个真实顾虑。",
                "镜头 3：给出温和但明确的建议。",
            ],
            lines=[
                f"很多客户聊到{topic}，真正担心的不是成本，而是做完没有结果。",
                "所以这条内容的核心不是复刻，而是把情绪路径换成自己的行业表达。",
                "先让对方觉得你懂他，再给出清晰选择，转化才自然。",
            ],
            cover_text=f"{topic}客户真正担心什么",
            hashtags=[topic, "客户共鸣", "真实痛点"],
        ),
    ]
