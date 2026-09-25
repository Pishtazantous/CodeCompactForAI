---
id: 02-make-language-file
title: "How to Generate a Language File"
lang: en
category: helper
version: 2
---

# How to Generate a Language File

Language files capture the traps specific to a programming language:
subtle behaviors, idioms with consequences, and anti-patterns that
arrive from other languages.

A language file is NOT a general style guide. It focuses on rules
that a general model applies inconsistently. If a rule is common to
every language, it belongs in Universal. If a rule is common to every
backend, it belongs in the backend delivery file. The language file
holds only what is specific to the language itself.

## When to Use This Guide

Use this guide when generating or regenerating a file under
`prompts/domains/language/`.

Use it when:

- A new language is added to the system.
- An existing language file is too shallow and needs a rewrite.
- The language gains a new version with breaking changes worth
  documenting.

Do NOT use it when:

- Generating a framework file (see `03-make-framework-file.md`).
- Generating a delivery file (see `01-make-delivery-file.md`).
- Generating a concern file (see `04-make-concern-file.md`).

## Files to Attach

### Required

- `_universal/00-master-anti-slop.md`

This file is mandatory. Without it, the AI cannot avoid duplicating
universal rules, and the generated file will overlap with the
universal layer.

### Required (1-2 examples from the same category)

Attach at least one, ideally two, existing language files that are
accepted as good. See the table below for language-specific
recommendations.

### Optional

- A delivery file if the language is used primarily in one delivery
  context (for example `02-backend-anti-slop.md` for a server-only
  language like Elixir).

## Reference Attachments by Language

The following table tells you which existing language files to
attach as references for each target language. Attach two whenever
possible.

| Target language | Primary reference | Secondary reference |
|---|---|---|
| Python | 02-python-anti-slop.md | 02-ruby-anti-slop.md |
| Ruby | 02-ruby-anti-slop.md | 02-python-anti-slop.md |
| JavaScript | 02-javascript-anti-slop.md | 02-typescript-anti-slop.md |
| TypeScript | 02-typescript-anti-slop.md | 02-javascript-anti-slop.md |
| Go | 02-go-anti-slop.md | 02-rust-anti-slop.md |
| Rust | 02-rust-anti-slop.md | 02-go-anti-slop.md |
| Java | 02-java-kotlin-anti-slop.md | 02-csharp-anti-slop.md |
| Kotlin | 02-java-kotlin-anti-slop.md | 02-swift-anti-slop.md |
| C# | 02-csharp-anti-slop.md | 02-java-kotlin-anti-slop.md |
| Swift | 02-swift-anti-slop.md | 02-kotlin (if present) or 02-csharp-anti-slop.md |
| C++ | 02-cpp-anti-slop.md | 02-rust-anti-slop.md |
| C | 02-cpp-anti-slop.md | 02-rust-anti-slop.md |
| PHP | 02-php-anti-slop.md | 02-python-anti-slop.md |
| Elixir | 02-elixir-anti-slop.md | 02-rust-anti-slop.md |
| Haskell | 02-elixir-anti-slop.md | 02-rust-anti-slop.md |
| Clojure | 02-elixir-anti-slop.md | 02-ruby-anti-slop.md |
| Scala | 02-java-kotlin-anti-slop.md | 02-rust-anti-slop.md |
| Zig | 02-cpp-anti-slop.md | 02-rust-anti-slop.md |
| Lua | 02-python-anti-slop.md | 02-javascript-anti-slop.md |
| Perl | 02-python-anti-slop.md | 02-php-anti-slop.md |
| R | 02-python-anti-slop.md | (any dynamic language) |
| Objective-C | 02-cpp-anti-slop.md | 02-swift-anti-slop.md |

If the target language is not listed, pick the two references whose
paradigm is closest. A dynamic language references other dynamic
languages. A systems language references other systems languages. A
managed language references other managed languages.

## Additional Prompt Requirements

When filling in the master prompt for a language file, insert the
following block under the `Mandatory Rules` section. This block
overrides the defaults for the language category.

```
### Language-Specific Requirements

Language files must satisfy the following in addition to the general
rules:

1. Version Applicability.

   The Stack Assumptions section MUST include a subsection titled
   "Version Applicability" that states:

   - The minimum supported version of the language.
   - Features used by the file that require a higher version.
   - How the file behaves if the project targets an older version.

   Example:
       Supported: Rust 2021 edition or later.
       Features used: `let-else` (1.65+), `OnceLock` (1.70+),
       `async fn` in traits (1.75+).
       If the project targets an older edition, some rules do not
       apply; the file is still readable but the features are not
       available.

   Do not write "version X or later" without listing the specific
   features that require it.

2. Traps from Other Languages.

   The file MUST include a section titled "Traps from Other
   Languages" with at least five rules. Each rule describes a habit
   that developers bring from another language and that is wrong or
   dangerous in this language.

   Example:
       From Java: using exceptions for control flow. Python uses
       exceptions for errors, not for ordinary branching. Prefer
       `dict.get` over `try/except KeyError`.

   The section is mandatory. It is where most language-specific
   slop originates.

3. Rationale for Every Rule.

   Every rule MUST include a one-line rationale, even when the rule
   seems obvious. The rationale helps the model generalize the rule
   to cases the file does not cover.

   BAD:
       ### 3.1 No `any`

       Do not use `any`.

   GOOD:
       ### 3.1 No `any`

       `any` disables type checking for the value and everything it
       touches. It is the single largest source of type-safety loss
       in TypeScript.

4. At Least 20 Anti-Patterns.

   The `Anti-Patterns` section MUST have at least 20 items, not 20
   rules total. Rules live in the earlier sections; the anti-pattern
   section is a list of concrete mistakes.

   Each anti-pattern has:
   - A short title.
   - A one-line explanation.
   - A BAD/GOOD code pair, unless the anti-pattern is purely
     structural (in which case a textual BAD/GOOD is acceptable).

5. At Least 15 Rules with BAD/GOOD.

   Not 50% of rules. At least 15 concrete code examples in the
   entire file. This number is a floor, not a target.

   If the file has fewer than 15 code examples, it is likely too
   abstract and needs concrete cases.
```

## Filling in the Master Prompt

Use this template for the metadata portion of the master prompt:

```
Path: prompts/domains/language/02-<lang>-anti-slop.md
id: 02-<lang>-anti-slop
title: <Language> Anti-Slop Layer
domain_type: language
depends_on: [00-master-anti-slop]

Coverage:
Rules specific to <language>: <list 4-6 topics from the
Suggested Topics section below>.

NOT covered:
Framework rules, delivery rules, generic programming rules.
<language>-specific frameworks (for example Django for Python,
Rails for Ruby) belong in their own framework files.
```

Then insert the `Additional Prompt Requirements` block above under
the `Mandatory Rules` section of the master prompt.

## Suggested Topics by Language Paradigm

Use these as a starting set of sections. Adjust for the specific
language.

### Dynamic Languages

Python, Ruby, PHP, JavaScript, Lua, Perl, R.

- Mutable defaults and shared state
- Exception handling patterns
- Type coercion and truthiness
- String and collection idioms
- Module and import discipline
- Comprehension / iteration style
- The GIL, threads, and async (Python and Ruby)
- Traps from statically typed languages

### Managed Static Languages

TypeScript, Java, Kotlin, C#, Scala, Swift, Go.

- Type system usage (generics, unions, nullability)
- Error handling (exceptions, Result, error values)
- Nullability discipline
- Concurrency primitives
- Collections and iteration
- Memory and reference semantics
- Traps from scripting languages

### Systems Languages

Rust, C++, C, Zig.

- Memory ownership and lifetimes
- Unsafe code discipline
- Error handling without exceptions
- Concurrency and atomicity
- Build and tooling (sanitizers, static analysis)
- Undefined behavior traps
- Traps from managed languages

### Functional Languages

Elixir, Haskell, Clojure, F#, Erlang, OCaml.

- Immutability discipline
- Pattern matching
- Process and supervision design
- Purity at the core, effects at the edge
- Recursion and tail calls
- Traps from imperative languages

### Logic and Query Languages

Prolog, Datalog, SQL.

- Declarative thinking
- Recursion and termination
- Ordering and side effects
- Traps from imperative thinking

## Suggested Topics by Specific Language

When the target language is on this list, use the suggested topics
as the starting set.

### Python

- Mutable default arguments
- Exception handling (`except Exception`, bare except, swallowing)
- Type hints and runtime validation
- `pathlib` over `os.path`, f-strings over `%`
- Async and the GIL
- Dataclasses and pydantic
- Anti-patterns from Java (verbose classes) and JavaScript
  (callback pyramids)

### JavaScript

- Equality (`===` over `==`)
- Coercion and truthiness
- Async/await and Promise handling
- `var` vs `let` vs `const`
- Module systems (ESM vs CommonJS)
- Array methods vs loops
- Anti-patterns from Java (class-heavy code) and Python
  (unnecessary abstraction)

### TypeScript

- Type system usage (unions, generics, narrowing)
- `any`, `unknown`, and `as`
- Utility types
- Enums and namespaces
- Module imports (type-only imports, barrel files)
- Anti-patterns from JavaScript (untyped code) and Java
  (over-abstracted type hierarchies)

### Go

- Error handling and wrapping
- Goroutines and context
- Channels and select
- Interfaces (small, consumer-defined)
- Slices, maps, and preallocation
- Anti-patterns from Java (heavy OOP) and Python (dynamic
  patterns that do not translate)

### Rust

- Ownership and borrowing
- Error handling (`Result`, `?`, `unwrap`, `expect`)
- Lifetimes and elision
- Unsafe code and safety comments
- Concurrency (Send, Sync, channels, async)
- Traits and trait objects
- Anti-patterns from C++ (manual memory) and Go (simple error
  wrapping without context)

### Java / Kotlin

- Nullability (`Optional`, platform types, `!!`)
- Immutability (records, data classes, final)
- Dependency injection (constructor, no field injection)
- Concurrency (executors, coroutines)
- Streams and collections
- Anti-patterns from C# (LINQ in Java), Python (dynamic patterns)

### C#

- Nullable reference types
- Async/await discipline (`ConfigureAwait`, no `.Result`)
- LINQ discipline (deferred execution, multiple enumeration)
- IDisposable and `using`
- Records and immutability
- Dependency injection
- Anti-patterns from Java (verbose getters) and JavaScript
  (dynamic patterns)

### C++

- RAII and smart pointers
- Undefined behavior traps
- Move semantics and the Rule of Zero/Five
- Modern idioms (`auto`, `constexpr`, `std::optional`)
- Concurrency and atomics
- Build and sanitizers
- Anti-patterns from C (manual memory) and Java (heavy inheritance)

### PHP

- `declare(strict_types=1)`
- Type declarations
- PSR compliance
- Superglobals and sessions
- Prepared statements and escaping
- Composer discipline
- Anti-patterns from PHP 5 (global state, `mysql_*`) and
  JavaScript (async patterns in a synchronous language)

### Ruby

- Idiomatic style (predicate methods, bang methods)
- Blocks, procs, and lambdas
- Modules and mixins over inheritance
- Metaprogramming discipline
- Exception handling (`rescue StandardError`)
- Anti-patterns from Java (verbose classes) and Perl (heavy
  metaprogramming)

### Elixir

- Functional core, effectful edge
- Processes and OTP supervision
- Pattern matching and guards
- Tagged tuples for errors
- Atoms, strings, and binaries
- Anti-patterns from Ruby (mutable patterns) and Erlang (raw
  process primitives without OTP)

### Swift

- Optionals and `guard let`
- Value vs reference semantics
- Memory management (weak, unowned, `[weak self]`)
- Swift Concurrency (async/await, actors)
- Protocol-oriented design
- Anti-patterns from Objective-C (force unwrap, KVO) and Java
  (heavy class hierarchies)

### C

- Manual memory and buffer safety
- Pointer arithmetic discipline
- Undefined behavior
- Concurrency without atomics
- Build and sanitizers
- Anti-patterns from C++ (using C++ idioms in C code) and
  scripting languages (assuming runtime safety)

## Verification

After receiving the file from the AI, verify:

1. Every item in the master prompt's self-audit checklist.
2. Every item in the `Language-Specific Self-Audit` below.
3. The file is between 250 and 400 lines (language files are
   slightly longer than other domain files because of the anti-
   pattern count).
4. The file does not repeat rules from the attached sibling files.

If any item fails, request a revision from the AI rather than saving
a weak file.

## Language-Specific Self-Audit

Before saving the generated file, verify every item:

Version Applicability:
- [ ] A subsection titled "Version Applicability" exists under
      Stack Assumptions
- [ ] The minimum supported version is stated
- [ ] Features requiring a higher version are listed
- [ ] The behavior under an older version is described

Traps from Other Languages:
- [ ] A section titled "Traps from Other Languages" exists
- [ ] At least five rules are present
- [ ] Each rule names the source language
- [ ] Each rule describes the wrong habit and the correct one

Rationale Discipline:
- [ ] Every rule has a one-line rationale
- [ ] The rationale explains why, not just what

Anti-Patterns:
- [ ] The Anti-Patterns section has at least 20 items
- [ ] Each item has a short title
- [ ] At least 10 items have a BAD/GOOD code pair

Code Examples:
- [ ] At least 15 rules in the file have BAD/GOOD code pairs
- [ ] Code blocks use a language tag (`python`, `go`, `rust`, etc.)
- [ ] Names are realistic (user, order, fetchUser), not `foo` or
      `bar`
- [ ] Examples are 5-15 lines

Structural:
- [ ] Frontmatter is complete
- [ ] Opening paragraph is 3-5 lines
- [ ] At least 12 sections total
- [ ] Response to Violation section matches the fixed template
- [ ] Entire file is in English
- [ ] No emoji

Non-Duplication:
- [ ] No rule from Universal is repeated
- [ ] No rule from the attached sibling files is repeated
- [ ] References to other files have one-line summaries

If any item fails, ask the AI to revise the specific section. Do not
save a file that fails the self-audit.

## Common Failures

The following failures occur frequently when generating language
files. Use this table during review.

| Failure | How to spot it | Fix |
|---|---|---|
| General style guide | Rules apply to any language | Move to Universal or delete |
| Missing rationale | Rules say "do not" without "because" | Request rationale |
| No version applicability | Stack Assumptions says "version X or later" only | Request the feature list |
| No traps section | Missing "Traps from Other Languages" | Request the section |
| Too few anti-patterns | Under 20 items | Request more |
| Shallow code examples | Under 15 BAD/GOOD pairs | Request concrete cases |
| Repeats Universal | Includes "no TODO", "declare assumptions" | Delete; they are in Universal |
| Framework bleed | Includes React hooks, Django models | Move to the framework file |
| Delivery bleed | Includes API contracts, DB rules | Move to the delivery file |
| Over-length | Over 400 lines | Split or trim |

## After the File Is Accepted

1. Save to `prompts/domains/language/02-<lang>-anti-slop.md`.
2. Update `prompts/README.md` to include the new file in the
   language list.
3. If the language has a dominant framework, generate the framework
   file next, using this file as a reference.
4. If the language has a dominant delivery (for example a
   server-only language), confirm the delivery file exists and is
   attached for future projects.

## Time Budget

Generating a language file with a frontier model takes 3-6 minutes
(language files are longer than other domain files). Review takes
10-15 minutes with the self-audit checklist. If review takes longer
than 20 minutes, the master prompt likely needs refinement for
future language files.

## Reference Example

The example in `prompts/_send-packages/example-svelte/` shows the
workflow for a framework file. The same workflow applies to language
files, with the additional `Language-Specific Requirements` block
inserted into the master prompt.
