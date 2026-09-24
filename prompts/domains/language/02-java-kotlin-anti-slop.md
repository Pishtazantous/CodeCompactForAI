---
id: 02-java-kotlin-anti-slop
title: "Java & Kotlin Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: language
version: 1
---
# Java & Kotlin Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. This layer covers Java
and Kotlin contracts; framework and delivery rules remain in their own files.

## 1. Scope and Assumptions
1. Read `pom.xml`, Gradle files, or the project manifest before choosing a
   language feature, library, or runtime. Do not assume a dependency exists.
2. Match the module's Java and Kotlin versions, formatting, null-safety mode,
   and annotation processor settings.
3. Keep public APIs compatible with the configured binary and source level.

## 2. Nullability and Boundary Validation
4. In Java, make nullability explicit at APIs where practical. Never dereference
   a value whose provider did not establish non-null behavior.
5. In Kotlin, do not force an unsafe call to silence a platform type. Check the
   boundary or isolate the platform call behind a typed adapter.
6. Validate configuration, JSON, database rows, and user input at the edge.
   Do not let malformed values reach business logic.
7. Prefer early returns for null, invalid state, and unsupported operations.

## 3. Dependency Injection
8. Constructor-inject required dependencies. Do not reach through a global
   service locator or call a static factory from business logic.
9. Depend on the narrowest interface that expresses the required behavior.
   Do not inject an entire framework context for one small operation.
10. Keep scopes explicit: singleton, request, or feature scope is a lifecycle
    decision, not a convenience annotation.
11. In Kotlin, use a primary constructor with stable, immutable dependencies;
    do not mutate injected fields after initialization.

## 4. Exceptions and Error Types
12. Catch the narrowest exception that can be handled. Never use
    `catch (Exception)` as a substitute for a design decision.
13. Do not catch, log, and rethrow the same exception. Add context or let the
    boundary translate it once.
14. Never use checked exceptions for routine control flow across layers. A
    Java method should either declare a meaningful recovery contract or return
    a domain result appropriate to the language.
15. Preserve causes when wrapping an exception; do not replace a useful cause
    with a generic message.

## 5. Coroutines and Concurrency
16. Every coroutine scope has an owner and a cancellation reason. Do not create
    a scope in a class without a lifecycle or use `GlobalScope` in production.
17. Use structured concurrency: launch child work in the caller's scope and
    let failures cancel the operation.
18. Make dispatcher injection explicit at boundaries. Do not perform blocking
    I/O on a constrained UI dispatcher.
19. Use `withContext` for a bounded dispatcher change, not to hide blocking
    work in a supposedly non-blocking function.
20. Do not launch fire-and-forget work whose result or exception nobody owns.

## 6. Kotlin Idiom
21. Use `val` by default; use `var` only when reassignment is part of the
    state machine.
22. Prefer data classes for value objects, sealed interfaces for closed
    hierarchies, and exhaustive `when` expressions.
23. Use safe calls, elvis, and scope functions only when they preserve the
    intended null semantics. Do not hide a missing value in a default.
24. Keep extension functions focused and place them in the package that owns
    the concept; do not add broad `Any` extensions.
25. Name extension functions as operations, not as generic property accessors.

## 7. Collections and Concurrency
26. Prefer immutable collection types at API boundaries. Return a defensive
    copy when a Java or Kotlin API exposes mutable storage.
27. Do not use a synchronized collection to hide a multi-step invariant. State
    which lock or single-owner actor protects the invariant.
28. Keep transaction boundaries in the service layer and keep them short. Do
    not hold a transaction across remote calls.
29. Treat `ConcurrentHashMap` as a concurrent container, not as a solution to
    races involving multiple keys or related updates.

## 8. Java Interoperability
30. Do not expose platform types to Kotlin without an adapter and a test.
31. Mark nullable parameters explicitly in Java when the Kotlin boundary can
    return null; never rely on a non-null Java annotation that is not enforced.
32. Keep Java default methods and Kotlin interface defaults from creating
    ambiguous calls. Resolve overloads explicitly at the boundary.

40. Review collection ownership across the Java and Kotlin boundary so a
    mutable Java list is not exposed as an immutable Kotlin contract.
41. Check that every platform-type adapter has a test for null and absent data.
42. Keep coroutine exception handling at an ownership boundary rather than
    catching cancellation in every layer.
44. Review dependency scopes against request and process lifetimes.
45. Keep checked-exception translation in Java adapters, not domain rules.
46. Prefer exhaustive Kotlin `when` for closed state machines.
47. Exercise cancellation and failure propagation in coroutine tests.
48. Check resource closing under both Java and Kotlin ownership models.
49. Review public signatures for binary and source compatibility.
50. Keep suppression annotations specific and explain their reason.

## Domain-Specific Anti-Patterns

### 9.1 Implicit Null Contracts
BAD:
```kotlin
val name = user.getName().trim()
return name
```
GOOD:
```kotlin
val rawName = user.name ?: return Result.failure(InvalidUser)
return Result.success(rawName.trim())
```

### 9.2 Swallowed Failures
BAD:
```java
try { repository.save(order); }
catch (Exception ignored) { status = "saved"; }
```
GOOD:
```java
try { repository.save(order); }
catch (DataAccessException error) { throw new OrderWriteException(order.id(), error); }
```

### 9.3 Orphaned Coroutines
BAD:
```kotlin
fun start() { CoroutineScope(Dispatchers.IO).launch { send() } }
```
GOOD:
```kotlin
class Sender(private val scope: CoroutineScope) {
    fun start() = scope.launch { send() }
}
```

## 9. Resource and API Hygiene
33. Use try-with-resources or `use` for closeable resources. Close resources
    on every success and failure path.
34. Do not add a dependency or plugin without permission. Match the repository's
    dependency injection and logging conventions.
35. Use records for immutable Java data carriers and Kotlin data classes for
    Kotlin code, but do not make mutable domain entities records casually.

## 10. Verification Checklist
36. Compile with the configured Java and Kotlin toolchains and run existing
    static analysis and tests.
37. Review nullability, coroutine cancellation, transaction boundaries,
    and checked-exception translation.
38. Report exact commands and results. Do not claim a build passed unless it
    was actually run.
39. Check that no new dependency, coroutine scope, or exception suppression
    was introduced without a documented reason and test coverage.

## 11. Response to Violation
Identify the file, symbol, and violated numbered rule. Explain the runtime or
maintenance failure, then make the narrowest correction. Do not repeat the
master layer. If a nullability, DI, or API correction changes a public
contract, call that out before editing. Never hide a compiler, coroutine, or
static-analysis signal to make the change appear clean.
