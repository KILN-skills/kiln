---
name: website-visual-inspector
description: See what a website looks like (desktop and mobile screenshots) and break down its background — colors, gradients, images, video, canvas, ::before/::after pseudo-elements, overlays, and the color palette. Use when the user says "look at this website", "check how it looks", "what's the background on this site", "clone/copy this design", "grab the colors/gradient from this site", or gives a URL and asks about its visuals (also in Indonesian, such as "lihat website ini", "cek tampilan", "background website apa", "tiru desain").
allowed-tools: Bash, Read, Write
---

# Website Visual Inspector

This skill lets the agent **see** a website the way a person does (through screenshots) and **read** its background precisely (through computed CSS), then combine the two.

## Setup (once)

```bash
pip install playwright        # add --break-system-packages if needed
python -m playwright install chromium
```

## Workflow

1. **Run the inspection**
   ```bash
   python3 scripts/inspect_site.py <URL> --out site-inspect
   ```
   Options: `--dark` (render in dark mode), `--no-mobile`, `--no-download`, `--wait 3000` (for sites with heavy animation).
   The URL can also be a local file (`./index.html`) or a dev server (`http://localhost:3000`).

2. **Look at it** — open the screenshots with Read (Read can display images):
   - `site-inspect/viewport_desktop.png` → first impression / hero section
   - `site-inspect/screenshot_desktop.png` → the whole page
   - `site-inspect/screenshot_mobile.png` → the mobile version
   A very tall full-page screenshot can look tiny; crop it first if you need detail:
   `python3 -c "from PIL import Image; im=Image.open('site-inspect/screenshot_desktop.png'); im.crop((0,0,1440,1800)).save('site-inspect/crop_1.png')"`

3. **Read the background data** — start with `site-inspect/report.md` (short). Open `backgrounds.json` only for details on a specific element.

4. **Combine** what you see in the screenshots with the CSS data. Example: the hero looks purple-blue → match it to the gradient in the report and give the exact selector and value.

## What it detects

| Kind | Source |
|---|---|
| Solid colors | `background-color` on every element plus `html`/`body` |
| Gradients | `linear/radial/conic-gradient`, including stacked ones |
| Images | `url(...)` in `background-image` (downloaded to `backgrounds/`) |
| Pseudo-elements | `::before` / `::after` (often used for dark overlays or noise) |
| Background video | `<video>` with autoplay/loop/muted, plus poster |
| Canvas | large `<canvas>` (WebGL / particle animation — only visible in screenshots) |
| Img as background | `<img>` with `object-fit: cover` + `position: absolute/fixed` |
| Effects | `background-attachment: fixed` (parallax), `blend-mode`, `filter`, `backdrop-filter` (glassmorphism) |
| Design tokens | color CSS variables on `:root` |
| Palette | background colors ranked by area (`palette.json`) |

## When answering the user

- Show the relevant screenshots (send the files if the user can't see the working folder).
- Name the main background: exact color/gradient (hex and CSS), images and downloaded files, overlay layers.
- If the user wants to **recreate** the design, write ready-to-use CSS that reproduces the background. Images and logos from another site belong to their owner; suggest replacing them with the user's own assets for anything public.
- If there's a `canvas` or video, explain that it's an animation and describe it from the screenshots.
- Reply in the user's language.

## Common problems

- **Blank page / blocked as a bot** → try `--wait 5000`; some sites (Cloudflare challenges) can't be inspected automatically. Don't try to get past a CAPTCHA.
- **Content appears on scroll** → the script already auto-scrolls; add `--wait` if it's still empty.
- **Images fail to download** → the URL is still recorded in the report; hotlink protection can refuse downloads.
- **Cross-origin stylesheets** → CSS variables from CDN files may not be readable, but computed styles are still accurate.
