#!/usr/bin/env python3
"""Capture what a website actually looks like and how it moves, so it can be judged visually.

Usage:
  python3 capture.py <url-or-html-file> [--out DIR] [--widths 375,1440] [--steps 8] [--intro-ms 1600]

Produces in DIR (default ./.visual-qa):
  full_<w>.png        full-page screenshot per width (after scrolling through to trigger reveals)
  intro_sheet.png     contact sheet of the first ~1.6s after load (hero intro animation timing)
  scroll_sheet.png    contact sheet of the viewport while scrolling down (scroll animations)
  reduced_<w>.png     first viewport with prefers-reduced-motion: reduce
  report.json         console errors, horizontal overflow, layout shift (CLS), broken images, fonts

Requires: pip install playwright pillow && python3 -m playwright install chromium
"""
import argparse
import json
import os
import sys
import time

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit("Missing Playwright: pip install playwright pillow && python3 -m playwright install chromium")

try:
    from PIL import Image, ImageDraw
except ImportError:
    Image = None

CLS_JS = """
window.__cls = 0;
new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__cls += e.value; })
  .observe({ type: 'layout-shift', buffered: true });
"""

CHECK_JS = """() => {
  const doc = document.documentElement;
  const overflow = doc.scrollWidth - doc.clientWidth;
  const offenders = [];
  if (overflow > 1) {
    for (const el of document.querySelectorAll('body *')) {
      const r = el.getBoundingClientRect();
      if (r.right > doc.clientWidth + 1 && r.width > 0) {
        offenders.push((el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') +
          (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\\s+/).slice(0,2).join('.') : '')));
        if (offenders.length >= 5) break;
      }
    }
  }
  const broken = [...document.images].filter(i => i.complete && i.naturalWidth === 0).map(i => i.currentSrc || i.src).slice(0, 10);
  const upscaled = [...document.images].filter(i => i.naturalWidth && i.clientWidth * devicePixelRatio > i.naturalWidth * 1.2)
    .map(i => `${i.currentSrc || i.src} (${i.naturalWidth}px shown at ${Math.round(i.clientWidth * devicePixelRatio)}px)`).slice(0, 10);
  const fonts = [...new Set([...document.querySelectorAll('h1,h2,h3,p,a,button')].map(e => getComputedStyle(e).fontFamily.split(',')[0].trim()))];
  return { horizontalOverflowPx: overflow, overflowElements: offenders, brokenImages: broken,
           blurryUpscaledImages: upscaled, fontsInUse: fonts, cls: Math.round((window.__cls || 0) * 1000) / 1000 };
}"""


def sheet(paths, labels, out, cols=4, thumb_w=480):
    if not Image or not paths:
        return False
    ims = [Image.open(p) for p in paths]
    ratio = thumb_w / ims[0].width
    th = int(ims[0].height * ratio)
    rows = (len(ims) + cols - 1) // cols
    canvas = Image.new("RGB", (cols * thumb_w + (cols + 1) * 8, rows * (th + 26) + 8), (24, 24, 24))
    d = ImageDraw.Draw(canvas)
    for i, (im, lab) in enumerate(zip(ims, labels)):
        x = 8 + (i % cols) * (thumb_w + 8)
        y = 8 + (i // cols) * (th + 26)
        canvas.paste(im.resize((thumb_w, th)), (x, y + 18))
        d.text((x, y + 2), lab, fill=(230, 230, 230))
    canvas.save(out)
    for p in paths:
        os.remove(p)
    return True


def scroll_through(page, h):
    total = page.evaluate("document.documentElement.scrollHeight")
    y = 0
    while y < total:
        page.mouse.wheel(0, h * 0.6)  # wheel, not scrollTo, so Lenis/smooth-scroll libs react
        page.wait_for_timeout(250)
        y += h * 0.6
        total = page.evaluate("document.documentElement.scrollHeight")
    page.wait_for_timeout(600)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--out", default=".visual-qa")
    ap.add_argument("--widths", default="375,1440")
    ap.add_argument("--steps", type=int, default=8)
    ap.add_argument("--intro-ms", type=int, default=1600)
    a = ap.parse_args()

    url = a.target
    if os.path.exists(url):
        url = "file://" + os.path.abspath(url)
    os.makedirs(a.out, exist_ok=True)
    widths = [int(w) for w in a.widths.split(",")]
    report = {"url": url, "viewports": {}}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for w in widths:
            h = 812 if w < 768 else 900
            ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1)
            page = ctx.new_page()
            errors = []
            page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.add_init_script(CLS_JS)

            page.goto(url, wait_until="domcontentloaded")
            # Intro filmstrip (largest width only)
            if w == max(widths):
                frames, labels, t0 = [], [], time.time()
                n = 8
                for i in range(n):
                    target = t0 + (a.intro_ms / 1000) * i / (n - 1)
                    time.sleep(max(0, target - time.time()))
                    f = os.path.join(a.out, f"_intro{i}.png")
                    page.screenshot(path=f)
                    frames.append(f)
                    labels.append(f"t = {int((time.time() - t0) * 1000)} ms")
                sheet(frames, labels, os.path.join(a.out, "intro_sheet.png"))

            page.wait_for_load_state("networkidle")
            # Scroll filmstrip (largest width only)
            if w == max(widths):
                total = page.evaluate("document.documentElement.scrollHeight")
                frames, labels = [], []
                for i in range(a.steps):
                    page.mouse.wheel(0, (total - h) / max(1, a.steps - 1) if i else 0)
                    page.wait_for_timeout(700)
                    f = os.path.join(a.out, f"_scroll{i}.png")
                    page.screenshot(path=f)
                    frames.append(f)
                    labels.append(f"scroll {int(page.evaluate('scrollY'))}px")
                sheet(frames, labels, os.path.join(a.out, "scroll_sheet.png"))
                page.mouse.wheel(0, -total)
                page.wait_for_timeout(500)

            scroll_through(page, h)
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(800)
            page.screenshot(path=os.path.join(a.out, f"full_{w}.png"), full_page=True)
            info = page.evaluate(CHECK_JS)
            info["consoleErrors"] = errors[:10]
            report["viewports"][w] = info
            ctx.close()

            # Reduced motion
            ctx = browser.new_context(viewport={"width": w, "height": h}, reduced_motion="reduce")
            page = ctx.new_page()
            page.goto(url, wait_until="networkidle")
            page.wait_for_timeout(500)
            page.screenshot(path=os.path.join(a.out, f"reduced_{w}.png"))
            ctx.close()
        browser.close()

    with open(os.path.join(a.out, "report.json"), "w") as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report, indent=2))
    print(f"\nSaved to {os.path.abspath(a.out)}: " + ", ".join(sorted(os.listdir(a.out))))
    if not Image:
        print("(Install pillow to get contact sheets.)")


if __name__ == "__main__":
    main()
