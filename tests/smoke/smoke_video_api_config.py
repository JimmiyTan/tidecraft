"""视频 api 模式配置检查 smoke。"""

import sys
from pathlib import Path


def main() -> int:
    """验证 api provider 配置可加载，但不触发联网。"""
    project_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(project_root / "src"))

    from lobster_farm.common.config import load_app_config
    from lobster_farm.video_gateway.providers.registry import get_video_provider

    temp_env = project_root / "data" / "temp" / "valid_video_api.env"
    temp_env.parent.mkdir(parents=True, exist_ok=True)
    temp_env.write_text(
        "\n".join(
            [
                "RUN_MODE=real",
                "FEISHU_ADAPTER=dry-run",
                "VIDEO_PROVIDER=api",
                "VIDEO_API_KEY=test_key",
                "VIDEO_PROVIDER_BASE_URL=https://video.example.test",
                "VIDEO_SUBMIT_PATH=/submit",
                "VIDEO_STATUS_PATH=/status/{remote_task_id}",
            ]
        ),
        encoding="utf-8",
    )
    try:
        config = load_app_config(temp_env)
        provider = get_video_provider(config)
        if provider.name != "api":
            raise SystemExit("api 配置检查失败：未选择 api provider。")
        print("smoke_video_api_config: ok")
        return 0
    finally:
        temp_env.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
