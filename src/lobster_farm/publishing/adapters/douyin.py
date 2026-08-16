"""抖音发布适配器设计稿。"""

from lobster_farm.publishing.adapters.base import (
    PublishAdapter,
    PublishAdapterResult,
    PublishRequest,
)


class DouyinPublishAdapter(PublishAdapter):
    """面向未来官方发布接口的占位适配器。"""

    def submit(self, request: PublishRequest) -> PublishAdapterResult:
        """仅返回占位结果，不调用抖音真实发布接口。"""
        return PublishAdapterResult(
            task_id=request.task_id,
            platform="douyin",
            accepted=False,
            message="phase-07 仅提供抖音发布适配器设计稿，不执行真实发布。",
        )
