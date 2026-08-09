# CivicPulse — Phase 1: Architecture

This is the buildable artifact for Phase 1. It fixes the Unity Catalog layout, every table's exact schema (Bronze/Silver/Gold Delta + Lakebase relational), and the agent's tool contracts, so Phase 2 (data engineering) has concrete tables to write into instead of design decisions to make on the fly.

---

## 1. Unity Catalog Layout

Free Edition gives you one default catalog/workspace — keep everything under a single catalog with schema-level separation so permissions and cleanup stay simple.

```
catalog: civicpulse
├── schema: bronze        -- raw ingested data, append-only
│   ├── bronze_bills
│   └── bronze_agendas
├── schema: silver        -- cleaned, typed, chunked
│   ├── silver_bills
│   └── silver_agenda_chunks
├── schema: gold          -- serving layer, queried by the app/agent
│   ├── gold_bill_summary
│   ├── gold_bill_chunks        -- chunk + embedding, synced to AI Search
│   └── gold_vote_history
└── schema: ops           -- pipeline bookkeeping
    └── ingestion_log
```

Naming convention: `{layer}_{entity}`. All tables are Delta by default (no `USING` clause needed on Free Edition serverless SQL).

---

## 2. Bronze Layer DDL

Raw landing zone. One row per ingested record/document, minimal transformation, full fidelity preserved for replay.

```sql
CREATE SCHEMA IF NOT EXISTS civicpulse.bronze;

CREATE TABLE IF NOT EXISTS civicpulse.bronze.bronze_bills (
  ingestion_id      STRING NOT NULL,      -- uuid, one per ingestion event
  source_bill_id    STRING NOT NULL,      -- Open States bill id, e.g. 'ocd-bill/...'
  state              STRING,
  session            STRING,
  raw_json           STRING,               -- full API response, untouched
  ingested_at        TIMESTAMP,
  source              STRING DEFAULT 'openstates_api'  -- or 'openstates_bulk_dump'
) USING DELTA;

CREATE TABLE IF NOT EXISTS civicpulse.bronze.bronze_agendas (
  ingestion_id      STRING NOT NULL,
  city                STRING NOT NULL,
  meeting_date       DATE,
  file_name          STRING,
  raw_bytes_path     STRING,               -- volume path to the original PDF
  raw_text           STRING,               -- extracted text, unstructured/unclean
  ingested_at        TIMESTAMP,
  source              STRING DEFAULT 'manual_upload'   -- or 'scraped'
) USING DELTA;
```

---

## 3. Silver Layer DDL

Cleaned, typed, chunked. This is where Spark does the real work: normalizing bill status fields, splitting agenda text into paragraphs, chunking for embedding.

```sql
CREATE SCHEMA IF NOT EXISTS civicpulse.silver;

CREATE TABLE IF NOT EXISTS civicpulse.silver.silver_bills (
  bill_id            STRING NOT NULL,     -- normalized key, PK
  state               STRING,
  session             STRING,
  title               STRING,
  status              STRING,              -- introduced | committee | hearing_scheduled | passed | failed
  sponsor             STRING,
  topics              ARRAY<STRING>,       -- derived topic tags, e.g. ['housing','rent_control']
  last_action_date    DATE,
  next_hearing_date   DATE,
  full_text           STRING,
  updated_at          TIMESTAMP
) USING DELTA;

CREATE TABLE IF NOT EXISTS civicpulse.silver.silver_agenda_chunks (
  chunk_id           STRING NOT NULL,     -- PK
  city                 STRING,
  meeting_date         DATE,
  agenda_item_title    STRING,
  chunk_text           STRING,             -- ~400-600 tokens, sentence-boundary aware
  chunk_index          INT,                -- position within the source document
  source_bronze_id     STRING,             -- FK back to bronze_agendas.ingestion_id
  created_at            TIMESTAMP
) USING DELTA;
```

---

## 4. Gold Layer DDL

Serving layer — what the SQL warehouse and AI Search index actually read from.

```sql
CREATE SCHEMA IF NOT EXISTS civicpulse.gold;

CREATE TABLE IF NOT EXISTS civicpulse.gold.gold_bill_summary (
  bill_id             STRING NOT NULL,    -- PK, matches silver_bills.bill_id
  state                STRING,
  title                STRING,
  plain_summary        STRING,             -- LLM-generated once, cached
  status                STRING,
  topics                ARRAY<STRING>,
  next_hearing_date     DATE,
  last_refreshed        TIMESTAMP
) USING DELTA;

-- Vector-enabled table synced to the single AI Search index (bills + agendas combined)
CREATE TABLE IF NOT EXISTS civicpulse.gold.gold_bill_chunks (
  chunk_id             STRING NOT NULL,   -- PK
  parent_id             STRING,            -- bill_id or agenda chunk_id
  parent_type            STRING,            -- 'bill' | 'agenda'
  chunk_text              STRING,
  embedding                ARRAY<FLOAT>,    -- populated by the embedding job
  state                    STRING,
  topics                    ARRAY<STRING>,
  created_at                 TIMESTAMP
) USING DELTA
TBLPROPERTIES (delta.enableChangeDataFeed = true);  -- lets AI Search sync incrementally

CREATE TABLE IF NOT EXISTS civicpulse.gold.gold_vote_history (
  bill_id              STRING NOT NULL,
  state                 STRING,
  topic                  STRING,
  outcome                 STRING,           -- passed | failed
  vote_date                DATE,
  vote_margin               STRING
) USING DELTA;
```

**AI Search index:** one endpoint, one index, built on `civicpulse.gold.gold_bill_chunks` with `embedding` as the vector column and Change Data Feed sync — this respects the one-endpoint/one-unit Free Edition limit by keeping bills and agenda chunks in a single combined index rather than two.

---

## 5. Lakebase Schema (Postgres DDL)

Relational application state — separate from the analytical Delta side, read/written directly by the agent and the app for low latency. This matches the ERD above.

```sql
CREATE TABLE users (
  user_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email              TEXT UNIQUE NOT NULL,
  state               TEXT NOT NULL,
  city                 TEXT,
  topics                TEXT[],            -- e.g. {'housing','small_business'}
  stake_statement        TEXT,              -- free-text "who I am" used to personalize tone
  created_at              TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE tracked_issues (
  issue_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id               UUID NOT NULL REFERENCES users(user_id),
  bill_id                 TEXT NOT NULL,     -- FK to Delta gold_bill_summary.bill_id (cross-store, no enforced FK)
  source_type              TEXT NOT NULL,     -- 'bill' | 'agenda_item'
  status                    TEXT NOT NULL,
  next_hearing_date          DATE,
  tracked_at                   TIMESTAMPTZ DEFAULT now(),
  status_updated_at             TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE testimony_drafts (
  draft_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id                UUID NOT NULL REFERENCES users(user_id),
  issue_id                 UUID NOT NULL REFERENCES tracked_issues(issue_id),
  draft_text                 TEXT NOT NULL,
  tone                        TEXT,             -- 'renter' | 'business_owner' | 'parent' | ...
  cited_sections                TEXT[],
  created_at                      TIMESTAMPTZ DEFAULT now(),
  submitted                        BOOLEAN DEFAULT false
);

CREATE TABLE notifications (
  notification_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id                  UUID NOT NULL REFERENCES users(user_id),
  issue_id                   UUID REFERENCES tracked_issues(issue_id),
  message                      TEXT NOT NULL,
  due_date                       DATE,
  read                              BOOLEAN DEFAULT false,
  created_at                          TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_tracked_issues_user ON tracked_issues(user_id);
CREATE INDEX idx_drafts_user ON testimony_drafts(user_id);
CREATE INDEX idx_notifications_user_unread ON notifications(user_id) WHERE read = false;
```

Note the deliberate boundary: Lakebase holds only per-user relational state (small, transactional, low-latency). Bill/agenda content stays entirely in Delta + AI Search — never duplicated into Lakebase. The agent bridges the two stores at query time.

---

## 6. Agent Tool Contracts (JSON Schema)

These are the exact tool definitions to register with your agent framework (Mosaic AI Agent Framework or a plain tool-calling loop against the foundation model API).

```json
[
  {
    "name": "search_bills_semantic",
    "description": "Semantic search over bill and agenda text for a topic or question.",
    "parameters": {
      "type": "object",
      "properties": {
        "query": {"type": "string"},
        "state": {"type": "string", "description": "Optional two-letter state code filter"},
        "topics": {"type": "array", "items": {"type": "string"}}
      },
      "required": ["query"]
    },
    "returns": "Array of {chunk_id, parent_id, parent_type, chunk_text, score}"
  },
  {
    "name": "get_bill_status",
    "description": "Get the current structured status of a specific bill.",
    "parameters": {
      "type": "object",
      "properties": {"bill_id": {"type": "string"}},
      "required": ["bill_id"]
    },
    "returns": "{bill_id, status, sponsor, last_action_date, next_hearing_date, topics}"
  },
  {
    "name": "get_vote_history",
    "description": "Look up past bill outcomes on a topic, optionally scoped to a state.",
    "parameters": {
      "type": "object",
      "properties": {
        "topic": {"type": "string"},
        "state": {"type": "string"}
      },
      "required": ["topic"]
    },
    "returns": "Array of {bill_id, state, outcome, vote_date, vote_margin}"
  },
  {
    "name": "get_user_profile",
    "description": "Load the requesting user's location, topics, and stated stake.",
    "parameters": {
      "type": "object",
      "properties": {"user_id": {"type": "string", "format": "uuid"}},
      "required": ["user_id"]
    },
    "returns": "{user_id, state, city, topics, stake_statement}"
  },
  {
    "name": "track_issue",
    "description": "Add a bill or agenda item to the user's watchlist. Write action.",
    "parameters": {
      "type": "object",
      "properties": {
        "user_id": {"type": "string", "format": "uuid"},
        "bill_id": {"type": "string"},
        "source_type": {"type": "string", "enum": ["bill", "agenda_item"]}
      },
      "required": ["user_id", "bill_id", "source_type"]
    },
    "returns": "{issue_id, status: 'tracked'}"
  },
  {
    "name": "save_testimony_draft",
    "description": "Persist an agent-drafted public comment, grounded in retrieved bill text. Write action.",
    "parameters": {
      "type": "object",
      "properties": {
        "user_id": {"type": "string", "format": "uuid"},
        "issue_id": {"type": "string", "format": "uuid"},
        "draft_text": {"type": "string"},
        "tone": {"type": "string"},
        "cited_sections": {"type": "array", "items": {"type": "string"}}
      },
      "required": ["user_id", "issue_id", "draft_text"]
    },
    "returns": "{draft_id, status: 'saved'}"
  },
  {
    "name": "update_issue_status",
    "description": "Refresh a tracked issue's status after checking the source of truth. Write action.",
    "parameters": {
      "type": "object",
      "properties": {
        "issue_id": {"type": "string", "format": "uuid"},
        "new_status": {"type": "string"}
      },
      "required": ["issue_id", "new_status"]
    },
    "returns": "{issue_id, status: 'updated'}"
  },
  {
    "name": "create_notification",
    "description": "Flag an approaching deadline or status change to the user. Write action.",
    "parameters": {
      "type": "object",
      "properties": {
        "user_id": {"type": "string", "format": "uuid"},
        "issue_id": {"type": "string", "format": "uuid"},
        "message": {"type": "string"},
        "due_date": {"type": "string", "format": "date"}
      },
      "required": ["user_id", "message"]
    },
    "returns": "{notification_id, status: 'created'}"
  }
]
```

---

## 7. Repo Structure (suggested)

```
civicpulse/
├── jobs/
│   ├── ingest_bills.py            -- Bronze: Open States -> bronze_bills
│   ├── ingest_agendas.py          -- Bronze: PDFs -> bronze_agendas
│   ├── transform_bills.py         -- Bronze -> Silver -> Gold (bill_summary)
│   ├── transform_agendas.py       -- Bronze -> Silver (chunking)
│   └── embed_chunks.py            -- Silver/Gold -> embeddings -> AI Search sync
├── agent/
│   ├── tools.py                   -- implementations of the 8 tool contracts above
│   ├── agent.py                   -- tool-calling loop / Agent Framework config
│   └── prompts.py                 -- system prompt, grounding/citation rules
├── app/
│   ├── main.py                    -- Databricks App entrypoint
│   ├── pages/                     -- feed, bill detail, chat, dashboard, history
│   └── lakebase_client.py
├── sql/
│   ├── bronze_ddl.sql
│   ├── silver_ddl.sql
│   ├── gold_ddl.sql
│   └── lakebase_ddl.sql
└── README.md
```

---

## 8. Phase 1 Checklist

- [ ] Create `civicpulse` catalog and the four schemas
- [ ] Run Bronze/Silver/Gold DDL
- [ ] Provision the single Lakebase project, run Lakebase DDL
- [ ] Register an Open States API key; download the bulk-data fallback for 1–2 target states
- [ ] Confirm AI Search endpoint/index can be created against `gold_bill_chunks`
- [ ] Stub out the 8 agent tools as functions returning mock data, so the agent loop can be tested before Phase 2 lands real data

Once this checklist is done, Phase 2 is purely "make `ingest_bills.py` and `ingest_agendas.py` real" against tables that already exist.
