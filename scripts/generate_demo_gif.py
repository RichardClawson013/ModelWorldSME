"""
scripts/generate_demo_gif.py
Generate docs/media/demo.gif — animated terminal recording of the interview.

Requirements: pip install Pillow
Run:          python scripts/generate_demo_gif.py
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ── Conversation to display ───────────────────────────────────
CONVO = [
    ("sys", "ModelWorldSME — Business Elicitation Interview"),
    ("sys", "=" * 58),
    ("q",   "Tell me about your business. What do you do, and what"),
    ("q",   "does a typical day look like for you?"),
    ("a",   "> I run a small painting company. Five guys, mostly"),
    ("a",   "  residential. Quotes, invoices, right crew on site."),
    ("q",   "Your assistant needs a name — one you'll use"),
    ("q",   "consistently. It will appear in all output. Name?"),
    ("a",   "> Nova"),
    ("q",   "Tell me about a day that didn't go well."),
    ("a",   "> Client called angry — invoice sent to wrong email."),
    ("a",   "  Two crews waiting on an order I forgot to place."),
    ("q",   "Walk me through that step by step."),
    ("a",   "> Checked sent folder, wrong address. Resent it,"),
    ("a",   "  apologised. Client paid within the hour."),
    ("q",   "Let's talk about Create invoice. When it goes well,"),
    ("q",   "what does it actually look like?"),
    ("a",   "> Same day the job finishes. PDF to client, copy to"),
    ("a",   "  my folder. Paid within two weeks."),
    ("q",   "You said same day. Why does that matter to you?"),
    ("a",   "> Cash flow. Three invoices slip — I cover wages"),
    ("a",   "  out of my own pocket."),
    ("q",   "And why does cash flow matter — what's at stake?"),
    ("a",   "> I've had to delay payroll once. Never again."),
    ("q",   "Last question: what can your assistant do without"),
    ("q",   "asking, and what must it always check with you first?"),
    ("a",   "> Send reminders on its own. Quotes it can draft but"),
    ("a",   "  I always review. Payroll — never without me."),
    ("sys", ""),
    ("ok",  "Interview complete."),
    ("ok",  "Tasks confirmed: 24   Agent: Nova"),
    ("ok",  "Outputs: worldmodel · agent_config · SOUL · report"),
]

# ── Visual config ─────────────────────────────────────────────
W, H      = 820, 460
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_SIZE = 13
LINE_H    = 20
PAD_X     = 18
PAD_Y     = 48          # below title bar
MAX_LINES = (H - PAD_Y - 12) // LINE_H   # lines that fit

BG        = (22, 22, 35)
BAR       = (40, 42, 60)
C_SYS     = (140, 140, 170)
C_Q       = (200, 210, 240)
C_A       = (100, 210, 220)
C_OK      = (140, 220, 140)
C_DOT_R   = (255, 95,  87)
C_DOT_Y   = (255, 189, 46)
C_DOT_G   = (40,  201, 64)
C_TITLE   = (120, 120, 150)

FRAME_MS  = 180     # ms per frame (new line appears)
PAUSE_MS  = 2800    # ms on final frame


def color_for(kind: str):
    return {"sys": C_SYS, "q": C_Q, "a": C_A, "ok": C_OK}.get(kind, C_Q)


def make_frame(visible_lines: list[tuple[str, str]], font: ImageFont.FreeTypeFont,
               cursor: bool = False) -> Image.Image:
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Title bar
    draw.rectangle([0, 0, W, 36], fill=BAR)
    for i, col in enumerate([C_DOT_R, C_DOT_Y, C_DOT_G]):
        draw.ellipse([12 + i*20 - 5, 18 - 5, 12 + i*20 + 5, 18 + 5], fill=col)
    draw.text((W // 2, 10), "ModelWorldSME", font=font, fill=C_TITLE, anchor="mt")

    # Lines (show last MAX_LINES)
    shown = visible_lines[-MAX_LINES:]
    for row, (kind, text) in enumerate(shown):
        y = PAD_Y + row * LINE_H
        draw.text((PAD_X, y), text, font=font, fill=color_for(kind))

    # Blinking cursor (on last line)
    if cursor and shown:
        last_row = len(shown) - 1
        y = PAD_Y + last_row * LINE_H
        cx = PAD_X + (len(shown[-1][1]) + 1) * 8
        draw.rectangle([cx, y + 2, cx + 7, y + LINE_H - 2], fill=C_Q)

    return img


def main() -> None:
    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except Exception:
        font = ImageFont.load_default()
        print("Warning: using default bitmap font — DejaVuSansMono.ttf not found")

    frames: list[Image.Image] = []
    durations: list[int]      = []

    visible: list[tuple[str, str]] = []

    for i, (kind, text) in enumerate(CONVO):
        visible.append((kind, text))
        is_last = (i == len(CONVO) - 1)

        frame = make_frame(visible, font, cursor=not is_last)
        frames.append(frame)
        durations.append(PAUSE_MS if is_last else FRAME_MS)

    # Save
    out = Path(__file__).parent.parent / "docs" / "media" / "demo.gif"
    out.parent.mkdir(parents=True, exist_ok=True)

    frames[0].save(
        out,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,                 # loop forever
        optimize=False,
    )

    size_kb = out.stat().st_size // 1024
    print(f"Saved: {out}  ({size_kb} KB, {len(frames)} frames)")


if __name__ == "__main__":
    main()
