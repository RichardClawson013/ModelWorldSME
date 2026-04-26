"""
examples/demo_run.py — Scripted demo for GIF recording (VHS).

Runs a short, representative interview with pre-written answers.
Instant output — no typewriter delay — so VHS can capture it quickly.
"""

import sys
import time
from model_world_sme import InterviewFlow, default_worldmodel_path

CYAN  = "\033[36m"
RESET = "\033[0m"
BOLD  = "\033[1m"

# Short demo: just enough to show the method without running 5 minutes
ANSWERS = [
    "I run a small painting company. Five guys, mostly residential. "
    "Quotes in the morning, chasing invoices, making sure the right crew is at the right job.",
    "Nova",
    "Client called angry about an invoice I'd sent to the wrong email six weeks ago. "
    "Meanwhile two crews were waiting on a material order I'd forgotten.",
    "I checked the sent folder, saw the wrong address, resent it, offered a small discount. "
    "Client paid within the hour.",
    "The phone ringing — an angry client is never ambiguous.",
    "I sent it the same day the job finishes, PDF to the client, copy to my folder.",
    "Cash flow. If three invoices slip a week I'm covering wages out of my own pocket.",
    "I've had to delay payroll once. Never again.",
    "No, I think that covers it.",
    "Send reminders autonomously. Quotes it can draft but I always review. "
    "Payroll — never without me.",
]


def show(text: str, prefix: str = "") -> None:
    print(prefix + text, flush=True)
    time.sleep(0.05)


def main() -> None:
    flow = InterviewFlow(worldmodel_path=default_worldmodel_path())

    print(BOLD + "=" * 60 + RESET)
    print(BOLD + "ModelWorldSME — Business Elicitation Interview" + RESET)
    print(BOLD + "=" * 60 + RESET)

    answers = iter(ANSWERS)
    question = flow.next()

    while question:
        print()
        show(question)
        time.sleep(0.1)
        answer = next(answers, None)
        if answer is None:
            break
        show(answer, prefix=CYAN + "> " + RESET)
        time.sleep(0.1)
        question = flow.next(answer)

    print()
    print(BOLD + "=" * 60 + RESET)
    result = flow.export()
    agent = result.summary.get("agent_name", "assistant")
    total = result.summary.get("total_active", 0)
    print(f"  Tasks confirmed: {BOLD}{total}{RESET}")
    print(f"  Agent name:      {BOLD}{agent}{RESET}")
    print(f"  Outputs:         worldmodel · agent_config · SOUL · report")
    print(BOLD + "=" * 60 + RESET)


if __name__ == "__main__":
    main()
