-- CivicPulse — Lakebase schema (Postgres)
-- Relational application state: per-user, small, transactional, low-latency.
-- Bill/agenda content is NEVER duplicated here — it stays in Delta + AI Search.
-- The agent bridges the two stores at query time (bill_id is a cross-store
-- reference, not an enforced FK).

CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- for gen_random_uuid()

CREATE TABLE IF NOT EXISTS users (
  user_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email              TEXT UNIQUE NOT NULL,
  state               TEXT NOT NULL,
  city                 TEXT,
  topics                TEXT[],            -- e.g. {'housing','small_business'}
  stake_statement        TEXT,              -- free-text "who I am" used to personalize tone
  created_at              TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS tracked_issues (
  issue_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id               UUID NOT NULL REFERENCES users(user_id),
  bill_id                 TEXT NOT NULL,     -- FK to Delta gold_bill_summary.bill_id (cross-store, no enforced FK)
  source_type              TEXT NOT NULL CHECK (source_type IN ('bill', 'agenda_item')),
  status                    TEXT NOT NULL,
  next_hearing_date          DATE,
  tracked_at                   TIMESTAMPTZ DEFAULT now(),
  status_updated_at             TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS testimony_drafts (
  draft_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id                UUID NOT NULL REFERENCES users(user_id),
  issue_id                 UUID NOT NULL REFERENCES tracked_issues(issue_id),
  draft_text                 TEXT NOT NULL,
  tone                        TEXT,             -- 'renter' | 'business_owner' | 'parent' | ...
  cited_sections                TEXT[],
  created_at                      TIMESTAMPTZ DEFAULT now(),
  submitted                        BOOLEAN DEFAULT false
);

CREATE TABLE IF NOT EXISTS notifications (
  notification_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id                  UUID NOT NULL REFERENCES users(user_id),
  issue_id                   UUID REFERENCES tracked_issues(issue_id),
  message                      TEXT NOT NULL,
  due_date                       DATE,
  read                              BOOLEAN DEFAULT false,
  created_at                          TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_tracked_issues_user ON tracked_issues(user_id);
CREATE INDEX IF NOT EXISTS idx_drafts_user ON testimony_drafts(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user_unread ON notifications(user_id) WHERE read = false;
