# docs/index.html — Text changes only

These are the exact string replacements needed in docs/index.html.
Everything else (CSS, JS, logic) stays identical.

---

## 1. <title> tag (line 7)
CURRENT:
  ModelWorldSME — Business Elicitation Interview

REPLACE WITH:
  ModelWorldSME — Tell us about your business. We'll build the rest.

---

## 2. <meta name="description"> (line 6)
CURRENT:
  One interview. Three outputs. Give your AI agent a world it can actually operate in.

REPLACE WITH:
  Your agent doesn't know your business yet. One conversation fixes that.
  ModelWorldSME turns what's in your head into files your agent can actually use.

---

## 3. Header badge (line 198)
CURRENT:
  Live demo · no API key needed

REPLACE WITH:
  Live interview · runs in your browser · no signup

---

## 4. Loading message (line 192)
CURRENT:
  Loading knowledge base (2,986 tasks)…

REPLACE WITH:
  Getting ready (2,986 tasks, 16,281 connections)…

---

## 5. Results section title — find in JS around line 1100
CURRENT:
  Interview complete. Four files ready to download.

REPLACE WITH:
  Done. Here's what we built from your conversation.

---

## 6. Stat labels in finishInterview() — find around line 1110
CURRENT:
  Tasks confirmed
  Agent name

REPLACE WITH:
  Tasks mapped to your business
  Your agent's name

---

## 7. Download button descriptions — find in files[] array around line 1120
CURRENT:
  Confirmed tasks (JSON)
  Autonomy & escalation (YAML)
  Agent identity (Markdown)
  Risks & opportunities (HTML→PDF)

REPLACE WITH:
  Your business, mapped (JSON) — load this into your agent
  What the agent can do alone vs. ask you (YAML)
  Who the agent is — 12 sections from your own words (Markdown)
  Risk analysis, automation opportunities (open in browser → print PDF)

---

## 8. Error message (line 1152)
CURRENT:
  Could not load knowledge base

REPLACE WITH:
  Could not load the knowledge base

(No other change — the error detail and fallback instruction are fine as-is.)

---

## 9. Add a subtitle below the logo in the header
The header currently shows just the logo. Add this line immediately after the logo div:

  <p style="font-size:0.75rem;color:var(--muted);margin-top:3px;">
    Your business, mapped. Your agent, grounded.
  </p>

