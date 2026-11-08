---
name: ui-polish
description: Build and polish website UI so it looks professionally designed, not template-generic — layout, typography, spacing, color, responsive behavior, states, and micro-interactions — in React/Next.js, Vue, Tailwind, or plain HTML/CSS. Use whenever the user builds or tweaks a page, section, landing page, component, navbar, hero, form, or says "bikin tampilan", "rapikan UI", "kurang bagus", "buat responsive", "make it look better", even if they don't mention design.
---

# UI Polish

## 1. Read the room first
- Detect the stack: Tailwind (`tailwind.config.*` / `@import "tailwindcss"`), CSS Modules, styled-components, shadcn/ui (`components/ui/`), plain CSS.
- Reuse existing design tokens: colors, fonts, spacing, radius, existing components. Never invent a second button style when one exists.
- If there's no design system, set one small set of tokens (CSS variables or Tailwind theme) before writing components.

## 2. Pick a direction, not defaults
Before coding, decide in one line: the mood (e.g. "calm editorial", "bold startup", "warm local business") and what that means for type, color and density. Avoid the generic look: centered purple gradient hero, three identical icon cards, everything `rounded-2xl shadow-lg`.

## 3. Fundamentals checklist
**Typography**
- Max 2 font families. Body 16–18px, line-height 1.5–1.7; headings tighter (1.1–1.25).
- Line length 60–75 characters (`max-w-prose` / `max-width: 65ch`).
- Clear scale (e.g. 14/16/20/24/32/48) — don't pick random sizes.

**Spacing & layout**
- One spacing scale (4/8px based). Related things closer together than unrelated things.
- Generous section padding (64–128px desktop, 48–64px mobile).
- Use CSS Grid/Flex with `gap`, not margins on children.
- Align to a container width (e.g. 1120–1280px) consistently.

**Color**
- 1 primary, 1 accent max, plus neutrals. Primary only for the main action.
- Text contrast ≥ 4.5:1 (≥ 3:1 for large text). Don't put gray text on colored backgrounds.
- Support dark mode only if the project already does or user asks — and then via tokens.

**Hierarchy**
- Each section has one obvious focal point and one primary CTA.
- Squint test: the most important thing should still stand out when blurred.

## 4. Responsive — mobile first
- Write base styles for ~375px, then add `sm/md/lg` (or `min-width` queries).
- Check 375, 768, 1024, 1440. No horizontal scroll at any width (`overflow-x` is a symptom, fix the cause).
- Tap targets ≥ 44×44px; nav collapses to a usable menu; tables scroll in their own container or become cards.
- Fluid type for big headings: `font-size: clamp(2rem, 5vw, 3.5rem)`.
- Images: `width/height` or `aspect-ratio` set to avoid layout shift; `object-fit: cover`.

## 5. Every interactive element has all its states
hover, focus-visible (visible ring — never just `outline: none`), active, disabled, loading. Forms: label, placeholder that isn't the label, inline error, success. Lists/data: empty state, loading skeleton, error state.

## 6. Motion (subtle)
150–250ms, `ease-out` for entering. Animate `transform`/`opacity` only. Respect `@media (prefers-reduced-motion: reduce)`.

## 7. Verify visually
If a browser tool or Playwright is available, screenshot the page at mobile and desktop widths and actually look at it before reporting done. Fix what looks off — alignment, cramped spacing, orphaned words in headings, uneven card heights.

Report briefly: the direction chosen, what was changed, and anything that needs real content/images from the user.
