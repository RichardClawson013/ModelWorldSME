"""
scripts/generate_demo_svg.py — Generate docs/demo.svg from hardcoded demo conversation.

Pure Python, no dependencies. Produces an animated terminal SVG that GitHub renders inline.
Run: python scripts/generate_demo_svg.py
"""

from pathlib import Path

# Hardcoded painting-company demo conversation
LINES = [
    ("q", "ModelWorldSME — Business Elicitation Interview"),
    ("sep", ""),
    ("q", "Tell me about your business. What do you do, and what does a typical day"),
    ("q", "look like for you?"),
    ("a", "> I run a small painting company. Five guys, mostly residential. My day"),
    ("a", "  is quotes, chasing invoices, and making sure the right crew is on site."),
    ("sep", ""),
    ("q", "Your assistant needs a name — one you'll use consistently. This name is"),
    ("q", "permanent: it will appear in emails, reports, and messages on your behalf."),
    ("a", "> Nova"),
    ("sep", ""),
    ("q", "Tell me about a day that didn't go well."),
    ("a", "> Client called angry about an invoice I'd sent to the wrong email six weeks"),
    ("a", "  ago. Two crews were waiting on a material order I'd forgotten to place."),
    ("sep", ""),
    ("q", "Walk me through that step by step — from when you first noticed something"),
    ("q", "was off to how it ended."),
    ("a", "> Checked my sent folder, saw the wrong address immediately. Resent it,"),
    ("a", "  apologised, offered a small discount. Client paid within the hour."),
    ("sep", ""),
    ("q", "Let's talk about Create invoice. When that goes well, what does it look like?"),
    ("a", "> I send it the same day the job finishes. PDF to the client, copy to my folder."),
    ("sep", ""),
    ("q", "You said I send it the same day. Why does getting that right matter to you?"),
    ("a", "> Cash flow. If three invoices slip a week I'm covering wages out of my pocket."),
    ("sep", ""),
    ("q", "And why does cash flow matter — what's actually at stake if it slips?"),
    ("a", "> I've had to delay payroll once. Never again. That's the line."),
    ("sep", ""),
    ("q", "Last question: what should your assistant do without asking, and what should"),
    ("q", "it always check with you first?"),
    ("a", "> Send reminders on its own. Quotes it can draft but I always review. Payroll"),
    ("a", "  — never without me."),
    ("sep", ""),
    ("ok", "Interview complete.  Tasks confirmed: 24  ·  Agent: Nova"),
    ("ok", "Outputs: worldmodel.json · agent_config.yaml · SOUL.md · report.html"),
]

# SVG config
WIDTH       = 860
LINE_H      = 19
FONT_SIZE   = 13
PADDING_X   = 22
PADDING_TOP = 48        # space for title bar
FRAME_DELAY = 0.18      # seconds between lines appearing

COLORS = {
    "bg":    "#1e1e2e",   # Catppuccin Mocha base
    "bar":   "#313244",   # surface 0
    "q":     "#cdd6f4",   # text
    "a":     "#89dceb",   # sky (cyan)
    "sep":   "#45475a",   # surface 1
    "ok":    "#a6e3a1",   # green
    "btn_r": "#f38ba8",
    "btn_y": "#f9e2af",
    "btn_g": "#a6e3a1",
    "dot":   "#6c7086",
    "font":  "\"JetBrains Mono\", \"Fira Code\", \"Cascadia Code\", Consolas, monospace",
}

visible = [l for l in LINES if l[0] != "sep"]
sep_count = sum(1 for l in LINES if l[0] == "sep")
total_content_lines = len(visible)

HEIGHT = PADDING_TOP + len(LINES) * LINE_H + 28


def build_svg() -> str:
    parts: list[str] = []

    # Header
    parts.append(f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}"
     width="{WIDTH}" height="{HEIGHT}" style="font-family:{COLORS['font']}">
  <defs>""")

    # Keyframe animations — each line fades in at its own time
    total_dur = len(LINES) * FRAME_DELAY + 2.0
    for i in range(len(LINES)):
        t_start = i * FRAME_DELAY
        t_pct   = (t_start / total_dur) * 100
        t_end   = ((t_start + 0.15) / total_dur) * 100
        parts.append(f"""    <style>
      #L{i} {{ opacity: 0; animation: fi{i} {total_dur:.1f}s linear infinite; }}
      @keyframes fi{i} {{
        0%        {{ opacity: 0; }}
        {t_pct:.1f}%  {{ opacity: 0; }}
        {t_end:.1f}%  {{ opacity: 1; }}
        97%       {{ opacity: 1; }}
        100%      {{ opacity: 0; }}
      }}
    </style>""")

    parts.append("  </defs>")

    # Window background
    parts.append(f"""  <rect width="{WIDTH}" height="{HEIGHT}" rx="10" fill="{COLORS['bg']}"/>""")

    # Title bar
    parts.append(f"""  <rect width="{WIDTH}" height="36" rx="10" fill="{COLORS['bar']}"/>
  <rect y="26" width="{WIDTH}" height="10" fill="{COLORS['bar']}"/>""")

    # Traffic light dots
    for xi, col in enumerate([COLORS['btn_r'], COLORS['btn_y'], COLORS['btn_g']]):
        parts.append(f"""  <circle cx="{14 + xi * 20}" cy="18" r="6" fill="{col}"/>""")

    # Title
    parts.append(f"""  <text x="{WIDTH//2}" y="23" text-anchor="middle" fill="{COLORS['dot']}" font-size="12" font-family={COLORS['font']}>ModelWorldSME</text>""")

    # Lines
    for i, (kind, text) in enumerate(LINES):
        y = PADDING_TOP + i * LINE_H + LINE_H - 4

        if kind == "sep":
            parts.append(
                f"""  <line id="L{i}" x1="{PADDING_X}" y1="{y - 4}" x2="{WIDTH - PADDING_X}" y2="{y - 4}" """
                f"""stroke="{COLORS['sep']}" stroke-width="0.5"/>"""
            )
        else:
            color = COLORS.get(kind, COLORS["q"])
            safe  = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            parts.append(
                f"""  <text id="L{i}" x="{PADDING_X}" y="{y}" fill="{color}" """
                f"""font-size="{FONT_SIZE}" xml:space="preserve">{safe}</text>"""
            )

    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    out = Path(__file__).parent.parent / "docs" / "demo.svg"
    out.parent.mkdir(exist_ok=True)
    svg = build_svg()
    out.write_text(svg, encoding="utf-8")
    print(f"Written: {out}  ({len(svg):,} bytes, {HEIGHT}px tall)")


if __name__ == "__main__":
    main()
