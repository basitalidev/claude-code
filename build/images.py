#!/usr/bin/env python3
"""Image pipeline.

  python3 build/images.py placeholders          # make placeholder WebPs for any missing slot
  python3 build/images.py add <key> <photo.jpg> # crop/resize a source photo into the slot

Each slot is written as /assets/img/<key>-800.webp and <key>-1600.webp (3:2 crop).
Requires Pillow (pip install pillow).
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageOps

sys.path.insert(0, os.path.dirname(__file__))
from site_images import IMAGES  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "img")
SIZES = (800, 1600)
RATIO = 3 / 2


def out_path(key, w):
    return os.path.join(OUT, f"{key}-{w}.webp")


def save_slot(key, img):
    os.makedirs(OUT, exist_ok=True)
    img = ImageOps.fit(img.convert("RGB"), (1600, int(1600 / RATIO)), method=Image.LANCZOS, centering=(0.5, 0.45))
    for w in SIZES:
        im = img if w == 1600 else img.resize((w, int(w / RATIO)), Image.LANCZOS)
        im.save(out_path(key, w), "WEBP", quality=78, method=6)


def placeholder(key):
    w, h = 1600, int(1600 / RATIO)
    img = Image.new("RGB", (w, h), "#12325a")
    d = ImageDraw.Draw(img)
    for y in range(h):  # vertical gradient
        t = y / h
        d.line([(0, y), (w, y)], fill=(int(18 + 40 * t), int(50 + 30 * t), int(90 + 10 * t)))
    # simple mountain/roof silhouette so placeholders read as "image"
    d.polygon([(0, h), (0, h * .62), (w * .22, h * .38), (w * .38, h * .55), (w * .6, h * .3), (w * .8, h * .5), (w, h * .42), (w, h)], fill=(30, 58, 90))
    d.polygon([(w * .25, h), (w * .25, h * .78), (w * .45, h * .6), (w * .65, h * .78), (w * .65, h)], fill=(14, 30, 50))
    img = img.filter(ImageFilter.GaussianBlur(1))
    save_slot(key, img)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "placeholders"
    if cmd == "placeholders":
        made = [k for k in IMAGES if not os.path.exists(out_path(k, 1600)) and placeholder(k) is None]
        print(f"placeholders created: {len(made)}")
    elif cmd == "add":
        key, src = sys.argv[2], sys.argv[3]
        if key not in IMAGES:
            sys.exit(f"unknown slot {key}")
        save_slot(key, Image.open(src))
        print(f"{key}: written {', '.join(os.path.basename(out_path(key, w)) for w in SIZES)}")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
