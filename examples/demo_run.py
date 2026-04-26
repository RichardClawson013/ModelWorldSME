"""
examples/demo_run.py — Scripted demo for GIF recording.

Runs a complete interview with pre-written answers so the output is
reproducible. Each answer is chosen to produce impressive CDM probes,
laddering questions that quote the owner's own words, and exception
probing grounded in lived experience.

Used by scripts/generate_demo_gif.py to produce docs/media/demo.gif.
"""

import time
from model_world_sme import InterviewFlow, default_worldmodel_path

CYAN  = "\033[36m"
RESET = "\033[0m"
BOLD  = "\033[1m"

# 30 answers — enough for all phases:
#   1  intro
#   1  agent_name
#   1  cdm_incident
#   5  cdm_probes  (all five)
#   4  domain_confirm  (up to 4 domains — leftover answers skip gracefully)
#  12  laddering  (3 tasks × 4 answers: depth-0, depth-1, depth-2, exception)
#   1  custom
#   1  autonomy

ANSWERS = [
    # ── intro ────────────────────────────────────────────────────────────
    "I run a small painting company. Five guys, mostly residential. "
    "My day is quotes in the morning, chasing invoices, and making sure "
    "the right crew is at the right job.",

    # ── agent name ───────────────────────────────────────────────────────
    "Nova",

    # ── CDM incident ─────────────────────────────────────────────────────
    "A client called angry about an invoice from six weeks ago they said "
    "they never received. Turned out I'd sent it to the wrong email. "
    "Meanwhile two crews were waiting on a material order I forgot to place.",

    # ── CDM probe 0: timeline reconstruction ─────────────────────────────
    # Question will be: "Walk me through a client called angry about an invoice
    # step by step — from when you first noticed something was off to how it ended."
    "I checked my sent folder immediately, saw the wrong address, resent it, "
    "apologised, offered a small discount. Client paid within the hour. "
    "But by then the material order had been sitting three hours.",

    # ── CDM probe 1: cue recognition ─────────────────────────────────────
    # "At that moment, what was the first sign that told you this needed your attention?"
    "The phone ringing. An angry client is never ambiguous — you know "
    "before they say a word that something went wrong on your end.",

    # ── CDM probe 2: expertise ────────────────────────────────────────────
    # "What did you need to know or decide that someone without your experience
    # wouldn't have handled the same way?"
    "That it was an address error, not a payment dispute. A novice would "
    "have argued. I checked first, apologised second, and fixed it in five minutes.",

    # ── CDM probe 3: counterfactual ───────────────────────────────────────
    # "If you hadn't been there — what would have gone wrong?"
    "The invoice would have sat unpaid. The client would have taken the "
    "next job elsewhere without ever saying why.",

    # ── CDM probe 4: resolution ───────────────────────────────────────────
    # "How did it end up, and what would you do differently?"
    "It ended fine — client stayed, paid the same day. I added a rule: "
    "double-check the email address before hitting send. Every time.",

    # ── domain confirm 1  (D-FIN or D-OPS — whatever gets matched) ────────
    "Yes, that's the core of it — finance runs everything.",

    # ── domain confirm 2 ──────────────────────────────────────────────────
    "Yes, operations is constant. Something every single week.",

    # ── domain confirm 3 ──────────────────────────────────────────────────
    "Yes, that's right.",

    # ── domain confirm 4 ──────────────────────────────────────────────────
    "Yes.",

    # ── laddering task 1 — depth 0 (practice) ────────────────────────────
    # "Let's talk about Create invoice. When that goes well, what does it look like?"
    "I send it the same day the job finishes — PDF to the client, "
    "copy to my own folder. Usually paid within two weeks.",

    # ── laddering task 1 — depth 1 (consequence) ─────────────────────────
    # "You said I send it the same day. Why does getting that right matter to you?"
    "Cash flow. We're a small operation — if three invoices slip a week, "
    "I'm covering wages out of my own pocket.",

    # ── laddering task 1 — depth 2 (value) ───────────────────────────────
    # "You said cash flow. Why does cash flow matter — what's actually at stake?"
    "I've had to delay payroll once. Never again. That's the line.",

    # ── laddering task 1 — exception ─────────────────────────────────────
    # "You said never again is what matters. Tell me about a time Create invoice
    # didn't go that way..."
    "Besides the wrong email? Sometimes a client disputes the amount. "
    "Then I have to pull the original quote, the change orders, everything. "
    "Takes half a day and kills the week.",

    # ── laddering task 2 — depth 0 ───────────────────────────────────────
    "I draft it the same day, send within 24 hours. Most clients decide "
    "within a week.",

    # ── laddering task 2 — depth 1 ───────────────────────────────────────
    "First impression. If the quote is slow, they assume the job will be slow.",

    # ── laddering task 2 — depth 2 ───────────────────────────────────────
    "We lose the job. Someone faster sends a quote while I'm still thinking about it.",

    # ── laddering task 2 — exception ─────────────────────────────────────
    "Client called to say our quote never arrived. It went to spam. "
    "We lost the job — found out a month later they used someone else.",

    # ── laddering task 3 — depth 0 ───────────────────────────────────────
    "I call each crew lead the evening before. Confirm the address, "
    "start time, and whether materials are on site.",

    # ── laddering task 3 — depth 1 ───────────────────────────────────────
    "If a crew shows up at the wrong site it's a lost day. "
    "Five guys standing in the wrong street.",

    # ── laddering task 3 — depth 2 ───────────────────────────────────────
    "Wages for five people wasted, plus the client sees it. "
    "That kind of mistake you don't recover from easily.",

    # ── laddering task 3 — exception ─────────────────────────────────────
    "Crew showed up at last week's address by mistake. "
    "The neighbour called asking why painters were in their garden.",

    # ── custom tasks ──────────────────────────────────────────────────────
    "No, I think we've covered everything.",

    # ── autonomy ──────────────────────────────────────────────────────────
    "Invoice reminders it can send on its own. Quotes it can draft but "
    "I always review before sending. Payroll — never without me. "
    "Anything above 500 euros needs my sign-off.",
]


def show(text: str, prefix: str = "") -> None:
    print(prefix + text, flush=True)
    time.sleep(0.06)


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
