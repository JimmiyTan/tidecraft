"""热点雷达实现。"""

import json
from datetime import datetime
from pathlib import Path

from lobster_farm.content_pipeline.models import CandidateContent, dataclass_to_dict


def load_benchmark_accounts(config_file: Path) -> list[dict[str, object]]:
    """读取自定义对标账号池。"""
    if not config_file.exists():
        return []
    payload = json.loads(config_file.read_text(encoding="utf-8"))
    return list(payload.get("accounts", []))


def collect_official_hotlist(topic: str) -> list[CandidateContent]:
    """获取官方热榜占位线索。

    当前阶段不联网抓取，先生成可替换的官方热榜结构。
    """
    now = datetime.now().isoformat()
    return [
        CandidateContent(
            title=f"{topic} 热点观察：用户最关心的三个问题",
            link="official-hotlist://douyin/demo",
            heat_signal="官方热榜占位：高讨论度",
            published_at=now,
            account_name="抖音官方热榜占位",
            keywords=[topic, "热点", "用户问题"],
        )
    ]


def collect_benchmark_candidates(
    topic: str,
    config_file: Path,
) -> list[CandidateContent]:
    """从自定义对标账号池生成候选线索。"""
    now = datetime.now().isoformat()
    candidates: list[CandidateContent] = []
    for account in load_benchmark_accounts(config_file):
        keywords = [str(item) for item in account.get("keywords", [])]
        candidates.append(
            CandidateContent(
                title=f"{topic} 对标结构观察：{account.get('account_name', '未命名账号')}",
                link=str(account.get("profile_url", "")),
                heat_signal="对标账号池占位：需后续接入真实抓取",
                published_at=now,
                account_name=str(account.get("account_name", "未命名账号")),
                keywords=keywords or [topic],
            )
        )
    return candidates


def build_candidate_pool(topic: str, output_file: Path) -> list[CandidateContent]:
    """构建候选池并写入 JSON。"""
    config_file = Path("config/benchmark_accounts.example.json")
    candidates = collect_official_hotlist(topic)
    candidates.extend(collect_benchmark_candidates(topic, config_file))
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(
        json.dumps(
            {
                "generated_at": datetime.now().isoformat(),
                "topic": topic,
                "candidates": [dataclass_to_dict(item) for item in candidates],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return candidates
