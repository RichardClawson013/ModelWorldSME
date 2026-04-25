# ModelWorldSME

> One conversational interview. Three outputs. Any provider. Any model. Any orchestrator.

ModelWorldSME is an open-source library that turns a natural conversation with a business owner into a structured, personalized **world model** their AI agent can operate in.

No task grids. No checkboxes. No jargon. One question at a time — the matching happens invisibly in the background.

---

## What it produces

```
Interview (conversation)
        ↓
worldmodel_{name}.json      ← what the business does (2,928 task knowledge base)
agent_config_{name}.yaml    ← how the agent behaves in that world
SOUL_{name}.md              ← who the agent is
```

The agent name chosen during the interview is **permanent** — it appears in all output files and in every message the agent sends on the owner's behalf.

---

## Scientific basis

| Method | Source | Used for |
|---|---|---|
| Critical Decision Method (CDM) | Klein, 1989 | Incident-based narrative elicitation |
| Laddering | Kelly, 1955 | Three layers deep per task |
| Exception probing | Beyer & Holtzblatt, 1997 | "When does this go wrong?" |
| Causal graph mirroring | MKB WorldModel v1.5 | Upstream/downstream task suggestions |

Triangulation of methods improved validity in 15 of 23 studies (Crandall, Klein & Hoffman, 2006, *Working Minds*).

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
import asyncio
from model_world_sme import InterviewFlow
from model_world_sme.orchestrators import TerminalOrchestrator

async def main():
    flow = InterviewFlow(worldmodel_path="worldmodel/sme_worldmodel_v1.5.json")
    orchestrator = TerminalOrchestrator()

    async for question in flow.questions():
        answer = await orchestrator.send(question)
        flow.answer(answer)

    result = flow.export()
    print(result.agent_config_yaml)

asyncio.run(main())
```

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

## Interview flow

```
Phase 0  — Business narrative    "Tell me about your business..."
Phase 0b — Agent name            Permanent. Appears in all output.
Phase 1  — Critical incident     CDM: "Tell me about a day that didn't go well..."
           CDM follow-ups        4 probes (Klein, 1989)
Phase 2  — Domain confirmation   Plain-language per domain (no task names ever shown)
Phase 3  — Laddering             3 layers per top-risk task (Kelly, 1955)
           Exception probing     "When does this go wrong?" (Beyer & Holtzblatt, 1997)
Phase 4  — Custom tasks          "Anything we haven't covered?"
Phase 5  — Autonomy mapping      What can the agent handle alone vs. ask first?
```

---

## Output format

### worldmodel.json
```json
{
  "schema_version": "1.5-custom",
  "_meta": {
    "company_name": "...",
    "agent_name": "...",
    "method": "CDM+Laddering+ExceptionProbing"
  },
  "tasks": [ ... confirmed tasks only ... ]
}
```

### agent_config.yaml
```yaml
agent:
  name: "Aria"
  name_permanent: true
  name_appears_in_output: true

autonomy:
  autonomous:
    - "Send weekly report"
  ask_first:
    - "Send invoice above threshold"

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
