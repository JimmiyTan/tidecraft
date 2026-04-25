"""mock 视频 provider。"""

import json
from datetime import datetime

from lobster_farm.video_gateway.providers.base import BaseVideoProvider
from lobster_farm.video_gateway.schemas import VideoJobRequest, VideoJobResult


class MockVideoProvider(BaseVideoProvider):
    """生成本地 JSON 文件作为视频结果占位。"""

    name = "mock"

    def generate(self, request: VideoJobRequest) -> VideoJobResult:
        """生成 mock 视频结果文件。"""
        try:
            request.output_dir.mkdir(parents=True, exist_ok=True)
            request_file = request.output_dir / "provider_request.json"
            response_file = request.output_dir / "provider_response.json"
            output_file = request.output_dir / "video_result.json"
            request_payload = {
                "task_id": request.task_id,
                "topic": request.topic,
                "review_items_count": len(request.review_items),
            }
            payload = {
                "task_id": request.task_id,
                "status": "pending_review",
                "provider": self.name,
                "remote_task_id": f"mock_{request.task_id}",
                "provider_status": "ready",
                "topic": request.topic,
                "review_items": request.review_items,
                "generated_at": datetime.now().isoformat(),
            }
            request_file.write_text(
                json.dumps(request_payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            response_file.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            output_file.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            return VideoJobResult(
                ok=True,
                task_id=request.task_id,
                status="video_ready",
                output_file=output_file,
                provider=self.name,
                remote_task_id=payload["remote_task_id"],
                provider_status="ready",
                provider_payload=payload,
                provider_request_file=request_file,
                provider_response_file=response_file,
            )
        except OSError as exc:
            return VideoJobResult(
                ok=False,
                task_id=request.task_id,
                status="failed",
                output_file=None,
                provider=self.name,
                error_category="filesystem",
                error_message=str(exc),
            )
