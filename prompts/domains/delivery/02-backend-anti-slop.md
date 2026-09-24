---
id: 02-backend-anti-slop
title: "Backend Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: delivery
version: 1
---

# Backend Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
security anti-patterns, output format) are NOT repeated here.

This file covers rules specific to backend services: API contracts,
validation, error handling, persistence, authentication, logging,
configuration, migrations, and resource protection.

## 1. Stack Assumptions

This layer applies to backend services regardless of language or
framework. Common stacks include:

- Node.js + Express / Fastify / NestJS + TypeScript
- Python + FastAPI / Django / Flask
- Go + Gin / Fiber / Echo
- Rust + Axum / Actix
- Ruby + Rails
- PHP + Laravel
- Java / Kotlin + Spring Boot
- C# + ASP.NET Core

Framework-specific rules live in `domains/framework/`. Language-specific
rules live in `domains/language/`. This file covers only what is common
to all backend services.

## 2. API Contract Discipline

### 2.1 No Invented Endpoints

If a task requires a new endpoint, confirm before writing:

- HTTP method
- Path (including version prefix, e.g. `/api/v1/...`)
- Request body shape
- Query and path parameters
- Response shape
- Success and error status codes

### 2.2 No Invented Fields

If a type, interface, or schema is referenced but not seen, fetch its
definition. If it does not exist, ask. Never silently create a field.

### 2.3 Response Shape Must Match the Project

If the project uses `{ success, data, message }`, every new endpoint
returns that shape. Never `{ result }`, never `{ error }`, never a bare
object. If unsure, fetch two existing endpoints and copy the shape.

### 2.4 Status Code Convention

Match what similar endpoints in the project use. Common conventions:

- POST that creates a resource: 201
- POST that does not create: 200
- Validation error: 400
- Missing or invalid auth: 401
- Insufficient permissions: 403
- Resource not found: 404
- Conflict (duplicate, state mismatch): 409
- Unprocessable entity (semantic error): 422
- Rate limit exceeded: 429
- Server error: 500

If the project uses different codes, follow the project, not this list.

### 2.5 Versioning

Do not introduce a new API version prefix without explicit instruction.
If a breaking change is required, propose a versioning strategy and wait
for approval before writing code.

## 3. Input Validation

- Validate every external input: body, query, params, headers, cookies.
- Never access `req.body.x` (or equivalent) in business logic without
  prior validation.
- Use the project's existing validator: `zod`, `joi`,
  `express-validator`, `class-validator`, `pydantic`, `marshmallow`, or
  equivalent. Do not introduce a second validator.
- Validation schemas live next to the route or in the project's
  established `validators/` or `schemas/` directory. Match the project's
  layout, do not invent one.
- Every validation rule has a clear reason. No blanket "validate
  everything" patterns that add noise without protection.
- Validation error messages are user-facing strings and follow the
  project's language convention (see section 7.4 of `00-master-anti-slop.md`).
- Reject unknown fields explicitly when the project's pattern does so
  (strict schemas). Otherwise, document why unknown fields are allowed.

## 4. Error Handling

- Use the project's central error handler. Never
  `res.status(500).send(...)` (or equivalent) from inside a route
  handler.
- Throw typed errors (`AppError`, `NotFoundError`, `ValidationError`) if
  the project defines them. Otherwise throw the language's native error
  and let the central handler catch it.
- Never swallow errors silently. `catch { }` with an empty body is
  forbidden.
- Never expose stack traces, SQL errors, file paths, or internal
  identifiers to the client.
- Every thrown error must be logged (see section 7).
- Distinguish operational errors (bad input, missing resource) from
  programmer errors (null dereference, undefined function). Handle them
  differently.

## 5. Database and Persistence

- Use the project's existing data-access layer. Do not add a second ORM
  or query builder.
- Every write operation is either idempotent or wrapped in a transaction
  if the project's pattern requires it.
- Never write raw SQL unless the project already does.
- Never `SELECT *` in production queries. List columns explicitly.
- Never issue N+1 queries. If a loop contains a database call, use a
  batch fetch or a join.
- Never log query results containing PII.
- All schema changes go through the project's migration system (see
  section 9).

## 6. Authentication and Authorization

- Use the project's existing auth middleware. Never re-implement it.
- Never hard-code a user ID, role, or token.
- Read identity from `req.user`, `req.session`, or the project's
  equivalent. Never from `req.query.userId` or a body field.
- Never bypass auth middleware in production code.
- Authorization checks (role, ownership) are explicit per route. Do not
  rely on a global middleware alone.
- Return 401 for missing or invalid credentials, 403 for valid
  credentials without permission. Do not blur the two.

## 7. Logging

- Use the project's logger (`pino`, `winston`, `zap`, `loguru`,
  `structlog`, or equivalent). Do not introduce a second logger.
- Never `console.log` (or `print`) in final code.
- Never log: secrets, tokens, passwords, full request bodies containing
  PII, or full database row dumps.
- Log levels:
  - `error`: 5xx responses, unhandled exceptions
  - `warn`: 4xx that indicates a problem (invalid token, rate limit hit)
  - `info`: successful side effects (user created, payment processed)
  - `debug`: flow details, only in development
- Logs must include enough context to debug: request ID, user ID,
  endpoint, outcome. Use the project's request context, not globals.

## 8. Async and Concurrency

- Never `await` inside a `forEach`. Use `for...of` or `Promise.all`.
- Never ignore a returned promise without explicit reasoning.
- Handle `Promise.all` rejections. Partial success is usually a bug.
- Never fire-and-forget a write operation.
- Set timeouts on all external calls (HTTP, database, cache).
- Never share mutable state between concurrent requests without
  synchronization.

## 9. Environment and Configuration

- Never hard-code config values: URLs, ports, credentials, feature
  flags.
- Read configuration through the project's config module, not directly
  from `process.env` (or equivalent) in business logic.
- Every new environment variable must be:
  - Added to `.env.example` (or equivalent)
  - Documented in the project's configuration reference
  - Listed in the response's "Next Steps"
- Never commit `.env`, `.env.local`, or files containing secrets.
- Validate required environment variables at startup, not at first use.

## 10. Migrations and Schema Changes

- Every schema change goes through a migration. No manual database
  edits.
- Every migration is either reversible or documented as intentionally
  irreversible with a reason.
- Never drop a column or table without explicit confirmation.
- Never mix schema change and data backfill in a single migration unless
  the project's pattern allows it.
- Migrations must be safe to run against a production-sized dataset.
  Beware of `ALTER TABLE` operations that lock.

## 11. Rate Limiting and Resource Protection

- Every public endpoint is behind the project's rate limiter.
- Every expensive operation (search, export, batch) has explicit
  limits: max page size, max batch size, max execution time.
- Never return unbounded lists. Use the project's pagination.
- Never allow a single request to consume unbounded memory or CPU.
- Reject requests with payloads larger than the configured limit before
  parsing the body.

## 12. API Documentation

- When adding or changing an endpoint, update the OpenAPI or equivalent
  spec in the same response.
- Match the project's existing documentation style: JSDoc `@openapi`
  blocks, separate YAML files, or auto-generated types.
- Never leave an endpoint documented with stale request or response
  shapes.
- Descriptions and examples follow the project's user-facing language
  convention.

## 13. Domain-Specific Anti-Patterns

### 13.1 Trusting the Client

BAD: Using `req.body.role` to decide whether the user is an admin.
GOOD: Reading the role from the authenticated session, ignoring any
client-provided role.

### 13.2 Catching Everything, Returning 200

BAD: `try { ... } catch (e) { res.status(200).json({ error: e.message }) }`
GOOD: Let the central handler decide the status code. Do not convert
errors into 200s.

### 13.3 Business Logic in Route Handlers

BAD: A route handler with 200 lines of orchestration, DB calls, and
side effects.
GOOD: Route handler validates input, calls a service function, returns
the result. Business logic lives in the service layer.

### 13.4 Silent Schema Drift

BAD: Adding a field to a model without a migration, expecting the ORM
to sync.
GOOD: Every schema change has a migration file. The database schema in
production matches the migration history.

### 13.5 Global Mutable State

BAD: A module-level `let currentUser` set by middleware.
GOOD: Request-scoped context passed explicitly through function
arguments or the framework's request object.

### 13.6 Injecting Loggers via Imports of `console`

BAD: `console.log("user:", user)` scattered across files.
GOOD: A single logger injected or imported from the project's logging
module, with structured fields.

### 13.7 Returning Internal IDs

BAD: Exposing the database primary key as the public identifier when
the project uses UUIDs or slugs elsewhere.
GOOD: Match the project's public-identifier convention.

### 13.8 Numeric Status Codes Without Meaning

BAD: Returning 200 with `{ success: false }` for a failed operation.
GOOD: Return the correct HTTP status (4xx for client errors, 5xx for
server errors), and let the body describe the failure.

## 14. Response to Violation

If a previous response violated a rule here:
In the previous response, [specific rule] was violated. Correction:
[corrected code]



No justification. No apology paragraph. Fix and move on.