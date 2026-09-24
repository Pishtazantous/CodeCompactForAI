---
id: 02-gin-anti-slop
title: "Gin Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-backend-anti-slop]
category: domain
domain_type: framework
version: 1
---
# Gin Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`, the architecture layer, and `domains/delivery/02-backend-anti-slop.md`. General backend rules remain inherited.

## 1. Gin Boundaries

1. Keep router construction in the bootstrap function.
2. Group routes by resource and attach middleware at the group.
3. Keep handlers focused on binding, authorization, service calls, and response mapping.
4. Use constructor-injected services for handlers.
5. Keep repositories and infrastructure outside handler packages.
6. Use the existing response helper and error mapper.
7. Treat `gin.Context` as valid only during the request.
8. Validate JSON, query, path, form, and header inputs.
9. Bind into request DTOs, not database models.
10. Keep configuration in the project configuration layer.
11. Set body, read, and write limits deliberately.
12. Do not add a second router or validation library.
13. Keep tests beside the handler package.
14. Report assumptions not confirmed from the repository.

## 2. Handlers and Middleware

15. Call `c.Next()` once on the normal middleware path.
16. Call `c.Abort()` only when the request must stop.
17. Do not call `c.Next()` after writing a response.
18. Keep authorization explicit in route groups or handlers.
19. Do not retain a context in a goroutine or service.
20. Copy request values before asynchronous work.
21. Use `c.Error` or the existing central mapper for failures.
22. Return immediately after writing a response.
23. Keep database work out of middleware.
24. Use bounded request values and slices.
25. Test middleware order and abort behavior.

### 2.1 Context After Handler

BAD:
```go
go func() {
    save(c.Query("email"))
    c.JSON(200, gin.H{"ok": true})
}()
c.Abort()
```

GOOD:
```go
email := c.Query("email")
c.JSON(202, gin.H{"queued": true})
go enqueueSave(email)
```

### 2.2 Abort and Continue

BAD:
```go
func auth(c *gin.Context) {
    c.AbortWithStatus(401)
    c.Next()
}
```

GOOD:
```go
func auth(c *gin.Context) {
    if !authorized(c) {
        c.AbortWithStatus(401)
        return
    }
    c.Next()
}
```

## 3. Binding and Validation

26. Use the binding method matching the input location.
27. Use `ShouldBind` when errors map to the project response.
28. Reject unknown JSON fields when the contract is closed.
29. Keep binding tags for shape and format only.
30. Validate cross-field rules in a service.
31. Convert numeric input and check range before use.
32. Do not bind directly into a persistence model.
33. Keep binding DTOs close to the route.
34. Do not duplicate validator logic in handlers.
35. Test malformed, missing, extra, and oversized input.
36. Never interpolate a route value into SQL.
37. Use the repository's query builder and parameters.

### 3.1 Raw Identifier

BAD:
```go
db.Raw("select * from users where id = " + c.Query("id")).Scan(&user)
```

GOOD:
```go
id, err := strconv.Atoi(c.Query("id"))
if err != nil { respondError(c, err); return }
user, err := repository.FindByID(context.Background(), id)
```

## 4. Errors and Concurrency

38. Use one central error mapper.
39. Do not expose database or internal paths.
40. Preserve status and error envelope conventions.
41. Pass `context.Context` to external I/O.
42. Handle goroutine failures and write results before response.
43. Never fire-and-forget a required write.
44. Use a worker pool for durable asynchronous work.
45. Bound concurrent calls and page sizes.
46. Do not share mutable request state between goroutines.
47. Ensure each response has one writer.
48. Test cancellation and timeout paths.

### 4.1 Swallowed Error

BAD:
```go
if err := service.Create(input); err == nil {
    c.JSON(200, gin.H{"ok": true})
}
```

GOOD:
```go
if err := service.Create(input); err != nil {
    respondError(c, err)
    return
}
c.JSON(201, gin.H{"ok": true})
```

## 5. Database and Operations

49. Use the existing repository and connection lifecycle.
50. Select explicit fields in large queries.
51. Prevent N+1 with joins or batched loading.
52. Use transactions for multi-write operations.
53. Keep external services behind interfaces.
54. Validate configuration before accepting traffic.
55. Set server timeouts explicitly.
56. Use the project logger with request correlation.
57. Do not log credentials or full bodies.
58. Preserve auth and rate-limit middleware boundaries.
59. Add tests for route, binding, middleware, and error behavior.
60. Run the repository formatter, vet, tests, and build.

### 5.1 Handler Owns SQL

BAD:
```go
func list(c *gin.Context) {
    db.Find(&orders)
    c.JSON(200, orders)
}
```

GOOD:
```go
func list(c *gin.Context) {
    orders, err := service.List(c.Request.Context(), page, limit)
    if err != nil { respondError(c, err); return }
    c.JSON(200, orders)
}
```

## Domain-Specific Anti-Patterns

### A. Global Catch-All Middleware

BAD:
```go
router.Use(func(c *gin.Context) {
    c.Set("user", authenticateEverywhere(c))
    c.Next()
})
```

GOOD:
```go
private := router.Group("/private")
private.Use(authenticate)
private.GET("/orders", listOrders)
```

### B. Handler Retains Context

BAD:
```go
go func() { save(c.Query("email")); c.JSON(200, data) }()
```

GOOD:
```go
email := c.Query("email"); c.JSON(202, gin.H{"queued": true})
```

### C. Binding Directly to Model

BAD:
```go
var user User; c.ShouldBindJSON(&user)
```

GOOD:
```go
var input CreateUserInput; c.ShouldBindJSON(&input)
```

## 6. Response to Violation
1. Name the Gin route, binding, or middleware boundary and preserve its contracts.
2. Add a focused test and run the repository formatter, vet, and tests.
3. Report unverified assumptions; change no unrelated files and create no commit.
