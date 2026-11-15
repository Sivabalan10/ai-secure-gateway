from __future__ import annotations

from typing import Any

import httpx

from core.exceptions import ProviderRequestError, UnsupportedProviderError
from providers.base_provider import BaseProvider


class HuggingFaceProvider(BaseProvider):
    def __init__(
        self,
        api_key: str = "",
        base_url: str = "https://router.huggingface.co/v1",
        allowed_models: list[str] | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.allowed_models = allowed_models or []
        self.timeout = timeout

    def _validate_model(self, model: str) -> None:
        if not self.allowed_models:
            return
        normalized_model = model.split(":", 1)[0]
        if normalized_model not in {entry.split(":", 1)[0] for entry in self.allowed_models}:
            raise UnsupportedProviderError(f"Unsupported model: {model}")

    async def generate(self, prompt: str, model: str, options: dict[str, Any]) -> str:
        if not prompt or not prompt.strip():
            raise ProviderRequestError("Prompt cannot be empty.")

        self._validate_model(model)

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": float(options.get("temperature", 0.2)),
            "max_tokens": int(options.get("max_tokens", 500)),
            "stream": False,
        }

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
            except httpx.TimeoutException as exc:
                raise ProviderRequestError("The external AI provider did not respond within the configured timeout.") from exc
            except httpx.RequestError as exc:
                raise ProviderRequestError("The external AI provider could not process the request.") from exc

            if response.status_code >= 400:
                raise ProviderRequestError("The external AI provider could not process the request.")

            try:
                data = response.json()
            except ValueError as exc:
                raise ProviderRequestError("The external AI provider returned an invalid response format.") from exc

        choices = data.get("choices") if isinstance(data, dict) else None
        if isinstance(choices, list) and choices:
            first_choice = choices[0]
            if isinstance(first_choice, dict):
                message = first_choice.get("message")
                if isinstance(message, dict) and isinstance(message.get("content"), str):
                    return message["content"]
                if isinstance(message, dict) and isinstance(message.get("content"), list):
                    text_parts = []
                    for item in message["content"]:
                        if isinstance(item, dict) and isinstance(item.get("text"), str):
                            text_parts.append(item["text"])
                    if text_parts:
                        return "".join(text_parts)

        if isinstance(data, dict):
            if "choices" in data and not data["choices"]:
                raise ProviderRequestError("The external AI provider returned an empty response.")
            if "output_text" in data:
                return str(data["output_text"])
            if "generated_text" in data:
                return str(data["generated_text"])

        raise ProviderRequestError("The external AI provider returned an invalid response format.")
