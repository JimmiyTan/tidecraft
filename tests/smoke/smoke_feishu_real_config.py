"""飞书 real 模式配置检查 smoke。"""

import sys
from pathlib import Path


def main() -> int:
    """验证 real 配置可被加载，但不触发真实联网。"""
    project_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(project_root / "src"))

    from lobster_farm.common.config import load_app_config
    from lobster_farm.feishu_bridge.adapters import get_feishu_adapter

    temp_env = project_root / "data" / "temp" / "valid_feishu_real.env"
    temp_env.parent.mkdir(parents=True, exist_ok=True)
    temp_env.write_text(
        "\n".join(
            [
                "RUN_MODE=real",
                "FEISHU_ADAPTER=real",
                "FEISHU_API_BASE_URL=https://example.test",
                "FEISHU_APP_ID=test_app_id",
                "FEISHU_APP_SECRET=test_secret",
                "FEISHU_DEFAULT_CHAT_ID=test_chat_id",
                "VIDEO_PROVIDER=mock",
            ]
        ),
        encoding="utf-8",
    )
    try:
        config = load_app_config(temp_env)
        adapter = get_feishu_adapter(config)
        if adapter.name != "real":
            raise SystemExit("real 配置检查失败：未选择 real adapter。")
        print("smoke_feishu_real_config: ok")
        return 0
    finally:
        temp_env.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
