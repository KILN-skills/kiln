---
name: react-motion
description: Build UI animation in React/Next.js with Motion for React (formerly Framer Motion) — micro-interactions, enter/exit with AnimatePresence, layout and shared-element animations, gestures (hover, tap, drag), scroll-linked values, staggered lists, modals, tabs, menus, and page transitions. Use whenever the user mentions Motion, framer-motion, motion/react, AnimatePresence, layoutId, page transition in Next.js, animated modal/menu/tabs, or wants React components to feel smooth and alive.
---

# React Motion (Motion for React)

## 1. Setup
- New code: `npm i motion` and `import { motion, AnimatePresence } from "motion/react"`.
- If the project already uses `framer-motion`, keep it consistent; to migrate, swap the package and change imports `framer-motion` → `motion/react` (API is the same).
- Next.js App Router: components using `motion.*` must be client components (`"use client"`). For server components, use `import * as motion from "motion/react-client"`.
- Wrap the app once:
```tsx
<MotionConfig reducedMotion="user" transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}>
```
- Bundle-size sensitive? Use `LazyMotion` + `m` components with `domAnimation` features.

## 2. Core patterns
**Variants + stagger (lists, hero groups)**
```tsx
const list = { hidden: {}, show: { transition: { staggerChildren: 0.06, delayChildren: 0.1 } } };
const item = { hidden: { opacity: 0, y: 16 }, show: { opacity: 1, y: 0 } };
<motion.ul variants={list} initial="hidden" whileInView="show" viewport={{ once: true, amount: 0.3 }}>
  {items.map(i => <motion.li key={i.id} variants={item} />)}
</motion.ul>
```

**Enter/exit (modals, toasts, dropdowns)** — `AnimatePresence` must stay mounted; the child gets a stable `key`:
```tsx
<AnimatePresence>
  {open && (
    <motion.div key="modal" initial={{ opacity: 0, scale: 0.96 }} animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.98, transition: { duration: 0.15 } }} />
  )}
</AnimatePresence>
```
Use `mode="wait"` when swapping one element for another (tab content, steps).

**Layout animation** — `layout` prop animates size/position changes (accordion, filtering grid, reordering). Shared element: same `layoutId` in two places (tab underline, card → detail). Wrap related groups in `<LayoutGroup>`.

**Micro-interactions**
```tsx
<motion.button whileHover={{ y: -2 }} whileTap={{ scale: 0.97 }}
  transition={{ type: "spring", stiffness: 400, damping: 25 }} />
```
Springs for physical feel (buttons, drag, toggles); tweens with ease-out for reveals.

**Scroll-linked**
```tsx
const ref = useRef(null);
const { scrollYProgress } = useScroll({ target: ref, offset: ["start end", "end start"] });
const y = useTransform(scrollYProgress, [0, 1], [60, -60]);
<motion.img ref={ref} style={{ y }} />
```
For complex pinned/scrubbed storytelling, use GSAP instead (`scroll-animation` skill).

**Drag** — `drag="x"`, `dragConstraints={ref}`, `dragElastic`, `onDragEnd` with velocity for swipe carousels.

## 3. Page transitions in Next.js
- App Router has no built-in exit animations for routes. Options, simplest first:
  1. Enter-only animation in `app/template.tsx` (re-mounts on navigation): wrap children in a `motion.div` fade/slide-in.
  2. View Transitions API (`document.startViewTransition`, or the framework's experimental support) for cross-fade/morph between routes.
  3. Full enter+exit: a client wrapper with `AnimatePresence mode="wait"` keyed on `usePathname()` — works but needs care with the router freezing old content; test thoroughly.
- Pages Router: `AnimatePresence` around `<Component key={router.asPath} />` in `_app`.
- Keep route transitions short (≤ 400ms) — users navigate often.

## 4. Rules
- Animate transforms and opacity. For size changes use `layout`, not animating `height` directly (exception: `height: "auto"` for accordions is supported, use sparingly).
- Don't animate on every render — stable `initial`/`animate` values, memoize variants outside the component.
- `whileInView` with `viewport={{ once: true }}` for reveals; don't replay on every scroll pass.
- Respect reduced motion (`MotionConfig reducedMotion="user"` or `useReducedMotion()` for custom logic).
- Focus management in animated modals/menus still applies (see `a11y-audit`): focus trap, `Esc`, return focus.
- Don't use Motion and GSAP on the same element.

## 5. Verify
Click/hover/tab through each animated component; open/close quickly many times (no stuck states); check with reduced motion on; React DevTools Profiler shows no re-render storms during animation.
