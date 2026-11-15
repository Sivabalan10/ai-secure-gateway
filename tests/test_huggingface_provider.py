import pytest

from core.exceptions import ProviderRequestError
from providers.huggingface_provider import HuggingFaceProvider


class DummyResponse:
    def __init__(self, status_code: int, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


class DummyClient:
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url, headers=None, json=None):
        return DummyResponse(200, {"choices": [{"message": {"content": "Response from provider"}}]})


@pytest.mark.asyncio
async def test_huggingface_provider_success(monkeypatch) -> None:
    import httpx

    monkeypatch.setattr(httpx, "AsyncClient", DummyClient)
    provider = HuggingFaceProvider(
        api_key="test-key",
        base_url="https://example.com",
        allowed_models=["google/gemma-2b-it"],
        timeout=10.0,
    )

    result = await provider.generate("Hello there", "google/gemma-2b-it", {"temperature": 0.2, "max_tokens": 100})
    assert result == "Response from provider"


@pytest.mark.asyncio
async def test_huggingface_provider_uses_chat_completions_api(monkeypatch) -> None:
    import httpx

    class ChatCompletionsClient(DummyClient):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.request_url = None
            self.request_json = None

        async def post(self, url, headers=None, json=None):
            self.request_url = url
            self.request_json = json
            return DummyResponse(200, {"choices": [{"message": {"content": "chat reply"}}]})

    fake_client = ChatCompletionsClient()
    monkeypatch.setattr(httpx, "AsyncClient", lambda *args, **kwargs: fake_client)
    provider = HuggingFaceProvider(
        api_key="test-key",
        base_url="https://router.huggingface.co/v1",
        allowed_models=["openai/gpt-oss-120b:fastest"],
        timeout=10.0,
    )

    result = await provider.generate("Hello there", "openai/gpt-oss-120b:fastest", {"temperature": 0.2, "max_tokens": 100})
    assert result == "chat reply"
    assert fake_client.request_url == "https://router.huggingface.co/v1/chat/completions"
    assert fake_client.request_json["messages"] == [{"role": "user", "content": "Hello there"}]


@pytest.mark.asyncio
async def test_huggingface_provider_invalid_response(monkeypatch) -> None:
    import httpx

    class EmptyResponseClient(DummyClient):
        async def post(self, url, headers=None, json=None):
            return DummyResponse(200, {"unexpected": "value"})

    monkeypatch.setattr(httpx, "AsyncClient", EmptyResponseClient)
    provider = HuggingFaceProvider(api_key="test-key", allowed_models=["google/gemma-2b-it"])

    with pytest.raises(ProviderRequestError):
        await provider.generate("Hello there", "google/gemma-2b-it", {"temperature": 0.2, "max_tokens": 100})


@pytest.mark.asyncio
async def test_huggingface_provider_connection_error(monkeypatch) -> None:
    import httpx

    class FailingClient(DummyClient):
        async def post(self, url, headers=None, json=None):
            raise httpx.ConnectError("DNS lookup failed")

    monkeypatch.setattr(httpx, "AsyncClient", FailingClient)
    provider = HuggingFaceProvider(api_key="test-key", allowed_models=["google/gemma-2b-it"])

    with pytest.raises(ProviderRequestError):
        await provider.generate("Hello there", "google/gemma-2b-it", {"temperature": 0.2, "max_tokens": 100})
