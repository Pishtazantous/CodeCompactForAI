---
id: 02-laravel-anti-slop
title: "Laravel Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-backend-anti-slop]
category: domain
domain_type: framework
version: 1
---
# Laravel Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`, the architecture layer, and `domains/delivery/02-backend-anti-slop.md`. General backend rules remain inherited.

## 1. Laravel Boundaries

1. Use the existing app, module, or domain organization.
2. Keep controllers thin and services responsible for workflows.
3. Use Form Requests for browser and API input.
4. Use route model binding when it matches the local style.
5. Keep policies explicit for resource actions.
6. Reuse the existing exception handler and logger.
7. Keep configuration in config files and environment-backed values.
8. Keep providers explicit and avoid service location.
9. Use jobs for retryable asynchronous work.
10. Use events only for meaningful domain notifications.
11. Keep Blade views presentation-only and escaped.
12. Keep migrations separate from request behavior.
13. Reuse project test helpers and factories.
14. Do not add packages without approval.

## 2. Eloquent

15. Select explicit fields in large or sensitive queries.
16. Eager load relationships needed by a response.
17. Use transactions for multi-write operations.
18. Use model validation for model-owned invariants.
19. Use database constraints for durable invariants.
20. Use `find` for required records and `first` intentionally for optional records.
21. Avoid `fill` and `update` with unvalidated input.
22. Keep scopes composable and free of hidden writes.
23. Do not perform external work in accessors or observers.
24. Avoid lazy loading in a response.
25. Add query-count tests for list and detail actions.
26. Use concurrency controls when updates can race.
27. Keep database values out of transport DTOs.

### 2.1 N+1 Query

BAD:
```php
return Order::all()->map(fn ($order) => $order->customer->name);
```

GOOD:
```php
return Order::with('customer')->paginate();
```

### 2.2 Unvalidated Mass Assignment

BAD:
```php
$order->update($request->all());
```

GOOD:
```php
$order->update($request->validated());
```

## 3. Controllers and Middleware

28. Authorize the specific model and action.
29. Return the established resource or view shape.
30. Set status codes for created and error responses.
31. Keep redirects within trusted local routes.
32. Use middleware only for request-wide concerns.
33. Keep authentication and authorization in the existing chain.
34. Do not query twice from middleware and a controller.
35. Return one response for each branch.
36. Preserve CSRF and secure-cookie settings.
37. Do not catch exceptions and return success.
38. Use the project exception response envelope.
39. Keep correlation IDs in safe logs.
40. Validate request limits explicitly.
41. Test invalid, unauthorized, and missing cases.

### 3.1 Middleware Business Query

BAD:
```php
public function handle($request, $next)
{
    Order::count();
    return $next($request);
}
```

GOOD:
```php
public function handle($request, $next)
{
    $request->attributes->set('request_id', $request->headers->get('X-Request-Id'));
    return $next($request);
}
```

## 4. Facades and the Container

41. Use facades consistently with neighboring code.
42. Inject services when a boundary needs an interface or a test double.
43. Do not call the container from domain models.
44. Register bindings in providers or the established config.
45. Bind interfaces explicitly.
46. Use scoped bindings for request resources.
47. Keep singleton state immutable or synchronized.
48. Do not use the container as a runtime service locator.
49. Do not create a binding for a capability already provided.
50. Test lifetime-sensitive bindings.

### 4.1 Service Locator

BAD:
```php
class OrderService
{
    public function place(array $data): void
    {
        app(PaymentGateway::class)->charge($data);
    }
}
```

GOOD:
```php
class OrderService
{
    public function __construct(private PaymentGateway $payments) {}

    public function place(array $data): void
    {
        $this->payments->charge($data);
    }
}
```

## 5. Jobs, Events, and Views

51. Make jobs idempotent and retry-safe.
52. Do not assume a job runs exactly once.
53. Keep job payloads minimal and serializable.
54. Use the project queue and retry policy.
55. Emit events only after the required transaction commits.
56. Do not call external services before commit.
57. Keep observers free of hidden workflow logic.
58. Use explicit Blade locals where the project already does.
59. Keep raw HTML disabled for untrusted values.
60. Keep templates free of persistence calls.
61. Test transaction rollback and job retry.

### 5.1 Observer Side Effect

BAD:
```php
class UserObserver
{
    public function created(User $user): void
    {
        Mail::to($user->email)->send(new WelcomeMail($user));
    }
}
```

GOOD:
```php
class UserObserver
{
    public function created(User $user): void
    {
        SendWelcome::dispatch($user->id);
    }
}
```

## Domain-Specific Anti-Patterns

### A. Mass Assignment

BAD:
```php
$user->fill($request->all())->save();
```

GOOD:
```php
$user->fill($request->validated())->save();
```

### B. Service Locator in a Model

BAD:
```php
app(PaymentGateway::class)->charge($this);
```

GOOD:
```php
$this->payments->charge($this);
```

### C. Observer Sends Mail Inline

BAD:
```php
Mail::to($user->email)->send(new WelcomeMail($user));
```

GOOD:
```php
SendWelcome::dispatch($user->id);
```

## 6. Response to Violation
1. Name the Laravel boundary and preserve its validation, policy, and error contracts.
2. Add a focused test and run the repository formatter, analyzer, and tests.
3. Report unverified assumptions; change no unrelated files and create no commit.
