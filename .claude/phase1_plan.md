# Phase 1 Plan — Hacker News Intelligence System (Agentic MVP)

**Goal:** Ship and deploy a public, reliable product that ingests Hacker News (HN), understands broad-scale concerns (“metrics”), quantifies how people feel about them, and updates in near-realtime.

This phase is deliberately **HN-only** to validate the full agentic pipeline end-to-end before adding other sources.

---

## 0) Outcomes & Constraints

### Outcomes
- Live dashboard: trending/top HN stories + their evolving “metric” mix
- Metrics page: broad concerns with quantified values + charts + explanations
- Backfill: all HN stories/comments for the current year (as seed data)
- Agentic architecture ready for Phase 2 (Reddit/X/blogs)

### Non-goals (Phase 1)
- No “trending hashtags”
- No per-user custom topics yet
- No geo/region inference yet (Phase 2)

### Practical constraints
- Must be deployable on a single VPS or small container platform
- Must be resilient to API hiccups and backfill scale
- Must be safe for public display (moderation/sanitization)

---

## 1) Technical Stack (Recommended)

### Backend + Workers
- **Python 3.11+**
- **FastAPI** (API server)
- **Pydantic** (schemas)
- **Celery** *(or RQ)* for background jobs
- **Redis** for:
  - task queue + caching
  - (optional) Redis Streams for event bus

### Storage
- **PostgreSQL 15+**
- **pgvector** extension for embeddings (Phase 1 uses it for KNN)
- Optional: **S3-compatible object storage** (MinIO/S3) for raw HTML/article dumps (can be postponed)

### Frontend
- **Next.js (React)** for UI
- **SSE (Server-Sent Events)** or WebSocket for near-realtime updates
- Charting: **Recharts** or **Plotly**

### ML / NLP
- Embeddings: **sentence-transformers** (384-dim recommended for cost/size)
- Sentiment/opinion:
  - Start with a transformer suitable for short forum text, producing **valence + confidence**
  - Intensity: derived from model logits spread, or a separate regression model later
- Language detection: **fasttext-langdetect** or lightweight alternative

### Observability
- Logging: **structlog** or stdlib logging (JSON logs)
- Metrics: **Prometheus** + **Grafana** (optional early), or OpenTelemetry
- Error reporting: Sentry (optional)

### Deployment
- Docker + docker-compose (Phase 1)
- Cloud: Fly.io / Render / Railway / DigitalOcean / AWS Lightsail
- Reverse proxy: Nginx / Caddy

---

## 2) Source APIs (HN)

### Recommended approach
- **Algolia HN Search API**: fast “top/trending” lists, queryable
- **HN Firebase API**: canonical items (story/comment), comment tree via `kids`

**Pattern:** use Algolia to discover and refresh a watchlist, then use Firebase to fetch item/comment details reliably.

---

## 3) Data Model (Phase 1)

### Canonical content tables
- `hn_item`
  - `id` (HN item id, PK)
  - `type` (story/comment/poll/etc)
  - `by` (author username) *store raw only if needed*
  - `author_hash` (sha256(salt + username))
  - `time` (unix)
  - `text` (HN HTML) + `text_clean` (plain)
  - `parent` (HN id)
  - `kids` (int[] optional)
  - `title`, `url`, `score`, `descendants` (stories)
  - `deleted`, `dead`
  - indexes: `(type, time)`, `(parent)`, `(time)`

- `author_profile`
  - `author_hash` (PK)
  - `first_seen_time`, `last_seen_time`
  - `comment_count`, `story_count`
  - `spam_score`, `bot_likelihood`
  - `influence_cap_state` (jsonb)

### ML outputs
- `embedding`
  - `item_id` (FK -> hn_item)
  - `embedding` (vector(384) via pgvector)
  - `model_version`

- `opinion_signal`
  - `item_id`
  - `valence` (float, -1..+1)
  - `intensity` (float, 0..1)
  - `confidence` (float, 0..1)
  - `label` (pos/neu/neg) *(optional derived)*
  - `model_version`

### Metric nodes (broad concerns)
- `metric_node`
  - `node_id` (uuid PK)
  - `label` (short)
  - `definition` (plain-English)
  - `centroid` (vector(384))
  - `parent_id` (uuid nullable)
  - `created_at`, `updated_at`
  - `status` (active/merged/deprecated)
  - `version` (int)
  - `health_stats` (jsonb: size, variance, drift)

- `item_metric_edge`
  - `item_id`
  - `node_id`
  - `weight` (0..1)
  - `created_at`
  - unique (item_id, node_id)

### Rollups for dashboards (pre-aggregated)
- `metric_rollup`
  - `node_id`
  - `window` (enum: today/week/month/year/all_time, plus optional last_60m)
  - `bucket_start` (timestamp)
  - `presence` (float)  # weighted share
  - `pos_share`, `neu_share`, `neg_share` (floats)
  - `valence_score` (-100..+100)
  - `split_score` (0..100)
  - `consensus_pos` (0..100)
  - `consensus_neg` (0..100)
  - `heat_score` (0..100)
  - `momentum` (-100..+100)
  - `unique_authors` (int)
  - `thread_count` (int)

---

## 4) Metric Semantics (Phase 1)

### What a “Metric Node” means
A **Metric Node** is a durable broad-scale concern/values axis (not a keyword). It’s defined by a centroid embedding + curated label/definition.

### Multi-mapping rule
Each comment/story can attach to **multiple nodes**:
- compute nearest nodes (top-K, e.g., K=5)
- convert distances to weights via softmax
- keep attachments above threshold (e.g., weight >= 0.12)

### Core quantified values (must be chartable)
- **Presence %**: node share of total weighted content
- **Sentiment pie**: pos/neu/neg shares
- **Valence score**: scaled to -100..+100
- **Split/controversy**: high when both pos and neg are meaningfully present
- **Consensus (+/-)**: strong when neutral is low and one side dominates
- **Heat**: intensity × unique authors (down-weight bots)
- **Momentum**: change vs baseline (today vs week average)

**Guardrails**
- Minimum unique authors to rank (e.g., >= 20 for “today” lists)
- Influence cap per author per node per day (e.g., max 3 full-weight then 0.2x)
- Confidence-weighting: low-confidence opinion signals down-weighted

---

## 5) Agent Cluster (Phase 1)

**Execution model:** agents are independent workers reading/writing to Postgres and publishing events through Redis (queue or streams). Supervisor schedules tasks.

### Event bus (recommended minimal)
- Redis Streams with channels:
  - `hn.discovery`
  - `hn.content`
  - `nlp.opinion`
  - `nlp.embedding`
  - `metric.mapping`
  - `metric.gardening`
  - `metric.rollups`
  - `moderation.ui`

### Agents

1) **Supervisor Agent**
- schedules periodic jobs:
  - trending refresh (every 60–120s)
  - comment refresh for hot stories (every 15–30s)
  - rollup updates (every 30–60s)
  - backfill batches (until done)
- handles retries/backoff; stores checkpoints

2) **Trend Scout Agent**
- pulls top/trending story IDs (Algolia)
- updates `watchlist` table with TTL and priority score (velocity/score)

3) **Thread Harvester Agent**
- fetches story + incremental comments via Firebase
- writes raw items to `hn_item`
- emits events for newly seen items

4) **Normalizer Agent**
- cleans HN HTML → plain text
- removes code blocks optionally (keep separately if desired)
- dedup:
  - exact: hash of normalized text
  - near-dup: optional later
- writes `text_clean`

5) **Author Integrity Agent**
- hashes usernames
- updates `author_profile` stats
- computes `bot_likelihood`, applies influence caps (weights)

6) **Opinion Analyst Agent**
- reads new normalized items
- computes valence/intensity/confidence
- writes `opinion_signal`

7) **Metric Mapper Agent**
- embeds text → `embedding`
- attaches items to metric nodes → `item_metric_edge`

8) **Metric Gardener Agent**
- creates initial metric nodes from backfilled data via clustering
- ongoing: conservative split/merge policy
- maintains parent/child hierarchy + versioning

9) **Rollup Accountant Agent**
- incremental rollups for each node per window
- computes ranking lists: top, controversial, consensus, heated, rising

10) **Moderator Agent**
- sanitizes representative examples and UI text:
  - redact emails/phones/addresses
  - suppress slurs/hate/harassment in displayed snippets
- marks items for UI as safe/sensitive/blocked

---

## 6) Repo Structure (Monorepo)

```
repo/
  apps/
    api/                # FastAPI
    web/                # Next.js
  agents/
    supervisor/
    trend_scout/
    thread_harvester/
    normalizer/
    author_integrity/
    opinion_analyst/
    metric_mapper/
    metric_gardener/
    rollup_accountant/
    moderator/
  libs/
    schemas/            # Pydantic models: events, db objects
    hn_clients/         # Algolia + Firebase clients
    nlp/                # embedding + opinion models
    storage/            # db, migrations, repositories
    utils/              # hashing, text cleaning, time windows
  infra/
    docker-compose.yml
    Dockerfile.api
    Dockerfile.agent
    nginx/              # optional
  migrations/           # Alembic
  docs/
    phase1_plan.md
```

---

## 7) API Endpoints (Phase 1)

### Public
- `GET /health`
- `GET /stories/trending?limit=50`
- `GET /stories/{id}` (story + metrics summary)
- `GET /stories/{id}/comments?limit=...`
- `GET /metrics/top?window=today|week|month|year|all_time`
- `GET /metrics/{node_id}?window=...`
- `GET /metrics/{node_id}/examples?window=...`
- `GET /rankings?window=...&lens=top|controversial|consensus_pos|consensus_neg|heated|rising`

### Realtime
- `GET /stream/trending` (SSE)
- `GET /stream/story/{id}` (SSE)
- `GET /stream/metrics` (SSE)

---

## 8) Deployment Plan (Phase 1)

### docker-compose services
- `postgres` (with pgvector)
- `redis`
- `api` (FastAPI)
- `web` (Next.js)
- `agent_*` (workers; scale out `thread_harvester`, `opinion_analyst`, `metric_mapper`)

### Scaling knobs
- Harvester concurrency
- Opinion + embedding batch size
- Rollup interval
- Watchlist size (hot stories only)

---

## 9) Milestones (Each must be deployable)

### Milestone 1 — Live HN Ingestion (Deployable)
**Deliverable:** trending stories + story detail + live comment updates  
**Agents:** Supervisor, Trend Scout, Thread Harvester  
**Success:** stable refresh, correct comment trees, basic UI

### Milestone 2 — Opinion Signals (Deployable)
**Deliverable:** per-story sentiment pie + heat indicator (live)  
**Agents:** + Normalizer, Author Integrity (basic), Opinion Analyst, Moderator (basic)  
**Success:** stable scores; low-confidence down-weighted; influence cap active

### Milestone 3 — Metric Nodes (Deployable)
**Deliverable:** metrics page + story→metrics mapping  
**Agents:** + Metric Mapper, Metric Gardener (creation only)  
**Success:** nodes are understandable; multi-mapping works; examples are clean

### Milestone 4 — Metric Intelligence (Deployable)
**Deliverable:** controversy/consensus/heat/momentum + plain-English explanations  
**Agents:** + Rollup Accountant  
**Success:** rankings stable; explanations reference quantified values

### Milestone 5 — Ranking Lenses (Deployable)
**Deliverable:** tabs/lenses: top, controversial, consensus, heated, rising  
**Success:** guardrails prevent tiny nodes from dominating lists

### Milestone 6 — Phase 1 Complete (Deployable)
**Deliverable:** year backfill complete, metric tree stable, production readiness  
**Success:** uptime, observability, moderation safe-by-default

---

## 10) Phase 1 Exit Criteria
- ✅ Backfill complete for current year
- ✅ Realtime updates stable
- ✅ Metric nodes meaningful and explainable
- ✅ Ranking lenses reliable
- ✅ Moderated UI safe
- ✅ Architecture cleanly supports new source adapters (Phase 2)
