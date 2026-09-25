---
id: 02-axum-anti-slop
title: "Axum Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-backend-anti-slop, 02-rust-anti-slop]
category: domain
domain_type: framework
version: 1
---

# Axum Anti-Slop Layer

Layered under the master, architecture, backend, and Rust language layers.
This file covers Axum routing, extractors, state, Tower middleware, and typed
handler errors.

## 1. Stack Assumptions

1. Use the Axum, Tokio, and Rust versions declared by the project.
2. Read the router construction and application entry point first.
3. Use the project's existing validation and error response types.
4. Confirm whether the project uses `State`, `Extension`, or both.
5. Keep handler state explicit in function signatures.
6. Match existing async runtime and cancellation conventions.
7. Do not add a second router or middleware stack.
8. Use the existing dependency injection pattern for repositories.
9. Confirm configured limits and timeouts before exposing public routes.
10. Test with the runtime and features used by the release build.

## 2. Project Structure

11. Keep router assembly separate from application use cases.
12. Group routes according to the existing domain organization.
13. Keep extractors small and reusable only after they earn duplication.
14. Keep shared state definitions in an application module.
15. Keep database and network adapters outside handlers.
16. Keep domain errors independent of Axum response types.
17. Use existing error modules and visibility conventions.
18. Do not create a generic utility module for unrelated types.
19. Keep feature flags at the application boundary.
20. Do not make domain logic depend on `Router` or extractor types.

## 3. Routing and Handlers

21. Register specific paths before wildcard or fallback routes.
22. Use explicit method routers and stable path parameter names.
23. Return the project's response type rather than ad hoc JSON maps.
24. Keep handler parameters small and easy to test.
25. Validate path, query, headers, and body through typed extractors.
26. Do not perform a blocking operation directly on the async runtime.
27. Delegate business operations to application services.
28. Keep status and error mapping in one reviewed boundary.
29. Add route tests for extraction and expected rejection.
30. Keep request cancellation connected to external work.
31. Do not use `unwrap` on request data or shared state.
32. Do not return secrets or internal diagnostics from an extractor error.

## 4. Extractors

33. Implement `FromRequestParts` for data independent of the body.
34. Implement `FromRequest` only when consuming the body is intentional.
35. Keep extractor validation deterministic and side-effect free where possible.
36. Return typed rejection responses with useful status and message.
37. Do not parse the same body in multiple extractors.
38. Make body limits part of the router or server configuration.
39. Keep authentication extraction separate from authorization decisions.
40. Avoid extractor implementations that call the database on every request.
41. Test malformed, missing, and out-of-order extractor inputs.
42. Keep extractor state dependencies explicit through `State`.

## 5. State and Shared Resources

43. Define application state with types that express ownership.
44. Use `Arc` only for genuinely shared resources.
45. Do not put request-specific values in router state.
46. Keep connection pools behind an existing repository or infrastructure type.
47. Avoid holding locks across await points.
48. Make shutdown and pool draining explicit.
49. Clone handles cheaply and deliberately.
50. Do not use global mutable state for test configuration.
51. Test independent state construction for unit tests.
52. Keep state initialization failures visible at startup.

## 6. Tower Middleware

53. Compose Tower layers in a documented order.
54. Put request context and tracing before handlers that need it.
55. Put authentication before authorization and route execution.
56. Keep timeout and body limits on the correct server or route layer.
57. Use the project's existing tracing, CORS, and compression layers.
58. Do not create a middleware that silently drops a response.
59. Ensure errors from inner services are mapped consistently.
60. Test middleware composition, not only isolated handlers.
61. Keep recovery behavior separate from expected application errors.
62. Do not duplicate backend rules that already exist in the service layer.

## 6. Domain-Specific Anti-Patterns

### 6.1 Catch-all extractor

BAD:
```rust
impl<S> FromRequest<S> for RequestData {
    type Rejection = Infallible;
    async fn from_request(_req: Request, _state: &S) -> Result<Self, Self::Rejection> {
        Ok(Self::default())
    }
}
```

GOOD:
```rust
impl<S> FromRequest<S> for RequestData {
    type Rejection = ApiError;
    async fn from_request(req: Request, _state: &S) -> Result<Self, Self::Rejection> {
        validate_request_data(req)
    }
}
```

### 6.2 State as a bag of globals

BAD:
```rust
#[derive(Clone)]
struct AppState { user: User, request_id: String, db: Pool }
```

GOOD:
```rust
#[derive(Clone)]
struct AppState { db: Pool }
```

### 6.3 Blocking work on Tokio

BAD:
```rust
async fn load(State(state): State<AppState>) {
    let rows = state.db.blocking_query();
}
```

GOOD:
```rust
async fn load(State(state): State<AppState>) -> Result<Rows, AppError> {
    state.repository.load().await
}
```

## 7. Response to Violation

- Correction — `Typed request boundary / FromRequest`: replace catch-all defaulting with explicit validation, bounded inputs, and the established rejection type.
- Verify — `Typed request boundary / FromRequest`: run the focused extractor test; expected result is safe rejection for missing, malformed, and oversized input.
- Correction — `Application state / AppState`: remove request-specific fields, keep owned shared resources explicit, and avoid locks across `.await` points.
- Verify — `Application state / AppState`: run `cargo test --all-features <state-test>`; expected result is PASS with isolated state and no cross-request leakage.
- Correction — `Handler boundary / repository call`: replace blocking work with the repository's async contract and preserve cancellation through external calls.
- Verify — `Handler boundary / repository call`: run `cargo clippy --all-targets --all-features -- -D warnings`; expected result is no blocking, lock, or cancellation diagnostics.
- Scope — limit the patch to the cited rule, file, or symbol; record changed and unchanged paths plus any untested runtime path.
