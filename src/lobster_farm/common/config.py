"""统一配置加载与校验工具。"""

from dataclasses import dataclass
import os
from pathlib import Path

from lobster_farm.common.paths import get_project_root, resolve_project_path


class ConfigError(ValueError):
    """配置错误。"""


@dataclass
class AppConfig:
    """应用统一配置。"""

    app_env: str
    app_name: str
    app_timezone: str
    run_mode: str
    workspace_root: Path
    data_dir: Path
    log_dir: Path
    export_dir: Path
    asset_dir: Path
    feishu_enabled: bool
    feishu_adapter: str
    feishu_api_base_url: str
    feishu_app_id: str
    feishu_app_secret: str
    feishu_bot_name: str
    feishu_default_chat_id: str
    feishu_request_timeout_seconds: int
    feishu_max_retries: int
    video_provider: str
    video_api_key: str
    video_provider_base_url: str
    video_submit_path: str
    video_status_path: str
    video_output_dir: Path
    video_request_timeout_seconds: int
    video_max_retries: int
    video_poll_interval_seconds: int
    video_max_poll_attempts: int
    orchestrator_state_file: Path
    orchestrator_queue_dir: Path
    orchestrator_task_state_dir: Path
    orchestrator_task_index_file: Path
    orchestrator_max_retries: int
    log_level: str


def _parse_env_file(file_path: Path) -> dict[str, str]:
    """解析简单的 KEY=VALUE 文件。"""
    values: dict[str, str] = {}
    if not file_path.exists():
        return values
    for raw_line in file_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip().lstrip("\ufeff")] = value.strip()
    return values


def _to_bool(value: str, default: bool = False) -> bool:
    """解析布尔值。"""
    if value == "":
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def _to_int(value: str, default: int) -> int:
    """解析整数。"""
    if value == "":
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise ConfigError(f"配置项必须是整数：{value}") from exc


def load_raw_config(env_file: Path | None = None) -> dict[str, str]:
    """读取 .env.example 并用 .env 覆盖默认值。"""
    project_root = get_project_root()
    example_values = _parse_env_file(project_root / ".env.example")
    # 验证脚本可通过项目内临时 env 文件运行，避免误触真实外部服务。
    override_env_file = os.environ.get("LOBSTER_ENV_FILE", "")
    local_env_path = env_file or (
        resolve_project_path(override_env_file)
        if override_env_file
        else project_root / ".env"
    )
    local_values = _parse_env_file(local_env_path)
    return {**example_values, **local_values}


def load_app_config(env_file: Path | None = None) -> AppConfig:
    """加载并校验应用配置。"""
    raw = load_raw_config(env_file)
    config = AppConfig(
        app_env=raw.get("APP_ENV", "dev"),
        app_name=raw.get("APP_NAME", "lobster-farm"),
        app_timezone=raw.get("APP_TIMEZONE", "Asia/Shanghai"),
        run_mode=raw.get("RUN_MODE", "dry-run"),
        workspace_root=resolve_project_path(raw.get("WORKSPACE_ROOT", "./")),
        data_dir=resolve_project_path(raw.get("DATA_DIR", "./data")),
        log_dir=resolve_project_path(raw.get("LOG_DIR", "./logs")),
        export_dir=resolve_project_path(raw.get("EXPORT_DIR", "./exports")),
        asset_dir=resolve_project_path(raw.get("ASSET_DIR", "./assets")),
        feishu_enabled=_to_bool(raw.get("FEISHU_ENABLED", "false")),
        feishu_adapter=raw.get("FEISHU_ADAPTER", "dry-run"),
        feishu_api_base_url=raw.get("FEISHU_API_BASE_URL", "https://open.feishu.cn"),
        feishu_app_id=raw.get("FEISHU_APP_ID", ""),
        feishu_app_secret=raw.get("FEISHU_APP_SECRET", ""),
        feishu_bot_name=raw.get("FEISHU_BOT_NAME", "lobster-bot"),
        feishu_default_chat_id=raw.get("FEISHU_DEFAULT_CHAT_ID", ""),
        feishu_request_timeout_seconds=_to_int(
            raw.get("FEISHU_REQUEST_TIMEOUT_SECONDS", "10"), 10
        ),
        feishu_max_retries=_to_int(raw.get("FEISHU_MAX_RETRIES", "2"), 2),
        video_provider=raw.get("VIDEO_PROVIDER", "mock"),
        video_api_key=raw.get("VIDEO_API_KEY", ""),
        video_provider_base_url=raw.get("VIDEO_PROVIDER_BASE_URL", ""),
        video_submit_path=raw.get("VIDEO_SUBMIT_PATH", "/submit"),
        video_status_path=raw.get("VIDEO_STATUS_PATH", "/status/{remote_task_id}"),
        video_output_dir=resolve_project_path(
            raw.get("VIDEO_OUTPUT_DIR", "./exports/pending_review")
        ),
        video_request_timeout_seconds=_to_int(
            raw.get("VIDEO_REQUEST_TIMEOUT_SECONDS", "30"), 30
        ),
        video_max_retries=_to_int(raw.get("VIDEO_MAX_RETRIES", "2"), 2),
        video_poll_interval_seconds=_to_int(
            raw.get("VIDEO_POLL_INTERVAL_SECONDS", "5"), 5
        ),
        video_max_poll_attempts=_to_int(
            raw.get("VIDEO_MAX_POLL_ATTEMPTS", "12"), 12
        ),
        orchestrator_state_file=resolve_project_path(
            raw.get("ORCHESTRATOR_STATE_FILE", "./data/state/workflow_state.json")
        ),
        orchestrator_queue_dir=resolve_project_path(
            raw.get("ORCHESTRATOR_QUEUE_DIR", "./data/queue")
        ),
        orchestrator_task_state_dir=resolve_project_path(
            raw.get("ORCHESTRATOR_TASK_STATE_DIR", "./data/state/tasks")
        ),
        orchestrator_task_index_file=resolve_project_path(
            raw.get("ORCHESTRATOR_TASK_INDEX_FILE", "./data/state/task_index.json")
        ),
        orchestrator_max_retries=_to_int(raw.get("ORCHESTRATOR_MAX_RETRIES", "1"), 1),
        log_level=raw.get("LOG_LEVEL", "INFO"),
    )
    validate_config(config)
    return config


def validate_config(config: AppConfig) -> None:
    """校验运行模式和真实服务必填项。"""
    valid_modes = {"dev", "dry-run", "real"}
    if config.run_mode not in valid_modes:
        raise ConfigError(f"RUN_MODE 只能是 dev、dry-run 或 real：{config.run_mode}")

    valid_feishu_adapters = {"dry-run", "real"}
    if config.feishu_adapter not in valid_feishu_adapters:
        raise ConfigError(f"FEISHU_ADAPTER 不支持：{config.feishu_adapter}")

    valid_video_providers = {"mock", "api"}
    if config.video_provider not in valid_video_providers:
        raise ConfigError(f"VIDEO_PROVIDER 不支持：{config.video_provider}")

    if config.run_mode != "real" and config.feishu_adapter == "real":
        raise ConfigError("只有 RUN_MODE=real 时才允许 FEISHU_ADAPTER=real")

    if config.run_mode != "real" and config.video_provider == "api":
        raise ConfigError("只有 RUN_MODE=real 时才允许 VIDEO_PROVIDER=api")

    if config.run_mode == "real":
        if config.feishu_adapter == "real":
            missing = [
                name
                for name, value in {
                    "FEISHU_API_BASE_URL": config.feishu_api_base_url,
                    "FEISHU_APP_ID": config.feishu_app_id,
                    "FEISHU_APP_SECRET": config.feishu_app_secret,
                    "FEISHU_DEFAULT_CHAT_ID": config.feishu_default_chat_id,
                }.items()
                if not value
            ]
            if missing:
                raise ConfigError("real 飞书模式缺少配置：" + ", ".join(missing))
        if config.video_provider == "api":
            missing = [
                name
                for name, value in {
                    "VIDEO_API_KEY": config.video_api_key,
                    "VIDEO_PROVIDER_BASE_URL": config.video_provider_base_url,
                    "VIDEO_SUBMIT_PATH": config.video_submit_path,
                    "VIDEO_STATUS_PATH": config.video_status_path,
                }.items()
                if not value
            ]
            if missing:
                raise ConfigError("api 视频模式缺少配置：" + ", ".join(missing))
