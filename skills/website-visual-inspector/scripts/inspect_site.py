#!/usr/bin/env python3
"""
inspect_site.py — Screenshot a website and extract all of its backgrounds.

Output (in the --out folder):
  screenshot_desktop.png      full-page screenshot 1440px
  screenshot_mobile.png       full-page screenshot 390px (iPhone-ish)
  viewport_desktop.png        only the first screen (above the fold)
  backgrounds.json            every element that has a background
  backgrounds/                background image/video files that downloaded
  palette.json                the most-used background colors
  report.md                   a short summary that's easy for an agent to read

Usage:
  python3 inspect_site.py https://example.com
  python3 inspect_site.py https://example.com --out result --no-mobile --wait 3000
  python3 inspect_site.py ./index.html            (local files work too)
"""
import argparse
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import url2pathname

# Windows consoles default to a legacy code page; force UTF-8 so symbols in the report print instead of crashing.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")


try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit("Playwright is not installed. Run:\n"
             "  pip install playwright && python -m playwright install chromium")

# JavaScript run in the page to collect every background
COLLECT_JS = r"""
() => {
  const out = [];
  const isTransparent = c => !c || c === 'transparent' || /rgba\(\s*0,\s*0,\s*0,\s*0\s*\)/.test(c);
  const urlsIn = s => {
    const r = []; const re = /url\(\s*(['"]?)(.*?)\1\s*\)/g; let m;
    while ((m = re.exec(s || ''))) r.push(m[2]);
    return r;
  };
  const sel = el => {
    if (el.id) return '#' + CSS.escape(el.id);
    let s = el.tagName.toLowerCase();
    if (el.classList.length) s += '.' + [...el.classList].slice(0, 3).map(c => CSS.escape(c)).join('.');
    const p = el.parentElement;
    if (p) {
      const same = [...p.children].filter(x => x.tagName === el.tagName);
      if (same.length > 1) s += `:nth-of-type(${same.indexOf(el) + 1})`;
      if (p !== document.body && p !== document.documentElement) return sel(p) + ' > ' + s;
    }
    return s;
  };

  const all = [document.documentElement, ...document.querySelectorAll('*')];
  for (const el of all) {
    const r = el.getBoundingClientRect();
    for (const pseudo of [null, '::before', '::after']) {
      const cs = getComputedStyle(el, pseudo);
      if (pseudo && (cs.content === 'none' || cs.content === 'normal')) continue;
      const color = cs.backgroundColor;
      const image = cs.backgroundImage;
      const hasImg = image && image !== 'none';
      if (isTransparent(color) && !hasImg) continue;
      out.push({
        selector: sel(el) + (pseudo || ''),
        tag: el.tagName.toLowerCase(),
        rect: { x: Math.round(r.left + scrollX), y: Math.round(r.top + scrollY),
                w: Math.round(r.width), h: Math.round(r.height) },
        backgroundColor: isTransparent(color) ? null : color,
        backgroundImage: hasImg ? image : null,
        isGradient: hasImg && /gradient\(/.test(image),
        imageUrls: urlsIn(image).map(u => { try { return new URL(u, location.href).href } catch { return u } }),
        size: cs.backgroundSize, position: cs.backgroundPosition,
        repeat: cs.backgroundRepeat, attachment: cs.backgroundAttachment,
        blendMode: cs.backgroundBlendMode, opacity: cs.opacity,
        filter: cs.filter !== 'none' ? cs.filter : null,
        backdropFilter: (cs.backdropFilter && cs.backdropFilter !== 'none') ? cs.backdropFilter : null,
      });
    }
  }

  // Video and canvas used as backgrounds (usually absolute/fixed, large, behind content)
  const media = [];
  for (const v of document.querySelectorAll('video')) {
    const r = v.getBoundingClientRect(); const cs = getComputedStyle(v);
    media.push({ kind: 'video', selector: sel(v),
      src: v.currentSrc || v.src || (v.querySelector('source') || {}).src || null,
      poster: v.poster || null, autoplay: v.autoplay, loop: v.loop, muted: v.muted,
      position: cs.position, zIndex: cs.zIndex, objectFit: cs.objectFit,
      rect: { w: Math.round(r.width), h: Math.round(r.height) } });
  }
  for (const c of document.querySelectorAll('canvas')) {
    const r = c.getBoundingClientRect(); const cs = getComputedStyle(c);
    if (r.width * r.height < 40000) continue;
    media.push({ kind: 'canvas (likely a WebGL/particle animation)', selector: sel(c),
      position: cs.position, zIndex: cs.zIndex, rect: { w: Math.round(r.width), h: Math.round(r.height) } });
  }
  // a large <img> with object-fit: cover and absolute position is a common "fake" background
  for (const im of document.querySelectorAll('img')) {
    const r = im.getBoundingClientRect(); const cs = getComputedStyle(im);
    if (cs.objectFit === 'cover' && ['absolute', 'fixed'].includes(cs.position) && r.width > 400) {
      media.push({ kind: 'img-as-background', selector: sel(im), src: im.currentSrc || im.src,
        rect: { w: Math.round(r.width), h: Math.round(r.height) } });
    }
  }

  // CSS variables on :root related to color/background
  const vars = {};
  const rootCs = getComputedStyle(document.documentElement);
  for (const sheet of document.styleSheets) {
    let rules; try { rules = sheet.cssRules } catch { continue }
    for (const rule of rules || []) {
      if (rule.selectorText && /(^|,)\s*(:root|html|body)\b/.test(rule.selectorText)) {
        for (const name of rule.style) if (name.startsWith('--')) vars[name] = rootCs.getPropertyValue(name).trim();
      }
    }
  }

  return {
    title: document.title,
    url: location.href,
    pageSize: { w: document.documentElement.scrollWidth, h: document.documentElement.scrollHeight },
    bodyBackground: getComputedStyle(document.body).backgroundColor,
    htmlBackground: getComputedStyle(document.documentElement).backgroundColor,
    backgrounds: out, media, cssVariables: vars,
  };
}
"""


def safe_name(url: str, i: int) -> str:
    p = urlparse(url)
    base = os.path.basename(p.path) or f"bg_{i}"
    base = re.sub(r"[^A-Za-z0-9._-]", "_", base)[:80]
    return f"{i:02d}_{base}"


def auto_scroll(page):
    """Scroll slowly to the bottom so lazy-loaded content and scroll animations render."""
    page.evaluate("""async () => {
      await new Promise(res => {
        let y = 0; const step = innerHeight * 0.8;
        const t = setInterval(() => {
          scrollBy(0, step); y += step;
          if (y >= document.documentElement.scrollHeight) { clearInterval(t); scrollTo(0, 0); res(); }
        }, 150);
      });
    }""")


def dismiss_overlays(page):
    """Try to close common cookie banners so they don't cover the screenshot (picks the most private option). Includes Indonesian labels."""
    for label in ["Reject all", "Tolak semua", "Decline", "Only necessary", "Necessary only", "Close", "Tutup"]:
        try:
            btn = page.get_by_role("button", name=re.compile(label, re.I)).first
            if btn.is_visible(timeout=300):
                btn.click(timeout=1000)
                return
        except Exception:
            pass


def to_hex(c):
    m = re.match(r"rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)", c or "")
    if not m:
        return c
    r, g, b, a = m.groups()
    if a is not None and float(a) == 0:
        return "transparent"
    h = "#{:02x}{:02x}{:02x}".format(int(r), int(g), int(b))
    return h if a in (None, "1") else f"{h} @ {float(a):.2f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--out", default="site-inspect")
    ap.add_argument("--wait", type=int, default=1500, help="ms to wait after load (animations/fonts)")
    ap.add_argument("--no-mobile", action="store_true")
    ap.add_argument("--no-download", action="store_true", help="don't download background image files")
    ap.add_argument("--dark", action="store_true", help="render with prefers-color-scheme: dark")
    args = ap.parse_args()

    url = args.url
    if not re.match(r"^[a-z]+://", url):
        p = Path(url)
        url = p.resolve().as_uri() if p.exists() else "https://" + url

    out = Path(args.out)
    (out / "backgrounds").mkdir(parents=True, exist_ok=True)
    scheme = "dark" if args.dark else "light"

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1440, "height": 900}, color_scheme=scheme,
                                  device_scale_factor=1)
        page = ctx.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        try:
            page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        dismiss_overlays(page)
        auto_scroll(page)
        page.wait_for_timeout(args.wait)

        page.screenshot(path=str(out / "viewport_desktop.png"))
        page.screenshot(path=str(out / "screenshot_desktop.png"), full_page=True)
        data = page.evaluate(COLLECT_JS)

        # Download background images through the browser context (cookies/referer included)
        downloaded = {}
        if not args.no_download:
            urls = []
            for bg in data["backgrounds"]:
                urls += bg["imageUrls"]
            urls += [m.get("src") for m in data["media"] if m.get("src")]
            urls += [m.get("poster") for m in data["media"] if m.get("poster")]
            for i, u in enumerate(dict.fromkeys(u for u in urls if u and not u.startswith("data:"))):
                try:
                    if u.startswith("file://"):
                        # Only copy local files when inspecting a local page, never for a web page.
                        if not url.startswith("file://"):
                            downloaded[u] = "SKIPPED: local file referenced by a web page"
                            continue
                        src = Path(url2pathname(urlparse(u).path))
                        f = out / "backgrounds" / safe_name(u, i)
                        f.write_bytes(src.read_bytes())
                        downloaded[u] = str(f.relative_to(out))
                        continue
                    r = ctx.request.get(u, timeout=20000)
                    if r.ok and len(r.body()) < 50_000_000:
                        f = out / "backgrounds" / safe_name(u, i)
                        f.write_bytes(r.body())
                        downloaded[u] = str(f.relative_to(out))
                except Exception as e:
                    downloaded[u] = f"FAILED: {e.__class__.__name__}"
        data["downloaded"] = downloaded

        if not args.no_mobile:
            mctx = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True,
                                       has_touch=True, device_scale_factor=2, color_scheme=scheme)
            mp = mctx.new_page()
            mp.goto(url, wait_until="domcontentloaded", timeout=60000)
            try:
                mp.wait_for_load_state("networkidle", timeout=15000)
            except Exception:
                pass
            dismiss_overlays(mp)
            auto_scroll(mp)
            mp.wait_for_timeout(args.wait)
            mp.screenshot(path=str(out / "screenshot_mobile.png"), full_page=True)
            mctx.close()
        browser.close()

    # Palette: background colors weighted by area
    weight = Counter()
    for bg in data["backgrounds"]:
        if bg["backgroundColor"]:
            weight[to_hex(bg["backgroundColor"])] += max(1, bg["rect"]["w"] * bg["rect"]["h"])
    total = sum(weight.values()) or 1
    palette = [{"color": c, "areaShare": round(w / total, 3)} for c, w in weight.most_common(12)]

    (out / "backgrounds.json").write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "palette.json").write_text(json.dumps(palette, indent=2), encoding="utf-8")

    # Short report
    big = sorted(data["backgrounds"], key=lambda b: -b["rect"]["w"] * b["rect"]["h"])
    L = [f"# Visual inspection: {data['title'] or data['url']}", "",
         f"- URL: {data['url']}",
         f"- Page size: {data['pageSize']['w']}×{data['pageSize']['h']} px",
         f"- Background `html`: {to_hex(data['htmlBackground'])} · `body`: {to_hex(data['bodyBackground'])}",
         f"- Color scheme used: {scheme}", "",
         "## Screenshot", "- `viewport_desktop.png` (first screen)", "- `screenshot_desktop.png` (full page)"]
    if not args.no_mobile:
        L.append("- `screenshot_mobile.png` (full page, 390px)")
    L += ["", "## Background palette (by area)"]
    L += [f"- {p['color']} — {p['areaShare']*100:.1f}%" for p in palette]

    grads = [b for b in data["backgrounds"] if b["isGradient"]]
    imgs = [b for b in data["backgrounds"] if b["imageUrls"]]
    L += ["", f"## Gradient ({len(grads)})"]
    for b in grads[:15]:
        L.append(f"- `{b['selector']}` ({b['rect']['w']}×{b['rect']['h']}): `{b['backgroundImage'][:300]}`")
    L += ["", f"## Background images ({len(imgs)})"]
    for b in imgs[:25]:
        for u in b["imageUrls"]:
            L.append(f"- `{b['selector']}` → {u[:150]}  \n  size={b['size']}, position={b['position']}, "
                     f"repeat={b['repeat']}, attachment={b['attachment']}"
                     + (f", file=`{downloaded[u]}`" if u in downloaded else ""))
    L += ["", f"## Video / canvas / img used as background ({len(data['media'])})"]
    for m in data["media"]:
        L.append(f"- {m['kind']}: `{m['selector']}` {json.dumps({k: v for k, v in m.items() if k not in ('kind', 'selector')})}")
    fx = [b for b in data["backgrounds"]
          if b["attachment"] == "fixed" or b["backdropFilter"] or b["filter"]
          or (b["blendMode"] and b["blendMode"] != "normal")]
    L += ["", f"## Effects ({len(fx)})"]
    for b in fx[:15]:
        bits = []
        if b["attachment"] == "fixed": bits.append("parallax (attachment: fixed)")
        if b["backdropFilter"]: bits.append(f"backdrop-filter: {b['backdropFilter']} (glassmorphism)")
        if b["filter"]: bits.append(f"filter: {b['filter']}")
        if b["blendMode"] and b["blendMode"] != "normal": bits.append(f"blend-mode: {b['blendMode']}")
        L.append(f"- `{b['selector']}`: " + ", ".join(bits))
    L += ["", "## 10 largest elements with a background"]
    for b in big[:10]:
        desc = b["backgroundImage"][:120] if b["backgroundImage"] else to_hex(b["backgroundColor"])
        L.append(f"- `{b['selector']}` {b['rect']['w']}×{b['rect']['h']} @y={b['rect']['y']}: {desc}")
    color_vars = {k: v for k, v in data["cssVariables"].items()
                  if re.search(r"#|rgb|hsl|oklch|gradient|color|bg|background", k + v, re.I)}
    if color_vars:
        L += ["", "## Color/background CSS variables"]
        L += [f"- `{k}`: {v}" for k, v in list(color_vars.items())[:40]]
    (out / "report.md").write_text("\n".join(L) + "\n", encoding="utf-8")

    print(f"Done → {out.resolve()}")
    print(f"  {len(data['backgrounds'])} elements with a background, {len(grads)} gradients, "
          f"{len(imgs)} images, {len(data['media'])} media")


if __name__ == "__main__":
    main()
