from types import SimpleNamespace

import pytest

from core.exceptions import PromptSecurityError
from core.gateway import SecureAIGateway
from sanitization.sanitizer import Sanitizer


class StubProvider:
    async def generate(self, prompt: str, model: str, options: dict) -> str:
        assert "10.10.20.30" not in prompt
        assert "SECRET123" not in prompt
        return "safe response"


class StubFactory:
    def get_provider(self, provider_name: str):
        assert provider_name == "huggingface"
        return StubProvider()


class StubProcessor:
    def process(self, content: str, result, request):
        return {
            "request_id": "req_001",
            "provider": request.model_provider_details.provider,
            "model": request.model_provider_details.model,
            "content": content,
            "security": {
                "sanitized": result.detection_count > 0,
                "risk_score": result.risk_score,
                "detected_categories": result.detected_categories,
            },
        }


@pytest.mark.asyncio
async def test_gateway_approves_sanitized_prompt() -> None:
    gateway = SecureAIGateway(
        sanitizer=Sanitizer(),
        provider_factory=StubFactory(),
        response_processor=StubProcessor(),
    )

    request = SimpleNamespace(
        prompt="Server IP is 10.10.20.30 and password=SECRET123.",
        model_provider_details=SimpleNamespace(provider="huggingface", model="google/gemma-2b-it"),
        options={"temperature": 0.2, "max_tokens": 100},
        request_id="req_001",
    )

    result = await gateway.process_request(request)
    assert result["content"] == "safe response"
    assert result["security"]["sanitized"] is True


@pytest.mark.asyncio
async def test_gateway_rejects_private_key_prompt() -> None:
    gateway = SecureAIGateway(
        sanitizer=Sanitizer(),
        provider_factory=StubFactory(),
        response_processor=StubProcessor(),
    )

    request = SimpleNamespace(
        prompt="-----BEGIN PRIVATE KEY-----\nabc\n-----END PRIVATE KEY-----",
        model_provider_details=SimpleNamespace(provider="huggingface", model="google/gemma-2b-it"),
        options={"temperature": 0.2, "max_tokens": 100},
        request_id="req_002",
    )

    with pytest.raises(PromptSecurityError):
        await gateway.process_request(request)
