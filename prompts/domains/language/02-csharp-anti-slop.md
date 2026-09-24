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

Layered under `_universal/00-master-anti-slop.md`. This layer covers C#
language and library contracts. Framework rules are maintained separately.

## 1. Scope and Assumptions
1. Read the project file, target framework, nullable setting, analyzers, and
   package manifest before choosing an API or language feature.
2. Match the project's C# language version and runtime. Do not assume a
   record, collection, or async feature is available without checking.
3. Preserve the existing style, namespaces, and public accessibility.

## 2. Nullable Reference Types
4. Treat a reference return as non-null only when its invariant is established.
   Validate external data and use nullable annotations for absence.
5. Do not use `null!` or a null-forgiving operator to silence a real uncertainty.
   Fix the contract or isolate the unsafe interop boundary.
6. Check `async` results and `Task` failures; a task that returns `null` must
   make that possibility visible to callers.

## 3. LINQ
7. Use LINQ for a clear transformation, filter, or aggregation over a known
   sequence. Do not nest query operators to hide multiple responsibilities.
8. Materialize a query only when the result is consumed more than once or the
   query is deferred across a changing source.
9. Prefer explicit loops when a query would enumerate an I/O-backed sequence
   multiple times, perform hidden work, or make a hot path less clear.
10. Do not use `Any` followed by `First` when a single `FirstOrDefault` and a
    clear branch express the operation. Do not mutate a collection while
    enumerating it.

## 4. Async and Concurrency
11. Every asynchronous method returns `Task` or `Task<T>` and is awaited by its
    caller unless the method explicitly owns a lifetime or is a fire-and-forget
    event handler.
12. Use `await` instead of `.Result` or `.Wait()`. Blocking a synchronization
    context can deadlock and hide cancellation.
13. Configure `ConfigureAwait(false)` only where the project already does so and
    the library genuinely needs it; do not add it mechanically.
14. Pass `CancellationToken` through the full asynchronous call chain and honor
    it at every cancellable boundary.
15. Do not use `async void` except for event handlers whose exceptions are
    handled by the host boundary.

## 5. IDisposable and Lifetime
16. Implement `IDisposable` or `IAsyncDisposable` when a type owns a resource.
    Dispose it exactly once on every path.
17. Use `using` or `await using` for scoped resources; do not rely on finalizers
    to release a live resource.
18. If a type contains disposable fields, document ownership and avoid disposing
    a dependency supplied by the caller.
19. Never call `GC.Collect` or `GC.WaitForPendingFinalizers` as normal cleanup.

## 6. Records and Value Semantics
20. Use a record for an immutable data carrier when its value equality is part
    of the contract. Do not use records for mutable entities with identity.
21. Prefer `init` and non-nullable required properties for construction-time
    invariants. Add a factory when validation must occur before creation.
22. Do not use a record's generated equality to compare domain entities when
    identity and business equality differ.

## 7. Exceptions and Results
23. Throw specific exceptions for programmer and framework failures. Return a
    result type for expected business outcomes when the caller must branch.
24. Do not catch `Exception` merely to log and rethrow. Preserve the inner
    exception and translate at one application boundary.
25. Never expose stack traces, connection strings, or sensitive exception text
    to an untrusted client.

## 8. General Idioms
26. Prefer `var` when the right-hand side makes the type obvious; use explicit
    types at public boundaries and when the type is the contract.
27. Use pattern matching for readable state handling, not to obscure a failed
    case with a catch-all.
28. Use cancellation-aware APIs, bounded queues, and timeouts for remote work.
29. Keep `async` naming accurate; a method containing `await` returns a task.
30. Avoid mutable static state. Static caches require an explicit invalidation
    and concurrency design.

40. Review LINQ enumerations for repeated database or network work, especially
    inside `Select`, `Where`, and nested query operators.
41. Confirm that `ConfigureAwait` matches the library policy and surrounding
    synchronization context rather than being added by habit.
42. Check async methods for a truthful return type and owned cancellation.
44. Verify that nullable annotations survive query and serialization boundaries.
45. Review deferred LINQ execution whenever the source can change.
46. Confirm that disposal ownership remains clear through wrappers.
47. Exercise async cancellation, empty results, and repeated enumeration.
48. Record actual analyzer and test output.

44. Review LINQ enumerations for repeated database or network work.
45. Check cancellation reaches HTTP, database, and queue calls.
46. Inspect disposable ownership through wrapper types.
47. Verify record immutability and equality semantics.
48. Review changed public signatures for compatibility.
49. Check LINQ predicates for null and empty behavior.
50. Confirm every task is awaited or intentionally owned.
51. Review analyzer suppressions for continued necessity.
52. Run the repository's configured analyzers and tests.
53. Record exact command output and exit status.
54. Exercise disposal, cancellation, and deferred enumeration.
55. Inspect static state for invalidation and races.
56. Keep exception translation at one application boundary.
57. Verify remote operations use bounded timeouts.
58. Check record constructors preserve domain invariants.
59. Review async event-handler exception behavior.
60. Confirm API results model absence explicitly.
61. Record each verification command and outcome.

## Domain-Specific Anti-Patterns

### 9.1 Nullable Collapse
BAD:
```csharp
public User GetUser(string id) => repository.Find(id);
```
GOOD:
```csharp
public User? GetUser(string id) => repository.Find(id);
```

### 9.2 Accidental N Plus One
BAD:
```csharp
foreach (var order in orders) Console.WriteLine(order.Customer.Name);
```
GOOD:
```csharp
var customers = await store.LoadCustomers(orders.Select(o => o.CustomerId));
foreach (var order in orders) Console.WriteLine(customers[order.CustomerId].Name);
```

### 9.3 Sync Over Async
BAD:
```csharp
var value = client.FetchAsync(id).Result;
```
GOOD:
```csharp
var value = await client.FetchAsync(id, cancellationToken);
```

## 10. Verification Checklist
31. Build for the configured target framework and run analyzers and tests.
32. Search for `.Result`, `.Wait()`, `null!`, ignored `Task`, and undisposed
    resources before review.
33. Exercise cancellation, null input, empty collections, and repeated async
    enumeration paths.
34. Report commands and outcomes precisely; do not claim unrun verification.

## 11. Response to Violation
State the file and symbol, identify the numbered rule, and explain the concrete
failure mode. Apply the smallest correction while preserving the public
contract. Refer to the master layer instead of repeating its rules. If a
nullable, async, or public API change is required, explain the compatibility
impact before editing and request approval when the task does not authorize it.
