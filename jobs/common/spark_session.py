"""
Shared Spark session helper for all CivicPulse jobs.

On Databricks (notebook or Jobs cluster / serverless job), `spark` is already
injected into the global namespace — get_spark() just returns it. Locally
(unit tests, dev laptop) it falls back to a local SparkSession with Delta
support so the transform logic can be exercised without a workspace.
"""

from __future__ import annotations


def get_spark():
    try:
        # Databricks notebooks/jobs inject `spark` globally.
        return globals()["spark"]  # type: ignore[name-defined]
    except KeyError:
        pass

    try:
        from pyspark.sql import SparkSession

        return (
            SparkSession.builder.appName("civicpulse-local")
            .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
            .config(
                "spark.sql.catalog.spark_catalog",
                "org.apache.spark.sql.delta.catalog.DeltaCatalog",
            )
            .getOrCreate()
        )
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "No Spark session available. Run inside Databricks, or "
            "`pip install pyspark delta-spark` for local development."
        ) from exc
