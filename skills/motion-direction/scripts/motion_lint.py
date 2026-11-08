#!/usr/bin/env python3
"""Find common web-animation anti-patterns in a source tree (no dependencies).

Usage: python3 motion_lint.py <src-dir> [--json]
Checks JS/TS/JSX/TSX/Vue/Svelte/Astro/CSS/SCSS files for:
  - animating layout properties (top/left/width/height/margin) in GSAP, Motion, CSS transitions/keyframes
  - scroll event listeners (prefer ScrollTrigger / IntersectionObserver / CSS scroll timelines)
  - GSAP in React components without useGSAP / gsap.context cleanup
  - ScrollTrigger markers left on
  - project-wide: animations present but no prefers-reduced-motion handling
  - transition: all
"""
import json
import os
import re
import sys


# Windows consoles default to a legacy code page; force UTF-8 so symbols in the report print instead of crashing.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

EXTS = (".js", ".jsx", ".ts", ".tsx", ".mjs", ".vue", ".svelte", ".astro", ".css", ".scss")
SKIP = {"node_modules", ".git", "dist", "build", ".next", ".nuxt", "out", ".astro", "coverage", ".svelte-kit"}
LAYOUT = r"(?:top|left|right|bottom|width|height|margin(?:Top|Left|Right|Bottom)?|padding)"

RULES = [
    ("warn", re.compile(r"gsap\.(?:to|from|fromTo|set)\([^)]*\{[^}]*\b" + LAYOUT + r"\s*:", re.S),
     "GSAP animates a layout property — use x/y/scale/autoAlpha instead"),
    ("warn", re.compile(r"\b(?:animate|initial|exit|whileHover|whileInView)=\{\{[^}]*\b" + LAYOUT + r"\s*:"),
     "Motion animates a layout property — use x/y/scale or the `layout` prop"),
    ("warn", re.compile(r"transition(?:-property)?\s*:\s*[^;{}\n]*\b(?:top|left|width|height|margin)\b"),
     "CSS transition on a layout property — use transform/opacity"),
    ("info", re.compile(r"transition\s*:\s*all\b"),
     "`transition: all` — list the exact properties"),
    ("warn", re.compile(r"addEventListener\(\s*['\"]scroll['\"]"),
     "scroll event listener — prefer ScrollTrigger, IntersectionObserver, or CSS scroll-driven animations"),
    ("warn", re.compile(r"markers\s*:\s*true"),
     "ScrollTrigger markers: true — remove before shipping"),
]

MOTION_HINT = re.compile(r"gsap\.|from\s+['\"](?:motion|framer-motion)|@keyframes|ScrollTrigger|new Lenis|animation\s*:")
REDUCED = re.compile(r"prefers-reduced-motion|reducedMotion|useReducedMotion")
REACT_FILE = re.compile(r"from\s+['\"]react['\"]|['\"]use client['\"]")
GSAP_USE = re.compile(r"gsap\.(?:to|from|fromTo|timeline)\(")
GSAP_CLEAN = re.compile(r"useGSAP|gsap\.context|\.revert\(\)|matchMedia\(")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        sys.exit(1)
    root = args[0]
    findings, any_motion, any_reduced, scanned = [], False, False, 0

    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP]
        for fn in fns:
            if not fn.endswith(EXTS):
                continue
            path = os.path.join(dp, fn)
            try:
                text = open(path, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            scanned += 1
            rel = os.path.relpath(path, root)
            if MOTION_HINT.search(text):
                any_motion = True
            if REDUCED.search(text):
                any_reduced = True
            for sev, rx, msg in RULES:
                for m in rx.finditer(text):
                    line = text.count("\n", 0, m.start()) + 1
                    findings.append((sev, f"{rel}:{line}", msg))
            if REACT_FILE.search(text) and GSAP_USE.search(text) and not GSAP_CLEAN.search(text):
                findings.append(("error", rel, "GSAP in a React component without useGSAP/gsap.context — leaks & double-runs in Strict Mode"))

    if any_motion and not any_reduced:
        findings.append(("error", "(project)", "Animations found but no prefers-reduced-motion handling anywhere"))

    if "--json" in sys.argv:
        print(json.dumps([{"severity": s, "where": w, "message": m} for s, w, m in findings], indent=2))
    else:
        icon = {"error": "❌", "warn": "⚠️ ", "info": "ℹ️ "}
        for s, w, m in findings:
            print(f"{icon[s]} {w} — {m}")
        errs = sum(1 for f in findings if f[0] == "error")
        print(f"\nScanned {scanned} file(s): {len(findings)} finding(s), {errs} error(s)" if findings
              else f"✅ Scanned {scanned} file(s): no motion anti-patterns found")
    sys.exit(1 if any(f[0] == "error" for f in findings) else 0)


if __name__ == "__main__":
    main()
