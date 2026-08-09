"""
CivicPulse — Bronze -> Silver for council agendas.

Splits each agenda's raw extracted text into agenda-item-scoped chunks.
Agenda packets are irregular by nature (strategy doc section 1: "the
unstructured data is genuinely irregular") — item boundaries are detected
with a permissive heading regex tuned for common Legistar-style numbering
("ITEM 4.", "4.", "Agenda Item 4:") rather than assuming a single clean
format.
"""

from __future__ import annotations

import re
import sys
import uuid
from datetime import datetime, timezone

sys.path.append("../")
from config.settings import BRONZE_AGENDAS, CHUNK_TOKENS_OVERLAP, CHUNK_TOKENS_TARGET, SILVER_AGENDA_CHUNKS
from jobs.common.logging_utils import log_run
from jobs.common.spark_session import get_spark
from jobs.common.text_chunking import chunk_text

ITEM_HEADING_RE = re.compile(
    r"(?im)^\s*(?:item\s*)?(\d{1,3})[.):]\s*(.+)$"
)


def split_into_items(raw_text: str) -> list[tuple[str, str]]:
    """
    Return [(item_title, item_body), ...]. Falls back to a single
    'Full Document' pseudo-item if no headings are detected, so unusually
    formatted agendas still get chunked rather than dropped.
    """
    matches = list(ITEM_HEADING_RE.finditer(raw_text or ""))
    if not matches:
        return [("Full Document", raw_text or "")]

    items = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw_text)
        title = match.group(2).strip()[:200]
        body = raw_text[start:end].strip()
        items.append((title, body))
    return items


def run() -> None:
    spark = get_spark()
    with log_run(spark, "transform_agendas", source_table=BRONZE_AGENDAS, target_table=SILVER_AGENDA_CHUNKS) as stats:
        bronze_rows = spark.table(BRONZE_AGENDAS).collect()
        stats["rows_in"] = len(bronze_rows)

        out_rows = []
        created_at = datetime.now(timezone.utc)
        for row in bronze_rows:
            for item_title, item_body in split_into_items(row["raw_text"]):
                for idx, chunk in enumerate(
                    chunk_text(item_body, CHUNK_TOKENS_TARGET, CHUNK_TOKENS_OVERLAP)
                ):
                    out_rows.append((
                        str(uuid.uuid4()),
                        row["city"],
                        row["meeting_date"],
                        item_title,
                        chunk,
                        idx,
                        row["ingestion_id"],
                        created_at,
                    ))

        columns = [
            "chunk_id", "city", "meeting_date", "agenda_item_title",
            "chunk_text", "chunk_index", "source_bronze_id", "created_at",
        ]
        if out_rows:
            df = spark.createDataFrame(out_rows, columns)
            df.write.format("delta").mode("overwrite").saveAsTable(SILVER_AGENDA_CHUNKS)
        stats["rows_out"] = len(out_rows)
        print(f"transform_agendas: {len(bronze_rows)} agendas -> {len(out_rows)} chunks")


if __name__ == "__main__":
    run()
