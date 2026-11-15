from __future__ import annotations

import re


SENSITIVITY_WEIGHTS = {
    "INTERNAL_IP": 10,
    "EMAIL": 10,
    "USERNAME": 10,
    "PHONE_NUMBER": 15,
    "PASSWORD": 40,
    "API_KEY": 50,
    "PRIVATE_KEY": 100,
    "CREDIT_CARD": 60,
}

PATTERNS = {
    "INTERNAL_IP": re.compile(
        r"\b(?:10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2})\b"
    ),
    "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "API_KEY": re.compile(r"(?i)(api[_ -]?key\s*[:=]\s*)([A-Za-z0-9_\-]{8,})"),
    "PASSWORD": re.compile(r"(?i)(password\s*[:=]\s*)([A-Za-z0-9!@#$%^&*()_+=\-./?]{3,})"),
    "USER": re.compile(r"(?i)(username\s*[:=]\s*)([A-Za-z0-9_.-]{3,})"),
    "PHONE": re.compile(r"(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}"),
    "PRIVATE_KEY": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.DOTALL),
    "CREDIT_CARD": re.compile(r"\b(?:\d[ -]?){13,19}\b"),
}
