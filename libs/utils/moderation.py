from __future__ import annotations

import re

_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
_PHONE_RE = re.compile(
    r"(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
)

_OFFENSIVE_KEYWORDS = frozenset([
    "kill yourself", "kys", "die in a fire",
])


def redact_pii(text: str) -> str:
    """Replace emails and phone numbers with redaction markers."""
    result = _EMAIL_RE.sub("[EMAIL]", text)
    result = _PHONE_RE.sub("[PHONE]", result)
    return result


def check_offensive(text: str) -> tuple[bool, str | None]:
    """Check for offensive content. Returns (is_offensive, reason)."""
    lower = text.lower()
    for keyword in _OFFENSIVE_KEYWORDS:
        if keyword in lower:
            return True, f"offensive keyword: {keyword}"
    return False, None
