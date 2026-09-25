---
id: 02-fiber-anti-slop
title: "Fiber Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-backend-anti-slop, 02-go-anti-slop]
category: domain
domain_type: framework
version: 1
---

# Fiber Anti-Slop Layer

Layered under the master, architecture, backend, and Go language layers.
This file covers Fiber routing, plugins, schemas, hooks, context values, and
shutdown behavior.

## 1. Stack Assumptions

1. Use the Fiber version and Go version declared by the project.
2. Read the existing application setup and route layout first.
3. Use the project's existing validation, logging, and error packages.
4. Confirm whether WebSocket, multipart, or proxy middleware is required.
5. Keep Fiber context values explicit and short-lived.
6. Treat middleware execution order as part of the route contract.
7. Do not add a second web framework or validation system.
8. Match the existing response and error envelope.
9. Keep handlers free of database and business-rule details.
10. Verify graceful shutdown behavior with active requests.

## 2. Project Structure

11. Keep app construction separate from route registration.
12. Group routes by the existing resource organization.
13. Keep handlers thin and delegate to application services.
14. Keep schemas next to the route or in the established schema directory.
15. Keep middleware for cross-cutting behavior only.
16. Keep fiber context helpers thin and typed.
17. Do not import database clients into route-registration code.
18. Use the existing package and file naming conventions.
19. Keep application state injected through constructors.
20. Do not create a generic utils package for unrelated helpers.

## 3. Routing and Controllers

21. Register static and parameter routes in a deliberate order.
22. Put specific routes before parameter and wildcard routes.
23. Validate path parameters before use.
24. Use the project's schema validator for body, query, and headers.
25. Do not read unvalidated input in a controller.
26. Keep HTTP methods consistent with their side effects.
27. Set explicit status codes for created and deleted resources.
28. Use the same response envelope for success and error paths.
29. Keep a controller from issuing multiple unrelated side effects.
30. Return after writing a response.
31. Never call `SendStatus` and then attempt to write a body.
32. Keep route tests focused on status, body, and contract boundaries.

## 4. Middleware and Hooks

33. Order request ID, logging, parsing, authentication, authorization, and
    handlers according to the existing application contract.
34. Use Fiber hooks only for process lifecycle events that are actually needed.
35. Make every middleware `Next` or terminal behavior explicit.
36. Do not call `Next` after a response has been sent unless intentional.
37. Propagate context values with namespaced keys and documented types.
38. Do not use the default context for unrelated request data.
39. Set timeouts and body limits for expensive or public operations.
40. Keep recovery middleware outermost and test its error mapping.
41. Ensure middleware cleanup runs when a request is rejected.
42. Keep CORS and security headers in one reviewed location.
43. Avoid middleware that performs database writes on every request.
44. Do not silently bypass authentication through an alternate route.

## 5. Schema and Context

45. Define one schema per validated boundary, not a global permissive object.
46. Reject unknown fields when the project uses strict schemas.
47. Keep schema types separate from database models.
48. Convert validated DTOs explicitly in the application layer.
49. Keep context values immutable from the handler's perspective.
50. Do not store request-scoped credentials in package globals.
51. Make context key collisions impossible by ownership or naming.
52. Avoid putting large request bodies in context values.
53. Keep query pagination and filtering bounded.
54. Use a stable error code for each expected validation failure.
55. Test malformed, oversized, and unexpected fields.
56. Store request IDs in typed context values and preserve them through logging.
57. Convert validated DTOs before calling application services.
58. Use the request context for cancellation instead of package globals.
59. Reject unsupported content types before body parsing.
60. Map Fiber errors through the project's stable error envelope.
61. Exercise direct, grouped, nested, and parameterized route registration.
62. Verify graceful shutdown with active requests and streaming responses.

## 6. Domain-Specific Anti-Patterns

### 6.1 Middleware order creates a bypass

BAD:
```go
app.Get("/admin/*", handler)
app.Use("/admin", authMiddleware)
```

GOOD:
```go
admin := app.Group("/admin", authMiddleware)
admin.Get("/*", handler)
```

### 6.2 Handler owns persistence

BAD:
```go
func listUsers(c *fiber.Ctx) error {
    rows, err := database.Query("select * from users")
    return c.JSON(rows, err)
}
```

GOOD:
```go
func listUsers(c *fiber.Ctx) error {
    result, err := userService.List(c.Context())
    return respond(c, result, err)
}
```

### 6.3 Unbounded query

BAD:
```go
limit := c.QueryInt("limit")
return list(c, limit)
```

GOOD:
```go
limit := schema.ParseLimit(c.Query("limit"))
return list(c, limit)
```

## 7. Response to Violation

- Correction — name the cited Fiber rule, file, and symbol; apply only that
  middleware, schema, context, or service-boundary correction.
- Verify — run the focused route test plus the repository's Go checks; report
  the actual command output and any untested streaming or shutdown path.
- Scope — preserve unrelated handlers and contracts, and record changed and
  unchanged files without claiming an unrun check passed.
