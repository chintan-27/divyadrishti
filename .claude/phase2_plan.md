# Phase 2 Plan — Multi-Source Intelligence Expansion (Reddit, X, Blogs)

**Goal:** Expand from HN-only to a multi-source intelligence system while keeping metric semantics stable and comparable across platforms.

---

## 0) Outcomes & Constraints

### Outcomes
- Add **Reddit** (threads + comments) as second source
- Add **X (Twitter)** as third source (if API access available)
- Add **Blogs/News** via RSS + article extraction
- Cross-source dedup + normalization
- Optional: regional/geo inference (confidence-weighted)

### Constraints
- Do not rebuild the metric system per platform
- Avoid shallow “trending” features; keep broad concerns
- Aggressively protect against bots/amplification (especially X)

---

## 1) Technical Stack Additions

### Ingestion connectors
- Reddit: **PRAW** or direct API + async client
- X: official X API client (handle rate limits + paid tiers)
- RSS: **feedparser**
- Article extraction: **trafilatura** or **readability-lxml**
- URL canonicalization: `url-normalize`, custom rules per domain

### Search / indexing (optional upgrade)
- OpenSearch/Elasticsearch for fast text search and timeline queries
- Keep pgvector for semantic mapping; consider OpenSearch vector if consolidating

### Message bus (if scaling)
- Redis Streams → Kafka (optional) once throughput increases

---

## 2) Unified Content Schema

Create a cross-platform `content_item` abstraction:

- `content_item`
  - `id` (internal uuid)
  - `source` (hn|reddit|x|blog)
  - `source_item_id` (string)
  - `thread_id` (string)
  - `parent_id` (string nullable)
  - `author_hash`
  - `created_at`
  - `text_raw`, `text_clean`
  - `url`
  - `engagement` (json: score/likes/retweets/replies)
  - `metadata` (json: subreddit, hashtags, lang, etc)
  - unique (source, source_item_id)

Migrate HN pipeline to write into `content_item` (HN-specific tables can remain as raw store if you like).

---

## 3) New / Updated Agents (Phase 2)

### A) Source Adapter Agents
1) **Reddit Adapter Agent**
- pulls configured subreddits or search queries
- ingests posts + comment trees
- normalizes into `content_item`

2) **X Adapter Agent**
- ingests posts + replies (query-based)
- separates originals vs reposts/retweets
- stores amplification metadata in `engagement/metadata`

3) **RSS/Blog Adapter Agent**
- ingests RSS feeds
- fetches full article HTML where allowed
- extracts clean article text into `content_item`

### B) Cross-Source Quality & Fusion
4) **Cross-Source Dedup Agent**
- canonical URL normalization
- near-duplicate clustering across sources via embedding similarity
- produces a `canonical_cluster_id` (optional table)

5) **Amplification Control Agent (X-focused)**
- down-weights retweets/reposts
- detects repost storms
- computes organic vs amplified presence per metric

6) **Geo Inference Agent (optional Phase 2)**
- derives region using:
  - explicit geotags (rare)
  - profile location parsing
  - text place mentions (NER + gazetteer)
  - community proxy (local subreddits)
- outputs `region_id` + `geo_confidence`

---

## 4) Metric Enhancements (Cross-Source)

### Cross-source rollups
For each metric node:
- presence by source (stacked)
- platform diversity score (how many sources contribute)
- source bias warnings (e.g., 90% from one platform)

### Narrative drivers
- child nodes become “drivers”
- track which drivers are rising within the parent metric

### Regional views (if enabled)
- per region: presence, sentiment pie, controversy, heat
- always show coverage + confidence indicators

---

## 5) UI Views (Phase 2)

- Multi-source metrics dashboard
- Compare metric presence across sources (HN vs Reddit vs X vs Blogs)
- “Organic vs amplified” lens for X
- Regional view (optional) with confidence overlay
- Filters:
  - source selection
  - time window
  - language
  - region (if enabled)

---

## 6) Deployment & Scaling (Phase 2)

### Scale units
- adapters scaled independently per source
- embedding + opinion analysis scaled horizontally
- dedup agent may need more CPU/memory

### Storage evolution
- Keep Postgres as system of record
- Consider:
  - OpenSearch for full-text + vector
  - Dedicated vector DB if embeddings dominate cost/latency

### Compliance
- Respect each platform ToS
- Store only permitted fields
- Ability to delete content if required

---

## 7) Milestones (Each deployable)

### Milestone 1 — Unified Schema Migration (Deployable)
- Convert HN pipeline to write `content_item`
- No UX change; enables multi-source

### Milestone 2 — Reddit Integration (Deployable)
- Ingest selected subreddits + comments
- Metrics show HN+Reddit with source breakdown

### Milestone 3 — RSS/Blogs Integration (Deployable)
- Ingest RSS feeds
- Extract article content + canonical URL dedup
- Metrics include blogs (clearly labeled)

### Milestone 4 — X Integration (Deployable, if API access)
- Ingest query streams
- Amplification control active
- Show organic vs amplified presence

### Milestone 5 — Cross-Source Dedup (Deployable)
- Near-duplicate + canonical URL normalization across sources
- Narratives unify without double counting

### Milestone 6 — Regional Intelligence (Deployable, optional)
- Geo inference + confidence-weighted regional rollups
- UI exposes coverage/confidence

---

## 8) Phase 2 Exit Criteria
- ✅ Multi-source ingestion stable
- ✅ Cross-source metrics comparable and explainable
- ✅ Amplification control prevents distortion
- ✅ Optional: regional views with confidence indicators
