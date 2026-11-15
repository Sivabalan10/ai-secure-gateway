from __future__ import annotations

from sanitization.detection_rules import SENSITIVITY_WEIGHTS


class RiskEvaluator:
    def __init__(self, weights: dict[str, int] | None = None) -> None:
        self.weights = weights or SENSITIVITY_WEIGHTS

    def calculate(self, categories: list[str]) -> int:
        categories = [str(category) for category in categories]
        return sum(self.weights.get(category, 0) for category in categories)

    def decide(self, categories: list[str], risk_score: int) -> str:
        if "PRIVATE_KEY" in categories or risk_score >= 60:
            return "REJECT"
        if 30 <= risk_score < 60:
            return "APPROVE_WITH_SANITIZATION"
        return "APPROVE"
