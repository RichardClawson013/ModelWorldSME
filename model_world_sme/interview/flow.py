"""
interview/flow.py — Conversational interview state machine.

Turn-based: call next(answer) to advance the interview one step.
The first call takes no answer. Returns None when complete.

This replaces the previous async-generator approach, which was fundamentally
incompatible with dynamic interviews: a generator cannot adapt to answers it
has not yet received.

Scientific basis:
  CDM              — Klein, 1989
  Laddering        — Kelly, 1955
  Exception probing — Beyer & Holtzblatt, 1997
"""

from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..core.matching import extract_tasks_from_narrative
from ..core.cdm import make_cdm_probes
from ..core.laddering import make_laddering_question, make_exception_question
from ..core.autonomy import parse_autonomy_answer, parse_threshold
from ..core.export import (
    apply_task_insights,
    add_custom_task,
    check_consistency,
    build_summary,
    export_worldmodel_json,
    export_agent_config_yaml,
    export_soul_md,
    DOMAIN_LABELS,
)
from ..core.report import build_html_report
from .questions import AGENT_NAME_QUESTION, make_domain_question, _DOMAIN_FOLLOWUPS


@dataclass
class InterviewResult:
    worldmodel_json: str = ""
    agent_config_yaml: str = ""
    soul_md: str = ""
    html_report: str = ""
    summary: dict[str, Any] = field(default_factory=dict)
    warnings: list[dict[str, Any]] = field(default_factory=list)


class InterviewFlow:
    """
    Drives a complete business elicitation interview.

    Usage:
        flow = InterviewFlow(worldmodel_path="worldmodel/sme_worldmodel_v1.5.json")
        question = flow.next()           # first question, no answer yet
        while question:
            answer = input(f"{question}\\n> ")
            question = flow.next(answer)
        result = flow.export()
    """

    def __init__(self, worldmodel_path: str | Path) -> None:
        path = Path(worldmodel_path)
        with path.open(encoding="utf-8") as f:
            self._model: dict[str, Any] = json.load(f)

        self._confirmed_ids: set[str] = set()
        self._insights: dict[str, dict[str, Any]] = {}
        self._narrative_parts: list[str] = []
        self._meta: dict[str, Any] = {}

        # Phase
        self._phase = "intro"

        # CDM state
        self._incident = ""
        self._cdm_probes: list[str] = []
        self._cdm_index = 0

        # Domain confirm state — list of (domain_code, [task_name, ...])
        self._domain_queue: list[tuple[str, list[str]]] = []

        # Laddering state
        self._ladder_queue: list[dict[str, Any]] = []
        self._ladder_task: dict[str, Any] | None = None
        self._ladder_depth = 0
        self._ladder_last_answer = ""
        self._in_exception = False

    # ── Public interface ───────────────────────────────────────────

    def next(self, answer: str | None = None) -> str | None:
        """
        Feed the previous answer (or None for the very first call).
        Returns the next question, or None when the interview is complete.
        """
        if answer is not None:
            self._ingest(answer)
        return self._emit()

    @property
    def done(self) -> bool:
        return self._phase == "done"

    def export(self) -> InterviewResult:
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
            soul_md=export_soul_md(self._model, self._confirmed_ids),
            html_report=build_html_report(self._model, self._confirmed_ids),
            summary=build_summary(self._model, self._confirmed_ids),
            warnings=check_consistency(self._model),
        )

    # ── Answer processing ─────────────────────────────────────────

    def _ingest(self, answer: str) -> None:
        """Process an incoming answer and advance the phase if this answer completes it."""
        self._narrative_parts.append(answer)
        self._run_matching()

        if self._phase == "intro":
            self._meta["description"] = answer
            self._phase = "agent_name"

        elif self._phase == "agent_name":
            name = answer.strip().split()[0] if answer.strip() else "assistant"
            self._meta["agent_name"] = name
            self._phase = "cdm_incident"

        elif self._phase == "cdm_incident":
            self._incident = answer
            self._cdm_probes = make_cdm_probes(answer)
            self._cdm_index = 0
            self._phase = "cdm_probes"

        elif self._phase == "cdm_probes":
            self._cdm_index += 1
            if self._cdm_index >= len(self._cdm_probes):
                self._prepare_domain_queue()
                if self._domain_queue:
                    self._phase = "domain_confirm"
                else:
                    self._enter_laddering_or_custom()

        elif self._phase == "domain_confirm":
            if self._domain_queue:
                self._domain_queue.pop(0)
            if not self._domain_queue:
                self._enter_laddering_or_custom()

        elif self._phase == "laddering":
            self._process_ladder_answer(answer)

        elif self._phase == "custom":
            ans = answer.strip()
            _neg = ("no", "nee", "nope", "nothing", "none", "not really", "that's all", "i think we")
            if len(ans) > 5 and not ans.lower().startswith(_neg):
                add_custom_task(self._model, ans)
            self._phase = "autonomy"

        elif self._phase == "autonomy":
            self._process_global_autonomy(answer)
            self._phase = "done"

    # ── Question generation ───────────────────────────────────────

    def _emit(self) -> str | None:
        """Return the next question for the current phase."""
        if self._phase == "intro":
            return (
                "Tell me about your business. "
                "What do you do, and what does a typical day look like for you?"
            )

        if self._phase == "agent_name":
            return AGENT_NAME_QUESTION

        if self._phase == "cdm_incident":
            return (
                "Tell me about a day that didn't go well — not necessarily the worst, "
                "just a day when things piled up or something slipped through."
            )

        if self._phase == "cdm_probes":
            if self._cdm_index < len(self._cdm_probes):
                return self._cdm_probes[self._cdm_index]
            return None

        if self._phase == "domain_confirm":
            if self._domain_queue:
                domain, task_names = self._domain_queue[0]
                return make_domain_question(domain, task_names)
            return None

        if self._phase == "laddering":
            return self._make_ladder_question()

        if self._phase == "custom":
            return "Is there anything you do regularly that we haven't talked about yet?"

        if self._phase == "autonomy":
            return (
                "Last question: if your assistant could handle things on its own — "
                "what would you want it to do without asking, "
                "and what should it always check with you first?"
            )

        return None  # done

    # ── Matching ──────────────────────────────────────────────────

    def _run_matching(self) -> None:
        full = " ".join(self._narrative_parts)
        matched = extract_tasks_from_narrative(full, self._model.get("tasks", []))
        for t in matched:
            self._confirmed_ids.add(t["id"])

    # ── Phase helpers ─────────────────────────────────────────────

    def _enter_laddering_or_custom(self) -> None:
        self._prepare_ladder_queue()
        if self._ladder_queue:
            self._phase = "laddering"
            self._start_next_ladder_task()
        else:
            self._phase = "custom"

    def _prepare_domain_queue(self) -> None:
        task_map = {t["id"]: t for t in self._model.get("tasks", [])}
        domains: dict[str, list[str]] = {}
        for tid in self._confirmed_ids:
            task = task_map.get(tid)
            if not task:
                continue
            domain = task.get("domain", "")
            name = self._display_name(task)
            if domain and name:
                domains.setdefault(domain, []).append(name)
        # Only confirm domains where we found 2+ tasks (reduces noise) and
        # that have a defined follow-up question
        self._domain_queue = [
            (domain, names)
            for domain, names in domains.items()
            if len(names) >= 2 and domain in _DOMAIN_FOLLOWUPS
        ][:4]

    def _prepare_ladder_queue(self) -> None:
        task_map = {t["id"]: t for t in self._model.get("tasks", [])}
        risk_order = ["critical", "high", "medium", "low"]
        candidates = [task_map[tid] for tid in self._confirmed_ids if tid in task_map]
        self._ladder_queue = sorted(
            candidates,
            key=lambda t: (
                risk_order.index(t.get("failure", {}).get("risk_level", "low"))
                if t.get("failure", {}).get("risk_level", "low") in risk_order
                else 3
            ),
        )[:3]

    def _start_next_ladder_task(self) -> None:
        self._ladder_task = self._ladder_queue.pop(0)
        self._ladder_depth = 0
        self._ladder_last_answer = ""
        self._in_exception = False

    @staticmethod
    def _display_name(task: dict) -> str:
        """Return a short readable task name for use in interview questions."""
        import re
        name_en = task.get("name_en", "")
        name_nl = re.sub(r"\s*\(\d+\)\s*$", "", task.get("name", "")).strip()
        # O*NET descriptions can be full sentences — truncate at 50 chars on a word boundary
        if name_en and len(name_en) <= 50:
            return name_en
        if name_nl and len(name_nl) <= 40:
            return name_nl
        if name_en:
            words = name_en[:50].rsplit(" ", 1)
            return words[0].rstrip(".,;") + "…"
        return name_nl or "this task"

    def _make_ladder_question(self) -> str | None:
        if not self._ladder_task:
            return None
        task_name = self._display_name(self._ladder_task)
        if self._in_exception:
            return make_exception_question(task_name, self._ladder_last_answer or None)
        return make_laddering_question(
            task_name,
            self._ladder_depth,
            self._ladder_last_answer or None,
        )

    def _process_ladder_answer(self, answer: str) -> None:
        if not self._ladder_task:
            self._phase = "custom"
            return

        ins = self._insights.setdefault(self._ladder_task["id"], {})

        if self._in_exception:
            ins["exception"] = answer
            apply_task_insights(self._ladder_task, ins)
            if self._ladder_queue:
                self._start_next_ladder_task()
            else:
                self._phase = "custom"
        else:
            ins.setdefault("laddering", []).append(answer)
            self._ladder_last_answer = answer
            self._ladder_depth += 1
            if self._ladder_depth >= 3:
                self._in_exception = True

    def _process_global_autonomy(self, answer: str) -> None:
        """Apply a global autonomy answer to all confirmed tasks that have no specific level set."""
        autonomy = parse_autonomy_answer(answer)
        threshold = parse_threshold(answer)
        task_map = {t["id"]: t for t in self._model.get("tasks", [])}
        for tid in self._confirmed_ids:
            task = task_map.get(tid)
            if not task:
                continue
            ins = self._insights.setdefault(tid, {})
            if not ins.get("autonomy"):
                ins["autonomy"] = autonomy
            if threshold and not ins.get("threshold"):
                ins["threshold"] = threshold
            apply_task_insights(task, ins)
