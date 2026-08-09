"""
CivicPulse — Bronze ingestion: Open States bills -> civicpulse.bronze.bronze_bills

Two data paths, matching the Free Edition risk mitigation in the strategy doc
(section 14/18 — "restricted outbound internet"):

  1. LIVE API  — pulls updated bills for TARGET_STATES via the Open States v3
     API. Used when outbound HTTPS to openstates.org is reachable from the
     workspace.
  2. BULK DUMP — reads the pre-downloaded Alabama 2026rs JSON dump staged in
     Phase 1 at config.settings.ALABAMA_BULK_DUMP_PATH. Used as the
     guaranteed-to-work fallback (and what the demo build defaults to).

Both paths land raw, untouched JSON into Bronze — no parsing/typing happens
here. That's transform_bills.py's job. Bronze is append-only and idempotent
per ingestion_id, so re-running this job is always safe.
"""

from __future__ import annotations

import json
import sys
import uuid
from datetime import datetime, timezone

import requests

sys.path.append("../")  # allow `config` import when run as a Databricks notebook/job
from config.settings import (
    ALABAMA_BULK_DUMP_PATH,
    BRONZE_BILLS,
    OPENSTATES_API_KEY_SECRET,
    SECRET_SCOPE,
    TARGET_SESSION,
    TARGET_STATES,
)
from jobs.common.logging_utils import log_run
from jobs.common.spark_session import get_spark

OPENSTATES_BASE_URL = "https://v3.openstates.org"


def _get_api_key(dbutils) -> str:
    return dbutils.secrets.get(scope=SECRET_SCOPE, key=OPENSTATES_API_KEY_SECRET)


def fetch_live(state: str, session: str, api_key: str, per_page: int = 20) -> list[dict]:
    """Pull bills updated in the last run window for one state/session via the live API."""
    bills, page = [], 1
    headers = {"X-API-KEY": api_key}
    while True:
        resp = requests.get(
            f"{OPENSTATES_BASE_URL}/bills",
            headers=headers,
            params={"jurisdiction": state, "session": session, "page": page, "per_page": per_page},
            timeout=30,
        )
        resp.raise_for_status()
        payload = resp.json()
        bills.extend(payload.get("results", []))
        if page >= payload.get("pagination", {}).get("max_page", 1):
            break
        page += 1
    return bills


def load_bulk_dump(spark, path: str) -> list[dict]:
    """Read the staged bulk-data JSON dump (Phase 1: Alabama 2026rs, 1,507 bills)."""
    raw = spark.read.text(path, wholetext=True).collect()[0][0]
    data = json.loads(raw)
    # Open States bulk exports are typically {"bills": [...]}; be forgiving of a bare list too.
    return data["bills"] if isinstance(data, dict) and "bills" in data else data


def to_bronze_rows(bills: list[dict], state: str, session: str, source: str) -> list[tuple]:
    ingested_at = datetime.now(timezone.utc)
    rows = []
    for bill in bills:
        rows.append(
            (
                str(uuid.uuid4()),                     # ingestion_id
                bill.get("id", bill.get("identifier", "")),  # source_bill_id
                state,
                session,
                json.dumps(bill),                        # raw_json, untouched
                ingested_at,
                source,
            )
        )
    return rows


def run(use_bulk_fallback: bool = True) -> None:
    spark = get_spark()
    columns = [
        "ingestion_id", "source_bill_id", "state", "session",
        "raw_json", "ingested_at", "source",
    ]

    with log_run(spark, "ingest_bills", target_table=BRONZE_BILLS) as run_stats:
        all_rows: list[tuple] = []

        if use_bulk_fallback:
            for state in TARGET_STATES:
                bills = load_bulk_dump(spark, ALABAMA_BULK_DUMP_PATH)
                all_rows.extend(
                    to_bronze_rows(bills, state, TARGET_SESSION, source="openstates_bulk_dump")
                )
        else:
            try:
                dbutils  # noqa: B018 - only defined inside Databricks notebooks
            except NameError as exc:
                raise RuntimeError("Live API path requires dbutils (run inside Databricks).") from exc
            api_key = _get_api_key(dbutils)  # type: ignore[name-defined]
            for state in TARGET_STATES:
                bills = fetch_live(state, TARGET_SESSION, api_key)
                all_rows.extend(to_bronze_rows(bills, state, TARGET_SESSION, source="openstates_api"))

        run_stats["rows_in"] = len(all_rows)
        if all_rows:
            df = spark.createDataFrame(all_rows, columns)
            df.write.mode("append").saveAsTable(BRONZE_BILLS)
        run_stats["rows_out"] = len(all_rows)
        print(f"ingest_bills: wrote {len(all_rows)} rows to {BRONZE_BILLS}")


if __name__ == "__main__":
    run(use_bulk_fallback=True)
