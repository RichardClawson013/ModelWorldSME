# Why ModelWorldSME exists

## The problem with "AI for business"

Most business owners are told their AI agent needs a system prompt. So they write one — a paragraph describing who they are and what they want. The agent does something plausible. Things work until they don't.

What's missing is not better prompting. It's knowledge.

An AI agent acting in a business needs to understand *what that business actually does* — not at a marketing level, but at the task level. The tasks that run every week. The ones where failure costs money. The ones the owner handles differently on bad days. The edge cases that only exist because a client once called angry about an invoice from six weeks ago.

That knowledge lives in one place: inside the person who built the business. It is not in any database, not in O*NET, not in ESCO. Those are excellent references — covering 1,400+ occupations and 3,000+ European roles respectively — but they describe what work looks like on average, not what it looks like in this business, on this street, with these clients.

## The gap

Osterwalder's Business Model Canvas is the best single-page view of a business. It captures value propositions, key activities, revenue streams. What it does not capture is the procedural knowledge underneath — the sequence of decisions made when a quote becomes a job, when a job hits a complication, when a client disputes a figure at the end of a month that was already tight.

LeCun's "A Path Towards Autonomous Machine Intelligence" (2022) argues that any system aiming to act intelligently in the real world needs a world model — an internal representation of how things work, how they connect, and what happens when they go wrong. LLMs trained on text don't have this. They have *descriptions* of the world. That's different.

ModelWorldSME builds the world model that's missing.

## Why conversation, not forms

The owner of a painting company knows they need to invoice the same day a job finishes. They know this because cash flow — and behind cash flow, payroll, and behind payroll, the one time they had to delay it, which they will never forget.

You cannot surface that with a dropdown. The knowledge is layered: practice, consequence, value. It surfaces through conversation, through following the thread, through asking "why does that matter?" until you reach something that actually matters.

This is not an original observation. It is forty years of cognitive task analysis research:

- Klein's Critical Decision Method (1989) extracts tacit knowledge through incident reconstruction. Not "what do you normally do?" but "tell me about the day that went wrong."
- Kelly's laddering technique (1955) follows a person's own words, three levels deep. Practice → consequence → value. Each question quotes the previous answer.
- Beyer and Holtzblatt's exception probing (1997) asks not just how things go right, but how they go wrong. The failure conditions are where the tacit knowledge lives.

ModelWorldSME implements all three, linked together, in a single conversation.

## What comes out

Four files.

**The world model** — every task confirmed during the conversation, with the causal chains that connect them and the failure modes the owner described. Not a list of what a business like this might do. A map of what *this* business actually does, with downstream consequences attached.

**The configuration** — what the agent can do without asking, what it needs approval for, what it should never touch. Specific thresholds. Exact escalation triggers. Built from what the owner said, not inferred from general principles.

**The identity file — the SOUL** — twelve sections, no placeholders. The owner's own words on what good work looks like. The consequence they described when it slips. The deepest value at stake — "I've had to delay payroll once. Never again. That's the line." The failure stories from lived experience. The communication style. The hard limits. The facts that carry across every session. Grounded in Constitutional AI (Bai et al. 2022): an identity document specific enough that you can predict the agent's behaviour on situations it has never explicitly encountered. Injected at every session start.

**The report** — a printable analysis of the business: risk tiers by domain, automation opportunities, compliance gaps. Open in a browser, print to PDF.

The owner answered the questions. The outputs reflect that. The agent operates in a world it actually understands — including the parts the owner has never written down.

## The name

A "Subject Matter Expert" (SME) is the person who holds the knowledge. The acronym also happens to describe the businesses in scope: small and medium enterprises. The interview extracts knowledge from the SME of the SME. That felt right.

---

*ModelWorldSME is open source under Apache 2.0.*
*Built by RichardClawson013. Grounded in four decades of cognitive task analysis research.*
