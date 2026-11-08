---
name: seo-setup
description: Set up and audit technical SEO and social sharing for websites — titles, meta descriptions, Open Graph/Twitter cards, canonical URLs, sitemap.xml, robots.txt, structured data (JSON-LD), headings, and indexability — for Next.js, Nuxt, Astro, Vite/React SPAs, and static HTML. Use whenever the user mentions SEO, Google ranking, "biar muncul di Google", meta tags, link previews on WhatsApp/Facebook/X, sitemap, schema, or is launching a website.
---

# SEO Setup

## 1. Check the current state
Run on the build output (e.g. `out/`, `dist/`, `.next` export, or a saved HTML file):
```
python3 scripts/site_check.py <dir-or-file>
```
It flags per page: missing/duplicate title & description, length issues, missing canonical, OG/Twitter tags, `lang`, multiple/missing `h1`, images without alt, `noindex`. Also check `robots.txt` and `sitemap.xml` exist.

**SPA warning:** a client-only React/Vue SPA serves an empty HTML shell — crawlers and social previews see nothing. For sites that need SEO, recommend SSR/SSG (Next.js, Nuxt, Astro) or prerendering.

## 2. Per-page essentials
- `<title>`: unique, ~50–60 chars, main keyword early, brand at the end (`Jasa Desain Interior Medan | Nama Brand`).
- `<meta name="description">`: unique, ~140–160 chars, written to get the click.
- `<link rel="canonical" href="https://domain.com/path">` absolute URL.
- One `<h1>` matching search intent; logical `h2/h3`.
- Open Graph: `og:title`, `og:description`, `og:image` (1200×630, absolute URL, < 1MB), `og:url`, `og:type`. Twitter: `twitter:card=summary_large_image`.
- `<html lang="…">`, `<meta name="viewport" content="width=device-width, initial-scale=1">`.
- Descriptive URLs (`/layanan/desain-interior`, not `/page?id=3`), internal links with descriptive anchor text.

Framework ways to do it:
- **Next.js App Router:** `export const metadata` / `generateMetadata`, `app/sitemap.ts`, `app/robots.ts`, `app/opengraph-image.tsx`. Set `metadataBase`.
- **Nuxt:** `useSeoMeta()`, `@nuxtjs/sitemap`.
- **Astro:** a `<SEO>`/`BaseHead` component, `@astrojs/sitemap`.
- **Static/Vite:** tags in each HTML file; generate sitemap at build.

## 3. Site-wide
- `robots.txt` allowing crawl + `Sitemap: https://domain.com/sitemap.xml`. Make sure staging is `noindex` and production is NOT.
- `sitemap.xml` with all canonical, indexable URLs.
- Structured data (JSON-LD in `<script type="application/ld+json">`): `Organization` or `LocalBusiness` (name, address, phone, opening hours, geo — important for local businesses), `WebSite`, `BreadcrumbList`, `Product`, `Article`, `FAQPage` as relevant. Validate with Google's Rich Results Test.
- Favicon set + `site.webmanifest`.
- 404 page returns real 404 status; redirects are 301; one canonical host (www vs non-www, https).
- Performance and mobile usability affect ranking — hand off to `web-performance` if needed.

## 4. Report
Table of issues per page (or "all pages") with fixes applied; list what needs the user's input (real business info, OG image design, final domain). Remind them to submit the sitemap in Google Search Console after deploy.
