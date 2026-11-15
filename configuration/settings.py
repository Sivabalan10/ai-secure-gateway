import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def resolve_env_file() -> str:
    project_root = Path(__file__).resolve().parents[1]
    workspace_root = project_root.parent
    for candidate in (project_root / ".env", workspace_root / ".env"):
        if candidate.exists():
            return str(candidate)
    return str(project_root / ".env")


class Settings(BaseSettings):
    app_name: str = "secure-ai-gateway"
    environment: str = "development"
    debug: bool = False
    api_prefix: str = "/api/v1"
    session_ttl_seconds: int = 1800
    max_prompt_size: int = 20000
    client_credentials: dict[str, str] = Field(default_factory=dict)
    hf_api_key: str = ""
    hf_allowed_models: list[str] = [
        "openai/gpt-oss-120b:fastest",
        "meta-llama/Llama-3.2-3B-Instruct:fastest",
    ]
    provider_timeout_seconds: float = 30.0
    huggingface_base_url: str = "https://router.huggingface.co/v1"

    model_config = SettingsConfigDict(
        env_file=resolve_env_file(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("client_credentials", mode="before")
    @classmethod
    def parse_client_credentials(cls, value: Any) -> dict[str, str]:
        if isinstance(value, dict):
            return value
        if value in (None, ""):
            return {}
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, dict):
                    return {str(key): str(val) for key, val in parsed.items()}
            except json.JSONDecodeError:
                return {}
        return {}

    @field_validator("hf_allowed_models", mode="before")
    @classmethod
    def parse_allowed_models(cls, value: Any) -> list[str]:
        if isinstance(value, list):
            return [str(item) for item in value]
        if value in (None, ""):
            return []
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return [str(item) for item in parsed]
            except json.JSONDecodeError:
                return []
        return []


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
