from __future__ import annotations

from abc import ABC, abstractmethod


class BaseProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, model: str, options: dict) -> str:
        """Generate a response from the selected LLM."""
