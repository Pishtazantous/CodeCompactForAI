---
id: 02-database-anti-slop
title: "Database Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: delivery
version: 1
---

# Database Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
security anti-patterns, output format) are NOT repeated here.

This file covers rules specific to database work: schema design,
migrations, queries, indexes, transactions, and safety. It is engine
agnostic: rules that depend on a specific database (PostgreSQL, MySQL,
MongoDB, Redis) live in the project-specific layer or in a future
engine-specific file.

## 1. Stack Assumptions

This layer applies to any relational or document database used by an
application. It covers:

- Schema design and normalization decisions
- Migrations and versioning
- Query construction and performance
- Indexing strategy
- Transactions and isolation
- Access control at the database level

It does NOT cover:

- ORM-specific rules (those belong in the relevant framework layer)
- Application-level caching (that is a separate concern)
- Data pipelines and ETL (that is `02-data-pipeline-anti-slop.md`)

## 2. Schema Design

### 2.1 Reference Existing Tables First

Before creating a new table, search the schema for an existing table
that covers the same concept. Duplicate tables are the source of
divergent data.

### 2.2 One Table, One Concept

A table represents a single concept. If a table has columns that only
apply to some rows, the model is wrong.

### 2.3 Normalize Until It Hurts, Denormalize Until It Works

Start normalized (third normal form or the project's standard).
Denormalize only with a measured performance reason, documented in the
migration.

### 2.4 Nullable vs Not Null

- Default to `NOT NULL` unless the field is genuinely optional.
- A nullable column must have a documented reason.
- Never encode "not yet set" and "explicitly empty" in the same NULL.

### 2.5 Naming Conventions

Match the project's existing convention exactly:

- `snake_case` for tables and columns in most SQL projects
- Singular or plural table names (pick one, do not mix)
- Foreign keys named `<referenced_table>_id`
- Index names follow a consistent pattern

If unsure, list the existing tables and match.

## 3. Migrations

### 3.1 Every Change Through a Migration

No manual `ALTER TABLE` in production. No ORM auto-sync in production.
Every schema change has a migration file in the project's migration
directory.

### 3.2 Migrations Are Immutable

Once a migration has been applied in any shared environment, it is
frozen. Fixing a bug in an applied migration requires a new migration.

### 3.3 Reversible or Documented

Every migration is either:

- Reversible (with a working `down`), or
- Explicitly irreversible, with a comment explaining why.

### 3.4 Backwards-Compatible by Default

A migration must be safe to apply while the old application code is
still running. The pattern:

1. Add the new column (nullable or with a default)
2. Deploy code that writes to it
3. Backfill data (separate step)
4. Add `NOT NULL` constraint (separate migration)
5. Remove the old column (separate migration, after code is deployed)

Never combine add, backfill, and constraint in a single migration on a
large table.

### 3.5 Lock Awareness

Know which operations lock the table:

- Adding a column with a default: locks in older engines
- Adding an index: locks writes unless `CONCURRENTLY` (PostgreSQL)
- Changing a column type: often rewrites the table
- Adding a foreign key: locks unless validated separately

For any operation on a table with more than 1M rows, consider the
project's locking strategy and split into smaller steps.

### 3.6 No Destructive Operations Without Confirmation

Never `DROP TABLE`, `DROP COLUMN`, or `TRUNCATE` in a migration without
explicit confirmation. Even when the task "obviously" requires it.

## 4. Queries

### 4.1 No `SELECT *`

Always list columns explicitly. `SELECT *` breaks when a column is added
or removed, and it transfers data that is not needed.

### 4.2 No N+1

If a loop contains a query, it is an N+1 pattern. Use:

- A join
- A batch fetch (`WHERE id IN (...)`)
- The ORM's eager-load mechanism

Report the N+1 to the user before fixing it if the fix requires schema
or API changes.

### 4.3 Pagination Is Mandatory

Every query that returns a list has a limit and an offset or cursor. No
unbounded `SELECT ... FROM big_table`.

### 4.4 Explicit Column Aliases in Joins

When joining, qualify every column with its table alias. Never rely on
`USING` unless the project already does.

### 4.5 Prefer `EXISTS` Over `COUNT(*) > 0`

For existence checks, `EXISTS` stops at the first match. `COUNT(*)`
counts everything.

### 4.6 No Functions in `WHERE` on Indexed Columns

`WHERE LOWER(email) = 'x'` cannot use a normal index on `email`. Either
create a functional index, store the lowercased value, or adjust the
column type to `citext` (PostgreSQL).

### 4.7 Read-Modify-Write in a Transaction

Any pattern that reads a value, computes a new value, and writes it back
must be inside a transaction with appropriate isolation. Otherwise two
concurrent requests will silently overwrite each other.

## 5. Indexes

### 5.1 Every Foreign Key Has an Index

Unless the database creates one automatically (MySQL with InnoDB does
for FKs), add an index on every foreign key column. Without it, joins
and cascading deletes are slow.

### 5.2 Index the Columns You Filter and Sort By

For each new query pattern in a migration or a service, identify the
filter and sort columns and ensure an index exists.

### 5.3 Composite Index Order Matters

`(a, b)` supports queries on `a` and on `(a, b)`. It does not support
queries on `b` alone. Order columns by selectivity and by how they are
used.

### 5.4 Do Not Over-Index

Every index costs writes. A table with 15 indexes has slow inserts.
Before adding an index, check whether an existing composite index
already covers the query.

### 5.5 Partial and Functional Indexes Are Tools

If a query only filters on a subset (`WHERE deleted_at IS NULL`), a
partial index is smaller and faster. If the query uses
`LOWER(email)`, a functional index is required.

## 6. Transactions

### 6.1 Define the Unit of Work

Every write operation defines its transaction boundary. What must
succeed or fail together?

### 6.2 Short Transactions

Transactions hold locks. A transaction that includes a network call,
user input, or long computation will block other requests. Do the I/O
outside the transaction, then commit inside.

### 6.3 Choose the Right Isolation Level

Default to the database's default isolation (usually `READ COMMITTED`).
Escalate to `REPEATABLE READ` or `SERIALIZABLE` only with a reason and
a plan for handling serialization failures.

### 6.4 Handle Deadlocks

When two transactions acquire locks in different orders, the database
detects a deadlock and aborts one. The application must catch the
deadlock error and retry with backoff. Never swallow it.

### 6.5 No Nested Transactions Without Savepoints

If the project's ORM does not support savepoints, do not nest
transactions. Refactor into a single transaction or use savepoints
explicitly.

## 7. Data Types

### 7.1 Use the Right Type

- Money: integer (minor units) or the database's native decimal. Never
  `float`.
- Timestamps: the database's timestamp-with-timezone type. Never a
  string.
- Identifiers: the project's convention (UUID, bigint). Never a
  sequence exposed as a public identifier if the project uses UUIDs
  elsewhere.
- Booleans: the database's boolean type. Never `0`/`1` as `int`.
- Enums: use a lookup table or a `CHECK` constraint, or the database's
  native enum type if the project uses it.

### 7.2 String Length Limits

Every string column has a maximum length that reflects the domain.
`VARCHAR(255)` for everything is a smell; it means the schema was not
designed.

### 7.3 No Serialized Blobs in Relational Tables

Storing JSON blobs in a `TEXT` column to avoid schema design is an
anti-pattern. Use a `JSONB` column (PostgreSQL) if the data is genuinely
schemaless, or model it properly.

## 8. Access Control

### 8.1 Least Privilege

Application users have only the permissions they need: `SELECT`,
`INSERT`, `UPDATE`, `DELETE` on the tables they use. Not `SUPERUSER`,
not `CREATEDB`, not `CREATEROLE`.

### 8.2 Separate Migration User

Migrations run with a user that has DDL privileges. Application queries
run with a user that does not. Never use the same user for both.

### 8.3 No Credentials in Code

Database credentials come from the environment or the project's secret
manager. Never hard-coded, never committed, never logged.

## 9. Backups and Recovery

### 9.1 No Destructive Operation Without a Backup

Before any migration that drops, truncates, or rewrites large amounts
of data, ensure a backup exists. State this in the migration notes.

### 9.2 Test the Restore Path

A backup that has never been restored is not a backup. When working on
recovery procedures, verify they actually work on a copy.

### 9.3 Point-in-Time Recovery

If the project supports PITR, ensure the WAL (PostgreSQL) or binlog
(MySQL) is being archived. Without it, recovery is limited to the last
full backup.

## 10. Domain-Specific Anti-Patterns

### 10.1 Soft Deletes Without a Plan

BAD: Adding `deleted_at` and expecting all queries to filter it
automatically.
GOOD: Either use a view that filters, or make the ORM's default scope
handle it, or name the column and document that callers must filter.

### 10.2 Timestamps Without Timezone

BAD: `created_at TIMESTAMP` (no tz).
GOOD: `created_at TIMESTAMPTZ` (PostgreSQL) or `DATETIME` with explicit
UTC convention.

### 10.3 Enum Columns With Application Values

BAD: A `status` column that stores whatever the application passes.
GOOD: A `CHECK` constraint, a lookup table, or a native enum type that
the database enforces.

### 10.4 Cascading Deletes as a Default

BAD: `ON DELETE CASCADE` on every foreign key.
GOOD: Cascade only where the child row is meaningless without the
parent. Otherwise, `RESTRICT` and handle deletion in the application.

### 10.5 Ignoring Query Plans

BAD: Adding a query to the codebase without checking its plan on
production-sized data.
GOOD: Running `EXPLAIN ANALYZE` on a realistic dataset for any query
that touches large tables.

### 10.6 Migrating Without a Rollback Plan

BAD: A migration that drops a column with no plan for reverting if
something breaks.
GOOD: Every migration in the response is accompanied by its `down` or
by an explicit note that it is irreversible.

### 10.7 Cross-Service Transactions

BAD: A transaction that spans two databases or two services.
GOOD: A saga or an outbox pattern. Distributed transactions are not
available in most modern databases.

### 10.8 Serial as the Public Identifier

BAD: Exposing the auto-increment primary key in URLs and APIs.
GOOD: A UUID or a random slug as the public identifier, keeping the
serial key internal.

### 10.9 JSON as a Schema

BAD: A single `data JSONB` column holding the entire domain model.
GOOD: Normal columns for queryable fields, `JSONB` only for genuinely
dynamic attributes.

### 10.10 Migrations Applied Manually in Production

BAD: A migration that says "run this on the server when you deploy".
GOOD: The migration is part of the deploy pipeline and runs
automatically.

## 11. Response to Violation

If a previous response violated a rule here:
In the previous response, [specific rule] was violated. Correction:
[corrected code]



No justification. No apology paragraph. Fix and move on.