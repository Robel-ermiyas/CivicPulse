-- CivicPulse — Bronze layer
-- Raw landing zone. One row per ingested record/document, minimal transformation,
-- full fidelity preserved for replay. Append-only.

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
