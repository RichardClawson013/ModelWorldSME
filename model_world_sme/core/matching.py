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

# Domains that apply to most SME businesses.
# Boosted unless the narrative contains logistics-specific signals.
_CORE_SME_DOMAINS = {"D-FIN", "D-SAL", "D-KLA", "D-OPS", "D-HRM", "D-STR", "D-MKT"}

# Signals that indicate a logistics/delivery business specifically.
_LOGISTICS_SIGNALS = {
    "shipping", "freight", "warehouse", "customs", "tariff", "cargo",
    "shipment", "logistics", "dispatch", "fleet", "driver", "route",
    "transport", "levering", "bezorging", "vracht", "douane",
}

# Signals that indicate an IT/legal business specifically.
_ICT_SIGNALS    = {"server", "network", "software", "database", "cloud", "it department"}
_LEGAL_SIGNALS  = {"compliance officer", "legal counsel", "regulatory", "litigation"}

# Domain score boost for core SME domains (applied when no conflicting signal).
_DOMAIN_BOOST = 2


def _narrative_domain_hints(narrative: str) -> set[str]:
    """Return which specialist domains are signalled by the narrative."""
    lower = narrative.lower()
    hints: set[str] = set()
    if any(s in lower for s in _LOGISTICS_SIGNALS):
        hints.add("D-DEL")
    if any(s in lower for s in _ICT_SIGNALS):
        hints.add("D-ICT")
    if any(s in lower for s in _LEGAL_SIGNALS):
        hints.add("D-LEG")
    return hints


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

    Applies a domain relevance boost so that generic SME business language
    (invoices, quotes, crew, clients) matches Finance/Sales/Ops tasks rather
    than logistics or customs tasks that happen to mention the same words in
    an unrelated context.

    Returns up to *top_n* tasks sorted by relevance score (highest first).
    """
    expanded = _expand_synonyms(narrative)
    words = [w for w in re.split(r"\W+", expanded) if len(w) >= 4]

    # Determine which specialist domains the narrative actually signals.
    specialist_domains = _narrative_domain_hints(narrative)
    boost_core = not specialist_domains  # boost core SME domains when no specialist signal

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

        # Exact prefix match on Dutch name — strongest signal.
        name_prefix = task.get("name", "")[:10].lower()
        if name_prefix and name_prefix in narrative.lower():
            score += 3

        # Domain relevance boost.
        domain = task.get("domain", "")
        if boost_core and domain in _CORE_SME_DOMAINS:
            score += _DOMAIN_BOOST
        elif specialist_domains and domain in specialist_domains:
            score += _DOMAIN_BOOST

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
