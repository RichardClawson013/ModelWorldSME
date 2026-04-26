# ModelWorldSME

[![CI](https://github.com/RichardClawson013/ModelWorldSME/actions/workflows/ci.yml/badge.svg)](https://github.com/RichardClawson013/ModelWorldSME/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/model-world-sme)](https://pypi.org/project/model-world-sme/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/model-world-sme)](https://pypi.org/project/model-world-sme/)

> Interview a business owner. Build a world model. Give their agent something to actually work with.

**[Try it live →](https://richardclawson013.github.io/ModelWorldSME/)**

![ModelWorldSME demo](docs/demo.gif)

---

## The problem

O*NET describes 1,400 occupations. ESCO maps 3,000 European roles. Osterwalder's Business Model Canvas fits a company onto one page. None of them tell you what the invoice looks like for *this* painting company, why it has to go out the same day the job finishes, or what happened the one time it didn't.

That knowledge lives inside the person who built the business. It is procedural, tacit, and invisible to any model trained on general text.

LeCun (2022) argues that intelligent agents need a *world model* — an internal representation of how things work, how they connect, and what happens when they go wrong. An agent operating without one is guessing. It may guess well most of the time. It will fail exactly when the consequences are highest.

ModelWorldSME builds that world model from a single conversation.

---

## How it works

One interview. No task grids. No checkboxes. No jargon.

The method is grounded in forty years of cognitive task analysis research:

| Technique | Source | What it surfaces |
|---|---|---|
| **Critical Decision Method** | Klein, 1989 | Tacit expertise through incident reconstruction |
| **Laddering** | Kelly, 1955 | Three layers per task — practice → consequence → value |
| **Exception probing** | Beyer & Holtzblatt, 1997 | Failure conditions from lived experience |

Matching runs silently in the background. The owner never sees a task ID.

---

## Demo

```
============================================================
ModelWorldSME — Business Elicitation Interview
============================================================

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
  Meanwhile two crews were waiting on a material order I forgot to place.

Walk me through a client call about an invoice from six weeks ago
step by step — from when you first noticed something was off to
how it ended.

> Started with the client calling angry. I checked my sent folder,
  saw the wrong address immediately. Resent it, apologised, offered
  a small discount. Client paid within the hour. But by then the
  material order had been sitting for three hours.

Let's talk about Create invoice. When that goes well, what does
it actually look like in practice?

> I send it the same day the job finishes, PDF to the client,
  copy to my own folder. Usually paid within two weeks.

You said I send it the same day the job finishes. Why does
getting that right matter to you?

> Cash flow. We're a small operation — if three invoices slip
  a week, I'm covering wages out of my own pocket.

And why does cash flow matter — what's actually at stake if it slips?

> I've had to delay payroll once. Never again. That's the line.

You said I've had to delay payroll once. Tell me about a time
Create invoice didn't go that way — when it went wrong, or when
you had to handle it completely differently than usual.

> Besides the obvious? Sometimes a client disputes the amount.
  Then I have to pull the original quote, the change orders,
  everything. Takes half a day and kills the week.

...

Last question: if your assistant could handle things on its own —
what would you want it to do without asking, and what should it
always check with you first?

> Send reminders for unpaid invoices, definitely. Quotes it can
  draft but I always review before sending. Payroll — never touch
  that without me.

============================================================
Interview complete. Generating outputs...
  Tasks confirmed: 23
  Agent name:      Nova
  Saved to:        output/
```

---

## What it produces

```
Interview (conversation)
        ↓
worldmodel_Nova.json      ← what the business does (personalized from 2,986-task knowledge base)
agent_config_Nova.yaml    ← how Nova behaves in that world
SOUL_Nova.md              ← who Nova is
report_Nova.html          ← risk, autonomy, and opportunity analysis (print to PDF)
```

The agent name chosen during the interview is **permanent** — it appears in all output files and in every message the agent sends on the owner's behalf.

---

## Install

```bash
pip install model-world-sme
```

Or from source:

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

question = flow.next()          # first question, no answer yet
while question:
    print(question)
    answer = input("> ")
    question = flow.next(answer)

result = flow.export()
print(result.agent_config_yaml)
# result.html_report  ← write to file and open in browser to print PDF
```

Or run the terminal example directly:

```bash
python examples/terminal_example.py
```

---

## Interview phases

```
Phase 0   — Business narrative    "Tell me about your business..."
Phase 0b  — Agent name            Permanent. Appears in all output.
Phase 1   — Critical incident     CDM: "Tell me about a day that didn't go well..."
            CDM follow-ups        5 probes, each referencing what was just said
Phase 2   — Domain confirmation   References actual task names found in the narrative
Phase 3   — Laddering             3 layers per top-risk task, following their own words
            Exception probing     "When does this go wrong?" — tied to their laddering answers
Phase 4   — Custom tasks          "Anything we haven't covered?"
Phase 5   — Autonomy mapping      One question: what can the agent handle alone vs. ask first?
```

Every question is built from the previous answer. CDM probes reference the incident the owner described. Laddering quotes their own words. Exception probing surfaces failure conditions from lived experience. None of it is scripted — it follows the conversation.

---

## Output format

### worldmodel.json
```json
{
  "schema_version": "1.5-custom",
  "_meta": {
    "agent_name": "Nova",
    "method": "CDM+Laddering+ExceptionProbing"
  },
  "tasks": [ "...confirmed tasks only, with laddering answers embedded..." ]
}
```

### agent_config.yaml
```yaml
agent:
  name: "Nova"
  name_permanent: true

autonomy:
  autonomous:
    - "Send payment reminder"
  ask_first:
    - "Send quote to client"

escalation:
  - task: "Process payment"
    trigger: "Amount above 500"
```

### SOUL.md
A Markdown identity file — pre-filled from interview answers, ready to extend.

### report.html
A printable business analysis report covering risk tiers, autonomy breakdown, opportunity sizing, and compliance. Open in any browser and print to PDF.

---

## Plug in your provider

```python
from model_world_sme.adapters import AnthropicDriver, OpenAIDriver, OllamaDriver, GoogleDriver, MistralDriver

# Anthropic
driver = AnthropicDriver(api_key="...", model="claude-haiku-4-5-20251001")

# OpenAI (or any OpenAI-compatible endpoint)
driver = OpenAIDriver(api_key="...", model="gpt-4o-mini")

# Local (Ollama — no API key)
driver = OllamaDriver(model="llama3.2")

# Google Gemini
driver = GoogleDriver(api_key="...", model="gemini-2.5-flash")

# Mistral
driver = MistralDriver(api_key="...", model="mistral-small-latest")
```

---

## Plug in your orchestrator

```python
from model_world_sme.orchestrators import HermesOrchestrator, LangChainOrchestrator

# Hermes (Nous Foundation)
orchestrator = HermesOrchestrator(send=ctx.send_message, receive=ctx.receive_message)

# LangChain
orchestrator = LangChainOrchestrator(chain=my_chain.invoke)

# Build your own — implement one method:
from model_world_sme.orchestrators import BaseOrchestrator

class MyOrchestrator(BaseOrchestrator):
    async def send(self, message: str) -> str:
        # deliver message to user, return their reply
        ...
```

---

## World model

The knowledge base (`worldmodel/sme_worldmodel_v1.5.json`) contains **2,986 SME tasks** across 10 domains:

| Domain | Label |
|---|---|
| D-FIN | Finance & Administration |
| D-SAL | Sales |
| D-KLA | Customer Service |
| D-MKT | Marketing |
| D-HRM | People & HR |
| D-OPS | Operations |
| D-DEL | Logistics & Delivery |
| D-ICT | IT & Systems |
| D-LEG | Legal & Compliance |
| D-STR | Strategy |

Tasks are connected by **16,281 causal edges** (upstream → downstream). Each task carries O*NET occupation codes, ESCO mappings, SBI 2025 sector codes, risk levels, and autonomy profiles.

---

## Run the tests

```bash
python tests/test_core.py
```

---

## License

Apache 2.0 — see [LICENSE](LICENSE).

---

## Credits

- **CDM methodology** — Klein, G.A. (1989). *Recognition-primed decisions.* Advances in Man-Machine Systems Research.
- **Laddering** — Kelly, G.A. (1955). *The Psychology of Personal Constructs.* Norton.
- **Exception probing** — Beyer, H. & Holtzblatt, K. (1997). *Contextual Design.* Morgan Kaufmann.
- **Triangulation** — Crandall, Klein & Hoffman (2006). *Working Minds.* MIT Press.
- **Procedural Knowledge Ontology** — Carriero et al. (2025). ESWC. CC-BY-4.0.
- **Temporal graph concept** — [Graphiti](https://github.com/getzep/graphiti) by Zep (Apache 2.0).
- **World model concept** — LeCun, Y. (2022). *A Path Towards Autonomous Machine Intelligence.*
- **O*NET** — U.S. Department of Labor. *Occupational Information Network.*
- **ESCO** — European Commission. *European Skills, Competences, Qualifications and Occupations.*
