"""
core/laddering.py — Laddering + Exception Probing.

Based on:
  Kelly, G.A. (1955). The Psychology of Personal Constructs.
  Beyer, H. & Holtzblatt, K. (1997). Contextual Design.

Real laddering follows the person's own words at every depth.
The chain is: practice → consequence → value.
Each question must reference the previous answer — not the task name from a model.
Exception probing surfaces real failure conditions from lived experience.
"""

from __future__ import annotations
import re


def _key_phrase(text: str, max_words: int = 8) -> str:
    """Pull the most meaningful short phrase from an answer for follow-up use."""
    text = text.strip()
    clause = re.split(r"[,;.!?\n]", text)[0].strip()
    words = clause.split()
    if words and words[0].lower() in {"i", "we", "so", "well", "it", "that", "because", "yeah", "the"}:
        words = words[1:]
    result = " ".join(words[:max_words])
    return result.lower() if result else "that"


def make_laddering_question(
    task_name: str,
    depth: int,
    prev_answer: str | None = None,
) -> str | None:
    """
    Return a laddering question at *depth* (0–2).

    At depth 0, asks what the task looks like in practice.
    At depths 1 and 2, *prev_answer* is used to make the question reference
    what the person actually said — not a pre-written template with a task name.

    Returns None if depth > 2.

    Depth mapping:
      0 — practice:    "What does this actually look like?"
      1 — consequence: "Why does getting that right matter?"  (uses their words)
      2 — value:       "What's at stake if it slips?"         (uses their words)
    """
    if depth == 0:
        return f"Let's talk about {task_name}. When that goes well, what does it actually look like in practice?"
    if depth == 1:
        phrase = _key_phrase(prev_answer) if prev_answer else task_name
        return f"You said {phrase}. Why does getting that right matter to you?"
    if depth == 2:
        phrase = _key_phrase(prev_answer) if prev_answer else "that"
        return f"And why does {phrase} matter — what's actually at stake if it slips?"
    return None


def make_exception_question(
    task_name: str,
    laddering_answer: str | None = None,
) -> str:
    """
    Return an exception probing question that references what was said during
    laddering, so it surfaces failure conditions from experience rather than
    asking about a generic scenario.
    """
    if laddering_answer:
        phrase = _key_phrase(laddering_answer)
        return (
            f"You said {phrase} is what matters. "
            f"Tell me about a time {task_name} didn't go that way — "
            f"when it went wrong, or when you had to handle it completely differently than usual."
        )
    return (
        f"Tell me about a time {task_name} went wrong, "
        f"or a situation where you had to handle it completely differently than usual."
    )
