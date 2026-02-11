# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**divyadrishti** is a multi-source public intelligence platform that ingests social/news content (HN, Reddit, X, blogs), understands broad-scale concerns ("metric nodes"), quantifies sentiment/controversy/consensus, and surfaces insights through dashboards and APIs.

Phase plans live in `.claude/phase{1,2,3}_plan.md`. Skills live in `.claude/skills/`.

## Architecture

### Monorepo Structure (target)
```
apps/api/          — FastAPI backend
apps/web/          — Next.js frontend
agents/            — 10+ independent worker agents (supervisor, trend_scout, thread_harvester, normalizer, author_integrity, opinion_analyst, metric_mapper, metric_gardener, rollup_accountant, moderator)
libs/schemas/      — Pydantic models (events, DB objects)
libs/hn_clients/   — Algolia + Firebase HN clients
libs/nlp/          — Embedding (sentence-transformers 384-dim) + opinion models
libs/storage/      — DB layer, migrations, repositories
libs/utils/        — Hashing, text cleaning, time windows
infra/             — Docker Compose, Dockerfiles, nginx (deferred)
migrations/        — Schema migrations (deferred)
```

### Tech Stack
- **Package manager:** uv
- **Backend:** Python 3.11+, FastAPI, Pydantic, Celery/RQ, Redis (queue + cache + event bus via Streams)
- **Storage:** DuckDB (embedded, with VSS extension for vector search)
- **Frontend:** Next.js (React), SSE for realtime, Recharts/Plotly
- **ML/NLP:** sentence-transformers (384-dim embeddings), transformer-based sentiment (valence/intensity/confidence), fasttext-langdetect
- **Deploy:** Docker Compose → single VPS or container platform (deferred)

### Core Concepts
- **Metric Node**: A durable broad-scale concern defined by a centroid embedding + label/definition. NOT a keyword — a semantic cluster.
- **Multi-mapping**: Each content item attaches to multiple metric nodes via softmax-weighted top-K nearest centroids (threshold >= 0.12).
- **Quantified values per node**: presence%, sentiment pie, valence (-100..+100), split/controversy, consensus (+/-), heat (intensity × unique authors), momentum (vs baseline).
- **Guardrails**: min unique authors to rank, per-author influence cap per node per day, confidence-weighting of opinion signals.

### Agent Execution Model
Agents are independent workers reading/writing DuckDB and publishing events through Redis Streams. The Supervisor Agent schedules periodic jobs (trending refresh, comment refresh, rollups, backfill). Event channels: `hn.discovery`, `hn.content`, `nlp.opinion`, `nlp.embedding`, `metric.mapping`, `metric.gardening`, `metric.rollups`, `moderation.ui`.

### Data Flow (Phase 1)
Algolia (discover) → Firebase (fetch items) → hn_item table → normalize → embed + opinion → map to metric nodes → rollups → API/SSE → dashboard

## Build & Run Commands

```bash
# Install dependencies
uv sync

# Backend API
uv run uvicorn apps.api.main:app --reload

# Workers (Celery)
uv run celery -A agents worker --loglevel=info

# Frontend
cd apps/web && npm run dev

# Tests
uv run pytest
uv run pytest tests/path/to/test_file.py::test_name  # single test

# Lint & type check
uv run ruff check .
uv run mypy .
```

## Development Rules

### Commits
- Small, focused commits. One logical change per commit.
- Each commit should be independently reviewable — if a reviewer can't understand it in under 2 minutes, it's too big.
- No "Co-Authored-By" lines. Commits should look like normal human commits.
- Commit messages: imperative mood, concise subject line. Body only if the "why" isn't obvious.
- Never bundle unrelated changes. If you're adding a model AND an API route, that's two commits.

### Code Changes
- Touch the minimum number of files needed. If a change spans 10+ files, break it into smaller PRs or commits.
- Add tests in the same commit as the code they test, not separately.
- Don't refactor surrounding code while implementing a feature — separate commit or separate PR.
- Don't add boilerplate "just in case" — no empty __init__.py files for modules that don't exist yet, no stub implementations for future agents.

### PR Discipline
- PRs should be small enough to review in one sitting (<300 lines changed, ideally <150).
- One concern per PR. "Add hn_item table + migration" is good. "Set up database layer with all tables and seed data" is too broad.
- If a milestone requires many changes, break it into a chain of small PRs that each leave the codebase in a working state.

## Phase Roadmap
- **Phase 1** (current): HN-only. Validate full agentic pipeline end-to-end. 6 milestones from live ingestion → metric intelligence → ranking lenses → year backfill.
- **Phase 2**: Add Reddit, X, RSS/blogs. Unified `content_item` schema. Cross-source dedup, amplification control, optional geo inference.
- **Phase 3**: Multi-tenant product. Custom topics, stance modeling (support/oppose), alerts, briefings, RBAC, compliance/ethics agent.
