-- CivicPulse — Silver layer
-- Cleaned, typed, chunked. Spark normalizes bill status fields, splits agenda
-- text into paragraphs, and chunks text for embedding.

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
