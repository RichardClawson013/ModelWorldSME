# ModelWorldSME

> One conversational interview. Three outputs. Any provider. Any model. Any orchestrator.

ModelWorldSME is an open-source library that turns a natural conversation with a business owner into a structured, personalized **world model** their AI agent can operate in.

No task grids. No checkboxes. No jargon. One question at a time — the matching happens invisibly in the background.

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
worldmodel_Nova.json      ← what the business does (2,928 task knowledge base)
agent_config_Nova.yaml    ← how Nova behaves in that world
SOUL_Nova.md              ← who Nova is
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
from model_world_sme import InterviewFlow

flow = InterviewFlow(worldmodel_path="worldmodel/sme_worldmodel_v1.5.json")

question = flow.next()          # first question, no answer yet
while question:
    print(question)
    answer = input("> ")
    question = flow.next(answer)

result = flow.export()
print(result.agent_config_yaml)
```

Or run the terminal example directly:

```bash
python examples/terminal_example.py
```

---

## How the interview works

The interview is **turn-based**: every question is built from the previous answer. There are no pre-written scripts — the CDM probes reference the incident the owner described, laddering follows their own words, and exception probing surfaces failure conditions from lived experience.

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

Matching runs silently in the background throughout — the owner never sees a task ID or domain code.

---

## Scientific basis

| Method | Source | Used for |
|---|---|---|
| Critical Decision Method (CDM) | Klein, 1989 | Incident-based narrative elicitation |
| Laddering | Kelly, 1955 | Three layers deep per task, following the owner's own words |
| Exception probing | Beyer & Holtzblatt, 1997 | "When does this go wrong?" |
| Causal graph mirroring | MKB WorldModel v1.5 | Upstream/downstream task suggestions |

Triangulation of methods improved validity in 15 of 23 studies (Crandall, Klein & Hoffman, 2006, *Working Minds*).

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

## Output format

### worldmodel.json
```json
{
  "schema_version": "1.5-custom",
  "_meta": {
    "company_name": "...",
    "agent_name": "Nova",
    "method": "CDM+Laddering+ExceptionProbing"
  },
  "tasks": [ ... confirmed tasks only ... ]
}
```

### agent_config.yaml
```yaml
agent:
  name: "Nova"
  name_permanent: true
  name_appears_in_output: true

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
A Markdown identity file for the agent — pre-filled from interview answers, ready to extend.

---

## World model

The knowledge base (`worldmodel/sme_worldmodel_v1.5.json`) contains **2,928 SME tasks** across 10 domains:

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

Tasks are connected by **16,281 causal edges** (upstream → downstream). The agent can traverse this graph to understand the ripple effects of any action before taking it.

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
- **Procedural Knowledge Ontology** — Carriero et al. (2025). ESWC. CC-BY-4.0.
- **Temporal graph concept** — [Graphiti](https://github.com/getzep/graphiti) by Zep (Apache 2.0).
- **World model concept** — inspired by LeCun, Y. (2022). *A Path Towards Autonomous Machine Intelligence.*
