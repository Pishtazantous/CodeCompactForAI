---
id: 02-typescript-anti-slop
title: "TypeScript Anti-Slop Layer"
lang: en
depends_on: ["_universal/00-style-guide.md", "_universal/00-master-anti-slop.md", "domains/framework/02-architecture-anti-slop.md"]
category: domain
domain_type: language
version: 3
---

# TypeScript Anti-Slop Layer

This file defines behavioral contracts specific to the TypeScript language. It sits in the language layer, below the universal and architectural rules, and above framework-specific rules. It covers the type system, strict mode, generics, narrowing, and the escape hatches that let type errors hide at runtime. It does not cover framework rules (React, Express, Next.js — see `domains/framework/`), delivery rules (see `domains/delivery/`), or JavaScript semantics beyond what TypeScript inherits (see `02-javascript-anti-slop.md`).

TypeScript's value is the type checker. Every rule below either preserves that value or documents the rare case where a controlled escape is justified. The checker is not an adversary; disabling it to make an error go away is the single largest source of type-safety loss.

## Scope

This file applies to projects using TypeScript 5.4 or later, compiled with `tsc` or a compatible bundler (`vite`, `esbuild`, `swc`, `ts-node`, `tsx`), utilizing ES modules, and containing a `tsconfig.json` file.

### Version Applicability

- **Minimum version**: TypeScript 5.4.
- **Features requiring specific versions**:
  - `using` declarations: TypeScript 5.2+.
  - `const` type parameters: TypeScript 5.0+.
  - `satisfies` operator: TypeScript 4.9+.
  - `accessor` keyword: TypeScript 4.9+.
  - `in` operator narrowing for unlisted keys: TypeScript 4.9+.
- If the project targets an older version, the version-specific syntax above is unavailable, but the remaining rules still apply.

## Rule Severity

Severity follows `_universal/00-style-guide.md`.

## Contracts

A TypeScript codebase commits to four contracts. The table below maps each contract to the rules that enforce it.

| Contract | Description | Enforced By |
|---|---|---|
| Type Checker Integrity | Strict mode is enabled, and type escapes (`any`, `as`, `@ts-ignore`) are strictly controlled. | TS-001 to TS-014 |
| Structural Clarity | Interfaces, types, generics, and utility types are used predictably and without unnecessary complexity. | TS-015 to TS-030 |
| Module and Enum Discipline | Modern ES modules are used; legacy namespaces and unsafe enums are prohibited. | TS-031 to TS-040 |
| Signature and Boundary Safety | Function signatures are explicit, and boundary data is validated, not just asserted. | TS-041 to TS-044, TS-026 |

## Compiler Configuration

### TS-001 — Strict Mode Enforcement

**MUST**

The `tsconfig.json` MUST have `strict: true`. If it does not, that is a project decision that MUST NOT be changed silently. `strict` enables eight related flags that together close the majority of type-safety holes.

### TS-002 — Recommended Strict Flags

**SHOULD**

The following flags SHOULD be enabled and verified against the project's tsconfig: `noImplicitAny`, `strictNullChecks`, `strictFunctionTypes`, `strictBindCallApply`, `strictPropertyInitialization`, `noImplicitThis`, `useUnknownInCatchVariables`, `noUnusedLocals`, `noUnusedParameters`, `noFallthroughCasesInSwitch`, `noImplicitReturns`, `noUncheckedIndexedAccess`, and `exactOptionalPropertyTypes`. `noUncheckedIndexedAccess` catches array access that may return `undefined`.

### TS-003 — No Weakening Flags

**MUST NOT**

Adding `// @ts-nocheck` at the top of a file or disabling a strict flag in `tsconfig.json` to fix a single error MUST NOT occur. Weakening the config to silence an error hides the class of errors the flag was designed to catch.

## The `any` and `unknown` Types

### TS-004 — `any` Prohibition

**MUST NOT**

The `any` type MUST NOT be used. `any` disables type checking for the value and everything it touches; a single `any` in a call chain propagates and defeats the type system.

Example (illustrative, TypeScript):

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

### TS-005 — `unknown` as the Default

**MUST**

When the shape of incoming data is not known at compile time, `unknown` MUST be used, then narrowed with a type guard or schema. `unknown` forces the caller to prove the type before using the value.

### TS-006 — Justified `any` Isolation

**MAY**

The only acceptable case for `any` is a broken third-party library type. Even then, it MUST be isolated in a single function, commented, and wrapped in a properly typed function. `any` MUST NOT leak into the caller.

### TS-007 — `never` and `void` Discipline

**MUST**

`never` MUST be used for functions that never return (throw, infinite loop). `void` MUST be used for functions that return nothing meaningful. `void` MUST NOT be used as a generic type argument to mean "no value".

## Type Assertions and Escapes

### TS-008 — Unjustified `as` Prohibition

**MUST NOT**

The `as` keyword MUST NOT be used without a documented reason. `as` tells the compiler "trust me"; when the trust is misplaced, the error appears at runtime. Schema validation MUST be preferred.

Example (illustrative, TypeScript):

BAD: `const user = response as User;`
GOOD: `const user = userSchema.parse(response);`

### TS-009 — `as const` Allowance

**MAY**

`as const` narrows literals and is not an escape hatch. It MAY be used freely to preserve literal types.

### TS-010 — Double Assertion Prohibition

**MUST NOT**

Double assertions (`value as unknown as Target`) indicate genuinely incompatible types. The real type MUST be found or a runtime check introduced. Double assertions MUST NOT be used to bypass the compiler.

### TS-011 — Non-Null Assertion (`!`) Discipline

**SHOULD NOT**

The non-null assertion (`value!.property`) SHOULD NOT be used unless the surrounding code guarantees it and the compiler cannot see that. Optional chaining (`?.`) and nullish coalescing (`??`) SHOULD be preferred.

## `@ts-ignore` and `@ts-expect-error`

### TS-012 — `@ts-ignore` Prohibition

**MUST NOT**

`@ts-ignore` MUST NOT be used. It silences errors without any indication that the silence is intentional. If the underlying issue is fixed, the `@ts-ignore` remains and hides new errors.

### TS-013 — `@ts-expect-error` Documentation

**MUST**

Every `@ts-expect-error` MUST be accompanied by a comment explaining why the error is expected. `@ts-expect-error` fails when there is no error to suppress, making it safer than `@ts-ignore`.

### TS-014 — Type Fix Preference

**SHOULD**

Almost every `@ts-expect-error` is a type guard, a schema parse at the boundary, or a correctly typed wrapper away from being unnecessary. Fixing the type SHOULD be preferred over suppressing the error.

## Interfaces, Types, and Utility Types

### TS-015 — `interface` for Object Shapes

**SHOULD**

`interface` SHOULD be used when the shape describes an object and might be extended.

### TS-016 — `type` for Complex Structures

**SHOULD**

`type` SHOULD be used for unions, intersections, mapped types, tuples, and simple aliases.

### TS-017 — Concept Consistency

**MUST NOT**

Mixing `interface` and `type` for the same concept (e.g., `interface User` in one file and `type User = ...` in another) MUST NOT occur. One style MUST be picked per entity.

### TS-018 — Extending vs Intersecting

**SHOULD**

`interface Admin extends User` SHOULD be used for extension. `type Admin = User & { role: Role }` SHOULD be used when the base is a union or a generic.

### TS-019 — Index Signature Discipline

**SHOULD NOT**

Index signatures (`{ [key: string]: T }`) lose the shape and SHOULD NOT be used. `Record<K, V>` SHOULD be used when keys are dynamic, or an explicit interface when they are not.

### TS-020 — Generic Relationship Requirement

**MUST**

A generic parameter MUST relate two or more positions in the signature. Generics MUST NOT be used when the type does not flow through the function.

### TS-021 — Over-Constrained Generics Prohibition

**MUST NOT**

Generics MUST NOT be over-constrained (e.g., `<T extends Record<string, unknown>>` when the body does not require it). Over-constraining prevents callers from passing arrays, primitives, or class instances.

### TS-022 — Minimal Generic Constraints

**MUST**

If the body accesses `x.id`, the constraint MUST be `{ id: string }`. If the body accesses nothing, there MUST be no constraint.

### TS-023 — `const` Type Parameters

**SHOULD**

`const T` SHOULD be used to preserve the literal types of arguments instead of widening them (TypeScript 5.0+).

### TS-024 — Narrowing Over Casting

**SHOULD**

TypeScript can often prove a type from control flow. `typeof`, `instanceof`, `in`, and discriminated unions SHOULD be used instead of casting.

### TS-025 — Custom Type Guards

**MUST**

A custom type guard (`value is Type`) MUST be used to narrow `unknown` to a structured type without a cast.

### TS-026 — Schema Validation at Boundaries

**MUST**

At API, storage, and message boundaries, the project's schema library (`zod`, `valibot`, `io-ts`, `ajv`) MUST be used. Type guards for complex shapes MUST be derived from schemas, not written by hand.

### TS-027 — Exhaustiveness Checks

**MUST**

For discriminated unions, a `never` check MUST be used in the default branch to produce a compile error when a new variant is added and the switch is not updated.

### TS-028 — Built-In Utility Types

**SHOULD**

Built-in utility types (`Partial`, `Required`, `Readonly`, `Pick`, `Omit`, `Record`, `Exclude`, `Extract`, `NonNullable`, `ReturnType`, `Parameters`, `Awaited`, `InstanceType`) SHOULD be used instead of custom implementations.

### TS-029 — Deeply Nested Utility Types Prohibition

**MUST NOT**

Deeply nested utility types (e.g., `Omit<Partial<Pick<User, "a" | "b">>, "b">`) MUST NOT be used. The model SHOULD be split into named types.

### TS-030 — `satisfies` for Config Objects

**SHOULD**

The `satisfies` operator SHOULD be used for config objects to validate the value against a type without widening the inferred type (TypeScript 4.9+).

## Enums, Namespaces, and Modules

### TS-031 — String Unions Over `enum`

**SHOULD**

String unions (`type Status = "active" | "inactive"`) SHOULD be preferred over `enum`. String unions serialize to JSON naturally, generate no runtime code, and work with `as const` objects.

### TS-032 — `as const` Object Iteration

**SHOULD**

`as const` arrays SHOULD be used to derive union types for iteration (e.g., `type Status = (typeof STATUSES)[number]`).

### TS-033 — Numeric Enum Prohibition

**MUST NOT**

Numeric enums MUST NOT be used. They produce reverse mappings and are notoriously unsafe (e.g., `Status[0]` compiles).

### TS-034 — `const enum` Prohibition

**MUST NOT**

`const enum` MUST NOT be used. It has cross-module issues with modern bundlers and with `isolatedModules`.

### TS-035 — `namespace` Prohibition

**MUST NOT**

`namespace` MUST NOT be used. ES modules MUST be used instead. `namespace` predates the module system and conflicts with bundlers and `isolatedModules`.

### TS-036 — `require` Prohibition

**MUST NOT**

`require` MUST NOT be used in TypeScript. `import` MUST be used. `require` defeats tree-shaking and type inference. Dynamic `import()` is the exception for lazy loading.

### TS-037 — Type-Only Imports

**MUST**

`import type { User }` MUST be used when importing types. The import is erased at compile time and prevents runtime cycles.

### TS-038 — Namespace Import Prohibition

**MUST NOT**

`import * as X` MUST NOT be used unless the module is genuinely a namespace. Namespace imports prevent tree-shaking. Named exports MUST be imported explicitly.

### TS-039 — Barrel File Prohibition

**MUST NOT**

Barrel files (`index.ts` re-exporting everything) MUST NOT be used. They break tree-shaking, create circular import risk, and make stack traces harder to read. Imports MUST come directly from the specific file.

See ARCH-056 in `domains/framework/02-architecture-anti-slop.md`.

### TS-040 — Circular Import Resolution

**MUST NOT**

Circular imports MUST NOT exist. If two modules need each other, the shared type or function MUST be extracted into a third module. Type-only imports (`import type`) MUST be used to break type-level cycles.

## Functions and Signatures

### TS-041 — Explicit Return Types on Public Functions

**MUST**

Public (exported) functions MUST have an explicit return type. This prevents accidental widening and makes the contract readable. Private functions may omit the return type when it is obvious.

### TS-042 — Optional vs `undefined` Consistency

**MUST**

The distinction between `prop?: T` and `prop: T | undefined` MUST be handled consistently according to the project's `exactOptionalPropertyTypes` setting.

### TS-043 — Default Parameters Over `undefined` Checks

**SHOULD**

Default parameters (`name = "world"`) SHOULD be used instead of `undefined` checks (`name = name || "world"`). Default parameters distinguish `undefined` from `null`, `""`, `0`, and `false`.

### TS-044 — Function Overload Discipline

**SHOULD**

Function overloads SHOULD only be used when each overload has a distinct return type tied to the input type. Otherwise, a single signature with a union SHOULD be used.

## Traps from Other Languages

### TS-045 — Java Class Overuse

**SHOULD NOT**

TypeScript favors plain objects and functions. Reaching for a class with static methods (as in Java) SHOULD NOT be done. Exported functions SHOULD be used instead.

### TS-046 — C# Interface Overuse

**SHOULD NOT**

TypeScript favors structural typing. Defining an `IUserRepository` interface for every class (as in C#) SHOULD NOT be done. Interfaces SHOULD only be added when a second implementation exists.

### TS-047 — JavaScript Implicit `any`

**MUST NOT**

JavaScript habits (no type annotations) produce implicit `any` under `noImplicitAny: false`. The flag MUST be enabled and types MUST be annotated.

### TS-048 — Python Duck Typing

**MUST NOT**

Python relies on duck typing at runtime. TypeScript enforces it at compile time. Types MUST be written; runtime duck typing MUST NOT be relied upon.

### TS-049 — Go Error Return Values

**SHOULD NOT**

Go returns `(result, error)`. TypeScript throws or uses a Result type. Inventing a `[result, error]` tuple SHOULD NOT be done unless the project already uses that pattern.

### TS-050 — Rust Result Types

**SHOULD**

`Result<T, E>` in TypeScript is fine, but there is no `?` operator. Callers MUST check the discriminant manually. It SHOULD only be used when the project already does.

## AI-Specific TypeScript Discipline

### TS-070 — TS Type and API Verification

**MUST**

Before using a TypeScript utility type, compiler option, or third-party library type, the assistant MUST verify it exists in the target TypeScript version and library version. Invented utility types or incorrect generic constraints produce compiler errors that block the build.

See MAS-036 in `_universal/00-master-anti-slop.md`.

### TS-071 — Existing Type Discovery

**MUST**

Before creating a new type alias, interface, or generic utility, the assistant MUST search the project for an existing equivalent. Inventing parallel type definitions for the same domain concept creates type mismatches and casting bugs.

See MAS-035 in `_universal/00-master-anti-slop.md`.

### TS-072 — Type Complexity Restraint

**SHOULD**

The assistant SHOULD NOT introduce highly complex conditional types, deep mapped types, or template literal types unless the project already uses them and the type-level computation is strictly required. Runtime validation is often clearer than extreme type-level programming.

See MAS-038 in `_universal/00-master-anti-slop.md`.

## Anti-Patterns

### TS-051 — Single-Field Interfaces

**MUST NOT**

A single-field interface (`interface UserId { id: string; }`) MUST NOT be used. A type alias (`type UserId = string`) MUST be used instead. A single-field interface adds a layer with no shape information.

### TS-052 — `Partial<T>` for Update Payloads

**MUST NOT**

`Partial<T>` MUST NOT be used for update payloads. It allows setting `id`, `createdAt`, and any field the caller should not touch. A specific `UpdateUserInput` type MUST be used.

### TS-053 — Deeply Nested Conditional Types

**MUST NOT**

A type with three or more levels of conditional types is unmaintainable and MUST NOT be used. It MUST be split into named types or replaced with a runtime schema.

### TS-054 — `Object` as a Type

**MUST NOT**

`Object` (uppercase) MUST NOT be used as a type. It refers to the wrapper type and matches almost anything. `object` (lowercase) or a specific shape MUST be used.

### TS-055 — `Function` as a Type

**MUST NOT**

`Function` MUST NOT be used as a type. A specific signature (e.g., `(...args: unknown[]) => unknown`) MUST be used.

### TS-056 — `{}` as a Type

**MUST NOT**

`{}` MUST NOT be used as a type. It matches almost every non-null value, including primitives. `object` MUST be used.

### TS-057 — `readonly` on Public Arrays

**MUST**

Public arrays passed as arguments MUST be typed as `readonly T[]` to prevent the function from mutating the caller's array.

### TS-058 — `interface` Merging in Application Code

**MUST NOT**

Declaration merging (two `interface User` declarations merging silently) MUST NOT be used in application code. It is a library feature and confuses readers.

### TS-059 — `declare` for Runtime Values

**MUST NOT**

`declare const X: T` MUST NOT be used for runtime values unless they are genuinely ambient (globals injected by a bundler). If the value does not exist at runtime, the code fails silently.

### TS-060 — `// @ts-check` in Plain JS Files

**MUST**

A `.js` file in a TypeScript project MUST include `// @ts-check` at the top to be checked by `tsc`. Without it, the file is silently ignored.

### TS-061 — Mutable Default Objects in Class Properties

**MUST NOT**

Class properties initialized with object literals (`private cache = {}`) MUST NOT be used if the class is transpiled to ES5, as the initializer may run once and be shared. Assignment in the constructor MUST be used.

### TS-062 — `unknown` Without Narrowing

**MUST NOT**

`unknown` MUST NOT be used without narrowing. Using it without narrowing defeats the point of the type. `unknown` is a promise to the reader that the value will be narrowed before use.

### TS-063 — `T extends any` in a Generic

**MUST NOT**

`<T extends any>` MUST NOT be used. It is the same as `<T>` but noisier.

### TS-064 — Union Type With Overlapping Members

**MUST NOT**

A union type with overlapping members (e.g., `"active" | "inactive" | string`) MUST NOT be used. The `string` member makes the literals redundant. The union MUST be narrowed.

### TS-065 — `Record<string, any>`

**MUST NOT**

`Record<string, any>` MUST NOT be used. A typed config object with known keys or `Record<string, unknown>` MUST be used.

### TS-066 — `Promise<any>` Return Type

**MUST NOT**

A promise that resolves to `any` MUST NOT be returned. It disables typing for the resolved value and its consumers.

### TS-067 — Untyped Catch Variables

**MUST**

The `useUnknownInCatchVariables` flag MUST be enabled. Without it, `catch (e)` types `e` as `any`. With the flag, `e` is `unknown` and MUST be narrowed.

### TS-068 — `ReadonlyArray<T>` Syntax Consistency

**MUST**

The syntax for readonly arrays (`ReadonlyArray<T>` vs `readonly T[]`) MUST be consistent across the project. Mixed use is noise.

### TS-069 — Type-Only Export

**MUST**

When re-exporting types, `export type { User }` MUST be used. Type-only exports are erased at compile time, preventing runtime imports of types.

## Response to Violation

When a rule in this file is violated, report:

Violation: TS-{NNN}
Reason: {one-line reason}
Correction: {smallest fix}

For multiple violations, report each rule ID separately.

Do not replace a technical correction with a generic explanation.