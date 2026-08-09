-- CivicPulse — Gold / serving layer
-- What the SQL warehouse, agent tools, and AI Search index actually read from.

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

-- Vector-enabled table synced to the single AI Search index (bills + agendas combined).
CREATE TABLE IF NOT EXISTS civicpulse.gold.gold_bill_chunks (
  chunk_id             STRING NOT NULL,   -- PK
  parent_id             STRING,            -- bill_id or agenda chunk_id
  parent_type            STRING,            -- 'bill' | 'agenda'
  chunk_text              STRING,
  embedding                ARRAY<FLOAT>,    -- populated by embed_chunks.py (databricks-gte-large-en, 1024-dim)
  state                    STRING,
  topics                    ARRAY<STRING>,
  created_at                 TIMESTAMP
) USING DELTA
TBLPROPERTIES (
  delta.enableChangeDataFeed = true,               -- lets AI Search sync incrementally
  delta.deletedFileRetentionDuration = 'interval 30 days'
);

CREATE TABLE IF NOT EXISTS civicpulse.gold.gold_vote_history (
  bill_id              STRING NOT NULL,
  state                 STRING,
  topic                  STRING,
  outcome                 STRING,           -- passed | failed
  vote_date                DATE,
  vote_margin               STRING
) USING DELTA;

-- Pipeline bookkeeping (ops schema) — used by every ingest/transform job for idempotent, resumable runs.
CREATE SCHEMA IF NOT EXISTS civicpulse.ops;

CREATE TABLE IF NOT EXISTS civicpulse.ops.ingestion_log (
  run_id               STRING NOT NULL,
  job_name              STRING NOT NULL,   -- e.g. 'ingest_bills', 'transform_bills', 'embed_chunks'
  source_table           STRING,
  target_table             STRING,
  rows_in                   BIGINT,
  rows_out                    BIGINT,
  status                        STRING,     -- 'success' | 'failed'
  error_message                  STRING,
  started_at                       TIMESTAMP,
  finished_at                        TIMESTAMP
) USING DELTA;
