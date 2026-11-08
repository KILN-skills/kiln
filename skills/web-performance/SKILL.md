---
name: web-performance
description: Diagnose and fix website speed — Core Web Vitals (LCP, INP, CLS), bundle size, images, fonts, caching, and rendering strategy — for Next.js, React/Vite, Vue/Nuxt, Astro, and static sites. Use whenever the user says the site is slow, "website lemot", wants a better Lighthouse/PageSpeed score, mentions Core Web Vitals, large bundles, or is preparing a site for launch.
---

# Web Performance

Measure → fix the biggest bottleneck → measure again. Never optimize blind.

## 1. Measure
- Production build only (`npm run build && npm run start` / `preview`). Dev mode numbers are meaningless.
- Lighthouse (mobile preset): `npx lighthouse <url> --preset=perf --form-factor=mobile --output=json --output-path=./lh.json --chrome-flags="--headless"` if Chrome is available; otherwise ask the user to run PageSpeed Insights and paste the result.
- Bundle: `npx vite-bundle-visualizer`, `ANALYZE=true` with `@next/bundle-analyzer`, or `npx source-map-explorer 'dist/**/*.js'`.
- Note the baseline: LCP, INP/TBT, CLS, total JS (gzipped), page weight.

Targets: **LCP < 2.5s, INP < 200ms, CLS < 0.1**, initial JS < ~170KB gzipped for content sites.

## 2. Fix by metric

**LCP (largest content slow)**
- Find the LCP element (usually hero image or heading).
- Hero image: modern format (AVIF/WebP), correct size, `fetchpriority="high"`, NOT `loading="lazy"`. Next.js: `<Image priority />`.
- Remove render-blocking CSS/JS in `<head>`; inline critical CSS if needed.
- Server: use SSG/ISR or cache HTML for pages that don't need per-request data; check TTFB.
- `preconnect` to required third-party origins (fonts CDN, API).

**CLS (layout jumps)**
- `width`/`height` or `aspect-ratio` on every image, video, iframe, ad slot.
- Fonts: `font-display: swap` + size-adjusted fallback (`next/font` does this), or `optional`.
- Don't insert banners/content above existing content after load; reserve space.

**INP (slow interactions)**
- Find long tasks (> 50ms). Break up heavy handlers; defer non-urgent work (`requestIdleCallback`, `startTransition`).
- Avoid re-rendering huge lists — virtualize (`@tanstack/react-virtual`), memoize expensive children.
- Third-party scripts (chat widgets, analytics, tag managers): load `afterInteractive`/`lazyOnload`, or on user intent.

**Bundle size**
- Dynamic import heavy, below-the-fold or route-specific code (`next/dynamic`, `React.lazy`, `defineAsyncComponent`).
- Replace heavy deps: moment → date-fns/dayjs, lodash → native or `lodash-es` per-function imports, full icon packs → individual imports.
- Next.js App Router: keep `"use client"` as low in the tree as possible; data fetching in server components.
- Remove unused dependencies (`npx depcheck`).

**Assets & caching**
- Images: responsive `srcset`/`sizes`; lazy-load below the fold.
- Fonts: self-host, subset, WOFF2, preload only the 1–2 used above the fold.
- Static assets: hashed filenames + `Cache-Control: public, max-age=31536000, immutable`. HTML: short cache or revalidate.
- Compression (Brotli/gzip) on the server/CDN.

## 3. Re-measure and report
Show a before/after table of the same metrics. List remaining opportunities ranked by expected impact vs effort. Don't claim gains you didn't measure.
