---
name: test-writer
description: Write meaningful automated tests for JavaScript/TypeScript (Vitest, Jest, Testing Library, Playwright) and Python (pytest) that follow the project's existing conventions. Use whenever the user asks to add tests, improve coverage, "bikin test", "buat unit test", test a function/component/endpoint, or after implementing a feature that has no tests.
---

# Test Writer

Good tests fail when behavior breaks and pass when it doesn't. They're not coverage padding.

## 1. Detect the setup — never assume

Run `scripts/detect_test_setup.sh` from the project root. It reports the framework, test command, and where existing tests live.

Then open 1–2 existing test files near the target code and copy their conventions: file naming (`*.test.ts` vs `*.spec.ts`, `test_*.py`), folder (`__tests__/`, `tests/`, colocated), imports, fixtures/factories, mocking style. Consistency beats your preferences.

If there is no test setup at all, propose one (Vitest for Vite/TS projects, Jest otherwise; pytest for Python) and ask before installing.

## 2. Decide what to test

Read the target code and list behaviors, not lines:
- **Happy path** — the main expected use
- **Edge cases** — empty input, zero, negative, very large, unicode, `null`/`None`/`undefined`, duplicate items
- **Error paths** — invalid input raises/rejects with the right error
- **Boundaries** — exactly at limits (`<` vs `<=`)
- **State/side effects** — what gets written, called, emitted

Prioritize by risk: business logic and data transforms first; trivial getters last or never.

## 3. Write the tests

Principles:
- One behavior per test, named as a sentence: `it("returns empty list when no users match")`, `def test_returns_empty_list_when_no_users_match()`.
- Arrange / Act / Assert, visibly separated.
- Assert on outputs and observable effects, not on internal implementation details.
- Mock only at the edges (network, time, filesystem, randomness, external APIs). Don't mock the code under test.
- Deterministic: freeze time (`vi.useFakeTimers()`, `freezegun`/`time-machine`), seed randomness, no real network.
- Use parametrization for input tables: `it.each` / `test.each`, `@pytest.mark.parametrize`.
- React components: Testing Library, query by role/label text (`getByRole("button", { name: /simpan/i })`), use `userEvent`, not implementation selectors.
- Python async: `pytest-asyncio` if the project uses it.
- API endpoints: FastAPI `TestClient` / Django test client / supertest for Express.

## 4. Prove the tests are real

1. Run the new tests — they must pass.
2. **Mutation check**: temporarily break the code under test (flip a condition, return early) and confirm at least one new test fails. Revert. A test that can't fail is worthless.
3. Run the whole related suite to make sure nothing else broke.

## 5. Report

Briefly list: which behaviors are now covered, anything deliberately skipped (and why), and any bugs the tests uncovered — report those to the user rather than silently "fixing" the test to match buggy behavior.
