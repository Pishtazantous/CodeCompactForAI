---
id: 02-data-pipeline-anti-slop
title: "Data Pipeline Anti-Slop Layer"
lang: en
depends_on: ["_universal/00-style-guide.md", "_universal/00-master-anti-slop.md"]
category: domain
domain_type: delivery
version: 2
---

# Data Pipeline Anti-Slop Layer

This file defines behavioral contracts specific to data pipelines. It sits in the delivery layer, below the universal anti-slop rules and above ML pipeline or database schema patterns. It covers ETL and ELT, idempotency, backfills, schema evolution, late-arriving data, DAG design, data quality, and the discipline of treating data as a production asset. It does not cover database schema design (see `02-database-anti-slop.md`) or ML pipeline rules (see `02-ml-system-anti-slop.md`).

Data is a production asset. Every pipeline run is a contract with downstream consumers.

## Scope

This file applies to pipelines built with Apache Airflow, Dagster, Prefect, dbt, Apache Spark, Flink, Beam, Kafka Streams, Kafka Connect, AWS Glue, Google Dataflow, Azure Data Factory, and custom orchestrators (cron + a script). The principles are tool-agnostic. The examples use SQL and Bash syntax where illustrative.

## Rule Severity

Severity follows `_universal/00-style-guide.md`.

## Contracts

A data pipeline commits to seven contracts. The table below maps each contract to the rules that enforce it.

| Contract | Description | Enforced By |
|---|---|---|
| Idempotency | Re-running a pipeline on the same input produces the same output. | DP-001 to DP-005 |
| Backfill Safety | Backfills are first-class operations with rate limiting and idempotency. | DP-006 to DP-010 |
| Schema Stability | Schema changes are additive, versioned, and announced. | DP-011 to DP-015 |
| Late Data Handling | Watermarks, windows, and event timestamps handle out-of-order data. | DP-016 to DP-019 |
| DAG Discipline | Tasks are single-purpose, idempotent, and have retries and timeouts. | DP-020 to DP-027 |
| Data Quality | Data is validated at boundaries, quarantined on failure, and monitored. | DP-028 to DP-032 |
| Storage and Cost | Columnar formats, partitioning, retention, and cost monitoring are enforced. | DP-033 to DP-037 |

## Idempotency

### DP-001 — Idempotent Execution

**MUST**

A pipeline run MUST produce the same output when run twice on the same input. This is the single most important property of a data pipeline. Non-idempotent pipelines double-count rows, send duplicate emails, and produce silent corruption.

See MAS-037 in `_universal/00-master-anti-slop.md`.

### DP-002 — Upsert Over Insert

**MUST**

Idempotent write patterns MUST be used. Plain `INSERT` statements that fail on re-run are prohibited. Use upserts or delete-then-insert on partitions.

Example (illustrative, SQL):

BAD:
```sql
INSERT INTO daily_metrics (date, value) VALUES (...);
```

GOOD:
```sql
INSERT ... ON CONFLICT (date) DO UPDATE SET value = EXCLUDED.value;
```

Or delete the partition before writing:
```sql
DELETE FROM daily_metrics WHERE date = '2025-01-15';
INSERT INTO daily_metrics ...;
```

### DP-003 — Partitioned Writes

**MUST**

Writes MUST target a partition that matches the pipeline's logical unit (a day, an hour, a batch). Re-running MUST replace the partition atomically.

### DP-004 — Deterministic Ordering

**MUST**

If the pipeline processes events, ordering MUST be deterministic. Parallel processing that produces different output on different runs is not idempotent and MUST NOT be used.

### DP-005 — Side Effect Marker

**MUST**

External side effects (email sends, webhooks, file uploads) MUST happen once per logical run. A state table MUST track them to prevent duplicates.

Example (illustrative, SQL):
```sql
INSERT INTO sent_notifications (run_id, user_id)
VALUES (...) ON CONFLICT DO NOTHING;
```

## Backfills

### DP-006 — Backfill as First-Class Operation

**MUST**

A backfill MUST be treated as a separate operation with its own tooling, rate limit, and audit. It MUST NOT be "run the pipeline with a different date".

### DP-007 — Documented Backfill Command

**MUST**

Every pipeline MUST have a documented way to backfill a range.

Example (illustrative, Bash):
```bash
pipeline backfill --from 2025-01-01 --to 2025-01-31 --job daily_metrics
```

### DP-008 — Backfill Rate Limiting

**MUST**

A backfill for a large range (e.g., a year of data) can saturate the source database, the target warehouse, and the network. It MUST be rate-limited.

See MAS-040 in `_universal/00-master-anti-slop.md`.

### DP-009 — Backfill Overwrite Documentation

**MUST**

If the source has changed since the original run, the backfill produces different results. Whether the backfill is intended to overwrite MUST be explicitly documented.

### DP-010 — Backfill Idempotency

**MUST**

The backfill MUST use the same idempotent write path as the regular run. A separate, ad-hoc code path that bypasses the partition-replace logic is prohibited.

## Schema Evolution

### DP-011 — Additive Schema Changes

**MUST**

Schema changes MUST be additive. Renaming or removing a column breaks every consumer. Add the new column, migrate consumers, then remove the old one in a later release.

### DP-012 — Nullable New Columns

**MUST**

A new column MUST be added as nullable. A new column with `NOT NULL` and no default breaks existing writers. Add as nullable, backfill, then enforce.

### DP-013 — Versioned Stream Schemas

**MUST**

A Kafka topic or a similar stream MUST have a versioned schema (Avro, Protobuf, JSON Schema) registered in a schema registry. Consumers MUST negotiate the version.

### DP-014 — Breaking Change Announcement

**MUST**

A schema change that breaks consumers MUST be announced in advance, with a migration window.

### DP-015 — No Silent Type Changes

**MUST NOT**

Changing a column type (e.g., `int` to `string`) MUST NOT occur silently. Even if the database accepts it, every consumer breaks.

## Late and Out-of-Order Data

### DP-016 — Watermark Definition

**MUST**

A streaming pipeline MUST define a watermark: how late data may arrive. Data after the watermark MUST be dropped or routed to a dead-letter queue.

### DP-017 — Windowed Aggregation Discipline

**MUST**

A windowed aggregation (hourly, daily) MUST wait until the watermark passes before emitting the final result. Late data within the window is incorporated; later data is not.

### DP-018 — Idempotent Late Arrival

**MUST**

A late event MUST re-process the affected window. The window's output MUST be recomputed, not added to.

### DP-019 — Event Timestamp Usage

**MUST**

Events MUST be assumed to arrive out of order. An event timestamp MUST be included in every message. Arrival time MUST NOT be used for ordering.

## DAG Design

### DP-020 — Single Purpose Task

**MUST**

A task MUST do one thing. Extract, transform, and load MUST be three tasks.

### DP-021 — Task Idempotency

**MUST**

Each task MUST be safe to retry. See DP-001 for idempotency requirements.

### DP-022 — Task Independence

**SHOULD**

Parallel branches SHOULD run concurrently where possible. Sequential dependencies MUST be explicit.

### DP-023 — No Cross-DAG Imports

**MUST NOT**

A DAG MUST NOT import from another DAG. Shared logic MUST go in a library module.

See MAS-035 in `_universal/00-master-anti-slop.md`.

### DP-024 — Retry with Backoff

**MUST**

A task MUST have a retry policy with backoff (e.g., `retries=3`, `retry_delay=timedelta(minutes=5)`, `exponential_backoff=True`). Retries without delay are prohibited.

### DP-025 — Failure Alerts

**MUST**

A task failure MUST alert the on-call. A DAG that fails silently is worse than one that crashes loudly.

See MAS-037 in `_universal/00-master-anti-slop.md`.

### DP-026 — Task Timeouts

**MUST**

Every task MUST have a timeout. A task that hangs forever blocks the DAG.

See MAS-040 in `_universal/00-master-anti-slop.md`.

### DP-027 — Backfill Scheduler Separation

**MUST NOT**

Backfills MUST NOT run in the regular scheduler. They MUST be run manually or via a separate scheduler and MUST NOT compete with the regular schedule for worker slots.

## Data Quality

### DP-028 — Boundary Validation

**MUST**

Data entering the pipeline MUST be validated:

- Schema (types, nullability, required fields).
- Range (numbers within bounds).
- Referential integrity (foreign keys exist).
- Business rules (status values are in the allowed set).

### DP-029 — Bad Data Quarantine

**MUST**

A malformed record MUST go to a dead-letter queue; the pipeline MUST continue. A malformed record crashing the pipeline is prohibited.

### DP-030 — Data Quality Metrics

**MUST**

The following MUST be tracked and alerted when deviating from baseline:

- Row counts per run.
- Null rates per column.
- Distinct value counts for categorical columns.
- Freshness (time since last update).

### DP-031 — No Silent Data Loss

**MUST NOT**

A filter that drops rows (e.g., 5%) is a decision. It MUST be logged and alerted on changes to the drop rate. Silent data loss is prohibited.

### DP-032 — In-Pipeline Tests

**MUST**

A pipeline MUST include tests:

- Uniqueness of primary keys.
- Foreign key integrity.
- Expected ranges.
- No unexpected nulls.

Use dbt tests, Great Expectations, or a custom framework.

## Storage and Cost

### DP-033 — Columnar Format Usage

**MUST**

Analytical data MUST be stored in columnar formats (Parquet, ORC, or Avro). CSV is a transfer format, not a storage format.

### DP-034 — Partitioning Strategy

**MUST**

Data MUST be partitioned by the column most used in filters (usually date). Over-partitioning (e.g., by hour on a small dataset) produces small files and slow queries and MUST NOT be used.

### DP-035 — File Compaction

**SHOULD**

Small files slow down queries. A compaction job SHOULD periodically merge them.

### DP-036 — Data Retention Policy

**MUST**

Old data MUST be deleted per policy. A pipeline that writes 10 TB a month and never deletes anything is a growing cost.

### DP-037 — Cost Monitoring

**MUST**

Query cost on cloud warehouses (BigQuery, Snowflake, Redshift) is driven by bytes scanned. It MUST be monitored. A query that scans 1 TB MUST be a decision, not an accident.

## AI-Specific Data Pipeline Discipline

### DP-060 — Schema Verification Before Query

**MUST**

Before writing any pipeline query or transformation, the assistant MUST verify that the referenced tables, columns, and partitions exist in the project's schema definitions or catalog. Invented column names produce runtime failures that are invisible at development time.

See MAS-036 in `_universal/00-master-anti-slop.md`.

### DP-061 — Existing Pipeline Discovery

**MUST**

Before creating a new pipeline task or DAG, the assistant MUST search the project for an existing equivalent. Inventing parallel pipelines for the same data creates divergent datasets and maintenance burden.

See MAS-035 in `_universal/00-master-anti-slop.md`.

### DP-062 — Pipeline Complexity Restraint

**SHOULD**

The assistant SHOULD NOT introduce complex orchestration patterns (multi-level DAG dependencies, custom schedulers, exotic frameworks) unless the project already uses them and the scale explicitly requires them.

See MAS-038 in `_universal/00-master-anti-slop.md`.

## Anti-Patterns

### DP-040 — Time-Based Table Names

**MUST NOT**

Time-based table names (e.g., `events_2025_01_15_14_30`) are prohibited. Every run creates a new table and consumers do not know which to read. One table partitioned by `event_date` MUST be used.

### DP-041 — Silent Failure Anti-Pattern

**MUST NOT**

A try/except that logs and continues is prohibited. A dead-letter queue with an alert MUST be used.

See MAS-037 in `_universal/00-master-anti-slop.md`.

### DP-042 — Hard-Coded Dates

**MUST NOT**

Hard-coded dates in a scheduled DAG (e.g., `WHERE date = '2025-01-15'`) are prohibited. Templated dates (e.g., `{{ ds }}` in Airflow) MUST be used.

### DP-043 — Retry Without Backoff

**MUST NOT**

A task that fails due to a transient issue and retries in a tight loop overwhelms the source. Retries MUST have backoff. See DP-024.

### DP-044 — Cross-Environment Data Leakage

**MUST NOT**

A staging pipeline reading from production without a filter is prohibited. Environment-scoped credentials and explicit data subsets MUST be used.

### DP-045 — Lineage Requirement

**MUST**

Column-level lineage (dbt, OpenLineage) MUST be maintained. Nobody MUST be left unaware of which pipeline produced a table or which tables depend on it.

### DP-046 — Pipeline Documentation

**MUST**

A pipeline MUST have a README, an owner, and an SLA. When it fails at 3 AM, someone MUST know what to do.

### DP-047 — Unbounded Parallelism

**MUST NOT**

A pipeline that launches thousands of concurrent tasks is prohibited. A pool with a concurrency limit MUST be used.

See MAS-040 in `_universal/00-master-anti-slop.md`.

### DP-048 — Partition Pruning Prevention

**MUST NOT**

Queries that prevent partition pruning (e.g., `WHERE YEAR(event_time) = 2025`) are prohibited. Direct partition column filters MUST be used (e.g., `WHERE event_date >= '2025-01-01' AND event_date < '2026-01-01'`).

### DP-049 — Timezone Confusion

**MUST NOT**

Mixing UTC and local time, storing naive datetimes, or using `WHERE date = ...` that produces different results depending on the server's timezone is prohibited. All timestamps MUST be UTC and timezone-aware.

### DP-050 — Scheduler Replay Backfill

**MUST NOT**

Running the scheduler for a past date does not equal a backfill. The scheduler has current code, current resources, and current side effects. The dedicated backfill path MUST be used.

### DP-051 — Data Contracts

**MUST**

A producer MUST NOT change its schema without notifying consumers. Data contracts (a registry, a version, a documented interface) MUST be used to prevent 2 AM breakages.

### DP-052 — Overwrite Without Snapshot

**MUST NOT**

A backfill or a re-run overwriting historical data with no way to compare is prohibited. A snapshot of the previous state MUST be kept.

### DP-053 — PII Control

**MUST NOT**

A pipeline copying PII into an analytics warehouse without masking is prohibited. Tokenization or masking at the boundary MUST be used; PII MUST stay in the source system.

### DP-054 — Production Testing Prohibition

**MUST NOT**

A new transformation tested only against the production dataset is prohibited. A sampled dataset in staging, with representative edge cases, MUST be used.

### DP-055 — Transformation Version Control

**MUST**

SQL MUST be in Git and deployed via the pipeline. SQL edited directly in the warehouse UI is prohibited.

### DP-056 — Cron-Only Scheduling

**MUST NOT**

A cron job with no visibility, no retries, and no alerting is prohibited. If it fails, nobody notices until the data is stale. An orchestrator MUST be used.

## Response to Violation

When a rule in this file is violated, report:

Violation: DP-{NNN}
Reason: {one-line reason}
Correction: {smallest fix}

For multiple violations, report each rule ID separately.

Do not replace a technical correction with a generic explanation.