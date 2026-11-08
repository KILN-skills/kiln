# Premium motion craft — from "basic" to "award-style"

The difference is rarely the library. It's choreography, easing, layering, and restraint.

## Basic → premium translations

| Looks basic | Do this instead |
|---|---|
| Whole block fades up | Split into parts: label first, then headline by line (masked), then body, then CTA — overlapping, not sequential |
| `opacity 0→1, y 50→0, 0.5s ease` | `yPercent: 110 → 0` inside an `overflow: hidden` mask, `1.1s expo.out` — text "rises from a slot" |
| Same fade-up on every section | One motion idea per section that matches its content (numbers count, images unmask, lists cascade, quotes highlight word-by-word) |
| Things start one after another | Overlap with timeline position params: `"<0.15"`, `"-=0.6"` — the next motion starts before the last finishes |
| All durations 0.3s | Scale duration with distance & size: small UI 0.2–0.35s, text lines 0.8–1.1s, full-screen images 1.2–1.6s |
| `ease` / `ease-in-out` | Entrances `expo.out` / `power4.out` (`cubic-bezier(0.16,1,0.3,1)`); big moves between states `expo.inOut`; scrub `none` |
| Image just fades in | Unmask with `clip-path: inset()` while the image inside scales `1.3 → 1` slower than the mask (two speeds = depth) |
| Flat parallax on one image | 3 depth layers at different speeds (bg 0.8, mid 1, fg 1.15) + slight scale on the bg |
| Hover = color change | Underline draws from left (`scaleX` origin left), exits to the right; image preview follows cursor on list hover; button text rolls up and is replaced by a copy from below |
| Stagger `0.1` in DOM order | Stagger from a meaningful origin: `stagger: { each: 0.05, from: "center" }` or `"edges"`, or by grid position (`grid: "auto"`) |
| Section snaps in when reached | Scrub tied to scroll for signature moments (the user "drives" it), `scrub: 0.8–1.2` for a slight smoothing lag |
| Nothing happens while idle | Very subtle ambient life in the hero: slow gradient drift, grain, a 3D object breathing, cursor-reactive light — low amplitude |
| Page loads → content | Short preloader/intro (≤ 1.2s, skip on revisit via sessionStorage) that hands off into the hero animation, so the first frame is designed |
| Hard page navigation | Page transition: overlay wipe or shared-element morph (View Transitions / Barba / Motion `layoutId`) |

## Choreography template (hero)
```js
const tl = gsap.timeline({ defaults: { ease: "expo.out", duration: 1.1 } });
tl.from(".hero__eyebrow", { yPercent: 100, autoAlpha: 0, duration: 0.8 })
  .from(split.lines, { yPercent: 110, stagger: 0.08 }, "<0.1")
  .fromTo(".hero__media", { clipPath: "inset(100% 0 0 0)" }, { clipPath: "inset(0% 0 0 0)", duration: 1.4, ease: "expo.inOut" }, "<0.2")
  .from(".hero__media img", { scale: 1.35, duration: 1.8 }, "<")
  .from(".hero__cta, .nav", { autoAlpha: 0, y: 12, stagger: 0.06, duration: 0.6 }, "-=0.9");
```
Rule of thumb: total ≤ 1.5s, the headline is readable by ~0.6s, the nav/CTA arrive last.

## Layering & depth
- Put type **over** imagery (with `mix-blend-mode: difference` or a scrim) instead of side by side.
- Foreground elements (stickers, small images, shapes) moving at a different scroll speed than the section create depth cheaply.
- Grain overlay: a fixed, `pointer-events: none` layer with a tiny noise PNG/SVG at 4–8% opacity removes the "flat digital" look.
- Light: a large blurred radial gradient that slowly drifts or follows the cursor at 10–20% opacity.

## Signature moment ideas (pick 1–3 per page)
- **Sticky stack**: cards pinned, each new card slides over the previous one which scales down to 0.9 and darkens.
- **Horizontal gallery** with images skewing slightly by scroll velocity (`ScrollTrigger` `getVelocity()` → `skewX`, clamped).
- **Big type marquee** whose direction and speed follow scroll direction.
- **Zoom-through**: a small framed image scales up to fill the screen as you scroll, revealing the next section inside it.
- **Text fill**: huge statement whose words go from 15% to 100% opacity as you scroll through it.
- **Image trail**: images spawn and fade along the cursor path in the hero (pointer devices only).
- **WebGL hover distortion** on project images (wave/RGB shift shader on hover) — see `web-3d`.
- **Counter + chart draw**: stats count up while SVG lines draw (`DrawSVG` or `stroke-dashoffset`).

## Restraint checklist
- Is there at least one calm section between two signature moments?
- Can someone who just wants the info (prices, contact) get it in 2 seconds without waiting for motion?
- Does reduced motion still look intentional (not broken/empty)?
- On mobile, is every signature moment either simplified or still smooth at 60fps?
