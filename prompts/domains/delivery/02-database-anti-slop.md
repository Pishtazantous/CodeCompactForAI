---
id: 02-database-anti-slop
title: "Database Anti-Slop Layer"
lang: en
depends_on: ["_universal/00-style-guide.md", "_universal/00-master-anti-slop.md"]
category: domain
domain_type: delivery
version: 3
---

# Database Anti-Slop Layer

This file defines behavioral contracts specific to database work. It sits in the delivery layer, below the universal anti-slop rules and above framework-specific ORM patterns. It covers schema design, migrations, queries, indexes, transactions, data types, access control, and backup. It is engine-agnostic: PostgreSQL, MySQL, SQLite, MongoDB, and their managed equivalents share these rules. It does not cover ORM-specific patterns (see framework files), application-level caching (see `02-backend-anti-slop.md`), or data pipeline design (see `02-data-pipeline-anti-slop.md`).

A database is the last line of defense for data integrity. The application can be rewritten; the data cannot be recreated.

## Scope

This file applies to relational databases (PostgreSQL, MySQL, MariaDB, SQL Server, SQLite, Oracle), document databases (MongoDB, CouchDB, Firestore), key-value stores used as primary storage (DynamoDB, Cassandra), and managed services (RDS, Aurora, Cloud SQL, Atlas). The examples use SQL and PostgreSQL-specific syntax where illustrative. Engine-specific details are noted where they differ.

## Rule Severity

Severity follows `_universal/00-style-guide.md`.

## Contracts

A database commits to eight contracts. The table below maps each contract to the rules that enforce it.

| Contract | Description | Enforced By |
|---|---|---|
| Data Integrity | Every row satisfies the constraints the schema declares. Constraints are enforced by the database, not only by the application. | DB-002, DB-004, DB-007, DB-086 |
| Query Predictability | A query's performance is predictable from its plan. No query scans a table without an index unless the table is small. | DB-020, DB-026, DB-027, DB-075 |
| Transactional Safety | A multi-step write either completes fully or leaves no trace. Partial writes are not visible to readers. | DB-034 to DB-040 |
| Schema Evolution | Every schema change is reversible, tested, and applied through a migration. No manual edits to production. | DB-009 to DB-015 |
| Access Control | Every user and service has the minimum permissions it needs. Application users cannot alter the schema. | DB-049 to DB-054 |
| Data Durability | Every write that is acknowledged is durable across a crash. The database's durability settings match the business requirement. | DB-043, DB-055 to DB-060 |
| Observability | Slow queries, lock waits, replication lag, and connection count are visible. The database is not a black box. | DB-061 to DB-067 |
| Resource Discipline | Connections, transactions, and queries are bounded and cleaned up. | DB-018, DB-035, DB-078, DB-079 |

## Schema Design

### DB-001 — Existing Table Discovery

**MUST**

Before creating a new table, the assistant MUST search the schema for an existing table that covers the same concept. Duplicate tables cause divergent data.

See MAS-035 in `_universal/00-master-anti-slop.md`.

### DB-002 — Single Concept Table

**MUST**

A table MUST represent a single concept. If a table has columns that apply only to some rows, the model is wrong.

Example (illustrative, SQL):

BAD: A `contacts` table with `company_name` and `personal_note`, where `company_name` is only set for business contacts.

GOOD: A `contacts` table with a `type` column and a separate `companies` table.

### DB-003 — Normalization Baseline

**SHOULD**

Schemas SHOULD start in third normal form. Denormalization MUST only occur with a measured performance reason, documented in the migration.

### DB-004 — NOT NULL Default

**MUST**

Columns MUST default to `NOT NULL`. A nullable column MUST have a documented reason.

Example (illustrative, SQL):

BAD: `email VARCHAR(255)` allowing nulls because the schema author did not think about it.

GOOD: `email VARCHAR(255) NOT NULL` when every user must have an email.

### DB-005 — Nullable Semantics

**MUST**

A nullable column means "this value may legitimately be absent". It MUST NOT mean "we did not know at insert time". A separate status column MUST be used for the latter.

### DB-006 — Schema Naming Convention

**MUST**

The project's existing naming convention MUST be matched:

- Tables: `snake_case`, usually plural (`users`, `order_items`).
- Columns: `snake_case` (`created_at`, `user_id`).
- Foreign keys: `<referenced_table_singular>_id` (`user_id`).
- Indexes: `<table>_<column>_idx` or the project's pattern.

Plural and singular table names MUST NOT be mixed.

### DB-007 — Primary Key Requirement

**MUST**

Every table MUST have a primary key. A surrogate key (UUID, bigint) is preferred for the internal identifier. A natural key (unique constraint) is used for business identity. A table without a primary key accumulates duplicate rows.

### DB-008 — Public Identifier Separation

**MUST**

If the project exposes resources to clients (URLs, APIs), the public identifier MUST be a UUID or a random slug, not the auto-increment primary key.

Example (illustrative):

BAD: `/users/42` (sequential, enumerable).

GOOD: `/users/9f3a...` (UUID, non-enumerable).

## Migrations

### DB-009 — Migration-Only Changes

**MUST**

Every schema change MUST go through a migration. Manual `ALTER TABLE` in production and ORM auto-sync in production MUST NOT be used.

See MAS-035 in `_universal/00-master-anti-slop.md`.

### DB-010 — Immutable Migrations

**MUST**

Once applied in a shared environment, a migration MUST be frozen. Fixing a bug MUST require a new migration.

### DB-011 — Migration Reversibility

**MUST**

Every migration MUST be either reversible (with a working `down`) or explicitly irreversible, with a comment explaining why.

### DB-012 — Backwards-Compatible Migrations

**MUST**

Breaking changes MUST follow the safe sequence:

1. Add the new column (nullable or with a default).
2. Deploy code that writes to it.
3. Backfill data (separate step).
4. Add the `NOT NULL` constraint (separate migration).
5. Remove the old column (later migration after the code stops using it).

Steps MUST NOT be combined on a large table.

### DB-013 — Lock-Aware Migrations

**MUST**

Operations that lock the table MUST be identified and mitigated:

- Adding a column with a default: locks on older engines.
- Adding an index: locks writes unless `CONCURRENTLY` (PostgreSQL).
- Changing a column type: often rewrites the table.
- Adding a foreign key: locks unless validated separately.

For any table over 1M rows, the project's online-schema-change strategy MUST be used.

### DB-014 — Destructive Operation Confirmation

**MUST NOT**

`DROP TABLE`, `DROP COLUMN`, `TRUNCATE` MUST NOT be executed without explicit confirmation, even when the task seems to require it.

### DB-015 — CI Migration Testing

**MUST**

The migration MUST be tested against a copy of the production schema in CI before deployment.

## Queries

### DB-016 — Explicit Column Selection

**MUST NOT**

`SELECT *` MUST NOT be used. Columns MUST be listed explicitly. `SELECT *` breaks when a column is added or removed and transfers data the caller does not need.

### DB-017 — N+1 Query Prevention

**MUST NOT**

A loop containing a query is an N+1 pattern and MUST NOT be used.

Example (illustrative, application + SQL):

BAD:
```javascript
for (const user of users) {
  const orders = await db.query("SELECT * FROM orders WHERE user_id = $1", [user.id]);
}
```

GOOD:
```sql
SELECT u.id, u.name, o.id AS order_id, o.total
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE u.id = ANY($1);
```

See MAS-040 in `_universal/00-master-anti-slop.md`.

### DB-018 — Mandatory Pagination

**MUST**

Every list query MUST have a `LIMIT`. Unbounded `SELECT` queries MUST NOT be executed.

### DB-019 — Cursor Pagination

**MUST**

Cursor pagination MUST be used for deep pages. `OFFSET` on large tables scans and discards rows, causing severe performance degradation.

Example (illustrative, SQL):

BAD:
```sql
SELECT * FROM events ORDER BY created_at DESC LIMIT 20 OFFSET 100000;
```

GOOD:
```sql
SELECT * FROM events
WHERE created_at < $1
ORDER BY created_at DESC
LIMIT 20;
```

### DB-020 — Sargable Queries

**MUST NOT**

Functions MUST NOT be used in `WHERE` clauses on indexed columns, as they prevent index usage.

Example (illustrative, SQL):

BAD:
```sql
SELECT * FROM users WHERE LOWER(email) = 'x@y.com';
```

GOOD: An expression index on `LOWER(email)`, a `CITEXT` column (PostgreSQL), or storing the value normalized.

### DB-021 — Explicit Join Aliases

**MUST**

Every column in a join MUST be qualified with its table alias. Ambiguous column names MUST NOT be used.

Example (illustrative, SQL):

BAD:
```sql
SELECT id, name FROM users JOIN orders ON ...;
```

GOOD:
```sql
SELECT u.id, u.name FROM users u JOIN orders o ON o.user_id = u.id;
```

### DB-022 — Existence Check Optimization

**MUST**

For existence checks, `EXISTS` MUST be used instead of `COUNT(*) > 0`. `EXISTS` stops at the first match.

Example (illustrative, SQL):

BAD:
```sql
SELECT COUNT(*) FROM users WHERE email = $1;
```

GOOD:
```sql
SELECT EXISTS(SELECT 1 FROM users WHERE email = $1);
```

### DB-023 — Transactional Read-Modify-Write

**MUST**

A pattern that reads a value, computes a new value, and writes it back MUST be inside a transaction with appropriate isolation to prevent race conditions.

Example (illustrative, SQL):

BAD:
```sql
SELECT balance FROM accounts WHERE id = 1;  -- returns 100
UPDATE accounts SET balance = 120 WHERE id = 1;  -- races with another request
```

### DB-024 — Request Path Query Limit

**MUST NOT**

Queries that may take seconds MUST NOT run in the request path. Heavy work MUST be moved to a background job.

### DB-025 — Leading Wildcard Prohibition

**MUST NOT**

`LIKE '%...'` MUST NOT be used on large tables, as a leading wildcard cannot use a normal index. Full-text search or a trigram index MUST be used instead.

## Indexes

### DB-026 — Foreign Key Indexing

**MUST**

Every foreign key MUST have an index. Without an index, joins and cascading deletes scan the child table. (Note: MySQL with InnoDB is an exception and creates it automatically).

### DB-027 — Filter and Sort Indexing

**MUST**

For every query pattern in the codebase, the filter and sort columns MUST be identified and an index MUST exist.

### DB-028 — Composite Index Ordering

**MUST**

Composite index columns MUST be ordered by selectivity and usage pattern. `(a, b)` supports queries on `a` and on `(a, b)`, but does not support queries on `b` alone.

### DB-029 — Index Overhead Awareness

**MUST NOT**

Tables MUST NOT be over-indexed. Every index costs writes and storage. A table with 15 indexes has slow inserts.

### DB-030 — Partial Index Usage

**SHOULD**

Partial indexes SHOULD be used for subset queries to reduce index size and improve speed.

Example (illustrative, PostgreSQL):

BAD:
```sql
CREATE INDEX idx_orders_user ON orders(user_id);
```

GOOD (if query is always `WHERE status = 'pending'`):
```sql
CREATE INDEX idx_orders_pending ON orders(user_id)
WHERE status = 'pending';
```

### DB-031 — Expression Index Usage

**SHOULD**

Expression indexes SHOULD be used for computed filters.

Example (illustrative, PostgreSQL):
```sql
CREATE INDEX idx_users_lower_email ON users(LOWER(email));
```

### DB-032 — Meaningful Index Names

**MUST**

Index names MUST be meaningful and communicate the table, column, and purpose (e.g., `idx_users_email` instead of `users_email_index_1`).

### DB-033 — Unused Index Removal

**MUST**

Unused indexes MUST be removed. An index that no query uses wastes storage and slows writes. Index usage MUST be monitored.

## Transactions

### DB-034 — Explicit Transaction Boundaries

**MUST**

Every write operation MUST define its transaction boundary. What must succeed or fail together MUST be explicit.

### DB-035 — Short Transaction Duration

**MUST NOT**

Transactions hold locks. A transaction MUST NOT include a network call, user input, or long computation. External calls MUST be done outside the transaction.

Example (illustrative, SQL):

BAD:
```sql
BEGIN;
SELECT ...;  -- acquire locks
-- application calls an external API (takes 2 seconds)
UPDATE ...;
COMMIT;
```

See MAS-040 in `_universal/00-master-anti-slop.md`.

### DB-036 — Isolation Level Selection

**MUST**

The database's default isolation level (e.g., `READ COMMITTED` in PostgreSQL) MUST be used by default. Escalation to `REPEATABLE READ` or `SERIALIZABLE` MUST only occur with a reason and a plan for handling serialization failures.

### DB-037 — Deadlock Handling

**MUST**

The application MUST catch deadlock errors and retry with backoff.

### DB-038 — Nested Transaction Prohibition

**MUST NOT**

If the database or ORM does not support savepoints, transactions MUST NOT be nested. They MUST be refactored into a single transaction.

### DB-039 — Idempotent Transaction Retries

**MUST**

A transaction that must be retried (after a serialization failure or a deadlock) MUST be idempotent. An idempotency key or a natural key MUST be used.

### DB-040 — HTTP Response Transaction Boundary

**MUST NOT**

A transaction MUST NOT be held across an HTTP response. A transaction that commits after the response is sent is unpredictable. Commits MUST happen before responding.

## Data Types

### DB-041 — Appropriate Data Types

**MUST**

The correct native type MUST be used:

- **Money**: integer (minor units) or native decimal.
- **Timestamps**: timestamp-with-timezone type.
- **Identifiers**: the project's convention (UUID, bigint).
- **Booleans**: the database's boolean type.
- **Enums**: a lookup table, a `CHECK` constraint, or the native enum type.

### DB-042 — Money Type Prohibition

**MUST NOT**

Money MUST NOT be stored as `FLOAT`. Floating point cannot represent most decimal values exactly (`0.1 + 0.2 != 0.3`). `BIGINT` (cents) or `NUMERIC` MUST be used.

### DB-043 — Timezone-Aware Timestamps

**MUST**

Timestamps MUST use the timezone-aware type (`TIMESTAMPTZ` in PostgreSQL) or `DATETIME` with an explicit UTC convention (MySQL). Plain `TIMESTAMP` MUST NOT be used.

### DB-044 — String Length Bounds

**MUST**

Every string column MUST have a maximum length that reflects the domain. `VARCHAR(255)` for everything is a smell.

Example (illustrative, SQL):

BAD: `name VARCHAR(255)` for a name that can be at most 100 chars.

GOOD: `name VARCHAR(100) NOT NULL`.

### DB-045 — VARCHAR vs TEXT Semantics

**MUST**

In PostgreSQL, `VARCHAR(n)` and `TEXT` have identical performance. `VARCHAR(n)` MUST only be used when the length limit is a business rule.

### DB-046 — JSONB Usage Discipline

**MUST NOT**

`JSONB` MUST only be used for genuinely schemaless data (settings, metadata). It MUST NOT be used to avoid schema design. Normal columns MUST be used for queryable fields.

### DB-047 — ENUM Strategy

**MUST**

Native `ENUM` types MUST NOT be used without a strategy. PostgreSQL enums are difficult to alter. A lookup table or a `CHECK` constraint MUST be preferred unless the values are truly stable.

### DB-048 — UUID Version Selection

**MUST**

UUIDv4 (random) or UUIDv7 (time-ordered) MUST be used. UUIDv7 is preferred for primary keys because it preserves insert locality.

## Access Control

### DB-049 — Least Privilege Principle

**MUST**

Application users MUST have only the permissions they need (`SELECT`, `INSERT`, `UPDATE`, `DELETE` on specific tables). `SUPERUSER`, `CREATEDB`, and `CREATEROLE` MUST NOT be granted.

### DB-050 — Migration User Separation

**MUST**

Migrations MUST run with a user that has DDL privileges. Application queries MUST run with a user that does not. A compromised application MUST NOT be able to alter the schema.

### DB-051 — Credential Secrecy

**MUST NOT**

Database credentials MUST come from the environment or a secret manager. They MUST NEVER be hard-coded, committed, or logged.

### DB-052 — Row-Level Security

**SHOULD**

For multi-tenant applications, row-level security (RLS) in PostgreSQL SHOULD be considered. The policy is enforced at the database, not only in application code.

### DB-053 — Analytics Replica Usage

**MUST**

Reporting or analytics queries MUST run against a read replica, not the primary. The primary MUST serve transactions.

### DB-054 — Connection Encryption

**MUST**

The connection to the database MUST use TLS. Even for local development, TLS MUST be used if the project supports it.

## Backup and Recovery

### DB-055 — Pre-Destructive Backup

**MUST**

Before any migration that drops, truncates, or rewrites large amounts of data, a backup MUST exist.

### DB-056 — Restore Path Testing

**MUST**

A backup that has never been restored is not a backup. Restores MUST be tested into a test environment at least quarterly.

### DB-057 — Point-in-Time Recovery

**MUST**

If the database supports PITR, WAL (PostgreSQL) or binlog (MySQL) archiving MUST be enabled. Without it, recovery is limited to the last full backup.

### DB-058 — Backup Encryption

**MUST**

Backups MUST be encrypted with a key that is not stored in the same location as the backup.

### DB-059 — RPO and RTO Documentation

**MUST**

The recovery point objective (RPO) and recovery time objective (RTO) MUST be documented. The backup strategy MUST match them.

### DB-060 — Recovery Runbook

**MUST**

A runbook for restoring the database MUST be documented (who to call, what to do, how to verify).

## Observability

### DB-061 — Slow Query Logging

**MUST**

The slow query log MUST be enabled and reviewed.

### DB-062 — Query Statistics Extension

**MUST**

Query statistics extensions (e.g., `pg_stat_statements` for PostgreSQL) MUST be enabled to show top queries by time, calls, and rows.

### DB-063 — Connection Count Monitoring

**MUST**

Connection count MUST be monitored. A connection pool that exhausts the database's `max_connections` causes failures.

### DB-064 — Replication Lag Monitoring

**MUST**

Replication lag MUST be monitored. A read replica that lags behind the primary serves stale data. Alerts MUST fire when it exceeds the threshold.

### DB-065 — Lock Wait Monitoring

**MUST**

Lock waits MUST be monitored and investigated. Long lock waits block other transactions.

### DB-066 — Disk Usage Monitoring

**MUST**

Disk usage MUST be monitored and forecasted. A database that fills its disk stops accepting writes.

### DB-067 — Failure Alerting

**MUST**

Alerts MUST fire when the database is unavailable, not only when a metric crosses a threshold.

## AI-Specific Database Discipline

### DB-068 — Schema Verification Before Query

**MUST**

Before writing any database query, the assistant MUST verify that the referenced tables, columns, and indexes exist in the project's migration files or schema definitions. Invented column names produce runtime failures that are invisible at compile time.

See MAS-036 in `_universal/00-master-anti-slop.md`.

### DB-069 — Migration Pattern Verification

**MUST**

Before creating a migration, the assistant MUST fetch and follow the project's existing migration pattern. Migration frameworks differ (Knex, Alembic, Django, Flyway, Entity Framework). Invented migration syntax breaks the migration chain.

See MAS-035 in `_universal/00-master-anti-slop.md`.

### DB-070 — Index Verification

**MUST**

Before adding an index, the assistant MUST verify the table size and existing indexes. Adding an index to a massive table without `CONCURRENTLY` (or equivalent) locks the table and causes an outage.

### DB-071 — Complexity Restraint in Schema

**SHOULD**

The assistant SHOULD NOT introduce complex schema patterns (partitioning, materialized views, complex triggers) unless the project already uses them and the task explicitly requires them.

See MAS-038 in `_universal/00-master-anti-slop.md`.

## Anti-Patterns

### DB-072 — Soft Delete Strategy

**MUST NOT**

Soft deletes (`deleted_at TIMESTAMP`) MUST NOT be used without a plan. Every query MUST NOT manually filter `WHERE deleted_at IS NULL`. A view, an ORM default scope, or a documented convention MUST be used.

### DB-073 — Untyped Enum Prohibition

**MUST NOT**

A `status` column that stores whatever the application passes MUST NOT be used. A `CHECK` constraint, a lookup table, or a native enum MUST be used.

### DB-074 — Cascading Delete Restraint

**MUST NOT**

`ON DELETE CASCADE` MUST NOT be the default on every foreign key. Cascade MUST only be used where the child row is meaningless without the parent. Otherwise, `RESTRICT` MUST be used and deletion handled in the application.

### DB-075 — Query Plan Verification

**MUST NOT**

A new query MUST NOT be added to the codebase without checking its plan (`EXPLAIN`) on production-sized data.

### DB-076 — Cross-Service Transaction Prohibition

**MUST NOT**

Transactions that span two databases or two services MUST NOT be used. Distributed transactions are not available in most modern databases. A saga or an outbox pattern MUST be used.

### DB-077 — ORM Auto-Sync Prohibition

**MUST NOT**

ORM auto-sync (`synchronize: true`) in production MUST NOT be used. It drops and recreates columns based on entity definitions and destroys data.

### DB-078 — Connection Pooling Requirement

**MUST**

A connection pool MUST be used. Every request MUST NOT open a new database connection, as the database's `max_connections` will be exhausted.

See MAS-040 in `_universal/00-master-anti-slop.md`.

### DB-079 — Connection Pool Limits

**MUST**

A connection pool MUST have a maximum limit. Under load, an unbounded pool opens thousands of connections and crashes the database.

### DB-080 — Implicit Type Casting Prohibition

**MUST NOT**

Implicit type casting (e.g., `WHERE id = '123'` where `id` is an integer) MUST NOT be used. Some databases cast implicitly and skip the index.

### DB-081 — Nullable Column Comparison

**MUST**

When comparing nullable columns (e.g., `WHERE status != 'active'`), rows where `status IS NULL` are excluded. `IS DISTINCT FROM` (PostgreSQL) or explicit null handling MUST be used.

### DB-082 — Unsafe Update/Delete Prohibition

**MUST NOT**

`UPDATE` or `DELETE` statements without a `WHERE` clause MUST NOT be executed.

### DB-083 — Justified Denormalization

**MUST NOT**

Denormalization (e.g., adding a `total_count` column) MUST NOT occur without a measured performance problem. The column will drift from the source.

### DB-084 — Computed Value Synchronization

**MUST NOT**

Computed values (e.g., `full_name`) MUST NOT be stored without a mechanism to recompute them on write. A generated column or application-level sync MUST be used.

### DB-085 — Surrogate Key Preference

**SHOULD**

Composite primary keys (e.g., `(user_id, created_at)`) SHOULD be avoided. A surrogate key and a unique constraint SHOULD be used instead.

### DB-086 — Business Key Uniqueness

**MUST**

Business keys (e.g., `email`) MUST have a unique constraint. Duplicates accumulate until someone notices.

### DB-087 — Coordinated ID Generation

**MUST**

Application-generated IDs MUST be coordinated. Two application instances MUST NOT generate the same ID (e.g., timestamps with second precision). UUIDs or a coordinated sequence MUST be used.

### DB-088 — Regulated Data Audit Trail

**MUST NOT**

Hard deletion of user data MUST NOT occur without an audit trail for regulated data. Soft delete or an audit log MUST be preferred.

### DB-089 — Table Concept Separation

**MUST NOT**

"One Big Table" (e.g., a `users` table with 80 columns covering identity, preferences, billing, and audit) MUST NOT be used. Tables MUST be split by concept.

### DB-090 — Pagination Metadata

**MUST**

A paginated response MUST include a cursor or total count. Clients cannot request the next page without metadata.

### DB-091 — Vacuum Configuration

**MUST NOT**

Autovacuum (PostgreSQL) MUST NOT be disabled or misconfigured. Table bloat grows and performance degrades.

## Response to Violation

When a rule in this file is violated, report:

Violation: DB-{NNN}
Reason: {one-line reason}
Correction: {smallest fix}

For multiple violations, report each rule ID separately.

Do not replace a technical correction with a generic explanation.