---
name: scroll-animation
description: Build scroll-driven animations with GSAP, ScrollTrigger, SplitText and Lenis smooth scroll — reveals, pinned sections, horizontal scroll, parallax, scrubbed timelines, text effects — in vanilla JS, React, Next.js, Vue/Nuxt, or Astro, with correct setup, cleanup and responsive fallbacks. Use whenever the user mentions GSAP, ScrollTrigger, Lenis, smooth scroll, parallax, pin, scrub, "animasi saat scroll", horizontal scroll, or scroll storytelling.
---

# Scroll Animation (GSAP + ScrollTrigger + Lenis)

If GreenSock's official skills (`gsap-core`, `gsap-scrolltrigger`, `gsap-react`, `gsap-plugins`) are installed, use them for API details; this skill covers project setup, integration and the mistakes that break real sites.

## 1. Install
```
npm i gsap lenis
npm i @gsap/react   # React / Next.js only
```
All GSAP plugins (ScrollTrigger, SplitText, Flip, ScrollSmoother, MorphSVG, DrawSVG…) ship in the public `gsap` package and are free for commercial use. Import from `gsap/<PluginName>` and call `gsap.registerPlugin(...)` once.

## 2. One setup module
Create `lib/motion/setup.(js|ts)` (or `animations/`) that is imported once on the client:
```js
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { SplitText } from "gsap/SplitText";
import Lenis from "lenis";
import "lenis/dist/lenis.css";

gsap.registerPlugin(ScrollTrigger, SplitText);

export function initSmoothScroll() {
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) return null;
  const lenis = new Lenis();
  lenis.on("scroll", ScrollTrigger.update);
  const tick = (time) => lenis.raf(time * 1000); // GSAP time is seconds, Lenis wants ms
  gsap.ticker.add(tick);
  gsap.ticker.lagSmoothing(0);
  return () => { gsap.ticker.remove(tick); lenis.destroy(); };
}
```
Use either Lenis **or** GSAP ScrollSmoother, not both.

## 3. Framework integration
**React / Next.js (App Router)** — files using GSAP need `"use client"`. Always use `useGSAP` (auto-cleanup, no double-run in Strict Mode):
```tsx
"use client";
import { useRef } from "react";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";
import { ScrollTrigger } from "gsap/ScrollTrigger";
gsap.registerPlugin(useGSAP, ScrollTrigger);

export function Features() {
  const root = useRef<HTMLElement>(null);
  useGSAP(() => {
    const mm = gsap.matchMedia();
    mm.add("(prefers-reduced-motion: no-preference)", () => {
      gsap.from(".feature", {
        autoAlpha: 0, y: 32, stagger: 0.08, ease: "power3.out",
        scrollTrigger: { trigger: root.current, start: "top 75%" },
      });
    });
  }, { scope: root }); // selectors are scoped to this component
  return <section ref={root}>…</section>;
}
```
- Event handlers that create animations: wrap with `contextSafe` from `useGSAP`.
- Smooth scroll provider: a client component in the root layout that calls `initSmoothScroll()` in an effect (or `ReactLenis` from `lenis/react` with `autoRaf: false` and the GSAP ticker).
- Route change in Next.js: scroll to top (`lenis.scrollTo(0, { immediate: true })`) and `ScrollTrigger.refresh()` after the new page mounts.

**Vue / Nuxt** — create in `onMounted` inside `gsap.context(() => {…}, rootEl)`, call `ctx.revert()` in `onUnmounted`. Nuxt: client-only plugin (`plugins/gsap.client.ts`).

**Astro / static multi-page** — a `<script>` in the layout; with View Transitions, re-init on `astro:page-load` and kill triggers on `astro:before-swap`.

**Vanilla** — one `main.js` that runs after DOM ready; group per section in `gsap.context()`.

## 4. ScrollTrigger rules that prevent 90% of bugs
- Put `scrollTrigger` on a **timeline** or top-level tween — never on tweens nested inside a timeline.
- Use `ease: "none"` with `scrub`.
- Creation order matters: create triggers top-to-bottom in page order (or set `refreshPriority`), especially with pinning.
- Pin a wrapper, not the element you animate. Don't pin inside a `transform`ed parent. Avoid `pinSpacing: false` unless intentional.
- Use function values (`x: () => …`) + `invalidateOnRefresh: true` for anything depending on viewport size.
- Call `ScrollTrigger.refresh()` after images/fonts/dynamic content change layout (`window.addEventListener("load", …)`, `document.fonts.ready`).
- Debug with `markers: true` — remove before shipping.
- Initial hidden states: use `gsap.from`/`fromTo` or `autoAlpha` set by JS, so content is visible without JS.
- `once: true` for reveals that shouldn't replay (most of them).

## 5. Responsive & reduced motion
Wrap every scene in `gsap.matchMedia()`:
```js
const mm = gsap.matchMedia();
mm.add({
  isDesktop: "(min-width: 1024px)",
  isMobile: "(max-width: 1023px)",
  motionOK: "(prefers-reduced-motion: no-preference)",
}, ({ conditions: c }) => {
  if (!c.motionOK) return;            // static layout, no animation
  if (c.isDesktop) { /* pinned / horizontal scenes */ }
  if (c.isMobile)  { /* simple fade-ups only */ }
});
```
matchMedia reverts automatically when conditions change — no manual cleanup.

## 6. Performance
- Animate `x/y/scale/rotation/autoAlpha` (transforms + opacity). Avoid animating `width/height/top/left` and heavy `filter: blur()` on large areas.
- Prefer one timeline per section over dozens of separate triggers; `ScrollTrigger.batch` for many identical reveals.
- `gsap.quickTo` for pointer-follow effects.
- Big images inside scrubbed scenes: proper `sizes`, and avoid scaling huge bitmaps every frame.

## 7. Verify
Scroll the whole page up and down fast; resize the window; reload mid-page; navigate away and back (SPA) — no jumps, no duplicated pins, no console errors. Test with reduced motion on, at 375px, and with CPU throttling.

Recipes for common effects: `../motion-direction/references/patterns.md`.
