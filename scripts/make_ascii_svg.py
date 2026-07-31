"""Render an adaptive, high-density terminal halftone portrait as SVG."""
from html import escape
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
SOURCE, TARGET = ROOT / "source-prepped.png", ROOT / "profile-ascii.svg"
if not SOURCE.is_file():
    raise SystemExit("Run scripts/prep_photo.py source-photo.jpg first.")

# Keep the published SVG canvas unchanged while increasing sampling density.
WIDTH, HEIGHT, PAD, BAR = 630, 866, 20, 31
COLS, ROWS = 96, 78
ART_W, ART_H = WIDTH - PAD * 2, HEIGHT - 78
CELL_W, CELL_H = ART_W / COLS, ART_H / ROWS
PORTRAIT_COLOR = "#56d364"
RAMP = " .:*cCsS"  # light to dense; intentionally excludes heavy symbols


def adaptive_halftone() -> list[str]:
    """Use local contrast plus Floyd–Steinberg diffusion for facial detail."""
    image = Image.open(SOURCE).convert("L")
    image = ImageEnhance.Contrast(image).enhance(1.28)
    image = image.filter(ImageFilter.UnsharpMask(radius=1.4, percent=125, threshold=2))
    image = image.resize((COLS, ROWS), Image.Resampling.LANCZOS)
    gray = np.asarray(image, dtype=np.float32) / 255.0
    darkness = 1.0 - gray
    local_average = 1.0 - np.asarray(image.filter(ImageFilter.GaussianBlur(1.15)), dtype=np.float32) / 255.0
    working = np.clip(darkness + 0.58 * (darkness - local_average), 0.0, 1.0)
    mask = darkness > 0.055  # rembg-composited white remains fully empty
    levels = len(RAMP) - 1
    characters: list[list[str]] = [[" "] * COLS for _ in range(ROWS)]

    for y in range(ROWS):
        for x in range(COLS):
            if not mask[y, x]:
                continue
            original = working[y, x]
            level = int(np.clip(round(original * levels), 0, levels))
            quantized = level / levels
            characters[y][x] = RAMP[level]
            error = original - quantized
            for dx, dy, weight in ((1, 0, 7 / 16), (-1, 1, 3 / 16), (0, 1, 5 / 16), (1, 1, 1 / 16)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < COLS and 0 <= ny < ROWS and mask[ny, nx]:
                    working[ny, nx] = np.clip(working[ny, nx] + error * weight, 0.0, 1.0)
    return ["".join(row) for row in characters]


lines = adaptive_halftone()
parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">',
    '<title id="title">Animated ASCII portrait of Afsal A Azeez</title>',
    '<desc id="desc">A high-density monochrome terminal halftone portrait that sketches itself once over a transparent background.</desc>',
    '<style>text{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}.row{animation:draw .216s steps(7,end) both}.cursor{transform-box:fill-box;transform-origin:left center;animation:cursor .216s linear both}@keyframes draw{from{opacity:0;clip-path:inset(0 100% 0 0)}to{opacity:1;clip-path:inset(0 0 0 0)}}@keyframes cursor{0%{opacity:0;transform:translateX(0)}8%{opacity:.9}90%{opacity:.9}100%{opacity:0;transform:translateX(590px)}}</style>',
    f'<line x2="{WIDTH}" y1="{BAR}" y2="{BAR}" stroke="#30363d"/>',
    f'<text x="{WIDTH / 2}" y="20" text-anchor="middle" fill="#8b949e" font-size="12">afsal@github: ~/whoami</text>',
]
for index, color in enumerate(("#8b949e", "#6e7681", "#484f58")):
    parts.append(f'<circle cx="{PAD + index * 15}" cy="15" r="4" fill="{color}"/>')

# More rows need a slightly tighter stagger to preserve the original total reveal time.
for row, line in enumerate(lines):
    delay, duration = row * 0.041, 0.216
    row_y = BAR + row * CELL_H
    text_y = BAR + 17 + row * CELL_H
    text = (f'<text class="row" x="{PAD}" y="{text_y:.2f}" fill="{PORTRAIT_COLOR}" '
            f'font-size="{CELL_H * .86:.2f}" xml:space="preserve" textLength="{ART_W:.2f}" '
            f'lengthAdjust="spacing" style="animation-delay:{delay:.3f}s">{escape(line)}</text>')
    # CSS animation works in GitHub-rendered SVGs; without it, the text stays visible.
    parts.append(text)
    parts.append(
        f'<rect x="{PAD}" y="{row_y + 1:.2f}" width="{CELL_W:.2f}" height="{CELL_H - 2:.2f}" '
        f'fill="{PORTRAIT_COLOR}" opacity="0" class="cursor" style="animation-delay:{delay:.3f}s"/>'
    )

parts += [
    f'<line x2="{WIDTH}" y1="{HEIGHT - 30}" y2="{HEIGHT - 30}" stroke="#30363d"/>',
    f'<text x="{PAD}" y="{HEIGHT - 10}" fill="#8b949e" font-size="12">whoami  <tspan fill="#c9d1d9">Afsal A Azeez</tspan></text>',
    '</svg>',
]
TARGET.write_text("".join(parts), encoding="utf-8")
print(f"wrote {TARGET}")
