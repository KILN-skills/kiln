#!/usr/bin/env bash
# Print a compact map of a JS/TS or Python project.
set -uo pipefail
root="${1:-.}"
cd "$root" || exit 1

IGNORE='node_modules|.git|dist|build|.next|.nuxt|out|coverage|.venv|venv|env|__pycache__|.mypy_cache|.pytest_cache|.ruff_cache|.turbo|.cache|target'

echo "=== Project: $(basename "$(pwd)") ==="
echo
echo "=== Tree (depth 3) ==="
if command -v tree >/dev/null 2>&1; then
  tree -L 3 -a -I "$IGNORE" --dirsfirst | head -120
else
  find . -maxdepth 3 -not -path '*/.*/*' 2>/dev/null | grep -vE "/($IGNORE)(/|$)" | sort | head -120
fi

echo
echo "=== Manifests & config ==="
ls -1 package.json pnpm-workspace.yaml turbo.json nx.json tsconfig*.json pyproject.toml requirements*.txt setup.py setup.cfg Pipfile poetry.lock uv.lock manage.py Dockerfile docker-compose*.yml .env.example CLAUDE.md AGENTS.md README* 2>/dev/null

if [[ -f package.json ]]; then
  echo
  echo "=== package.json scripts & key deps ==="
  node -e '
    const p=require("./package.json");
    console.log("scripts:", JSON.stringify(p.scripts||{},null,2));
    const d={...(p.dependencies||{}),...(p.devDependencies||{})};
    console.log("deps:", Object.keys(d).join(", "));
  ' 2>/dev/null
fi

if [[ -f pyproject.toml ]]; then
  echo
  echo "=== pyproject.toml (head) ==="
  head -60 pyproject.toml
fi

echo
echo "=== Largest source files (likely core logic) ==="
find . \( -name node_modules -o -name .git -o -name .venv -o -name venv -o -name dist -o -name build -o -name .next \) -prune -o \
  -type f \( -name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.jsx' -o -name '*.py' \) -print0 2>/dev/null \
  | xargs -0 wc -l 2>/dev/null | grep -v ' total$' | sort -rn | head -15
