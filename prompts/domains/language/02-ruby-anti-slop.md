---
id: 02-ruby-anti-slop
title: "Ruby Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: language
version: 1
---
# Ruby Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. This layer covers Ruby
object design, metaprogramming, data access, and blocks. Rails or other
framework rules live in the relevant framework files.

## 1. Scope and Assumptions
1. Read the Gemfile, Ruby version, framework boot files, and existing test
   commands before selecting syntax or adding a gem.
2. Match the project's supported Ruby release and frozen-string, warnings, and
   concurrency settings.
3. Prefer the smallest public API that satisfies the current caller.

## 2. N+1 and Data Access
4. Do not call a database-backed association or method inside a loop when the
   same relation can be loaded once. Verify the generated queries.
5. Use eager loading only for relationships needed in the current operation;
   avoid loading every association indiscriminately.
6. Keep query construction in repository or query-object code. Do not build
   ad hoc fragments from request strings.
7. Treat a callback that performs another query as a possible N+1 source and
   document its execution count.

## 3. Metaprogramming
8. Use metaprogramming to remove a demonstrated repetition, not to make an
   API look dynamic. Keep generated methods small and discoverable.
9. Define methods on an explicit receiver or a narrowly scoped module. Do not
   monkey-patch core classes from an initializer.
10. Give every `define_method`, `method_missing`, and generated attribute a
    concrete reason, tests, and an error behavior for invalid input.
11. Prefer explicit declarations when a stack trace, type checker, or reader
    needs to understand the method.

## 4. Blocks, Procs, and Control Flow
12. Use a block for an operation whose behavior belongs to the call site. Use
    a proc only when the block must be stored, passed, or composed.
13. Distinguish lambda return and argument behavior from proc behavior. Do not
    use a proc accidentally where strict arity or return semantics are needed.
14. Avoid `return` from a stored block unless the block is known to be invoked
    within the defining method and that behavior is intentional.
15. Prefer `each` for side effects and `map`, `select`, or `reduce` when a
    transformed or aggregate result is required.

## 5. Mutability and Ownership
16. Treat `Hash`, `Array`, and `String` as mutable values unless frozen. Freeze
    constants and public value objects when accidental mutation would corrupt
    state.
17. Do not mutate arguments unless the method name and contract say so. Return
    a new value for transformations.
18. Use `dup` deliberately; understand whether a shallow copy shares nested
    mutable objects.
19. Keep singleton state explicit and thread-safe. Do not store request data in
    class variables or global mutable hashes.

## 6. Exceptions and Boundaries
20. Rescue the narrowest standard or domain exception possible. Never rescue
    `Exception` to continue a request after an unknown failure.
21. Do not rescue and return nil unless absence is a documented result. Log
    or re-raise errors that require operator attention.
22. Validate input before calling framework or filesystem APIs. Do not trust
    `params`, cookies, or deserialized objects merely because the framework
    populated them.

## 7. Objects and Modules
23. Prefer small objects with explicit methods over a god object containing
    unrelated state. A module should have a coherent responsibility.
24. Use a `Struct` or `Data` type for small immutable values only when the
    project supports it and equality is appropriate.
25. Keep visibility explicit. Do not expose an internal writer or mutable
    collection just because a test currently needs access.
26. Use `private` for implementation helpers; do not use `send` to bypass it in
    production code.

## 8. Tooling and API Hygiene
27. Follow the project's formatter, linter, and test framework. Do not add a
    gem or initializer without permission.
28. Prefer a small public method over a `method_missing` fallback. If dynamic
    dispatch is required, raise a clear `NoMethodError` for unknown names.
29. Use keyword arguments for options when the project does so; avoid a long
    positional argument list whose meaning changes silently.
30. Keep comments and identifiers in the project's established language.

35. Check relation-loading changes against query logs and fixture boundaries.
36. Review every core-class modification for load-order and test-isolation risk.
37. Prefer explicit keyword options when a public method gains another flag.
39. Test nil, empty, and missing-record behavior at public boundaries.
40. Review singleton and class-variable state for request isolation.
41. Keep dynamic dispatch behind an explicit protocol boundary.
42. Check keyword arguments and mutation behavior in tests.
43. Run the configured Ruby version with the full verification set.
44. Record query counts when eager loading changes.

44. Check query logs after relation-loading changes.
45. Review dynamic dispatch outside explicit library boundaries.
46. Inspect long-lived closures for retained request data.
47. Test nil, empty, and missing-record behavior.
48. Review singleton state for request isolation.
49. Check mutation behavior across method boundaries.
50. Run the configured formatter, linter, and tests.
51. Record query counts when they affect correctness or cost.
52. Report the exact verification commands and results.

## Domain-Specific Anti-Patterns

### 9.1 Hidden Queries
BAD:
```ruby
orders.each { |order| puts order.customer.name }
```
GOOD:
```ruby
orders.includes(:customer).each { |order| puts order.customer.name }
```

### 9.2 Core Monkey Patches
BAD:
```ruby
class String
  def to_slug = downcase.gsub(" ", "-")
end
```
GOOD:
```ruby
module Sluggable
  def slug = downcase.gsub(" ", "-")
end
```

### 9.3 Hidden Proc Returns
BAD:
```ruby
callback = Proc.new { return :stopped }
callback.call
puts "unreachable"
```
GOOD:
```ruby
callback = lambda { :stopped }
callback.call
puts "continued"
```

## 10. Verification Checklist
31. Run focused tests and the project's lint and type checks when present.
32. Search for `N+1` query paths, `rescue Exception`, monkey patches,
    `method_missing`, `Proc.new`, and ignored return values.
33. Test empty collections, missing records, repeated invocation, and concurrent
    access where relevant.
34. Report commands and outcomes exactly; do not claim unrun tests passed.

## 11. Response to Violation
Identify the file and method, quote the numbered rule, and explain the runtime,
security, or maintainability failure. Apply the smallest correction and keep
the public contract stable. Do not repeat universal guidance. If removing a
monkey patch or changing eager loading changes behavior or performance,
describe the impact before editing and seek approval when required.
