# Popular effect recipes

Pick, adapt to the project's tokens, and always include the reduced-motion fallback.

## Hero headline reveal (line by line, masked)
GSAP + SplitText:
```js
import gsap from "gsap";
import { SplitText } from "gsap/SplitText";
gsap.registerPlugin(SplitText);

document.fonts.ready.then(() => {
  const split = SplitText.create(".hero-title", { type: "lines", mask: "lines" });
  gsap.from(split.lines, { yPercent: 110, duration: 1, ease: "expo.out", stagger: 0.08 });
});
```
Wait for fonts, or line breaks will be wrong. Keep `aria-label`/real text intact (SplitText handles a11y by default).

## Fade-up on enter (the workhorse)
Motion for React:
```tsx
<motion.div
  initial={{ opacity: 0, y: 24 }}
  whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true, amount: 0.3 }}
  transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
/>
```
GSAP batch for many items:
```js
ScrollTrigger.batch(".reveal", {
  start: "top 85%",
  onEnter: (els) => gsap.fromTo(els, { autoAlpha: 0, y: 24 }, { autoAlpha: 1, y: 0, stagger: 0.08, ease: "power3.out" }),
  once: true,
});
```

## Pinned horizontal scroll section
```js
const track = document.querySelector(".h-track");
const mm = gsap.matchMedia();
mm.add("(min-width: 768px) and (prefers-reduced-motion: no-preference)", () => {
  gsap.to(track, {
    x: () => -(track.scrollWidth - window.innerWidth),
    ease: "none",
    scrollTrigger: {
      trigger: ".h-section", pin: true, scrub: 1,
      end: () => "+=" + (track.scrollWidth - window.innerWidth),
      invalidateOnRefresh: true,
    },
  });
});
// below 768px the track is a normal vertical stack via CSS
```

## Parallax layers
```js
gsap.utils.toArray("[data-speed]").forEach((el) => {
  gsap.to(el, {
    yPercent: () => (1 - parseFloat(el.dataset.speed)) * 100,
    ease: "none",
    scrollTrigger: { trigger: el.parentElement, start: "top bottom", end: "bottom top", scrub: true },
  });
});
```
Keep movement small (speed 0.8–1.2). Big parallax causes motion sickness.

## Text highlight as you scroll (word by word)
```js
const split = SplitText.create(".manifesto", { type: "words" });
gsap.fromTo(split.words, { opacity: 0.15 }, {
  opacity: 1, stagger: 0.05, ease: "none",
  scrollTrigger: { trigger: ".manifesto", start: "top 75%", end: "bottom 40%", scrub: true },
});
```

## Image reveal with clip-path
```js
gsap.fromTo(".reveal-img", { clipPath: "inset(100% 0 0 0)" }, {
  clipPath: "inset(0% 0 0 0)", duration: 1.2, ease: "expo.inOut",
  scrollTrigger: { trigger: ".reveal-img", start: "top 80%" },
});
```

## Number counter
```js
const obj = { v: 0 };
gsap.to(obj, {
  v: 1250, duration: 1.5, ease: "power2.out",
  onUpdate: () => (el.textContent = Math.round(obj.v).toLocaleString("id-ID")),
  scrollTrigger: { trigger: el, start: "top 85%", once: true },
});
```

## Magnetic button (pointer devices only)
```js
if (matchMedia("(hover: hover) and (pointer: fine)").matches) {
  const xTo = gsap.quickTo(btn, "x", { duration: 0.4, ease: "power3" });
  const yTo = gsap.quickTo(btn, "y", { duration: 0.4, ease: "power3" });
  btn.addEventListener("pointermove", (e) => {
    const r = btn.getBoundingClientRect();
    xTo((e.clientX - r.left - r.width / 2) * 0.3);
    yTo((e.clientY - r.top - r.height / 2) * 0.3);
  });
  btn.addEventListener("pointerleave", () => { xTo(0); yTo(0); });
}
```

## Custom cursor follower
Same `quickTo` pattern on a fixed `pointer-events: none` dot. Hide on touch devices, keep the native cursor visible (don't `cursor: none` on links/inputs).

## Infinite marquee (CSS only)
```css
.marquee { overflow: hidden; }
.marquee__track { display: flex; width: max-content; animation: marquee 30s linear infinite; }
.marquee:hover .marquee__track { animation-play-state: paused; }
@keyframes marquee { to { transform: translateX(-50%); } } /* content duplicated twice */
@media (prefers-reduced-motion: reduce) { .marquee__track { animation: none; } }
```

## Shared-element / layout animation (React)
```tsx
<motion.div layoutId={`card-${id}`} /> // in list
<motion.div layoutId={`card-${id}`} /> // in expanded modal, wrapped in <AnimatePresence>
```

## Native page transitions (View Transitions API)
```css
@view-transition { navigation: auto; } /* cross-document, multi-page sites */
::view-transition-old(root) { animation: 200ms ease-in both fade-out; }
::view-transition-new(root) { animation: 300ms ease-out both fade-in; }
```
Name elements with `view-transition-name: hero-image;` to morph them between pages. Progressive enhancement: unsupported browsers just navigate normally.

## Scroll-linked progress bar (CSS only)
```css
.progress { transform-origin: 0 50%; animation: grow linear both; animation-timeline: scroll(root); }
@keyframes grow { from { transform: scaleX(0); } to { transform: scaleX(1); } }
```
