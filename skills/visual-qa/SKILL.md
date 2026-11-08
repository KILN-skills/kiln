---
name: visual-qa
description: Actually look at the website being built — screenshots at mobile and desktop, filmstrips of the intro animation and of scrolling — then critique it like an art director against a "basic vs premium" rubric and iterate until it no longer looks generic. Use after building or changing any page, section, hero, image treatment or animation; whenever the user says it looks basic, plain, boring, "kurang wow", "masih biasa", "kayak template", "belum keren", asks for feedback on the design, or before calling any visual work done.
---

# Visual QA — see it, judge it, push it

Code that "should" look good often doesn't. Never report visual work as done without looking at it.

## 1. Run the site and capture
Start the dev server (or use a built HTML file), then:
```
python3 scripts/capture.py http://localhost:3000 --out .visual-qa
```
First time only: `pip install playwright pillow && python3 -m playwright install chromium`.
For a specific page or section, pass its URL (e.g. `/#work`). Add `.visual-qa/` to `.gitignore`.

Then **Read** these images and look carefully:
- `full_1440.png`, `full_375.png` — overall composition, rhythm, mobile layout
- `intro_sheet.png` — the first ~1.6s: is there an intro moment? Is it choreographed or does everything fade at once?
- `scroll_sheet.png` — do sections enter with intent? Anything empty, half-revealed, or jumping?
- `reduced_*.png` — content fully visible without motion?
- `report.json` — overflow offenders, broken/blurry images, console errors, CLS, fonts in use

If the user can share a reference site they love, capture it the same way and compare side by side — the gap is usually obvious once both are on screen.

## 2. Critique with the rubric
Score each 1–5 and write one concrete observation per line. Be honest — a 2 is a 2.

| Area | Basic (1–2) | Premium (4–5) |
|---|---|---|
| **Typography** | one size jump, default weights, system font, centered everything | dramatic scale contrast (display 6–12vw vs small labels), tight tracking on big type, characterful display font + quiet text font, deliberate alignment (often left / asymmetric) |
| **Composition** | every section = centered title + 3 cards, same height, same padding | varied section structures, grid-breaking elements, overlap, asymmetry, purposeful whitespace, a clear focal point per screen |
| **Color & surface** | flat background, one accent everywhere | restrained palette, tonal depth (layered surfaces, subtle gradients, grain/noise, light), accent used rarely so it pops |
| **Imagery** | stock photos dropped in raw, mismatched styles, rectangles only | consistent art direction & treatment, crops with intent, masks/shapes, depth (foreground over image), images integrated with type (see `visual-assets`) |
| **Intro moment** | text fades in, or nothing | choreographed sequence: staggered line reveal, image unmask, nav arrives last; overlap between steps; total ≤ 1.5s |
| **Scroll motion** | every block does the same fade-up | each section has its own motion idea matching its content; 1–3 signature moments (pin, scrub, parallax depth, text that reacts); calm sections in between |
| **Easing & timing** | `ease`/linear, all 300ms, things start together | custom curves (expo/quart out), durations vary by distance/size, overlapping starts (`"-=0.4"`), stagger from a meaningful origin |
| **Interaction** | color change on hover only | hover reveals (image preview on link hover, underline draw, magnetic CTA), cursor feedback, state changes animated with physics |
| **Detail** | default focus rings, abrupt states | polished states everywhere, consistent radii, optical alignment, no orphan words in headings |

## 3. Turn the lowest scores into specific changes
Pick the **3 lowest-scoring areas** and propose specific changes — not "make it more modern", but e.g.:
- "Hero h1 is 64px centered; make it 11vw, left-aligned, two lines, split into lines with a masked yPercent reveal staggered 0.08s, image unmask starts at -0.6s overlap."
- "Features section repeats the 3-card pattern; switch to a sticky left title + scrolling right list where each item scales its number on enter."
- "Photos are mismatched stock; apply a unified duotone + grain treatment and crop all to 4:5 (see visual-assets)."

Use `../motion-direction/references/premium-craft.md` for the motion upgrades and `visual-assets` for images.

## 4. Iterate
Implement → capture again → compare with the previous capture → re-score. Do at least **two passes** for any hero or signature section. Stop when every area is ≥ 4 or the remaining gaps need the user's input (real photos, brand fonts, copy).

## 5. Report
Show the before/after scores, the key changes made, and the images (send the final `full_1440.png` and `intro_sheet.png` to the user if they can't see your screen). List what would push it further but needs their decision or assets.
