from __future__ import annotations


class PlaceholderManager:
    def __init__(self) -> None:
        self.mapping: dict[str, str] = {}
        self._counts: dict[str, int] = {}

    def build_placeholder(self, category: str) -> str:
        count = self._counts.get(category, 0) + 1
        self._counts[category] = count
        return f"<{category}_{count}>"

    def register(self, category: str, value: str) -> str:
        placeholder = self.build_placeholder(category)
        self.mapping[placeholder] = value
        return placeholder
