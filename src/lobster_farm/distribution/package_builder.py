"""双平台分发包生成。"""

import json
from pathlib import Path

from lobster_farm.content_pipeline.models import RewriteVersion


def build_distribution_packages(task_dir: Path, rewrite: RewriteVersion) -> dict[str, str]:
    """生成抖音和视频号发布准备包。"""
    files: dict[str, str] = {}
    douyin_dir = task_dir / "douyin"
    wechat_dir = task_dir / "wechat_channels"
    douyin_dir.mkdir(parents=True, exist_ok=True)
    wechat_dir.mkdir(parents=True, exist_ok=True)

    platform_payloads = {
        "douyin": {
            "dir": douyin_dir,
            "title": rewrite.title,
            "caption": "短平快表达，突出前 3 秒冲突。\n" + "\n".join(rewrite.lines),
            "hashtags": rewrite.hashtags + ["抖音热点", "原创改写"],
        },
        "wechat_channels": {
            "dir": wechat_dir,
            "title": rewrite.title.replace("翻车", "踩坑"),
            "caption": "更适合视频号的稳健表达：\n" + "\n".join(rewrite.lines),
            "hashtags": rewrite.hashtags + ["视频号", "行业观察"],
        },
    }

    for platform, payload in platform_payloads.items():
        platform_dir = payload["dir"]
        title_file = platform_dir / "title.txt"
        caption_file = platform_dir / "caption.txt"
        hashtags_file = platform_dir / "hashtags.json"
        title_file.write_text(str(payload["title"]), encoding="utf-8")
        caption_file.write_text(str(payload["caption"]), encoding="utf-8")
        hashtags_file.write_text(
            json.dumps(payload["hashtags"], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        files[f"{platform}/title.txt"] = title_file.as_posix()
        files[f"{platform}/caption.txt"] = caption_file.as_posix()
        files[f"{platform}/hashtags.json"] = hashtags_file.as_posix()
    return files


def build_review_distribution_package(
    task_dir: Path,
    task_id: str,
    topic: str,
    candidate_titles: list[str],
    scripts: list[str],
    review_note: str,
) -> dict[str, str]:
    """为 approved 任务生成双平台分发准备包。"""
    distribution_root = task_dir / "distribution"
    distribution_root.mkdir(parents=True, exist_ok=True)
    primary_title = candidate_titles[0] if candidate_titles else topic
    primary_script = scripts[0] if scripts else f"{topic} 审核通过，待人工发布。"

    payloads = {
        "douyin": {
            "title": primary_title,
            "caption": f"{primary_script}\n\n审核备注：{review_note or '无'}",
            "hashtags": [topic, "抖音发布准备", "人工审核通过"],
        },
        "wechat_channels": {
            "title": primary_title.replace("误区", "要点"),
            "caption": f"视频号版发布准备：\n{primary_script}\n\n审核备注：{review_note or '无'}",
            "hashtags": [topic, "视频号发布准备", "人工审核通过"],
        },
    }

    generated_files: dict[str, str] = {}
    for platform, payload in payloads.items():
        platform_dir = distribution_root / platform
        platform_dir.mkdir(parents=True, exist_ok=True)
        (platform_dir / "title.txt").write_text(payload["title"], encoding="utf-8")
        (platform_dir / "caption.txt").write_text(payload["caption"], encoding="utf-8")
        (platform_dir / "hashtags.json").write_text(
            json.dumps(payload["hashtags"], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (platform_dir / "publish_payload.json").write_text(
            json.dumps(
                {
                    "task_id": task_id,
                    "platform": platform,
                    "title": payload["title"],
                    "caption": payload["caption"],
                    "hashtags": payload["hashtags"],
                    "auto_publish": False,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        generated_files[f"{platform}/title.txt"] = (platform_dir / "title.txt").as_posix()
        generated_files[f"{platform}/caption.txt"] = (
            platform_dir / "caption.txt"
        ).as_posix()
        generated_files[f"{platform}/hashtags.json"] = (
            platform_dir / "hashtags.json"
        ).as_posix()
        generated_files[f"{platform}/publish_payload.json"] = (
            platform_dir / "publish_payload.json"
        ).as_posix()
    return generated_files
