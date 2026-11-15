from __future__ import annotations

from typing import Any


class InMemoryAuditRepository:
    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []

    def add(self, entry: dict[str, Any]) -> None:
        self._entries.append(entry)

    def list(self) -> list[dict[str, Any]]:
        return list(self._entries)
