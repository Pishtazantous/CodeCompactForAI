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

Layered under `_universal/00-master-anti-slop.md`. This layer covers C++
ownership, undefined behavior, resource lifetime, and modern C++ design.
Build, framework, and platform rules remain elsewhere.

## 1. Scope and Assumptions
1. Read `CMakeLists.txt`, compiler settings, warnings, standard version, and
   dependency files before selecting a language feature or library.
2. Match the project's supported standard, ABI, allocator, and exception
   model. Do not assume C++20 or a compiler extension is available.
3. Preserve public headers, ownership conventions, and compilation settings.

## 2. Ownership and RAII
4. Represent every resource owner with a class that acquires in its constructor
   and releases in its destructor. Prefer `std::unique_ptr` for exclusive
   dynamic ownership.
5. Use `std::shared_ptr` only when shared lifetime is required; prefer weak
   observation and make cycles impossible by design.
6. Do not write a raw `new` and `delete` pair in application code. Use a
   container or smart pointer unless a custom lifetime contract is essential.
7. Prefer values and `std::span` for non-owning views. Make the referenced
   lifetime clear in the parameter type and documentation.

## 3. Undefined Behavior
8. Do not dereference null, dangling, uninitialized, or out-of-range pointers.
   Check preconditions or use a safe abstraction.
9. Do not overflow signed arithmetic, shift by an invalid amount, or cast a
   large value into a smaller type without checking the range.
10. Do not modify an object while another thread reads or writes it without a
    defined synchronization mechanism.
11. Do not form a reference to a temporary, bind a reference beyond the
    referenced object's lifetime, or return a view to a local container.
12. Do not rely on unspecified evaluation order, unsequenced accesses, or
    implementation-defined layout for portable behavior.

## 4. Move Semantics
13. Use `std::move` only when the value is immediately transferred; it is a
    cast, not a copy elision command.
14. Use `std::forward` when preserving a template parameter's value category.
    Do not use `std::forward` on a local that will be used again.
15. A move constructor or assignment may leave the source valid but unspecified.
    Do not read a moved-from object unless its type documents a stronger rule.
16. Mark or delete copy operations when a type cannot support them. Do not let
    accidental shallow copies duplicate an owning pointer.
17. Prefer `std::move` over copying large values, but measure performance before
    introducing complexity solely for micro-optimization.

## 5. Exceptions and Error Handling
18. Use exceptions for exceptional failures only when the project does. For
    expected errors, prefer a status, expected type, or error code that the
    caller must handle.
19. Use RAII so cleanup occurs during stack unwinding. Never skip a resource
    destructor by managing ownership with a raw pointer.
20. Do not catch an unknown exception handler to continue. Catch the specific
    exception that recovery handles and preserve a useful cause.
21. Do not throw from a destructor or a `noexcept` function. Translate failures
    at the API boundary.

## 6. Modern Idiom
22. Prefer `auto` for long iterator and expression types, but use explicit types
    at public boundaries and where inference hides a conversion.
23. Prefer range-based `for`, `std::span`, `std::string_view`, and standard
    containers over hand-written index loops when ownership permits.
24. Use `const` to express non-mutation. Do not return a mutable reference to
    private state merely to avoid a getter.
25. Prefer `enum class`, scoped enums, and strong types when values from
    different domains can otherwise be confused.
26. Use structured bindings when they improve readability; do not use them to
    obscure a deep nested expression.

## 7. Templates and Concurrency
27. Constrain templates at the point of use and keep the requirement visible in
    the declaration. Do not rely on an accidental implementation type.
28. Instantiate templates in a translation unit when this reduces build cost
    or controls symbol visibility, following project convention.
29. Do not start a thread without a defined join, detach policy, and exception
    strategy. Capture required values explicitly and avoid shared mutable state.
30. Protect invariants, not individual assignments. Choose atomics only when
    they express the actual synchronization requirement.

## 8. Headers, Build, and Dependencies
31. Include what you use and keep public headers self-contained. Avoid including
    heavy implementation headers in a public interface.
32. Do not add a package or enable a language standard without permission. Keep
    build warnings treated according to project policy.
33. Do not use a macro to hide a type or ownership rule. If a macro is required
    by the platform, isolate it and document the invariant.
34. Preserve ABI and source compatibility unless the task authorizes a break.

## 9. Verification Checklist
35. Build with the configured compiler, warnings, and standard. Run sanitizers
    or static analysis when the project has commands for them.
36. Search for raw `new`, `delete`, casts, `goto`, C arrays, unchecked indexes,
    detached threads, and manual lock/unlock.
37. Test copy, move, destruction, allocation failure where practical, and
    ownership under early return or exception.
38. Report commands and results precisely; never claim an unrun sanitizer
    passed.

## 10. Additional Review Gates
39. Review every pointer and reference for a written owner and a clear order of
    destruction when a container or object graph is involved.
40. Check integer conversions and container index operations at trust
    boundaries, not only in the happy path.
41. Verify that a move does not leave a lock, file, or network resource owned
    by the moved-from object.
42. Inspect thread shutdown for joins, condition-variable wakeups, and exception
    paths; detached work is not a cleanup strategy.
43. Confirm that headers expose only declarations and that implementation
    details do not become accidental ABI dependencies.
44. Run compiler warnings, sanitizers, and tests with the project's configured
    flags and report the actual output.

## Domain-Specific Anti-Patterns

### 10.1.1 Manual Ownership
BAD:
```cpp
Widget* make() { return new Widget(); }
int size(Widget* p) { return p->rows; }
```
GOOD:
```cpp
std::unique_ptr<Widget> make();
std::size_t size(const std::span<const std::byte> data);
```

### 10.1.2 Dangling Views
BAD:
```cpp
std::string_view label() { std::string value = make(); return value; }
```
GOOD:
```cpp
std::string make_label() { return make(); }
```

### 10.1.3 Raw Ownership Transfer
BAD:
```cpp
Buffer* copy() { return new Buffer(data_, size_); }
```
GOOD:
```cpp
std::unique_ptr<Buffer> copy() const {
    return std::make_unique<Buffer>(data_, size_);
}
```

## 11. Response to Violation
Name the file, symbol, and numbered rule, then explain the lifetime,
undefined-behavior, or maintenance failure. Apply the smallest RAII or type
correction and preserve the public contract. Refer to the master layer instead
of repeating it. If the fix changes ownership, ABI, exceptions, or the
compiler standard, state that impact before editing.
