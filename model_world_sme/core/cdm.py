"""
core/cdm.py — Critical Decision Method probes.

Based on: Klein, G. (1989). Recognition-primed decisions.
"""

CDM_PROBES: list[str] = [
    "What was the first sign that something needed your attention?",
    "How did you decide what to tackle first?",
    "What would someone new to your business have done wrong in that situation?",
    "Was there a moment of doubt? How did you decide then?",
]


def get_cdm_probe(index: int) -> str | None:
    """Return CDM follow-up probe by index, or None if out of range."""
    if 0 <= index < len(CDM_PROBES):
        return CDM_PROBES[index]
    return None
