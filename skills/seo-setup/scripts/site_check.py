#!/usr/bin/env python3
"""Static SEO + accessibility checker for built HTML (no dependencies).

Usage: python3 site_check.py <dir-or-html-file> [--json]
Scans every .html file (skipping node_modules) and reports per-page issues,
plus site-wide checks (duplicate titles/descriptions, robots.txt, sitemap.xml).
"""
import json
import os
import sys
from collections import defaultdict
from html.parser import HTMLParser

# Windows consoles default to a legacy code page; force UTF-8 so symbols in the report print instead of crashing.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")


SKIP_DIRS = {"node_modules", ".git", ".venv", "venv", "__pycache__"}


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lang = None
        self.title = ""
        self._in_title = False
        self.meta = {}
        self.canonical = None
        self.viewport = False
        self.headings = []
        self.imgs_no_alt = 0
        self.inputs = []          # (id, type, has_aria_label)
        self.label_fors = set()
        self._label_depth = 0
        self.inputs_in_label = 0
        self.empty_links = 0
        self.empty_buttons = 0
        self._stack = []          # [tag, text, has_label_attr, has_img_alt]
        self.ld_json = 0

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        if tag == "html":
            self.lang = a.get("lang") or None
        elif tag == "title":
            self._in_title = True
        elif tag == "meta":
            key = a.get("name") or a.get("property")
            if key:
                self.meta[key.lower()] = a.get("content", "")
            if (a.get("name") or "").lower() == "viewport":
                self.viewport = True
        elif tag == "link" and "canonical" in a.get("rel", "").lower().split():
            self.canonical = a.get("href")
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.headings.append(int(tag[1]))
        elif tag == "img":
            if "alt" not in a:
                self.imgs_no_alt += 1
            for item in self._stack:
                if "alt" in a and a["alt"].strip():
                    item[3] = True
        elif tag == "script" and a.get("type") == "application/ld+json":
            self.ld_json += 1
        elif tag == "label":
            self._label_depth += 1
            if a.get("for"):
                self.label_fors.add(a["for"])
        elif tag in ("input", "select", "textarea"):
            t = a.get("type", "text").lower()
            if t not in ("hidden", "submit", "button", "reset", "image"):
                has_aria = bool(a.get("aria-label") or a.get("aria-labelledby") or a.get("title"))
                if self._label_depth:
                    self.inputs_in_label += 1
                else:
                    self.inputs.append((a.get("id"), t, has_aria))
        if tag in ("a", "button"):
            has_label = bool(a.get("aria-label") or a.get("aria-labelledby") or a.get("title"))
            self._stack.append([tag, "", has_label, False])

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag == "label":
            self._label_depth = max(0, self._label_depth - 1)
        elif tag in ("a", "button"):
            for i in range(len(self._stack) - 1, -1, -1):
                if self._stack[i][0] == tag:
                    _, text, has_label, has_img_alt = self._stack.pop(i)
                    if not text.strip() and not has_label and not has_img_alt:
                        if tag == "a":
                            self.empty_links += 1
                        else:
                            self.empty_buttons += 1
                    break

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        for item in self._stack:
            item[1] += data


def check_page(path):
    p = PageParser()
    with open(path, encoding="utf-8", errors="replace") as f:
        p.feed(f.read())
    issues = []
    title = p.title.strip()
    desc = p.meta.get("description", "").strip()

    if not title:
        issues.append(("error", "Missing <title>"))
    elif not 15 <= len(title) <= 65:
        issues.append(("warn", f"Title length {len(title)} (aim ~50-60)"))
    if not desc:
        issues.append(("error", "Missing meta description"))
    elif not 70 <= len(desc) <= 170:
        issues.append(("warn", f"Meta description length {len(desc)} (aim ~140-160)"))
    if not p.lang:
        issues.append(("error", "Missing <html lang>"))
    if not p.viewport:
        issues.append(("error", "Missing viewport meta"))
    if not p.canonical:
        issues.append(("warn", "Missing canonical link"))
    if "noindex" in p.meta.get("robots", "").lower():
        issues.append(("warn", "Page is noindex (OK for staging/private pages only)"))
    missing_og = [k for k in ("og:title", "og:description", "og:image") if not p.meta.get(k)]
    if missing_og:
        issues.append(("warn", "Missing Open Graph: " + ", ".join(missing_og)))
    og_img = p.meta.get("og:image", "")
    if og_img and not og_img.startswith("http"):
        issues.append(("warn", "og:image should be an absolute URL"))
    if not p.meta.get("twitter:card"):
        issues.append(("info", "Missing twitter:card"))

    h1 = p.headings.count(1)
    if h1 == 0:
        issues.append(("error", "No <h1>"))
    elif h1 > 1:
        issues.append(("warn", f"{h1} <h1> elements (use one)"))
    for prev, cur in zip(p.headings, p.headings[1:]):
        if cur > prev + 1:
            issues.append(("warn", f"Heading level skips h{prev} -> h{cur}"))
            break

    if p.imgs_no_alt:
        issues.append(("error", f"{p.imgs_no_alt} <img> without alt attribute"))
    unlabeled = [i for i in p.inputs if not i[2] and not (i[0] and i[0] in p.label_fors)]
    if unlabeled:
        issues.append(("error", f"{len(unlabeled)} form field(s) without a label"))
    if p.empty_links:
        issues.append(("error", f"{p.empty_links} link(s) with no accessible text"))
    if p.empty_buttons:
        issues.append(("error", f"{p.empty_buttons} button(s) with no accessible text"))
    if p.ld_json == 0:
        issues.append(("info", "No JSON-LD structured data"))
    return title, desc, issues


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json = "--json" in sys.argv
    if not args:
        print(__doc__)
        sys.exit(1)
    target = args[0]
    files = []
    if os.path.isfile(target):
        files = [target]
        root = os.path.dirname(target) or "."
    else:
        root = target
        for dp, dns, fns in os.walk(target):
            dns[:] = [d for d in dns if d not in SKIP_DIRS]
            files += [os.path.join(dp, f) for f in fns if f.endswith(".html")]
    files.sort()
    if not files:
        print(f"No .html files found in {target}. Build/export the site first (e.g. dist/, out/, build/).")
        sys.exit(1)

    results, titles, descs = {}, defaultdict(list), defaultdict(list)
    for f in files:
        rel = os.path.relpath(f, root)
        title, desc, issues = check_page(f)
        results[rel] = issues
        if title:
            titles[title].append(rel)
        if desc:
            descs[desc].append(rel)

    site = []
    for t, pages in titles.items():
        if len(pages) > 1:
            site.append(("warn", f"Duplicate title on {len(pages)} pages: \"{t[:50]}\""))
    for d, pages in descs.items():
        if len(pages) > 1:
            site.append(("warn", f"Duplicate description on {len(pages)} pages"))
    if os.path.isdir(target):
        for name in ("robots.txt", "sitemap.xml"):
            if not any(os.path.exists(os.path.join(target, sub, name)) for sub in ("", "public")):
                site.append(("warn", f"No {name} found in output"))

    if as_json:
        print(json.dumps({"pages": results, "site": site}, indent=2))
        return

    icon = {"error": "❌", "warn": "⚠️ ", "info": "ℹ️ "}
    counts = defaultdict(int)
    for rel, issues in results.items():
        print(f"\n{rel}")
        if not issues:
            print("  ✅ no issues")
        for sev, msg in issues:
            counts[sev] += 1
            print(f"  {icon[sev]} {msg}")
    if site:
        print("\nSite-wide")
        for sev, msg in site:
            counts[sev] += 1
            print(f"  {icon[sev]} {msg}")
    print(f"\n{len(files)} page(s): {counts['error']} errors, {counts['warn']} warnings, {counts['info']} info")
    sys.exit(1 if counts["error"] else 0)


if __name__ == "__main__":
    main()
