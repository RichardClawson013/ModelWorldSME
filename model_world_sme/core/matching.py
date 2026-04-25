"""
core/matching.py — Narrative to world model task matching.

Fully deterministic. No AI, no API, no internet required.
"""

from __future__ import annotations
import re
from typing import Any

SYNONYMS: dict[str, list[str]] = {
    "invoice":      ["factuur", "billing", "rekening", "nota"],
    "payment":      ["betaling", "betalen", "transfer", "overschrijving"],
    "customer":     ["klant", "client", "opdrachtgever", "afnemer"],
    "supplier":     ["leverancier", "vendor", "inkoop"],
    "employee":     ["personeel", "medewerker", "staff", "werknemer"],
    "quote":        ["offerte", "quotation", "proposal", "aanbieding"],
    "contract":     ["overeenkomst", "agreement"],
    "planning":     ["schedule", "agenda", "rooster"],
    "purchase":     ["inkoop", "bestelling", "order"],
    "sales":        ["verkoop", "omzet"],
    "report":       ["rapport", "rapportage", "verslag", "overzicht"],
    "tax":          ["btw", "vat", "belasting", "aangifte"],
    "absence":      ["verzuim", "sick", "ziek", "verlof"],
    "project":      ["klus", "opdracht", "werk"],
    "budget":       ["begroting", "kosten", "uitgaven"],
    "website":      ["web", "online", "digitaal"],
    "email":        ["mail", "e-mail", "bericht", "correspondentie"],
    "complaint":    ["klacht", "klachten", "bezwaar"],
    "maintenance":  ["onderhoud", "reparatie", "service"],
    "delivery":     ["levering", "bezorging", "transport"],
}


def _expand_synonyms(text: str) -> str:
    lower = text.lower()
    extra: list[str] = []
    for canonical, synonyms in SYNONYMS.items():
        hits = [canonical] + synonyms
        if any(h in lower for h in hits):
            extra.extend(hits)
    return lower + " " + " ".join(extra)


def extract_tasks_from_narrative(
    narrative: str,
    tasks: list[dict[str, Any]],
    top_n: int = 12,
) -> list[dict[str, Any]]:
    """Match free-text narrative against world model tasks.

    Returns up to *top_n* tasks sorted by relevance score (highest first).
    """
    expanded = _expand_synonyms(narrative)
    words = [w for w in re.split(r"\W+", expanded) if len(w) >= 4]

    scores: dict[str, int] = {}

    for task in tasks:
        search_blob = _expand_synonyms(" ".join(filter(None, [
            task.get("name", ""),
            task.get("name_en", ""),
            task.get("description", ""),
            task.get("cause", {}).get("trigger", ""),
            task.get("cause", {}).get("business_need", ""),
            task.get("effect", {}).get("output", ""),
            *task.get("state_inputs", []),
            *task.get("state_outputs", []),
        ])))

        score = sum(1 for w in words if w in search_blob)

        name_prefix = task.get("name", "")[:10].lower()
        if name_prefix and name_prefix in narrative.lower():
            score += 3

        if score > 0:
            scores[task["id"]] = score

    task_map = {t["id"]: t for t in tasks}
    return [
        task_map[tid]
        for tid, _ in sorted(scores.items(), key=lambda x: -x[1])[:top_n]
        if tid in task_map
    ]


def suggest_related_tasks(
    recognized_ids: list[str],
    all_tasks: list[dict[str, Any]],
    max_suggestions: int = 6,
) -> list[dict[str, Any]]:
    """Suggest tasks via causal graph (upstream + downstream of recognized tasks)."""
    task_map = {t["id"]: t for t in all_tasks}
    known = set(recognized_ids)
    scores: dict[str, int] = {}

    for tid in recognized_ids:
        task = task_map.get(tid)
        if not task:
            continue
        related = (
            task.get("cause", {}).get("upstream_tasks", [])
            + task.get("effect", {}).get("downstream_tasks", [])
        )
        for rel_id in related:
            if rel_id not in known:
                scores[rel_id] = scores.get(rel_id, 0) + 1

    return [
        task_map[tid]
        for tid, _ in sorted(scores.items(), key=lambda x: -x[1])[:max_suggestions]
        if tid in task_map
    ]
