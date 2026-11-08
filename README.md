# Kiln

**Senior engineering habits, forged into your AI agent.**

Kiln is a set of 18 skills that make AI coding agents work the way an experienced engineer does: understand the code first, then design, build in thin slices, test, review, and only then ship. Each skill is a structured workflow with steps, checkpoints, and exit criteria, not just a prompt.

## Install

```bash
npx skills add KILN-skills/kiln
```

Works with Claude Code, Cursor, Codex, GitHub Copilot, Windsurf, Cline, Gemini CLI, OpenCode, and other agents that support `SKILL.md` skills.

Install a single skill:

```bash
npx skills add KILN-skills/kiln --skill code-review
```

Or copy any folder from [`skills/`](skills) into your agent's skills directory (for Claude Code: `~/.claude/skills/` or `.claude/skills/` in your project).

## The firing schedule

| Phase | Command | Skills |
|---|---|---|
| Understand | `/understand` | `codebase-onboard`, `website-visual-inspector` |
| Design | `/design` | `motion-direction`, `visual-assets` |
| Build | `/build` | `ui-polish`, `react-motion`, `scroll-animation`, `web-3d` |
| Test | `/test` | `test-writer`, `debug-root-cause`, `visual-qa` |
| Review | `/review` | `code-review`, `safe-refactor`, `a11y-audit`, `web-performance` |
| Ship | `/ship` | `seo-setup`, `ship-website`, `smart-commit` |

Extra commands: `/speed` (web performance audit) and `/tidy` (refactor without changing behavior).

You don't need to call the skills by name. Your agent picks the right one from what you ask, for example "review this diff", "the site is slow", or "add tests for this function".

## Skills

| Skill | What it does |
|---|---|
| [`codebase-onboard`](skills/codebase-onboard) | Maps an unfamiliar repo: architecture, entry points, data flow, and where a change belongs |
| [`website-visual-inspector`](skills/website-visual-inspector) | Screenshots a site on desktop and mobile and breaks down its background, gradients, and palette |
| [`motion-direction`](skills/motion-direction) | Decides what moves and what stays still, picks the animation tool, and sets a motion system |
| [`visual-assets`](skills/visual-assets) | One visual style for every image: crops, color treatment, masking, responsive exports |
| [`ui-polish`](skills/ui-polish) | Layout, typography, spacing, color, and states so the UI never looks like a template |
| [`react-motion`](skills/react-motion) | React animation with Motion: AnimatePresence, layoutId, gestures, page transitions |
| [`scroll-animation`](skills/scroll-animation) | GSAP, ScrollTrigger, and Lenis: reveals, pinning, parallax, with proper cleanup |
| [`web-3d`](skills/web-3d) | Three.js and React Three Fiber, shaders, particles, and GLB models with fallbacks |
| [`test-writer`](skills/test-writer) | Meaningful tests with Vitest, Jest, Playwright, or pytest, following project conventions |
| [`debug-root-cause`](skills/debug-root-cause) | Finds the root cause of a bug systematically instead of guessing at patches |
| [`visual-qa`](skills/visual-qa) | Screenshots and animation filmstrips, then an art-director critique until it stops looking generic |
| [`code-review`](skills/code-review) | Senior-level review: correctness, security, performance, readability, with severity labels |
| [`safe-refactor`](skills/safe-refactor) | Refactors with tests as a safety net: extract, rename, split, migrate to TypeScript |
| [`a11y-audit`](skills/a11y-audit) | WCAG 2.2 AA audit: keyboard, focus, labels, contrast, ARIA, screen readers |
| [`web-performance`](skills/web-performance) | Measure first, then fix: LCP, INP, CLS, bundles, images, fonts, caching |
| [`seo-setup`](skills/seo-setup) | Meta tags, Open Graph, canonical URLs, sitemap, robots, and JSON-LD |
| [`ship-website`](skills/ship-website) | Pre-launch checks and deploys to Vercel, Netlify, Cloudflare Pages, or a VPS |
| [`smart-commit`](skills/smart-commit) | Atomic Conventional Commits, PR descriptions, and release notes from the real diff |

## Notes

- Paths inside a skill, such as `scripts/capture.py`, are relative to that skill's folder.
- Some skills include small helper scripts in Python or shell. The screenshot-based ones (`visual-qa`, `website-visual-inspector`) need Playwright: `pip install playwright pillow && python -m playwright install chromium`.
- Several skills also trigger on Indonesian phrases, such as "cek kode ini" or "website lemot".

## License

[MIT](LICENSE)
