"""
CivicPulse — Silver/Gold -> embeddings -> civicpulse.gold.gold_bill_chunks

Populates the single vector-enabled table that the one allowed AI Search
index (civicpulse.gold.civicpulse_gold_bill_chunks_index, per Phase 1) syncs
from via Change Data Feed. Two chunk sources feed the same table, tagged by
`parent_type`, so bills and agendas share one combined index — this is what
keeps CivicPulse inside the Free Edition one-endpoint/one-unit limit
(architecture doc section 4).

Runs incrementally (strategy doc section 14: "chunk-and-embed incrementally,
not one giant backfill") — only chunk_ids not already present in
gold_bill_chunks are embedded on each run.

Also (re)builds gold_bill_summary: one cached plain-language summary per
bill, generated once via the agent's LLM and only regenerated if full_text
changed since last_refreshed.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone

sys.path.append("../")
from pyspark.sql import functions as F

from agent.llm import embed_texts, generate_summary
from config.settings import (
    EMBEDDING_MODEL,
    GOLD_BILL_CHUNKS,
    GOLD_BILL_SUMMARY,
    SILVER_AGENDA_CHUNKS,
    SILVER_BILLS,
)
from jobs.common.logging_utils import log_run
from jobs.common.spark_session import get_spark
from jobs.common.text_chunking import chunk_text


def _table_exists(spark, table: str) -> bool:
    try:
        spark.table(table)
        return True
    except Exception:
        return False


def embed_bill_chunks(spark) -> int:
    """Chunk each bill's full_text and embed any chunk_id not already in Gold."""
    bills = spark.table(SILVER_BILLS).select("bill_id", "state", "topics", "full_text").collect()

    existing_ids: set[str] = set()
    if _table_exists(spark, GOLD_BILL_CHUNKS):
        existing_ids = {r["chunk_id"] for r in spark.table(GOLD_BILL_CHUNKS).select("chunk_id").collect()}

    new_rows = []
    created_at = datetime.now(timezone.utc)
    for bill in bills:
        for idx, chunk in enumerate(chunk_text(bill["full_text"])):
            chunk_id = f"bill::{bill['bill_id']}::{idx}"
            if chunk_id in existing_ids:
                continue
            new_rows.append({
                "chunk_id": chunk_id,
                "parent_id": bill["bill_id"],
                "parent_type": "bill",
                "chunk_text": chunk,
                "state": bill["state"],
                "topics": bill["topics"],
            })

    if not new_rows:
        return 0

    embeddings = embed_texts([r["chunk_text"] for r in new_rows], model=EMBEDDING_MODEL)
    for row, vec in zip(new_rows, embeddings):
        row["embedding"] = vec
        row["created_at"] = created_at

    df = spark.createDataFrame(new_rows)
    df.write.format("delta").mode("append").saveAsTable(GOLD_BILL_CHUNKS)
    return len(new_rows)


def embed_agenda_chunks(spark) -> int:
    """Agenda chunks are already pre-chunked in Silver — embed any not yet in Gold."""
    if not _table_exists(spark, SILVER_AGENDA_CHUNKS):
        return 0

    agenda_chunks = spark.table(SILVER_AGENDA_CHUNKS).collect()
    existing_ids: set[str] = set()
    if _table_exists(spark, GOLD_BILL_CHUNKS):
        existing_ids = {r["chunk_id"] for r in spark.table(GOLD_BILL_CHUNKS).select("chunk_id").collect()}

    new_rows = []
    created_at = datetime.now(timezone.utc)
    for row in agenda_chunks:
        chunk_id = f"agenda::{row['chunk_id']}"
        if chunk_id in existing_ids:
            continue
        new_rows.append({
            "chunk_id": chunk_id,
            "parent_id": row["chunk_id"],
            "parent_type": "agenda",
            "chunk_text": row["chunk_text"],
            "state": None,
            "topics": [],
        })

    if not new_rows:
        return 0

    embeddings = embed_texts([r["chunk_text"] for r in new_rows], model=EMBEDDING_MODEL)
    for row, vec in zip(new_rows, embeddings):
        row["embedding"] = vec
        row["created_at"] = created_at

    df = spark.createDataFrame(new_rows)
    df.write.format("delta").mode("append").saveAsTable(GOLD_BILL_CHUNKS)
    return len(new_rows)


def refresh_bill_summaries(spark) -> int:
    """Generate (once) or refresh (if full_text changed) each bill's cached plain-language summary."""
    bills = spark.table(SILVER_BILLS).collect()

    cached: dict[str, str] = {}
    if _table_exists(spark, GOLD_BILL_SUMMARY):
        cached = {r["bill_id"]: r["plain_summary"] for r in spark.table(GOLD_BILL_SUMMARY).collect()}

    rows = []
    refreshed_at = datetime.now(timezone.utc)
    for bill in bills:
        summary = cached.get(bill["bill_id"]) or generate_summary(bill["title"], bill["full_text"])
        rows.append((
            bill["bill_id"], bill["state"], bill["title"], summary,
            bill["status"], bill["topics"], bill["next_hearing_date"], refreshed_at,
        ))

    columns = ["bill_id", "state", "title", "plain_summary", "status", "topics", "next_hearing_date", "last_refreshed"]
    if rows:
        df = spark.createDataFrame(rows, columns)
        df.write.format("delta").mode("overwrite").saveAsTable(GOLD_BILL_SUMMARY)
    return len(rows)


def run() -> None:
    spark = get_spark()
    with log_run(spark, "embed_chunks", target_table=GOLD_BILL_CHUNKS) as stats:
        bill_chunk_count = embed_bill_chunks(spark)
        agenda_chunk_count = embed_agenda_chunks(spark)
        summary_count = refresh_bill_summaries(spark)
        stats["rows_in"] = bill_chunk_count + agenda_chunk_count
        stats["rows_out"] = bill_chunk_count + agenda_chunk_count
        print(
            f"embed_chunks: +{bill_chunk_count} bill chunks, +{agenda_chunk_count} agenda chunks, "
            f"{summary_count} summaries refreshed/cached"
        )
        # NOTE: with delta.enableChangeDataFeed=true on gold_bill_chunks, a TRIGGERED
        # sync of the AI Search index (civicpulse-endpoint) should be kicked off after
        # this job — see resources/jobs.yml for the pipeline task ordering.


if __name__ == "__main__":
    run()
