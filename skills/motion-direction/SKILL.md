---
name: motion-direction
description: Art-direct animation for websites that mix normal content with "wow" motion — decide what to animate and what to keep still, pick the right tool (CSS, Motion for React, GSAP + ScrollTrigger, Lenis, Three.js/R3F, Lottie, View Transitions), set a motion system (durations, easing, stagger), and keep it fast, accessible and mobile-safe. Use whenever the user wants an animated, interactive, award-style or "keren" website, landing page, portfolio, hero, scroll effect, page transition, or asks "tambahin animasi", "biar lebih hidup", "kayak website Awwwards", even before choosing a library.
---

# Motion Direction

Great animated sites are **mostly calm** with a few moments that land hard. Motion supports the content; it never replaces it or blocks reading.

## 1. Plan the rhythm before coding
Write a motion plan per section, as a table, and show it to the user for anything bigger than a single component:

| Section | Role | Motion level | Effect | Tool |
|---|---|---|---|---|
| Hero | first impression | 🔥 signature | split-text reveal + 3D object reacting to cursor | GSAP SplitText, R3F |
| Logos | proof | 💤 still | none (or slow marquee) | CSS |
| Features | explain | 🌊 light | fade-up + stagger on enter | Motion / GSAP |
| Showcase | wow #2 | 🔥 signature | pinned horizontal scroll | GSAP ScrollTrigger |
| Pricing / form | convert | 💤 still | only micro-interactions | CSS |
| Footer | close | 🌊 light | big type parallax | GSAP |

Rules of rhythm:
- **1–3 signature moments per page.** Everything else is light or still. Alternate intense → calm → intense.
- Never animate what the user must read *right now* or must act on (prices, forms, error messages, nav).
- Every animation must answer "what does this communicate?" — hierarchy, continuity, feedback, or delight. "Because it looks cool" is allowed only for the signature moments.
- Content must be readable with JS disabled or before animation runs — no `opacity: 0` content that only appears if a script succeeds (set initial hidden states from JS, or with a `.js` class on `<html>`).

## 2. Choose the tool (smallest that works)

| Need | Use |
|---|---|
| Hover, focus, button press, simple fades | **CSS** transitions/keyframes |
| React UI: mount/unmount, layout changes, gestures, shared elements, modals, tabs | **Motion for React** (`npm i motion`, `import { motion } from "motion/react"`) → `react-motion` skill |
| Scroll-driven storytelling: pin, scrub, horizontal scroll, parallax, text split, timelines | **GSAP + ScrollTrigger** (+ SplitText, Flip — all free now) → `scroll-animation` skill |
| Smooth/inertia scrolling | **Lenis** (synced to GSAP ticker) |
| Page-to-page transitions | View Transitions API (native, Astro/Next support), or Motion `AnimatePresence`, or Barba.js for multi-page static sites |
| 3D, shaders, particles, interactive objects | **Three.js / React Three Fiber** → `web-3d` skill. Quick designer-made 3D: Spline |
| Designer-made vector animation (icons, illustrations) | **Lottie** (`lottie-web` / `@lottiefiles/dotlottie-*`) or Rive |
| Simple scroll-linked CSS only | CSS `animation-timeline: view()` / `scroll()` with `@supports` fallback |

Don't mix GSAP and Motion on the same element. Mixing them on the same page is fine (Motion for UI, GSAP for scroll scenes).

## 3. Motion system (define once, reuse)
Put tokens in one file (`motion.ts` / CSS variables):
```ts
export const dur = { fast: 0.15, base: 0.3, slow: 0.6, cinematic: 1.2 }; // seconds
export const ease = {
  out: "cubic-bezier(0.22, 1, 0.36, 1)",      // entrances (GSAP: "expo.out" / "power3.out")
  inOut: "cubic-bezier(0.65, 0, 0.35, 1)",    // moving between states
  in: "cubic-bezier(0.55, 0, 1, 0.45)",       // exits (keep exits ~30% faster than entrances)
};
export const stagger = { tight: 0.04, base: 0.08, loose: 0.15 };
```
- Micro-interactions 100–200ms; UI transitions 200–400ms; reveals 500–900ms; signature/hero up to ~1.5s total.
- Entrances: `ease-out`. Exits: faster, `ease-in`. Never linear except for scrubbed scroll and marquees.
- Small distances: reveal with 16–40px translate, not 100px+.
- Stagger lists but cap the total (e.g. max 8 items staggered; the rest appear together).

## 4. Performance budget (non-negotiable)
- Animate only `transform` and `opacity` (and `filter`/`clip-path` sparingly). Never `top/left/width/height/margin` — use `scale`/`translate` or FLIP.
- `will-change` only on elements actively animating; remove after.
- No scroll event listeners doing work — use ScrollTrigger, IntersectionObserver, or CSS scroll timelines.
- Lazy-load heavy stuff (Three.js, Lottie files, big GSAP scenes) with dynamic import when near viewport.
- Target 60fps on a mid-range Android phone. Test with CPU 4× throttling in DevTools Performance panel.
- Hero must not hurt LCP: the LCP text/image should be visible fast; animate *in* quickly, don't wait for a 3D scene to load.

## 5. Accessibility & mobile
- Always respect reduced motion: replace big movement with opacity fades or nothing.
  - CSS: `@media (prefers-reduced-motion: reduce) { ... }`
  - GSAP: `gsap.matchMedia()` with `"(prefers-reduced-motion: no-preference)"`
  - Motion: `<MotionConfig reducedMotion="user">`
- Nothing flashes more than 3 times per second. No auto-playing motion longer than 5s without a way to pause (marquees, video backgrounds).
- Mobile: simplify. Pinned horizontal scroll → vertical stack; cursor effects → disabled on touch (`(hover: hover) and (pointer: fine)`); reduce particle counts / 3D quality.
- Smooth scroll must not break: anchor links, browser find, keyboard scrolling, `position: sticky`.

## 6. Verify
Run `python3 scripts/motion_lint.py <src-dir>` to catch common anti-patterns (layout-property animation, missing reduced-motion handling, ScrollTrigger without cleanup, scroll listeners).
Then check in a browser at 375px and 1440px, with reduced motion ON and OFF, and with CPU throttling. Report the motion plan, what was built, and any device-specific fallbacks.

Finally run the `visual-qa` skill: capture intro and scroll filmstrips and score the result. Motion you haven't looked at frame by frame is not done.

References:
- `references/premium-craft.md` — **read this before writing any animation**: basic → premium translations, choreography template, layering/depth, signature-moment ideas. This is what separates a template look from an award-style site.
- `references/patterns.md` — ready-to-adapt code recipes for popular effects.
