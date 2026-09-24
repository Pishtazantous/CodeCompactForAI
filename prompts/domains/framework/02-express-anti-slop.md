---
id: 02-express-anti-slop
title: "Express Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-backend-anti-slop]
category: domain
domain_type: framework
version: 1
---

# Express Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`,
`domains/framework/02-architecture-anti-slop.md`, and
`domains/delivery/02-backend-anti-slop.md`. Universal, architectural,
and general backend rules are NOT repeated here.

This file covers rules specific to Express: routing, middleware,
request and response handling, error propagation, and the patterns
that produce silent failures in Express applications.

## 1. Stack Assumptions

This layer assumes:

- Express 4.x or 5.x.
- Node.js 18 or later.
- Either JavaScript or TypeScript. If TypeScript, the project has
  `@types/express` installed.
- Async/await is used for asynchronous handlers.

If the project uses a wrapper framework (NestJS, Fastify, Koa), this
file does not apply. Use the file for that framework instead.

## 2. Project Structure

### 2.1 Reference the Project's Layout First

Express has no opinion on folder structure, so every project invents
its own. Before adding a file:

1. Fetch two or three routes from the project.
2. Fetch one middleware.
3. Fetch the app setup (`app.ts`, `server.ts`, or `index.ts`).
4. Match the folder layout, naming, and export style exactly.

If the project organizes routes in `routes/`, `controllers/`, and
`services/`, keep that organization. Do not introduce a `features/`
folder with a different structure.

### 2.2 The Canonical Layers

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

### 2.3 One Router Per Resource

Each resource has its own router file:
routes/users.ts
routes/orders.ts
routes/auth.ts

text

The router is mounted at a base path in the app setup:

```typescript
app.use("/api/v1/users", usersRouter);
```
Do not define every route in a single routes.ts.

3. Routing
3.1 Order Matters
Express matches routes in the order they are defined. A catch-all
route (app.get("*", ...)) must come last. A 404 handler must come
after all real routes. An error handler must come last of all.

BAD:

typescript
app.get("*", notFound);
app.use("/api/users", usersRouter);  // never reached
3.2 Use Router for Modular Routes
BAD:

typescript
app.get("/users", listUsers);
app.post("/users", createUser);
app.get("/users/:id", getUser);
app.patch("/users/:id", updateUser);
// in the same file as the app setup
GOOD:

typescript
// routes/users.ts
const router = Router();
router.get("/", listUsers);
router.post("/", createUser);
router.get("/:id", getUser);
router.patch("/:id", updateUser);
export default router;

// app.ts
app.use("/api/v1/users", usersRouter);
3.3 Route Parameter Validation
Every route parameter (:id, :slug) is validated before use.
A user-supplied :id reaches the database as NaN, "undefined",
or a SQL injection attempt otherwise.

typescript
router.get("/:id", validateParams(idSchema), getUser);
3.4 HTTP Method Semantics
GET: read, no side effects, idempotent.

POST: create, not idempotent.

PUT: replace, idempotent.

PATCH: partial update, not necessarily idempotent.

DELETE: remove, idempotent.

Do not use GET for mutations. Browsers, caches, and crawlers issue
GET without user intent.

3.5 Response Codes
Express defaults to 200 for res.send and res.json. Set the
status explicitly when it is not 200.

BAD:

typescript
router.post("/", createUser);  // returns 200 by default
GOOD:

typescript
router.post("/", createUser);
// inside createUser:
res.status(201).json({ ... });
See domains/delivery/02-backend-anti-slop.md section 2.4 for the
full status code convention.

3.6 Route Ordering for Overlapping Paths
More specific routes come before more general ones:

typescript
router.get("/me", getCurrentUser);       // before /:id
router.get("/:id", getUserById);
Otherwise /me is matched as an :id.

4. Middleware
4.1 Middleware Order
Express middleware runs in the order it is mounted. Standard order:

Request ID / correlation

Logging

Body parsing (express.json, express.urlencoded)

Cookie parsing

CORS

Rate limiting

Authentication

Authorization

Route handlers

404 handler

Error handler (last, four arguments)

Do not reorder without a reason.

4.2 Error Middleware Has Four Arguments
Express identifies error middleware by the number of arguments:

typescript
app.use((err, req, res, next) => {
  // ...
});
The first parameter is err. If you rename it or drop it, Express
treats the middleware as normal and never calls it on errors.

4.3 Never Send a Response in Two Places
BAD:

typescript
router.get("/", (req, res) => {
  if (!user) {
    res.status(401).json({ error: "unauthorized" });
    // forgot to return
  }
  res.json({ user });  // second response, error
});
Always return after sending a response.

typescript
if (!user) {
  return res.status(401).json({ error: "unauthorized" });
}
res.json({ user });
4.4 next(err) for Errors, next() for Pass-Through
next() passes to the next middleware.

next(err) passes to the error handler.

next("route") skips to the next matching route.

Do not call next(err) after sending a response. Do not call
res.send after next(err).

4.5 Async Errors Need a Wrapper or Express 5
In Express 4, an error thrown from an async handler is not caught
by the error middleware. It becomes an unhandled rejection.

BAD:

typescript
router.get("/", async (req, res) => {
  const user = await getUser(req.params.id);  // throws
  res.json(user);
});
Two valid fixes:

Option A: express-async-errors installed once:

typescript
import "express-async-errors";
Option B: A wrapper:

typescript
const asyncHandler = (fn) => (req, res, next) =>
  Promise.resolve(fn(req, res, next)).catch(next);

router.get("/", asyncHandler(async (req, res) => {
  const user = await getUser(req.params.id);
  res.json(user);
}));
Express 5 handles async errors natively. Match the project's version.

4.6 Middleware Applies to Routes Defined After It
BAD:

typescript
router.use(requireAuth);
router.get("/public", publicHandler);  // unexpectedly protected
Order middleware deliberately. router.use applies to all routes
defined after it on that router.

4.7 Attach to req Sparingly
Express allows attaching data to req:

typescript
req.user = user;
This is common for auth. But req should not become a global bag.
Prefer a request-scoped context module or res.locals for
non-essential data.

If you use req.user, augment the Express type:

typescript
declare global {
  namespace Express {
    interface Request {
      user?: AuthUser;
    }
  }
}
Do not use (req as any).user.

5. Request Handling
5.1 Validate Everything
req.body, req.query, req.params, and req.headers are
attacker-controlled. Validate all of them with the project's
validator (see domains/delivery/02-backend-anti-slop.md section 3).

5.2 req.body Requires express.json()
If express.json() is not mounted (or is mounted after the route),
req.body is undefined. Check the mount order before debugging
a body issue.

5.3 Query Params Are Strings
req.query.limit is a string, never a number, unless a validation
layer parsed it. Never limit - 1 on a string.

5.4 Never Trust req.ip Behind a Proxy
Behind a load balancer, req.ip is the proxy's address unless
app.set("trust proxy", ...) is configured. Trust only as many
proxies as exist in the deployment.

5.5 Never Read Cookies Without a Parser
Without cookie-parser, req.cookies is undefined. Check the
middleware before debugging.

5.6 File Uploads Go Through Multer or an Equivalent
Never read the raw body of a multipart request. Use multer or the
project's configured parser. See 02-backend-anti-slop.md section 5
for upload validation rules.

6. Response Handling
6.1 Always Return After Sending
Covered in 4.3. Repeating because it is the most common Express bug.

6.2 Do Not Mix res.send, res.json, res.end
Pick one per route. res.json is the default for APIs. Never call
two of them.

6.3 Consistent Response Shape
Every successful response has the same shape. Every error response
has the same shape. See 02-backend-anti-slop.md section 2.3.

6.4 Headers Set Before Body
Once res.send or res.json is called, headers are flushed.
res.setHeader after that throws or is ignored.

6.5 res.status() Returns res
Chaining works:

typescript
res.status(201).json({ ... });
But do not chain side effects. Pick one style per project.

6.6 Streaming for Large Responses
For large files, res.sendFile or res.download. For computed
streams, res.write and res.end. Never load a 500MB file into
memory.

7. Error Handling
7.1 One Central Error Handler
The app has exactly one error middleware, mounted last:

typescript
app.use((err, req, res, next) => {
  const status = err.status ?? 500;
  const message = err.expose ? err.message : "Internal server error";
  logger.error({ err, requestId: req.id }, "request failed");
  res.status(status).json({ success: false, error: { message } });
});
Individual routes never send a 500 directly.

7.2 Typed Errors
Define the project's error classes and throw them:

typescript
throw new NotFoundError("User");
throw new ValidationError("email", "invalid format");
The central handler maps them to status codes.

7.3 Never Expose Stack Traces
In production, the response has no stack trace. Stack traces go to
logs only.

7.4 Log Once, at the Top
Covered in 02-backend-anti-slop.md section 4 and 7. The central
handler logs. Individual middleware do not log-and-rethrow.

7.5 404 Handler
A 404 handler is mounted after all routes:

typescript
app.use((req, res) => {
  res.status(404).json({ success: false, error: { message: "Not found" } });
});
Without it, unmatched routes fall through to the error handler or
produce a default Express 404 HTML page.

7.6 Graceful Shutdown
On SIGTERM:

Stop accepting new requests.

Wait for in-flight requests to finish (with a timeout).

Close the database connections.

Exit.

typescript
process.on("SIGTERM", async () => {
  server.close(async () => {
    await db.close();
    process.exit(0);
  });
});
Do not call process.exit(0) on SIGTERM without closing the server.

8. Security Middleware
8.1 Helmet
helmet() sets security headers. It is enabled in every Express app
that serves HTTP. Do not disable it "for a moment".

8.2 CORS
Configure CORS with an explicit allowlist:

BAD:

typescript
app.use(cors({ origin: "*" }));
GOOD:

typescript
app.use(cors({
  origin: ["https://app.example.com", "https://admin.example.com"],
  credentials: true,
}));
Never origin: true (which reflects any origin) with
credentials: true.

8.3 Rate Limiting
express-rate-limit or the project's equivalent on:

Login endpoints

Password reset

Registration

Any endpoint that sends an email or SMS

Public APIs

See domains/concern/02-security-critical-anti-slop.md section 3.4.

8.4 Body Size Limit
express.json({ limit: "100kb" }) by default. A larger limit only
when the endpoint genuinely receives large JSON. Never unbounded.

8.5 express.urlencoded Limits
express.urlencoded({ extended: false, limit: "10kb" }). The
extended: false prevents prototype pollution through nested objects.

8.6 Trust Proxy
Only enable if there is a proxy in front:

typescript
app.set("trust proxy", 1);  // one proxy in front
Do not trust proxy with true. It lets any client spoof X-Forwarded-For.

9. Logging and Observability
9.1 Request ID
Every request has a request ID. It is generated if missing, attached
to the request, added to the response headers, and included in every
log line.

typescript
import { randomUUID } from "node:crypto";

app.use((req, res, next) => {
  req.id = req.header("x-request-id") ?? randomUUID();
  res.setHeader("x-request-id", req.id);
  next();
});
9.2 Structured Logging
Log in JSON, not in string interpolation. Include requestId,
userId, method, path, status, durationMs.

Use pino, winston, or the project's logger. Never console.log
in production.

9.3 Do Not Log the Body
A request body may contain passwords, tokens, or PII. Log the shape
(keys, not values) at most. Never the full body.

9.4 Response Time
Log the response time for every request. It is the cheapest
observability signal and the most useful.

10. Express-Specific Anti-Patterns
10.1 Missing return After res.send
Covered in 4.3 and 6.1. The single most common Express bug.

10.2 app.use Without a Path
BAD:

typescript
app.use(authMiddleware);  // runs on every request
If authMiddleware does work on every request (parses tokens,
queries the database), it slows down every route, including public
ones.

Mount it on the routers that need it:

typescript
app.use("/api/v1", authMiddleware, apiRouter);
10.3 app.use((req, res, next) => { ... }) as a Route
app.use matches any method and any path prefix. If the intent is
GET /specific, use app.get.

10.4 Async Errors Swallowed
Covered in 4.5. Express 4 does not catch async throws.

10.5 Order-Dependent Route Bugs
Routes like /users/:id and /users/me in the wrong order. Or a
catch-all that swallows everything. Express matches in definition
order.

10.6 Middleware That Never Calls next
BAD:

typescript
app.use((req, res, next) => {
  if (!req.user) {
    res.status(401).end();
    // forgot next()
  }
  // forgot next() on success too
});
Every middleware either sends a response or calls next(). Never
does neither.

10.7 next() After Sending a Response
BAD:

typescript
res.json({ data });
next();  // continues the chain after response sent
This can cause "headers already sent" errors downstream.

10.8 Error Handler in the Middle
An error handler mounted before some routes only catches errors from
routes defined before it. Mount it last.

10.9 Error Handler With Three Arguments
Covered in 4.2. Express identifies error handlers by arity.

10.10 body-parser as a Separate Dependency
express.json() and express.urlencoded() are built into Express 4.16+.
Do not add body-parser unless the project requires it for legacy
reasons.

10.11 Trusting req.query Types
Covered in 5.3. Query values are strings.

10.12 res.send on Objects
res.send({ obj }) sets Content-Type: text/html in some cases.
Use res.json for JSON.

10.13 CORS Wildcard With Credentials
Covered in 8.2. Browsers reject Access-Control-Allow-Origin: * with
credentials: true, but a misconfigured proxy may serve it anyway.

10.14 Missing Body Parser
A POST route that reads req.body without express.json()
mounted. req.body is undefined, and the code crashes or silently
treats it as empty.

10.15 express.static Serving the Project Root
BAD: app.use(express.static(".")). It serves package.json,
.env, and every source file.

Serve a specific directory: app.use(express.static("public")).

10.16 Route Regex Without Anchoring
app.get("/user", ...) matches /user exactly. app.get(/user/, ...) matches any path containing user. Use new RegExp("^/user$")
when a regex is genuinely needed.

10.17 Synchronous Blocking in a Handler
BAD: fs.readFileSync, crypto.pbkdf2Sync, or a long CPU loop
inside a handler. This blocks the entire event loop for the duration.

Use the async variant or offload to a worker.

10.18 Response Sent, Code Continues
Covered in 4.3. An await after res.json may still run and mutate
state that the response already reflects.

10.19 Nested Routers With Duplicate Middleware
app.use("/api", auth) and app.use("/api/v1", auth) on the same
request path runs auth twice. Audit the mount chain.

10.20 Error Object as a Response
BAD:

typescript
res.status(500).json({ error: err });
This serializes the entire error object, including stack traces and
internal fields.

GOOD:

typescript
res.status(500).json({ error: { message: "Internal server error" } });
10.21 next() Called Twice
BAD:

typescript
if (!user) {
  next(new Error("no user"));
}
next();  // called again
Guarantees the handler chain runs twice.

11. Response to Violation
If a previous response violated a rule here:

text
In the previous response, [specific rule] was violated. Correction:
[corrected code]
No justification. No apology paragraph. Fix and move on.

text

---