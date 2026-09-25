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

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
security anti-patterns, output format) are NOT repeated here.

This file covers rules specific to Java and Kotlin: type system,
nullability, dependency injection, exceptions, concurrency, and the
patterns that produce bloated or fragile code. Framework rules
(Spring Boot, Android) live in `domains/framework/`.

## 1. Stack Assumptions

This layer assumes:

- Java 17 or later, or Kotlin 1.9 or later.
- Maven or Gradle for builds.
- The project uses a standard formatter (Spotless, ktlint).

## 2. Type System

### 2.1 Prefer Immutability

BAD: A mutable class with setters for every field.
GOOD: A `record` (Java) or a `data class` (Kotlin) with `val` fields.

Java:
```java
public record User(String id, String email, Role role) {}
```

Kotlin:
```kotlin
data class User(val id: String, val email: String, val role: Role)
```

### 2.2 `final` by Default (Java)

In Java, mark classes `final`, methods `final`, and fields `final`
unless extension or mutation is intended.

BAD: A public non-final class with public non-final fields.
GOOD: `public final class User { private final String id; ... }`

### 2.3 Kotlin `val` Over `var`

BAD: `var name = "Alice"` when `name` is never reassigned.
GOOD: `val name = "Alice"`.

### 2.4 Sealed Hierarchies Over Enums With Data

BAD: An enum where some values carry data and others do not.
GOOD: A sealed interface/class with subtypes.

Kotlin:
```kotlin
sealed interface Result<out T> {
    data class Ok<T>(val value: T) : Result<T>
    data class Err(val error: Throwable) : Result<Nothing>
}
```

### 2.5 Generics Are Not `Object`

BAD: `List<Object> items`.
GOOD: `List<Item> items` or `List<? extends Item> items`.

### 2.6 Wildcards Only When Necessary

Java: `List<? extends Number>` for read-only. `List<? super Integer>`
for write-only. Otherwise, use the exact type.

### 2.7 No Raw Types

BAD: `List items = new ArrayList();`.
GOOD: `List<Item> items = new ArrayList<>();`.

## 3. Nullability

### 3.1 Java: `Optional` at API Boundaries

BAD: `public User findUser(String id) { return null; }`.
GOOD: `public Optional<User> findUser(String id) { ... }`.

`Optional` is for return types. Do not use it for fields or method
parameters.

### 3.2 Java: `@Nullable` and `@NonNull`

Use JSR-305 or the project's nullability annotations consistently.

BAD: A method that sometimes returns `null` and is not annotated.
GOOD: `@Nullable User findUser(...)` or `Optional<User> findUser(...)`.

### 3.3 Kotlin: No `!!` Except When Proven

BAD: `val id = user.id!!`.
GOOD: `val id = user.id ?: throw IllegalStateException("user id missing")`
or `requireNotNull(user.id) { "user id missing" }`.

`!!` throws `NullPointerException` with no context.

### 3.4 Kotlin: Platform Types

Calling Java from Kotlin produces platform types (`String!`). They
can be `null` at runtime. Treat them as nullable and handle
explicitly.

### 3.5 Kotlin: Smart Casts

Use `val` and pattern matching to enable smart casts.

BAD:
```kotlin
if (x is String) {
    println(x.length)  // works only if x is a val
}
```

GOOD:
```kotlin
val x: Any = ...
if (x is String) {
    println(x.length)  // smart cast to String
}
```

## 4. Dependency Injection

### 4.1 Constructor Injection Only

BAD:
```java
public class UserService {
    @Autowired private UserRepository repo;
}
```

GOOD:
```java
public class UserService {
    private final UserRepository repo;
    public UserService(UserRepository repo) { this.repo = repo; }
}
```

Field injection hides dependencies, prevents immutability, and
complicates testing.

### 4.2 No Service Locator

BAD: `ServiceLocator.get(UserService.class)`.
GOOD: Constructor injection.

### 4.3 One Constructor Per Bean

If a class has multiple constructors, mark one with `@Autowired`
(Spring) or the framework's annotation.

### 4.4 No Circular Dependencies

BAD: `A` depends on `B`, `B` depends on `A`.
GOOD: Extract a third class, or restructure.

Circular dependencies are a design smell, not a framework limitation.

## 5. Exceptions

### 5.1 Unchecked Over Checked (Modern Java)

Checked exceptions clutter signatures. Modern Java projects prefer
unchecked exceptions for all but recoverable cases.

BAD: `throws IOException, SQLException, ParseException` on every
method.
GOOD: Wrap in an unchecked domain exception at the boundary.

### 5.2 Never Catch `Exception` Blindly

BAD: `try { ... } catch (Exception e) { log(e); }`.
GOOD: Catch specific exceptions, or let the framework handle them.

### 5.3 Never Swallow

BAD: `catch (IOException e) { }`.
GOOD: Log and rethrow, or convert and rethrow.

### 5.4 Never `printStackTrace`

BAD: `e.printStackTrace();`.
GOOD: `log.error("...", e);` through the project's logger.

### 5.5 Custom Exception Hierarchies

```java
public class AppException extends RuntimeException { ... }
public class NotFoundException extends AppException { ... }
public class ValidationException extends AppException { ... }
```

Consistent hierarchy allows centralized handling.

### 5.6 Kotlin: No Checked Exceptions

Kotlin does not have checked exceptions. Do not pretend it does.

### 5.7 Kotlin: `runCatching` With Care

`runCatching` catches `Throwable`, including `Error` subtypes. Do
not use it for control flow or to swallow programming errors.

## 6. Concurrency

### 6.1 Prefer Executors Over Raw Threads

BAD: `new Thread(() -> ...).start();`.
GOOD: `executor.submit(() -> ...);`.

### 6.2 Bounded Thread Pools

BAD: `Executors.newCachedThreadPool()` (unbounded).
GOOD: `new ThreadPoolExecutor(core, max, ...)` with a queue.

### 6.3 Shut Down Executors

An executor that is never shut down prevents JVM exit. Call
`shutdown()` and `awaitTermination()`.

### 6.4 `CompletableFuture` Over `Future.get`

BAD: `future.get()` blocks.
GOOD: `future.thenApply(...).thenAccept(...)`.

### 6.5 Kotlin Coroutines

- Structured concurrency: use `coroutineScope` or `supervisorScope`.
- Never `GlobalScope.launch` in application code.
- Pass the `CoroutineContext` explicitly.
- Cancellation is cooperative: check `isActive` or use cancellable
  operations.

BAD: `GlobalScope.launch { ... }`.
GOOD: `viewModelScope.launch { ... }` or a scoped coroutine.

### 6.6 Thread-Safe Collections

`HashMap` is not thread-safe. Use `ConcurrentHashMap` or synchronize
access.

### 6.7 `volatile` When Visibility Matters

A field read by multiple threads without synchronization requires
`volatile` or an `Atomic*` type.

## 7. Collections and Streams

### 7.1 Streams Over Loops for Transformations

BAD:
```java
List<String> names = new ArrayList<>();
for (User u : users) {
    if (u.active()) names.add(u.name());
}
```

GOOD:
```java
List<String> names = users.stream()
    .filter(User::active)
    .map(User::name)
    .toList();
```

### 7.2 Streams Are Not for Side Effects

BAD: `users.stream().forEach(this::sendEmail);`.
GOOD: A `for` loop.

`forEach` in a stream is a smell unless the stream is a terminal
operation that is genuinely terminal.

### 7.3 Avoid `Collectors.toList()` (Java 16+)

Use `.toList()` when an unmodifiable list is acceptable. Use
`Collectors.toCollection(ArrayList::new)` when mutability is needed.

### 7.4 Kotlin Collections

Use the standard operators (`filter`, `map`, `flatMap`, `associate`)
over manual loops. Use sequences (`asSequence()`) for chains over
large collections.

### 7.5 No `null` Elements in Collections

A `List<String>` that sometimes contains `null` forces every caller
to check. Use an empty list or a sentinel value.

## 8. Java & Kotlin Anti-Patterns

### 8.1 `null` Return for "Not Found"

Covered in 3.1.

### 8.2 Field Injection

Covered in 4.1.

### 8.3 Catching `Exception`

Covered in 5.2.

### 8.4 `printStackTrace`

Covered in 5.4.

### 8.5 `newCachedThreadPool`

Covered in 6.2.

### 8.6 `GlobalScope.launch` in Kotlin

Covered in 6.5.

### 8.7 `!!` in Kotlin

Covered in 3.3.

### 8.8 Mutable Static State

BAD: `public static final Map<String, User> CACHE = new HashMap<>();`.
GOOD: An injected cache with explicit lifecycle, or a
`ConcurrentHashMap` with synchronization.

### 8.9 Deep Inheritance Hierarchies

BAD: `AbstractBaseServiceImpl` → `AbstractServiceImpl` → `UserServiceImpl`.
GOOD: Composition and small interfaces.

### 8.10 `interface` With a Single Implementation

A single-implementation interface is a design smell unless the
interface is part of a public API.

### 8.11 `equals`/`hashCode` Mismatch

BAD: Overriding `equals` without `hashCode`.
GOOD: Both, or neither (use `record` / `data class`).

### 8.12 Mutable Fields in `record` / `data class`

BAD: A `record` with a `List` field that is mutated by callers.
GOOD: Defensive copies in the constructor, or immutable collections.

### 8.13 `Optional` as a Field

BAD: `private Optional<String> name;`.
GOOD: `private String name;` with a nullable-aware accessor.

### 8.14 `Optional.get()` Without Check

BAD: `optional.get()` (throws if empty).
GOOD: `optional.orElseThrow(() -> new NotFoundException(...))`.

### 8.15 Overly Broad Imports

BAD: `import com.example.*;`.
GOOD: Explicit imports.

### 8.16 Multiple `@Autowired` on One Class

If a class has more than one `@Autowired` field or setter, refactor
to constructor injection.

### 8.17 Ignoring `@Override`

BAD: A method that overrides a superclass method without
`@Override`.
GOOD: Always annotate.

### 8.18 String Concatenation in Loops

BAD: `String s = ""; for (...) s += x;`.
GOOD: `StringBuilder sb = new StringBuilder(); sb.append(x);`.

### 8.19 Boxing in Hot Paths

BAD: `List<Integer>` in a loop over primitives.
GOOD: `int[]` or a primitive stream.

### 8.20 `synchronized` on a Public Object

BAD: `synchronized (this) { ... }` where `this` is exposed.
GOOD: A private final lock object.

### 8.21 `equals` Without Type Check

BAD: `public boolean equals(Object o) { return ((User) o).id.equals(id); }` (ClassCastException).
GOOD: `if (!(o instanceof User u)) return false; return u.id.equals(id);`.

### 8.22 Kotlin `lateinit` Without a Reason

BAD: `lateinit var user: User` when the value could be a
constructor parameter.
GOOD: Constructor parameter, or `by lazy`, or a nullable with an
explicit check.

### 8.23 Kotlin `apply`/`also`/`let`/`run` Overuse

A chain of `apply { also { let { run { ... } } } }` is unreadable.
Use them for short, idiomatic expressions, not for long flows.

### 8.24 Kotlin `when` Without `else` on a Non-Sealed Type

BAD:
```kotlin
when (x) {
    is A -> ...
    is B -> ...
}
```
where `x` is not sealed.

GOOD: Add `else`, or make the type sealed.

### 8.25 Java Records for Mutable Types

A `record` is immutable by design. If the type must be mutable, use
a class.

## 9. Response to Violation

If a previous response violated a rule here:

```
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

No justification. No apology paragraph. Fix and move on.
