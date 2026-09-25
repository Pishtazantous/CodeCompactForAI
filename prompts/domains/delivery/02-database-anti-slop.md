---
id: 02-database-anti-slop
title: "Database Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: delivery
version: 2
---

# Database Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
generic security, dependency addition, output format) are NOT
repeated here.

This file covers rules specific to database work: schema design,
migrations, queries, indexes, transactions, data types, access
control, and backup. It is engine-agnostic: PostgreSQL, MySQL,
SQLite, MongoDB, and their managed equivalents share these rules.
It does NOT cover ORM-specific patterns (see the framework files),
application-level caching (see `02-backend-anti-slop.md`), or
data pipeline design (see `02-data-pipeline-anti-slop.md`).

A database is the last line of defense for data integrity. The
application can be rewritten; the data cannot be recreated. The
rules below reflect that reality.

## 1. Stack Assumptions

This file applies to:

- Relational databases: PostgreSQL, MySQL, MariaDB, SQL Server,
  SQLite, Oracle.
- Document databases: MongoDB, CouchDB, Firestore.
- Key-value stores used as primary storage: DynamoDB, Cassandra.
- Managed services: RDS, Aurora, Cloud SQL, Atlas.

The examples use SQL and PostgreSQL-specific syntax. The principles
are portable. Engine-specific details (isolation level names, index
types) are noted where they differ.

## 2. Delivery Contracts

A database commits to eight contracts. Every section below enforces
one or more of these.

### 2.1 Data Integrity

Every row satisfies the constraints the schema declares. Constraints
are enforced by the database, not only by the application.

### 2.2 Query Predictability

A query's performance is predictable from its plan. No query scans
a table without an index unless the table is small.

### 2.3 Transactional Safety

A multi-step write either completes fully or leaves no trace.
Partial writes are not visible to readers.

### 2.4 Schema Evolution

Every schema change is reversible, tested, and applied through a
migration. No manual edits to production.

### 2.5 Access Control

Every user and service has the minimum permissions it needs.
Application users cannot alter the schema; migration users do not
serve traffic.

### 2.6 Data Durability

Every write that is acknowledged is durable across a crash. The
database's durability settings match the business requirement.

### 2.7 Backup and Recovery

Every database has a backup. Every backup has a tested restore
procedure. The recovery point objective (RPO) and recovery time
objective (RTO) are documented.

### 2.8 Observability

Slow queries, lock waits, replication lag, and connection count are
visible. The database is not a black box.

## 3. Schema Design

### 3.1 Reference Existing Tables First

Before creating a new table, search the schema for an existing
table that covers the same concept. Duplicate tables cause divergent
data.

### 3.2 One Table, One Concept

A table represents a single concept. If a table has columns that
apply only to some rows, the model is wrong.

BAD: A `contacts` table with `company_name` and `personal_note`,
where `company_name` is only set for business contacts.

GOOD: A `contacts` table with a `type` column and a separate
`companies` table.

### 3.3 Normalize Until It Hurts, Denormalize Until It Works

Start in third normal form. Denormalize only with a measured
performance reason, documented in the migration.

### 3.4 `NOT NULL` by Default

Default to `NOT NULL`. A nullable column must have a documented
reason.

BAD: `email VARCHAR(255)` allowing nulls because the schema author
did not think about it.

GOOD: `email VARCHAR(255) NOT NULL` when every user must have an
email.

### 3.5 Nullable Means Optional, Not Unknown

A nullable column means "this value may legitimately be absent".
It does not mean "we did not know at insert time". Use a separate
status column for the latter.

### 3.6 Naming Conventions

Match the project's existing convention:

- Tables: `snake_case`, usually plural (`users`, `order_items`).
- Columns: `snake_case` (`created_at`, `user_id`).
- Foreign keys: `<referenced_table_singular>_id` (`user_id`).
- Indexes: `<table>_<column>_idx` or the project's pattern.

Do not mix plural and singular table names.

### 3.7 Primary Keys

Every table has a primary key. Prefer:

- A surrogate key (UUID, bigint) for the internal identifier.
- A natural key (unique constraint) for business identity.

A table without a primary key is a table that will accumulate
duplicate rows.

### 3.8 Public Identifier vs Internal Key

If the project exposes resources to clients (URLs, APIs), the
public identifier is a UUID or a random slug, not the auto-increment
primary key.

BAD: `/users/42` (sequential, enumerable).

GOOD: `/users/9f3a...` (UUID, non-enumerable).

## 4. Migrations

### 4.1 Every Change Through a Migration

No manual `ALTER TABLE` in production. No ORM auto-sync in
production.

### 4.2 Migrations Are Immutable

Once applied in a shared environment, a migration is frozen.
Fixing a bug requires a new migration.

### 4.3 Reversible or Documented

Every migration is either:

- Reversible (with a working `down`), or
- Explicitly irreversible, with a comment explaining why.

### 4.4 Backwards-Compatible by Default

The safe sequence for a breaking change:

1. Add the new column (nullable or with a default).
2. Deploy code that writes to it.
3. Backfill data (separate step).
4. Add the `NOT NULL` constraint (separate migration).
5. Remove the old column (later migration after the code stops
   using it).

Never combine steps on a large table.

### 4.5 Lock Awareness

Know which operations lock the table:

- Adding a column with a default: locks on older engines.
- Adding an index: locks writes unless `CONCURRENTLY` (PostgreSQL).
- Changing a column type: often rewrites the table.
- Adding a foreign key: locks unless validated separately.

For any table over 1M rows, use the project's online-schema-change
strategy.

### 4.6 No Destructive Operations Without Confirmation

`DROP TABLE`, `DROP COLUMN`, `TRUNCATE`. Never without explicit
confirmation, even when the task seems to require it.

### 4.7 Migrations Run in CI

The migration is tested against a copy of the production schema
before deployment.

## 5. Queries

### 5.1 No `SELECT *`

List columns explicitly. `SELECT *` breaks when a column is added or
removed, and transfers data the caller does not need.

### 5.2 No N+1

A loop containing a query is an N+1 pattern.

BAD:
```sql
-- In the application:
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

### 5.3 Pagination Is Mandatory

Every list query has a `LIMIT`. No unbounded `SELECT`.

### 5.4 Cursor Pagination for Deep Pages

BAD:
```sql
SELECT * FROM events ORDER BY created_at DESC LIMIT 20 OFFSET 100000;
```

The database scans 100,020 rows to return 20.

GOOD:
```sql
SELECT * FROM events
WHERE created_at < $1
ORDER BY created_at DESC
LIMIT 20;
```

### 5.5 No Functions in `WHERE` on Indexed Columns

BAD:
```sql
SELECT * FROM users WHERE LOWER(email) = 'x@y.com';
```

The index on `email` is not used.

GOOD: An expression index on `LOWER(email)`, or a `CITEXT` column
(PostgreSQL), or store the value normalized.

### 5.6 Explicit Column Aliases in Joins

Qualify every column with its table alias.

BAD:
```sql
SELECT id, name FROM users JOIN orders ON ...;
```

`id` and `name` are ambiguous.

GOOD:
```sql
SELECT u.id, u.name FROM users u JOIN orders o ON o.user_id = u.id;
```

### 5.7 `EXISTS` Over `COUNT(*) > 0`

For existence checks:

BAD:
```sql
SELECT COUNT(*) FROM users WHERE email = $1;
-- then check if count > 0
```

GOOD:
```sql
SELECT EXISTS(SELECT 1 FROM users WHERE email = $1);
```

The `EXISTS` stops at the first match.

### 5.8 Read-Modify-Write in a Transaction

A pattern that reads a value, computes a new value, and writes it
back must be inside a transaction with appropriate isolation.

BAD:
```sql
SELECT balance FROM accounts WHERE id = 1;  -- returns 100
UPDATE accounts SET balance = 120 WHERE id = 1;  -- races with another request
```

### 5.9 No Long-Running Queries in the Request Path

A query that may take seconds blocks a request thread. Move heavy
work to a background job.

### 5.10 Avoid `LIKE '%...'`

A leading wildcard cannot use a normal index. Use full-text search
or a trigram index.

## 6. Indexes

### 6.1 Every Foreign Key Has an Index

Without an index, joins and cascading deletes scan the child table.

Rationale: most databases do not create an index on a foreign key
automatically. MySQL with InnoDB is an exception.

### 6.2 Index the Columns You Filter and Sort By

For every query pattern in the codebase, identify the filter and
sort columns and ensure an index exists.

### 6.3 Composite Index Order Matters

`(a, b)` supports queries on `a` and on `(a, b)`. It does not
support queries on `b` alone.

Order columns by selectivity and by usage pattern.

### 6.4 Do Not Over-Index

Every index costs writes. A table with 15 indexes has slow inserts.

Rationale: indexes are not free. Each additional index adds write
overhead and storage.

### 6.5 Partial Indexes for Subset Queries

BAD:
```sql
CREATE INDEX idx_orders_user ON orders(user_id);
```

If the query is always `WHERE user_id = $1 AND status = 'pending'`:

GOOD:
```sql
CREATE INDEX idx_orders_pending ON orders(user_id)
WHERE status = 'pending';
```

The partial index is smaller and faster.

### 6.6 Expression Indexes for Computed Filters

A query filtering on `LOWER(email)` uses an expression index:

```sql
CREATE INDEX idx_users_lower_email ON users(LOWER(email));
```

### 6.7 Index Name Is Meaningful

`idx_users_email` is better than `users_email_index_1`. The name
communicates the table, column, and purpose.

### 6.8 Unused Indexes Are Removed

An index that no query uses wastes storage and slows writes. Monitor
index usage and remove unused ones.

## 7. Transactions

### 7.1 Define the Unit of Work

Every write operation defines its transaction boundary. What must
succeed or fail together?

### 7.2 Short Transactions

Transactions hold locks. A transaction that includes a network
call, user input, or long computation blocks other requests.

BAD:
```sql
BEGIN;
SELECT ...;  -- acquire locks
-- application calls an external API (takes 2 seconds)
UPDATE ...;
COMMIT;
```

GOOD: Do the external call outside the transaction.

### 7.3 Choose the Right Isolation Level

Default to the database's default (`READ COMMITTED` in PostgreSQL).
Escalate to `REPEATABLE READ` or `SERIALIZABLE` only with a reason
and a plan for handling serialization failures.

### 7.4 Handle Deadlocks

When two transactions acquire locks in different orders, the
database detects a deadlock and aborts one. The application must
catch the deadlock error and retry with backoff.

### 7.5 No Nested Transactions Without Savepoints

If the database or ORM does not support savepoints, do not nest
transactions. Refactor into a single transaction.

### 7.6 Idempotent Retries

A transaction that must be retried (after a serialization failure
or a deadlock) is idempotent. Use an idempotency key or a natural
key.

### 7.7 Never Hold a Transaction Across an HTTP Response

A transaction that commits after the response is sent is
unpredictable. Commit before responding.

## 8. Data Types

### 8.1 Use the Right Type

- **Money**: integer (minor units) or the database's native decimal.
  Never `float`.
- **Timestamps**: the timestamp-with-timezone type (`TIMESTAMPTZ` in
  PostgreSQL). Never a string.
- **Identifiers**: the project's convention (UUID, bigint).
- **Booleans**: the database's boolean type. Not `0`/`1` as `int`.
- **Enums**: a lookup table, a `CHECK` constraint, or the native
  enum type.

### 8.2 Money Never as Float

BAD: `price FLOAT`.

Floating point cannot represent most decimal values exactly.
`0.1 + 0.2 != 0.3`.

GOOD: `price_cents BIGINT` or `price NUMERIC(12, 2)`.

### 8.3 Timestamps With Timezone

BAD: `created_at TIMESTAMP`.

GOOD: `created_at TIMESTAMPTZ` (PostgreSQL) or `DATETIME` with an
explicit UTC convention (MySQL).

### 8.4 String Length Limits

Every string column has a maximum length that reflects the domain.
`VARCHAR(255)` for everything is a smell.

BAD: `name VARCHAR(255)` for a name that can be at most 100 chars.

GOOD: `name VARCHAR(100) NOT NULL`.

### 8.5 `VARCHAR` vs `TEXT`

In PostgreSQL, `VARCHAR(n)` and `TEXT` have identical performance.
Use `VARCHAR(n)` only when the length limit is a business rule.

### 8.6 JSONB for Genuinely Schemaless Data

Use a `JSONB` column for data that is genuinely variable (settings,
metadata). Do not use it to avoid schema design.

BAD: A `data JSONB` column holding the entire domain model.

GOOD: Normal columns for queryable fields, `JSONB` for extension
attributes.

### 8.7 No `ENUM` Without a Strategy

PostgreSQL enums are difficult to alter (adding a value requires a
migration; removing one is impossible without recreating the type).
Prefer a lookup table or a `CHECK` constraint unless the values are
truly stable.

### 8.8 UUID Version

Use UUIDv4 (random) or UUIDv7 (time-ordered). UUIDv7 is preferred
for primary keys because it preserves insert locality.

## 9. Access Control

### 9.1 Least Privilege

Application users have only the permissions they need:

- `SELECT`, `INSERT`, `UPDATE`, `DELETE` on the tables they use.
- Not `SUPERUSER`.
- Not `CREATEDB`, `CREATEROLE`.

### 9.2 Separate Migration User

Migrations run with a user that has DDL privileges. Application
queries run with a user that does not.

Rationale: a compromised application cannot alter the schema or
drop tables.

### 9.3 No Credentials in Code

Database credentials come from the environment or a secret manager.
Never hard-coded, never committed, never logged.

### 9.4 Row-Level Security When Multi-Tenant

For multi-tenant applications, consider row-level security (RLS) in
PostgreSQL. The policy is enforced at the database, not only in
application code.

### 9.5 Read-Only Replicas for Analytics

A reporting or analytics query runs against a read replica, not the
primary. The primary serves transactions.

### 9.6 Connection Encryption

The connection to the database uses TLS. Even for local development,
use TLS if the project supports it.

## 10. Backup and Recovery

### 10.1 No Destructive Operation Without a Backup

Before any migration that drops, truncates, or rewrites large
amounts of data, ensure a backup exists.

### 10.2 Test the Restore Path

A backup that has never been restored is not a backup. Restore into
a test environment at least quarterly.

### 10.3 Point-in-Time Recovery

If the database supports PITR, ensure WAL (PostgreSQL) or binlog
(MySQL) archiving is enabled. Without it, recovery is limited to the
last full backup.

### 10.4 Backups Are Encrypted

A backup of an unencrypted database is an unencrypted database in a
different folder. Encrypt backups with a key that is not stored in
the same location.

### 10.5 RPO and RTO Are Documented

The recovery point objective (how much data can be lost) and
recovery time objective (how long recovery takes) are written down.
The backup strategy matches them.

### 10.6 Document the Recovery Procedure

A runbook for restoring the database. Who to call, what to do, how
to verify. Recovery during an incident is not the time to figure it
out.

## 11. Observability

### 11.1 Slow Query Log

Every database supports a slow query log. Enable it. Review it.

### 11.2 `pg_stat_statements` (PostgreSQL)

Enable `pg_stat_statements` for query statistics. It shows the top
queries by time, calls, and rows.

### 11.3 Monitor Connection Count

A connection pool that exhausts the database's `max_connections`
causes failures. Monitor and alert.

### 11.4 Monitor Replication Lag

A read replica that lags behind the primary serves stale data.
Monitor the lag and alert when it exceeds the threshold.

### 11.5 Monitor Lock Waits

Long lock waits block other transactions. Monitor and investigate.

### 11.6 Monitor Disk Usage

A database that fills its disk stops accepting writes. Monitor
growth and forecast.

### 11.7 Alert on Failure, Not Just Metric

An alert fires when the database is unavailable, not only when a
metric crosses a threshold. A high-latency alert is less urgent than
a "database is down" alert.

## 12. Anti-Patterns

### 12.1 `SELECT *`

Covered in 5.1.

### 12.2 N+1 Queries

Covered in 5.2.

### 12.3 Soft Deletes Without a Plan

BAD: `deleted_at TIMESTAMP` and every query filters
`WHERE deleted_at IS NULL` manually.

GOOD: A view that filters, an ORM default scope, or a documented
convention that all callers follow.

### 12.4 Timestamps Without Timezone

Covered in 8.3.

### 12.5 Enum Columns Without a Constraint

A `status` column that stores whatever the application passes.

GOOD: A `CHECK` constraint, a lookup table, or a native enum.

### 12.6 Cascading Deletes as a Default

BAD: `ON DELETE CASCADE` on every foreign key.

Cascade only where the child row is meaningless without the parent.
Otherwise, `RESTRICT` and handle deletion in the application.

### 12.7 Ignoring Query Plans

Adding a query to the codebase without checking its plan on
production-sized data.

### 12.8 Migrating Without a Rollback Plan

A migration that drops a column with no plan for reverting if
something breaks.

### 12.9 Cross-Service Transactions

A transaction that spans two databases or two services. Distributed
transactions are not available in most modern databases. Use a saga
or an outbox pattern.

### 12.10 Serial as the Public Identifier

Covered in 3.8.

### 12.11 JSON as a Schema

Covered in 8.6.

### 12.12 Migrations Applied Manually in Production

A migration that says "run this on the server when you deploy".

### 12.13 `synchronize: true` in Production

ORM auto-sync in production drops and recreates columns based on
the entity definitions. It destroys data.

### 12.14 No Index on Foreign Keys

Covered in 6.1.

### 12.15 Unbounded `VARCHAR`

Covered in 8.4.

### 12.16 Money as Float

Covered in 8.2.

### 12.17 `LIKE '%...'`

Covered in 5.10.

### 12.18 `OFFSET` for Deep Pagination

Covered in 5.4.

### 12.19 No Backup

A production database without a backup. This is not an anti-pattern;
it is negligence.

### 12.20 Backup Never Tested

Covered in 10.2.

### 12.21 Schema Changes Outside Migrations

A developer who runs `ALTER TABLE` directly on production.

### 12.22 No Connection Pooling

Every request opens a new database connection. The database's
`max_connections` is exhausted.

### 12.23 Connection Pool Without Limits

A pool with no maximum. Under load, it opens thousands of
connections and crashes the database.

### 12.24 Long-Running Transactions

A transaction open for minutes blocks vacuum (PostgreSQL) or grows
the undo log (MySQL).

### 12.25 `TRUNCATE` Without Backup

A `TRUNCATE` on a production table without a recent backup.

### 12.26 Implicit Type Casting

`WHERE id = '123'` where `id` is an integer. Some databases cast
implicitly and skip the index.

### 12.27 `!=` on Nullable Columns

`WHERE status != 'active'` excludes rows where `status IS NULL`.
Use `WHERE status IS DISTINCT FROM 'active'` (PostgreSQL) or handle
nulls explicitly.

### 12.28 Missing `WHERE` on Update or Delete

```sql
UPDATE users SET active = false;
```

Without a `WHERE`, every row is updated. A production incident
waiting to happen.

### 12.29 Denormalization Without a Reason

Adding a `total_count` column without a measured performance
problem. The column drifts from the source.

### 12.30 Storing Computed Values Without Recomputing

A `full_name` column that is not updated when `first_name` or
`last_name` changes. Use a generated column or recompute on write.

### 12.31 String Column for Dates

`created_at VARCHAR(20)`. Sorting is lexicographic, comparison is
string-based, and timezone handling is manual.

### 12.32 Composite Primary Key Without Need

A composite primary key on `(user_id, created_at)`. Use a surrogate
key and a unique constraint.

### 12.33 Missing Unique Constraint

A `email` column without a unique constraint. Duplicates accumulate
until someone notices.

### 12.34 Application-Generated IDs Without Coordination

Two application instances generate the same ID (a timestamp with
second precision, a random with insufficient entropy). Use UUIDs or
a coordinated sequence.

### 12.35 Hard Delete of User Data Without Audit

Deleting a user row without preserving a record (for compliance or
dispute). Prefer soft delete or an audit log for regulated data.

### 12.36 One Big Table

A `users` table with 80 columns covering identity, preferences,
billing, and audit. Split by concept.

### 12.37 No Pagination Metadata

A paginated response without a cursor or total count. Clients
cannot request the next page.

### 12.38 Read-Only Queries on the Primary

Every analytics query hits the primary and slows transactions. Use
a read replica.

### 12.39 No `EXPLAIN` Before Deploy

A new query is deployed without checking its plan. The plan is a
sequential scan on a 10M row table.

### 12.40 Vacuum Neglect (PostgreSQL)

Autovacuum is disabled or misconfigured. Table bloat grows and
performance degrades.

## 13. Response to Violation

If a previous response violated a rule here:

```
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

No justification. No apology paragraph. Fix and move on.
