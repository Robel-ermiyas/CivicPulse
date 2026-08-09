"""
CivicPulse — Bronze -> Silver -> Gold for bills.

Known gap flagged in Phase 1 (docs/phase1-setup-summary.md section 4): the
Open States bulk export has no direct `status` field — status must be
*derived* from `actions[].classification`, the chronological action log each
bill carries. The derivation itself lives in jobs/common/bill_status.py (pure
Python, no Spark dependency) so it can be unit-tested without a Spark
session; this module just wires it up as Spark UDFs.

Bronze -> Silver:
  - parse raw_json, normalize into typed columns
  - derive status from actions[]
  - derive next_hearing_date from any action classified 'committee-referral'/
    'reading-2' etc. with a future date (bulk exports vary; kept permissive)
  - tag topics via keyword matching against a small curated topic lexicon
    (cheap, deterministic, good enough for MVP scope; swap for embedding-
    cluster tagging in the stretch phase per the strategy doc)

Silver -> Gold:
  - gold_bill_summary: one row per bill, plain-language summary generated
    once by the agent's LLM and cached (never regenerated unless the bill's
    full_text changes)
  - gold_vote_history: bills that have reached a terminal outcome (passed/
    failed), the structured input to the `get_vote_history` tool
"""

from __future__ import annotations

import sys

sys.path.append("../")
from pyspark.sql import functions as F
from pyspark.sql import types as T

from config.settings import (
    BRONZE_BILLS,
    GOLD_BILL_SUMMARY,
    GOLD_VOTE_HISTORY,
    SILVER_BILLS,
)
from jobs.common.bill_status import derive_next_hearing_date, derive_status, tag_topics
from jobs.common.logging_utils import log_run
from jobs.common.spark_session import get_spark

# Register as Spark UDFs for use inside the DataFrame pipeline.
_derive_status_udf = F.udf(lambda actions: derive_status(actions or []), T.StringType())
_derive_hearing_udf = F.udf(lambda actions: derive_next_hearing_date(actions or []), T.StringType())
_tag_topics_udf = F.udf(lambda text: tag_topics(text), T.ArrayType(T.StringType()))


def bronze_to_silver(spark) -> int:
    bronze = spark.table(BRONZE_BILLS)

    schema = T.StructType([
        T.StructField("id", T.StringType()),
        T.StructField("identifier", T.StringType()),
        T.StructField("title", T.StringType()),
        T.StructField("classification", T.ArrayType(T.StringType())),
        T.StructField("session", T.StringType()),
        T.StructField("sponsorships", T.ArrayType(
            T.StructType([T.StructField("name", T.StringType())])
        )),
        T.StructField("actions", T.ArrayType(
            T.StructType([
                T.StructField("date", T.StringType()),
                T.StructField("classification", T.ArrayType(T.StringType())),
            ])
        )),
        T.StructField("abstracts", T.ArrayType(
            T.StructType([T.StructField("abstract", T.StringType())])
        )),
    ])

    parsed = bronze.withColumn("bill", F.from_json(F.col("raw_json"), schema))

    silver = (
        parsed
        .withColumn("bill_id", F.coalesce(F.col("bill.identifier"), F.col("bill.id"), F.col("source_bill_id")))
        .withColumn("title", F.col("bill.title"))
        .withColumn("status", _derive_status_udf(F.col("bill.actions")))
        .withColumn("sponsor", F.col("bill.sponsorships")[0]["name"])
        .withColumn(
            "full_text",
            F.concat_ws(
                " ",
                F.col("title"),
                F.concat_ws(" ", F.transform(F.coalesce(F.col("bill.abstracts"), F.array()), lambda a: a["abstract"])),
            ),
        )
        .withColumn("topics", _tag_topics_udf(F.col("full_text")))
        .withColumn("last_action_date", F.to_date(F.array_max(
            F.transform(F.coalesce(F.col("bill.actions"), F.array()), lambda a: a["date"])
        )))
        .withColumn("next_hearing_date", F.to_date(_derive_hearing_udf(F.col("bill.actions"))))
        .withColumn("updated_at", F.current_timestamp())
        .select(
            "bill_id", "state", "session", "title", "status", "sponsor",
            "topics", "last_action_date", "next_hearing_date", "full_text", "updated_at",
        )
        .dropDuplicates(["bill_id"])
    )

    (
        silver.write.format("delta").mode("overwrite")
        .option("mergeSchema", "true")
        .saveAsTable(SILVER_BILLS)
    )
    return silver.count()


def silver_to_gold_vote_history(spark) -> int:
    """Bills with a terminal outcome feed get_vote_history()."""
    silver = spark.table(SILVER_BILLS)
    terminal = (
        silver
        .filter(F.col("status").isin("passed", "failed"))
        .withColumn("topic", F.explode_outer(F.col("topics")))
        .select(
            "bill_id", "state", "topic",
            F.col("status").alias("outcome"),
            F.col("last_action_date").alias("vote_date"),
            F.lit(None).cast("string").alias("vote_margin"),  # not present in bulk export; stretch enrichment
        )
    )
    terminal.write.format("delta").mode("overwrite").saveAsTable(GOLD_VOTE_HISTORY)
    return terminal.count()


def run() -> None:
    spark = get_spark()
    with log_run(spark, "transform_bills", source_table=BRONZE_BILLS, target_table=SILVER_BILLS) as stats:
        stats["rows_in"] = spark.table(BRONZE_BILLS).count()
        stats["rows_out"] = bronze_to_silver(spark)
        vote_rows = silver_to_gold_vote_history(spark)
        print(f"transform_bills: {stats['rows_out']} bills -> silver, {vote_rows} rows -> gold_vote_history")


if __name__ == "__main__":
    run()
