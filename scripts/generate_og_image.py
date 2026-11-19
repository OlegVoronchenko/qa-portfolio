#!/usr/bin/env python3
"""
Social Preview Image Generator
===============================

PURPOSE
-------
Produces public/og-image.png (1200x630), the static social-preview
card referenced by og:image / twitter:image in index.html.

WHY A ONE-OFF SCRIPT, NOT A BUILD STEP
----------------------------------------
This is a static asset with fixed, pre-approved content (name, role,
positioning) — it doesn't need to be regenerated on every build.
Run manually whenever the approved positioning text changes:

    python3 scripts/generate_og_image.py

WHY PILLOW
----------
Pillow is already a project dependency (qa/requirements.txt, used by
the screenshot blank-detector in qa/pages/portfolio_page.py). Drawing
directly with Pillow avoids adding a headless-browser or canvas
dependency just to produce one static image.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1200, 630
BG = (11, 17, 32)          # dark-900
CARD_BORDER = (30, 41, 59)  # dark-600
ACCENT = (16, 185, 129)     # accent (emerald)
WHITE = (241, 245, 249)     # slate-100
MUTED = (100, 116, 139)     # slate-500
MUTED_LIGHT = (148, 163, 184)  # slate-400

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "public" / "og-image.png"

FONT_DIR = Path("/System/Library/Fonts/Supplemental")
FONT_BOLD = FONT_DIR / "Arial Bold.ttf"
FONT_REGULAR = FONT_DIR / "Arial.ttf"
FONT_MONO = FONT_DIR / "Andale Mono.ttf"


def _font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(str(path), size)
    except OSError:
        return ImageFont.load_default()


def generate() -> None:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)

    # Subtle border frame for definition against social-platform chrome.
    draw.rectangle([(0, 0), (WIDTH - 1, HEIGHT - 1)], outline=CARD_BORDER, width=2)

    # Faint accent corner accent (top-left), echoing the site's dot-grid motif
    # without reproducing a busy pattern.
    draw.line([(0, 0), (120, 0)], fill=ACCENT, width=6)
    draw.line([(0, 0), (0, 120)], fill=ACCENT, width=6)

    margin_x = 90

    # Wordmark, matching Navbar's "OV QA" branding.
    f_wordmark = _font(FONT_BOLD, 28)
    draw.text((margin_x, 60), "OV", font=f_wordmark, fill=ACCENT)
    ov_w = draw.textlength("OV", font=f_wordmark)
    draw.text((margin_x + ov_w + 10, 60), "QA", font=f_wordmark, fill=MUTED_LIGHT)

    # Name
    f_name = _font(FONT_BOLD, 76)
    name_y = 170
    draw.text((margin_x, name_y), "Oleg", font=f_name, fill=WHITE)
    oleg_w = draw.textlength("Oleg ", font=f_name)
    draw.text((margin_x + oleg_w, name_y), "Voronchenko", font=f_name, fill=ACCENT)

    # Primary role
    f_role = _font(FONT_BOLD, 40)
    draw.text((margin_x, name_y + 100), "Lead Test Automation Engineer", font=f_role, fill=ACCENT)

    # Supporting positioning
    f_support = _font(FONT_MONO, 26)
    draw.text(
        (margin_x, name_y + 160),
        "Senior SDET · QA Architecture · Engineering Leadership",
        font=f_support,
        fill=MUTED_LIGHT,
    )

    # Industry / domain line
    f_domain = _font(FONT_REGULAR, 26)
    draw.text(
        (margin_x, name_y + 205),
        "Healthcare · Medical Devices · AI-Assisted Engineering",
        font=f_domain,
        fill=MUTED,
    )

    img.save(OUTPUT_PATH, format="PNG", optimize=True)
    print(f"Wrote {OUTPUT_PATH} ({OUTPUT_PATH.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    generate()
