"""发布平台适配器注册占位。"""

from lobster_farm.publishing.adapters.base import PublishAdapter
from lobster_farm.publishing.adapters.douyin import DouyinPublishAdapter
from lobster_farm.publishing.adapters.wechat_channels import WechatChannelsPublishAdapter


__all__ = [
    "PublishAdapter",
    "DouyinPublishAdapter",
    "WechatChannelsPublishAdapter",
]
