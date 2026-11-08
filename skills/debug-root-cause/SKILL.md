---
name: debug-root-cause
description: Systematically find and fix the root cause of bugs, errors, failing tests, and crashes in JavaScript/TypeScript and Python. Use whenever the user pastes an error or stack trace, says something is broken, "not working", "error", "kenapa gagal", "bug", a test fails, or behavior is unexpected — instead of guessing at a fix.
---

# Debug: Root Cause First

The most common debugging failure is patching the symptom. This skill forces a reproduce → hypothesize → prove → fix loop.

## 1. Reproduce

- Get the exact failing command (test, script, request). Run it yourself and capture the full output.
- If it doesn't reproduce, stop and gather info: environment, versions (`node -v`, `python --version`, lockfile), input data, env vars. Don't fix what you can't see.
- Make the reproduction as small and fast as possible (a single test, `pytest path::test_name -x`, `npx vitest run file -t "name"`).

## 2. Read the error properly

- Read the **whole** stack trace. The first frame in *the user's own code* (not `node_modules` / `site-packages`) is usually where to look.
- Read the actual code at those lines, plus callers.
- Common decoders:
  - `Cannot read properties of undefined (reading 'x')` / `AttributeError: 'NoneType'` → something upstream returned nothing; find where the value came from.
  - `ERR_MODULE_NOT_FOUND`, `ModuleNotFoundError` → path, ESM/CJS mismatch, virtualenv not active, missing dependency.
  - `UnhandledPromiseRejection`, `RuntimeWarning: coroutine was never awaited` → missing `await`.
  - Works locally, fails in CI → env vars, timezone, file ordering, node/python version, test isolation.
  - Flaky → shared state between tests, time, randomness, network, race conditions.

## 3. Hypothesize, then prove

Write down 1–3 hypotheses ranked by likelihood. For each, pick the cheapest experiment that would confirm or kill it:
- Add a targeted log/print of the suspicious value (remove it after).
- Write a failing test that pins the bug.
- `git bisect` if it "used to work": `git bisect start; git bisect bad; git bisect good <sha>` then run the repro at each step.
- Check what changed recently: `git log -p --since="3 days ago" -- <file>`.

Only move to a fix when one hypothesis is **proven**. If all are killed, go back to step 2 with the new evidence.

## 4. Fix at the root

- Fix where the bad value/state is *created*, not where it *explodes*.
- Avoid symptom patches: blanket `try/except`, `?.` everywhere, `# type: ignore`, raising timeouts, `retry` on deterministic failures. If a guard really is the right answer, explain why.
- Keep the fix minimal; refactors go in a separate step.

## 5. Prevent regression

- Add (or keep) the test that failed before the fix and passes after.
- Run the related test suite, not just the single test.
- Search for the same pattern elsewhere: `grep -rn "<pattern>" src/` — same bug often lives in sibling code.

## 6. Report

```
**Akar masalah:** <1–2 kalimat, sebutkan file:baris>
**Bukti:** <apa yang membuktikannya — output, test>
**Perbaikan:** <apa yang diubah dan kenapa di situ>
**Pencegahan:** <test yang ditambahkan / pola serupa yang ditemukan>
```

Match the user's language.
