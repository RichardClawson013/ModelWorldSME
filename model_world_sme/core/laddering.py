"""
core/laddering.py — Laddering technique + Exception probing.

Based on:
  Kelly, G.A. (1955). The Psychology of Personal Constructs.
  Beyer, H. & Holtzblatt, K. (1997). Contextual Design.
"""

LADDERING_TEMPLATES: list[str] = [
    "How do you know that {task} is done correctly?",
    "What goes wrong when {task} is not done or is delayed?",
    "When do you handle {task} differently from usual?",
]


def get_laddering_question(task_name: str, depth: int) -> str | None:
    """Return laddering question for *task_name* at *depth* (0-2), or None."""
    if 0 <= depth < len(LADDERING_TEMPLATES):
        return LADDERING_TEMPLATES[depth].format(task=task_name)
    return None


def get_exception_question(task_name: str) -> str:
    """Return exception probing question for *task_name*."""
    return (
        f"Can you describe a situation where {task_name} went wrong "
        f"or where you made an exception?"
    )
