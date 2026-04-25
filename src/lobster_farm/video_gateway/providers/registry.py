"""视频 provider 注册机制。"""

from lobster_farm.common.config import AppConfig
from lobster_farm.video_gateway.providers.api_provider import ApiVideoProvider
from lobster_farm.video_gateway.providers.base import BaseVideoProvider
from lobster_farm.video_gateway.providers.mock_provider import MockVideoProvider


def get_video_provider(config: AppConfig) -> BaseVideoProvider:
    """按配置返回视频 provider。"""
    providers: dict[str, BaseVideoProvider] = {
        "mock": MockVideoProvider(),
        "api": ApiVideoProvider(config),
    }
    return providers[config.video_provider]
