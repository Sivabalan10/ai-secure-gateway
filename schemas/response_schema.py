from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class APIError(BaseModel):
    code: str
    message: str
    details: dict[str, Any] | None = None
    model_config = ConfigDict(extra="forbid")


class StandardResponse(BaseModel):
    success: bool
    data: dict[str, Any] | None = None
    error: APIError | None = None
    model_config = ConfigDict(extra="forbid")


class StandardResponseEnvelope(StandardResponse):
    pass
