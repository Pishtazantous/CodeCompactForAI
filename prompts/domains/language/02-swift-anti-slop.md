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

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
security anti-patterns, output format) are NOT repeated here.

This file covers rules specific to Swift: optionals, value semantics,
memory management, concurrency, and the patterns that produce crashes
or retain cycles. Framework rules (SwiftUI, UIKit) live in
`domains/framework/`.

## 1. Stack Assumptions

This layer assumes:

- Swift 5.9 or later.
- Swift Package Manager or Xcode for builds.
- Swift Concurrency (async/await, actors) is available.

## 2. Optionals

### 2.1 No Force Unwrap in Production

BAD: `let name = user.name!`.
GOOD: `guard let name = user.name else { return }`.

Force unwrap crashes on `nil`. Every `!` is a potential crash.

### 2.2 `guard let` for Early Exit

BAD:
```swift
if let name = user.name {
    // 50 lines of code
}
```

GOOD:
```swift
guard let name = user.name else { return }
// 50 lines of code
```

### 2.3 `if let` for Conditional Logic

When the branch is short or there is an alternative, `if let` is fine.

### 2.4 Nil-Coalescing Over Force Unwrap

BAD: `let name = user.name!`.
GOOD: `let name = user.name ?? "Guest"`.

### 2.5 Optional Chaining

BAD:
```swift
if user != nil {
    if user!.profile != nil {
        print(user!.profile!.bio)
    }
}
```

GOOD: `print(user?.profile?.bio ?? "no bio")`.

### 2.6 `try?` Swallows Errors

BAD: `let data = try? load()` without checking `nil`.
GOOD: `do { let data = try load() } catch { ... }`.

`try?` discards the error. It is acceptable only when the error is
genuinely irrelevant.

### 2.7 `try!` Is Almost Never Correct

`try!` crashes on any thrown error. Use it only in tests or when the
error is truly impossible.

## 3. Value vs Reference Semantics

### 3.1 Structs for Values

Use `struct` for types that represent a value: a point, a user, a
configuration.

### 3.2 Classes for Identity

Use `class` when two references must share state, or when the type
has a lifecycle (a view controller, a network client).

### 3.3 Enum With Associated Values for State

```swift
enum LoadingState {
    case idle
    case loading
    case loaded(User)
    case failed(Error)
}
```

Better than a struct with multiple optional fields.

### 3.4 Mutating Methods on Structs

A method that changes a struct's state is marked `mutating`:

```swift
struct Counter {
    var value = 0
    mutating func increment() { value += 1 }
}
```

### 3.5 No Reference Types in Structs Without a Reason

A struct with a `class` field shares reference semantics through
that field. Use value types consistently.

## 4. Memory Management

### 4.1 `weak` for Delegates

A delegate is `weak`:

```swift
protocol UserServiceDelegate: AnyObject { ... }
class UserService {
    weak var delegate: UserServiceDelegate?
}
```

Without `weak`, the delegate relationship creates a retain cycle.

### 4.2 `[weak self]` in Closures

A closure that captures `self` strongly creates a retain cycle if
`self` holds the closure.

BAD:
```swift
service.fetch { result in
    self.update(result)  // strong capture
}
```

GOOD:
```swift
service.fetch { [weak self] result in
    self?.update(result)
}
```

### 4.3 `unowned` When the Lifetime Is Guaranteed

`unowned` is like `weak` but crashes if the object is deallocated.
Use it when the captured object's lifetime is guaranteed to outlive
the closure.

Use `unowned` sparingly. `weak` with `guard let` is safer.

### 4.4 No Retain Cycles in Closures

Covered in 4.2.

### 4.5 `deinit` for Cleanup

`deinit` is for invalidating timers, removing observers, and closing
resources.

### 4.6 No `deinit` for State

`deinit` should not have side effects beyond cleanup.

## 5. Concurrency

### 5.1 Structured Concurrency

Use `async let` and `TaskGroup` for parallel work:

BAD:
```swift
let a = await fetchA()
let b = await fetchB()
```

GOOD:
```swift
async let a = fetchA()
async let b = fetchB()
let (resultA, resultB) = await (a, b)
```

### 5.2 `Task` for Unstructured Work

Use `Task { }` for fire-and-forget work. Capture `[weak self]` when
referencing `self`.

### 5.3 `Task.detached` Rarely

`Task.detached` inherits no context. Use it only when you explicitly
want no inheritance.

### 5.4 Actors for Shared Mutable State

```swift
actor Counter {
    private var value = 0
    func increment() -> Int {
        value += 1
        return value
    }
}
```

Callers use `await counter.increment()`.

### 5.5 `@MainActor` for UI

Every UI update is on `@MainActor`. A `Task` that updates UI is
`@MainActor` or calls `await MainActor.run { ... }`.

### 5.6 No Blocking on the Main Thread

Synchronous network calls, file I/O, and heavy computation happen
off the main thread.

### 5.7 Cancellation

Check `Task.isCancelled` or call `try Task.checkCancellation()` in
long loops.

## 6. Collections

### 6.1 `map`, `filter`, `reduce`

Use the standard library's transformations.

BAD:
```swift
var names: [String] = []
for user in users {
    if user.active { names.append(user.name) }
}
```

GOOD:
```swift
let names = users.filter(\.active).map(\.name)
```

### 6.2 Key Paths

`\.active` and `\.name` are shorter and clearer than closures.

### 6.3 `first(where:)` Over `filter().first`

BAD: `users.filter { $0.active }.first`.
GOOD: `users.first { $0.active }`.

The first version processes the entire array.

### 6.4 `compactMap` for Optional Transformation

BAD:
```swift
let ids = users.map { $0.id }.filter { $0 != nil }.map { $0! }
```

GOOD:
```swift
let ids = users.compactMap { $0.id }
```

### 6.5 `Dictionary(grouping:by:)`

BAD: Manually grouping.
GOOD: `Dictionary(grouping: users, by: \.role)`.

## 7. Protocols and Extensions

### 7.1 Protocol-Oriented Design

Prefer protocols over inheritance. A protocol with a small method
surface is easier to compose.

### 7.2 Protocol Extensions for Defaults

```swift
protocol Greeter {
    func greet() -> String
}
extension Greeter {
    func greet() -> String { "Hello" }
}
```

### 7.3 No Protocol for a Single Type

A protocol with one conforming type is overhead unless it is
public API.

### 7.4 Associated Types

A protocol with associated types cannot be used as a type directly.
Use `some` or `any` (Swift 5.7+).

BAD: `var items: [Collection]` (compile error).
GOOD: `var items: [any Collection]` or `some Collection`.

### 7.5 `extension` for Organization

Group related methods in `extension`s. Do not put all methods in the
main type declaration.

## 8. Swift-Specific Anti-Patterns

### 8.1 Force Unwrap

Covered in 2.1.

### 8.2 `try!`

Covered in 2.7.

### 8.3 Retain Cycles

Covered in 4.

### 8.4 `!` on IBOutlets

A `@IBOutlet` that is never connected crashes on first access.
Verify connections, or use `@IBOutlet weak var` and handle `nil`.

### 8.5 Global Mutable State

BAD: `var currentUser: User?` at file scope.
GOOD: A dependency injected into the type that needs it, or an
`@MainActor` observable object.

### 8.6 String Concatenation in Loops

BAD: `var s = ""; for x in items { s += x }`.
GOOD: `items.joined()` or a `String` builder pattern.

### 8.7 `NSObject` Inherited Without Need

An `NSObject` subclass pays for Objective-C runtime overhead. Use
plain Swift types unless the type must interoperate with Objective-C
or KVO.

### 8.8 `@objc` Everywhere

`@objc` exposes the symbol to the Objective-C runtime. Use it only
when necessary.

### 8.9 `AnyObject` in Protocols by Default

BAD: `protocol UserService: AnyObject`.
GOOD: `protocol UserService` unless reference semantics are
required (delegates).

### 8.10 `class` When `struct` Works

Covered in 3.1 and 3.2.

### 8.11 Optional Booleans

BAD: `var isActive: Bool?`.
GOOD: A three-state enum (`unknown`, `active`, `inactive`), or a
default value.

### 8.12 Implicitly Unwrapped Optionals in Non-UI Code

`var user: User!` is a crash waiting to happen. Use it only for
outlets that are guaranteed to be connected.

### 8.13 `DispatchQueue` Over Structured Concurrency

BAD: `DispatchQueue.global().async { ... }`.
GOOD: `Task { ... }` or an actor.

GCD is not wrong, but Swift Concurrency is safer and more readable
in new code.

### 8.14 `NotificationCenter` Without Removal

An observer that is not removed leaks. Use the block-based API with
a stored token, or the async sequence API.

### 8.15 `UserDefaults` for Everything

`UserDefaults` is for small preferences. Not for tokens (use
Keychain), not for large data (use a database or files).

### 8.16 `print` for Logging

BAD: `print("user logged in")`.
GOOD: `os.Logger` or the project's logging framework.

### 8.17 `Date()` for Business Logic

`Date()` depends on the system clock, which can be changed by the
user. For business logic, use a clock abstraction.

### 8.18 `Result` When `async throws` Is Available

BAD: A callback-based API with a `Result` parameter.
GOOD: An `async throws` function.

### 8.19 `throws` for Non-Recoverable Errors

A function that throws an error the caller cannot handle should
`fatalError` or `precondition`, not `throw`.

### 8.20 Overuse of `@escaping`

`@escaping` is for closures that outlive the function. Non-escaping
is the default and is faster.

## 9. Response to Violation

If a previous response violated a rule here:

```
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

No justification. No apology paragraph. Fix and move on.
