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

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
security anti-patterns, output format) are NOT repeated here.

This file covers rules specific to Ruby: idiomatic style,
metaprogramming, blocks and procs, gems, and the patterns that
produce surprising behavior. Framework rules (Rails) live in
`domains/framework/`.

## 1. Stack Assumptions

This layer assumes:

- Ruby 3.2 or later.
- Bundler for dependencies.
- RuboCop for linting (or the project's chosen linter).

## 2. Idiomatic Ruby

### 2.1 Method Names

- `snake_case` for methods and variables.
- `PascalCase` for classes and modules.
- `SCREAMING_SNAKE_CASE` for constants.

### 2.2 Predicate Methods End With `?`

A method that returns a boolean ends with `?`: `empty?`, `valid?`,
`admin?`.

### 2.3 Bang Methods Signal Mutation

A method that mutates the receiver (or is more dangerous than its
non-bang version) ends with `!`: `save!`, `sort!`, `map!`.

### 2.4 Parentheses in Method Definitions

Modern Ruby style omits parentheses in method definitions when there
are no arguments:

BAD: `def run() { ... }` (acceptable but not idiomatic).
GOOD: `def run; ...; end`.

With arguments, use parentheses: `def run(task, priority)`.

### 2.5 No `and`/`or` for Control Flow

Use `&&` and `||`. `and` and `or` have lower precedence and produce
surprising behavior.

BAD: `result = do_thing and return` (may not do what you expect).
GOOD: `result = do_thing && return`.

### 2.6 No `unless...else`

BAD: `unless x; a; else; b; end`.
GOOD: `if x; b; else; a; end`.

`unless` is for single-branch conditions.

### 2.7 No Modifier `if` for Multi-Line Bodies

BAD: `do_something if condition` when `do_something` is complex.
GOOD: A full `if` block.

### 2.8 `then` Is Optional

Bad: `if x then a end`.
Good: `if x; a; end` or multi-line.

## 3. Blocks, Procs, and Lambdas

### 3.1 Blocks for Single Use

A block passed to a method (`items.each { |x| ... }`) is the idiomatic
form.

### 3.2 `Proc` vs `Lambda`

- `Proc`: lenient arity, `return` returns from the enclosing method.
- `Lambda`: strict arity, `return` returns from the lambda.

Prefer `lambda` (or `->`) unless you have a specific reason.

### 3.3 `&:method_name` for Simple Blocks

BAD: `items.map { |x| x.name }`.
GOOD: `items.map(&:name)`.

Use it only when the method takes no arguments.

### 3.4 No `return` in Blocks

A `return` inside a block passed to a method returns from the
enclosing method, not from the block. This surprises readers.

Use `next` to return from a block.

### 3.5 `yield` for Simple Yielding

A method that yields a single value uses `yield`. Use `block.call`
when storing the block.

## 4. Object Model

### 4.1 Composition Over Inheritance

Ruby allows multiple modules (`include`, `extend`). Prefer modules
over deep class hierarchies.

### 4.2 Modules for Namespacing

A module is a namespace and a mixin. Use `module Foo; class Bar; end; end`
to scope `Bar`.

### 4.3 `attr_reader` Over Manual Getters

BAD:
```ruby
def name
  @name
end
```

GOOD: `attr_reader :name`.

### 4.4 `attr_accessor` Only When Needed

`attr_accessor` creates both reader and writer. Use `attr_reader`
unless writing is required.

### 4.5 No `@@class_variables`

Class variables are shared across the hierarchy and produce
surprising behavior with inheritance. Use class instance variables
(`@var` at class level) or constants.

### 4.6 `self` Only When Required

`self.method` is required for setters and when a local variable
shadows the method. Otherwise, omit `self`.

## 5. Metaprogramming

### 5.1 Avoid `method_missing` Without `respond_to_missing?`

BAD:
```ruby
def method_missing(name, *args)
  # ...
end
```

If you define `method_missing`, also define `respond_to_missing?`.
Without it, `respond_to?` lies.

### 5.2 No `define_method` in Hot Paths

`define_method` is for DSLs and libraries. In application code, it
hides behavior and slows debugging.

### 5.3 `send` Only When Justified

`send` bypasses visibility. Use `public_send` for public methods.

BAD: `user.send(:admin?)` when `admin?` is public.
GOOD: `user.admin?`.

### 5.4 No `eval` Family

`eval`, `instance_eval` with user input, `class_eval` on strings:
never. They execute arbitrary code.

### 5.5 `const_get` With Care

`Object.const_get(user_input)` lets an attacker load any class.
Validate the input against an allowlist.

## 6. Error Handling

### 6.1 Never Rescue `Exception`

BAD: `rescue Exception => e`.
GOOD: `rescue StandardError => e`.

`Exception` includes `SignalException` and `NoMemoryError`. Catching
them prevents the process from responding to signals.

### 6.2 Never Rescue Without Handling

BAD: `begin; ...; rescue; end`.
GOOD: Handle the error, log it, or re-raise.

### 6.3 `raise` With a Class and Message

BAD: `raise "something failed"`.
GOOD: `raise ArgumentError, "name cannot be empty"`.

### 6.4 Custom Exception Classes

```ruby
class AppError < StandardError; end
class NotFoundError < AppError; end
```

Namespaced under the application.

### 6.5 `ensure` for Cleanup

`ensure` runs whether or not an exception was raised. Use it for
releasing resources.

### 6.6 `retry` With a Bound

BAD: `retry` in an infinite loop.
GOOD: `retry` with a counter and a limit.

## 7. Strings and Symbols

### 7.1 Symbols for Identifiers, Strings for Data

`user.role == :admin` (symbol). `user.name == "Alice"` (string).

### 7.2 Frozen String Literals

Add `# frozen_string_literal: true` at the top of every file. This
makes string literals immutable and reduces allocation.

### 7.3 `String#+` in Loops

BAD: `str += x` in a loop (allocates a new string per iteration).
GOOD: `StringIO` or an array joined at the end.

### 7.4 Heredocs for Multi-Line Strings

BAD: A multi-line string with `\n` concatenation.
GOOD: A heredoc (`<<~TEXT`).

## 8. Collections

### 8.1 Enumerable Methods

Use `map`, `select`, `reject`, `reduce`, `each_with_object`, `group_by`.

### 8.2 `each` for Side Effects, `map` for Transformation

BAD: `result = []; items.each { |x| result << transform(x) }`.
GOOD: `result = items.map { |x| transform(x) }`.

### 8.3 `detect` Over `find` (Alias)

Both work. Match the project's convention.

### 8.4 `Hash#fetch` for Required Keys

BAD: `config[:key]` (returns `nil` silently).
GOOD: `config.fetch(:key)` (raises `KeyError`).

### 8.5 `Hash#dig` for Nested Access

```ruby
value = config.dig(:database, :host) || "localhost"
```

### 8.6 No Hash With Indifferent Access Outside Rails

`HashWithIndifferentAccess` is a Rails extension. In plain Ruby, use
symbols or strings consistently.

## 9. Ruby-Specific Anti-Patterns

### 9.1 `rescue Exception`

Covered in 6.1.

### 9.2 Empty `rescue`

Covered in 6.2.

### 9.3 `eval` Family

Covered in 5.4.

### 9.4 `method_missing` Without `respond_to_missing?`

Covered in 5.1.

### 9.5 `send` for Public Methods

Covered in 5.3.

### 9.6 `@@class_variables`

Covered in 4.5.

### 9.7 `attr_accessor` for Everything

Covered in 4.4.

### 9.8 Monkey Patching Core Classes

BAD: Reopening `String` or `Array` to add a method.
GOOD: A refinement, a helper module, or a wrapper class.

Monkey patching breaks other gems that expect standard behavior.

### 9.9 Refinements Without Documentation

Refinements are lexically scoped and confusing. Use them sparingly
and document the scope.

### 9.10 Global Variables

BAD: `$current_user = ...`.
GOOD: A thread-local, an instance variable, or dependency injection.

### 9.11 `and`/`or` for Control Flow

Covered in 2.5.

### 9.12 `unless` With `else`

Covered in 2.6.

### 9.13 `defined?` for Nil Checks

BAD: `if defined?(@user) && @user`.
GOOD: `if @user`.

An uninitialized instance variable is `nil`; `defined?` adds noise.

### 9.14 `for` Loops

Ruby has `each`. `for` is rarely idiomatic.

BAD: `for item in items; ...; end`.
GOOD: `items.each { |item| ... }`.

### 9.15 `String#to_i` on User Input

BAD: `"abc".to_i` returns `0`, not an error.
GOOD: `Integer("abc")` raises `ArgumentError`.

### 9.16 `Object#try` Outside Rails

`try` is a Rails extension. In plain Ruby, use `&.`:

BAD: `user.try(:name)`.
GOOD: `user&.name`.

### 9.17 `blank?` and `present?` Outside Rails

Same as 9.16. Use explicit checks.

### 9.18 `Time.now` in Business Logic

`Time.now` depends on the system clock. Use `Time.current` (Rails)
or inject a clock.

### 9.19 Implicit `return` at the End of Long Methods

A method that ends with `if/else` implicitly returns the branch.
When the method is long, the reader cannot see the return value.
Use an explicit `return` or restructure.

### 9.20 Multiple Assignment

BAD: `a, b, c = method_that_returns_array` when the array length
is unknown.
GOOD: Destructure with explicit handling:
```ruby
a, b, *rest = method_that_returns_array
```

### 9.21 `Hash#each` With Two Variables

BAD: `hash.each { |k, v| ... }` where `hash` may be an array.
GOOD: `hash.each { |key, value| ... }` with a check that `hash` is a
`Hash`.

### 9.22 `class << self`

`class << self` is valid but unusual. Prefer `def self.method_name`.

### 9.23 `protected` and `private` Misunderstanding

`private` in Ruby is not like Java. A private method can be called
by subclasses via `send`. Understand the actual semantics.

### 9.24 `alias` Over `alias_method`

Both work. `alias_method` is safer inside modules. Match the
project's convention.

### 9.25 Overusing `define_method` in DSLs

A DSL with 20 `define_method` calls is hard to trace. Use them
sparingly.

## 10. Response to Violation

If a previous response violated a rule here:

```
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

No justification. No apology paragraph. Fix and move on.
