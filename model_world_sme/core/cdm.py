"""
core/cdm.py — Critical Decision Method probes.

Based on: Klein, G. (1989). Recognition-primed decisions.

CDM is incident-based cognitive task analysis. Every probe must reference
what was actually described — generic probes defeat the purpose of the method.
The probe sequence follows Klein's structure: timeline → cues → expertise →
counterfactual → resolution.
"""

from __future__ import annotations
import re


def _first_phrase(text: str, max_words: int = 7) -> str:
    """Extract a short usable phrase from narrative for probe interpolation."""
    text = text.strip()
    clause = re.split(r"[,;.!?\n]", text)[0].strip()
    words = clause.split()
    if words and words[0].lower() in {"i", "we", "so", "well", "it", "that", "on", "there", "yeah", "the"}:
        words = words[1:]
    result = " ".join(words[:max_words])
    return result.lower() if result else "that situation"


def make_cdm_probes(incident: str) -> list[str]:
    """
    Generate 5 CDM probes contextualised to the specific incident narrative.

    Each probe references what was described so the follow-up feels like a
    real conversation, not a questionnaire. The sequence:
      1. Timeline reconstruction — walk through the incident chronologically
      2. Cue recognition — what told you this needed attention?
      3. Expertise / tacit knowledge — what would a novice have missed?
      4. Counterfactual — what would have made it worse?
      5. Resolution + reflection — how did it end, what would you change?
    """
    phrase = _first_phrase(incident)
    return [
        f"Walk me through {phrase} step by step — from when you first noticed something was off to how it ended.",
        "At that moment, what was the first sign that told you this needed your attention?",
        "What did you need to know or decide that someone without your experience wouldn't have handled the same way?",
        "If you hadn't been there — or if things had gone slightly differently — what would have gone wrong?",
        "How did it end up, and if it happened again tomorrow, what would you do differently?",
    ]
