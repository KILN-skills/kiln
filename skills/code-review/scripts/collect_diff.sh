#!/usr/bin/env bash
# Collect the most relevant diff for review: staged -> unstaged -> branch vs main/master.
set -euo pipefail

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Not a git repository." >&2
  exit 1
fi

mode=""
if ! git diff --staged --quiet; then
  mode="staged"; diff_cmd=(git diff --staged)
elif ! git diff --quiet; then
  mode="unstaged"; diff_cmd=(git diff)
else
  base=""
  for b in main master; do
    if git rev-parse --verify --quiet "$b" >/dev/null; then base="$b"; break; fi
  done
  if [[ -n "$base" ]] && [[ "$(git rev-parse HEAD)" != "$(git rev-parse "$base")" ]]; then
    mode="branch vs $base"; diff_cmd=(git diff "$base"...HEAD)
  else
    echo "No changes found (staged, unstaged, or vs main/master)."
    exit 0
  fi
fi

echo "=== Review scope: $mode ==="
echo
echo "=== Files changed ==="
"${diff_cmd[@]}" --stat
echo
echo "=== Diff ==="
"${diff_cmd[@]}" --unified=5
