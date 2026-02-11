# Phase 3 Plan — Custom Intelligence for Businesses & Politics

**Goal:** Turn the system into a configurable intelligence product for organizations while enforcing strong safety and ethics boundaries.

---

## 0) Outcomes & Guardrails

### Outcomes
- Custom topics (brands, products, policies, people) defined by clients
- Stance modeling (support/oppose) separate from sentiment
- Alerts + reports + executive briefings
- Role-based access control and auditability

### Guardrails (must-have)
- Aggregate insights only (no microtargeting individuals)
- No individual profiling features
- Clear uncertainty, coverage, and bias indicators
- Strong moderation and redaction pipeline

---

## 1) Technical Stack Additions

### Identity & Auth
- Auth: OAuth (Auth0/Clerk) or self-hosted (Keycloak)
- RBAC: roles (admin, analyst, viewer)
- Tenant model: multi-tenant with Postgres **Row Level Security (RLS)**

### Reporting & Alerts
- Scheduled jobs: Celery beat (or APScheduler)
- Email: Postmark/SendGrid/SES
- Webhooks: Slack/Teams
- PDF generation: Playwright (HTML->PDF) or WeasyPrint
- Template engine: Jinja2 for HTML reports

### Data governance
- Encryption at rest (managed DB) + KMS if needed
- Audit log table + immutable append-only logs
- Secrets: Vault or cloud secrets manager

---

## 2) Product Features (Phase 3)

### A) Custom Topics
Topic definition includes:
- keywords + exclusions
- semantic description (embedding)
- optional example posts
- source constraints (which platforms)
- time/region/language constraints

Outputs:
- topic dashboards backed by the shared metric map
- topic→metric mapping (“what broader concerns this topic connects to”)

### B) Stance Modeling
Separate from sentiment:
- labels: support / oppose / mixed / irrelevant
- computed relative to a topic/entity
- show stance distribution + trend

### C) Alerts
Triggers:
- negative stance spike
- controversy increase
- emerging narrative within topic
- regional surge (if geo enabled)

### D) Briefings
Auto-generated summaries:
- what changed
- why (top driver metrics)
- representative examples (moderated)
- confidence and sampling notes

---

## 3) New Agents (Phase 3)

1) **Client Topic Agent**
- manages topic definitions
- builds topic embeddings
- runs topic matcher over new content
- maintains topic→metric links

2) **Stance Analyst Agent**
- stance classification conditioned on topic/entity
- writes stance signals and confidence

3) **Alert Agent**
- monitors rollups and triggers notifications
- debounces alerts to avoid spam

4) **Briefing Agent**
- produces executive summaries (structured JSON + optional narrative text)
- includes quantified metrics and driver breakdowns

5) **Compliance & Ethics Agent**
- enforces guardrails:
  - blocks requests implying microtargeting
  - audits outputs for disallowed content
- adds “safety notes” to reports where relevant

---

## 4) Tenant / User Data Model

- `tenant`
- `user` (tenant_id)
- `topic` (tenant_id)
- `topic_match` (topic_id, content_item_id, score)
- `topic_rollup` (topic_id, window, metrics similar to metric_rollup)
- `stance_signal` (content_item_id, topic_id, label, confidence)
- `alert_rule` (tenant_id, topic_id, thresholds)
- `alert_event` (tenant_id, topic_id, triggered_at, payload)
- `report` (tenant_id, topic_id, generated_at, storage_ref)
- `audit_log` (tenant_id, actor_id, action, payload, ts)

Use Postgres **RLS** so tenants cannot access each other’s data.

Shared global tables remain:
- `content_item`, `metric_node`, `item_metric_edge`, etc.

---

## 5) UI (Phase 3)

- Tenant dashboard
- Topic builder (keywords + semantic definition + examples)
- Topic analytics:
  - presence
  - sentiment pie
  - stance pie
  - controversy/consensus/heat/momentum
  - drivers (metric nodes + child nodes)
- Alerts configuration + history
- Report center (PDF/HTML exports)

---

## 6) Milestones (Each deployable)

### Milestone 1 — Multi-tenant foundation (Deployable)
- Auth + RLS + tenant scoping
- Basic topic creation (no stance yet)

### Milestone 2 — Topic Matching (Deployable)
- semantic + rules-based matcher
- topic dashboards with sentiment + drivers

### Milestone 3 — Stance (Deployable)
- stance model and stance charts
- stance-based rankings and deltas

### Milestone 4 — Alerts (Deployable)
- threshold alerts + debouncing
- email/webhook notifications

### Milestone 5 — Briefings & Reports (Deployable)
- scheduled briefings
- PDF/HTML export with charts and explanations

### Milestone 6 — Compliance & Audit (Deployable)
- audit logs
- compliance agent checks
- stronger moderation pipeline

---

## 7) Phase 3 Exit Criteria
- ✅ Clients can define topics and get reliable, explainable insights
- ✅ Stance is separated from sentiment
- ✅ Alerts and reports are production-grade
- ✅ Safety and compliance guardrails enforced by design
