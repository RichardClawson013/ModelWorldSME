"""
examples/demo_run.py — Scripted demo for GIF recording.

Runs a complete interview with pre-written answers so the output is
reproducible. Used by demo.tape (VHS) to generate the README GIF.
"""

import time
from model_world_sme import InterviewFlow, default_worldmodel_path

ANSWERS = [
    "I run a small painting company. Five guys, mostly residential. "
    "My day is quotes in the morning, chasing invoices, and making sure the right crew is at the right job.",
    "Nova",
    "Had a client call about an invoice from six weeks ago they said they never received. "
    "Turned out I'd sent it to the wrong email. Meanwhile two crews were waiting on a material order I forgot to place.",
    "Started with the client calling angry. I checked my sent folder, saw the wrong address immediately. "
    "Resent it, apologised, offered a small discount. Client paid within the hour.",
    "At that moment it was the phone ringing — an angry client is never a good sign.",
    "I knew immediately it was an admin error, not a payment issue. A junior would have panicked.",
    "If I hadn't caught it the client would have escalated. Could have lost the account.",
    "It ended fine, but I added a rule: always double-check the email address before sending.",
    "Yes, finance and operations are the core of it.",
    "I send it the same day the job finishes, PDF to the client, copy to my own folder. Usually paid within two weeks.",
    "Cash flow. We're a small operation — if three invoices slip a week, I'm covering wages out of my own pocket.",
    "I've had to delay payroll once. Never again. That's the line.",
    "Sometimes a client disputes the amount. Then I have to pull the original quote, the change orders, everything.",
    "No, I think we've covered it all.",
    "Send reminders for unpaid invoices, definitely. Quotes it can draft but I always review before sending. "
    "Payroll — never touch that without me.",
]

DELAY = 0.04  # seconds per character


def typewrite(text: str) -> None:
    for ch in text:
        print(ch, end="", flush=True)
        time.sleep(DELAY)
    print()


def main() -> None:
    flow = InterviewFlow(worldmodel_path=default_worldmodel_path())

    print("=" * 60)
    print("ModelWorldSME — Business Elicitation Interview")
    print("=" * 60)

    answers = iter(ANSWERS)
    question = flow.next()

    while question:
        print()
        typewrite(question)
        time.sleep(0.3)
        print()
        answer = next(answers, "")
        print(f"\033[36m> {answer}\033[0m")
        time.sleep(0.2)
        question = flow.next(answer)

    print()
    print("=" * 60)
    print("Interview complete. Generating outputs...")
    result = flow.export()
    agent = result.summary.get("agent_name", "assistant")
    total = result.summary.get("total_active", 0)
    print(f"  Tasks confirmed: {total}")
    print(f"  Agent name:      {agent}")
    print(f"  Outputs:         worldmodel · agent_config · SOUL · report")
    print("=" * 60)


if __name__ == "__main__":
    main()
