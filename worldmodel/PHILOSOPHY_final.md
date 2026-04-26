# Why ModelWorldSME exists

## It started with a practical problem

Every time I deployed an AI agent for a small business, the same thing happened. The agent could send emails. It could schedule things. It could look up information. What it couldn't do was operate in the business as if it understood how the business worked.

Not because the model was bad. Because nobody had told it anything real.

The owner had written a system prompt — a paragraph or two describing the business, maybe a list of things the agent should and shouldn't do. That's not a world model. That's a business card. An agent operating on a business card is guessing everything it doesn't explicitly know, and in a small business, that's most of what matters.

## The knowledge that never gets written down

The owner of a painting company knows that invoices go out the same day a job finishes. Not because it's in a policy document — there is no policy document. Because they've felt the alternative: cash runs thin, payroll gets tight, and once you've had to delay paying your crew, you change how you work.

That knowledge is real. It's operational. It determines behavior every single day. And it exists nowhere a system can read it.

The existing taxonomies don't help. O*NET, built by the US Department of Labor, describes over 19,000 tasks organized by occupation. It tells you what a bookkeeper does. It doesn't tell you what *this* bookkeeper does, why they do it in a specific order, what they're trying to avoid, or what breaks if they don't. ESCO, the European equivalent, covers 3,039 occupations across 28 languages — same gap, bigger vocabulary. Osterwalder's Business Model Canvas captures why a business exists and how it makes money. It says nothing about what people actually do between 8am and 6pm.

None of these systems were built to answer the question an agent needs answered: *can I safely do this task, what are the limits, and what happens downstream if I get it wrong?*

## Why conversation works

The knowledge that runs a business is layered. At the surface: what does the task look like in practice? Underneath: why does it matter? Deeper still: what's actually at stake?

You can't get to the bottom layer with a form. Forms produce surface-level answers. The owner describes their invoicing process the way they'd describe it to a new employee — clean, sequential, covering the normal case. What they don't include: the one time a client disputed a figure and it took half a day to reconstruct the original quote, the change orders, the whole paper trail. They don't include it because you didn't ask, and because it doesn't feel like a process — it feels like an exception.

Exceptions are where agents fail.

The techniques in this library come from forty years of cognitive task analysis — the field that studies how experts make decisions under pressure, not in ideal conditions. Klein's Critical Decision Method (1989) reconstructs incidents rather than routines. Kelly's laddering (1955) follows a person's own words three levels deep. Beyer and Holtzblatt's exception probing (1997) asks specifically about failure. Together, they surface the operational knowledge that a business owner couldn't have told you in a direct question, but absolutely can reconstruct when asked the right way.

## What comes out

Four files.

**The world model** — every task confirmed during the conversation, with the causal chains that connect them and the failure modes the owner described. Not a list of things a business like this might do. A map of what *this* business actually does, with the downstream consequences attached.

**The configuration** — what the agent can do without asking, what it needs approval for, what it should never touch. Specific thresholds. Exact escalation triggers. Built from what the owner said, not inferred from general principles.

**The identity file** — twelve sections, no placeholders. The owner's own words describing what good work looks like. The consequence they described when it slips. The deepest value at stake. The failure stories from experience. The communication style. The facts that carry across every session. Grounded in Constitutional AI (Bai et al. 2022): an identity document specific enough that you can predict the agent's behaviour on situations it has never explicitly encountered. Loaded at every session start.

**The report** — a printable analysis of the business: risk tiers by domain, automation opportunities, compliance gaps. Open in a browser, print to PDF.

The agent doesn't know everything. No agent does. But it knows what *this* business does, why it does it, where the lines are, and what happened the one time those lines got crossed. That's the difference between an agent that's useful and an agent that's a liability.

## The name

SME stands for Subject Matter Expert. It also stands for Small and Medium Enterprise. The interview extracts knowledge from the SME of the SME — the person who actually knows how the business works. That felt like the right frame.

## The honest part

This is v1. The matching is keyword-based and has gaps. The interview is deterministic where it should probably be adaptive. The knowledge base covers a lot but not everything. There are businesses where this produces something immediately useful and businesses where it produces a reasonable starting point that needs refinement.

The core idea — that agents need a model of the domain they operate in, and that the best way to build one is a structured conversation with the person who holds the knowledge — I believe that's right. The execution will get better.

---

*ModelWorldSME is open source under Apache 2.0.*
*Built by RichardClawson013. Grounded in four decades of cognitive task analysis research.*
