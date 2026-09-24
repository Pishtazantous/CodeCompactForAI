---
id: 02-rust-anti-slop
title: "Rust Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: language
version: 1
---
# Rust Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules are not
repeated. This layer covers Rust ownership, errors, unsafe code, lifetimes,
and API boundaries. Framework rules belong in `domains/framework/`.

## 1. Scope and Assumptions
1. Read the workspace manifest and the project toolchain before selecting
   edition, features, or dependencies. Never assume a crate or feature exists.
2. Preserve the existing formatter, clippy configuration, and public API.
3. Treat panic as a process-level invariant failure, not ordinary error flow.

## 2. Ownership and Borrowing
4. Prefer borrowing (`&T`, `&mut T`) to cloning. Clone only when the value
   must be independently owned or the clone is required by an interface.
5. Keep ownership visible. Do not use `Rc<RefCell<T>>` to bypass design
   constraints; first document why shared mutation is necessary.
6. Return owned values from transformations. Shadow a binding when the new
   value replaces the old one, and avoid simultaneous aliases that conflict.
7. Use iterators for owned collections; collect only at an API boundary.

## 3. Error Handling
8. Return `Result<T, E>` for expected failures. Reserve `panic!` for a broken
   invariant that every caller must prevent.
9. Attach context while preserving the source error with `?`; do not turn a
   typed error into a string.
10. Match the narrowest useful error variant. Do not catch `Err(_)` and
    continue with a default without recording why.
11. Do not silently discard a `Result` with `_`. A comment must identify the
    exact condition and its safe consequence.

## 4. Option and Error Boundaries
12. Use `Option` for absence and `Result` for failure. Do not replace both
    with a sentinel value.
13. Keep `?` inside functions returning compatible `Result` types. Convert at
    a boundary where the application error type is defined.
14. Never call `unwrap` in production request paths, initialization, or code
    handling external input. `unwrap` is acceptable in tests and compile-time
    constants whose invariant is locally obvious.
15. Use `expect` only when the message states an invariant and the failure is
    actionable. It is not permission to hide a fallible operation.

## 5. Unsafe Code
16. Do not introduce `unsafe` when a checked standard-library operation can
    express the requirement. Every unsafe block requires a nearby invariant
    comment and a focused test.
17. Keep unsafe operations behind a small safe API. Validate pointers, lengths,
    alignment, aliasing, and initialization before the block.
18. Do not assume a raw pointer remains valid after movement, reallocation, or
    a container resize. Treat references as having exactly the lifetime in
    the signature.
19. Run the project's Miri or other undefined-behavior checks when available;
    never claim they passed unless the command was run.

## 6. Lifetimes and APIs
20. Let elision infer ordinary lifetimes. Add a lifetime only when the return
    type genuinely borrows an input and inference cannot express the relationship.
21. Do not return a reference to a temporary, a lock guard's protected value
    beyond its guard, or a field whose owner is about to move.
22. Prefer owning return values for public APIs when borrowing would force
    callers to carry a lifetime tied to a short-lived request.
23. Do not use `'static` to silence a borrow error. It means the value can
    live forever, not merely that the compiler could not prove otherwise.

## 7. Traits, Types, and Performance
24. Use newtypes when a primitive has a meaningful domain invariant; do not
    add a wrapper without a real unit or invariant.
25. Implement `Display` for user-facing output and `Debug` for diagnostics.
    Do not expose secrets through either implementation.
26. Avoid premature `Arc`, generic complexity, or trait objects. Choose the
    simplest type that expresses ownership and dynamic dispatch needs.
27. Use `std::mem::take` or `replace` to move out of a value only when the
    old value has a clear, type-correct replacement.
28. Measure before optimizing. `clone` and allocation are not automatically
    bad; hidden ownership ambiguity is.

## 8. Public API and Cargo Hygiene
29. Keep feature flags additive and documented. Avoid enabling a feature only
    to make a local build pass if it changes the supported contract.
30. Do not add dependencies to `Cargo.toml` without permission. Prefer an
    existing standard facility when it is adequate.
31. Preserve `#[non_exhaustive]` and enum compatibility rules already used by
    the project. A new variant can be a breaking change without it.
32. Document panic, unsafe, and ownership requirements on public functions
    where a caller could otherwise be surprised.

40. Review recursive types for ownership cycles before adding reference-counted
    nodes to the graph.
41. Check feature gates at public API boundaries and reject unknown runtime
    configurations during startup.
42. Prefer iterator adapters over intermediate vectors when ownership permits.
44. Inspect unsafe blocks for pointer validity and aliasing before merging.
45. Report each executed verification command and its outcome.

## Domain-Specific Anti-Patterns

### 9.1 Hidden Cloning
BAD:
```rust
fn label(user: User) -> String {
    let owner = user.clone();
    format_user(owner, user)
}
```
GOOD:
```rust
fn label(user: &User) -> String {
    format_user(user)
}
```

### 9.2 Lossy Error Conversion
BAD:
```rust
let config = std::fs::read_to_string(path)
    .map_err(|error| error.to_string());
```
GOOD:
```rust
let config = std::fs::read_to_string(path)
    .with_context(|| format!("read {path}"))?;
```

### 9.3 Production Panics
BAD:
```rust
let port = env::var("PORT").unwrap().parse().unwrap();
```
GOOD:
```rust
let port = env::var("PORT")?.parse::<u16>()?;
```

### 9.4 Unbounded Lifetimes
BAD:
```rust
fn first(text: &String) -> &'static str { &text[0] }
```
GOOD:
```rust
fn first(text: &str) -> &str { &text[0] }
```

## 10. Verification Checklist
36. Confirm ownership, mutability, and lifetimes with the compiler, not prose.
37. Search for `unwrap`, `expect`, `panic!`, `unsafe`, and ignored results.
38. Test empty input, malformed external data, cancellation, and error paths.
39. Report commands run and their results; do not claim unrun verification.

## 11. Response to Violation
When a violation is found, stop before changing unrelated code. State the
file and symbol, name the violated rule, explain the concrete failure mode,
then propose the smallest safe correction. Preserve the public contract and
reference this file rather than restating universal rules. If the requested
behavior requires a new dependency or a breaking API change, stop and seek
explicit approval.
