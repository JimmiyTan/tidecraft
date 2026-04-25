"""失败分支 smoke 验证。"""

import sys
from pathlib import Path


def main() -> int:
    """验证 real/api 配置缺失时会被配置校验拦截。"""
    project_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(project_root / "src"))

    from lobster_farm.common.config import ConfigError, load_app_config

    temp_env = project_root / "data" / "temp" / "invalid_real.env"
    temp_env.parent.mkdir(parents=True, exist_ok=True)
    temp_env.write_text(
        "\n".join(
            [
                "RUN_MODE=real",
                "FEISHU_ADAPTER=real",
                "VIDEO_PROVIDER=api",
            ]
        ),
        encoding="utf-8",
    )
    try:
        try:
            load_app_config(temp_env)
        except ConfigError:
            print("smoke_failure_branch: ok")
            return 0
        raise SystemExit("失败分支验证失败：缺失 real 配置时未报错。")
    finally:
        temp_env.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
