---
id: 02-swift-anti-slop
title: "Swift Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: language
version: 1
---
# Swift Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. This layer covers Swift
value semantics, optionals, concurrency, and UI-independent APIs. Framework
and platform rules remain separate.

## 1. Scope and Assumptions
1. Read Package.swift, project settings, deployment targets, and existing
   concurrency configuration before selecting an API.
2. Match the project's Swift language mode and platform availability. Do not
   assume a modern actor, macro, or concurrency feature is enabled.
3. Keep access control and API stability consistent with the package.

## 2. Optionals and Force Unwrapping
4. Every force unwrap, implicitly unwrapped optional, and `try!` is a claim
   that failure is impossible. Production code must instead handle or narrow
   the failure.
5. Use `guard let` or `if let` at boundaries that can be absent. Do not pass
   optional values through multiple layers before checking them.
6. Use `try?` only when absence is an intentional domain outcome and the result
   type remains clear. Do not discard an error with `try!` or `try?`.
7. Distinguish an absent value from a thrown failure; do not map every error to
   `nil` without a documented decision.

## 3. Ownership and Retain Cycles
8. Use structs for value-shaped data and classes only when identity or shared
   mutable state is required.
9. Closures stored on an object must have an explicit ownership plan. Mark
   `weak` or `unowned` only when the owner is designed to outlive the closure
   or the closure must not retain it.
10. Do not use `unowned` as a convenient replacement for a weak reference;
    it can crash when the referenced object is gone.

## 4. Actors and Concurrency
11. An actor protects mutable state; it is not a general replacement for a
    lock. Keep actor state minimal and name its invariant.
12. Use async functions at I/O boundaries and propagate `CancellationError` and
    task cancellation. Do not hide cancellation with a broad catch.
13. Do not use `Task.detached` to avoid an actor hop. Detached tasks lose
    priority, task-local values, and actor context; use them only for truly
    independent work.
14. Keep `MainActor` isolation at the UI boundary, not on domain services that
    do not touch UI state.
15. Avoid concurrent mutable collections. Choose a safe value or place mutation
    behind a single owner.

## 5. Property Wrappers
16. Use a property wrapper when it centralizes a proven invariant, such as
    dependency storage or validated state. Do not wrap a property merely to
    shorten its declaration.
17. Expose wrapped types and projected values deliberately. A wrapper whose
    projected value is an implementation detail must not become public API by
    accident.
18. Keep wrapped state access on the correct actor or isolation domain.

## 6. Value Semantics and Copying
19. Prefer `let` and immutable structs. Use `var` only for intentional local
    mutation; do not make a value mutable just to satisfy a legacy API.
20. Treat `Data`, `String`, and collection values according to copy-on-write
    behavior; do not assume a copy always duplicates bytes.
21. Do not use `inout` for a hidden mutation. Document whether a function can
    consume, retain, or alias its argument.

## 7. Memory and Resources
22. Use `defer` for cleanup on every path, but prefer scoped APIs when the
    language provides them.
23. Avoid `unowned` temporary values in closures and deinitializers. Check the
    lifetime of every callback retained beyond the current call.
24. Do not use Objective-C runtime tricks or `unsafeBitCast` to bypass Swift's
    type system in new code.

## 8. API and Style Rules
25. Use `snake_case` for values and functions, `UpperCamelCase` for types, and
    follow the project's access-control and naming conventions.
26. Mark public APIs and non-obvious generic constraints with concise English
    documentation. Do not document what the signature already proves.
27. Use a protocol when multiple concrete types need the same behavior and
    ownership is not the primary concern. Do not create a protocol for one
    implementation without a boundary reason.
28. Do not add packages or enable experimental language features without
    explicit permission.

34. Confirm that every stored delegate has a defined owner and lifetime.
35. Verify that task properties propagate the intended actor and priority.
36. Exercise missing optionals, thrown errors, and cancellation paths.
37. Check access control before exposing a property wrapper's projected value.
39. Test actor reentrancy and task cancellation under contention.
40. Review weak or unowned captures against object destruction order.
41. Keep main-actor annotations at the actual presentation boundary.
42. Record deployment-target and analyzer results.

42. Inspect stored delegates for reference cycles.
43. Test actor reentry and cancellation under contention.
44. Check property wrappers for exposed implementation details.
45. Confirm concurrency annotations match deployment targets.
46. Verify every optional boundary handles absence explicitly.
47. Review task priorities and actor inheritance.
48. Run the configured formatter, analyzer, and tests.
49. Record actual verification results.

## Domain-Specific Anti-Patterns

### 9.1 Crash as Validation
BAD:
```swift
let id = response.value!.id
return try! decoder.decode(User.self, from: data)
```
GOOD:
```swift
guard let value = response.value else { throw AppError.invalidResponse }
return try decoder.decode(User.self, from: data)
```

### 9.2 Retain Cycles
BAD:
```swift
final class Screen {
    var onSave: (() -> Void)?
    func install() { onSave = { [self] in save() } }
}
```
GOOD:
```swift
final class Screen {
    var onSave: (() -> Void)?
    func install() { onSave = { [weak self] in self?.save() } }
}
```

### 9.3 Unmanaged Tasks
BAD:
```swift
func refresh() { Task.detached { await self.load() } }
```
GOOD:
```swift
@MainActor
func refresh() { Task { await model.load() } }
```

## 10. Verification Checklist
29. Repeated `DispatchQueue.main.async` calls are not a concurrency model; fix
    the ownership and isolation design instead.
30. `NotificationCenter` observers and task callbacks must have a clear
    cancellation or lifecycle policy.
31. Run the project's formatter, analyzer, and tests for the supported target.
32. Search for `!`, `try!`, `as!`, `unowned`, and `Task.detached` before review.
33. Exercise cancellation, missing optionals, actor contention, and deinit paths.

## 11. Response to Violation
Name the file and symbol, cite the numbered rule, and describe the crash or
concurrency failure it prevents. Make the smallest safe change, preserving
API compatibility. Do not repeat universal guidance. If fixing the issue
requires a deployment-target change, new dependency, or public API break,
stop and state that impact before editing.
