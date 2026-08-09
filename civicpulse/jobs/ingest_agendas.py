"""
CivicPulse — Bronze ingestion: city council agenda/minutes PDFs -> civicpulse.bronze.bronze_agendas

Unlike bills, there is no bulk-data source for local council agendas (strategy
doc section 15) — this job reads whatever PDFs have been staged (manually
downloaded, or scraped by a separate, out-of-scope process) under
`{RAW_FILES_VOLUME}/agendas/{city}/` and lands their extracted text into
Bronze, unclean, exactly as extracted. transform_agendas.py does the
cleaning/chunking.

Scoped to a single demo city per the strategy doc's scope-creep mitigation
(section 18) — expand DEMO_CITY / add more city folders once the pipeline is
proven on one clean, digitally-native agenda source.
"""

from __future__ import annotations

import sys
import uuid
from datetime import datetime, timezone
from pathlib import PurePosixPath

sys.path.append("../")
from config.settings import BRONZE_AGENDAS, RAW_FILES_VOLUME
from jobs.common.logging_utils import log_run
from jobs.common.spark_session import get_spark


def extract_pdf_text(path: str) -> str:
    """
    Extract raw text from a single agenda PDF. Uses pdfplumber, which handles
    the mildly irregular multi-column layouts common in Legistar-style agenda
    packets better than a naive PyPDF text dump. Scanned (image-only) PDFs
    are out of scope for the MVP (strategy doc: "keep OCR as stretch only").
    """
    import pdfplumber

    text_parts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text_parts.append(page.extract_text() or "")
    return "\n".join(text_parts)


def discover_pdfs(dbutils, city: str) -> list[str]:
    city_dir = f"{RAW_FILES_VOLUME}/agendas/{city}/"
    try:
        return [f.path for f in dbutils.fs.ls(city_dir) if f.path.lower().endswith(".pdf")]
    except Exception:
        return []


def parse_meeting_date(file_name: str):
    """Best-effort YYYY-MM-DD extraction from a conventionally-named agenda file."""
    import re

    match = re.search(r"(\d{4}-\d{2}-\d{2})", file_name)
    return match.group(1) if match else None


def run(city: str) -> None:
    spark = get_spark()
    try:
        dbutils  # noqa: B018
    except NameError as exc:
        raise RuntimeError("ingest_agendas requires dbutils (run inside Databricks).") from exc

    columns = [
        "ingestion_id", "city", "meeting_date", "file_name",
        "raw_bytes_path", "raw_text", "ingested_at", "source",
    ]

    with log_run(spark, "ingest_agendas", target_table=BRONZE_AGENDAS) as run_stats:
        pdf_paths = discover_pdfs(dbutils, city)  # type: ignore[name-defined]
        run_stats["rows_in"] = len(pdf_paths)

        rows = []
        ingested_at = datetime.now(timezone.utc)
        for path in pdf_paths:
            file_name = PurePosixPath(path).name
            raw_text = extract_pdf_text(path)
            rows.append(
                (
                    str(uuid.uuid4()),
                    city,
                    parse_meeting_date(file_name),
                    file_name,
                    path,
                    raw_text,
                    ingested_at,
                    "manual_upload",
                )
            )

        if rows:
            df = spark.createDataFrame(rows, columns)
            df.write.mode("append").saveAsTable(BRONZE_AGENDAS)
        run_stats["rows_out"] = len(rows)
        print(f"ingest_agendas: wrote {len(rows)} rows to {BRONZE_AGENDAS}")


if __name__ == "__main__":
    from config.settings import DEMO_CITY

    run(city=DEMO_CITY)
