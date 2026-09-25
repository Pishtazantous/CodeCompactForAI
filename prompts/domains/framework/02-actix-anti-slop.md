---
id: 02-actix-anti-slop
title: "Actix Web Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-backend-anti-slop, 02-rust-anti-slop]
category: domain
domain_type: framework
version: 1
---

# Actix Web Anti-Slop Layer

Layered under the master, architecture, backend, and Rust language layers.
This file covers Actix routing, actors, extractors, application state, and
error responses.

## 1. Stack Assumptions

1. Use the Actix Web, Tokio, and Rust versions declared by the project.
2. Read the application factory and route setup first.
3. Use the project's existing validation, logging, and error types.
4. Match the existing actor and message style if actors are present.
5. Confirm whether `web::Data`, `web::Context`, or app state owns each value.
6. Treat actors as independent concurrency boundaries.
7. Do not add a second application or error abstraction.
8. Keep handler futures cancellable and bounded.
9. Test with the feature set used by the release build.
10. Do not assume an actor mailbox preserves ordering beyond its contract.

## 2. Project Structure

11. Keep application construction separate from route registration.
12. Group handlers by the existing resource or feature structure.
13. Keep actors in the domain or application layer that owns their state.
14. Keep actor messages typed and narrowly scoped.
15. Keep extractors separate from business operations.
16. Keep database and network adapters outside handlers and actors.
17. Use existing visibility and module export conventions.
18. Do not create a generic utility module for unrelated concerns.
19. Keep errors in the established error module.
20. Do not make domain types depend on `HttpRequest` or `web::Data`.

## 3. Routing and Handlers

21. Register specific routes before catch-all and fallback handlers.
22. Use explicit method and path parameter types.
23. Validate path, query, headers, cookies, and body before use.
24. Return the project's response and error envelope.
25. Keep handlers thin and delegate to services.
26. Do not perform blocking I/O directly in an async handler.
27. Keep database transactions inside the data-access boundary.
28. Avoid shared mutable request data through `web::Data`.
29. Add explicit payload and collection limits.
30. Test success, rejection, and unexpected extractor failures.

## 4. Actors

31. Give each actor a single reason to exist.
32. Define messages that express domain operations, not database rows.
33. Keep mailbox messages bounded by the product's concurrency needs.
34. Never put an unbounded stream in a mailbox.
35. Treat actor state as private unless the public API exposes it.
36. Stop actors explicitly during shutdown.
37. Make message handling idempotent when retries are possible.
38. Keep actor failures observable and typed.
39. Do not call a blocking client synchronously from actor context.
40. Use `Addr` or the project's existing handle for communication.
41. Avoid actor-to-actor cycles without an explicit shutdown path.
42. Test concurrent messages, cancellation, and failure isolation.

## 5. Extractors and State

43. Implement extractors for data needed at the boundary.
44. Keep authentication extraction separate from authorization checks.
45. Return stable rejection types for invalid input.
46. Do not perform hidden database work in `FromRequest`.
47. Keep request identity in request context, not in shared application data.
48. Use `web::Data` only for shared, owned resources.
49. Clone handles deliberately; do not clone large mutable structures.
50. Keep lock scopes short and never hold them across unrelated await points.
51. Make state initialization failures visible at startup.
52. Test handlers with isolated state construction.

## 6. Errors and Middleware

53. Use `ResponseError` or the project's existing response conversion.
54. Keep internal error details out of client responses.
55. Log operational and programmer errors with the project logger.
56. Never swallow an error with an empty handler branch.
57. Map extraction, authorization, and application errors consistently.
58. Keep middleware order explicit: context, limits, auth, handlers, errors.
59. Do not let recovery middleware hide programming defects.
60. Ensure CORS, tracing, and compression are composed once.
61. Test middleware behavior with failed and successful requests.
62. Keep backend policy in the backend layer, not scattered in handlers.

## 6. Domain-Specific Anti-Patterns

### 6.1 Actor used as a database proxy

BAD:
```rust
struct DbActor;
impl Actor for DbActor {
    type Context = Context<Self>;
    fn started(&mut self, _ctx: &mut Self::Context) {}
}
```

GOOD:
```rust
struct AccountActor { service: AccountService }
impl Actor for AccountActor { type Context = Context<Self>; }
```

### 6.2 Shared request state

BAD:
```rust
struct CurrentRequest { user: Option<User> }
web::Data<Mutex<CurrentRequest>>
```

GOOD:
```rust
struct AppState { service: AccountService }
web::Data<AppState>
```

### 6.3 Silent extractor failure

BAD:
```rust
impl FromRequest for Identity {
    type Error = Error;
    type Future = Ready<Result<Self, Self::Error>>;
    fn from_request(_req: &HttpRequest, _: &mut Payload) -> Self::Future {
        ready(Ok(Self::default()))
    }
}
```

GOOD:
```rust
impl FromRequest for Identity {
    type Error = Error;
    type Future = Ready<Result<Self, Self::Error>>;
    fn from_request(req: &HttpRequest, _: &mut Payload) -> Self::Future {
        ready(parse_identity(req))
    }
}
```

## 7. Response to Violation

- Correction — `Extractor rejection / Identity::from_request`: make parsing return the project's typed error instead of `default()`, and keep request data out of shared actor state.
- Verify — `Extractor rejection / Identity::from_request`: run the focused extractor test; expected result is a safe rejection with no default identity.
- Correction — `Actor mailbox / typed message`: narrow the message to the domain operation, bound accepted input, and preserve explicit actor shutdown and cancellation.
- Verify — `Actor mailbox / typed message`: run `cargo test --all-features <actor-test>`; expected result is PASS for concurrent processing and shutdown.
- Correction — `Handler boundary / blocking I/O`: move blocking work behind the established async boundary and keep database transactions in the owning adapter.
- Verify — `Handler boundary / blocking I/O`: run `cargo clippy --all-targets --all-features -- -D warnings`; expected result is no blocking or async-policy diagnostics.
- Scope — limit the patch to the cited rule, file, or symbol; record changed and unchanged paths and any unverified runtime assumption.
