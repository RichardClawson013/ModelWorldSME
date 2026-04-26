"""
core/report.py — HTML business analysis report from interview data.

Produces a single self-contained HTML file the owner can open in any browser
and print to PDF. Covers: confirmed tasks by domain, risk analysis, autonomy
breakdown, causal highlights, compliance, and opportunity sizing.
"""

from __future__ import annotations
from datetime import date
from typing import Any

from .export import DOMAIN_LABELS


def build_html_report(
    model: dict[str, Any],
    confirmed_ids: set[str],
) -> str:
    """Return a self-contained HTML report as a string."""
    meta       = model.get("_meta", {})
    agent_name = meta.get("agent_name", "Your Assistant")
    company    = meta.get("company_name", "Your Business")
    today      = meta.get("generated_on", date.today().isoformat())

    confirmed = [t for t in model.get("tasks", []) if t["id"] in confirmed_ids or t.get("custom")]

    by_domain: dict[str, int] = {}
    for t in confirmed:
        d = t.get("domain", "?")
        by_domain[d] = by_domain.get(d, 0) + 1

    critical = [t for t in confirmed if t.get("failure", {}).get("risk_level") == "critical"]
    high     = [t for t in confirmed if t.get("failure", {}).get("risk_level") == "high"]
    medium   = [t for t in confirmed if t.get("failure", {}).get("risk_level") == "medium"]

    autonomous = [t for t in confirmed if t.get("agent_profile", {}).get("automatable") == "autonomous"]
    notify     = [t for t in confirmed if t.get("agent_profile", {}).get("automatable") == "notify"]
    ask_first  = [t for t in confirmed if t.get("agent_profile", {}).get("automatable") == "ask_first"]
    human_only = [t for t in confirmed if t.get("agent_profile", {}).get("automatable") == "human_only"]
    compliance = [t for t in confirmed if t.get("domain") == "D-LEG"]

    est_hours_week = round(len(autonomous) * 1.5 + len(notify) * 0.5)
    est_hours_year = est_hours_week * 50

    def task_list(tasks: list[dict[str, Any]], max_n: int = 20) -> str:
        rows = []
        for t in tasks[:max_n]:
            name = t.get("name_en") or t.get("name") or t["id"]
            rows.append(f"<li>{name}</li>")
        return "".join(rows)

    domain_rows = "".join(
        f"<tr><td>{DOMAIN_LABELS.get(d, d)}</td><td>{d}</td><td><strong>{n}</strong></td></tr>"
        for d, n in sorted(by_domain.items(), key=lambda x: -x[1])
    )

    def section(header: str, items: list[dict[str, Any]], css_class: str) -> str:
        if not items:
            return ""
        return (
            f'<h3><span class="{css_class}">● {header}</span> ({len(items)})</h3>'
            f"<ul>{task_list(items)}</ul>"
        )

    critical_warning = ""
    if critical:
        critical_warning = (
            f'<div class="section-note">'
            f"⚠️ <strong>{len(critical)} critical-risk task{'s' if len(critical) > 1 else ''}</strong> identified. "
            f"These are the tasks most likely to cause serious business harm if they fail.</div>"
        )

    compliance_section = ""
    if compliance:
        compliance_section = f"""
<h2>Compliance</h2>
<p>{len(compliance)} compliance-relevant task{'s' if len(compliance) > 1 else ''} confirmed.</p>
<ul>{task_list(compliance)}</ul>
<div class="section-note">
  {agent_name} should apply ask_first or human_only autonomy levels to all compliance tasks
  unless the owner has explicitly confirmed otherwise.
</div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<title>Business World Model Report — {company}</title>
<style>
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    max-width: 860px; margin: 0 auto; padding: 40px 24px;
    color: #1a1d27; line-height: 1.6;
  }}
  h1 {{ font-size: 2rem; font-weight: 800; margin-bottom: 4px; }}
  h2 {{
    font-size: 1.25rem; font-weight: 700;
    border-bottom: 2px solid #e5e7eb; padding-bottom: 6px;
    margin: 36px 0 16px; color: #3a6fd8;
  }}
  h3 {{ font-size: 1rem; font-weight: 600; margin: 20px 0 8px; }}
  .meta {{ color: #6b7280; font-size: 0.875rem; margin-bottom: 32px; }}
  .kpi-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 12px; margin-bottom: 32px;
  }}
  .kpi {{ background: #f3f6ff; border-radius: 10px; padding: 16px; text-align: center; }}
  .kpi-num {{ font-size: 2.5rem; font-weight: 800; color: #3a6fd8; line-height: 1; }}
  .kpi-label {{ font-size: 0.72rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 4px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
  th {{ text-align: left; padding: 8px 12px; background: #f3f6ff; color: #374151; }}
  td {{ padding: 8px 12px; border-bottom: 1px solid #e5e7eb; }}
  ul {{ padding-left: 20px; margin: 0; }}
  li {{ padding: 3px 0; font-size: 0.9rem; }}
  .risk-critical {{ color: #dc2626; font-weight: 700; }}
  .risk-high     {{ color: #d97706; font-weight: 600; }}
  .risk-medium   {{ color: #0ea5e9; }}
  .section-note {{
    background: #f9fafb; border-left: 3px solid #3a6fd8;
    padding: 12px 16px; font-size: 0.875rem; color: #374151;
    border-radius: 0 6px 6px 0; margin: 12px 0;
  }}
  .opportunity-box {{
    background: #f0fdf4; border: 1px solid #bbf7d0;
    border-radius: 8px; padding: 16px; margin: 12px 0;
  }}
  .opportunity-box strong {{ color: #166534; }}
  footer {{
    margin-top: 60px; padding-top: 20px;
    border-top: 1px solid #e5e7eb;
    font-size: 0.8rem; color: #9ca3af;
  }}
  @media print {{ body {{ padding: 20px; }} }}
</style>
</head>
<body>

<h1>Business World Model</h1>
<div class="meta">
  Generated for <strong>{company}</strong> · Agent: <strong>{agent_name}</strong> · {today}<br/>
  Method: CDM + Laddering + Exception Probing · ModelWorldSME v1.0
</div>

<div class="kpi-grid">
  <div class="kpi"><div class="kpi-num">{len(confirmed)}</div><div class="kpi-label">Tasks confirmed</div></div>
  <div class="kpi"><div class="kpi-num">{len(autonomous)}</div><div class="kpi-label">Fully autonomous</div></div>
  <div class="kpi"><div class="kpi-num">{len(critical) + len(high)}</div><div class="kpi-label">High-risk tasks</div></div>
  <div class="kpi"><div class="kpi-num">{len(by_domain)}</div><div class="kpi-label">Business domains</div></div>
  <div class="kpi"><div class="kpi-num">~{est_hours_week}h</div><div class="kpi-label">Automatable / week</div></div>
</div>

<h2>Executive Summary</h2>
<p>
  This report captures the business operations of <strong>{company}</strong> as elicited through a structured
  interview combining Critical Decision Method (Klein, 1989), Laddering (Kelly, 1955), and Exception Probing
  (Beyer &amp; Holtzblatt, 1997).
</p>
<p style="margin-top:10px">
  The interview confirmed <strong>{len(confirmed)} tasks</strong> across
  <strong>{len(by_domain)} business domains</strong>.
  Based on the autonomy mapping, <strong>{agent_name}</strong> can handle approximately
  <strong>{est_hours_week} hours of work per week</strong> without human intervention —
  roughly <strong>{est_hours_year} hours per year</strong>.
</p>
{critical_warning}

<h2>Tasks by Domain</h2>
<table>
  <thead><tr><th>Domain</th><th>Code</th><th>Tasks confirmed</th></tr></thead>
  <tbody>{domain_rows or "<tr><td colspan='3'>No tasks confirmed</td></tr>"}</tbody>
</table>

<h2>Risk Analysis</h2>
{section("Critical risk", critical, "risk-critical")}
{section("High risk", high, "risk-high")}
{section("Medium risk", medium, "risk-medium")}

<h2>Autonomy Mapping</h2>
<p>Based on the owner's answers during the interview:</p>
{section(f"Fully autonomous — {agent_name} acts without asking", autonomous, "risk-medium")}
{section(f"Act + notify — {agent_name} acts, then informs owner", notify, "risk-medium")}
{section("Ask first — agent asks permission before acting", ask_first, "risk-medium")}
{section("Human only — always handled by the owner", human_only, "risk-medium")}

<h2>Opportunity Analysis</h2>
<div class="opportunity-box">
  <strong>Time savings:</strong> With {len(autonomous)} autonomous tasks and {len(notify)} notify-only tasks,
  {agent_name} can save the business an estimated <strong>{est_hours_week} hours per week</strong>
  (~{est_hours_year} hours/year) in direct execution time.
</div>
<div class="opportunity-box">
  <strong>Risk reduction:</strong> {len(critical) + len(high)} high-priority tasks have been identified
  for proactive monitoring. Automating these with guardrails reduces the chance of costly failures.
</div>
<div class="opportunity-box">
  <strong>Knowledge capture:</strong> The interview surfaced tacit knowledge — including failure modes
  and exception conditions — that is now encoded in the world model. This knowledge persists even when
  people leave or roles change.
</div>
{compliance_section}

<h2>Output Files</h2>
<ul>
  <li><strong>worldmodel_{agent_name}.json</strong> — Personalized world model (confirmed tasks only)</li>
  <li><strong>agent_config_{agent_name}.yaml</strong> — Agent behaviour configuration</li>
  <li><strong>SOUL_{agent_name}.md</strong> — Agent identity file</li>
  <li><strong>report_{agent_name}.html</strong> — This report (print to PDF from your browser)</li>
</ul>

<h2>Scientific Basis</h2>
<ul>
  <li>Critical Decision Method — Klein, G.A. (1989). <em>Recognition-primed decisions.</em></li>
  <li>Laddering — Kelly, G.A. (1955). <em>The Psychology of Personal Constructs.</em></li>
  <li>Exception probing — Beyer, H. &amp; Holtzblatt, K. (1997). <em>Contextual Design.</em></li>
  <li>World model concept — LeCun, Y. (2022). <em>A Path Towards Autonomous Machine Intelligence.</em></li>
</ul>

<footer>
  Generated by <a href="https://github.com/RichardClawson013/ModelWorldSME">ModelWorldSME</a> v1.0 ·
  Apache 2.0 · {today}
</footer>
</body>
</html>"""
