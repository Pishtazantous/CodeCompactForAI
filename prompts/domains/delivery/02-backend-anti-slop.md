---
id: 02-backend-anti-slop
title: "Backend Anti-Slop Layer"
lang: en
depends_on: ["_universal/00-style-guide.md", "_universal/00-master-anti-slop.md"]
category: domain
domain_type: delivery
version: 5
---

# Backend Anti-Slop Layer

This file defines behavioral contracts specific to backend services. It sits in the delivery layer, below the universal anti-slop rules and above framework-specific patterns. It covers API contracts, input validation, error handling, authentication, persistence, concurrency, logging, configuration, migrations, and graceful shutdown. It does not cover framework-specific patterns (see framework files like `02-express-anti-slop.md`, `02-nestjs-anti-slop.md`), language rules (see language files), database schema design (see `02-database-anti-slop.md`), or security-critical systems in detail (see `02-security-critical-anti-slop.md`).

A backend is a contract with clients the developer does not control. Every response shape, status code, and error format is a public interface.

## Scope

This file applies to backend services regardless of language or framework. Common stacks include Node.js + Express/Fastify/NestJS, Python + FastAPI/Django/Flask, Go + net/http/Gin/Fiber, Rust + Axum/Actix, Ruby + Rails, PHP + Laravel, Java/Kotlin + Spring Boot, and C# + ASP.NET Core. The examples are language-neutral unless explicitly marked as illustrative of a specific framework. Framework-specific patterns live in framework files. Language rules live in language files.

## Rule Severity

Severity follows `_universal/00-style-guide.md`.

## Contracts

A backend commits to nine contracts. The table below maps each contract to the rules that enforce it.

| Contract | Description | Enforced By |
|---|---|---|
| Response Shape | Every response has a documented shape. Success and error shapes are consistent. | BE-001, BE-003 |
| Status Code Correctness | The HTTP status code matches the outcome. | BE-002 |
| Input Validation | Every external input is validated before use. | BE-006 to BE-012 |
| Error Containment | An error in one request does not affect other requests. | BE-013, BE-017, BE-090 |
| Identity Integrity | The server decides who the caller is. Client-provided identity is never trusted. | BE-020, BE-025 |
| Data Consistency | Every write operation either completes fully or leaves no trace. | BE-032 |
| Observability | Every request is traceable. Logs and metrics answer what happened. | BE-041, BE-042 |
| Configuration Integrity | Configuration is validated at startup. Invalid configuration fails fast. | BE-047, BE-049 |
| Graceful Lifecycle | Startup and shutdown are controlled. In-flight requests complete. | BE-064, BE-091 |

## API Contract Discipline

### BE-001 — Consistent Response Shape

**MUST**

If the project uses `{ success, data, message }`, every endpoint MUST return that shape. A single endpoint that returns `{ result }` breaks every client.

Example (illustrative):

BAD:
```json
{ "result": { "id": 1, "name": "Alice" } }
```

GOOD:
```json
{ "success": true, "data": { "id": 1, "name": "Alice" } }
```

Fetch two existing endpoints before adding a new one. Match the shape exactly.

### BE-002 — Status Code Convention

**MUST**

Status codes MUST follow project conventions. Common conventions include:

- POST that creates a resource: `201`
- POST that does not create: `200`
- Validation error: `400`
- Missing or invalid auth: `401`
- Insufficient permissions: `403`
- Not found: `404`
- Method not allowed: `405`
- Conflict (duplicate, state mismatch): `409`
- Unprocessable entity (semantic): `422`
- Rate limit exceeded: `429`
- Server error: `500`
- Upstream failure: `502` / `503` / `504`

Returning `200` with `{ "success": false }` for an error is a contract violation.

### BE-003 — Documented Endpoint Shape

**MUST**

Every endpoint MUST have an OpenAPI (or equivalent) entry with request, response, and error shapes. Undocumented endpoints are invisible to consumers and break tooling.

### BE-004 — Versioning Strategy

**MUST**

A breaking change MUST require a new version. Common strategies include URL prefix (`/api/v1/`, `/api/v2/`), header (`Accept: application/vnd.api+json;version=2`), or content negotiation. One strategy MUST be picked and used consistently.

Adding an optional field is not breaking. Removing a field, changing a type, or making an optional field required is breaking.

### BE-005 — No Undocumented Fields

**MUST NOT**

If a field is in the response, it MUST be in the schema. If it is in the schema, it MUST be intentional. Internal IDs, database column names, and debug fields MUST NOT appear in production responses.

## Input Validation

### BE-006 — External Input Validation

**MUST**

The following are attacker-controlled and MUST be validated:

- Request body
- Query string parameters
- Path parameters
- Headers (including `Authorization`, `Content-Type`, `X-Forwarded-*`)
- Cookies
- File uploads (name, type, size, content)

### BE-007 — Project Validator Usage

**MUST**

The project's existing validator MUST be used. A second validator MUST NOT be introduced.

Example (illustrative validator names): `zod`, `joi`, `class-validator`, `pydantic`, `marshmallow`.

### BE-008 — Unknown Field Rejection

**MUST**

Schemas MUST reject unknown fields. A schema that ignores unknown properties allows mass assignment attacks. Use the project's strict mode. Unknown fields MUST produce a `400`.

Example (illustrative, zod-style):
```typescript
const schema = z.object({ email: z.string().email() }).strict();
```

Example (illustrative, pydantic-style):
```python
class CreateUser(BaseModel):
    email: EmailStr
    class Config:
        extra = "forbid"
```

### BE-009 — Field Validation

**MUST**

Every field MUST have:

- Type (string, number, boolean, object, array).
- Length (max chars for strings, max items for arrays).
- Format (email, UUID, URL scheme allowlist, ISO date).
- Range (numeric min/max, date bounds).

### BE-010 — Allowlist Over Blocklist

**MUST**

An allowlist of "good" values MUST be used instead of a blocklist of "bad" values. A blocklist is always incomplete. An allowlist is enforceable.

BAD: Rejecting `<script>` in a string field.
GOOD: Accepting only `^[a-zA-Z0-9_-]{1,64}$` in a username field.

### BE-011 — Boundary Validation

**MUST**

Validation MUST happen at the request entry boundary. Business logic MUST receive validated, typed values.

BAD: A service method that re-validates a request body.
GOOD: A service method that receives `CreateUserInput` (a typed object) and trusts it.

### BE-012 — Validation Error Field Paths

**MUST**

Validation errors MUST include field paths. Clients cannot display errors without knowing which field failed.

BAD:
```json
{ "error": "invalid" }
```

GOOD:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "details": [{ "field": "email", "message": "must be a valid email" }]
  }
}
```

## Error Handling

### BE-013 — Central Error Handler

**MUST**

One central handler MUST catch all errors from route handlers and convert them to responses. Route handlers MUST NOT set error status codes directly.

See MAS-037 in `_universal/00-master-anti-slop.md`.

### BE-014 — Typed Domain Errors

**MUST**

Domain errors MUST be typed: `NotFoundError`, `ValidationError`, `ConflictError`, `UnauthorizedError`. The central handler MUST map them to HTTP status codes.

Example (illustrative):

BAD:
```typescript
throw new Error("user not found"); // no type, maps to 500
```

GOOD:
```typescript
throw new NotFoundError("User", id); // maps to 404
```

### BE-015 — Stack Trace Prohibition

**MUST NOT**

Stack traces MUST NOT be exposed in responses. Stack traces go to logs, never to the response.

BAD:
```json
{ "error": "Error: connection refused at /app/src/db.ts:42:11" }
```

GOOD:
```json
{ "error": { "code": "INTERNAL_ERROR", "message": "An error occurred" } }
```

### BE-016 — Single Logging Point

**MUST**

The central handler MUST log errors once. A route handler that catches an error, logs it, and rethrows causes double logging.

### BE-017 — Error Propagation

**MUST NOT**

Errors MUST NOT be swallowed. An error that is not logged and not rethrown is a silent failure.

BAD:
```typescript
try { await processOrder(order); } catch (e) {}
```

See MAS-037 in `_universal/00-master-anti-slop.md`.

### BE-018 — Operational vs Programmer Errors

**MUST**

Operational errors (bad input, missing resource, network timeout) MUST be mapped to 4xx or a well-known 5xx. Programmer errors (null dereference, undefined function, assertion failure) MUST be mapped to `500`, logged with full context, and alerted.

### BE-019 — Stable Error Codes

**MUST**

Error codes MUST be stable across versions. `USER_NOT_FOUND` is stable. The human-readable message may change.

## Authentication and Authorization

### BE-020 — Server-Decided Identity

**MUST**

The server MUST read the caller's identity from a signed token, a session, or a verified source. Identity MUST NEVER be read from a body field, a query param, or a header the client controls.

Example (illustrative):

BAD:
```typescript
const userId = req.body.userId;
const user = await db.users.findById(userId);
```

GOOD:
```typescript
const userId = req.user.id; // set by auth middleware
const user = await db.users.findById(userId);
```

### BE-021 — Boundary Authentication

**MUST**

Authentication MUST run before the route handler. The handler MUST assume the authenticated identity is already set.

### BE-022 — Resource-Level Authorization

**MUST**

Authentication is not authorization. Checking that the user is logged in does not check that the user owns the resource. Authorization MUST happen at the resource level.

Example (illustrative):

BAD:
```typescript
router.get("/orders/:id", auth, async (req, res) => {
  const order = await db.orders.findById(req.params.id);
  res.json(order); // any authenticated user reads any order
});
```

GOOD:
```typescript
router.get("/orders/:id", auth, async (req, res) => {
  const order = await db.orders.findOne({
    id: req.params.id,
    userId: req.user.id,
  });
  if (!order) return res.status(404).json({ error: "not found" });
  res.json(order);
});
```

### BE-023 — 404 Over 403 for Unauthorized Resources

**MUST**

If a resource exists but belongs to another user, `404` MUST be returned instead of `403`. Returning `403` reveals that the resource exists. Return `404` unless the caller has a legitimate reason to know the resource exists.

### BE-024 — Default-Deny Authorization

**MUST**

New endpoints MUST be denied by default. Access MUST be granted explicitly by a decorator, a middleware, or a role check.

BAD: An endpoint that is public until someone remembers to add auth.

GOOD: A default-deny policy with explicit opt-in for the few open endpoints.

### BE-025 — Server-Side Role Verification

**MUST NOT**

The role MUST be read from the session or a database lookup. The role MUST NEVER be trusted from a header (`X-User-Role`), a body field, or a query param.

### BE-026 — Authentication Rate Limiting

**MUST**

Login, signup, password reset, and OTP verification MUST have rate limits per account and per IP. Without them, brute force is trivial.

## Database and Persistence

### BE-027 — Project Data Layer Usage

**MUST**

If the project has a repository layer or a data access layer, it MUST be used. Queries MUST NOT be made from a route handler or a service that bypasses the repository.

### BE-028 — Parameterized Queries

**MUST**

Queries MUST be parameterized. String interpolation into SQL is an injection vulnerability.

BAD:
```typescript
db.query(`SELECT * FROM users WHERE email = '${email}'`);
```

GOOD:
```typescript
db.query("SELECT * FROM users WHERE email = $1", [email]);
```

### BE-029 — Explicit Column Selection

**MUST NOT**

`SELECT *` MUST NOT be used in production. Columns MUST be listed explicitly. `SELECT *` breaks when a column is added or removed and transfers data the caller does not need.

### BE-030 — N+1 Query Prevention

**MUST NOT**

A loop with a query inside is an N+1 pattern and MUST NOT be used.

BAD:
```typescript
const users = await db.users.findAll();
for (const user of users) {
  user.orders = await db.orders.findByUserId(user.id);
}
```

GOOD:
```typescript
const users = await db.users.findAllWithOrders();
// or:
const userIds = users.map(u => u.id);
const orders = await db.orders.findByUserIds(userIds);
```

### BE-031 — Mandatory Pagination

**MUST**

Every list endpoint MUST have a limit. No endpoint MUST return an unbounded list.

BAD: `GET /users` returns all users.

GOOD: `GET /users?limit=20&cursor=...` returns a page.

### BE-032 — Idempotent Writes or Transactions

**MUST**

A write operation that must succeed or fail atomically MUST be wrapped in a transaction. A write operation that may be retried MUST be idempotent (via an idempotency key or a natural key).

### BE-033 — PII Logging Prohibition

**MUST NOT**

Query results may contain PII. The query shape (columns, filters) MUST be logged, not the values.

### BE-034 — Pre-Deployment Migrations

**MUST**

Database migrations MUST run before the new code is deployed. The old code MUST tolerate the new schema (additive changes only during the transition).

## Concurrency and Async

### BE-035 — Non-Blocking Request Thread

**MUST NOT**

CPU-heavy tasks (image resize, PDF generation, large sort) MUST NOT run on the request thread. They MUST be offloaded to a job queue. Return `202 Accepted` with a job ID.

Example (illustrative queue names): BullMQ, Celery, Sidekiq, NATS JetStream.

### BE-036 — External Call Timeouts

**MUST**

Every HTTP, database, cache, and queue call MUST have a timeout. A call without one hangs forever.

See MAS-040 in `_universal/00-master-anti-slop.md`.

### BE-037 — No Shared Mutable State

**MUST NOT**

Module-level caches updated by requests MUST NOT be used. A cache with a defined lifecycle (Redis, a dedicated cache service) or an explicit in-memory cache with a lock MUST be used instead.

### BE-038 — Promise Rejection Handling

**MUST**

Every promise MUST be awaited, caught, or explicitly marked as fire-and-forget. An unawaited promise that rejects crashes the process or logs an unhandled error.

### BE-039 — Client Disconnect Cancellation

**MUST**

When the client disconnects, in-flight work MUST be cancelled. A long-running query that continues after the client is gone wastes resources.

### BE-040 — Bounded Concurrency

**MUST**

A batch operation that processes many items MUST have a concurrency limit. Unbounded parallelism exhausts the thread pool or the database connection pool.

## Logging

### BE-041 — Structured Logging

**MUST**

Logs MUST be structured (typically JSON) with consistent fields, not string interpolation.

BAD:
```typescript
console.log(`User ${userId} logged in from ${ip}`);
```

GOOD:
```typescript
logger.info({ userId, ip }, "user logged in");
```

### BE-042 — Request ID on Every Log

**MUST**

A request ID (from the header or generated) MUST be attached to every log line for a request. This enables tracing a request across services.

### BE-043 — Log Levels

**MUST**

Log levels MUST be used consistently:

- `error`: 5xx responses, unhandled exceptions.
- `warn`: 4xx that indicate a problem (invalid token, rate limit).
- `info`: successful side effects (user created, payment processed).
- `debug`: flow details, disabled in production.

### BE-044 — PII and Secret Logging Prohibition

**MUST NOT**

Logs are often less protected than the database. Passwords, tokens, secrets, and PII MUST NEVER appear in logs.

### BE-045 — Log Shape Over Value

**MUST**

The shape MUST be logged, not the value.

BAD: `logger.info({ body: req.body }, "request")`.

GOOD: `logger.info({ bodyKeys: Object.keys(req.body) }, "request")`.

### BE-046 — Production Logger Usage

**MUST NOT**

`console.log` MUST NOT be used in production code. The project's logger MUST be used. `console.log` bypasses formatting, level, and destination configuration.

## Configuration

### BE-047 — Startup Validation

**MUST**

Every required environment variable MUST be validated at boot. A missing `DATABASE_URL` MUST fail immediately, not at the first request.

### BE-048 — Config in Code Prohibition

**MUST NOT**

Configuration values MUST NOT be hardcoded in code.

BAD: `const apiUrl = "https://api.example.com"`.

GOOD: `const apiUrl = config.getOrThrow("API_URL")`.

### BE-049 — Typed Configuration

**MUST**

The config MUST be a typed object (validated with a schema), not scattered environment variable lookups inside service code.

### BE-050 — Secret Commitment Prohibition

**MUST NOT**

`.env` files MUST be gitignored. `.env.example` MUST list variable names with placeholder values. Secrets MUST NEVER be committed.

### BE-051 — Environment-Specific Config

**MUST**

Development, staging, and production MUST have separate values for the same keys. The keys MUST be the same across environments; the values MUST differ.

## Migrations and Schema Changes

### BE-052 — Migration-Only Changes

**MUST**

Every schema change MUST go through a migration. Manual `ALTER TABLE` in production and ORM auto-sync in production MUST NOT be used.

### BE-053 — Immutable Migrations

**MUST**

Once applied in a shared environment, a migration MUST be frozen. Fixing a bug MUST require a new migration.

### BE-054 — Backwards-Compatible Changes

**MUST**

The deploy sequence is: migrate, then deploy new code. The old code MUST tolerate the new schema. This means:

- Add columns with defaults or nullable.
- Never rename or drop a column that the old code uses.
- Remove old columns in a later migration after the code no longer references them.

### BE-055 — Destructive Operation Confirmation

**MUST NOT**

`DROP TABLE`, `DROP COLUMN`, `TRUNCATE` MUST NOT be executed without explicit confirmation.

### BE-056 — Automated Migration Execution

**MUST**

The deploy pipeline MUST run migrations. A developer MUST NOT SSH into production and run them manually.

## Rate Limiting and Resource Protection

### BE-057 — Public Endpoint Rate Limiting

**MUST**

Authentication, signup, password reset, public APIs, and expensive endpoints MUST have rate limits. An endpoint without one is a DoS vector.

### BE-058 — Per-User and Per-IP Limits

**MUST**

Limits MUST be per user and per IP. A per-IP limit alone is bypassed by a botnet. A per-user limit alone is bypassed by many accounts. Both MUST be used.

### BE-059 — Rate Limit Headers

**MUST**

Responses MUST include rate limit headers: `Retry-After`, `X-RateLimit-Limit`, `X-RateLimit-Remaining`. Clients can back off without guessing.

### BE-060 — Body Size Limit

**MUST**

The request body parser MUST have a maximum size. A body without a limit allows memory exhaustion.

Example (illustrative, Express-style):
```typescript
app.use(express.json({ limit: "100kb" }));
```

### BE-061 — Request Processing Timeout

**MUST**

A request that exceeds a maximum duration MUST be aborted. A pathological query or a slow upstream MUST NOT hold a connection forever.

## Health and Lifecycle

### BE-062 — Liveness Endpoint

**MUST**

A liveness endpoint MUST return `200` when the process is running. It MUST NOT check dependencies. A failing dependency does not mean the process should be killed.

### BE-063 — Readiness Endpoint

**MUST**

A readiness endpoint MUST return `200` when the process can serve traffic (database reachable, cache available). A failing dependency MUST remove the process from the load balancer, but MUST NOT restart it.

### BE-064 — Graceful Shutdown

**MUST**

On shutdown signal:

1. Stop accepting new requests.
2. Finish in-flight requests (with a timeout).
3. Close database and cache connections.
4. Exit with code `0`.

A process that exits immediately drops in-flight requests.

### BE-065 — Load Balancer Drain Delay

**SHOULD**

In orchestrated environments, the process SHOULD wait a few seconds after shutdown signal before closing the listener, allowing the load balancer to remove it from rotation.

### BE-066 — Startup Health Check

**MUST**

During startup, the process MUST report "not ready" until migrations and warmups complete. Traffic MUST NOT arrive before the process is ready.

## AI-Specific Backend Discipline

### BE-067 — Schema Verification Before Query

**MUST**

Before writing any database query, the assistant MUST verify that the referenced tables, columns, and indexes exist in the project's migration files or schema definitions. Invented column names produce runtime failures that are invisible at compile time.

If the schema cannot be verified, the assistant MUST ask the user rather than guess.

See MAS-036 in `_universal/00-master-anti-slop.md`.

### BE-068 — ORM Method Verification

**MUST**

Before using an ORM method, the assistant MUST verify the method exists in the project's ORM version. Different ORM versions have different APIs. Invented methods produce AttributeError, TypeError, or undefined function errors at runtime.

BAD: Using `db.users.findByEmail()` when the ORM only has `db.users.findOne({ email })`.

GOOD: Fetch the ORM's model file or documentation first, then use the verified method.

See MAS-036 in `_universal/00-master-anti-slop.md`.

### BE-069 — Migration Pattern Verification

**MUST**

Before creating a migration, the assistant MUST fetch and follow the project's existing migration pattern. Migration frameworks differ (Knex, Alembic, Django, Flyway, Entity Framework). Invented migration syntax breaks the migration chain.

### BE-070 — Connection Pattern Verification

**MUST**

Before writing database connection code, the assistant MUST verify the project's existing connection pattern. Connection pooling, retry logic, and transaction handling differ across projects. Invented connection patterns create resource leaks.

See MAS-036 in `_universal/00-master-anti-slop.md`.

### BE-071 — Existing Pattern Discovery

**MUST**

Before creating a new service, repository, middleware, or utility, the assistant MUST search the project for an existing equivalent. If one exists, it MUST be used. If it is close but imperfect, the gap MUST be reported before creating a replacement.

This prevents duplicate data layers, competing validators, and fragmented patterns.

See MAS-035 in `_universal/00-master-anti-slop.md`.

### BE-072 — Architecture Restraint

**SHOULD**

The assistant SHOULD NOT introduce architectural layers, design patterns, or abstractions that the project does not already use. A simple CRUD endpoint does not need a factory, a strategy pattern, or an event bus unless the project already uses them.

Speculative architecture increases maintenance burden without immediate value.

See MAS-038 in `_universal/00-master-anti-slop.md`.

## Anti-Patterns

### BE-073 — Catch-All 200 Response

**MUST NOT**

Catching everything and returning 200 is prohibited. The central handler MUST decide the status.

BAD: `catch (e) { res.status(200).json({ error: e.message }) }`.

### BE-074 — Business Logic in Route Handlers

**MUST NOT**

A handler with extensive orchestration, DB calls, and side effects MUST NOT be used. Logic MUST be extracted to a service.

### BE-075 — 500 for Client Errors

**MUST NOT**

A validation error returned as `500` misleads the client and MUST NOT be used.

### BE-076 — Endpoints Without Auth

**MUST NOT**

An admin or protected endpoint without an auth check is security by UI, not security, and MUST NOT be used.

### BE-077 — UI-Only Authorization

**MUST NOT**

Checking auth in the UI only is prohibited. The frontend hides the delete button, but the backend allows the delete for any authenticated user. The backend MUST enforce authorization.

### BE-078 — Missing Content-Type Validation

**MUST NOT**

A JSON endpoint that accepts `text/plain` and parses it as JSON is prohibited. The parser may produce unexpected results.

### BE-079 — 200 for Failed Login

**MUST NOT**

Returning 200 for a failed login is prohibited.

BAD: `res.json({ success: false, message: "invalid credentials" })` with status `200`.

GOOD: `res.status(401).json({ error: "invalid credentials" })`.

### BE-080 — Internal ID Leakage

**MUST NOT**

Returning database primary keys or internal UUIDs when the project uses a different public identifier is prohibited.

### BE-081 — Manual JSON Serialization

**MUST NOT**

Hand-building JSON strings with manual serialization of a hand-built object is prohibited. The framework's serializer MUST be used.

### BE-082 — Accept Header Ignorance

**MUST NOT**

An endpoint that always returns JSON, even when the client sends `Accept: application/xml`, is prohibited. Return `406` if the format is not supported.

### BE-083 — Method-Specific Handler Concern Mixing

**MUST NOT**

`GET /users/create` for creating a user is prohibited. Use `POST /users`.

### BE-084 — Secret in URL

**MUST NOT**

A token in a query string is prohibited. URLs are logged, cached, and leaked via referrer.

### BE-085 — Missing Idempotency Key

**MUST NOT**

A payment or critical write endpoint without an idempotency key is prohibited. A retry creates a duplicate operation.

### BE-086 — Missing CORS Configuration

**MUST NOT**

An API called from a browser without CORS headers, or with a wildcard `Access-Control-Allow-Origin: *` combined with `Allow-Credentials: true`, is prohibited.

### BE-087 — 500 on Missing Required Field

**MUST NOT**

A missing required field is `400`, not `500`.

### BE-088 — Missing Pagination Metadata

**MUST NOT**

A paginated response without a cursor or total count is prohibited. Clients cannot request the next page.

### BE-089 — Long-Running Synchronous Migrations

**MUST NOT**

A migration that locks a table for hours in production is prohibited. Split into batches or run during a maintenance window.

## Response and Resource Completeness

### BE-090 — Complete Error Responses

**MUST**

Every endpoint that can fail MUST return a structured error response. Every endpoint that may return no data MUST return an explicit empty representation. Silent failures and missing error states are prohibited.

See MAS-037 in `_universal/00-master-anti-slop.md`.

### BE-091 — Resource Cleanup

**MUST**

Every connection, file handle, or lock acquired by the assistant's code MUST be released when no longer needed. Unreleased resources cause exhaustion and hangs.

See MAS-040 in `_universal/00-master-anti-slop.md`.

## Response to Violation

When a rule in this file is violated, report:

Violation: BE-{NNN}
Reason: {one-line reason}
Correction: {smallest fix}

For multiple violations, report each rule ID separately.

Do not replace a technical correction with a generic explanation.