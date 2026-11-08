#!/usr/bin/env bash
# Detect test framework, test command, and existing test locations for JS/TS and Python projects.
set -uo pipefail
root="${1:-.}"
cd "$root" || exit 1

found=0

if [[ -f package.json ]]; then
  found=1
  echo "=== JavaScript / TypeScript ==="
  pm="npm"
  [[ -f pnpm-lock.yaml ]] && pm="pnpm"
  [[ -f yarn.lock ]] && pm="yarn"
  [[ -f bun.lockb || -f bun.lock ]] && pm="bun"
  echo "Package manager: $pm"
  echo -n "Test script: "
  node -e 'const p=require("./package.json");console.log((p.scripts&&p.scripts.test)||"(none)")' 2>/dev/null || grep -o '"test"[^,]*' package.json || echo "(none)"
  echo -n "Frameworks in deps: "
  for f in vitest jest mocha @playwright/test cypress @testing-library/react @testing-library/vue supertest; do
    grep -q "\"$f\"" package.json && echo -n "$f "
  done
  echo
  ls vitest.config.* jest.config.* playwright.config.* 2>/dev/null | sed 's/^/Config: /'
fi

if [[ -f pyproject.toml || -f setup.cfg || -f pytest.ini || -f requirements.txt || -f tox.ini ]]; then
  found=1
  echo "=== Python ==="
  for f in pyproject.toml pytest.ini setup.cfg tox.ini; do
    [[ -f $f ]] && grep -qE '^\[(tool\.pytest|pytest)' "$f" && echo "pytest config in: $f"
  done
  echo -n "Test libs mentioned: "
  cat pyproject.toml requirements*.txt setup.cfg 2>/dev/null | grep -oiE 'pytest(-[a-z]+)?|hypothesis|freezegun|time-machine|factory[-_]boy|httpx|respx|responses' | sort -u | tr '\n' ' '
  echo
fi

if [[ $found -eq 0 ]]; then
  echo "No package.json or Python project files found in $(pwd)."
fi

echo "=== Existing test files (first 15) ==="
find . \( -path ./node_modules -o -path ./.venv -o -path ./venv -o -path ./.git -o -path ./dist -o -path ./build \) -prune -o \
  -type f \( -name '*.test.*' -o -name '*.spec.*' -o -name 'test_*.py' -o -name '*_test.py' \) -print 2>/dev/null | head -15
