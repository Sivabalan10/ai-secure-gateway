from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ClientAuthRequest(BaseModel):
    client_id: str = Field(..., min_length=3, max_length=128)
    client_secret: str = Field(..., min_length=8, max_length=256)
    model_config = ConfigDict(extra="forbid")


class SessionResponse(BaseModel):
    session_id: str
    session_token: str
    expires_in: int
    model_config = ConfigDict(extra="forbid")
