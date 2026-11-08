---
name: smart-commit
description: Create clean, atomic git commits with Conventional Commit messages, and write PR descriptions and release notes from the actual diff. Use whenever the user says commit, "commit-in", "bikin commit", push, prepare a PR, write a PR description, changelog, or release notes.
---

# Smart Commit

## Safety rules (always)
- Never commit secrets. Before committing, scan the staged diff for things like `API_KEY=`, `sk-`, `-----BEGIN`, `password =`, `.env` files. If found, stop and tell the user.
- Never `git push --force`, `reset --hard`, or rewrite history unless the user explicitly asks.
- Never commit without showing the user the plan first if there are >1 commits or unrelated changes.

## 1. Look at what changed
```
git status --short
git diff --stat
git diff            # and git diff --staged
```
Read the actual diff — messages are written from the code, not from file names.

## 2. Split into atomic commits
If the changes mix concerns (a feature + an unrelated fix + formatting), propose a split:
```
1. fix(auth): handle expired refresh token   → src/auth/refresh.ts
2. feat(profile): add avatar upload           → src/profile/*, tests
3. chore: format with prettier                → (formatting only)
```
Stage per commit with `git add <paths>` (or `git add -p` for partial files). If everything is one concern, one commit is fine.

## 3. Write the message (Conventional Commits)
```
<type>(<scope>): <imperative summary, ≤ 72 chars, no period>

<body: WHY the change was needed and anything non-obvious about HOW.
Wrap at 72. Skip the body for trivial changes.>

<footer: BREAKING CHANGE: ..., Closes #123>
```
Types: `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `build`, `ci`, `chore`, `style`, `revert`.
Scope = the module/area (`api`, `auth`, `ui`, `deps`). Check `git log --oneline -20` and follow the repo's existing style if it differs (language, scope format, emoji usage).

Good: `fix(cart): prevent negative quantity when removing last item`
Bad: `update files`, `fix bug`, `WIP`

## 4. PR description (when asked)
Base it on `git log main..HEAD` and `git diff main...HEAD`:
```
## What and why
<problem and solution in 2–4 sentences>

## Changes
- <grouped by area>

## How to test
- [ ] <concrete steps a reviewer can follow>

## Notes
<risks, migrations, env vars, screenshots for UI, follow-ups>
```
If `gh` is available and the user wants it, `gh pr create --title ... --body-file ...`.

## 5. Release notes (when asked)
Group commits since the last tag (`git describe --tags --abbrev=0`) into ✨ Features, 🐛 Fixes, ⚡ Performance, ⚠️ Breaking changes — written for users, not developers.

Write messages in English unless the repo history is in another language or the user asks otherwise.
