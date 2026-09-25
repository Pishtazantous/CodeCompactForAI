---
id: 02-typescript-anti-slop
title: "TypeScript Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: language
version: 2
---

# TypeScript Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
generic security, dependency addition, output format) are NOT
repeated here.

This file covers rules specific to TypeScript: the type system,
strict mode, generics, narrowing, and the escape hatches that let
type errors hide at runtime. It does NOT cover framework rules
(React, Express, Next.js — see `domains/framework/`), delivery rules
(see `domains/delivery/`), or JavaScript semantics beyond what
TypeScript inherits (see `02-javascript-anti-slop.md`).

TypeScript's value is the type checker. Every rule below either
preserves that value or documents the rare case where a controlled
escape is justified. The checker is not an adversary; disabling it
to make an error go away is the single largest source of type-safety
loss.

## 1. Stack Assumptions

This file assumes:

- TypeScript 5.4 or later.
- `tsc` or a bundler that uses it (`vite`, `esbuild`, `swc`,
  `ts-node`, `tsx`).
- A `tsconfig.json` is present.
- The project uses ES modules.

### Version Applicability

- **Minimum version**: TypeScript 5.4.
- **Features used in this file that require specific versions**:
  - `using` declarations: TypeScript 5.2+.
  - `const` type parameters: TypeScript 5.0+.
  - `satisfies` operator: TypeScript 4.9+.
  - `accessor` keyword: TypeScript 4.9+.
  - `in` operator narrowing for unlisted keys: TypeScript 4.9+.
- **If the project targets an older version**: the version-specific
  syntax above is unavailable. The remaining rules still apply.

## 2. Compiler Configuration

### 2.1 `strict: true`

`tsconfig.json` has `strict: true`. If it does not, that is a
project decision, not something to change silently.

Rationale: `strict` enables eight related flags (`noImplicitAny`,
`strictNullChecks`, `strictFunctionTypes`, and others) that together
close the majority of type-safety holes.

### 2.2 Related Flags

Recommended flags, verified against the project's tsconfig:

- `noImplicitAny`
- `strictNullChecks`
- `strictFunctionTypes`
- `strictBindCallApply`
- `strictPropertyInitialization`
- `noImplicitThis`
- `useUnknownInCatchVariables`
- `noUnusedLocals`
- `noUnusedParameters`
- `noFallthroughCasesInSwitch`
- `noImplicitReturns`
- `noUncheckedIndexedAccess`
- `exactOptionalPropertyTypes`

Rationale: `noUncheckedIndexedAccess` catches array access that may
return `undefined`. `exactOptionalPropertyTypes` distinguishes
`prop?: T` from `prop: T | undefined`.

### 2.3 No Weakening Flags

Never add `// @ts-nocheck` at the top of a file. Never disable a
strict flag in `tsconfig.json` to fix a single error.

Rationale: weakening the config to silence an error hides the class
of errors the flag was designed to catch.

## 3. The `any` Type

### 3.1 No `any`

BAD:
```typescript
function handle(data: any) {
  return data.user.name;
}
```

GOOD:
```typescript
function handle(data: unknown): string {
  if (!isUserPayload(data)) throw new Error("invalid payload");
  return data.user.name;
}
```

Rationale: `any` disables type checking for the value and everything
it touches. A single `any` in a call chain propagates.

### 3.2 `unknown` Is the Correct Default

When the shape of incoming data is not known at compile time, use
`unknown`, then narrow with a type guard or schema.

Rationale: `unknown` forces the caller to prove the type before
using the value.

### 3.3 Justified `any`

There is one acceptable case: a broken third-party library type.
Even then:

- Isolate it in a single function.
- Add a comment explaining why.
- Wrap the result in a properly typed function.

Never let `any` leak into the caller.

### 3.4 `never` and `void`

- `never` is for functions that never return (throw, infinite loop).
- `void` is for functions that return nothing meaningful.

Rationale: `void` as a generic type argument to mean "no value" is
misleading; use `void` only as a return type.

## 4. Type Assertions

### 4.1 No `as` Without a Reason

BAD:
```typescript
const user = response as User;
```

GOOD:
```typescript
const user = userSchema.parse(response);
```

Rationale: `as` tells the compiler "trust me". When the trust is
misplaced, the error appears at runtime.

### 4.2 `as const` Is Allowed

`as const` narrows literals and is not an escape hatch. Use it
freely.

### 4.3 Double Assertions Are a Red Flag

`value as unknown as Target` means the types are genuinely
incompatible. Find the real type or introduce a runtime check.

### 4.4 Non-Null Assertion `!`

`value!.property` tells the compiler "this is not null". Use only
when the surrounding code guarantees it and the compiler cannot
see that.

BAD:
```typescript
const name = user!.profile!.name;
```

GOOD:
```typescript
const name = user?.profile?.name ?? "anonymous";
```

## 5. `@ts-ignore` and `@ts-expect-error`

### 5.1 `@ts-ignore` Is Forbidden

Rationale: it silences errors without any indication that the
silence is intentional. If the underlying issue is fixed, the
`@ts-ignore` remains and hides new errors.

### 5.2 `@ts-expect-error` Requires a Comment

```typescript
// @ts-expect-error -- library types are wrong; see issue #1234
user.doThing();
```

Rationale: `@ts-expect-error` at least fails when there is no error
to suppress. Every occurrence needs a comment.

### 5.3 Prefer Fixing the Type

Almost every `@ts-expect-error` is a type guard, a schema parse at
the boundary, or a correctly typed wrapper away from being
unnecessary.

## 6. Interfaces and Type Aliases

### 6.1 `interface` for Object Shapes

Use `interface` when the shape describes an object and might be
extended.

### 6.2 `type` for Everything Else

`type` for unions, intersections, mapped types, tuples, and simple
aliases.

### 6.3 Do Not Mix the Two for the Same Concept

Pick one style for a given entity. `interface User` in one file and
`type User = ...` in another is a consistency bug.

### 6.4 Extending vs Intersecting

- `interface Admin extends User` for extension.
- `type Admin = User & { role: Role }` when the base is a union or
  a generic.

### 6.5 Index Signatures Are a Smell

`{ [key: string]: T }` loses the shape. Use `Record<K, V>` when the
keys are dynamic, or an explicit interface when they are not.

## 7. Generics

### 7.1 Generics Express a Relationship

A generic parameter must relate two or more positions in the
signature.

BAD:
```typescript
function wrap<T>(value: T): { value: T } {
  return { value };
}
```

GOOD:
```typescript
function first<T>(items: readonly T[]): T | undefined {
  return items[0];
}
```

### 7.2 No Over-Constrained Generics

BAD:
```typescript
function identity<T extends Record<string, unknown>>(x: T): T {
  return x;
}
```

The constraint prevents callers from passing an array, a primitive,
or a class instance. It adds nothing.

GOOD:
```typescript
function identity<T>(x: T): T {
  return x;
}
```

### 7.3 Constrain Only What You Use

If the body accesses `x.id`, the constraint is `{ id: string }`. If
the body accesses nothing, there is no constraint.

### 7.4 `const` Type Parameters

```typescript
function tuple<const T extends readonly unknown[]>(...args: T): T {
  return args;
}
```

Rationale: `const T` preserves the literal types of the arguments
instead of widening them.

## 8. Narrowing and Type Guards

### 8.1 Prefer Narrowing Over Casting

TypeScript can often prove a type from control flow. Use `typeof`,
`instanceof`, `in`, and discriminated unions instead of casting.

### 8.2 Custom Type Guards

```typescript
function isUser(value: unknown): value is User {
  return (
    typeof value === "object" &&
    value !== null &&
    "id" in value &&
    typeof (value as { id: unknown }).id === "string"
  );
}
```

Rationale: a type guard is the only way to narrow `unknown` to a
structured type without a cast.

### 8.3 Schema Validation at Boundaries

At API, storage, and message boundaries, use the project's schema
library (`zod`, `valibot`, `io-ts`, `ajv`). Type guards for complex
shapes are derived from schemas, not written by hand.

### 8.4 Exhaustiveness Checks

For discriminated unions, use a `never` check in the default branch.

```typescript
function describe(status: Status): string {
  switch (status.kind) {
    case "ok": return "ok";
    case "error": return status.message;
    default: {
      const _exhaustive: never = status;
      throw new Error(`unhandled: ${JSON.stringify(_exhaustive)}`);
    }
  }
}
```

Rationale: the `never` check produces a compile error when a new
variant is added and the switch is not updated.

## 9. Utility Types

### 9.1 Use the Built-In Utility Types

`Partial`, `Required`, `Readonly`, `Pick`, `Omit`, `Record`,
`Exclude`, `Extract`, `NonNullable`, `ReturnType`, `Parameters`,
`Awaited`, `InstanceType`.

BAD:
```typescript
type MyRecord = { [key: string]: string };
```

GOOD:
```typescript
type MyRecord = Record<string, string>;
```

### 9.2 Avoid Deeply Nested Utility Types

`Omit<Partial<Pick<User, "a" | "b">>, "b">` is a sign the model
should be split. Define a named type.

```typescript
type UserDraft = Pick<User, "a">;
```

### 9.3 `satisfies` for Type Checking Without Widening

BAD:
```typescript
const config: Record<string, string | number> = {
  port: 3000,
  host: "localhost",
};
// config.port is string | number
```

GOOD:
```typescript
const config = {
  port: 3000,
  host: "localhost",
} satisfies Record<string, string | number>;
// config.port is number
```

Rationale: `satisfies` validates the value against the type without
widening the inferred type.

## 10. Enums and Namespaces

### 10.1 Prefer String Unions Over `enum`

BAD:
```typescript
enum Status {
  Active = "active",
  Inactive = "inactive",
}
```

GOOD:
```typescript
type Status = "active" | "inactive";
```

Rationale: string unions serialize to JSON naturally, generate no
runtime code, and work with `as const` objects.

### 10.2 `as const` Object for Iteration

```typescript
const STATUSES = ["active", "inactive"] as const;
type Status = (typeof STATUSES)[number];
```

### 10.3 No Numeric Enums

Numeric enums produce reverse mappings and are notoriously unsafe
(`Status[0]` compiles). Never use them.

### 10.4 No `const enum`

`const enum` has cross-module issues with modern bundlers and with
`isolatedModules`. Use `as const` objects or string unions.

### 10.5 No `namespace`

Use ES modules. `namespace` predates the module system and conflicts
with bundlers and `isolatedModules`.

## 11. Modules and Imports

### 11.1 No `require` in TypeScript

Use `import`. `require` defeats tree-shaking and type inference. The
exception is dynamic `import()` for lazy loading.

### 11.2 Type-Only Imports

```typescript
import type { User } from "./types";
```

Rationale: the import is erased at compile time and prevents
runtime cycles.

### 11.3 No `import * as X`

Namespace imports prevent tree-shaking. Import named exports
explicitly, unless the module is genuinely a namespace.

### 11.4 No Barrel Files

An `index.ts` re-exporting everything breaks tree-shaking, creates
circular import risk, and makes stack traces harder to read. Import
directly from the specific file.

### 11.5 Circular Imports Are a Design Smell

If two modules need each other, extract the shared type or function
into a third module.

## 12. Function Signatures

### 12.1 Explicit Return Types on Public Functions

Public (exported) functions have an explicit return type. This
prevents accidental widening and makes the contract readable.

Private functions may omit the return type when it is obvious.

### 12.2 Optional vs `undefined`

`prop?: T` and `prop: T | undefined` are not the same when
`exactOptionalPropertyTypes` is enabled. Match the project's
convention.

### 12.3 Default Parameters Over `undefined` Checks

BAD:
```typescript
function greet(name?: string) {
  name = name || "world";
  return `hello ${name}`;
}
```

GOOD:
```typescript
function greet(name = "world") {
  return `hello ${name}`;
}
```

Rationale: default parameters distinguish `undefined` from `null`,
`""`, `0`, and `false`.

### 12.4 Function Overloads Only When Necessary

Overloads are justified when each overload has a distinct return
type tied to the input type. Otherwise, a single signature with a
union is simpler.

## 13. Traps from Other Languages

### 13.1 From Java: Overuse of Classes

Java code often reaches for a class. TypeScript favors plain objects
and functions.

BAD:
```typescript
class UserService {
  static getUser(id: string) { /* ... */ }
}
```

GOOD:
```typescript
export function getUser(id: string) { /* ... */ }
```

### 13.2 From C#: Overuse of Interfaces

C# code often defines an interface for every class. TypeScript
favors structural typing; interfaces are used at module boundaries.

BAD: `interface IUserRepository` with a single implementation.

GOOD: A concrete `UserRepository` type. Add an interface only when
a second implementation exists.

### 13.3 From JavaScript: Implicit `any` Via Missing Types

JavaScript habits (no type annotations) produce implicit `any` under
`noImplicitAny: false`. Enable the flag and annotate.

### 13.4 From Python: Duck Typing by Default

Python relies on duck typing at runtime. TypeScript enforces it at
compile time. Write the types, do not rely on the runtime.

### 13.5 From Go: Error Return Values

Go returns `(result, error)`. TypeScript throws or uses a Result
type. Do not invent a `[result, error]` tuple unless the project
uses that pattern.

### 13.6 From Rust: Result Types Without the Ecosystem

`Result<T, E>` in TypeScript is fine, but there is no `?` operator.
Callers check the discriminant manually. Use it only when the
project already does.

## 14. Anti-Patterns

### 14.1 `any` in a Signature

Covered in 3.1.

### 14.2 `as` to Force a Type

Covered in 4.1.

### 14.3 `@ts-ignore` Without a Reason

Covered in 5.1.

### 14.4 `enum`

Covered in 10.1.

### 14.5 `namespace`

Covered in 10.5.

### 14.6 Double Assertion

Covered in 4.3.

### 14.7 Non-Null Assertion `!`

Covered in 4.4.

### 14.8 Implicit `any` in Function Parameters

```typescript
function handle(data) { /* data is any */ }
```

`noImplicitAny` catches this. Enable it.

### 14.9 Single-Field Interfaces

BAD:
```typescript
interface UserId { id: string; }
```

GOOD:
```typescript
type UserId = string;
```

Rationale: a single-field interface adds a layer with no shape
information.

### 14.10 `Partial<T>` for Update Payloads

BAD:
```typescript
function updateUser(id: string, data: Partial<User>) { /* ... */ }
```

This allows setting `id`, `createdAt`, and any field the caller
should not touch.

GOOD:
```typescript
function updateUser(id: string, data: UpdateUserInput) { /* ... */ }
```

### 14.11 Deeply Nested Conditional Types

A type with three levels of conditional types is unmaintainable.
Split into named types or replace with a runtime schema.

### 14.12 `Object` as a Type

BAD: `function handle(x: Object)`.

GOOD: `function handle(x: object)` or a specific shape.

Rationale: `Object` (uppercase) refers to the wrapper type and
matches almost anything.

### 14.13 `Function` as a Type

BAD: `function call(fn: Function)`.

GOOD: `function call(fn: (...args: unknown[]) => unknown)` or a
specific signature.

### 14.14 `{}` as a Type

BAD: `function handle(x: {})`.

GOOD: `function handle(x: object)`.

Rationale: `{}` matches almost every non-null value, including
primitives.

### 14.15 Casting Through `unknown`

Covered in 4.3.

### 14.16 Type Assertions on JSON Responses

BAD:
```typescript
const data = (await response.json()) as User;
```

GOOD:
```typescript
const data = userSchema.parse(await response.json());
```

### 14.17 `readonly` Missing on Public Arrays

BAD:
```typescript
function sum(values: number[]) {
  values.push(0); // mutates the caller's array
}
```

GOOD:
```typescript
function sum(values: readonly number[]) { /* ... */ }
```

### 14.18 `interface` Merging in Application Code

Declaration merging is a library feature. In application code, two
`interface User` declarations that merge silently confuse readers.

### 14.19 No `satisfies` for Config Objects

Without `satisfies`, a config object either widens or requires an
explicit type annotation that loses literal types.

### 14.20 `declare` for Runtime Values

`declare const X: T` asserts a value exists at runtime. If it does
not, the code fails silently. Use it only for genuinely ambient
values (globals injected by a bundler).

### 14.21 `// @ts-check` Missing in Plain JS Files

A `.js` file with `// @ts-check` gets checked. Without it, the file
is silently ignored by `tsc`.

### 14.22 Mutable Default Objects in Class Properties

```typescript
class Service {
  private cache: Record<string, string> = {}; // shared across instances
}
```

Class properties with object literals are per-instance, but the
initializer runs once if the class is transpiled to ES5. Prefer
assigning in the constructor.

### 14.23 `unknown` Without Narrowing

```typescript
function handle(data: unknown) {
  return data.name; // error: Object is of type 'unknown'
}
```

`unknown` is a promise to the reader: this value will be narrowed
before use. Using it without narrowing defeats the point.

### 14.24 `T extends any` in a Generic

BAD: `<T extends any>(x: T) => x`.

This is the same as `<T>(x: T) => x` but noisier.

### 14.25 Union Type With Overlapping Members

```typescript
type Status = "active" | "inactive" | string;
```

The `string` member makes the literals redundant. Narrow the union.

### 14.26 `Record<string, any>`

BAD: `const config: Record<string, any> = {}`.

GOOD: A typed config object with known keys.

### 14.27 `Promise<any>` Return Type

A promise that resolves to `any` disables typing for the resolved
value and its consumers.

### 14.28 Untyped Catch Variables Without `useUnknownInCatchVariables`

Without the flag, `catch (e)` types `e` as `any`. With the flag, `e`
is `unknown` and must be narrowed.

### 14.29 `ReadonlyArray<T>` Written as `readonly T[]` for Clarity

Both are valid. Match the project's convention. Mixed use is noise.

### 14.30 Type-Only Export Missing

```typescript
export { User } from "./types"; // not a type-only export
```

GOOD:
```typescript
export type { User } from "./types";
```

Rationale: type-only exports are erased at compile time, preventing
runtime imports of types.

## 15. Response to Violation

If a previous response violated a rule here:

```
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

No justification. No apology paragraph. Fix and move on.
