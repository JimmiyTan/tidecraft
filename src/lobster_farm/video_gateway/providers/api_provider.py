"""API 视频 provider。"""

import json
import time
from typing import Any

from lobster_farm.common.config import AppConfig
from lobster_farm.video_gateway.providers.base import BaseVideoProvider
from lobster_farm.video_gateway.providers.http_client import (
    VideoHttpClient,
    VideoHttpError,
)
from lobster_farm.video_gateway.schemas import VideoJobRequest, VideoJobResult


class ApiVideoProvider(BaseVideoProvider):
    """真实 API provider，负责提交任务和查询状态。"""

    name = "api"

    def __init__(
        self,
        config: AppConfig,
        http_client: VideoHttpClient | None = None,
        sleep_func=time.sleep,
    ) -> None:
        """保存配置、HTTP 客户端和 sleep 函数。"""
        self.config = config
        self.http_client = http_client or VideoHttpClient(
            base_url=config.video_provider_base_url,
            api_key=config.video_api_key,
            timeout_seconds=config.video_request_timeout_seconds,
        )
        self.sleep_func = sleep_func

    def generate(self, request: VideoJobRequest) -> VideoJobResult:
        """提交视频任务并轮询结果。"""
        request.output_dir.mkdir(parents=True, exist_ok=True)
        validation_error = self._validate_required_config()
        provider_request = self._build_provider_request(request)
        request_file = request.output_dir / "provider_request.json"
        response_file = request.output_dir / "provider_response.json"
        self._write_json(request_file, self._redact_request(provider_request))

        if validation_error:
            payload = {"error": validation_error}
            self._write_json(response_file, payload)
            return self._failed_result(
                request,
                "validation_error",
                validation_error,
                provider_payload=payload,
                request_file=request_file,
                response_file=response_file,
            )

        try:
            submit_payload = self._call_with_retry(
                lambda: self.http_client.post_json(
                    self.config.video_submit_path,
                    provider_request,
                ).payload
            )
            remote_task_id = self._extract_remote_task_id(submit_payload)
            provider_status = self._extract_status(submit_payload, default="submitted")

            latest_payload = submit_payload
            if provider_status not in {"ready", "completed", "succeeded", "success"}:
                latest_payload = self._poll_until_ready(remote_task_id)
                provider_status = self._extract_status(latest_payload, default="unknown")

            self._write_json(response_file, latest_payload)
            if provider_status not in {"ready", "completed", "succeeded", "success"}:
                return self._failed_result(
                    request,
                    "provider_status",
                    f"视频 API 未返回完成状态：{provider_status}",
                    remote_task_id=remote_task_id,
                    provider_status=provider_status,
                    provider_payload=latest_payload,
                    request_file=request_file,
                    response_file=response_file,
                )

            output_file = request.output_dir / "video_result.json"
            video_payload = {
                "task_id": request.task_id,
                "provider": self.name,
                "remote_task_id": remote_task_id,
                "provider_status": provider_status,
                "provider_payload": latest_payload,
            }
            self._write_json(output_file, video_payload)
            return VideoJobResult(
                ok=True,
                task_id=request.task_id,
                status="video_ready",
                output_file=output_file,
                provider=self.name,
                remote_task_id=remote_task_id,
                provider_status=provider_status,
                provider_payload=latest_payload,
                provider_request_file=request_file,
                provider_response_file=response_file,
            )
        except VideoHttpError as exc:
            category = self._classify_error(exc)
            payload = exc.response_payload or {"error": str(exc)}
            self._write_json(response_file, payload)
            return self._failed_result(
                request,
                category,
                str(exc),
                provider_payload=payload,
                request_file=request_file,
                response_file=response_file,
            )
        except (KeyError, TypeError, ValueError) as exc:
            payload = {"error": str(exc)}
            self._write_json(response_file, payload)
            return self._failed_result(
                request,
                "response_parse",
                str(exc),
                provider_payload=payload,
                request_file=request_file,
                response_file=response_file,
            )

    def _validate_required_config(self) -> str:
        """校验 API provider 必填项。"""
        missing = [
            name
            for name, value in {
                "VIDEO_API_KEY": self.config.video_api_key,
                "VIDEO_PROVIDER_BASE_URL": self.config.video_provider_base_url,
                "VIDEO_SUBMIT_PATH": self.config.video_submit_path,
                "VIDEO_STATUS_PATH": self.config.video_status_path,
            }.items()
            if not value
        ]
        return "缺少配置：" + ", ".join(missing) if missing else ""

    def _build_provider_request(self, request: VideoJobRequest) -> dict[str, Any]:
        """构造 provider 请求。"""
        return {
            "task_id": request.task_id,
            "topic": request.topic,
            "review_items": request.review_items,
        }

    def _call_with_retry(self, action):
        """调用动作并按配置重试。"""
        last_error = None
        for _ in range(self.config.video_max_retries + 1):
            try:
                return action()
            except VideoHttpError as exc:
                last_error = exc
        if last_error:
            raise last_error
        raise VideoHttpError("unknown", "视频 API 调用失败")

    def _poll_until_ready(self, remote_task_id: str) -> dict[str, Any]:
        """轮询直到 provider 返回完成状态或达到上限。"""
        latest_payload: dict[str, Any] = {}
        for attempt in range(self.config.video_max_poll_attempts):
            if attempt > 0:
                self.sleep_func(self.config.video_poll_interval_seconds)
            status_path = self.config.video_status_path.format(
                remote_task_id=remote_task_id
            )
            latest_payload = self._call_with_retry(
                lambda: self.http_client.get_json(status_path).payload
            )
            status = self._extract_status(latest_payload, default="unknown")
            if status in {"ready", "completed", "succeeded", "success", "failed", "error"}:
                return latest_payload
        return latest_payload

    def _extract_remote_task_id(self, payload: dict[str, Any]) -> str:
        """从 provider 响应中提取远端任务 ID。"""
        data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
        remote_task_id = (
            payload.get("remote_task_id")
            or payload.get("task_id")
            or data.get("remote_task_id")
            or data.get("task_id")
            or data.get("id")
        )
        if not remote_task_id:
            raise ValueError("视频 API 响应缺少 remote_task_id/task_id/id")
        return str(remote_task_id)

    def _extract_status(self, payload: dict[str, Any], default: str) -> str:
        """从 provider 响应中提取状态。"""
        data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
        status = payload.get("status") or data.get("status") or default
        return str(status)

    def _failed_result(
        self,
        request: VideoJobRequest,
        category: str,
        message: str,
        remote_task_id: str = "",
        provider_status: str = "failed",
        provider_payload: dict[str, Any] | None = None,
        request_file=None,
        response_file=None,
    ) -> VideoJobResult:
        """构造失败结果。"""
        return VideoJobResult(
            ok=False,
            task_id=request.task_id,
            status="failed",
            output_file=None,
            provider=self.name,
            remote_task_id=remote_task_id,
            provider_status=provider_status,
            provider_payload=provider_payload or {},
            error_category=category,
            error_message=message,
            provider_request_file=request_file,
            provider_response_file=response_file,
        )

    def _classify_error(self, error: VideoHttpError) -> str:
        """分类视频 API 错误。"""
        if error.category in {"timeout", "network", "response_parse"}:
            return error.category
        if error.status_code in {401, 403}:
            return "permission"
        if error.status_code == 404:
            return "not_found"
        return error.category

    def _redact_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        """脱敏请求信息。"""
        return {
            "task_id": payload.get("task_id", ""),
            "topic": payload.get("topic", ""),
            "review_items_count": len(payload.get("review_items", [])),
        }

    def _write_json(self, file_path, payload: dict[str, Any]) -> None:
        """写入 JSON 文件。"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
