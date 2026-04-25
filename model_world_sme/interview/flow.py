"""
interview/flow.py — Conversational interview state machine.

One question at a time. Human language only. Model names never surface.
Matching happens invisibly in the background.

Scientific basis:
  CDM    — Klein, 1989
  Laddering — Kelly, 1955
  Exception probing — Beyer & Holtzblatt, 1997
"""

from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..core.matching import extract_tasks_from_narrative, suggest_related_tasks
from ..core.cdm import CDM_PROBES
from ..core.laddering import get_laddering_question, get_exception_question
from ..core.autonomy import parse_autonomy_answer, parse_threshold
from ..core.export import (
    apply_task_insights,
    add_custom_task,
    check_consistency,
    build_summary,
    export_worldmodel_json,
    export_agent_config_yaml,
    export_soul_md,
)
from .questions import OPENING_QUESTION, AGENT_NAME_QUESTION, DOMAIN_QUESTIONS


@dataclass
class InterviewResult:
    worldmodel_json: str = ""
    agent_config_yaml: str = ""
    soul_md: str = ""
    summary: dict[str, Any] = field(default_factory=dict)
    warnings: list[dict[str, Any]] = field(default_factory=list)


class InterviewFlow:
    """
    Drives a complete business elicitation interview.

    Usage:
        flow = InterviewFlow(worldmodel_path="worldmodel/sme_worldmodel_v1.5.json")
        async for question in flow.questions():
            answer = await orchestrator.send(question)
            flow.answer(answer)
        result = flow.export()
    """

    def __init__(self, worldmodel_path: str | Path) -> None:
        path = Path(worldmodel_path)
        with path.open(encoding="utf-8") as f:
            self._model: dict[str, Any] = json.load(f)

        self._confirmed_ids: set[str] = set()
        self._insights: dict[str, dict[str, Any]] = {}
        self._narrative_parts: list[str] = []
        self._phase = 0
        self._cdm_index = 0
        self._laddering_tasks: list[dict[str, Any]] = []
        self._laddering_index = 0
        self._laddering_depth = 0
        self._done = False

        # Collected meta
        self._meta: dict[str, Any] = {}

    # ── Public interface ──────────────────────────────────────────

    async def questions(self):
        """Yield (question_text) one at a time. Call .answer(text) after each."""
        # Phase 0 — Company intro
        yield "Tell me about your business. What do you do, and what does a typical day look like for you?"

        # Phase 0b — Agent name (permanent — explain this clearly)
        yield AGENT_NAME_QUESTION

        # Phase 1 — Critical incident (CDM)
        yield "Tell me about a day that didn't go well — not necessarily the worst, just a day when things piled up or something slipped."

        for probe in CDM_PROBES:
            yield probe

        # Phase 2 — Domain confirmation (silent matching already done)
        for q in self._get_domain_questions():
            yield q

        # Phase 3 — Laddering (top risk tasks)
        for q in self._get_laddering_questions():
            yield q

        # Phase 4 — Custom tasks
        yield "Is there anything you do regularly that we haven't talked about yet?"

        # Phase 5 — Autonomy summary
        yield (
            "Last question: if your assistant could handle things on its own — "
            "what would you want it to do without asking, and what should it always check with you first?"
        )

        self._done = True

    def answer(self, text: str) -> None:
        """Feed a user answer into the interview engine."""
        self._narrative_parts.append(text)
        self._process_answer(text)

    def export(self) -> InterviewResult:
        """Build and return all three output artifacts."""
        from datetime import date
        self._model["_meta"] = {
            **self._meta,
            "generated_on": date.today().isoformat(),
            "tool_version": "ModelWorldSME-1.0",
            "method": "CDM+Laddering+ExceptionProbing",
        }

        return InterviewResult(
            worldmodel_json=export_worldmodel_json(self._model, self._confirmed_ids),
            agent_config_yaml=export_agent_config_yaml(self._model, self._confirmed_ids),
            soul_md=export_soul_md(self._model),
            summary=build_summary(self._model, self._confirmed_ids),
            warnings=check_consistency(self._model),
        )

    # ── Internal ─────────────────────────────────────────────────

    def _process_answer(self, text: str) -> None:
        if self._phase == 0:
            self._meta["description"] = text
            self._run_matching(text)
            self._phase = 1
        elif self._phase == 1:
            # Agent name
            name = text.strip().split()[0] if text.strip() else "assistant"
            self._meta["agent_name"] = name
            self._phase = 2
        elif self._phase == 2:
            # CDM narrative
            self._run_matching(text)
            self._cdm_index += 1
            if self._cdm_index >= len(CDM_PROBES):
                self._phase = 3
                self._prepare_laddering()
        elif self._phase == 3:
            # Domain confirmations — yes/no parsing
            lower = text.lower()
            if any(w in lower for w in ("yes", "correct", "right", "indeed", "yep", "sure")):
                pass  # already confirmed via matching
            elif any(w in lower for w in ("no", "not", "never", "nope")):
                pass  # could remove from confirmed_ids — keep simple for now
            self._run_matching(text)
        elif self._phase == 4:
            # Laddering answers
            self._store_laddering_answer(text)
        elif self._phase == 5:
            # Custom tasks
            if len(text.strip()) > 5:
                add_custom_task(self._model, text.strip())
        elif self._phase == 6:
            # Autonomy summary
            autonomy = parse_autonomy_answer(text)
            threshold = parse_threshold(text)
            for tid in self._confirmed_ids:
                ins = self._insights.setdefault(tid, {})
                if not ins.get("autonomy"):
                    ins["autonomy"] = autonomy
                if threshold and not ins.get("threshold"):
                    ins["threshold"] = threshold

    def _run_matching(self, text: str) -> None:
        full = " ".join(self._narrative_parts)
        matched = extract_tasks_from_narrative(full, self._model.get("tasks", []))
        for t in matched:
            self._confirmed_ids.add(t["id"])

    def _get_domain_questions(self) -> list[str]:
        from ..core.export import DOMAIN_LABELS
        active_domains = {
            t.get("domain", "")
            for t in self._model.get("tasks", [])
            if t["id"] in self._confirmed_ids
        }
        questions = []
        for domain, label in DOMAIN_LABELS.items():
            if domain in active_domains and domain in DOMAIN_QUESTIONS:
                questions.append(DOMAIN_QUESTIONS[domain])
        return questions or ["You mentioned several areas of your business. Which of these takes the most of your time?"]

    def _prepare_laddering(self) -> None:
        task_map = {t["id"]: t for t in self._model.get("tasks", [])}
        priority = ["critical", "high", "medium", "low"]
        self._laddering_tasks = sorted(
            [task_map[tid] for tid in self._confirmed_ids if tid in task_map],
            key=lambda t: priority.index(t.get("failure", {}).get("risk_level", "low"))
            if t.get("failure", {}).get("risk_level", "low") in priority else 3
        )[:3]
        self._phase = 4

    def _get_laddering_questions(self) -> list[str]:
        questions = []
        for task in self._laddering_tasks:
            name = task.get("name_en") or task.get("name", task["id"])
            for depth in range(3):
                q = get_laddering_question(name, depth)
                if q:
                    questions.append(q)
            questions.append(get_exception_question(name))
        return questions

    def _store_laddering_answer(self, text: str) -> None:
        if not self._laddering_tasks:
            return
        task = self._laddering_tasks[self._laddering_index]
        ins = self._insights.setdefault(task["id"], {})
        ins.setdefault("laddering", []).append(text)
        self._laddering_depth += 1
        steps_per_task = 4  # 3 laddering + 1 exception
        if self._laddering_depth >= steps_per_task:
            apply_task_insights(task, ins)
            self._laddering_depth = 0
            self._laddering_index += 1
            if self._laddering_index >= len(self._laddering_tasks):
                self._phase = 5
