from __future__ import annotations

from typing import Any

from core.exceptions import PromptSecurityError


class SecureAIGateway:
    def __init__(self, sanitizer: Any, provider_factory: Any, response_processor: Any) -> None:
        self.sanitizer = sanitizer
        self.provider_factory = provider_factory
        self.response_processor = response_processor

    async def process_request(self, request: Any) -> dict[str, Any]:
        result = self.sanitizer.sanitize(request.prompt)
        if result.decision == "REJECT":
            raise PromptSecurityError(
                "The prompt contains sensitive information that violates the configured security policy."
            )

        provider = self.provider_factory.get_provider(request.model_provider_details.provider)
        content = await provider.generate(
            prompt=result.sanitized_prompt,
            model=request.model_provider_details.model,
            options=request.options.model_dump() if hasattr(request.options, "model_dump") else dict(request.options),
        )
        return self.response_processor.process(content, result, request)
