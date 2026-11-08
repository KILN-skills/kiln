---
name: visual-assets
description: Make website imagery look art-directed instead of basic — choose one visual style, source or generate images (photos, AI images, 3D renders, illustrations), unify them with consistent crops and color treatment, and present them with masks, layering, image effects and textured backgrounds; export optimized responsive images. Use whenever the user's site has images, photos, illustrations, icons, backgrounds, hero visuals or galleries, says images look plain/stock/"gambarnya biasa", needs images for a section, or wants AI image prompts.
---

# Visual Assets — imagery with art direction

Basic sites drop raw stock photos into rectangles. Premium sites treat imagery as a **system**: one style, consistent treatment, composed with the type and motion.

## 1. Define the image direction (write it down first)
One short spec the whole site follows:
```
Style:     documentary photography, natural light, warm film grade, subtle grain
Subjects:  people's hands at work, materials close-up, spaces with depth
Crops:     4:5 portrait for features, 21:9 for full-bleed breaks, 1:1 for team
Treatment: warm-film + grain 0.05; on dark sections duotone (#14110f / #f1e6d2)
Shapes:    soft radius 4px OR arch tops for hero only — not both everywhere
Never:     smiling-at-camera stock, mixed lighting styles, rounded-2xl + shadow on every image
```
Derive it from the brand: a law firm ≠ a coffee shop ≠ a creative studio. If the user has real photos, they win over stock — build the direction around them.

## 2. Source or generate
Priority: user's own photos → custom 3D renders/illustrations → AI-generated set → curated stock (Unsplash/Pexels — check license; credit if required).

**AI image prompts** — generate a *set*, not one-offs. Use one fixed style block appended to every prompt so the series matches:
```
[subject], [composition: e.g. close-up / wide with negative space on the left for text],
STYLE: editorial photography, 35mm film look, soft natural window light, warm muted palette
(terracotta, sand, deep brown), shallow depth of field, subtle grain, no text, no logos
```
Ask for the composition you need for the layout (empty space where the headline goes, subject facing into the page). Generate 3–4 variants, pick, then treat with the script below so they match exactly. Never generate images of real identifiable people or copyrighted characters/brands.

**Illustrations / icons**: one family only (same stroke width, corner style, palette). For icons use one set (Lucide, Phosphor, Tabler) at one stroke weight.

## 3. Unify with the treatment script
```
python3 scripts/image_treat.py raw/ public/images/ \
  --ratio 4:5 --look warm-film --grain 0.05 --width 1600
```
Looks: `warm-film`, `cool-film`, `duotone` (`--dark --light`), `mono`, `fade`. It crops to one ratio (with `--focus x,y`), grades, adds grain, and exports WebP + half-size for `srcset`. Even mismatched stock photos look like one shoot after this.

## 4. Present images with intent (CSS)
Pick 2–3 of these per site, not all:
- **Masks & shapes**: `clip-path: inset(0 round 999px 999px 0 0)` (arch), `clip-path: polygon(...)`, SVG masks, text-as-mask (`background-clip: text` with an image).
- **Layering**: image partially behind the headline; small secondary image overlapping a large one (offset grid); caption/label chips on the image.
- **Live duotone in CSS** (switchable on hover):
  ```css
  .duo { position: relative; background: #f1e6d2; }
  .duo img { filter: grayscale(1) contrast(1.1); mix-blend-mode: multiply; }
  .duo::after { content: ""; position: absolute; inset: 0; background: #14110f; mix-blend-mode: lighten; }
  ```
- **Grain overlay** for the whole page: a fixed `::after` with a small noise SVG (`feTurbulence`) at 4–8% opacity, `pointer-events: none`.
- **Backgrounds that aren't flat**: large blurred radial gradients (mesh look), subtle noise, thin grid/lines, a giant outlined word behind content.
- **Framing**: generous padding around a single image, thin 1px borders, image + monospaced caption + index number (`01 — Studio`) feels editorial.
- **Full-bleed breaks**: one edge-to-edge 21:9 image between dense sections to reset the rhythm.

## 5. Image motion (pair with `scroll-animation`)
- **Unmask reveal**: clip-path wipe on the frame + inner image scales 1.3 → 1 slower (two speeds).
- **Inner parallax**: image is 120% of its frame height and moves `yPercent -10 → 10` while scrolling; the frame stays still.
- **Hover**: zoom inside frame (`scale 1.06`, 0.8s expo.out) + caption slides up; on lists, a floating preview image follows the cursor.
- **Gallery**: horizontal drag/scroll, skew by scroll velocity, or sticky stack.
- **WebGL**: distortion/RGB-shift on hover, liquid transitions between slides — see `web-3d`. Use for 1 signature gallery only.

## 6. Technical quality (non-negotiable)
- Correct `width`/`height` or `aspect-ratio` on every image (no CLS).
- `srcset` + `sizes`; hero image `fetchpriority="high"`, everything else `loading="lazy"`. Next.js `<Image>` with `sizes` and `placeholder="blur"`.
- Never display an image larger than its native resolution (blurry) — `visual-qa`'s report lists upscaled images.
- Meaningful `alt` for content images, `alt=""` for decorative ones.
- Hero image < ~250 KB, others < ~150 KB.

## 7. Check it
Run `visual-qa` and look at the full-page screenshots: do all images feel like one shoot? Is each image placed with a reason (not just filling a card)? Is there at least one moment where image and type interact?
