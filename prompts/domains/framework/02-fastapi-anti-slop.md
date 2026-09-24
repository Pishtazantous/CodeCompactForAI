---
id: 02-fastapi-anti-slop
title: "FastAPI Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-backend-anti-slop]
category: domain
domain_type: framework
version: 1
---
# FastAPI Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`, the architecture layer, and `domains/delivery/02-backend-anti-slop.md`. General backend rules remain inherited.

## 1. Application Boundaries

1. Keep the app factory, routers, schemas, dependencies, services, and adapters separate.
2. Register routers once in the composition root.
3. Keep routes focused on parsing, authorization, orchestration, and response mapping.
4. Use Pydantic models at every public transport boundary.
5. Use existing validators and services; do not add a second schema system.
6. Reuse the project exception and logging configuration.
7. Keep configuration in typed settings.
8. Use lifespan for clients, pools, and background resources.
9. Import through module public APIs.
10. Keep schemas close to routers unless a shared contract package exists.
11. Preserve the established sync or async style within a module.
12. Keep generated OpenAPI synchronized with annotations.

## 2. Pydantic Contracts

13. Separate create, update, read, and persistence models when fields differ.
14. Reject unknown fields when the contract is closed.
15. Validate types, ranges, and formats at the boundary.
16. Keep cross-field business rules in the service.
17. Do not return `dict` when a response model is possible.
18. Keep internal fields and secrets out of response models.
19. Use aliases only when the public contract requires them.
20. Keep examples safe and representative.
21. Preserve decimal and datetime precision.
22. Give every route an explicit response model or response class.
23. Do not expose ORM objects directly when they contain relationships.
24. Add contract tests for accepted and rejected payloads.

### 2.1 Permissive Response

BAD:
```python
@app.get('/users/{user_id}', response_model=dict)
async def get_user(user_id: int):
    return load_user(user_id)
```

GOOD:
```python
@app.get('/users/{user_id}', response_model=UserRead)
async def get_user(user_id: int):
    return await service.load_user(user_id)
```

### 2.2 Duplicate Validation

BAD:
```python
async def create(data: dict, current=Depends(auth)):
    if not data.get('email'):
        raise ValueError('email required')
```

GOOD:
```python
async def create(data: UserCreate, current=Depends(auth)):
    return await service.create(data)
```

## 3. Dependencies

25. Use dependencies for wiring and reusable request preconditions.
26. Inject the current user through a typed dependency.
27. Load a required resource through a dependency that raises the project not-found error.
28. Use `yield` for sessions with deterministic cleanup.
29. Use dependency caching only when the value is request-safe.
30. Keep dependency failures in the central error mapper.
31. Do not resolve services from a global container in routes.
32. Keep authorization visible in the dependency graph.
33. Do not hide a route-specific policy in a cached dependency.
34. Keep dependencies free of unbounded queries.
35. Test dependency success, denial, absence, and cleanup.

### 3.1 Uncached Session Dependency

BAD:
```python
def db_one():
    return Session()

def db_two():
    return Session()
```

GOOD:
```python
def get_db():
    with Session() as session:
        yield session
```

## 4. Async and I/O

36. Use `async def` only for non-blocking operations.
37. Do not call blocking ORM, filesystem, or HTTP code in an async route.
38. Use the project's async client or a sync route.
39. Await required writes before returning.
40. Bound concurrent calls and handle partial failures.
41. Pass request cancellation to external I/O.
42. Close clients and pools in lifespan shutdown.
43. Do not mix sync and async access to one mutable resource.
44. Avoid background tasks for required writes.
45. Use a task queue for durable asynchronous work.
46. Avoid fire-and-forget calls in route bodies.
47. Test timeout and cancellation behavior.
48. Keep the event loop free of CPU-heavy work.

### 4.1 Blocking Call in Async Route

BAD:
```python
@app.post('/imports')
async def create_import(data: ImportRequest):
    return requests.post(partner_url, json=data.model_dump())
```

GOOD:
```python
@app.post('/imports')
async def create_import(data: ImportRequest):
    return await partner_client.import_data(data)
```

## 5. OpenAPI and Errors

49. Describe auth, status codes, and response models explicitly.
50. Use stable operation IDs and the existing tag convention.
51. Keep error responses compatible with the backend envelope.
52. Map domain exceptions with typed exception handlers.
53. Do not expose traceback, SQL, or filesystem details.
54. Preserve request IDs in logs and safe errors.
55. Do not write a response and then raise another error.
56. Keep middleware for request-wide concerns only.
57. Validate startup settings before serving traffic.
58. Update generated clients when a contract changes.
59. Test OpenAPI for required fields and status codes.
60. Do not introduce undocumented response variants.

### 5.1 Middleware Error Mapping

BAD:
```python
@app.middleware('http')
async def errors(request, call_next):
    try:
        return await call_next(request)
    except Exception:
        return JSONResponse({'detail': 'failed'}, status_code=200)
```

GOOD:
```python
@app.exception_handler(DomainError)
async def domain_error(request, exc):
    return JSONResponse({'detail': exc.code}, status_code=exc.status_code)
```

## Domain-Specific Anti-Patterns

### A. Service Locator in a Route

BAD:
```python
@app.get('/orders')
async def orders():
    return await request.app.state.container.order_service.list()
```

GOOD:
```python
@app.get('/orders')
async def orders(service: OrderService = Depends(get_order_service)):
    return await service.list()
```

### B. Shared Mutable State

BAD:
```python
app.state.current_user = None
```

GOOD:
```python
async def current_user(credentials=Depends(read_credentials)):
    return authenticate(credentials)
```

### C. Required Write in Background Task

BAD:
```python
asyncio.create_task(order_repository.save(order))
return {"accepted": True}
```

GOOD:
```python
await order_repository.save(order)
return {"accepted": True}
```

## 6. Response to Violation
1. Name the route, dependency, or lifecycle boundary and preserve its contracts.
2. Add a focused test and run the repository formatter, linter, and tests.
3. Report unverified assumptions; change no unrelated files and create no commit.
