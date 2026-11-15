from __future__ import annotations

import re
from dataclasses import dataclass, field

from sanitization.detection_rules import PATTERNS
from sanitization.placeholder_manager import PlaceholderManager
from sanitization.risk_evaluator import RiskEvaluator
from sanitization.sensitive_detector import SensitiveDetector


@dataclass
class SanitizationResult:
    sanitized_prompt: str
    detected_categories: list[str]
    detection_count: int
    risk_score: int
    decision: str
    placeholder_mapping: dict[str, str] = field(default_factory=dict)


class Sanitizer:
    def __init__(self, max_prompt_size: int = 20000, risk_evaluator: RiskEvaluator | None = None) -> None:
        self.max_prompt_size = max_prompt_size
        self.risk_evaluator = risk_evaluator or RiskEvaluator()
        self.detector = SensitiveDetector()

    def sanitize(self, prompt: str) -> SanitizationResult:
        if not prompt:
            raise ValueError("Prompt cannot be empty.")
        if len(prompt) > self.max_prompt_size:
            raise ValueError("Prompt exceeds the configured maximum size.")

        findings = self.detector.detect(prompt)
        categories = sorted(findings)

        placeholders = PlaceholderManager()
        sanitized = prompt

        for category in categories:
            for raw_value in findings[category]:
                placeholder = placeholders.register(category, raw_value)
                if category == "PRIVATE_KEY":
                    sanitized = re.sub(PATTERNS["PRIVATE_KEY"], placeholder, sanitized, count=1)
                elif category == "API_KEY":
                    sanitized = re.sub(rf"(?i)(api[_ -]?key\s*[:=]\s*){re.escape(raw_value)}", rf"\1{placeholder}", sanitized, count=1)
                elif category == "PASSWORD":
                    sanitized = re.sub(rf"(?i)(password\s*[:=]\s*){re.escape(raw_value)}", rf"\1{placeholder}", sanitized, count=1)
                elif category == "USER":
                    sanitized = re.sub(rf"(?i)(username\s*[:=]\s*){re.escape(raw_value)}", rf"\1{placeholder}", sanitized, count=1)
                elif category == "EMAIL":
                    sanitized = re.sub(re.escape(raw_value), placeholder, sanitized, count=1)
                elif category == "INTERNAL_IP":
                    sanitized = re.sub(re.escape(raw_value), placeholder, sanitized, count=1)
                elif category == "PHONE":
                    sanitized = re.sub(re.escape(raw_value), placeholder, sanitized, count=1)
                elif category == "CREDIT_CARD":
                    sanitized = re.sub(re.escape(raw_value), placeholder, sanitized, count=1)

        detection_count = sum(len(values) for values in findings.values())
        risk_score = self.risk_evaluator.calculate(categories)
        decision = self.risk_evaluator.decide(categories, risk_score)

        return SanitizationResult(
            sanitized_prompt=sanitized,
            detected_categories=categories,
            detection_count=detection_count,
            risk_score=risk_score,
            decision=decision,
            placeholder_mapping=placeholders.mapping,
        )
