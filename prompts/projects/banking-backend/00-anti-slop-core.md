---
id: 00-anti-slop-core
title: "Core Anti-Slop Layer - banking-backend"
lang: en
depends_on: [00-master-anti-slop, 02-backend-anti-slop, 02-typescript-anti-slop]
category: project
version: 1
---

# Core Anti-Slop Layer - banking-backend

Layered under `_universal/00-master-anti-slop.md` and the relevant
domain layers. Universal and domain rules are NOT repeated here.

This file contains ONLY rules specific to this repository: its tools,
its patterns, its known anti-patterns, and the reading order that must
be respected before editing any file.

Fill in the sections marked `<!-- FILL IN -->` before the first AI
session on this project. Incomplete sections weaken the layer.

## 1. This Repository's Tools

The tools below are the ones every new piece of code must use. Never
introduce a second one for the same purpose.

### 1.1 Validation

<!-- FILL IN: which library validates external input?
     Examples: zod, joi, express-validator, class-validator, yup.
     Also: where do schemas live? (validators/, schemas/, next to routes) -->

- Library:
- Schema location:
- Naming convention for schemas (e.g. `createUserSchema`):
- Validation error shape:

### 1.2 Error Handling

<!-- FILL IN: what is the central error handler? What error classes exist? -->

- Central error handler:
- Error base class:
- Subclasses:
- Response shape for errors:
- HTTP status code mapping:

### 1.3 Logging

<!-- FILL IN: which logger is used and how is it accessed? -->

- Logger library:
- How it is imported:
- Log levels used in this project:
- Structured fields required (e.g. `requestId`, `userId`):

### 1.4 Database

<!-- FILL IN: which ORM / query builder / driver? -->

- Database engine:
- ORM / query builder:
- Migration tool:
- Migration directory:
- Naming convention for tables and columns:
- Connection pooling configuration:

### 1.5 Authentication and Authorization

<!-- FILL IN: how does auth work in this project? -->

- Auth mechanism (JWT / session / API key):
- Where tokens are issued:
- Where tokens are verified:
- Middleware name and location:
- How the current user is accessed in a request:
- How roles are checked:

### 1.6 Testing

<!-- FILL IN: which test framework and how are tests structured? -->

- Test framework:
- Test file location and naming:
- How to run tests:
- Mocking conventions:
- Test data factories:

### 1.7 Configuration

<!-- FILL IN: how does the app read configuration? -->

- Config module location:
- How env vars are accessed:
- Required env vars list location:
- `.env.example` location:

### 1.8 API Documentation

<!-- FILL IN: how is the API documented? -->

- OpenAPI / Swagger setup:
- Where endpoint docs live (JSDoc, separate YAML, generated):
- Documentation generation command:

## 2. This Repository's Patterns

### 2.1 Folder Layout

<!-- FILL IN: what is the folder structure?
     Example:
       src/
         routes/         -- HTTP route definitions
         controllers/    -- request handling, delegates to services
         services/       -- business logic
         repositories/   -- data access
         models/         -- domain models
         schemas/        -- validation schemas
         middleware/     -- express middleware
         utils/          -- shared helpers
         types/          -- shared types
-->

- Route definitions:
- Request handlers:
- Business logic:
- Data access:
- Domain types:
- Shared utilities:

### 2.2 Naming Conventions

<!-- FILL IN: exact naming rules for files, classes, functions, variables. -->

- File names:
- Class names:
- Function names:
- Variable names:
- Constants:
- Types and interfaces:
- Database tables:
- Database columns:
- Environment variables:

### 2.3 Import Style

<!-- FILL IN: absolute vs relative imports, aliases, ordering. -->

- Absolute imports:
- Aliases (e.g. `@/`):
- Import order (std, external, internal, relative):
- Type-only imports:

### 2.4 Response Shape

<!-- FILL IN: what does a successful response look like? -->

- Success response shape:
- Error response shape:
- Pagination shape:
- List response shape:
- Single-item response shape:

### 2.5 Async and Error Flow

<!-- FILL IN: how is async error handling done in controllers? -->

- How are async handler errors caught (express-async-handler,
  try/catch, wrapper)?
- How are database errors translated to domain errors?
- How are validation errors surfaced to the client?

### 2.6 Service Layer Contract

<!-- FILL IN: what is the contract for service functions? -->

- Do services throw or return Result?
- Do services return domain models or DTOs?
- Do services know about HTTP (req, res) or are they framework-
  agnostic?
- How are transactions handled in services?

## 3. Known Anti-Patterns in This Repo

<!-- FILL IN as discovered. Each entry is a pattern that exists in
     old code and must NOT be propagated to new code. If you touch an
     old file with one of these, migrate it or report it. -->

- <!-- Example:
  Old controllers use `res.json({ data, success })` without a `message`
  field. New controllers must use the full shape
  `{ success, data, message }`.
-->

- <!-- Example:
  Some services call `console.log` directly. New services must use
  the logger from `src/utils/logger.ts`.
-->

- <!-- Example:
  Older migrations use raw SQL. New migrations use the ORM's schema
  builder. -->

## 4. Required Reading Before Editing

Before editing any file in this repository, fetch in this order:

1. The file itself.
2. The file's tests, if any.
3. One similar file already considered "good" in the repo (ask the
   user if unsure which one).
4. Shared types and utility modules the file depends on.

Fetching order matters. Reading the file first prevents you from
assuming its shape from the manifest.

## 5. Constraints Specific to This Repository

<!-- FILL IN: any constraints that are unique to this project. -->

- Compliance requirements (e.g. PCI-DSS, GDPR, internal audit):
- Performance budget (e.g. p99 latency target):
- Supported runtimes and versions:
- Deployment target:
- Third-party services that must not be replaced:

## 6. Response to Violation

If a previous response violated a rule here:
In the previous response, [specific rule] was violated. Correction:
[corrected code]

text

No justification. No apology paragraph. Fix and move on.