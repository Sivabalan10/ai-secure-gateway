from __future__ import annotations

from connection.connection_manager import ConnectionManager
from core.exceptions import UnsupportedProviderError
from providers.base_provider import BaseProvider
from providers.huggingface_provider import HuggingFaceProvider


class ProviderFactory:
    def __init__(self, settings: object, connection_manager: ConnectionManager | None = None) -> None:
        self.settings = settings
        self.connection_manager = connection_manager

    def get_provider(self, provider_name: str) -> BaseProvider:
        provider_name = (provider_name or "").lower()
        if provider_name == "huggingface":
            return HuggingFaceProvider(
                api_key=getattr(self.settings, "hf_api_key", ""),
                base_url=getattr(self.settings, "huggingface_base_url", "https://router.huggingface.co/v1"),
                allowed_models=getattr(self.settings, "hf_allowed_models", []),
                timeout=getattr(self.settings, "provider_timeout_seconds", 30.0),
            )
        raise UnsupportedProviderError("The requested provider is not supported.")
