"""视频 provider 抽象定义。"""

from abc import ABC, abstractmethod

from lobster_farm.video_gateway.schemas import VideoJobRequest, VideoJobResult


class BaseVideoProvider(ABC):
    """视频 provider 基类。"""

    @abstractmethod
    def generate(self, request: VideoJobRequest) -> VideoJobResult:
        """生成视频占位结果。"""
