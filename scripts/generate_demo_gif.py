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


# ── Terminal colours ──────────────────────────────────────────────────────────

BG      = (18,  18,  24)
FG      = (210, 210, 210)
ANSWER  = (120, 220, 100)
HEADER  = (255, 200,  80)
OUTPUT  = (100, 180, 255)   # file output lines (cyan-blue)


# ── ANSI strip ────────────────────────────────────────────────────────────────

_ANSI_ESC = re.compile(r"\x1b\[[0-9;]*m")

def strip_ansi(text: str) -> str:
    return _ANSI_ESC.sub("", text)


# ── Classify lines ────────────────────────────────────────────────────────────

def classify(raw: str) -> tuple[str, str]:
    clean = strip_ansi(raw)
    if clean.startswith("> "):
        return "answer", clean[2:]
    if "==" in clean and clean.strip().startswith("="):
        return "header", clean
    if clean.strip().startswith("──"):
        return "section", clean
    if clean.strip().startswith("  Tasks confirmed") or clean.strip().startswith("  Agent name") or clean.strip().startswith("  Saved"):
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
        timeout=90,
    )
    return result.stdout.splitlines()


# ── Colour map ────────────────────────────────────────────────────────────────

def colour_for(line_type: str) -> tuple[int, int, int]:
    return {
        "question": FG,
        "answer":   ANSWER,
        "header":   HEADER,
        "section":  HEADER,
        "blank":    FG,
        "output":   OUTPUT,
    }.get(line_type, FG)


# ── Frame duration ────────────────────────────────────────────────────────────

def duration_for(line_type: str) -> int:
    return {
        "question": 200,
        "answer":   160,
        "header":   350,
        "section":  250,
        "blank":    60,
        "output":   120,
    }.get(line_type, 120)


# ── Render ────────────────────────────────────────────────────────────────────

WIDTH      = 860
FONT_SIZE  = 13
PAD_X      = 20
PAD_TOP    = 16
LINE_H     = FONT_SIZE + 6
WRAP_WIDTH = 80
MAX_LINES  = 28


def wrap_lines(line_type: str, text: str) -> list[tuple[str, str]]:
    """Wrap a single classified line into sub-lines, preserving type."""
    if line_type == "blank":
        return [("blank", "")]
    display = ("> " + text) if line_type == "answer" else text
    wrapped = textwrap.wrap(display, width=WRAP_WIDTH) or [display or ""]
    return [(line_type, sub) for sub in wrapped]


def render_window(window: list[tuple[str, str]], font) -> "Image":
    from PIL import Image, ImageDraw
    h = PAD_TOP * 2 + len(window) * LINE_H
    img = Image.new("P", (WIDTH, h))
    # Build palette: BG, FG, ANSWER, HEADER, OUTPUT
    palette_rgb = [BG, FG, ANSWER, HEADER, OUTPUT] + [(0, 0, 0)] * 251
    flat: list[int] = []
    for r, g, b in palette_rgb:
        flat += [r, g, b]
    img.putpalette(flat)
    rgb = Image.new("RGB", (WIDTH, h), BG)
    draw = ImageDraw.Draw(rgb)
    for li, (lt, lt_text) in enumerate(window):
        y = PAD_TOP + li * LINE_H
        draw.text((PAD_X, y), lt_text, font=font, fill=colour_for(lt))
    return rgb.quantize(colors=16, method=2)


def build_frames(all_lines: list[tuple[str, str]], font) -> tuple[list, list[int]]:
    frames: list = []
    durations: list[int] = []
    visible: list[tuple[str, str]] = []
    pending_blank = False

    for line_type, text in all_lines:
        if line_type == "blank":
            pending_blank = True
            continue

        if pending_blank:
            visible.append(("blank", ""))
            pending_blank = False

        # Add all wrapped sub-lines to visible, emit ONE frame per logical line
        sub_lines = wrap_lines(line_type, text)
        for lt, sub in sub_lines:
            visible.append((lt, sub))

        window = visible[-MAX_LINES:]
        frames.append(render_window(window, font))
        durations.append(duration_for(line_type))

    # Hold last frame
    if frames:
        durations[-1] = 3500

    return frames, durations


def main() -> None:
    print("Capturing real interview output…")
    raw_lines = capture_demo()
    print(f"  Got {len(raw_lines)} lines")

    # Classify every raw line
    classified = [classify(line) for line in raw_lines]

    # Mark output-section lines (after "Interview complete") as "output" type
    in_output = False
    final: list[tuple[str, str]] = []
    for lt, text in classified:
        if "Interview complete" in text:
            in_output = True
        if in_output and lt in ("question",):
            lt = "output"
        final.append((lt, text))

    print(f"  Processing {len(final)} lines (full interview + output)")

    font = _load_font(FONT_SIZE)

    print("Rendering frames…")
    frames, durations = build_frames(final, font)
    print(f"  {len(frames)} frames")

    out = ROOT / "docs" / "media" / "demo.gif"
    out.parent.mkdir(parents=True, exist_ok=True)

    frames[0].save(
        out,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=False,
    )
    size_kb = out.stat().st_size // 1024
    print(f"Saved {out} ({size_kb} KB, {len(frames)} frames)")


if __name__ == "__main__":
    main()
