"""
scripts/generate_demo_gif.py — Generate animated demo GIF from real interview.

Runs demo_run.py, captures real output, renders terminal-style animated GIF.
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
    "/mnt/c/Windows/Fonts/consola.ttf",       # Consolas (Windows)
    "/mnt/c/Windows/Fonts/CascadiaMono.ttf",  # Cascadia Mono (Windows)
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


# ── Terminal colours ──────────────────────────────────────────────────────────

BG       = (18,  18,  24)      # near-black
FG       = (220, 220, 220)     # main text
CYAN     = (97,  214, 214)     # question colour (matches demo_run.py cyan)
PROMPT   = (97,  214, 214)     # "> " prefix
ANSWER   = (160, 230, 120)     # answer text (green tint)
HEADER   = (255, 200,  80)     # === lines and summary


# ── ANSI strip ────────────────────────────────────────────────────────────────

_ANSI_ESC = re.compile(r"\x1b\[[0-9;]*m")

def strip_ansi(text: str) -> str:
    return _ANSI_ESC.sub("", text)


# ── Classify lines ────────────────────────────────────────────────────────────

def classify(raw: str) -> tuple[str, str]:
    """Return (type, clean_text) for a raw output line."""
    clean = strip_ansi(raw)
    if clean.startswith("> "):
        return "answer", clean[2:]
    if clean.startswith("===") or clean.startswith("  Tasks") or clean.startswith("  Agent"):
        return "header", clean
    if clean.strip() == "":
        return "blank", ""
    return "question", clean


# ── Capture demo output ───────────────────────────────────────────────────────

def capture_demo() -> list[str]:
    result = subprocess.run(
        [sys.executable, str(ROOT / "examples" / "demo_run.py")],
        capture_output=True,
        text=True,
        env={**__import__("os").environ, "PYTHONPATH": str(ROOT)},
        timeout=60,
    )
    return result.stdout.splitlines()


# ── Select interesting lines for GIF ─────────────────────────────────────────

def select_lines(raw_lines: list[str]) -> list[tuple[str, str]]:
    """
    Pick the most representative lines: skip most domain-confirm exchanges,
    keep intro, CDM incident+first probe, two laddering sequences, summary.
    Returns list of (type, text) tuples.
    """
    classified = [classify(line) for line in raw_lines]

    # Find key indices
    question_indices = [i for i, (t, _) in enumerate(classified) if t == "question"]
    answer_indices   = [i for i, (t, _) in enumerate(classified) if t == "answer"]

    selected: list[tuple[str, str]] = []

    # Header (===)
    for i, (t, txt) in enumerate(classified):
        if t == "header" and "===" in txt and i < 3:
            selected.append((t, txt))

    # Q0 + A0: business narrative
    if len(question_indices) > 0:
        qi = question_indices[0]
        selected.append(("blank", ""))
        selected.append(classified[qi])
        if qi + 1 < len(classified) and classified[qi + 1][0] == "answer":
            selected.append(classified[qi + 1])

    # Q1 + A1: agent name
    if len(question_indices) > 1:
        qi = question_indices[1]
        selected.append(("blank", ""))
        selected.append(classified[qi])
        if qi + 1 < len(classified) and classified[qi + 1][0] == "answer":
            selected.append(classified[qi + 1])

    # Q2 + A2: CDM incident
    if len(question_indices) > 2:
        qi = question_indices[2]
        selected.append(("blank", ""))
        selected.append(classified[qi])
        if qi + 1 < len(classified) and classified[qi + 1][0] == "answer":
            selected.append(classified[qi + 1])

    # Q3 + A3: first CDM probe
    if len(question_indices) > 3:
        qi = question_indices[3]
        selected.append(("blank", ""))
        selected.append(classified[qi])
        if qi + 1 < len(classified) and classified[qi + 1][0] == "answer":
            selected.append(classified[qi + 1])

    # First laddering sequence: 4 Q+A pairs starting from first "Let's talk about"
    laddering_start = None
    for i, (t, txt) in enumerate(classified):
        if t == "question" and "Let's talk about" in txt:
            laddering_start = i
            break

    if laddering_start is not None:
        selected.append(("blank", ""))
        count = 0
        i = laddering_start
        while i < len(classified) and count < 8:
            t, txt = classified[i]
            if t in ("question", "answer"):
                selected.append((t, txt))
                count += 1
            i += 1

    # Autonomy question + answer (second to last Q+A)
    if len(question_indices) >= 2:
        qi = question_indices[-2]   # autonomy question
        selected.append(("blank", ""))
        selected.append(classified[qi])
        if qi + 1 < len(classified) and classified[qi + 1][0] == "answer":
            selected.append(classified[qi + 1])

    # Summary lines
    selected.append(("blank", ""))
    for i, (t, txt) in enumerate(classified):
        if t == "header":
            selected.append((t, txt))

    return selected


# ── Render frames ─────────────────────────────────────────────────────────────

WIDTH      = 900
FONT_SIZE  = 15
PAD_X      = 24
PAD_TOP    = 20
LINE_H     = FONT_SIZE + 6
WRAP_WIDTH = 78     # characters


def wrap_line(text: str) -> list[str]:
    if not text.strip():
        return [""]
    return textwrap.wrap(text, width=WRAP_WIDTH) or [""]


def colour_for(line_type: str) -> tuple[int, int, int]:
    return {
        "question": FG,
        "answer":   ANSWER,
        "header":   HEADER,
        "blank":    FG,
    }.get(line_type, FG)


def build_frames(
    selected: list[tuple[str, str]],
    font,
) -> list:
    from PIL import Image, ImageDraw

    frames: list = []
    visible: list[tuple[str, str]] = []   # lines rendered so far

    for line_type, text in selected:
        if line_type == "answer":
            display_text = "> " + text
        else:
            display_text = text

        wrapped = wrap_line(display_text)

        for sub in wrapped:
            visible.append((line_type, sub))

        # Build one frame per new line added
        height = PAD_TOP * 2 + max(1, len(visible)) * LINE_H
        height = max(height, 400)

        img = Image.new("RGB", (WIDTH, height), BG)
        draw = ImageDraw.Draw(img)

        for li, (lt, lt_text) in enumerate(visible):
            y = PAD_TOP + li * LINE_H
            col = colour_for(lt)
            draw.text((PAD_X, y), lt_text, font=font, fill=col)

        # Crop to last ~30 lines (scrolling window)
        max_lines = 30
        if len(visible) > max_lines:
            crop_top = (len(visible) - max_lines) * LINE_H
            img = img.crop((0, crop_top, WIDTH, crop_top + max_lines * LINE_H + PAD_TOP * 2))
            img = img.resize((WIDTH, max_lines * LINE_H + PAD_TOP * 2), Image.LANCZOS)

        frames.append(img)

    return frames


def main() -> None:
    print("Capturing real interview output…")
    raw_lines = capture_demo()
    print(f"  Got {len(raw_lines)} lines")

    selected = select_lines(raw_lines)
    print(f"  Selected {len(selected)} lines for GIF")

    font = _load_font(FONT_SIZE)

    print("Rendering frames…")
    frames = build_frames(selected, font)
    print(f"  {len(frames)} frames")

    out = ROOT / "docs" / "media" / "demo.gif"
    out.parent.mkdir(parents=True, exist_ok=True)

    durations = []
    for i, (lt, _) in enumerate(selected):
        if lt == "question":
            durations.append(220)
        elif lt == "answer":
            durations.append(180)
        elif lt == "header":
            durations.append(300)
        else:
            durations.append(80)

    frames[0].save(
        out,
        save_all=True,
        append_images=frames[1:],
        duration=durations[: len(frames)],
        loop=0,
        optimize=False,
    )
    size_kb = out.stat().st_size // 1024
    print(f"Saved {out} ({size_kb} KB, {len(frames)} frames)")


if __name__ == "__main__":
    main()
