"""Run logging into civicpulse.ops.ingestion_log — every job writes one row per run."""

from __future__ import annotations

import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone

from config.settings import INGESTION_LOG


@contextmanager
def log_run(spark, job_name: str, source_table: str = "", target_table: str = ""):
    """
    Usage:
        with log_run(spark, "ingest_bills", target_table=BRONZE_BILLS) as run:
            ...
            run["rows_in"] = 1507
            run["rows_out"] = 1507
    """
    run_id = str(uuid.uuid4())
    started_at = datetime.now(timezone.utc)
    state = {"rows_in": 0, "rows_out": 0}
    status, error_message = "success", None

    try:
        yield state
    except Exception as exc:  # noqa: BLE001 - we want to log *any* failure, then re-raise
        status, error_message = "failed", str(exc)
        raise
    finally:
        finished_at = datetime.now(timezone.utc)
        row = [
            (
                run_id,
                job_name,
                source_table,
                target_table,
                state["rows_in"],
                state["rows_out"],
                status,
                error_message,
                started_at,
                finished_at,
            )
        ]
        columns = [
            "run_id", "job_name", "source_table", "target_table",
            "rows_in", "rows_out", "status", "error_message",
            "started_at", "finished_at",
        ]
        spark.createDataFrame(row, columns).write.mode("append").saveAsTable(INGESTION_LOG)


def new_run_id() -> str:
    return str(uuid.uuid4())


def now_ts() -> float:
    return time.time()
