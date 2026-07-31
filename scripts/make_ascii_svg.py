"""Render source-prepped.png as a one-shot animated monochrome SVG portrait."""
from pathlib import Path
from html import escape
from PIL import Image, ImageEnhance

ROOT = Path(__file__).resolve().parents[1]
source, target = ROOT / "source-prepped.png", ROOT / "profile-ascii.svg"
if not source.is_file():
    raise SystemExit("Run scripts/prep_photo.py source-photo.jpg first.")
cols, rows, cw, ch = 72, 58, 8.2, 13.6
ramp = " .:-=+*#%@"
image = ImageEnhance.Contrast(Image.open(source).convert("L")).enhance(1.15).resize((cols, rows), Image.Resampling.LANCZOS)
lines = []
for y in range(rows):
    line = ""
    for x in range(cols):
        value = image.getpixel((x, y)) / 255
        line += " " if value > .86 else ramp[min(len(ramp)-1, int((1-value)*(len(ramp)-1)))]
    lines.append(line)
width, height, pad, bar = int(cols*cw+40), int(rows*ch+78), 20, 31
parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
 '<title id="title">Animated ASCII portrait of Afsal A Azeez</title><desc id="desc">A monochrome terminal portrait that reveals once and remains visible.</desc>',
 '<style>text{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}.row{opacity:0;animation:reveal .18s ease-out forwards}@keyframes reveal{to{opacity:1}}</style>',
 f'<rect width="{width}" height="{height}" rx="12" fill="#0d1117"/><rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="12" fill="none" stroke="#30363d"/>',
 f'<line x2="{width}" y1="{bar}" y2="{bar}" stroke="#30363d"/><text x="{width/2}" y="20" text-anchor="middle" fill="#8b949e" font-size="12">afsal@github: ~/portrait</text>']
for i, color in enumerate(("#8b949e", "#6e7681", "#484f58")):
    parts.append(f'<circle cx="{pad+i*15}" cy="15" r="4" fill="{color}"/>')
for y, line in enumerate(lines):
    delay = y * .045
    parts.append(f'<text class="row" x="{pad}" y="{bar+17+y*ch:.1f}" fill="#c9d1d9" font-size="{ch*.86:.1f}" xml:space="preserve" textLength="{cols*cw}" lengthAdjust="spacing" style="animation-delay:{delay:.3f}s">{escape(line)}</text>')
parts += [f'<line x2="{width}" y1="{height-30}" y2="{height-30}" stroke="#30363d"/>', f'<text x="{pad}" y="{height-10}" fill="#8b949e" font-size="12">whoami  <tspan fill="#c9d1d9">Afsal A Azeez</tspan></text>', '</svg>']
target.write_text(''.join(parts), encoding='utf-8')
print(f"wrote {target}")
