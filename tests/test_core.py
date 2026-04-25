"""
tests/test_core.py — Smoke tests for ModelWorldSME core.
Run: python -m pytest tests/ or python tests/test_core.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from model_world_sme.core import (
    extract_tasks_from_narrative,
    suggest_related_tasks,
    get_cdm_probe,
    get_laddering_question,
    get_exception_question,
    parse_autonomy_answer,
    parse_threshold,
    add_custom_task,
    check_consistency,
    build_summary,
    AUTONOMY_LEVELS,
)

MINI_MODEL = {
    "tasks": [
        {
            "id": "T-0001", "name": "Create invoice", "name_en": "Create invoice",
            "domain": "D-FIN",
            "description": "Invoice billing create send to customer client",
            "cause": {"trigger": "job done", "upstream_tasks": ["T-0002"]},
            "effect": {"downstream_tasks": ["T-0003"]},
            "state_inputs": [], "state_outputs": [],
            "agent_profile": {"automatable": "assisted", "guardrails": [], "escalation_triggers": []},
            "failure": {"risk_level": "high", "failure_mode": ""},
        },
        {
            "id": "T-0002", "name": "Write quote", "name_en": "Write quote",
            "domain": "D-SAL",
            "description": "Quotation proposal write customer request",
            "cause": {"trigger": "customer request", "upstream_tasks": []},
            "effect": {"downstream_tasks": ["T-0001"]},
            "state_inputs": [], "state_outputs": [],
            "agent_profile": {"automatable": "assisted", "guardrails": [], "escalation_triggers": []},
            "failure": {"risk_level": "medium", "failure_mode": ""},
        },
        {
            "id": "T-0003", "name": "Process payment", "name_en": "Process payment",
            "domain": "D-FIN",
            "description": "Payment process transfer receive money",
            "cause": {"trigger": "invoice sent", "upstream_tasks": ["T-0001"]},
            "effect": {"downstream_tasks": []},
            "state_inputs": [], "state_outputs": [],
            "agent_profile": {"automatable": "autonomous", "guardrails": [], "escalation_triggers": []},
            "failure": {"risk_level": "critical", "failure_mode": ""},
        },
    ],
    "_custom_tasks": [],
}

passed = failed = 0

def assert_ok(label, condition):
    global passed, failed
    if condition:
        print(f"  ✓ {label}")
        passed += 1
    else:
        print(f"  ✗ {label}")
        failed += 1

print("\nextract_tasks_from_narrative")
result = extract_tasks_from_narrative("I send invoices to customers", MINI_MODEL["tasks"])
assert_ok("recognises 'invoice'", any(t["id"] == "T-0001" for t in result))
assert_ok("returns list", isinstance(result, list))

print("\nsuggest_related_tasks")
suggestions = suggest_related_tasks(["T-0001"], MINI_MODEL["tasks"])
assert_ok("suggests upstream/downstream", len(suggestions) > 0)
assert_ok("does not include input task", all(t["id"] != "T-0001" for t in suggestions))

print("\nCDM probes")
assert_ok("probe 0 is string", isinstance(get_cdm_probe(0), str))
assert_ok("out of range returns None", get_cdm_probe(999) is None)

print("\nladdering")
assert_ok("depth 0 contains task name", "Create invoice" in (get_laddering_question("Create invoice", 0) or ""))
assert_ok("depth 2 exists", get_laddering_question("X", 2) is not None)
assert_ok("depth 3 is None", get_laddering_question("X", 3) is None)

print("\nexception probing")
assert_ok("contains task name", "Write quote" in get_exception_question("Write quote"))

print("\nparse_autonomy_answer")
assert_ok("'independently' → autonomous", parse_autonomy_answer("it can handle this independently") == "autonomous")
assert_ok("'ask first' → ask_first",      parse_autonomy_answer("ask me first before doing it")    == "ask_first")
assert_ok("'let me know' → notify",       parse_autonomy_answer("do it and let me know after")     == "notify")

print("\nparse_threshold")
assert_ok("500 detected",        parse_threshold("above 500 euros") == 500.0)
assert_ok("no amount → None",    parse_threshold("never do it alone") is None)

print("\nadd_custom_task")
model = {"tasks": [], "_custom_tasks": []}
task = add_custom_task(model, "Handle warranty claims")
assert_ok("task added",           len(model["tasks"]) == 1)
assert_ok("id starts T-CUSTOM",   task["id"].startswith("T-CUSTOM"))
assert_ok("domain is D-CUSTOM",   task["domain"] == "D-CUSTOM")

print("\ncheck_consistency")
assert_ok("no warnings on valid model", len(check_consistency(MINI_MODEL)) == 0)
broken = {"tasks": [t for t in MINI_MODEL["tasks"] if t["id"] != "T-0002"]}
assert_ok("broken upstream detected", any(w["type"] == "broken_upstream" for w in check_consistency(broken)))

print("\nbuild_summary")
summary = build_summary(MINI_MODEL, {"T-0001", "T-0003"})
assert_ok("total_active = 2", summary["total_active"] == 2)
assert_ok("D-FIN has 2",      summary["by_domain"].get("D-FIN") == 2)

print(f"\n{'─' * 40}")
print(f"Result: {passed} passed, {failed} failed\n")
sys.exit(1 if failed else 0)
