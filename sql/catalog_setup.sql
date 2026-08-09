-- CivicPulse — Catalog & schema bootstrap
-- Free Edition: single catalog, schema-level separation, serverless SQL (Delta by default).

CREATE CATALOG IF NOT EXISTS civicpulse;

CREATE SCHEMA IF NOT EXISTS civicpulse.bronze;
CREATE SCHEMA IF NOT EXISTS civicpulse.silver;
CREATE SCHEMA IF NOT EXISTS civicpulse.gold;
CREATE SCHEMA IF NOT EXISTS civicpulse.ops;

-- Volume for landing raw files (PDFs, bulk-data JSON dumps) before they're parsed into Bronze.
CREATE VOLUME IF NOT EXISTS civicpulse.bronze.raw_files;
