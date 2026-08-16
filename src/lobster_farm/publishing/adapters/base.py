"""发布适配器抽象接口。"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class PublishRequest:
    """未来真实发布接口的统一入参。"""

    task_id: str
    platform: str
    title: str
    caption: str
    hashtags: list[str]
    asset_paths: list[str]
    dry_run: bool = True


@dataclass
class PublishAdapterResult:
    """发布适配器统一返回结构。"""

    task_id: str
    platform: str
    accepted: bool
    message: str
    remote_id: str = ""


class PublishAdapter(ABC):
    """所有发布适配器必须实现的接口。"""

    @abstractmethod
    def submit(self, request: PublishRequest) -> PublishAdapterResult:
        """提交发布请求；phase-07 不允许真实调用平台接口。"""
