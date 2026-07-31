"""Prepare a private local portrait for monochrome ASCII rendering."""
from pathlib import Path
import sys
from PIL import Image, ImageEnhance, ImageOps
from rembg import remove

ROOT = Path(__file__).resolve().parents[1]
source = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "source-photo.jpg"
target = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "source-prepped.png"
if not source.is_file():
    raise SystemExit(f"Portrait not found: {source}")

image = remove(Image.open(source).convert("RGBA"))
# Center crop to a portrait-friendly 4:5 frame, preserving the face area.
w, h = image.size
side = min(w, int(h * 0.8))
left = (w - side) // 2
top = max(0, int((h - side / 0.8) * 0.28))
image = image.crop((left, top, left + side, min(h, top + int(side / 0.8))))
image = ImageOps.fit(image, (800, 1000), method=Image.Resampling.LANCZOS, centering=(0.5, 0.35))
alpha = image.getchannel("A")
gray = ImageOps.grayscale(image)
gray = ImageEnhance.Contrast(gray).enhance(1.55)
gray = ImageEnhance.Brightness(gray).enhance(1.08)
# White becomes a space in the ASCII ramp, leaving only the isolated subject.
prepared = Image.new("L", gray.size, 255)
prepared.paste(gray, mask=alpha)
prepared.save(target)
print(f"wrote {target}")
