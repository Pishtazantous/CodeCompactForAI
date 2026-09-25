---
id: 02-cpp-anti-slop
title: "C++ Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: language
version: 1
---

# C++ Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
security anti-patterns, output format) are NOT repeated here.

This file covers rules specific to C++: memory safety, modern C++
idioms, undefined behavior, and the patterns that produce crashes or
subtle corruption. Embedded C++ rules live in
`domains/delivery/02-embedded-anti-slop.md`.

## 1. Stack Assumptions

This layer assumes:

- C++17 or later. C++20 or C++23 preferred.
- A modern compiler (GCC 11+, Clang 14+, MSVC 19.30+).
- The project compiles with `-Wall -Wextra` (or equivalent) and
  treats warnings as errors in CI.

## 2. Memory Safety

### 2.1 RAII Everywhere

Every resource (memory, file, socket, lock) is owned by an object
whose destructor releases it.

BAD:
```cpp
auto* buf = new char[1024];
// ... may throw or return early
delete[] buf;
```

GOOD:
```cpp
auto buf = std::make_unique&lt;char[]&gt;(1024);
// released automatically
```

### 2.2 Smart Pointers Over Raw

- `std::unique_ptr&lt;T&gt;` for exclusive ownership.
- `std::shared_ptr&lt;T&gt;` for shared ownership.
- `std::weak_ptr&lt;T&gt;` to break cycles.
- Raw pointers only as non-owning observers.

### 2.3 `std::make_unique` and `std::make_shared`

BAD: `std::unique_ptr&lt;T&gt;(new T(...))`.
GOOD: `std::make_unique&lt;T&gt;(...)`.

`make_shared` allocates control block and object together.

### 2.4 No `delete`

If you write `delete`, something is wrong. Smart pointers call it for
you.

### 2.5 No `malloc`/`free` in C++

Use `new`/`delete` only inside smart pointer construction, or
containers. For raw memory, use `std::vector` or `std::array`.

### 2.6 `std::span` for Non-Owning Views

`std::span&lt;T&gt;` (C++20) replaces `(T* ptr, size_t len)` parameters.

### 2.7 No Naked `new`

Covered in 2.3.

### 2.8 Rule of Zero/Five

- **Rule of Zero**: if the class does not manage a resource, declare
  no special members.
- **Rule of Five**: if it does, declare destructor, copy constructor,
  copy assignment, move constructor, move assignment.

Do not declare one and forget the others.

## 3. Undefined Behavior

### 3.1 No Out-of-Bounds Access

- Use `.at()` for checked access, `operator[]` only when bounds are
  proven.
- `std::vector::at` throws; `operator[]` is UB on overflow.

### 3.2 No Use-After-Free

A pointer or reference to a destroyed object is UB.

BAD:
```cpp
auto&amp; ref = get_vector()[0];  // ref dangles if vector reallocates
```

### 3.3 No Dangling References

Returning a reference to a local is UB.

BAD:
```cpp
const std::string&amp; getName() {
    std::string name = "Alice";
    return name;  // dangling
}
```

GOOD: Return by value, or a reference to a member.

### 3.4 No Signed Overflow

Signed integer overflow is UB. Use unsigned for bit operations, or
check bounds.

### 3.5 No Null Dereference

A raw pointer may be null. Check before dereferencing.

### 3.6 No Uninitialized Reads

Every variable is initialized:

BAD: `int x; std::cout &lt;&lt; x;`.
GOOD: `int x = 0;` or `int x{};`.

### 3.7 No `reinterpret_cast` Without a Reason

`reinterpret_cast` bypasses the type system. Use it only for FFI or
serialization with documented layout.

### 3.8 `const_cast` Only at API Boundaries

Modifying a `const` object through `const_cast` is UB. Use it only
when a legacy API requires non-const but does not modify.

## 4. Modern C++ Idioms

### 4.1 `auto` When the Type Is Obvious

BAD: `auto x = 5;` is fine; `auto y = compute();` may hide the type.
GOOD: Explicit type when the type matters for readability.

### 4.2 Range-Based `for`

BAD:
```cpp
for (size_t i = 0; i &lt; vec.size(); ++i) {
    process(vec[i]);
}
```

GOOD:
```cpp
for (const auto&amp; item : vec) {
    process(item);
}
```

### 4.3 `const` by Default

Every variable, parameter, and method that does not mutate is
`const`.

### 4.4 `constexpr` Over `#define`

BAD: `#define MAX 100`.
GOOD: `constexpr int kMax = 100;`.

### 4.5 `enum class`

BAD: `enum Status { Active, Inactive };` (pollutes namespace).
GOOD: `enum class Status { Active, Inactive };`.

### 4.6 `nullptr` Over `NULL`/`0`

`nullptr` is type-safe.

### 4.7 `override` and `final`

Every overriding method is marked `override`. Classes not meant for
inheritance are `final`.

### 4.8 Move Semantics

A move constructor/assignment is `noexcept` when possible. Use
`std::move` to indicate the source is no longer needed.

BAD: `return std::move(local);` (prevents RVO).
GOOD: `return local;` (RVO applies).

### 4.9 No `using namespace std;` in Headers

In a header, `using namespace` pollutes every consumer's namespace.
Use explicit `std::` in headers. In `.cpp`, sparingly.

### 4.10 Structured Bindings

```cpp
for (const auto&amp; [key, value] : map) { ... }
```

## 5. Standard Library

### 5.1 Containers Over Raw Arrays

`std::vector` for dynamic, `std::array` for fixed, `std::string` for
text.

### 5.2 `std::string_view` for Non-Owning Strings

A function that reads a string takes `std::string_view` (C++17).
Beware of lifetime: a `string_view` does not own.

### 5.3 Algorithms Over Manual Loops

`std::sort`, `std::find_if`, `std::transform`, `std::accumulate`.
They are tested and often faster.

### 5.4 `std::optional` for Maybe-Values

BAD: `T* find(...)` returning `nullptr`.
GOOD: `std::optional&lt;T&gt; find(...)`.

### 5.5 `std::variant` for Sum Types

BAD: A struct with a tag and a union.
GOOD: `std::variant&lt;A, B, C&gt;` with `std::visit`.

### 5.6 `std::function` Has a Cost

`std::function` allocates for captures larger than a pointer. For
hot paths, use a template parameter.

### 5.7 No Raw `new` in Containers

`std::vector&lt;T*&gt;` with manual deletes is a leak waiting to happen.
Use `std::vector&lt;std::unique_ptr&lt;T&gt;&gt;`.

## 6. Concurrency

### 6.1 `std::thread` With RAII

A `std::thread` must be joined or detached before destruction.
Otherwise `std::terminate`.

Use `std::jthread` (C++20) for automatic join.

### 6.2 `std::mutex` With `std::lock_guard`

BAD:
```cpp
mutex.lock();
// ... may throw
mutex.unlock();
```

GOOD:
```cpp
std::lock_guard lock(mutex);
```

### 6.3 `std::atomic` for Simple Shared State

For counters and flags, `std::atomic` is faster than a mutex.

### 6.4 No Data Races

Any shared mutable state accessed by multiple threads without
synchronization is UB.

### 6.5 Memory Order

`std::memory_order_relaxed` is rarely correct. Use the default
(`seq_cst`) unless you have proven a weaker order is safe.

### 6.6 No Busy-Wait

A busy-wait loop burns CPU. Use condition variables or futures.

## 7. Build and Tooling

### 7.1 CMake Modern Style

- `target_link_libraries` with `PUBLIC`/`PRIVATE`/`INTERFACE`.
- `target_include_directories` per target, not global.
- No `include_directories` at the top.

### 7.2 Sanitizers

- `-fsanitize=address,undefined` in development.
- `-fsanitize=thread` for concurrency.
- Run tests under sanitizers.

### 7.3 No Warnings

`-Wall -Wextra -Werror`. Every warning is a bug.

### 7.4 Static Analysis

Clang-Tidy, cppcheck. Run in CI.

### 7.5 Formatter

`clang-format` with a project `.clang-format`.

## 8. C++-Specific Anti-Patterns

### 8.1 Raw `new`/`delete`

Covered in 2.1-2.4.

### 8.2 Manual Memory Management

Covered in 2.

### 8.3 Out-of-Bounds

Covered in 3.1.

### 8.4 Dangling References

Covered in 3.3.

### 8.5 `using namespace std;` in Headers

Covered in 4.9.

### 8.6 `NULL` Over `nullptr`

Covered in 4.6.

### 8.7 Missing `override`

A method that intends to override but is not marked `override` may
silently not override. Always mark.

### 8.8 Slicing

Passing a derived object by value to a base-typed parameter slices
it. Use references or pointers.

### 8.9 `std::endl` in Loops

`std::endl` flushes the stream. Use `'\n'` unless flushing is
required.

### 8.10 `#include` in Headers

Forward declarations where possible. Reduce compile times.

### 8.11 `#pragma once` vs Include Guards

`#pragma once` is widely supported. Use it, or an include guard. Do
not mix.

### 8.12 Macros for Constants

Covered in 4.4.

### 8.13 Magic Numbers

BAD: `if (x &gt; 86400)`.
GOOD: `constexpr int kSecondsPerDay = 86400;`.

### 8.14 C-Style Casts

BAD: `(int)x`.
GOOD: `static_cast&lt;int&gt;(x)`, `dynamic_cast`, `reinterpret_cast`,
`const_cast`.

### 8.15 `malloc`/`free` in C++

Covered in 2.5.

### 8.16 Copying Large Objects

BAD: `void process(std::vector&lt;int&gt; v)`.
GOOD: `void process(const std::vector&lt;int&gt;&amp; v)` or `std::span`.

### 8.17 Returning `const` by Value

BAD: `const std::string getName()`.
GOOD: `std::string getName()`.

`const` on return by value prevents moves.

### 8.18 `virtual` Without a Virtual Destructor

A base class with virtual methods needs a virtual destructor.
Otherwise deleting through a base pointer is UB.

### 8.19 `std::shared_ptr` Cycles

Two `shared_ptr`s pointing to each other leak. Use `weak_ptr`.

### 8.20 Exceptions Across `noexcept`

Throwing from a `noexcept` function calls `std::terminate`.

### 8.21 Ignoring `[[nodiscard]]`

A function marked `[[nodiscard]]` returns a value that matters.
Ignoring it is a bug.

### 8.22 `std::move` on Returned Locals

Covered in 4.8.

### 8.23 `const` Methods That Mutate

A `mutable` member allows mutation in a `const` method. Use it only
for caches and instrumentation.

### 8.24 Uninitialized Members

Every member is initialized in the constructor or via a default
member initializer.

### 8.25 `size_t` vs `int` Warnings

Mixing signed and unsigned produces warnings and bugs. Be consistent.

## 9. Response to Violation

If a previous response violated a rule here:

```
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

No justification. No apology paragraph. Fix and move on.
