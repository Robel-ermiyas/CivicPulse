"""
CivicPulse — central configuration.

Every job, agent tool, and app page imports from here instead of hard-coding
catalog/schema/table names, so a rename or environment change happens in one
place. Values below match what Phase 1 actually provisioned (see
docs/phase1-setup-summary.md) — do not drift from these without updating that
doc and the AI Search index definition together.
"""

import os

# ---------------------------------------------------------------------------
# Unity Catalog
# ---------------------------------------------------------------------------
CATALOG = "civicpulse"

BRONZE_SCHEMA = f"{CATALOG}.bronze"
SILVER_SCHEMA = f"{CATALOG}.silver"
GOLD_SCHEMA = f"{CATALOG}.gold"
OPS_SCHEMA = f"{CATALOG}.ops"

BRONZE_BILLS = f"{BRONZE_SCHEMA}.bronze_bills"
BRONZE_AGENDAS = f"{BRONZE_SCHEMA}.bronze_agendas"

SILVER_BILLS = f"{SILVER_SCHEMA}.silver_bills"
SILVER_AGENDA_CHUNKS = f"{SILVER_SCHEMA}.silver_agenda_chunks"

GOLD_BILL_SUMMARY = f"{GOLD_SCHEMA}.gold_bill_summary"
GOLD_BILL_CHUNKS = f"{GOLD_SCHEMA}.gold_bill_chunks"
GOLD_VOTE_HISTORY = f"{GOLD_SCHEMA}.gold_vote_history"

INGESTION_LOG = f"{OPS_SCHEMA}.ingestion_log"

RAW_FILES_VOLUME = f"/Volumes/{CATALOG}/bronze/raw_files"

# ---------------------------------------------------------------------------
# AI Search (Vector Search) — one endpoint / one index, Free Edition limit
# ---------------------------------------------------------------------------
AI_SEARCH_ENDPOINT = "civicpulse-endpoint"
AI_SEARCH_INDEX = f"{CATALOG}.gold.civicpulse_gold_bill_chunks_index"
AI_SEARCH_PRIMARY_KEY = "chunk_id"
AI_SEARCH_SYNC_MODE = "TRIGGERED"

# Embedding model chosen in Phase 1. embed_chunks.py must call exactly this
# model — the vector index rejects writes for any other dimension.
EMBEDDING_MODEL = "databricks-gte-large-en"
EMBEDDING_DIM = 1024

# ---------------------------------------------------------------------------
# Lakebase (Postgres) — single project, per-user relational state only
# ---------------------------------------------------------------------------
LAKEBASE_INSTANCE_NAME = "civicpulse-lakebase"
LAKEBASE_HOST = os.environ.get("LAKEBASE_HOST", "")
LAKEBASE_PORT = int(os.environ.get("LAKEBASE_PORT", "5432"))
LAKEBASE_DATABASE = os.environ.get("LAKEBASE_DATABASE", "civicpulse")
LAKEBASE_USER = os.environ.get("LAKEBASE_USER", "")
LAKEBASE_PASSWORD = os.environ.get("LAKEBASE_PASSWORD", "")  # prefer a Databricks secret in prod

# ---------------------------------------------------------------------------
# Secrets (Databricks secret scope), per Phase 1 setup
# ---------------------------------------------------------------------------
# Only Open States needs a secret -- the agent's LLM calls (chat + embeddings)
# go through the Databricks Foundation Model API via the workspace's own
# native auth (agent/llm.py), no external key required.
SECRET_SCOPE = "civicpulse"
OPENSTATES_API_KEY_SECRET = "openstates_api_key"

# ---------------------------------------------------------------------------
# Data source scope (kept intentionally narrow — see strategy doc section 18,
# "Scope creep" risk. Expand this list only after the demo path is solid.)
# ---------------------------------------------------------------------------
TARGET_STATES = ["AL"]          # Alabama first (bulk dump already staged, Phase 1)
TARGET_SESSION = "2026rs"
DEMO_CITY = "Demo City"          # replace with the real council once agenda PDFs are sourced

ALABAMA_BULK_DUMP_PATH = f"{RAW_FILES_VOLUME}/alabama_2026/AL_2026rs_bills.json"

# ---------------------------------------------------------------------------
# Agent / LLM provider — Databricks Foundation Model API
# ---------------------------------------------------------------------------
# Runs entirely on Databricks-hosted, pay-per-token foundation models -- no
# external provider, no external API key, no credit card. The same model
# class family (databricks-sdk's WorkspaceClient) that already serves
# EMBEDDING_MODEL below also serves chat/tool-calling; agent/llm.py wraps
# both through one OpenAI-compatible client obtained from
# WorkspaceClient().serving_endpoints.get_open_ai_client().
#
# Pick a Foundation Model API pay-per-token endpoint that supports tool
# calling. As of Phase 2, this repo uses Llama 3.3 70B; swap
# FOUNDATION_MODEL_CHAT if your workspace's Free Edition region offers a
# different pay-per-token chat model.
FOUNDATION_MODEL_CHAT = "databricks-meta-llama-3-3-70b-instruct"

# Retrieval / chunking
CHUNK_TOKENS_TARGET = 500
CHUNK_TOKENS_OVERLAP = 50
RETRIEVAL_TOP_K = 5

# Demo-facing latency target (strategy doc section 16)
LATENCY_TARGET_SECONDS = 8
