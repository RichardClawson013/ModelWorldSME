"""
core/autonomy.py — Autonomy level mapping for agent tasks.
"""

from __future__ import annotations
import re

AUTONOMY_LEVELS = {
    "autonomous":  "Agent acts without asking",
    "notify":      "Agent acts, then informs you",
    "ask_first":   "Agent asks permission before acting",
    "human_only":  "Always handled by you personally",
}

_AUTONOMOUS_SIGNALS  = ["independently", "on its own", "always", "fine", "go ahead"]
_NOTIFY_SIGNALS      = ["inform", "let me know", "after", "report"]
_ASK_FIRST_SIGNALS   = ["ask", "first", "check", "permission", "approve"]
_HUMAN_ONLY_SIGNALS  = ["never", "always me", "myself", "i do"]


def parse_autonomy_answer(answer: str) -> str:
    """Classify a free-text autonomy answer into one of the four autonomy levels."""
    lower = answer.lower()
    if any(s in lower for s in _AUTONOMOUS_SIGNALS):
        return "autonomous"
    if any(s in lower for s in _NOTIFY_SIGNALS):
        return "notify"
    if any(s in lower for s in _HUMAN_ONLY_SIGNALS):
        return "human_only"
    if any(s in lower for s in _ASK_FIRST_SIGNALS):
        return "ask_first"
    return "ask_first"  # safe default


def parse_threshold(answer: str) -> float | None:
    """Extract a monetary threshold from free text, e.g. 'above 500 euros'."""
    match = re.search(r"[$€£]?\s*([\d,]+(?:\.\d+)?)\s*(?:euro|eur|dollar|usd|gbp)?", answer, re.I)
    if match:
        raw = match.group(1).replace(",", "")
        try:
            return float(raw)
        except ValueError:
            pass
    return None
