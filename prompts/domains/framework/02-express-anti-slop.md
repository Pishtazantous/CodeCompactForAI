---
id: 02-express-anti-slop
title: "Express Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-backend-anti-slop]
category: domain
domain_type: framework
version: 2
---

# Express Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`,
`domains/framework/02-architecture-anti-slop.md`, and
`domains/delivery/02-backend-anti-slop.md`. Rules already covered in
those files are NOT repeated here.

This file covers rules specific to Express: routing, middleware
order, request and response handling, error propagation, and the
patterns that produce silent failures. It does NOT cover
framework-agnostic backend rules (see `02-backend-anti-slop.md`),
architecture rules (see `02-architecture-anti-slop.md`),
TypeScript rules (see `02-typescript-anti-slop.md`), or
NestJS-specific patterns (see `02-nestjs-anti-slop.md`).

Express is minimal by design. It provides routing and middleware
composition and nothing else. The framework's flexibility is a
strength when used with discipline and a liability when used
without. Every rule below reinforces the discipline.

## 1. Stack Assumptions

This layer assumes:

- Express 4.x or 5.x.
- Node.js 18 or later.
- Either JavaScript or TypeScript. If TypeScript, `@types/express`
  is installed.
- Async/await is the primary async style.

### Version Applicability

- **Minimum version**: Express 4.16.
- **Features used in this file that require specific versions**:
  - `express.json()` and `express.urlencoded()` built-in:
    Express 4.16+ (earlier required `body-parser`).
  - Native async error propagation: Express 5.0+.
  - `router.route()` chaining: all 4.x.
  - `trust proxy` per-hop config: 4.17+.
- **If the project uses Express 5**: async errors are caught
  automatically. The `asyncHandler` wrapper is not needed.
- **If the project uses Express 3 or earlier**: this file is not
  applicable. Migrate first.

If the project uses a wrapper framework (NestJS, Fastify, Koa), this
file does not apply. Use the file for that framework instead.

## 2. Framework Lifecycle Contracts

Express enforces six contracts on the developer. Every section below
enforces one or more of these.

### Contract 1: Middleware Runs in Order

Express composes the request pipeline by running middleware in the
order they are mounted. Reordering middleware changes behavior.
Understanding the order is a prerequisite for using Express.

### Contract 2: Request and Response Are Enhanced

Middleware attaches to `req` and `res` and the additions propagate
downstream. A middleware that sets `req.user` makes it available to
every handler mounted after it.

### Contract 3: One Response Per Request

A response is sent exactly once. Sending a second response throws
`ERR_HTTP_HEADERS_SENT`. The handler must return after sending.

### Contract 4: Errors Propagate via `next(err)`

An error thrown synchronously or passed to `next(err)` reaches the
error middleware. In Express 4, async errors are not caught
automatically.

### Contract 5: Error Middleware Has Four Arguments

Express identifies error middleware by arity. A middleware with
`(err, req, res, next)` is an error handler. With `(req, res,
next)`, it is a normal middleware.

### Contract 6: `next()` Continues, `next(err)` Skips

`next()` continues to the next middleware in the chain. `next(err)`
skips all non-error middleware and jumps to the error handler.

## 3. Project Structure

### 3.1 Reference the Project's Layout First

Express has no opinion on folder structure, so every project invents
its own. Before adding a file:

1. Fetch two or three routes from the project.
2. Fetch one middleware.
3. Fetch the app setup (`app.ts`, `server.ts`, or `index.ts`).
4. Match the folder layout, naming, and export style exactly.

Rationale: a second structure in the same project doubles the
cognitive cost of navigation.

### 3.2 The Canonical Layers

A well-structured Express application has:

- **App setup**: creates the app, mounts middleware, mounts routers.
- **Routers**: map paths and methods to handlers.
- **Controllers** (or handlers): validate input, call services,
  format responses.
- **Services**: business logic, no Express types.
- **Middleware**: cross-cutting concerns (auth, logging, error
  handling).

If the project has fewer layers, that is fine. If it has more (a
repositories folder, a validation folder), follow it.

### 3.3 One Router Per Resource

Each resource has its own router file:

```
routes/users.ts
routes/orders.ts
routes/auth.ts
```

BAD: Every route defined in a single `routes.ts`.

GOOD: A router per resource, mounted at a base path.

### 3.4 App Setup Is Separate From Server Startup

`app.ts` exports the configured Express app. `server.ts` imports the
app and calls `app.listen()`. This separation makes testing easier
(supertest uses the app without starting a server).

### 3.5 No Business Logic in Route Files

A route file maps paths to handlers. Business logic lives in
services.

## 4. Routing

### 4.1 Order Matters

Express matches routes in the order they are defined. A catch-all
route (`app.get("*", ...)`) must come last. A 404 handler must come
after all real routes. An error handler must come last of all.

BAD:
```typescript
app.get("*", notFound);
app.use("/api/users", usersRouter);  // never reached
```

### 4.2 Use `Router` for Modular Routes

BAD:
```typescript
app.get("/users", listUsers);
app.post("/users", createUser);
app.get("/users/:id", getUser);
```

GOOD:
```typescript
// routes/users.ts
const router = Router();
router.get("/", listUsers);
router.post("/", createUser);
router.get("/:id", getUser);
export default router;

// app.ts
app.use("/api/v1/users", usersRouter);
```

### 4.3 Route Parameter Validation

Every route parameter (`:id`, `:slug`) is validated before use.

BAD:
```typescript
router.get("/:id", async (req, res) => {
  const user = await db.users.findById(req.params.id);
  // "abc" reaches the database as a string
});
```

GOOD:
```typescript
router.get("/:id", validateParams(idSchema), async (req, res) => {
  const user = await db.users.findById(req.params.id);
});
```

### 4.4 HTTP Method Semantics

- `GET`: read, no side effects, idempotent.
- `POST`: create, not idempotent.
- `PUT`: replace, idempotent.
- `PATCH`: partial update, not necessarily idempotent.
- `DELETE`: remove, idempotent.

Do not use `GET` for mutations. Browsers, caches, and crawlers issue
`GET` without user intent.

### 4.5 Set Status Codes Explicitly

Express defaults to `200` for `res.send` and `res.json`.

BAD:
```typescript
router.post("/", createUser);  // returns 200 by default
```

GOOD:
```typescript
res.status(201).json({ success: true, data: user });
```

### 4.6 Route Ordering for Overlapping Paths

More specific routes come before more general ones:

BAD:
```typescript
router.get("/:id", getUserById);
router.get("/me", getCurrentUser);  // matched as :id = "me"
```

GOOD:
```typescript
router.get("/me", getCurrentUser);
router.get("/:id", getUserById);
```

### 4.7 Use `router.route()` for Method Chains

```typescript
router.route("/:id")
  .get(getUser)
  .patch(updateUser)
  .delete(deleteUser);
```

Rationale: `route()` groups methods on the same path, making the
resource's API visible in one place.

## 5. Middleware

### 5.1 Middleware Order Is Deliberate

Standard order:

1. Request ID / correlation.
2. Logging.
3. Body parsing (`express.json`, `express.urlencoded`).
4. Cookie parsing.
5. CORS.
6. Rate limiting.
7. Authentication.
8. Authorization.
9. Route handlers.
10. 404 handler.
11. Error handler (last, four arguments).

Do not reorder without a reason.

### 5.2 Error Middleware Has Four Arguments

Express identifies error middleware by the number of arguments:

```typescript
app.use((err, req, res, next) => {
  // ...
});
```

Rationale: if the first parameter is renamed or dropped, Express
treats the middleware as normal and never calls it on errors.

### 5.3 Never Send a Response in Two Places

BAD:
```typescript
router.get("/", (req, res) => {
  if (!user) {
    res.status(401).json({ error: "unauthorized" });
    // forgot to return
  }
  res.json({ user });  // second response, error
});
```

GOOD:
```typescript
if (!user) {
  return res.status(401).json({ error: "unauthorized" });
}
res.json({ user });
```

Rationale: sending two responses throws `ERR_HTTP_HEADERS_SENT`. The
second `res.json` fires after the first is on the wire.

### 5.4 Async Errors Need a Wrapper or Express 5

In Express 4, an error thrown from an `async` handler is not caught
by the error middleware.

BAD:
```typescript
router.get("/", async (req, res) => {
  const user = await getUser(req.params.id);  // throws, becomes unhandled
  res.json(user);
});
```

Two valid fixes:

**Option A**: `express-async-errors` installed once.

**Option B**: A wrapper:

```typescript
const asyncHandler = (fn) => (req, res, next) =>
  Promise.resolve(fn(req, res, next)).catch(next);

router.get("/", asyncHandler(async (req, res) => {
  const user = await getUser(req.params.id);
  res.json(user);
}));
```

Rationale: without a wrapper, the error becomes an unhandled
rejection. The response never sends, and the request hangs.

### 5.5 Middleware Applies Only to Routes Defined After It

BAD:
```typescript
router.use(requireAuth);
router.get("/public", publicHandler);  // unexpectedly protected
```

Rationale: `router.use` applies to all routes defined after it in
that router.

### 5.6 Attach to `req` Sparingly

Express allows attaching data to `req`:

```typescript
req.user = user;
```

This is common for auth. But `req` should not become a global bag.

If `req.user` is used, augment the Express type:

```typescript
declare global {
  namespace Express {
    interface Request {
      user?: AuthUser;
    }
  }
}
```

Rationale: `(req as any).user` defeats the type system. A type
augmentation documents the field.

### 5.7 Middleware Order per Router

A middleware mounted on a router applies only to that router's
routes. Use this to scope auth to a subset of routes.

## 6. Request Handling

### 6.1 Validate Everything

`req.body`, `req.query`, `req.params`, and `req.headers` are
attacker-controlled. Validate all of them.

### 6.2 `req.body` Requires `express.json()`

If `express.json()` is not mounted (or is mounted after the route),
`req.body` is `undefined`.

### 6.3 Query Params Are Strings

`req.query.limit` is a string, never a number.

BAD:
```typescript
const limit = req.query.limit - 1;  // NaN
```

GOOD:
```typescript
const limit = Number(req.query.limit ?? "20");
if (!Number.isInteger(limit) || limit <= 0) throw new BadRequest();
```

### 6.4 Never Trust `req.ip` Behind a Proxy

Behind a load balancer, `req.ip` is the proxy's address unless
`app.set("trust proxy", ...)` is configured.

BAD: `app.set("trust proxy", true)` lets any client spoof
`X-Forwarded-For`.

GOOD: `app.set("trust proxy", 1)` for one proxy in front.

### 6.5 Never Read Cookies Without a Parser

Without `cookie-parser`, `req.cookies` is `undefined`.

### 6.6 File Uploads Go Through Multer

Never read the raw body of a multipart request. Use `multer` or the
project's configured parser.

## 7. Response Handling

### 7.1 Always Return After Sending

Covered in 5.3. Repeating because it is the most common Express bug.

### 7.2 Do Not Mix `res.send`, `res.json`, `res.end`

Pick one per route. `res.json` is the default for APIs. Never call
two of them.

### 7.3 Consistent Response Shape

Every successful response has the same shape. Every error response
has the same shape. See `02-backend-anti-slop.md` section 3.1.

### 7.4 Headers Set Before Body

Once `res.send` or `res.json` is called, headers are flushed.

BAD:
```typescript
res.json({ data });
res.setHeader("X-Custom", "value");  // too late
```

### 7.5 Streaming for Large Responses

For large files, use `res.sendFile` or `res.download`. For computed
streams, use `res.write` and `res.end`.

Rationale: loading a 500 MB file into memory crashes the process.

### 7.6 `res.locals` for Request-Scoped Data

`res.locals` is designed for data that templates and downstream
middleware need. Use it instead of adding more fields to `req`.

## 8. Error Handling

### 8.1 One Central Error Handler

The app has exactly one error middleware, mounted last:

```typescript
app.use((err, req, res, next) => {
  const status = err.status ?? 500;
  const message = err.expose ? err.message : "Internal server error";
  logger.error({ err, requestId: req.id }, "request failed");
  res.status(status).json({ success: false, error: { message } });
});
```

Rationale: individual routes never send a 500 directly. The handler
maps every error to a consistent response.

### 8.2 Typed Errors

Define the project's error classes and throw them:

```typescript
throw new NotFoundError("User");
throw new ValidationError("email", "invalid format");
```

The central handler maps them to status codes.

### 8.3 Never Expose Stack Traces

In production, the response has no stack trace. Stack traces go to
logs only.

### 8.4 Log Once, at the Top

The central handler logs. Individual middleware do not log-and-
rethrow.

### 8.5 404 Handler

A 404 handler is mounted after all routes:

```typescript
app.use((req, res) => {
  res.status(404).json({ success: false, error: { message: "Not found" } });
});
```

Rationale: without it, unmatched routes fall through to the error
handler or produce a default Express 404 HTML page.

### 8.6 Graceful Shutdown

On `SIGTERM`:

1. Stop accepting new requests.
2. Wait for in-flight requests to finish (with a timeout).
3. Close database and cache connections.
4. Exit.

```typescript
process.on("SIGTERM", () => {
  server.close(async () => {
    await db.close();
    process.exit(0);
  });
});
```

Do not call `process.exit(0)` without closing the server.

## 9. Security Middleware

### 9.1 Helmet

`helmet()` sets security headers. It is enabled in every Express app
that serves HTTP.

### 9.2 CORS With Explicit Origins

BAD:
```typescript
app.use(cors({ origin: "*" }));
```

GOOD:
```typescript
app.use(cors({
  origin: ["https://app.example.com", "https://admin.example.com"],
  credentials: true,
}));
```

Rationale: `origin: "*"` with `credentials: true` is rejected by
browsers, but a misconfigured proxy may still serve it.

### 9.3 Rate Limiting on Sensitive Endpoints

`express-rate-limit` or equivalent on:

- Login endpoints.
- Password reset.
- Registration.
- Any endpoint that sends an email or SMS.

### 9.4 Body Size Limit

`express.json({ limit: "100kb" })` by default. Never unbounded.

### 9.5 `express.urlencoded` With `extended: false`

```typescript
app.use(express.urlencoded({ extended: false, limit: "10kb" }));
```

Rationale: `extended: true` allows nested objects, which enables
prototype pollution attacks.

### 9.6 `express.static` Serves a Specific Directory

BAD: `app.use(express.static("."))` serves `package.json`, `.env`,
and every source file.

GOOD: `app.use(express.static("public"))`.

## 10. Logging and Observability

### 10.1 Request ID

Every request has a request ID. It is generated if missing, attached
to the request, added to the response headers, and included in every
log line.

```typescript
import { randomUUID } from "node:crypto";

app.use((req, res, next) => {
  req.id = req.header("x-request-id") ?? randomUUID();
  res.setHeader("x-request-id", req.id);
  next();
});
```

### 10.2 Structured Logging

Log in JSON, not in string interpolation. Include `requestId`,
`userId`, `method`, `path`, `status`, `durationMs`.

### 10.3 Do Not Log the Body

A request body may contain passwords, tokens, or PII. Log the shape
(keys), not the values.

### 10.4 Response Time

Log the response time for every request. It is the cheapest
observability signal and the most useful.

## 11. TypeScript Integration

### 11.1 Augment Express Types

```typescript
// types/express.d.ts
declare global {
  namespace Express {
    interface Request {
      id: string;
      user?: AuthUser;
    }
  }
}

export {};
```

Rationale: without augmentation, `req.user` is a type error or a
cast.

### 11.2 Typed Request Handlers

BAD:
```typescript
router.get("/:id", (req: any, res: any) => { /* ... */ });
```

GOOD:
```typescript
import type { Request, Response } from "express";

router.get("/:id", (req: Request<{ id: string }>, res: Response) => {
  // req.params.id is string
});
```

### 11.3 No `any` in Handler Signatures

`any` defeats the type system for the entire handler.

## 12. Anti-Patterns

### 12.1 Missing `return` After `res.send`

Covered in 5.3.

### 12.2 `app.use` Without a Path

BAD:
```typescript
app.use(authMiddleware);  // runs on every request
```

If `authMiddleware` does work on every request (parses tokens,
queries the database), it slows down every route, including public
ones.

### 12.3 `app.use` as a Route

`app.use` matches any method and any path prefix. If the intent is
`GET /specific`, use `app.get`.

### 12.4 Async Errors Swallowed

Covered in 5.4.

### 12.5 Order-Dependent Route Bugs

Routes like `/users/:id` and `/users/me` in the wrong order.

### 12.6 Middleware That Never Calls `next`

BAD:
```typescript
app.use((req, res, next) => {
  if (!req.user) {
    res.status(401).end();
    // forgot next()
  }
});
```

Every middleware either sends a response or calls `next()`.

### 12.7 `next()` After Sending a Response

BAD:
```typescript
res.json({ data });
next();  // continues the chain after response sent
```

Rationale: `next()` after `res.json` can cause "headers already
sent" errors downstream.

### 12.8 Error Handler in the Middle

An error handler mounted before some routes only catches errors from
routes defined before it. Mount it last.

### 12.9 Error Handler With Three Arguments

Covered in 5.2.

### 12.10 `body-parser` as a Separate Dependency

`express.json()` and `express.urlencoded()` are built into Express
4.16+. Do not add `body-parser` unless the project requires it for
legacy reasons.

### 12.11 Trusting `req.query` Types

Covered in 6.3.

### 12.12 `res.send` on Objects

`res.send({ obj })` sets `Content-Type: text/html` in some cases.
Use `res.json` for JSON.

### 12.13 CORS Wildcard With Credentials

Covered in 9.2.

### 12.14 Missing Body Parser

A `POST` route that reads `req.body` without `express.json()`
mounted. `req.body` is `undefined`.

### 12.15 `express.static` Serving the Project Root

Covered in 9.6.

### 12.16 Synchronous Blocking in a Handler

BAD: `fs.readFileSync` or a long CPU loop inside a handler.

Rationale: Node.js is single-threaded. A synchronous operation
blocks the entire event loop for all concurrent requests.

### 12.17 Response Sent, Code Continues

Covered in 5.3.

### 12.18 Nested Routers With Duplicate Middleware

`app.use("/api", auth)` and `app.use("/api/v1", auth)` run `auth`
twice on the same request path.

### 12.19 Error Object as a Response

BAD:
```typescript
res.status(500).json({ error: err });
```

This serializes the entire error object, including stack traces.

GOOD:
```typescript
res.status(500).json({ error: { message: "Internal server error" } });
```

### 12.20 `next()` Called Twice

BAD:
```typescript
if (!user) {
  next(new Error("no user"));
}
next();  // called again
```

Rationale: calling `next()` twice runs the handler chain twice,
producing duplicate responses or double side effects.

### 12.21 Middleware Order Confusion

Logging middleware mounted after auth, so unauthenticated requests
are not logged. Move logging first.

### 12.22 `app.set("trust proxy", true)`

Covered in 6.4.

### 12.23 Route Handler That Reads `req.body` Before Parsing

Covered in 6.2.

### 12.24 Session Middleware Without a Store

`express-session` with the default MemoryStore. The store is not
designed for production: it leaks memory and does not survive
restart.

### 12.25 Error Handler That Does Not Log

An error handler that returns 500 but does not log the error. The
error is invisible.

### 12.26 Missing `Content-Type` Handling

A JSON endpoint that accepts any `Content-Type` and parses the body
anyway. Malformed input reaches the handler.

### 12.27 `req.params` Read Without Validation

Covered in 4.3.

### 12.28 No Health Endpoint

A container without `/health` is restarted by Kubernetes even when
it is running fine (or not restarted when it is broken).

### 12.29 No Request Timeout

A request that hangs holds a connection indefinitely.

### 12.30 CORS Configuration in Every Route

Duplicating CORS headers per route instead of using the `cors`
middleware once.

### 12.31 Manual JSON Serialization

Building JSON strings with `JSON.stringify` and `res.send` instead
of `res.json`.

### 12.32 Wildcard Route Before Specific Routes

Covered in 4.1.

### 12.33 Session Cookie Without `httpOnly`

A session cookie readable by JavaScript is vulnerable to XSS.

### 12.34 Missing `SameSite` on Session Cookie

A session cookie without `SameSite` is sent with cross-site
requests, enabling CSRF.

### 12.35 Body Parser Mounted After Routes

`express.json()` mounted after a router. The router's POST routes
see `req.body` as `undefined`.

### 12.36 Error Handler That Swallows

BAD:
```typescript
app.use((err, req, res, next) => {
  res.status(500).json({ error: "error" });
  // err never logged
});
```

### 12.37 Middleware That Modifies Global State

A middleware that mutates a module-level variable. The mutation
persists across requests and causes non-deterministic bugs.

### 12.38 No Rate Limiting on Login

An unprotected login endpoint allows unlimited password guesses.

### 12.39 Route That Returns HTML Error Pages

BAD: `res.status(500).send("<h1>Error</h1>")`.

GOOD: `res.status(500).json({ error: { message: "..." } })`.

Rationale: an API client parsing JSON fails on HTML.

### 12.40 Missing `trust proxy` Behind a Load Balancer

Behind a load balancer without `trust proxy`, `req.ip` is the
proxy's IP. Rate limiting by IP affects every user together.

## 13. Response to Violation

If a previous response violated a rule here:

```
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

No justification. No apology paragraph. Fix and move on.
