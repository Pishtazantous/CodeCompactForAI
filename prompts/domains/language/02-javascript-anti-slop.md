---
id: 02-javascript-anti-slop
title: "JavaScript Anti-Slop Layer"
lang: en
depends_on: ["_universal/00-style-guide.md", "_universal/00-master-anti-slop.md"]
category: domain
domain_type: language
version: 2
---

# JavaScript Anti-Slop Layer

This file defines behavioral contracts specific to the JavaScript language. It sits in the language layer, below the universal rules and above framework-specific rules. It covers language semantics, equality, coercions, scope, async, modules, and the common dynamic patterns that produce silent bugs. It does not cover framework rules (React, Vue, Node runtime — see `domains/framework/`), TypeScript rules (see `02-typescript-anti-slop.md`, which takes precedence when both apply), or delivery-specific rules (see `domains/delivery/`).

JavaScript's value is its ubiquity and flexibility; its danger is its implicit coercions, dynamic typing, and historical quirks. Every rule below either prevents a class of silent bug or documents a modern idiom that replaces a legacy trap.

## Scope

This file applies to JavaScript code running in any modern runtime (Node.js, browsers, Deno, Bun, workers) targeting ES2020 or later, as configured by the project's `package.json`, `tsconfig.json`, or bundler.

### Version Applicability

- **Minimum version**: ES2020.
- **Features assumed available**: `async/await`, optional chaining (`?.`), nullish coalescing (`??`), `Promise.allSettled`, `globalThis`, `import.meta`, dynamic `import()`, `structuredClone` (ES2022+).
- **Module system**: ES Modules (`import`/`export`) by default. CommonJS rules apply only when the project explicitly uses it.
- **If the project targets an older version**: features above their introduction year are unavailable; the remaining rules still apply.

For TypeScript projects, `02-typescript-anti-slop.md` takes precedence on any rule that overlaps (e.g., `any`, type assertions). This file governs runtime JavaScript behavior and idioms that persist even when TypeScript is layered on top.

## Rule Severity

Severity follows `_universal/00-style-guide.md`.

## Contracts

A JavaScript codebase commits to six contracts. The table below maps each contract to the rules that enforce it.

| Contract | Description | Enforced By |
|---|---|---|
| Modern Idioms | Strict mode, `const`/`let`, arrow functions, and modern syntax are the default. | JS-001 to JS-004 |
| Equality and Coercion Discipline | `===` is universal; coercions are explicit; truthiness is not relied upon. | JS-005 to JS-013 |
| Scope and Binding Safety | Block scoping, no implicit globals, and TDZ are respected. | JS-014 to JS-017 |
| Immutable Data Flow | Functions do not mutate arguments or shared state without explicit naming. | JS-018 to JS-026 |
| Async Correctness | Promises are awaited, errors are handled, and timeouts are bounded. | JS-032 to JS-043 |
| Module and Runtime Discipline | ESM is preferred, side effects are isolated, and runtime-specific APIs are used correctly. | JS-044 to JS-056 |

## Strict Mode and Modern Syntax

### JS-001 — Strict Mode Enforcement

**MUST**

ES modules are always strict. CommonJS files MUST have `"use strict"` at the top, or the project's pattern MUST enforce it. Sloppy mode behavior MUST NOT be relied upon. Strict mode catches implicit globals, invalid assignments, and other silent bugs.

### JS-002 — `var` Prohibition

**MUST NOT**

`var` MUST NOT be used. It is function-scoped, hoisted in confusing ways, and has no place in modern code. `let` MUST be used for reassignable bindings; `const` MUST be used for non-reassignable bindings.

Example (illustrative, JavaScript):

BAD:
```javascript
var count = 0;
for (var i = 0; i < 10; i++) { /* ... */ }
```

GOOD:
```javascript
let count = 0;
for (let i = 0; i < 10; i++) { /* ... */ }
```

### JS-003 — `const` by Default

**MUST**

A binding that is never reassigned MUST be declared `const`. The presence of `let` is a signal that reassignment happens in that scope. `const` prevents rebinding, not mutation; this distinction MUST NOT be confused.

### JS-004 — Arrow Function Discipline

**SHOULD**

Arrow functions SHOULD be used when the lexical `this` is intended. Function declarations SHOULD be used for named top-level functions, especially when hoisting is desired or when the function is used as a constructor. Arrow functions MUST NOT be used for methods on objects that need a dynamic `this`.

## Equality

### JS-005 — Strict Equality Only

**MUST**

`===` and `!==` MUST be used everywhere. `==` and `!=` perform type coercion with widely misunderstood rules and MUST NOT be used. The only accepted exception is `value == null`, which matches both `null` and `undefined`; even this MUST match the project's convention.

Example (illustrative, JavaScript):

BAD:
```javascript
if (x == 0) { /* true for "", [], "0" */ }
```

GOOD:
```javascript
if (x === 0) { /* true only for the number 0 */ }
```

### JS-006 — `Object.is` for Edge Cases

**SHOULD**

For `NaN` and `-0` distinctions, `Object.is` SHOULD be used. It is the only reliable way to compare these values.

### JS-007 — Object Comparison Discipline

**MUST NOT**

Two object literals with the same content are not `===` equal. `===` MUST NOT be used to compare objects structurally. A deep-equal utility from the project or explicit field comparison MUST be used.

## Coercion and Truthiness

### JS-008 — Explicit Coercion

**MUST NOT**

Implicit coercion in a branch or comparison MUST NOT be relied upon. Coercion MUST be made explicit.

Example (illustrative, JavaScript):

BAD:
```javascript
if (userInput) { /* true for "0", false for "" */ }
```

GOOD:
```javascript
if (userInput.length > 0) { /* explicit */ }
```

### JS-009 — Boolean Conversion Consistency

**MUST**

When explicit boolean conversion is needed, either `Boolean(x)` or `!!x` MUST be picked and applied consistently. `!!x` is shorter and conventional; `Boolean(x)` is clearer.

### JS-010 — Numeric Conversion Intent

**MUST**

`Number(x)` and `parseInt(x, 10)` do different things (`Number("") === 0`; `parseInt("") === NaN`). The conversion MUST match the intent. The radix MUST always be passed to `parseInt`; without it, leading-zero strings may be parsed as octal in older engines and linters flag it.

### JS-011 — `+` Overload Discipline

**MUST**

`+` concatenates strings and adds numbers; when operands differ in type, the result is a string. Operands MUST be explicitly converted before addition when types may differ.

Example (illustrative, JavaScript):

BAD: `const total = "5" + 3; // "53"`
GOOD: `const total = Number("5") + 3; // 8`

### JS-012 — Template Literals for Interpolation

**MUST**

Template literals MUST be used for string interpolation. String concatenation with `+` for interpolation is prohibited.

### JS-013 — `null` vs `undefined` Consistency

**MUST**

One value MUST be picked for "no value" and used consistently. In most modern projects, `undefined` represents "missing" and `null` represents "explicitly empty" (especially from JSON payloads). They MUST NOT be mixed within a single API or type.

## Scope and Hoisting

### JS-014 — Block Scope Discipline

**MUST**

`let` and `const` are block-scoped. A variable MUST NOT be declared outside the block where it is used.

### JS-015 — Intentional Hoisting

**MUST**

Function declarations hoist; function expressions and arrow functions do not. Hoisting MUST be relied on intentionally, never accidentally.

### JS-016 — Temporal Dead Zone Respect

**MUST NOT**

Accessing a `let` or `const` before its declaration throws — this is a feature that catches bugs. Declarations MUST NOT be moved to the top of a file "just in case" to work around it.

### JS-017 — No Implicit Globals

**MUST NOT**

Assigning to an undeclared variable creates a global in sloppy mode. This MUST NOT occur. Strict mode throws on this, which is the desired behavior.

Example (illustrative, JavaScript):

BAD:
```javascript
function setup() {
  config = {}; // creates global `config`
}
```

GOOD:
```javascript
function setup() {
  const config = {};
  return config;
}
```

## Objects and Arrays

### JS-018 — Destructuring Over Property Access

**SHOULD**

When reading multiple properties from the same object, destructuring SHOULD be preferred over individual property access.

### JS-019 — Default Values in Destructuring

**SHOULD**

Defaults SHOULD be used for optional fields in destructuring (e.g., `const { limit = 20 } = options;`). The same default MUST NOT then be reapplied inside the body with `||`.

### JS-020 — Rest and Spread Without Mutation

**MUST NOT**

`rest` (`...rest`) MUST be used for grouping remaining properties; `spread` (`...obj`) MUST be used for merging. Inputs MUST NOT be mutated via `Object.assign(target, source)`; a new object MUST be returned.

### JS-021 — `Object.freeze` for Constants

**SHOULD**

Module-level lookup tables that must not be mutated SHOULD use `Object.freeze`. Freezing is shallow; nested objects remain mutable unless frozen recursively.

### JS-022 — Array Methods Over Loops

**SHOULD**

`map`, `filter`, `reduce`, `find`, `some`, `every`, and `flatMap` SHOULD be preferred over manual `for` loops for transformations. `for...of` SHOULD be used when the loop has side effects or early exit. `.forEach` MUST NOT be used for transformations; it discards the return value and forces mutation.

### JS-023 — No Argument Mutation

**MUST NOT**

A function MUST NOT mutate its arguments. Mutation surprises callers and breaks memoization. A new value MUST be returned. Exception: the function's name explicitly says it mutates (e.g., `sortInPlace`, `pushItem`), or the project's established pattern is mutation-based.

### JS-024 — `Array.prototype.sort` Copy Discipline

**MUST**

`sort` sorts in place and returns the same array. If the input MUST NOT change, it MUST be copied first: `[...items].sort(...)`.

### JS-025 — `includes` Over `indexOf`

**SHOULD**

`includes` SHOULD be used for existence checks. `indexOf` SHOULD be used only when the index itself is needed.

### JS-026 — `Set` for Uniqueness

**SHOULD**

For removing duplicates or fast lookups, `Set` SHOULD be used instead of array scans.

## Functions

### JS-027 — Default Parameters Over `||`

**MUST**

Default parameters MUST be used instead of `||` inside the function body. `||` treats `0`, `""`, and `false` as missing; default parameters do not.

### JS-028 — Named Parameters via Destructuring

**SHOULD**

For functions with more than three parameters, an options object with destructuring SHOULD be used instead of a positional argument list.

### JS-029 — Early Return Discipline

**SHOULD**

Conditionals SHOULD NOT be nested. Early returns for failure cases SHOULD be used to flatten the control flow.

### JS-030 — Side Effect Naming

**MUST**

A function named `getUser` MUST NOT send an email. Read functions MUST be kept pure. Side effects MUST be named explicitly (e.g., `saveUser`, `sendWelcomeEmail`).

### JS-031 — No `arguments` Object

**MUST NOT**

The `arguments` object MUST NOT be used. Rest parameters (`...args`) MUST be used instead. `arguments` is not an array, does not work with arrow functions, and defeats rest-parameter tooling.

## Async and Promises

### JS-032 — `async`/`await` Over `.then` Chains

**SHOULD**

`async`/`await` SHOULD be used for readable control flow. `.then` SHOULD be used only for short chains or when mixing with non-async APIs.

### JS-033 — No `await` in `forEach`

**MUST NOT**

`forEach` does not await its callback — the loop returns immediately. `await` MUST NOT be used inside `forEach`. A `for...of` loop MUST be used for sequential async work, or `Promise.all` for parallel work.

Example (illustrative, JavaScript):

BAD:
```javascript
items.forEach(async (item) => {
  await process(item); // not awaited
});
```

GOOD:
```javascript
for (const item of items) {
  await process(item);
}
```

### JS-034 — `Promise.all` vs `Promise.allSettled`

**MUST**

`Promise.all` rejects on the first rejection and MUST be used only when all results are required. `Promise.allSettled` returns all outcomes and MUST be used when partial success is acceptable. `Promise.all` MUST NOT be used for fire-and-forget operations; unhandled rejections cause process crashes or silent failures.

### JS-035 — No Mixed Callbacks and Promises

**MUST NOT**

A function MUST either return a Promise or take a callback, not both. A callback API MUST NOT be wrapped in a Promise while also calling the callback.

### JS-036 — Timeouts on External Calls

**MUST**

Every network, database, or external call MUST have a timeout. A promise that never resolves hangs the request forever. `AbortController` MUST be used for `fetch` and equivalent APIs.

### JS-037 — Unhandled Rejection Prohibition

**MUST NOT**

A promise MUST NOT reject without a handler. Every promise chain MUST have a `.catch`, be inside a `try/catch`, or be returned from an async function whose caller handles it.

### JS-038 — Floating Promise Prohibition

**MUST NOT**

A promise that is created and not awaited, caught, returned, or intentionally ignored with a comment MUST NOT exist. Linters flag floating promises because they hide unhandled rejections.

## Error Handling

### JS-039 — Throw `Error` or Subclasses

**MUST**

Only `Error` or its subclasses MUST be thrown. String throws lose the stack trace and the `.message` property conventions.

Example (illustrative, JavaScript):

BAD: `throw "something went wrong";`
GOOD: `throw new Error("something went wrong");`

### JS-040 — No Silent Error Swallowing

**MUST NOT**

Errors MUST NOT be swallowed silently in a `catch` block. They MUST be logged, rethrown, or explicitly ignored with a comment explaining why.

### JS-041 — No Empty `catch`/`throw`

**MUST NOT**

A `try { ... } catch (e) { throw e; }` block adds nothing and MUST NOT exist. The `try`/`catch` MUST be removed.

### JS-042 — Re-throw With Context

**MUST**

When wrapping an error, the `cause` option MUST be used (e.g., `new Error("msg", { cause: error })`). Original error messages MUST NOT be concatenated and the original error object MUST NOT be discarded.

### JS-043 — No Logic on `error.message`

**MUST NOT**

`error.message` is for humans. Logic MUST NOT branch on message contents. Matching MUST be done on error types or codes (e.g., `error instanceof NotFoundError`).

## Modules

### JS-044 — ESM Over CommonJS

**MUST**

ESM (`import`/`export`) MUST be used. CommonJS (`require`) MUST only be used when the project is explicitly CommonJS and cannot migrate.

### JS-045 — Named Exports Preference

**SHOULD**

Named exports SHOULD be preferred over default exports. Named exports make refactoring tools work, avoid naming mismatches at import sites, and produce clearer stack traces. Default exports are acceptable when the module is truly a single concept and the project uses them consistently.

### JS-046 — Barrel File Prohibition

**MUST NOT**

Barrel files (`index.js` re-exporting everything from a folder) MUST NOT be used. They break tree-shaking, create circular import risk, and make stack traces harder to read. Imports MUST come directly from the specific file.

See ARCH-056 in `domains/framework/02-architecture-anti-slop.md`.

### JS-047 — No Top-Level Side Effects

**MUST NOT**

A module's top-level code runs on import. I/O, network calls, or global mutations MUST NOT be placed there. Work MUST be done in named functions. Exception: explicitly documented initialization modules with a single `init()` called by the application entry point.

### JS-048 — Dynamic Import for Lazy Loading

**SHOULD**

`await import("...")` SHOULD be used for code that is not needed at startup. Static imports always load eagerly.

## DOM and Browser

### JS-049 — `querySelector` Over Legacy Selectors

**SHOULD**

`querySelector` / `querySelectorAll` SHOULD be preferred over `getElementById` and other legacy selectors for uniform API surface.

### JS-050 — No `innerHTML` With Untrusted Data

**MUST NOT**

`innerHTML` MUST NOT be assigned untrusted data. `textContent` MUST be used, or the input MUST be sanitized with the project's sanitizer library.

See SEC-024 in `domains/concern/02-security-critical-anti-slop.md`.

### JS-051 — Event Delegation

**SHOULD**

For dynamic children, event listeners SHOULD be attached to a parent element (delegation) rather than one listener per child.

### JS-052 — Listener Removal Discipline

**MUST**

Every listener added to a long-lived element MUST be removed when no longer needed, or the element MUST be discarded. Otherwise, listeners leak memory.

### JS-053 — `localStorage` Discipline

**MUST NOT**

`localStorage` blocks the main thread and has a small quota. Large objects MUST NOT be stored. Sensitive data (tokens, PII) MUST NOT be stored there.

## Node.js Runtime

### JS-054 — `__dirname` Replacement in ESM

**MUST**

`__dirname` is not available in ESM. `import.meta.url` with `fileURLToPath` and `dirname` from `node:path` MUST be used instead.

### JS-055 — `node:` Prefix for Core Modules

**SHOULD**

The `node:` prefix SHOULD be used for core modules (e.g., `import fs from "node:fs"`). It distinguishes core modules from npm packages with the same name.

### JS-056 — `fs/promises` Over Callbacks

**SHOULD**

`fs/promises` SHOULD be preferred over callback-based `fs` APIs in async code.

### JS-057 — No `process.exit()` in Library Code

**MUST NOT**

Only the application entry point MUST call `process.exit()`. Library code MUST throw and let the caller decide.

### JS-058 — Streams for Large Data

**MUST**

Reading large files (e.g., >100 MB) with `readFile` crashes the process. Streams MUST be used for large data.

## Traps from Other Languages

### JS-060 — From Java: Class Overuse

**SHOULD NOT**

JavaScript favors plain objects, functions, and closures. Reaching for a class with static methods (as in Java) SHOULD NOT be done when a module of exported functions is clearer.

### JS-061 — From Python: Dict Mutation Discipline

**MUST NOT**

Python dicts are commonly mutated in place. In JavaScript, function arguments MUST NOT be mutated (see JS-023). A new object MUST be returned unless mutation is explicit in the function name.

### JS-062 — From Go: Error Return Values

**SHOULD NOT**

Go returns `(result, error)`. JavaScript throws or uses a Result type. Inventing a `[result, error]` tuple convention SHOULD NOT be done unless the project already uses it.

### JS-063 — From C/C++: Integer Division Assumption

**MUST NOT**

JavaScript has no integer division operator. `/` always produces a float. `Math.floor`, `Math.trunc`, or `Math.ceil` MUST be used explicitly. Assuming integer division produces silent wrong answers.

### JS-064 — From Rust: `null` Is Not `Option`

**MUST NOT**

JavaScript has no `Option<T>`. `null` and `undefined` are not a type-safe absence marker. For critical paths, a discriminated union (e.g., `{ kind: "some", value } | { kind: "none" }`) or a Result library SHOULD be used instead of relying on truthiness.

## AI-Specific JavaScript Discipline

### JS-080 — Runtime API Verification

**MUST**

Before using a runtime-specific API (Node `fs`, browser `localStorage`, Deno `Deno.readTextFile`), the assistant MUST verify it exists in the target runtime. Using Node-only APIs in browser code (or vice versa) produces silent runtime failures that are invisible at author time.

See MAS-036 in `_universal/00-master-anti-slop.md`.

### JS-081 — Existing Utility Discovery

**MUST**

Before writing a new utility function (e.g., `debounce`, `deepClone`, `formatDate`), the assistant MUST search the project and its declared dependencies for an existing equivalent. Inventing parallel utilities fragments the codebase and reintroduces bugs that established libraries have already solved.

See MAS-035 in `_universal/00-master-anti-slop.md`.

### JS-082 — Dynamic Pattern Restraint

**SHOULD**

The assistant SHOULD NOT introduce advanced dynamic patterns (Proxies, Reflect, metaprogramming, runtime code generation via `Function`) unless the project already uses them and the task strictly requires them. These patterns defeat static analysis and are a common source of AI-generated bugs.

See MAS-038 in `_universal/00-master-anti-slop.md`.

## Anti-Patterns

### JS-070 — Shared Mutable Module State

**MUST NOT**

A module-level `let cache = {}` that every function mutates MUST NOT exist. A dedicated cache module with a clear API, or no cache at all, MUST be used instead.

### JS-071 — `this` in Callbacks Without Binding

**MUST NOT**

Passing a method reference that relies on `this` without binding or arrow wrapping MUST NOT be done.

Example (illustrative, JavaScript):

BAD: `obj.on("event", function() { this.handle(); });`
GOOD: `obj.on("event", () => this.handle());` or bind explicitly.

### JS-072 — `new` With Factory Functions

**MUST NOT**

If a function returns an object, it MUST NOT be called with `new`. The `new` operator adds `this` binding rules that are easy to get wrong.

### JS-073 — Chained `||` for Default Values

**MUST NOT**

`const name = input || "default"` treats `0`, `""`, and `false` as missing. The nullish coalescing operator `??` MUST be used instead.

### JS-074 — `??` and `||` Precedence

**MUST**

`a ?? b || c` is a syntax error without parentheses. Even with parentheses, mixing them is confusing. The expression MUST be written explicitly: `(a ?? b) || c`.

### JS-075 — Optional Chaining Over Guard Chains

**SHOULD**

`user?.profile?.name` SHOULD be used instead of `user && user.profile && user.profile.name`. Optional chaining is shorter, clearer, and less error-prone.

### JS-076 — Non-Null Assertion Habit in Plain JS

**MUST NOT**

Plain JavaScript has no `!` non-null assertion. The TypeScript habit of assuming a value is non-null without checking MUST NOT be carried into plain JS. Explicit checks MUST be used.

### JS-077 — Node-Style Callback Signature

**MUST**

Node-style callbacks take `(err, result)`. A callback MUST NOT be called with a single argument when the convention is two; it silently misaligns consumers.

### JS-078 — Magic Numbers and Strings

**MUST NOT**

Magic numbers (`if (status === 3)`) and magic strings MUST NOT be used. Named constants (e.g., `STATUS.ACTIVE`) MUST be used instead.

### JS-079 — Deeply Nested Ternaries

**MUST NOT**

Deeply nested ternaries (`a ? "A" : b ? "B" : c ? "C" : "D"`) MUST NOT be used. A `switch`, a lookup table, or an `if/else` chain MUST be used instead.

### JS-083 — `JSON.parse(JSON.stringify(x))` for Deep Clone

**MUST NOT**

`JSON.parse(JSON.stringify(x))` loses `Date`, `Map`, `Set`, `undefined`, functions, and circular references. `structuredClone` (when available) or a proper deep-clone library MUST be used.

### JS-084 — `NaN` Comparison

**MUST NOT**

`NaN === NaN` is `false`. `Number.isNaN(x)` MUST be used instead of `x === NaN`.

### JS-085 — `typeof null` Trap

**MUST NOT**

`typeof null === "object"` is a historical bug. Branching on `typeof x === "object"` to detect objects MUST use `x !== null && typeof x === "object"`.

## Response to Violation

When a rule in this file is violated, report:

Violation: JS-{NNN}
Reason: {one-line reason}
Correction: {smallest fix}

For multiple violations, report each rule ID separately.

Do not replace a technical correction with a generic explanation.