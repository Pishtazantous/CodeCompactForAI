---
id: 02-csharp-anti-slop
title: "C# Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: language
version: 1
---

# C# Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
security anti-patterns, output format) are NOT repeated here.

This file covers rules specific to C#: nullable reference types,
async/await, LINQ, IDisposable, records, and the patterns that
produce deadlocks or resource leaks. Framework rules (ASP.NET Core)
live in `domains/framework/`.

## 1. Stack Assumptions

This layer assumes:

- .NET 8 or later.
- Nullable reference types enabled (`<Nullable>enable</Nullable>`).
- C# 12 or later.

## 2. Nullable Reference Types

### 2.1 Enable NRT Project-Wide

`<Nullable>enable</Nullable>` in the `.csproj`. Do not disable it in
files.

### 2.2 No `!` Without a Reason

The null-forgiving operator `!` tells the compiler to trust you.
Each use is a potential `NullReferenceException`.

BAD: `var name = user.Profile!.Name;`.
GOOD: Validate and handle:
```csharp
if (user.Profile is null) throw new InvalidOperationException();
var name = user.Profile.Name;
```

### 2.3 `?` for Maybe-Null

A method that may return `null` has `?`:
```csharp
public User? FindUser(string id) { ... }
```

A caller must handle `null`.

### 2.4 `ArgumentNullException.ThrowIfNull`

At public method boundaries:
```csharp
public void Process(User user)
{
    ArgumentNullException.ThrowIfNull(user);
    // ...
}
```

## 3. Async/Await

### 3.1 Async All the Way

BAD: `.Result` or `.Wait()` on a `Task` in a synchronous method.
GOOD: `await` from an `async` method.

`.Result` and `.Wait()` deadlock in UI and ASP.NET contexts.

### 3.2 `async Task` Over `async void`

BAD: `public async void DoWork()`.
GOOD: `public async Task DoWork()`.

`async void` exceptions are unobservable and crash the process.

Exception: event handlers, which are `async void` by signature.

### 3.3 `ConfigureAwait(false)` in Library Code

A library does not need to resume on the original context. Add
`ConfigureAwait(false)` in library code.

In ASP.NET Core applications, it is not needed (no synchronization
context).

### 3.4 `Task.Run` Is Not for Async I/O

BAD: `await Task.Run(() => httpClient.GetAsync(url))`.
GOOD: `await httpClient.GetAsync(url)`.

`Task.Run` moves work to a thread pool thread. Async I/O does not
need a thread.

### 3.5 Cancel Long-Running Operations

Every `async` method that may run long accepts a
`CancellationToken` and passes it down.

### 3.6 `ValueTask` for Hot Paths

`ValueTask` avoids allocation when the result is often synchronous.
Do not `await` a `ValueTask` more than once.

## 4. LINQ

### 4.1 LINQ for Transformations

Covered by examples below.

### 4.2 Deferred Execution

A LINQ query is not executed until it is enumerated. A query that
captures a mutable collection reflects changes until enumeration.

BAD:
```csharp
var query = items.Where(x => x.Active);
items.Add(newItem);  // query now includes newItem if not yet enumerated
```

If you need a snapshot, call `.ToList()`.

### 4.3 Multiple Enumeration

BAD:
```csharp
if (query.Any()) { var list = query.ToList(); }
```

The query is executed twice.

GOOD:
```csharp
var list = query.ToList();
if (list.Count > 0) { ... }
```

### 4.4 `.Count() > 0` Over `.Any()`

BAD: `if (query.Count() > 0)`.
GOOD: `if (query.Any())`.

`Count()` enumerates the entire sequence. `Any()` stops at the first.

### 4.5 `.Where(...).First()` Over `.First(...)`

BAD: `items.Where(x => x.Id == id).First()`.
GOOD: `items.First(x => x.Id == id)`.

### 4.6 No LINQ on Hot Paths Without Measurement

LINQ allocates iterators and closures. In tight loops, a `foreach`
over a `List<T>` is faster.

### 4.7 `AsNoTracking` for EF Core Reads

EF Core tracks entities by default. For read-only queries, add
`.AsNoTracking()`.

## 5. IDisposable

### 5.1 `using` for Every `IDisposable`

BAD: `var stream = File.OpenRead(path);`.
GOOD: `using var stream = File.OpenRead(path);`.

Dispose is called at the end of the scope.

### 5.2 `using` Declarations Over `using` Blocks

BAD:
```csharp
using (var stream = File.OpenRead(path))
{
    // ...
}
```

GOOD:
```csharp
using var stream = File.OpenRead(path);
// ...
```

### 5.3 Dispose in the Right Order

Dispose nested resources in reverse order of creation.

### 5.4 `IAsyncDisposable` for Async Cleanup

`await using var resource = ...` for `IAsyncDisposable`.

### 5.5 Dispose Pattern

A class with unmanaged resources implements `IDisposable` with the
full pattern:

```csharp
public sealed class Resource : IDisposable
{
    private bool _disposed;
    public void Dispose()
    {
        if (_disposed) return;
        _disposed = true;
        // dispose managed resources
        GC.SuppressFinalize(this);
    }
}
```

If the class has no unmanaged resources and is not a base class, a
simple `Dispose` is enough.

## 6. Records

### 6.1 `record` for Immutable Data

BAD: A class with a constructor and equality methods written by
hand.
GOOD: `public record User(string Id, string Email);`.

### 6.2 `record struct` for Small Value Types

For small, immutable value types that would otherwise be a struct
with equality.

### 6.3 `with` for Non-Destructive Mutation

```csharp
var updated = user with { Email = "new@example.com" };
```

The original `user` is unchanged.

### 6.4 No `record` With Mutable Collections

A record with a `List<T>` field is not truly immutable. Use an
immutable collection (`ImmutableList<T>`, `IReadOnlyList<T>`).

## 7. Dependency Injection

### 7.1 Constructor Injection

BAD:
```csharp
public class UserService
{
    [Inject] public IUserRepository Repo { get; set; }
}
```

GOOD:
```csharp
public class UserService
{
    private readonly IUserRepository _repo;
    public UserService(IUserRepository repo) => _repo = repo;
}
```

### 7.2 Correct Lifetime

- `Transient`: new instance per request.
- `Scoped`: one per request.
- `Singleton`: one for the application.

A `Singleton` that depends on a `Scoped` service is a captive
dependency bug.

### 7.3 `IOptions<T>` for Configuration

BAD: Reading `IConfiguration` directly everywhere.
GOOD: A strongly-typed `IOptions<MyOptions>`.

### 7.4 No Service Locator

BAD: `serviceProvider.GetService<UserService>()` in business code.
GOOD: Inject the dependency.

## 8. C#-Specific Anti-Patterns

### 8.1 `.Result` on `Task`

Covered in 3.1.

### 8.2 `async void`

Covered in 3.2.

### 8.3 Not Disposing `IDisposable`

Covered in 5.1.

### 8.4 Multiple Enumeration

Covered in 4.3.

### 8.5 `.Count() > 0`

Covered in 4.4.

### 8.6 Catching `Exception` Blindly

BAD: `catch (Exception) { }`.
GOOD: Catch specific exceptions.

### 8.7 `Thread.Sleep` in Async

BAD: `Thread.Sleep(1000)` in an async method.
GOOD: `await Task.Delay(1000)`.

`Thread.Sleep` blocks the thread; `Task.Delay` releases it.

### 8.8 `lock` on a Public Object

BAD: `lock (this)` or `lock (typeof(MyClass))`.
GOOD: A private `readonly object _lock = new();`.

### 8.9 String Concatenation in Loops

BAD: `string s = ""; for (...) s += x;`.
GOOD: `var sb = new StringBuilder();`.

### 8.10 `==` for Strings Without `StringComparison`

BAD: `if (name == "Alice")`.
GOOD: `if (name.Equals("Alice", StringComparison.Ordinal))` or
`.Equals(..., StringComparison.OrdinalIgnoreCase)`.

The default `==` uses ordinal for strings in C#, which is correct
for internal comparisons. For user-facing or case-insensitive
comparisons, be explicit.

### 8.11 `DateTime.Now`

BAD: `DateTime.Now` (local time).
GOOD: `DateTime.UtcNow` or `DateTimeOffset.UtcNow`.

### 8.12 `ToLower()` for Comparison

BAD: `if (name.ToLower() == "alice")`.
GOOD: `if (string.Equals(name, "alice", StringComparison.OrdinalIgnoreCase))`.

`ToLower` allocates and depends on the current culture.

### 8.13 Ignoring `CancellationToken`

Covered in 3.5.

### 8.14 `Task.Run` for I/O

Covered in 3.4.

### 8.15 `ConfigureAwait(true)` in Libraries

Covered in 3.3.

### 8.16 Overusing `dynamic`

`dynamic` bypasses compile-time checks and is slow. Use it only for
interop with COM or dynamic languages.

### 8.17 `var` Everywhere

`var` is fine when the type is obvious from the right-hand side. Not
when it is not.

BAD: `var result = Process();` where `Process` returns an unclear
type.
GOOD: `ProcessResult result = Process();`.

### 8.18 Magic Strings in Attribute Usage

BAD: `[Route("api/users")]` repeated.
GOOD: Constants or a route convention.

### 8.19 Mutating Structs

A struct is a value type. Mutating a copy does not affect the
original.

BAD: `list[0].Increment()` where `Increment` mutates the struct.
GOOD: `list[0] = list[0].Incremented()`.

### 8.20 `IEnumerable<T>` Returned From Hot Paths

A method returning `IEnumerable<T>` may hide deferred execution and
multiple enumeration. Return `IReadOnlyList<T>` or `T[]` when the
result is materialized.

### 8.21 `try`/`catch` for Control Flow

BAD: Using exceptions for expected conditions.
GOOD: `TryParse`, `TryGetValue`, or explicit checks.

### 8.22 Not Disposing `HttpClient`

BAD: `using var client = new HttpClient();` per request.
GOOD: A single `HttpClient` (or `IHttpClientFactory`) for the app's
lifetime.

`HttpClient` is designed to be reused.

### 8.23 `GC.Collect` in Production

Manual GC collection is almost never correct. Let the runtime decide.

### 8.24 Ignoring Warnings

The compiler's nullable and analyzer warnings are not noise. Fix
them or suppress with a reason.

### 8.25 `string.Format` Over Interpolation

BAD: `string.Format("Hello {0}", name)`.
GOOD: `$"Hello {name}"`.

## 9. Response to Violation

If a previous response violated a rule here:

```
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

No justification. No apology paragraph. Fix and move on.
