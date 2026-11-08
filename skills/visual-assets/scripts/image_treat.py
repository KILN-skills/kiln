#!/usr/bin/env python3
"""Batch-treat images so they look like one art-directed set, then export web-ready WebP.

Usage:
  python3 image_treat.py <input-dir-or-file> <output-dir> [options]

Options:
  --ratio 4:5          crop to aspect ratio (center/focus crop). e.g. 16:9, 1:1, 3:4
  --focus 0.5,0.4      crop focus point as x,y fractions (default 0.5,0.5)
  --width 1600         max output width (also writes @0.5x for srcset)
  --look NAME          none | duotone | warm-film | cool-film | mono | fade   (default none)
  --dark #111111 --light #f2e8d5   duotone colors (shadows, highlights)
  --grain 0.06         grain strength 0-0.2 (0 = off)
  --quality 80         WebP quality

Example (unify mismatched stock photos):
  python3 image_treat.py raw/ public/img/ --ratio 4:5 --look warm-film --grain 0.05
Requires: pip install pillow
"""
import argparse
import os
import random
import sys

try:
    from PIL import Image, ImageEnhance, ImageOps, ImageChops
except ImportError:
    sys.exit("pip install pillow")

EXTS = (".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp")


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def crop_ratio(im, ratio, focus):
    if not ratio:
        return im
    rw, rh = (float(x) for x in ratio.split(":"))
    target = rw / rh
    w, h = im.size
    if w / h > target:
        nw = int(h * target)
        x = int((w - nw) * focus[0])
        return im.crop((x, 0, x + nw, h))
    nh = int(w / target)
    y = int((h - nh) * focus[1])
    return im.crop((0, y, w, y + nh))


def grade(im, look, dark, light):
    if look == "none":
        return im
    if look == "mono":
        g = ImageOps.grayscale(im)
        return ImageOps.autocontrast(g, cutoff=1).convert("RGB")
    if look == "duotone":
        g = ImageOps.autocontrast(ImageOps.grayscale(im), cutoff=1)
        return ImageOps.colorize(g, black=dark, white=light)
    if look == "fade":
        im = ImageEnhance.Contrast(im).enhance(0.85)
        im = ImageEnhance.Color(im).enhance(0.8)
        lift = Image.new("RGB", im.size, (30, 30, 30))
        return ImageChops.add(im, lift, scale=1.0)
    r, g, b = im.split()
    if look == "warm-film":
        r = r.point(lambda v: min(255, int(v * 1.06 + 6)))
        b = b.point(lambda v: int(v * 0.9 + 10))
    elif look == "cool-film":
        r = r.point(lambda v: int(v * 0.93 + 8))
        b = b.point(lambda v: min(255, int(v * 1.05 + 8)))
    im = Image.merge("RGB", (r, g, b))
    im = ImageEnhance.Color(im).enhance(0.85)
    im = ImageEnhance.Contrast(im).enhance(1.05)
    # lifted blacks, softened highlights = film-like
    return im.point(lambda v: int(18 + v * (235 - 18) / 255))


def add_grain(im, strength, seed=7):
    if strength <= 0:
        return im
    rnd = random.Random(seed)
    w, h = im.size
    small = Image.new("L", (max(1, w // 2), max(1, h // 2)))
    small.putdata([int(128 + rnd.gauss(0, 255 * strength)) for _ in range(small.size[0] * small.size[1])])
    noise = small.resize((w, h), Image.BILINEAR).convert("RGB")
    return ImageChops.overlay(im, noise)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--ratio")
    ap.add_argument("--focus", default="0.5,0.5")
    ap.add_argument("--width", type=int, default=1600)
    ap.add_argument("--look", default="none", choices=["none", "duotone", "warm-film", "cool-film", "mono", "fade"])
    ap.add_argument("--dark", default="#111111")
    ap.add_argument("--light", default="#f2e8d5")
    ap.add_argument("--grain", type=float, default=0.0)
    ap.add_argument("--quality", type=int, default=80)
    a = ap.parse_args()

    files = [a.src] if os.path.isfile(a.src) else sorted(
        os.path.join(a.src, f) for f in os.listdir(a.src) if f.lower().endswith(EXTS))
    if not files:
        sys.exit("No images found.")
    os.makedirs(a.out, exist_ok=True)
    focus = tuple(float(x) for x in a.focus.split(","))
    total_in = total_out = 0

    for f in files:
        im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
        im = crop_ratio(im, a.ratio, focus)
        if im.width > a.width:
            im = im.resize((a.width, round(im.height * a.width / im.width)), Image.LANCZOS)
        im = grade(im, a.look, hex_rgb(a.dark), hex_rgb(a.light))
        im = add_grain(im, a.grain)
        base = os.path.splitext(os.path.basename(f))[0]
        out = os.path.join(a.out, f"{base}.webp")
        im.save(out, "WEBP", quality=a.quality, method=6)
        half = im.resize((im.width // 2, im.height // 2), Image.LANCZOS)
        half.save(os.path.join(a.out, f"{base}@0.5x.webp"), "WEBP", quality=a.quality, method=6)
        total_in += os.path.getsize(f)
        total_out += os.path.getsize(out)
        print(f"{os.path.basename(f)} -> {base}.webp {im.width}x{im.height} ({os.path.getsize(out)//1024} KB)")

    print(f"\n{len(files)} image(s): {total_in//1024} KB -> {total_out//1024} KB (full size)")
    print("Use: <img src='x.webp' srcset='x@0.5x.webp 800w, x.webp 1600w' sizes='(max-width: 768px) 100vw, 50vw' width height alt>")


if __name__ == "__main__":
    main()
