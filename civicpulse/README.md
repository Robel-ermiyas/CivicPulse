# CivicPulse

**Your legislative staffer, for free.**

CivicPulse reads state bills and city council agendas the moment they drop,
tells a resident which ones actually affect their life, and drafts their
public testimony before the comment window closes — the kind of tracking
paid lobbying platforms (FiscalNote, Quorum) charge thousands of dollars a
year for.

Built for the Databricks AI Capstone (Free Edition only — no paid
infrastructure anywhere in this repo). Full reasoning for why this idea over
the five official prompts is in [`docs/strategy.md`](docs/strategy.md); the
locked-in schema/contract design is in [`docs/architecture.md`](docs/architecture.md);
what Phase 1 actually provisioned is in [`docs/phase1-setup-summary.md`](docs/phase1-setup-summary.md).

---

## What's actually in this repo

Phase 1 (architecture + provisioning) is done — see the setup summary. **This
repo is Phase 2 and onward**: real Spark ingestion/transform jobs, a real
embedding pipeline, real agent tool bodies behind the Phase-1-tested tool
signatures, and a Databricks App frontend.

```
civicpulse/
├── sql/                    # Bronze/Silver/Gold Delta DDL + Lakebase (Postgres) DDL
├── jobs/                   # Spark jobs: ingest -> transform -> embed
│   └── common/             # shared Spark session, run-logging, text chunking
├── agent/                  # tool contracts, tool implementations, LLM wrapper, chat loop
├── app/                    # Databricks App (Streamlit): feed, bill detail, chat, dashboard, history
│   └── pages/
├── config/                 # single source of truth for catalog/schema/table/model names
├── resources/              # Databricks Asset Bundle job + app definitions
├── docs/                   # strategy, architecture, and Phase 1 setup docs this repo builds on
├── tests/                  # unit tests for the parts that don't need a live Spark/warehouse
├── databricks.yml          # Asset Bundle entrypoint (`databricks bundle deploy`)
└── requirements.txt
```

## Architecture at a glance

```
Open States API/bulk JSON ─┐
                            ├─> bronze_bills ──┐
City council PDFs ─────────┘                   ├─> transform ─> silver_bills / silver_agenda_chunks
                            bronze_agendas ─────┘        │
                                                          ├─> gold_bill_summary   (cached plain-language summaries)
                                                          ├─> gold_bill_chunks    (embedded, CDF-synced to AI Search)
                                                          └─> gold_vote_history

AI Search (1 endpoint, 1 index) <──CDF sync── gold_bill_chunks
        │
        ▼
   agent (Databricks Foundation Model API, tool-calling loop) ──reads──> Gold via SQL warehouse, AI Search
        │                              ──reads/writes──> Lakebase (users, tracked_issues,
        │                                                 testimony_drafts, notifications)
        ▼
   Databricks App (Streamlit): feed / bill detail / chat / dashboard / history
```

Every Free Edition constraint this maps to is enumerated with its specific
workaround in `docs/strategy.md` section 14 (one 2X-Small warehouse, ≤5
concurrent job tasks, one AI Search endpoint/unit, one Lakebase project, ≤3
Apps, restricted outbound internet).

## The agent's 8 tools

Read: `search_bills_semantic`, `get_bill_status`, `get_vote_history`, `get_user_profile`
Write: `track_issue`, `save_testimony_draft`, `update_issue_status`, `create_notification`

Contracts live in `agent/schemas.py` (unchanged from the Phase 1 stub
notebook). Bodies live in `agent/tools.py`, each with a `MOCK_MODE` fallback
so the whole loop is exercisable without live infrastructure — set
`CIVICPULSE_MOCK_MODE=false` once the warehouse/Lakebase/AI Search endpoint
above are live.

## Getting started

### 1. Provision infrastructure (Phase 1 — see `docs/phase1-setup-summary.md` for what's already done)

```bash
databricks bundle deploy -t dev          # deploys the job pipeline + app resources
databricks sql exec -f sql/catalog_setup.sql
databricks sql exec -f sql/bronze_ddl.sql
databricks sql exec -f sql/silver_ddl.sql
databricks sql exec -f sql/gold_ddl.sql
# Lakebase: provision an instance named civicpulse-lakebase, then run
psql "$LAKEBASE_CONNINFO" -f sql/lakebase_ddl.sql
```

Register secrets (only Open States needs one — the agent runs on the
workspace's own Databricks Foundation Model API, no external LLM key):
```bash
databricks secrets create-scope civicpulse
databricks secrets put-secret civicpulse openstates_api_key
```

### 2. Run the pipeline

Either trigger `civicpulse-nightly-pipeline` (see `resources/jobs.yml`) from
the workspace, or run locally against a dev Spark session:

```bash
pip install -r requirements.txt
python -m jobs.ingest_bills      # bulk-dump fallback by default (offline-safe)
python -m jobs.ingest_agendas
python -m jobs.transform_bills   # includes the actions[] -> status derivation
python -m jobs.transform_agendas
python -m jobs.embed_chunks      # databricks-gte-large-en, incremental
```

### 3. Run the app

```bash
export CIVICPULSE_MOCK_MODE=true   # or false once infra above is live
streamlit run app/main.py
```

### 4. Run tests

```bash
pytest tests/
```

## Data source & scope

- **Bills:** Open States (all 50 states, free/public). Demo build scoped to
  **Alabama, session 2026rs** (1,507 bills, bulk JSON dump — see
  `config/settings.TARGET_STATES` / `ALABAMA_BULK_DUMP_PATH`) to keep the
  Free Edition build inside quota per the strategy doc's scope-creep
  mitigation. Live API path (`jobs/ingest_bills.py: fetch_live`) is wired and
  ready once outbound access to openstates.org is confirmed from the
  workspace.
- **Agendas:** city council PDFs, no bulk source exists — staged manually per
  demo city (`config/settings.DEMO_CITY`), extracted with `pdfplumber`.

## Known gap carried from Phase 1

The Open States bulk export has no direct `status` field — `transform_bills.py`
derives it from each bill's `actions[].classification` history
(`derive_status`, unit-tested in `tests/test_transform_bills.py`).

## Grounding & citation rules

The agent (`agent/prompts.py`) is instructed to never state a fact about a
bill without a tool call backing it, to cite specific bill sections in every
testimony draft, and to always frame drafts as informational — never legal
advice (strategy doc section 18, "legal-sounding claims" risk).

## Evaluation

See `docs/strategy.md` section 16 for the full plan (retrieval hit@k,
groundedness spot-checks, tool-selection accuracy against scripted
conversations, action success rate, latency target <8s). `tests/` currently
covers the deterministic, non-LLM pieces (status derivation, chunking); the
retrieval/groundedness checks are meant to run as scripted conversations
against a live agent, not as offline unit tests.

## What's still ahead (stretch, per the roadmap in `docs/strategy.md` §19)

- Second demo persona already supported (`app/main.py: DEMO_PROFILES`) — add
  more tones/topics
- Topic-clustering visualization, "similar bill elsewhere" suggestions
- Multi-state expansion beyond Alabama once quota headroom is confirmed
- OCR path for scanned (non-digital-native) council agendas
