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

Layered under `_universal/00-master-anti-slop.md`. Universal rules are not
repeated. Storage and service concerns remain in the related layers.

## 1. Stack Assumptions

**1.1 Map sources and sinks.** Identify source contracts, partitions, keys,
watermarks, destinations, retention, and late-data policy before designing a
DAG.

**1.2 Use the existing engine.** Reuse the repository's scheduler, catalog,
serialization, table format, and orchestration conventions.

**1.3 Define freshness and completeness.** Every dataset needs an owner,
expected interval, acceptable delay, and a measurable failure condition.

## 2. Domain Contracts

**2.1 Processes are restartable.** A rerun with the same source snapshot and
partition must not create duplicate business effects.

**2.2 Schemas are contracts.** Producers declare fields, types, nullability,
compatibility, and ownership; consumers validate before writing.

**2.3 Data movement is observable.** Record source and sink offsets,
watermarks, row counts, rejected records, and run identifiers.

**2.4 Quality is a gate or a declared exception.** Do not silently publish
malformed, truncated, or unexpectedly missing partitions.

**2.5 Late data has a policy.** Define accept, correct, quarantine, or reject
behavior and preserve the original event time.

## 3. Domain-Specific Rules

**3.1 Make partitions deterministic.** Derive keys and paths from stable
business fields and a documented time zone.

**3.2 Checkpoint progress.** Persist offsets or completed partitions at safe
boundaries; never infer progress only from process memory.

**3.3 Design backfills separately.** Scope historical ranges, protect live
consumers, estimate cost, and use a replay-specific run identifier.

**3.4 Bound memory and fan-out.** Use batching, partition limits, and
backpressure. Never load an unbounded source into a single process.

**3.5 Validate schema compatibility.** Reject incompatible producer changes
before the task runs when the catalog supports contract checks.

**3.6 Quarantine bad records.** Keep raw input, failure reason, and safe
diagnostics; never replace a bad record with invented values.

**3.7 Handle dependencies explicitly.** A DAG node declares upstream inputs,
readiness, retries, and the result of a skipped or failed dependency.

**3.8 Test with duplicates and skew.** Include out-of-order, late, missing,
duplicated, and highly partitioned events.

**3.9 Preserve lineage.** Link dataset versions, code revision, parameters,
and source snapshot to every material output.

**3.22 Define replay ownership.** A backfill has a separate run, cost budget, namespace, and approval from live processing.

**3.23 Reconcile boundaries.** Compare source offsets, partition counts, rejected rows, and sink totals at every checkpoint.

**3.24 Make schema policy executable.** Compatibility checks run before transformation and fail with a field-level reason.

**3.25 Preserve raw inputs.** Quarantine or correction paths retain safe evidence and an operator path for the original event.

**3.26 Test delayed arrival.** Exercise event-time boundaries, clock skew, duplicates, empty partitions, and a failed dependency restart.

**3.30 Make quality gates executable.** Counts, schema, freshness, and rejection thresholds are checked at a stable boundary.

**3.31 Preserve replay identity.** Source snapshot, code revision, parameters, and run ID explain every output.

**3.32 Test recovery.** Restart from a checkpoint and compare sink state, counts, and lineage with the expected result.

**3.33 Keep lineage actionable.** Every material output names source snapshot, code revision, parameters, and run ID.

**3.34 Keep checks observable.** Record source, sink, quality, and run identifiers in safe pipeline metrics.

## 4. Domain-Specific Anti-Patterns

### 4.1 Non-Idempotent Sink Write

BAD:
```python
for row in rows:
    db.insert(row)
```

GOOD:
```python
for row in rows:
    db.upsert(row, keys=["account_id", "event_id"])
```

A retry has one durable effect per event key.

### 4.2 Latest Watermark Without Late Policy

BAD:
```python
watermark = max(watermark, event_time)
```

GOOD:
```python
if event_time < watermark - allowed_lateness:
    quarantine(event)
else:
    update_watermark(event)
```

Late data has an explicit, measurable destination.

### 4.3 Schema Change by Inference

BAD:
```python
output["amount"] = payload.get("total", 0)
```

GOOD:
```python
amount = schema.required_decimal(payload, "amount")
output["amount"] = amount
```

A contract failure stops or quarantines the record.

**3.10 Make partitioning time-safe.** Use source event time, a documented timezone, and a late-arrival policy; do not depend on ingestion order.

**3.11 Reconcile counts.** Compare source, transformed, rejected, and sink counts with an explicit tolerance and alert on unexplained loss.

**3.12 Protect replay.** A backfill uses its own namespace, parameters, and audit record so it cannot overwrite live output silently.

**3.13 Isolate failed partitions.** A bad partition is quarantined or marked failed without blocking unrelated partitions unless the contract requires a full stop.

**3.14 Retain safe diagnostics.** Include identifiers and schema locations, while redacting credentials, personal data, and raw sensitive payloads.

**3.15 Test recovery.** Kill a worker at each stage, resume from checkpoint, and verify that sink state and lineage remain correct.

**3.16 Define source snapshots.** Every run records the source offset or snapshot that justifies its outputs and evaluations.

**3.17 Make transforms deterministic.** Normalize units, time zones, null handling, and ordering before joining or aggregating.

**3.18 Protect deletion.** A correction or retention job has an explicit scope, audit trail, and recovery window.

**3.19 Respect consumer lag.** Do not rewrite a live table without coordinating readers that may still need the prior representation.

**3.20 Track operational metrics.** Measure duration, input rate, rejection rate, lag, and retry count with a stable run identifier.

**3.21 Test a clean replay.** Re-run a representative historical range and compare row counts, aggregates, and lineage to the expected result.

## 5. Response to Violation

If a prior response violated this layer, name the contract, idempotency,
schema, late-data, or DAG issue and show the corrected operator and policy.
Do not claim a backfill or data quality check ran unless it was executed.
