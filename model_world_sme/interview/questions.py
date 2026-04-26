"""
interview/questions.py — Human-language question templates.

These are what the business owner sees. Never a task ID or model field name.
"""

AGENT_NAME_QUESTION = (
    "Your assistant needs a name — one you'll use consistently. "
    "This name is permanent: it will appear in emails, reports, and messages "
    "sent on your behalf. Choose something that fits your business. "
    "What would you like to call your assistant?"
)

# Domain-specific follow-up sentences.
# No intro — make_domain_question() prepends the task names found.
_DOMAIN_FOLLOWUPS: dict[str, str] = {
    "D-FIN": "Walk me through how you handle that week to week — from when a job is done to when the money is in your account.",
    "D-SAL": "How do new clients find you, and what happens from first contact to a signed deal?",
    "D-KLA": "When a client reaches out with a question or complaint, what does that process look like from start to finish?",
    "D-MKT": "What does your marketing actually look like in practice — day to day, week to week?",
    "D-HRM": "Tell me about the people side of things — scheduling, tracking time, managing absence.",
    "D-OPS": "What are the recurring tasks that just have to happen every week for the business to keep running?",
    "D-DEL": "How does delivery or fulfillment work once a job is confirmed?",
    "D-ICT": "What systems and tools do you rely on daily — and what breaks when they don't work?",
    "D-LEG": "How do you keep track of the legal and regulatory side — contracts, permits, compliance?",
    "D-STR": "How do you make bigger decisions — pricing, new services, growth — is that planned or more ad hoc?",
}


def make_domain_question(domain: str, task_names: list[str]) -> str:
    """
    Build a domain confirmation question that references the actual task names
    found in the narrative, so it sounds like a natural follow-up rather than
    a domain checklist.
    """
    if len(task_names) == 1:
        intro = f'You mentioned "{task_names[0]}".'
    elif len(task_names) == 2:
        intro = f'You mentioned "{task_names[0]}" and "{task_names[1]}".'
    else:
        intro = f'You mentioned "{task_names[0]}", "{task_names[1]}", and related things.'

    followup = _DOMAIN_FOLLOWUPS.get(domain, "Tell me more about how that works in practice.")
    return f"{intro} {followup}"
