from __future__ import annotations

from typing import Any


class ResponseProcessor:
    def process(self, content: str, sanitization_result: Any, request: Any | None = None) -> dict[str, Any]:
        return {
            "request_id": getattr(request, "request_id", None) or "req_001",
            "provider": getattr(request, "model_provider_details", None).provider if request else "huggingface",
            "model": getattr(request, "model_provider_details", None).model if request else "unknown-model",
            "content": content,
            "security": {
                "sanitized": sanitization_result.detection_count > 0,
                "risk_score": sanitization_result.risk_score,
                "detected_categories": sanitization_result.detected_categories,
            },
        }
