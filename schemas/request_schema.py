from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ProviderDetails(BaseModel):
    provider: str = Field(..., min_length=2, max_length=64)
    model: str = Field(..., min_length=2, max_length=256)
    model_config = ConfigDict(extra="forbid", protected_namespaces=())


class InferenceRequestOptions(BaseModel):
    temperature: float = Field(default=0.2, ge=0.0, le=1.0)
    max_tokens: int = Field(default=500, gt=0, le=1000)
    model_config = ConfigDict(extra="forbid")


class InferenceRequest(BaseModel):
    model_provider_details: ProviderDetails
    prompt: str = Field(..., min_length=1, max_length=20000)
    options: InferenceRequestOptions = Field(default_factory=InferenceRequestOptions)
    request_id: str | None = Field(default=None, max_length=128)
    model_config = ConfigDict(extra="forbid", protected_namespaces=())
