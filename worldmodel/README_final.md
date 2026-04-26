# ModelWorldSME

[![CI](https://github.com/RichardClawson013/ModelWorldSME/actions/workflows/ci.yml/badge.svg)](https://github.com/RichardClawson013/ModelWorldSME/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/model-world-sme)](https://pypi.org/project/model-world-sme/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/model-world-sme)](https://pypi.org/project/model-world-sme/)

> **One conversation with the business owner. Three files the agent can actually use.**

**[Try it live →](https://richardclawson013.github.io/ModelWorldSME/)**

![ModelWorldSME demo](./docs/media/demo.gif)

---

## The problem every agent deployment runs into

You give an AI agent access to your email, your calendar, your invoicing tool. It does things. Some of them are useful. Then one day it does something that makes no sense — sends a payment reminder to a client you're in a dispute with, drafts a quote that's missing two months of price increases, handles a task that was supposed to come to you.

The agent isn't broken. It just doesn't know your business.

It doesn't know that invoices go out the same day a job finishes because that's the difference between making payroll and covering it yourself. It doesn't know that client X always pushes back on the first quote so you build in margin. It doesn't know that the material orders and the crew schedule are connected — delay one and the other collapses.

That knowledge lives in one place: inside you. It came from experience. A lot of it you've never written down. It's the reason you're good at running your business, and it's the reason your agent keeps guessing wrong.

**ModelWorldSME builds that knowledge into a structured file your agent can actually read.**

---

## What it does

It has a conversation with you — or with your client if you're building agents for others. A real conversation, not a form. It asks about your business, about a day that went wrong, about the tasks that matter most and what happens when they don't get done. From that conversation, it builds three files:

**`worldmodel_Nova.json`** — a map of every task confirmed during the interview: what triggers it, what depends on it, what breaks if it goes wrong, and whether the agent can handle it alone or needs to ask first. Nova is the agent's name — chosen during the interview, permanent.

**`agent_config_Nova.yaml`** — a configuration file the agent loads at startup. What it can do without asking. What it needs approval for. What it should never touch. Thresholds, escalation rules, autonomy levels — all based on what the owner actually said.

**`SOUL_Nova.md`** — the agent's identity, built entirely from the interview. Twelve sections, no placeholders: the owner's exact words on what good work looks like, what the consequences are when it slips, what's actually at stake, which tasks the agent owns alone, which it always checks first, which it never touches, escalation rules with specific thresholds, operating guardrails, the failure stories from lived experience, communication style, and the facts that carry across every session. Loaded at the start of every session. Based on Constitutional AI (Bai et al. 2022) — specific enough that you can predict the agent's behaviour on situations not explicitly covered.

**`report_Nova.html`** — a printable analysis of the business: risk tiers, automation opportunities, compliance gaps. Open in a browser, print to PDF.

---

## What the conversation looks like

This is a real run. Not staged.

```
Tell me about your business. What do you do, and what does
a typical day look like for you?

> I run a small painting company. Five guys, mostly residential.
  My day is quotes in the morning, chasing invoices, and making
  sure the right crew is at the right job.

Your assistant needs a name — one you'll use consistently.
This name is permanent: it will appear in emails, reports, and
messages sent on your behalf. What would you like to call your
assistant?

> Nova

Tell me about a day that didn't go well — not necessarily the
worst, just a day when things piled up or something slipped through.

> Had a client call about an invoice from six weeks ago they said
  they never received. Turned out I'd sent it to the wrong email.
  Meanwhile two crews were waiting on a material order I forgot
  to place.

Walk me through a client call about an invoice from six weeks ago
step by step — from when you first noticed something was off to
how it ended.

> Started with the client calling angry. I checked my sent folder,
  saw the wrong address immediately. Resent it, apologised, offered
  a small discount. Client paid within the hour. But by then the
  material order had been sitting for three hours.
```

Notice that second follow-up question. It's not a template — it's built from what was just said. "A client call about an invoice from six weeks ago" came from the owner's answer. Every question in the interview works this way. Each one picks up where the last one left off.

```
Let's talk about Create invoice. When that goes well, what does
it actually look like in practice?

> I send it the same day the job finishes, PDF to the client,
  copy to my own folder. Usually paid within two weeks.

You said "I send it the same day the job finishes." Why does
getting that right matter to you?

> Cash flow. We're a small operation — if three invoices slip
  a week, I'm covering wages out of my own pocket.

And why does cash flow matter — what's actually at stake if it slips?

> I've had to delay payroll once. Never again. That's the line.
```

Three questions on the same task. First: what does it look like? Second: why does it matter? Third: what's actually at stake? By the third answer, you're past the professional response and into the real one. "I've had to delay payroll once. Never again." That's the line. And now the agent knows it.

```
Last question: if your assistant could handle things on its own —
what would you want it to do without asking, and what should it
always check with you first?

> Send reminders for unpaid invoices, definitely. Quotes it can
  draft but I always review before sending. Payroll — never touch
  that without me.

============================================================
Interview complete. Generating outputs...
  Tasks confirmed: 35
  Agent name:      Nova
  Saved: worldmodel_Nova.json · agent_config_Nova.yaml · SOUL_Nova.md · report_Nova.html
```

---

## Why the questions work the way they do

The interview uses three techniques from forty years of research into how experts actually make decisions — not how they describe making them.

**Asking about a bad day, not a typical day (Critical Decision Method — Klein, 1989)**
When you ask someone "what do you normally do," you get the polished version. When you ask "tell me about a day that went wrong," you get the real one — with the missing material order and the client calling angry. People reconstruct real incidents in far more useful detail than they describe their routine. The follow-ups dig into that incident: what tipped you off, what would someone new have done differently, what would have happened if you hadn't caught it.

**Three questions deep on every important task (Laddering — Kelly, 1955)**
For each high-risk task, three questions following the owner's own words: practice (what does it actually look like), consequence (why does getting it right matter), value (what's actually at stake). Each question quotes the previous answer. This is why the conversation feels like a conversation — and why by the third answer you're getting something an agent can use as a hard limit.

**Asking when things go wrong (Exception probing — Beyer & Holtzblatt, 1997)**
Edge cases are where agents fail. If the agent only knows the happy path, the first unexpected situation is one it's never been prepared for. Exception probing asks specifically: "tell me about a time this didn't go the way it should." That's how you surface the rules that don't exist in any manual.

Combining these methods improved validity in 15 of 23 studies reviewed by Crandall, Klein & Hoffman (2006, *Working Minds*). That's why all three are used together.

---

## The knowledge base

The interview matches what the owner says against a knowledge base of **2,986 SME tasks** across 10 domains, connected by **16,281 causal edges**.

| Domain | What's in it |
|---|---|
| D-FIN | Invoicing, payments, tax, bookkeeping, cash flow |
| D-SAL | Leads, quotes, pipeline, negotiations, deals |
| D-KLA | Customer questions, complaints, retention |
| D-MKT | Social media, content, campaigns, SEO |
| D-HRM | Hiring, payroll, contracts, absence, onboarding |
| D-OPS | Scheduling, procurement, maintenance, production |
| D-DEL | Shipping, fulfillment, transport, logistics |
| D-ICT | Systems, backups, security, tools, automation |
| D-LEG | Contracts, GDPR, insurance, permits, compliance |
| D-STR | Pricing, growth, partnerships, strategic decisions |

A causal edge means task A feeds task B. Remove A and B breaks. That's what makes this a world model rather than a spreadsheet — it's a map of how a business actually works, with consequences.

---

## Who built this and why

This was not built in a lab. It was built by someone who deploys AI agents for small businesses and kept running into the same wall: every deployment required weeks of custom work to teach the agent what the business does before it could do anything useful.

O*NET (US Dept of Labor) describes 19,000+ tasks — organized by occupation, no causal structure, not built for agent safety. ESCO (European Commission) covers 3,039 occupations in 28 languages — same gap. Osterwalder's Business Model Canvas captures why a business exists but not what people do hour by hour. None of them answer: "can a machine safely do this task, what are the limits, and what breaks if it gets it wrong?"

This library fills that gap through conversation. It's v1. The matching is keyword-based. The knowledge base has gaps. But the core idea — agents need a model of the domain they operate in, and the fastest way to build one is to ask the right questions — that's the bet.

---

## Install

```bash
pip install model-world-sme
```

From source:

```bash
git clone https://github.com/RichardClawson013/ModelWorldSME
cd ModelWorldSME
pip install -e .
```

---

## Quick start

```python
from model_world_sme import InterviewFlow, default_worldmodel_path

flow = InterviewFlow(worldmodel_path=default_worldmodel_path())

question = flow.next()
while question:
    print(question)
    answer = input("> ")
    question = flow.next(answer)

result = flow.export()
# result.worldmodel_json    → load into your agent
# result.agent_config_yaml  → autonomy and escalation rules
# result.soul_md            → agent identity file
# result.html_report        → open in browser, print to PDF
```

Or just run it:

```bash
python examples/terminal_example.py
```

---

## Plug in your AI provider

```python
from model_world_sme.adapters import AnthropicDriver, OpenAIDriver, OllamaDriver, GoogleDriver, MistralDriver

driver = AnthropicDriver(api_key="...", model="claude-haiku-4-5-20251001")
driver = OpenAIDriver(api_key="...", model="gpt-4o-mini")
driver = OllamaDriver(model="llama3.2")           # local, no API key needed
driver = GoogleDriver(api_key="...", model="gemini-2.5-flash")
driver = MistralDriver(api_key="...", model="mistral-small-latest")
```

---

## Plug in your delivery channel

```python
from model_world_sme.orchestrators import HermesOrchestrator, LangChainOrchestrator, BaseOrchestrator

orchestrator = HermesOrchestrator(send=ctx.send_message, receive=ctx.receive_message)
orchestrator = LangChainOrchestrator(chain=my_chain.invoke)

class MyOrchestrator(BaseOrchestrator):
    async def send(self, message: str) -> str:
        ...
```

---

## Tests

```bash
python tests/test_core.py
```

---

## License

Apache 2.0 — see [LICENSE](LICENSE).

---

## Credits

**Research foundations**
- Klein, G.A. (1989). *Recognition-primed decisions.* Advances in Man-Machine Systems Research.
- Kelly, G.A. (1955). *The Psychology of Personal Constructs.* Norton.
- Beyer, H. & Holtzblatt, K. (1997). *Contextual Design.* Morgan Kaufmann.
- Crandall, B., Klein, G. & Hoffman, R.R. (2006). *Working Minds.* MIT Press.
- LeCun, Y. (2022). *A Path Towards Autonomous Machine Intelligence.*

**Open-source inspiration**
- [Graphiti](https://github.com/getzep/graphiti) by Zep (Apache 2.0) — causal structure and time-awareness in knowledge graphs
- Carriero et al. (2025). *Procedural Knowledge Ontology.* ESWC. CC-BY-4.0.

**Reference data**
- [O*NET](https://www.onetcenter.org/) — U.S. Dept of Labor. Public domain.
- [ESCO](https://esco.ec.europa.eu/) — European Commission.
