---
id: 02-fastify-anti-slop
title: "Fastify Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-backend-anti-slop]
category: domain
domain_type: framework
version: 1
---
# Fastify Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`, `domains/framework/02-architecture-anti-slop.md`, and `domains/delivery/02-backend-anti-slop.md`. Generic rules remain inherited.

## 1. Fastify Boundaries

1. Register plugins in the server composition root.
2. Keep route modules, services, and adapters distinct.
3. Use Fastify schemas as the transport contract.
4. Keep plugin encapsulation intentional.
5. Use request decorators only for request-shaped state.
6. Use application decorators only for stable services.
7. Let a child plugin access its own instance through `request.server`.
8. Never register a plugin inside a request handler.
9. Mount related routes under one stable prefix.
10. Keep setup and shutdown in the project lifecycle.
11. Close pools, clients, and subscriptions in `onClose`.
12. Reuse the existing logger and error hierarchy.
13. Set body and serializer limits deliberately.
14. Keep route tests focused on one plugin scope.
15. Avoid importing another plugin's private files.

## 2. Encapsulation and Hooks

16. A normal plugin should not leak decorators to its parent.
17. Use `fastify-plugin` only for intentional shared capabilities.
18. Register hooks in the scope that consumes their decorators.
19. Keep authentication in a protected scope.
20. Keep authorization near each operation.
21. Use `onRequest` only for cheap request metadata.
22. Use `preHandler` after required input validation.
23. Await every asynchronous hook before continuing.
24. Never call `reply` and then continue a hook chain.
25. Use `onClose` for every resource with ownership.
26. Do not hide route registration in a general hook.
27. Keep public plugin methods explicit.
28. Do not use decorators as mutable global state.
29. Test encapsulation with a sibling route.
30. Test startup and shutdown with resource doubles.

### 2.1 Scope Leakage

BAD:
```typescript
app.addHook('onRequest', authenticate)
app.get('/public', publicHandler)
```

GOOD:
```typescript
app.register(protectedRoutes, { prefix: '/private' })
```

### 2.2 Registration in a Handler

BAD:
```typescript
app.get('/users', async request => {
  request.server.register(userService)
  return request.userService.list()
})
```

GOOD:
```typescript
app.register(userRoutes, { prefix: '/api/v1/users' })
```

## 3. Schema Validation

31. Define schemas for params, querystring, body, and headers used by a route.
32. Define response schemas for every documented success code.
33. Reject unknown properties when the contract is closed.
34. Keep identifiers as constrained strings or integers.
35. Do not coerce invalid input in business code.
36. Use the project's error shape for schema failures.
37. Do not read `request.body` before validation.
38. Keep schemas next to routes unless a shared contract module exists.
39. Do not duplicate validation in a hook and handler.
40. Version breaking schema changes with the API.
41. Keep serializer output free of internal fields.
42. Test missing, malformed, and extra fields.

### 3.1 Open Body Contract

BAD:
```typescript
app.post('/users', {
  schema: { body: { type: 'object' } }
}, createUser)
```

GOOD:
```typescript
const body = {
  type: 'object',
  required: ['email'],
  additionalProperties: false,
  properties: { email: { type: 'string', format: 'email' } }
}
app.post('/users', { schema: { body, response: { 201: userSchema } } }, createUser)
```

## 4. Hooks and Errors

43. Set one application error handler in the composition root.
44. Throw typed errors from services.
45. Preserve correlation IDs in logs and safe responses.
46. Do not expose validation internals or database messages.
47. Return once a reply has been sent.
48. Let asynchronous route errors reach the error handler.
49. Keep operational and programmer errors distinguishable.
50. Preserve the project's status convention.
51. Do not add broad error mapping for one route.
52. Test error serialization and hook ordering.
53. Keep auth failures separate from authorization failures.
54. Avoid a global authorization hook with implicit exemptions.
55. Keep request IDs out of untrusted client output.
56. Do not log authorization headers or full bodies.

### 4.1 Hook After Reply

BAD:
```typescript
app.addHook('preHandler', async request => {
  request.reply.send({ error: 'denied' })
})
```

GOOD:
```typescript
app.addHook('preHandler', async request => {
  if (!request.user) throw new UnauthorizedError()
})
```

## 5. Operational Rules

57. Prevent N+1 queries with joins or batched loading.
58. Bound every list and expensive operation.
59. Do not mutate shared state between requests.
60. Use cancellation when a downstream operation supports it.
61. Keep external calls behind adapters.
62. Do not perform network setup in route construction.
63. Validate configuration before accepting traffic.
64. Keep health checks free of business mutations.
65. Test schema rejection, auth, errors, and cleanup.
66. Update OpenAPI output when schemas change.
67. Do not add a serializer or validator without approval.
68. Keep the diff limited to the affected plugin.
69. Report unverified runtime assumptions.
70. Run the repository checks after the change.

### 5.1 Reply and Continue

BAD:
```typescript
if (!user) return reply.code(401).send({ error: 'missing' })
return reply.send({ user })
```

GOOD:
```typescript
if (!user) throw new UnauthorizedError()
return reply.send({ user })
```

## Domain-Specific Anti-Patterns

### A. Shared Global Hook

BAD:
```typescript
app.addHook('onRequest', async request => {
  request.user = await authenticateEveryRequest(request)
})
```

GOOD:
```typescript
app.register(privateRoutes, {
  prefix: '/private',
  hooks: { onRequest: authenticate }
})
```

### B. Mutable Singleton State

BAD:
```typescript
app.decorate('currentUser', '')
```

GOOD:
```typescript
app.decorateRequest('user', null)
```

C. Unbounded Serializer

### C. Unbounded Response Schema

BAD:
```typescript
app.get('/users', { schema: { response: { 200: { type: 'object' } } } }, list)
```

GOOD:
```typescript
app.get('/users', { schema: { response: { 200: userListSchema } } }, list)
```

## 6. Response to Violation
1. Name the plugin boundary and preserve its schema, error, and authorization contracts.
2. Add a focused test and run the repository formatter, linter, and tests.
3. Report unverified assumptions; change no unrelated files and create no commit.
