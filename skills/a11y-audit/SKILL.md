---
name: a11y-audit
description: Audit and fix website accessibility to WCAG 2.2 AA — semantic HTML, keyboard navigation, focus, labels, alt text, color contrast, ARIA, and screen-reader behavior — in React/Next.js, Vue, or plain HTML. Use whenever the user mentions accessibility, a11y, WCAG, screen readers, keyboard navigation, contrast, or is building forms, modals, menus, dropdowns, or preparing a site for launch.
---

# Accessibility Audit

## 1. Automated pass (catches ~30–40%)
- Static HTML/build output: `python3 ../seo-setup/scripts/site_check.py <dist-or-out-dir-or-html-file>` — reports missing alt, labels, lang, heading order, empty links/buttons.
- Running site, if available: `npx @axe-core/cli <url>` or `npx pa11y <url>`.
- Lint: `eslint-plugin-jsx-a11y` (React) / `eslint-plugin-vuejs-accessibility` (Vue) — suggest adding if missing.

## 2. Manual checks (the important 60%)
**Keyboard**
- Tab through the whole page: every interactive element reachable, in a logical order, with a visible focus ring.
- No keyboard traps. `Esc` closes modals/menus. Skip link to main content on content-heavy sites.
- Clickable `div`/`span` → replace with `<button>` or `<a href>`. Links navigate, buttons act.

**Semantics & structure**
- One `<h1>`; headings don't skip levels. Landmarks: `header`, `nav`, `main`, `footer`.
- `<html lang="id">` (or correct language).
- Lists are `ul/ol`; data tables use `th` with `scope`.

**Forms**
- Every input has a `<label for>` (placeholder is not a label). Group radios/checkboxes with `fieldset`/`legend`.
- Errors: text near the field, linked via `aria-describedby`, field marked `aria-invalid="true"`; don't rely on red color alone.
- Correct `type` and `autocomplete` (`email`, `tel`, `name`, `current-password`).

**Images & media**
- Informative images: alt describing purpose. Decorative: `alt=""`. Icon-only buttons: `aria-label`.
- Video: captions; no autoplay with sound.

**Color & motion**
- Contrast ≥ 4.5:1 text, ≥ 3:1 large text & UI components/focus indicators.
- Info not conveyed by color alone. Respect `prefers-reduced-motion`.
- Content usable at 200% zoom and 320px width.

**Dynamic components**
- Prefer native elements (`<dialog>`, `<details>`, `<select>`) or a vetted library (Radix, Headless UI, React Aria) over hand-rolled ARIA.
- Modal: focus moves in, is trapped, returns to trigger on close; background `inert`.
- Live updates (toasts, form submit result): `aria-live="polite"` / `role="status"`.
- First rule of ARIA: don't use ARIA if native HTML works.

## 3. Report & fix
Group by severity: **Blocker** (can't complete a task with keyboard/screen reader), **Serious**, **Moderate**. For each: element/file, WCAG criterion (e.g. 1.1.1, 2.4.7), fix. Then apply fixes if the user agrees and re-run the automated checks.
