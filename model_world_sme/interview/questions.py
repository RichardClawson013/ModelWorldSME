"""
interview/questions.py — Human-language question templates.

These are what the business owner sees. Never a task ID or model field name.
"""

OPENING_QUESTION = (
    "Tell me about your business. What do you do, "
    "and what does a typical day look like for you?"
)

AGENT_NAME_QUESTION = (
    "Your assistant needs a name — one you'll use consistently. "
    "This name is permanent: it will appear in emails, reports, and messages "
    "sent on your behalf. Choose something that fits your business. "
    "What would you like to call your assistant?"
)

# One plain-language question per domain — confirms without naming tasks
DOMAIN_QUESTIONS: dict[str, str] = {
    "D-FIN": (
        "You mentioned finances. Walk me through how you handle invoicing, "
        "payments, and tax — what does that process actually look like week to week?"
    ),
    "D-SAL": (
        "How do new clients find you, and what happens from first contact "
        "to a signed deal?"
    ),
    "D-KLA": (
        "When a client has a question or a complaint, what does that journey look like "
        "from the moment it comes in?"
    ),
    "D-MKT": (
        "How do you put yourself out there — social media, ads, word of mouth? "
        "What does your marketing actually look like in practice?"
    ),
    "D-HRM": (
        "Tell me about your team — hiring, scheduling, tracking hours or absence. "
        "How do you handle the people side of the business?"
    ),
    "D-OPS": (
        "What are the recurring operational tasks that just have to happen "
        "every week for the business to keep running?"
    ),
    "D-DEL": (
        "How does delivery or fulfillment work — getting your product or service "
        "to the client once the job is confirmed?"
    ),
    "D-ICT": (
        "What systems and tools do you rely on daily? "
        "And what breaks when they don't work?"
    ),
    "D-LEG": (
        "Contracts, compliance, GDPR, permits — how do you keep track of the "
        "legal and regulatory side of things?"
    ),
    "D-STR": (
        "How do you make bigger decisions — pricing, new services, growth? "
        "Is that something you think about regularly or more ad hoc?"
    ),
}
