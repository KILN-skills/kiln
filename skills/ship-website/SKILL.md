---
name: ship-website
description: Pre-launch checklist and deployment for websites — production build check, environment variables, forms, security headers, domain/HTTPS, analytics, and deploying to Vercel, Netlify, Cloudflare Pages, or a VPS (Nginx + PM2/Docker). Use whenever the user wants to deploy, launch, "go live", "naikkan ke hosting", publish a site, connect a domain, or asks if a site is ready for production.
---

# Ship Website

## 1. Build must pass clean
```
npm ci && npm run lint && npx tsc --noEmit && npm run build
```
(Python backends: install from lockfile, run tests, `collectstatic`/migrations dry-run.) Zero errors; read the warnings. Then run the production build locally (`npm run start` / `preview`) and click through the main pages.

## 2. Pre-launch checklist
Go through and report ✅/❌ for each:

**Content & links**
- [ ] No lorem ipsum, placeholder images, `TODO`, test data, `console.log`
- [ ] All links work (internal + external), 404 page exists
- [ ] Contact info, legal pages (privacy policy if collecting data) present

**Forms & functionality**
- [ ] Every form actually submits in production (email/API/webhook) and shows success + error states
- [ ] Spam protection (honeypot, rate limit, Turnstile/reCAPTCHA) on public forms
- [ ] Server-side validation, not only client-side

**Config & security**
- [ ] Env vars set in the hosting dashboard; `.env*` in `.gitignore`; no secrets in client bundle (`NEXT_PUBLIC_`/`VITE_` vars are PUBLIC)
- [ ] HTTPS, one canonical host (www or not) with 301 redirect
- [ ] Security headers: `Content-Security-Policy` (at least a basic one), `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Strict-Transport-Security`, `frame-ancestors`/`X-Frame-Options`
- [ ] `npm audit --omit=dev` / `pip-audit` — no critical vulns
- [ ] Admin/staging routes protected; staging is `noindex`

**Quality gates** (use the other skills)
- [ ] `seo-setup` checks pass (titles, OG image, sitemap, robots)
- [ ] `a11y-audit` automated pass has no blockers
- [ ] `web-performance`: Lighthouse mobile ≥ 90 performance, CLS < 0.1
- [ ] Looks right on real mobile widths (`ui-polish` step 7)

**After launch**
- [ ] Analytics installed (respect cookie consent if needed)
- [ ] Error monitoring (Sentry or host logs)
- [ ] Google Search Console verified + sitemap submitted
- [ ] Uptime check

## 3. Deploy
Detect existing config first (`vercel.json`, `netlify.toml`, `wrangler.toml`, `Dockerfile`, `ecosystem.config.js`) and follow it.

- **Vercel** (best for Next.js): `npx vercel` (preview) → `npx vercel --prod`. Headers/redirects in `next.config.*` or `vercel.json`.
- **Netlify**: `npx netlify deploy --build` → `--prod`. Headers in `netlify.toml` or `_headers`.
- **Cloudflare Pages**: `npx wrangler pages deploy <out-dir>`. Headers in `_headers`.
- **VPS (Nginx)**: build on CI or server; Node app via PM2 (`pm2 start npm --name site -- start`, `pm2 save`) or Docker; Nginx reverse proxy + `certbot --nginx` for HTTPS; gzip/brotli and long cache for hashed assets.

Always deploy to preview/staging first, smoke-test, then promote. Never run a production deploy, DNS change, or database migration without the user's explicit go-ahead.

## 4. Report
The checklist with results, the deployed URL(s), and the remaining ❌ items ranked by risk.
