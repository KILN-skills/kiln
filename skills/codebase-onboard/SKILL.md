---
name: codebase-onboard
description: Quickly map and explain an unfamiliar JavaScript/TypeScript or Python codebase — architecture, entry points, data flow, how to run it, and where to make a given change. Use whenever the user opens a new project, asks "explain this repo", "gimana struktur project ini", "where is X handled", "how does this work", or wants to start a task in code they don't know yet.
---

# Codebase Onboarding

Goal: give the user an accurate mental model fast, grounded in real files — not a generic description of the framework.

## 1. Survey (cheap, broad)
Run `scripts/project_map.sh` from the repo root. It prints the tree (ignoring vendor dirs), manifests, scripts, and largest source files.

Then read, in order: `README*`, `package.json` / `pyproject.toml`, `CLAUDE.md` / `AGENTS.md` / `CONTRIBUTING.md` if present, `.env.example`, `docker-compose.yml`, CI config (`.github/workflows/`).

## 2. Identify the shape
Decide what kind of project it is from evidence:
- **Framework**: Next.js (`app/` or `pages/`), Vite/React, Express/Fastify/NestJS, FastAPI, Django (`manage.py`, `settings.py`), Flask, CLI tool, library, monorepo (`turbo.json`, `pnpm-workspace.yaml`, `nx.json`).
- **Entry points**: `main`/`bin` in package.json, `src/index.ts`, `server.ts`, `main.py`, `app.py`, `manage.py`, `__main__.py`.
- **Data layer**: Prisma/Drizzle/TypeORM/Mongoose, SQLAlchemy/Django ORM, migration folders.
- **External services**: env vars and SDK imports.

## 3. Trace one real flow end to end
Pick the most central feature (or the one the user cares about) and follow it: route/handler → service/business logic → data access → response. Name the actual files and functions. One concrete trace teaches more than ten folder descriptions.

## 4. Output
```
## Overview
<what the project is, who it's for, main stack — 2–3 sentences>

## How to run it
<install, required env vars, dev, test, build — exact commands from the repo>

## Key structure
<only the folders/files that matter, one line on each one's role>

## Main flow
<the trace from step 3, as numbered steps with file:function>

## Conventions and pitfalls
<patterns this repo uses; things that are easy to get wrong>

## To change X, start at…
<pointers to concrete files, if the user named a task>
```

Use a Mermaid diagram only if the flow has more than ~4 hops or branches. Write the report in the user's language (for example, Indonesian if they wrote in Indonesian); translate the headings too. Mark anything inferred rather than read as "(guess)".

## 5. Optional: save it
Offer to write the summary to `CLAUDE.md` in the repo root (append, don't overwrite existing content) so future Claude Code sessions start with this context.
