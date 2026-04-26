"""
core/export.py — Export personalized world model to JSON, YAML, and SOUL.md.
"""

from __future__ import annotations
import json
import re
from datetime import date
from typing import Any


def _clean_name(name: str) -> str:
    """Strip disambiguation suffixes like ' (2)' from task names."""
    return re.sub(r"\s*\(\d+\)\s*$", "", name).strip()

DOMAIN_LABELS: dict[str, str] = {
    "D-FIN": "Finance & Administration",
    "D-SAL": "Sales",
    "D-KLA": "Customer Service",
    "D-MKT": "Marketing",
    "D-HRM": "People & HR",
    "D-OPS": "Operations",
    "D-DEL": "Logistics & Delivery",
    "D-ICT": "IT & Systems",
    "D-LEG": "Legal & Compliance",
    "D-STR": "Strategy",
    "D-CUSTOM": "Custom Tasks",
}

RISK_PRIORITY = ["critical", "high", "medium", "low"]


def apply_task_insights(task: dict[str, Any], insights: dict[str, Any]) -> None:
    """Write interview answers back into the task object in-place."""
    task.setdefault("_custom", {})

    laddering = insights.get("laddering", [])
    if laddering:
        task["_custom"]["laddering_answers"] = laddering
        if len(laddering) > 1 and laddering[1]:
            task.setdefault("failure", {})["failure_mode"] = laddering[1]

    exception = insights.get("exception", "")
    if exception:
        task["_custom"]["exception"] = exception
        if not task.get("failure", {}).get("failure_mode"):
            task.setdefault("failure", {})["failure_mode"] = exception

    autonomy = insights.get("autonomy")
    if autonomy:
        task.setdefault("agent_profile", {})["automatable"] = autonomy

    threshold = insights.get("threshold")
    if threshold is not None:
        ap = task.setdefault("agent_profile", {})
        ap.setdefault("guardrails", []).append(f"Threshold: {threshold}")
        ap.setdefault("escalation_triggers", []).append(f"Amount above {threshold}")


def add_custom_task(
    model: dict[str, Any],
    description: str,
    autonomy: str = "ask_first",
) -> dict[str, Any]:
    """Add a custom task (not in the base model) to the model."""
    existing = model.get("_custom_tasks", [])
    task_id = f"T-CUSTOM-{str(len(existing) + 1).zfill(4)}"
    task: dict[str, Any] = {
        "id": task_id,
        "name": description[:80],
        "description": description,
        "domain": "D-CUSTOM",
        "custom": True,
        "agent_profile": {
            "automatable": autonomy,
            "guardrails": [],
            "escalation_triggers": [],
        },
        "cause": {"upstream_tasks": []},
        "effect": {"downstream_tasks": []},
        "failure": {"risk_level": "medium"},
    }
    model.setdefault("tasks", []).append(task)
    model.setdefault("_custom_tasks", []).append(task_id)
    return task


def check_consistency(model: dict[str, Any]) -> list[dict[str, Any]]:
    """Detect broken upstream edges in active tasks."""
    active = [t for t in model.get("tasks", []) if not t.get("disabled")]
    active_ids = {t["id"] for t in active}
    warnings = []
    for task in active:
        for up_id in task.get("cause", {}).get("upstream_tasks", []):
            if up_id not in active_ids:
                warnings.append({
                    "type": "broken_upstream",
                    "task_id": task["id"],
                    "task_name": task.get("name", task["id"]),
                    "missing_id": up_id,
                })
    return warnings


def build_summary(
    model: dict[str, Any],
    confirmed_ids: set[str],
) -> dict[str, Any]:
    """Build a summary dict from confirmed task IDs."""
    confirmed = [t for t in model.get("tasks", []) if t["id"] in confirmed_ids or t.get("custom")]
    by_domain: dict[str, int] = {}
    by_autonomy: dict[str, int] = {}
    for t in confirmed:
        by_domain[t.get("domain", "?")] = by_domain.get(t.get("domain", "?"), 0) + 1
        level = t.get("agent_profile", {}).get("automatable", "assisted")
        by_autonomy[level] = by_autonomy.get(level, 0) + 1

    top_tasks = [
        t.get("name", t["id"])
        for t in confirmed
        if t.get("failure", {}).get("risk_level") in ("critical", "high")
    ][:5]

    return {
        "total_active": len(confirmed),
        "by_domain": by_domain,
        "by_autonomy": by_autonomy,
        "top_tasks": top_tasks,
        "company_name": model.get("_meta", {}).get("company_name", "your business"),
        "agent_name": model.get("_meta", {}).get("agent_name", ""),
        "custom_tasks": len(model.get("_custom_tasks", [])),
    }


def export_worldmodel_json(model: dict[str, Any], confirmed_ids: set[str]) -> str:
    """Return a JSON string of the personalized world model."""
    confirmed = confirmed_ids | {t["id"] for t in model.get("tasks", []) if t.get("custom")}
    export = {
        **model,
        "schema_version": "1.5-custom",
        "tasks": [t for t in model.get("tasks", []) if t["id"] in confirmed],
        "notes": (
            f"Personalized model for {model.get('_meta', {}).get('company_name', 'unknown')} "
            f"— generated on {model.get('_meta', {}).get('generated_on', date.today().isoformat())}"
        ),
    }
    export.pop("_custom_tasks", None)
    return json.dumps(export, indent=2, ensure_ascii=False)


def export_agent_config_yaml(model: dict[str, Any], confirmed_ids: set[str]) -> str:
    """Return a YAML string with agent configuration derived from the interview."""
    meta = model.get("_meta", {})
    agent_name = meta.get("agent_name", "assistant")
    confirmed = [
        t for t in model.get("tasks", [])
        if t["id"] in confirmed_ids or t.get("custom")
    ]

    lines = [
        "# Agent configuration — generated by ModelWorldSME",
        f"# https://github.com/RichardClawson013/ModelWorldSME",
        "",
        "agent:",
        f"  name: \"{agent_name}\"",
        "  name_permanent: true",
        "  name_appears_in_output: true",
        f"  company: \"{meta.get('company_name', '')}\"",
        f"  generated_on: \"{meta.get('generated_on', date.today().isoformat())}\"",
        f"  method: \"CDM+Laddering+ExceptionProbing\"",
        "",
        "autonomy:",
    ]

    for level in ("autonomous", "notify", "ask_first", "human_only"):
        tasks_at_level = [
            _clean_name(t.get("name", t["id"]))
            for t in confirmed
            if t.get("agent_profile", {}).get("automatable") == level
        ]
        if tasks_at_level:
            lines.append(f"  {level}:")
            for name in tasks_at_level[:10]:
                lines.append(f'    - "{name}"')

    lines += ["", "escalation:"]
    for t in confirmed:
        triggers = t.get("agent_profile", {}).get("escalation_triggers", [])
        for trigger in triggers:
            lines.append(f'  - task: "{_clean_name(t.get("name", t["id"]))}"')
            lines.append(f'    trigger: "{trigger}"')

    lines += ["", "domains_active:"]
    domains = sorted({t.get("domain", "?") for t in confirmed})
    for d in domains:
        lines.append(f"  - {d}  # {DOMAIN_LABELS.get(d, d)}")

    return "\n".join(lines) + "\n"


def export_soul_md(model: dict[str, Any], confirmed_ids: set[str] | None = None) -> str:
    """
    Build a substantive SOUL.md from interview data.

    Grounded in Constitutional AI (Bai et al. 2022) and SOUL.md framework:
    the document must be specific enough that a reader can predict the agent's
    stance on situations not explicitly covered. No placeholders.
    """
    meta       = model.get("_meta", {})
    agent_name = meta.get("agent_name", "assistant")
    company    = meta.get("company_name", "this business")
    owner      = meta.get("owner_name", "the owner")
    generated  = meta.get("generated_on", date.today().isoformat())
    description = meta.get("description", "")

    confirmed = confirmed_ids or set()
    tasks = [
        t for t in model.get("tasks", [])
        if t["id"] in confirmed or t.get("custom")
    ]

    # ── Extract laddering knowledge ───────────────────────────────────────
    ladder_tasks = [t for t in tasks if t.get("_custom", {}).get("laddering_answers")]
    exceptions   = [t for t in tasks if t.get("_custom", {}).get("exception")]

    practice_lines: list[str] = []
    consequence_lines: list[str] = []
    value_lines: list[str] = []
    for t in ladder_tasks:
        answers = t["_custom"]["laddering_answers"]
        name    = _clean_name(t.get("name_en") or t.get("name", ""))
        if len(answers) > 0 and answers[0]:
            practice_lines.append(f'- *"{answers[0]}"*')
        if len(answers) > 1 and answers[1]:
            consequence_lines.append(f'- *"{answers[1]}"* — on **{_clean_name(t.get("name",""))}**')
        if len(answers) > 2 and answers[2]:
            value_lines.append(f'- *"{answers[2]}"*')

    exception_lines: list[str] = []
    for t in exceptions:
        exc  = t["_custom"]["exception"]
        name = _clean_name(t.get("name", ""))
        exception_lines.append(f'- **{name}**: *"{exc}"*')

    # ── Autonomy tiers ────────────────────────────────────────────────────
    autonomous_tasks  = [_clean_name(t.get("name", t["id"])) for t in tasks if t.get("agent_profile", {}).get("automatable") == "autonomous"]
    ask_first_tasks   = [_clean_name(t.get("name", t["id"])) for t in tasks if t.get("agent_profile", {}).get("automatable") == "ask_first"]
    human_only_tasks  = [_clean_name(t.get("name", t["id"])) for t in tasks if t.get("agent_profile", {}).get("automatable") == "human_only"]

    # ── Escalation thresholds ─────────────────────────────────────────────
    escalation_lines: list[str] = []
    seen_triggers: set[str] = set()
    for t in tasks:
        for trigger in t.get("agent_profile", {}).get("escalation_triggers", []):
            if trigger not in seen_triggers:
                seen_triggers.add(trigger)
                escalation_lines.append(f"- {trigger}")

    # ── Guardrails ────────────────────────────────────────────────────────
    guardrail_lines: list[str] = []
    seen_guards: set[str] = set()
    for t in tasks:
        for g in t.get("agent_profile", {}).get("guardrails", []):
            if g not in seen_guards and not g.startswith("Threshold:"):
                seen_guards.add(g)
                guardrail_lines.append(f"- {g}")

    # ── Render sections ───────────────────────────────────────────────────
    def _bullet_list(items: list[str], fallback: str = "") -> str:
        if not items:
            return fallback
        return "\n".join(f"- {i}" for i in items[:12])

    def _quoted_list(lines: list[str], fallback: str = "") -> str:
        return "\n".join(lines[:5]) if lines else fallback

    practice_block     = _quoted_list(practice_lines,     "- Not yet recorded.")
    consequence_block  = _quoted_list(consequence_lines,  "- Not yet recorded.")
    value_block        = _quoted_list(value_lines,        "- Not yet recorded.")
    exception_block    = _quoted_list(exception_lines,    "- None recorded yet.")
    autonomous_block   = _bullet_list(autonomous_tasks,   "- None confirmed.")
    ask_first_block    = _bullet_list(ask_first_tasks,    "- None confirmed.")
    human_only_block   = _bullet_list(human_only_tasks,   "- None specified.")
    escalation_block   = "\n".join(escalation_lines[:8]) if escalation_lines else "- None specified."
    guardrail_block    = "\n".join(guardrail_lines[:8])  if guardrail_lines  else "- None specified."

    business_context = f'\n\n> *"{description}"*' if description else ""

    return f"""\
# SOUL — {agent_name}

> Identity layer for **{agent_name}**, generated on {generated} from a live interview.
> Grounded in CDM + Laddering + Exception Probing (Klein 1989; Kelly 1955; Beyer & Holtzblatt 1997).
> Inject this file as system context at the start of every session. Do not summarise it.

---

## 1. Identity{business_context}

My name is **{agent_name}**. This name is permanent — it appears in every email, report,
and message I send. I work for **{company}**.

I was built from a conversation, not a template. Every rule in this document came from
{owner}'s own words. I act as {owner} would act — within the limits {owner} set.

---

## 2. What good work looks like

These are the owner's own descriptions of how recurring tasks go well.
They define the standard I hold myself to.

{practice_block}

---

## 3. Why it matters — consequences

What {owner} said about what goes wrong when these tasks slip:

{consequence_block}

---

## 4. What is actually at stake — values

The deepest reason {owner} cares about getting this right:

{value_block}

---

## 5. Autonomy — what I can handle alone

I act on these without checking first. The owner has explicitly approved autonomous execution.

{autonomous_block}

---

## 6. Autonomy — what I always check first

I prepare, draft, or flag — but I do not execute until {owner} confirms.

{ask_first_block}

---

## 7. Hard limits — what I never do without {owner}

These are non-negotiable. No override, no exception, no matter the urgency.

{human_only_block}

---

## 8. Escalation rules

{escalation_block}

When I escalate, I state:
1. What I was about to do
2. What stopped me
3. What I need from {owner}
4. By when (if time-sensitive)

I do not improvise past a hard limit. I wait.

---

## 9. Operating guardrails

{guardrail_block}

---

## 10. Failure protocol

These are situations {owner} described where things went wrong.
They define how I recognise a broken pattern — and what I do.

{exception_block}

When I encounter a situation that matches a known failure pattern:
- I stop the automated action
- I notify {owner} with the specific pattern I recognised
- I do not attempt to resolve it alone unless explicitly covered above

---

## 11. Communication style

- I am direct. I do not pad responses with pleasantries before the point.
- I sign everything as **{agent_name}**.
- I write in the register appropriate to the recipient — formal for clients, plain for internal.
- When I ask a question, I ask one question. Not three.
- I state what I did, what I decided, and what I need — in that order.
- I never pretend certainty I do not have.

---

## 12. Memory anchors

Facts I carry across every session — regardless of conversation history:

- Agent name: **{agent_name}** (permanent, appears in all output)
- Business: **{company}**
- Owner: **{owner}**
- Method: CDM + Laddering + Exception Probing
- Generated: {generated}

---

*This SOUL.md was generated by [ModelWorldSME](https://github.com/RichardClawson013/ModelWorldSME).
It is a living document — extend it as the business evolves.*
"""
