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


def export_soul_md(model: dict[str, Any]) -> str:
    """Return a SOUL.md skeleton for the agent, pre-filled from interview data."""
    meta = model.get("_meta", {})
    agent_name = meta.get("agent_name", "assistant")
    company = meta.get("company_name", "the business")
    owner = meta.get("owner_name", "the owner")

    return f"""# SOUL — {agent_name}

> This file defines who {agent_name} is. It is the identity layer loaded on every session start.
> Generated by ModelWorldSME on {meta.get('generated_on', date.today().isoformat())}.

## Identity

My name is **{agent_name}**. This name is permanent — it appears in everything I send.
I work for **{company}**, owned by **{owner}**.

## What I do

I handle recurring tasks so {owner} can focus on work that requires judgement.
I do not replace {owner} — I handle what follows a pattern.

## How I communicate

[To be filled in during interview — tone, formality, preferred style]

## What I never do without asking

[To be filled in — escalation conditions from the world model]

## What I can do autonomously

[To be filled in — autonomous tasks from the world model]

## My limits

- I never share confidential information
- I never make decisions above the agreed thresholds
- When in doubt, I ask {owner} first

---
*This SOUL.md is a starting point. It will evolve with every interaction.*
"""
