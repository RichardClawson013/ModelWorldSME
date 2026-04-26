"""
scripts/generate_demo_gif.py — Generate animated demo GIF from real interview.

Layout:
  - Fixed 900×540 terminal frame throughout.
  - Interview phase: scrolling window (last N lines visible).
  - Output phase: each file shown as a full static page, held for several seconds.

Output: docs/media/demo.gif
"""

from __future__ import annotations
import re
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).parent.parent

# ── Font ──────────────────────────────────────────────────────────────────────

FONT_CANDIDATES = [
    "/mnt/c/Windows/Fonts/consola.ttf",
    "/mnt/c/Windows/Fonts/CascadiaMono.ttf",
    "/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf",
]

def _load_font(size: int):
    from PIL import ImageFont
    for path in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            pass
    return ImageFont.load_default()


# ── Colours ───────────────────────────────────────────────────────────────────

BG      = (18,  18,  24)
FG      = (210, 210, 210)
ANSWER  = (100, 210,  90)
HEADER  = (255, 195,  60)
OUTPUT  = ( 90, 175, 255)
DIM     = (100, 100, 110)


# ── Canvas ────────────────────────────────────────────────────────────────────

W          = 900
H          = 540
FONT_SIZE  = 14
PAD_X      = 24
PAD_TOP    = 20
LINE_H     = FONT_SIZE + 8
WRAP_W     = 74    # chars per line at font size 14 on 900px
MAX_SCROLL = (H - PAD_TOP * 2) // LINE_H   # lines that fit


# ── ANSI ──────────────────────────────────────────────────────────────────────

_ANSI = re.compile(r"\x1b\[[0-9;]*m")

def strip_ansi(s: str) -> str:
    return _ANSI.sub("", s)


# ── Classification ────────────────────────────────────────────────────────────

def classify(raw: str) -> tuple[str, str]:
    s = strip_ansi(raw)
    if s.startswith("> "):
        return "answer", s[2:]
    if s.strip().startswith("====") or s.strip().startswith("  Tasks") or s.strip().startswith("  Agent") or s.strip().startswith("  Saved"):
        return "header", s
    if s.strip().startswith("──"):
        return "section", s
    if not s.strip():
        return "blank", ""
    return "question", s


def colour_for(t: str) -> tuple:
    return {"question": FG, "answer": ANSWER, "header": HEADER,
            "section": HEADER, "blank": BG, "output": OUTPUT,
            "dim": DIM}.get(t, FG)


# ── Capture ───────────────────────────────────────────────────────────────────

def capture() -> list[str]:
    env = {**__import__("os").environ, "PYTHONPATH": str(ROOT)}
    r = subprocess.run(
        [sys.executable, str(ROOT / "examples" / "demo_run.py")],
        capture_output=True, text=True, env=env, timeout=90,
    )
    return r.stdout.splitlines()


# ── Render helpers ────────────────────────────────────────────────────────────

def new_frame(font) -> tuple:
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    return img, draw


def quantize(img) -> "Image":
    return img.quantize(colors=24, method=2)


def draw_lines(draw, lines: list[tuple[str, str]], start_y: int = PAD_TOP) -> None:
    for i, (lt, text) in enumerate(lines):
        y = start_y + i * LINE_H
        if y > H:
            break
        draw.text((PAD_X, y), text, font=None, fill=colour_for(lt))


def draw_lines_font(draw, font, lines: list[tuple[str, str]], start_y: int = PAD_TOP) -> None:
    for i, (lt, text) in enumerate(lines):
        y = start_y + i * LINE_H
        if y > H:
            break
        draw.text((PAD_X, y), text, font=font, fill=colour_for(lt))


# ── Wrap a logical line into display sub-lines ────────────────────────────────

def wrap(lt: str, text: str) -> list[tuple[str, str]]:
    if lt == "blank":
        return [("blank", "")]
    display = ("> " + text) if lt == "answer" else text
    parts = textwrap.wrap(display, width=WRAP_W) or [display or ""]
    return [(lt, p) for p in parts]


# ── Build scrolling interview frames ──────────────────────────────────────────

def interview_frames(lines: list[tuple[str, str]], font) -> tuple[list, list[int]]:
    """One frame per logical line, scrolling window."""
    frames, durs = [], []
    visible: list[tuple[str, str]] = []
    skip_blank = True

    for lt, text in lines:
        if lt == "blank":
            if not skip_blank:
                visible.append(("blank", ""))
            continue
        skip_blank = False

        for sl, st in wrap(lt, text):
            visible.append((sl, st))

        window = visible[-MAX_SCROLL:]
        img, draw = new_frame(font)
        draw_lines_font(draw, font, window)
        frames.append(quantize(img))
        durs.append({"question": 220, "answer": 170, "header": 400, "section": 280}.get(lt, 150))

    return frames, durs


# ── Build static output page frames ──────────────────────────────────────────

def output_page_frames(sections: list[tuple[str, list[tuple[str, str]]]], font) -> tuple[list, list[int]]:
    """Each output file rendered as a full static page, held for 3.5s."""
    frames, durs = [], []

    for title, content_lines in sections:
        img, draw = new_frame(font)

        # Title bar
        draw.rectangle([(0, 0), (W, LINE_H + PAD_TOP)], fill=(30, 30, 40))
        draw.text((PAD_X, 6), title, font=font, fill=HEADER)

        # Content
        y = PAD_TOP + LINE_H + 8
        for lt, text in content_lines:
            if y > H - LINE_H:
                draw.text((PAD_X, y), "…", font=font, fill=DIM)
                break
            for sub_lt, sub in wrap(lt, text):
                draw.text((PAD_X, y), sub, font=font, fill=colour_for(sub_lt))
                y += LINE_H
                if y > H - LINE_H:
                    break

        frames.append(quantize(img))
        durs.append(3500)

    return frames, durs


# ── Split output lines into per-file sections ─────────────────────────────────

def split_output_sections(output_lines: list[tuple[str, str]]) -> list[tuple[str, list[tuple[str, str]]]]:
    """Group output lines by ── section headers."""
    sections: list[tuple[str, list]] = []
    current_title = "Output"
    current_lines: list[tuple[str, str]] = []

    for lt, text in output_lines:
        if lt == "section":
            if current_lines:
                sections.append((current_title, current_lines))
            current_title = strip_ansi(text).strip("─ \t")
            current_lines = []
        else:
            current_lines.append((lt, text))

    if current_lines:
        sections.append((current_title, current_lines))

    return [s for s in sections if s[1]]  # drop empty


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("Capturing real interview output…")
    raw = capture()
    print(f"  {len(raw)} lines captured")

    classified = [classify(line) for line in raw]

    # Split at "Interview complete"
    split = next(
        (i for i, (_, t) in enumerate(classified) if "Interview complete" in t),
        len(classified),
    )
    interview = classified[:split]
    output_raw = classified[split:]

    # Reclassify output content lines as "output" colour
    output = []
    for lt, text in output_raw:
        if lt == "question":
            lt = "output"
        output.append((lt, text))

    font = _load_font(FONT_SIZE)

    print("Building interview frames…")
    i_frames, i_durs = interview_frames(interview, font)
    print(f"  {len(i_frames)} interview frames")

    sections = split_output_sections(output)
    print(f"  {len(sections)} output sections: {[s[0][:30] for s in sections]}")

    print("Building output page frames…")
    o_frames, o_durs = output_page_frames(sections, font)
    print(f"  {len(o_frames)} output frames")

    all_frames = i_frames + o_frames
    all_durs   = i_durs   + o_durs

    # Hold very last frame longer
    if all_durs:
        all_durs[-1] = 5000

    out = ROOT / "docs" / "media" / "demo.gif"
    out.parent.mkdir(parents=True, exist_ok=True)

    all_frames[0].save(
        out,
        save_all=True,
        append_images=all_frames[1:],
        duration=all_durs,
        loop=0,
        optimize=False,
    )
    kb = out.stat().st_size // 1024
    print(f"\nSaved {out}\n  {kb} KB · {len(all_frames)} frames")


if __name__ == "__main__":
    main()
