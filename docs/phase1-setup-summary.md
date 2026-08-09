# CivicPulse — Phase 1 Setup Summary (Completed)

This documents everything provisioned and verified during Phase 1, so Phase 2
(data engineering) can build directly on top of it without re-deciding anything.
Reference architecture: `architecture.md`.

---

## 1. Unity Catalog

- Catalog: `civicpulse`
- Schemas created: `bronze`, `silver`, `gold`, `ops`
- All tables are Delta by default (Free Edition serverless SQL)

## 2. Bronze / Silver / Gold DDL — run and confirmed

- `civicpulse.bronze.bronze_bills`
- `civicpulse.bronze.bronze_agendas`
- `civicpulse.silver.silver_bills`
- `civicpulse.silver.silver_agenda_chunks`
- `civicpulse.gold.gold_bill_summary`
- `civicpulse.gold.gold_bill_chunks` — `delta.enableChangeDataFeed = true`,
  `delta.deletedFileRetentionDuration` extended to 30 days
- `civicpulse.gold.gold_vote_history`

All exactly match the DDL in `architecture.md` sections 2–4. No deviations.

## 3. Lakebase (Postgres)

- One Lakebase instance provisioned: `civicpulse-lakebase`
- DDL run and confirmed: `users`, `tracked_issues`, `testimony_drafts`,
  `notifications`, plus the 3 indexes from the architecture doc section 5
- Connection details held outside this doc (host/port/credentials) — not real
  data yet, tables are empty and ready for Phase 2 writes

## 4. Open States — data source

- API key registered, stored as a Databricks secret:
  scope=`civicpulse`, key=`openstates_api_key`
- Bulk-data fallback downloaded and staged:
  - State: **Alabama**, session **2026rs** (current/active session)
  - 1,507 bills, JSON format, ~15MB
  - Uploaded to: `/Volumes/civicpulse/bronze/raw_files/alabama_2026/AL_2026rs_bills.json`
  - Confirmed field shape: `id`, `title`, `classification`, `actions[]`
    (status must be *derived* from `actions[].classification` — there's no
    direct `status` field in the source data — flag this for `transform_bills.py`)

## 5. AI Search (Vector Search)

- Endpoint: `civicpulse-endpoint` — Online
- Index: `civicpulse.gold.civicpulse_gold_bill_chunks_index`
  - Source table: `civicpulse.gold.gold_bill_chunks`
  - Primary key: `chunk_id`
  - Index type: Hybrid (Delta Sync + keyword, built on CDF)
  - Embeddings: **existing embedding column** (not auto-computed) —
    `embedding` column, dimension **1024**
  - **Chosen embedding model for Phase 2:** `databricks-gte-large-en`
    (Databricks Foundation Model API, pay-per-token, 1024-dim) — this is
    what `embed_chunks.py` must call to populate `gold_bill_chunks.embedding`
  - Sync mode: Triggered

## 6. Agent — tool-calling loop, tested and working

- LLM provider: **Google Gemini** (`gemini-3.6-flash`), via the Interactions API
  - Chosen over Anthropic's API specifically because it needs no credit card
  - Key stored as Databricks secret: scope=`civicpulse`, key=`gemini_api_key`
- All 8 tool contracts from architecture doc section 6 stubbed with mock data:
  `search_bills_semantic`, `get_bill_status`, `get_vote_history`,
  `get_user_profile`, `track_issue`, `save_testimony_draft`,
  `update_issue_status`, `create_notification`
- Verified live: multi-turn conversation correctly selects the right tool,
  passes correct arguments, and carries context across turns
  (tested: bill status lookup → track that same bill for a user)
- Notebook: single-file Databricks notebook (not a git repo — everything
  runs inline in the workspace), tool stubs + schemas + loop all in one file

## 7. What Phase 2 inherits, unchanged

- All table schemas — exact column names/types Phase 2 scripts must write into
- The embedding model choice (`databricks-gte-large-en`, 1024-dim) — must match
  or the vector index will reject writes
- The mock tool **signatures and return shapes** in the agent notebook — Phase 2
  replaces each function body with a real Delta/Lakebase query, but keeps the
  same inputs/outputs so the agent loop needs zero changes
- The known gap: bill `status` needs derivation logic from `actions[]`, not a
  direct field copy

## 8. Not yet done (this is what Phase 2 is)

- `ingest_bills.py` — real ingestion from Open States API + Alabama JSON fallback → `bronze_bills`
- `ingest_agendas.py` — city agenda PDFs → `bronze_agendas` (separate pipeline, no bulk source exists for this)
- `transform_bills.py` / `transform_agendas.py` — Bronze → Silver → Gold, including status derivation
- `embed_chunks.py` — call `databricks-gte-large-en` to populate `gold_bill_chunks.embedding`
- Swapping the 8 mock tool bodies for real queries

---

## Status as of this repo

**This repo implements Phase 2** (see root `README.md`): `ingest_bills.py`,
`ingest_agendas.py`, `transform_bills.py` (including the `actions[]` → status
derivation flagged above), `transform_agendas.py`, and `embed_chunks.py` are
now real implementations against the tables above, and all 8 agent tools
have real bodies behind their unchanged Phase 1 signatures, with a
`CIVICPULSE_MOCK_MODE` fallback for offline/local demo use.

**LLM provider superseded:** Phase 1 (above) picked Gemini via an external
API key. This repo instead runs the agent entirely on the workspace's own
**Databricks Foundation Model API** — chat/tool-calling and embeddings both
go through `WorkspaceClient().serving_endpoints.get_open_ai_client()`
(`agent/llm.py`). This removes the external-provider dependency altogether:
no `gemini_api_key` secret is needed, nothing leaves the workspace, and it's
still zero-credit-card, same as the original Free Edition requirement that
motivated picking Gemini in the first place.
