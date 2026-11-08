---
name: code-review
description: Review code changes like a senior engineer — correctness, security, performance, readability — for JavaScript/TypeScript and Python. Use whenever the user asks to review, check, audit, or "look over" code, a diff, a PR, a branch, or staged changes, or asks "is this okay?", "ada bug?", "cek kode ini", even if they don't say "review".
---

# Code Review

Goal: find the issues that actually matter, ranked by impact, with concrete fixes. Not a style lecture.

## 1. Establish scope

Figure out what to review, in this order:
1. Files/snippets the user pointed at.
2. Otherwise `git diff --staged`; if empty, `git diff`; if empty, `git diff main...HEAD` (try `master` if `main` doesn't exist).
3. If still nothing, ask.

Run `scripts/collect_diff.sh` to get the diff plus a file list in one go. Read the surrounding code of every changed hunk — bugs usually live at the boundary between new and old code, so the diff alone is not enough.

## 2. Understand intent before judging

Read the commit message / PR description / user's explanation. Ask yourself: what is this change trying to do? A review that misses the intent produces noise.

## 3. Check, in priority order

**🔴 Blocker — correctness & security**
- Logic errors, off-by-one, wrong conditions, unhandled `null`/`undefined`/`None`
- Async mistakes: missing `await`, unhandled promise rejections, `async` in `forEach`, race conditions, Python `asyncio` calls blocking the loop
- Injection: SQL string concatenation, `eval`/`exec`, shell commands built from input, `dangerouslySetInnerHTML`, Python `pickle`/`yaml.load` on untrusted data
- Secrets hard-coded, auth/permission checks missing on new endpoints
- Resource leaks: files/connections not closed (use `with` / `try…finally`)
- Mutable default arguments in Python (`def f(x=[])`)

**🟡 Should fix — robustness & performance**
- N+1 queries, work inside loops that could be hoisted, unbounded memory growth
- Error handling that swallows exceptions (`except: pass`, empty `catch {}`)
- TypeScript: `any`, unsafe `as` casts, non-null `!` hiding real nulls
- Missing tests for new branches
- React: missing/incorrect `useEffect` dependencies, keys from array index on reorderable lists

**🟢 Nice to have — maintainability**
- Naming, duplication, dead code, overly long functions
- Only mention if it materially helps; skip pure taste.

## 4. Verify, don't guess

If a project has them, run them and include results:
- JS/TS: `npx tsc --noEmit`, `npm run lint`, `npm test -- --related` (or the project's equivalents in `package.json`)
- Python: `ruff check`, `mypy`, `pytest -q` on affected tests

Don't claim something is a bug unless you can explain the input that triggers it. If unsure, say "possible issue" and why.

## 5. Output format

```
## Ringkasan
<1–2 kalimat: apa yang diubah dan penilaian keseluruhan: ✅ siap merge / ⚠️ perlu perbaikan / ❌ jangan merge>

## 🔴 Blocker
- `path/file.ts:42` — <masalah>. <kenapa berbahaya>.
  Fix: <kode perbaikan singkat>

## 🟡 Sebaiknya diperbaiki
...

## 🟢 Saran
...

## Yang sudah bagus
<1–3 poin spesifik — bukan basa-basi>
```

Match the user's language (Indonesian or English). Omit empty sections. Max ~10 findings; if more, keep the most important and say how many minor ones were left out.

Offer to apply the fixes — don't edit files unless the user asks.
