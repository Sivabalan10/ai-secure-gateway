from __future__ import annotations

from sanitization.detection_rules import PATTERNS


class SensitiveDetector:
    def detect(self, prompt: str) -> dict[str, list[str]]:
        findings: dict[str, list[str]] = {}

        for category, pattern in PATTERNS.items():
            matches: list[str] = []
            if category in {"API_KEY", "PASSWORD", "USER"}:
                for group in pattern.findall(prompt):
                    if isinstance(group, tuple):
                        matches.append(group[1])
                    else:
                        matches.append(str(group))
            elif category == "PRIVATE_KEY":
                for match in pattern.findall(prompt):
                    matches.append(match)
            else:
                for match in pattern.findall(prompt):
                    matches.append(match)

            if matches:
                findings[category] = matches

        return findings
