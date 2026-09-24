---
id: 02-dotnet-anti-slop
title: "ASP.NET Core Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-backend-anti-slop]
category: domain
domain_type: framework
version: 1
---
# ASP.NET Core Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`, the architecture layer, and `domains/delivery/02-backend-anti-slop.md`. General backend rules remain inherited.

## 1. ASP.NET Core Boundaries

1. Follow the existing controller or minimal API style.
2. Keep endpoint code focused on transport and authorization.
3. Use DTOs for public request and response contracts.
4. Reuse the existing application service and repository patterns.
5. Register services in the composition root or existing extension.
6. Prefer constructor injection over service location.
7. Keep entities out of endpoint responses.
8. Reuse the central exception handler and logger.
9. Keep configuration in typed options.
10. Validate options at startup.
11. Use the existing authentication and authorization policy.
12. Keep migrations in the data layer.
13. Do not add a second ORM or validation library.
14. Keep the diff limited to ASP.NET Core.

## 2. Dependency Injection

15. Use scoped lifetime for `DbContext` and request-bound services.
16. Use singleton lifetime for stateless, thread-safe services.
17. Never capture a scoped service in a singleton.
18. Use constructor injection at the consuming boundary.
19. Do not resolve services from `IServiceProvider` in domain code.
20. Register concrete implementations explicitly.
21. Bind interfaces when a boundary requires substitution.
22. Use keyed services only when the local design needs them.
23. Test lifetime-sensitive registrations.
24. Keep service disposal owned by the container.

### 2.1 Captured Scoped Service

BAD:
```csharp
public sealed class Worker(IServiceProvider services)
{
    public Task Run() => services.GetRequiredService<IOrderRepository>().Add();
}
```

GOOD:
```csharp
public sealed class Worker(IServiceScopeFactory scopes)
{
    public async Task Run()
    {
        await using var scope = scopes.CreateAsyncScope();
        var repository = scope.ServiceProvider.GetRequiredService<IOrderRepository>();
        await repository.Add();
    }
}
```

### 2.2 Service Location

BAD:
```csharp
public sealed class Orders(IServiceProvider services)
{
    public Task Add() => services.GetRequiredService<IOrderService>().Add();
}
```

GOOD:
```csharp
public sealed class Orders(IOrderService service)
{
    public Task Add() => service.Add();
}
```

## 3. Middleware Pipeline

25. Order exception, correlation, authentication, authorization, and endpoint middleware deliberately.
26. Use middleware for request-wide concerns only.
27. Call the next delegate once on the normal path.
28. Do not write a response and then call next.
29. Use short-circuiting for a complete rejection response.
30. Keep database work out of middleware.
31. Pass cancellation tokens to downstream operations.
32. Ensure body and response limits are explicit.
33. Test ordering and short-circuit behavior.
34. Keep endpoint metadata authorization visible.

### 3.1 Response After Next

BAD:
```csharp
app.Use(async (context, next) =>
{
    await next();
    context.Response.StatusCode = 201;
});
```

GOOD:
```csharp
app.Use(async (context, next) =>
{
    using var scope = context.RequestServices.CreateScope();
    context.Items["scope"] = scope;
    await next();
});
```

## 4. EF Core

35. Register `DbContext` with a request lifetime.
36. Await all asynchronous database operations.
37. Use projections for read endpoints.
38. Prevent N+1 with Include, projection, or batching.
39. Use transactions for multi-write operations.
40. Handle concurrency tokens and conflicts explicitly.
41. Keep entities out of serialized responses.
42. Select explicit fields for sensitive or large queries.
43. Do not use raw SQL unless the project already does.
44. Keep migrations outside endpoint code.
45. Test provider-specific behavior where it matters.

### 4.1 Entity Returned from Endpoint

BAD:
```csharp
app.MapGet("/users/{id}", async (int id, AppDbContext db) =>
    await db.Users.FindAsync(id));
```

GOOD:
```csharp
app.MapGet("/users/{id}", async (int id, IUserQueries queries) =>
    await queries.GetResponse(id));
```

## 5. Validation, Errors, and Operations

46. Validate DTOs before application work.
47. Return the established ProblemDetails or error envelope.
48. Map typed domain exceptions centrally.
49. Do not expose stack traces, SQL, or internal paths.
50. Preserve correlation IDs in logs.
51. Do not catch `Exception` and return success.
52. Use cancellation tokens for external I/O.
53. Bound external calls and page sizes.
54. Keep secrets in the project secret store.
55. Test unauthorized, invalid, missing, and conflict paths.
56. Run the repository build, analyzers, and tests.
57. Report unverified assumptions.
58. Keep unrelated projects untouched.

### 5.1 Hidden Error Translation

BAD:
```csharp
try { return await service.Add(input); }
catch (Exception) { return Results.Ok(); }
```

GOOD:
```csharp
try { return Results.Created(await service.Add(input)); }
catch (DomainException error) { throw new ApiException(error); }
```

## Domain-Specific Anti-Patterns

### A. Global Middleware Query

BAD:
```csharp
app.Use(async (context, next) =>
{
    await using var db = context.RequestServices.GetRequiredService<AppDbContext>();
    context.Items["count"] = await db.Users.CountAsync();
    await next();
});
```

GOOD:
```csharp
app.MapGet("/users", async (IUserQueries queries) => await queries.List());
```

### B. Entity Exposure

BAD:
```csharp
public sealed record UserResponse(User User);
```

GOOD:
```csharp
public sealed record UserResponse(Guid Id, string Email);
```

### C. Scoped Service Captured by Singleton

BAD:
```csharp
public sealed class Worker(IServiceProvider services) { }
```

GOOD:
```csharp
public sealed class Worker(IServiceScopeFactory scopes) { }
```

## 6. Response to Violation
1. Name the ASP.NET Core boundary and preserve its response, error, and auth contracts.
2. Add a focused test and run the repository formatter, analyzers, and tests.
3. Report unverified assumptions; change no unrelated files and create no commit.
