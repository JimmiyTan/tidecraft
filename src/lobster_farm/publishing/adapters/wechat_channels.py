"""视频号发布适配器设计稿。"""

from lobster_farm.publishing.adapters.base import (
    PublishAdapter,
    PublishAdapterResult,
    PublishRequest,
)


class WechatChannelsPublishAdapter(PublishAdapter):
    """面向人工同步发布包的占位适配器。"""

    def submit(self, request: PublishRequest) -> PublishAdapterResult:
        """仅返回占位结果，不调用视频号真实发布接口。"""
        return PublishAdapterResult(
            task_id=request.task_id,
            platform="wechat_channels",
            accepted=False,
            message="phase-07 仅提供视频号人工同步适配器设计稿，不执行真实发布。",
        )
