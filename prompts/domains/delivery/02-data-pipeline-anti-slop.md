---
id: 02-data-pipeline-anti-slop
title: "Data Pipeline Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: delivery
version: 1
---

# Data Pipeline Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
security anti-patterns, output format) are NOT repeated here.

This file covers rules specific to data pipelines: ETL and ELT,
idempotency, backfills, schema evolution, late-arriving data, DAG
design, and the discipline of treating data as a production asset.
Database schema rules live in
`domains/delivery/02-database-anti-slop.md`. ML pipeline rules live in
`domains/delivery/02-ml-system-anti-slop.md`.

## 1. Stack Assumptions

This layer applies to pipelines built with:

- Apache Airflow, Dagster, Prefect
- dbt
- Apache Spark, Flink, Beam
- Kafka Streams, Kafka Connect
- AWS Glue, Google Dataflow, Azure Data Factory
- Custom orchestrators (cron + a script)

The principles are tool-agnostic.

## 2. Idempotency

### 2.1 Re-running Is Safe

A pipeline run that produces the same output when run twice on the
same input. This is the single most important property of a data
pipeline.

Non-idempotent pipelines double-count rows, send duplicate emails,
and produce silent corruption.

### 2.2 Upsert, Do Not Insert

BAD: `INSERT INTO daily_metrics (date, value) VALUES (...)`.
GOOD: `INSERT ... ON CONFLICT (date) DO UPDATE SET value = EXCLUDED.value`.

Or delete the partition before writing:

```sql
DELETE FROM daily_metrics WHERE date = '2025-01-15';
INSERT INTO daily_metrics ...
```

### 2.3 Partitioned Writes

Write to a partition that matches the pipeline's logical unit (a day,
an hour, a batch). Re-running replaces the partition.

### 2.4 Deterministic Ordering

If the pipeline processes events, sort deterministically. Parallel
processing that produces different output on different runs is not
idempotent.

### 2.5 No External Side Effects Without a Marker

An email send, a webhook, or a file upload happens once per logical
run. Track it in a state table:

```sql
INSERT INTO sent_notifications (run_id, user_id)
VALUES (...) ON CONFLICT DO NOTHING;
```

## 3. Backfills

### 3.1 Backfills Are First-Class

A backfill is not "run the pipeline with a different date". It is a
separate operation with its own tooling, its own rate limit, and its
own audit.

### 3.2 Backfill Script

Every pipeline has a documented way to backfill a range:

```bash
pipeline backfill --from 2025-01-01 --to 2025-01-31 --job daily_metrics
```

### 3.3 Backfill Load

A backfill for a year of data can saturate the source database, the
target warehouse, and the network. Rate-limit it.

### 3.4 Backfill Does Not Overwrite Without Reason

A backfill re-processes old data. If the source has changed since the
original run, the backfill produces different results. Document
whether the backfill is intended to overwrite.

### 3.5 Backfill Idempotency

The backfill uses the same idempotent write path as the regular run.
It does not have a separate, ad-hoc code path that bypasses the
partition-replace logic.

## 4. Schema Evolution

### 4.1 Add Columns, Do Not Rename

Renaming or removing a column breaks every consumer. Add the new
column, migrate consumers, then remove the old one in a later release.

### 4.2 Nullable by Default for New Columns

A new column with `NOT NULL` and no default breaks existing writers.
Add as nullable, backfill, then enforce.

### 4.3 Versioned Schemas for Streaming

A Kafka topic or a similar stream has a versioned schema (Avro,
Protobuf, JSON Schema) registered in a schema registry. Consumers
negotiate the version.

### 4.4 Document Breaking Changes

A schema change that breaks consumers is announced in advance, with
a migration window.

### 4.5 No Silent Type Changes

Changing `int` to `string` breaks every consumer. Even if the
database accepts it.

## 5. Late and Out-of-Order Data

### 5.1 Watermarks

A streaming pipeline defines a watermark: how late data may arrive.
Data after the watermark is dropped or routed to a dead-letter queue.

### 5.2 Windowed Aggregations

A windowed aggregation (hourly, daily) waits until the watermark
passes before emitting the final result. Late data within the window
is incorporated; later data is not.

### 5.3 Idempotent Late Arrival

A late event re-processes the affected window. The window's output
is recomputed, not added to.

### 5.4 Ordering Is Not Guaranteed

Assume events arrive out of order. Include an event timestamp in every
message. Do not use arrival time.

## 6. DAG Design

### 6.1 One Task, One Job

A task does one thing. Extract, transform, and load are three tasks.

### 6.2 Tasks Are Idempotent

Each task is safe to retry. See section 2.

### 6.3 Tasks Are Independent Where Possible

Parallel branches run concurrently. Sequential dependencies are
explicit.

### 6.4 No Cross-DAG Imports

A DAG does not import from another DAG. Shared logic goes in a
library module.

### 6.5 Retries With Backoff

A task has a retry policy: `retries=3`, `retry_delay=timedelta(minutes=5)`,
`exponential_backoff=True`. Not `retries=100` with no delay.

### 6.6 Failure Alerts

A task failure alerts the on-call. A DAG that fails silently is worse
than one that crashes loudly.

### 6.7 Timeouts

Every task has a timeout. A task that hangs forever blocks the DAG.

### 6.8 No Backfill in the Scheduler

Backfills are run manually (or via a separate scheduler). They do not
compete with the regular schedule for worker slots.

## 7. Data Quality

### 7.1 Validate at Boundaries

Data entering the pipeline is validated:

- Schema (types, nullability, required fields).
- Range (numbers within bounds).
- Referential integrity (foreign keys exist).
- Business rules (status values are in the allowed set).

### 7.2 Quarantine Bad Data

BAD: A malformed record crashes the pipeline.
GOOD: The record goes to a dead-letter queue; the pipeline continues.

### 7.3 Data Quality Metrics

Track:

- Row counts per run.
- Null rates per column.
- Distinct value counts for categorical columns.
- Freshness (time since last update).

Alert when any metric deviates from its baseline.

### 7.4 No Silent Data Loss

A filter that drops 5% of rows is a decision. Log it. Alert on
changes to the drop rate.

### 7.5 Test in the Pipeline

A pipeline includes tests:

- Uniqueness of primary keys.
- Foreign key integrity.
- Expected ranges.
- No unexpected nulls.

dbt tests, Great Expectations, or a custom framework.

## 8. Storage and Cost

### 8.1 Columnar Formats

Parquet, ORC, or Avro for analytical data. CSV is a transfer format,
not a storage format.

### 8.2 Partitioning

Partition by the column most used in filters (usually date).
Over-partitioning (by hour on a small dataset) produces small files
and slow queries.

### 8.3 Compaction

Small files slow down queries. A compaction job periodically merges
them.

### 8.4 Retention

Old data is deleted per policy. A pipeline that writes 10 TB a month
and never deletes anything is a growing cost.

### 8.5 Cost Monitoring

Query cost on cloud warehouses (BigQuery, Snowflake, Redshift) is
driven by bytes scanned. Monitor it. A query that scans 1 TB should
be a decision, not an accident.

## 9. Data Pipeline Anti-Patterns

### 9.1 Non-Idempotent Pipelines

Covered in 2.1. The most damaging data pipeline mistake.

### 9.2 `INSERT` Without Upsert

Covered in 2.2.

### 9.3 Time-Based Table Names

BAD: `events_2025_01_15_14_30`. Every run creates a new table.
Consumers do not know which to read.
GOOD: One table partitioned by `event_date`.

### 9.4 Silent Failures

BAD: A try/except that logs and continues.
GOOD: A dead-letter queue with an alert.

### 9.5 Hard-Coded Dates

BAD: `WHERE date = '2025-01-15'` in a daily DAG.
GOOD: `WHERE date = '{{ ds }}'` (Airflow) or an equivalent.

### 9.6 No Watermark

Covered in 5.1.

### 9.7 Retries Without Backoff

A task that fails due to a transient database issue retries in a
tight loop, overwhelming the database.

### 9.8 Cross-Environment Data Leakage

BAD: A staging pipeline that reads from production without a filter.
GOOD: Environment-scoped credentials and explicit data subsets.

### 9.9 No Lineage

Nobody knows which pipeline produced a table or which tables depend
on it. Column-level lineage (dbt, OpenLineage) answers this.

### 9.10 No Documentation

A pipeline with no README, no owner, no SLA. When it fails at 3 AM,
no one knows what to do.

### 9.11 DAGs That Import From Other DAGs

Covered in 6.4.

### 9.12 Parallelism Without Bound

BAD: A pipeline that launches 10,000 concurrent tasks.
GOOD: A pool with a concurrency limit.

### 9.13 No Partition Pruning

BAD: `SELECT * FROM events WHERE YEAR(event_time) = 2025`. This
prevents partition pruning.
GOOD: `WHERE event_date >= '2025-01-01' AND event_date < '2026-01-01'`.

### 9.14 Timezone Confusion

A pipeline that mixes UTC and local time. Timestamps stored as naive
datetimes. `WHERE date = ...` produces different results depending on
the server's timezone.

Always UTC. Always timezone-aware.

### 9.15 Ignoring Late Data

Covered in 5.

### 9.16 Backfill by Replaying the Scheduler

Running the scheduler for a past date does not equal a backfill. The
scheduler has current code, current resources, and current side
effects. Use the dedicated backfill path.

### 9.17 No Data Contracts

A producer changes its schema without notifying consumers. The
pipeline breaks at 2 AM. Data contracts (a registry, a version, a
documented interface) prevent this.

### 9.18 Overwriting Without a Snapshot

A backfill or a re-run overwrites historical data with no way to
compare. Keep a snapshot of the previous state.

### 9.19 PII Without Control

BAD: A pipeline that copies PII into an analytics warehouse without
masking.
GOOD: Tokenization or masking at the boundary; PII stays in the
source system.

### 9.20 Testing in Production

BAD: A new transformation tested only against the production dataset.
GOOD: A sampled dataset in staging, with representative edge cases.

### 9.21 No Version Control for Transformations

BAD: SQL edited directly in the warehouse UI.
GOOD: SQL in Git, deployed via the pipeline.

### 9.22 Cron-Only Scheduling

A cron job with no visibility, no retries, no alerting. If it fails,
nobody notices until the data is stale. Use an orchestrator.

### 9.23 Long-Running Backfills in the Scheduler

Covered in 6.8.

## 10. Response to Violation

If a previous response violated a rule here:

```
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

No justification. No apology paragraph. Fix and move on.
