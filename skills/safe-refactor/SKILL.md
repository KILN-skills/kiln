---
name: safe-refactor
description: Refactor JavaScript/TypeScript or Python code without changing behavior — extract functions, rename, split large files, remove duplication, modernize syntax, add types — with tests as a safety net. Use whenever the user asks to refactor, clean up, simplify, "rapikan kode", restructure, migrate JS to TS, add type hints, or reduce complexity.
---

# Safe Refactor

Refactoring = changing structure **without** changing behavior. The whole skill is about proving behavior didn't change.

## 1. Baseline
- Run the tests that cover the target code; record the result. Also run type check and lint (`tsc --noEmit`, `eslint`; `mypy`/`pyright`, `ruff`).
- If coverage of the target is weak, write **characterization tests** first: tests that pin current behavior (including weird behavior) for the main inputs. Commit or stash-point here so you can roll back.
- If tests are failing before you start, tell the user — don't refactor on a red baseline.

## 2. Plan
Write a short plan listing each transformation and the risk. Show it to the user if the refactor touches more than ~3 files or changes a public API.

Find all usages before renaming/moving anything:
```
grep -rn "functionName" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.py" .
```
Watch for dynamic usages grep might miss: string-based lookups, `getattr`, re-exports in `index.ts`/`__init__.py`, templates, config files.

## 3. Small steps, green between each
Do one transformation at a time and rerun tests after each:
- Extract function / component / hook
- Rename (symbol + all usages + imports)
- Replace conditional chains with lookup tables or early returns
- Remove dead code (confirm it's truly unused first)
- Split a large module; keep a re-export at the old path if external code imports it

If tests go red, undo the last step rather than debugging forward.

## 4. Don't sneak in behavior changes
- No bug fixes, feature additions, or dependency upgrades mixed in. If you spot a bug, note it and report it separately.
- Keep public signatures stable unless the user agreed to change them.
- Preserve error types/messages that callers might rely on.

## 5. Language-specific notes
**TypeScript:** prefer narrowing over `as`; replace `any` with real types or `unknown` + guards; use discriminated unions for state; `satisfies` for config objects.
**JS → TS migration:** rename file-by-file starting from leaves (utils) to roots; enable `strict` gradually; don't block on 100% types.
**Python:** add type hints from the outside in (public functions first); `dataclasses`/`pydantic` for dict-shaped data; replace `**kwargs` passthroughs with explicit params where it clarifies; f-strings; `pathlib` over `os.path`.

## 6. Finish
Run the full test suite + type check + lint. Summarize: what changed structurally, what was verified, and any bugs/smells noticed but deliberately left alone.
