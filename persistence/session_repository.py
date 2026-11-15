from __future__ import annotations

from typing import Any


class InMemorySessionRepository:
    def __init__(self) -> None:
        self._sessions: dict[str, dict[str, Any]] = {}

    def add(self, session_id: str, payload: dict[str, Any]) -> None:
        self._sessions[session_id] = payload

    def get(self, session_id: str) -> dict[str, Any] | None:
        return self._sessions.get(session_id)

    def list(self) -> list[dict[str, Any]]:
        return list(self._sessions.values())
