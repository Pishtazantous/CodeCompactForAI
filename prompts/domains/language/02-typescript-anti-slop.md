---
id: 02-typescript-anti-slop
title: "TypeScript Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: language
version: 1
---

# TypeScript Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
security anti-patterns, output format) are NOT repeated here.

This file covers rules specific to TypeScript: the type system, strict
mode, generics, narrowing, and the common escape hatches that let type
errors hide at runtime. It is framework-agnostic. Framework rules
(React, Next.js, NestJS) live in `domains/framework/`.

## 1. Stack Assumptions

This layer assumes:

- TypeScript is compiled by `tsc` or a bundler that uses it (`vite`,
  `esbuild`, `swc`, `ts-node`, `tsx`).
- The project has a `tsconfig.json`. The exact options may vary, but
  `strict: true` is the baseline unless the project has a documented
  reason not to.
- Type information is available to the editor and to CI. There is no
  assumption of runtime type checking unless the project uses a schema
  library.

## 2. Strict Mode and Compiler Options

### 2.1 `strict: true`

`tsconfig.json` has `strict: true`. If it does not, that is a project
decision and not something to change silently. Do not disable strict
mode to make a type error go away.

### 2.2 Related Flags

The following flags are recommended and are typically enabled when
`strict: true` is on, but verify against the project's tsconfig:

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

If the project enables additional flags (`exactOptionalPropertyTypes`,
`noUncheckedIndexedAccess`), respect them. Do not write code that
requires weakening them.

### 2.3 No Weakening Flags Without Permission

Never add `// @ts-nocheck` at the top of a file. Never disable a strict
flag in `tsconfig.json` to fix a single error. Never add `skipLibCheck:
true` unless it is already there.

## 3. The `any` Type

### 3.1 No `any`

`any` disables type checking for the value and everything it touches.
It is the single largest source of type-safety loss in TypeScript.

BAD:
typescript
function handle(data: any) {
  return data.user.name;
}
GOOD:

typescript
function handle(data: unknown): string {
  if (!isUserPayload(data)) throw new Error("invalid payload");
  return data.user.name;
}
3.2 unknown Is the Correct Default
When the shape of incoming data is not known at compile time, use
unknown, then narrow it with a type guard.

3.3 never and void
never is for functions that never return (throw, infinite loop).

void is for functions that return nothing meaningful.

Do not use void as a generic type argument to mean "no value".

3.4 Justified any
There is one acceptable case: interacting with a library whose types are
broken. Even then:

Isolate it in a single function.

Add a comment explaining why.

Wrap the result in a properly typed function.

Never let any leak into the caller.

4. Type Assertions and Casts
4.1 No as Without a Reason
as tells the compiler "trust me". When the trust is misplaced, the
error appears at runtime, not at compile time.

BAD:

typescript
const user = response as User;
GOOD:

typescript
const user = userSchema.parse(response);
4.2 as const Is Allowed
as const narrows literals and is not a type-safety escape hatch. Use
it freely.

4.3 Double Assertions Are a Red Flag
value as unknown as Target means the types are genuinely incompatible.
This is almost always a bug. Find the real type.

4.4 Non-Null Assertion !
value!.property tells the compiler "this is not null". Use only when
the surrounding code guarantees it and the compiler cannot see that.
Never use ! to silence strictNullChecks.

5. @ts-ignore and @ts-expect-error
5.1 @ts-ignore Is Forbidden
It silences errors without any indication that the silence is
intentional. If someone later fixes the underlying issue, the
@ts-ignore remains and hides new errors.

5.2 @ts-expect-error Requires a Comment
@ts-expect-error at least fails when there is no error to suppress. It
is acceptable in tests and for known library bugs, but every occurrence
needs a comment explaining what is being suppressed and why.

BAD:

typescript
// @ts-expect-error
user.doThing();
GOOD:

typescript
// @ts-expect-error -- library types are wrong; see issue #1234
user.doThing();
5.3 Prefer Fixing the Type
In almost every case where @ts-expect-error seems necessary, one of
these fixes the problem properly:

A type guard

A schema parse at the boundary

A correctly typed wrapper

A generic that captures the actual type

6. Interfaces and Type Aliases
6.1 interface for Object Shapes
Use interface when the shape describes an object and might be
extended by a consumer.

6.2 type for Everything Else
Use type for unions, intersections, mapped types, tuples, and simple
aliases.

6.3 Do Not Mix the Two for the Same Concept
Pick one style for a given entity. Do not declare interface User in
one file and type User = ... in another.

6.4 Extending vs Intersecting
interface Admin extends User is preferred for extension.

type Admin = User & { role: Role } is acceptable when the base is
a union or a generic.

6.5 Index Signatures Are a Smell
{ [key: string]: T } loses the shape of the object. Use a Record
when the keys are genuinely dynamic, or an explicit interface when they
are not.

7. Generics
7.1 Generics Express a Relationship
A generic parameter must relate two or more positions in the signature.
If the type parameter appears only once, it is not a generic, it is a
type alias.

BAD:

typescript
function wrap<T>(value: T): { value: T } {
  return { value };
}
Here T appears twice, but the function is still trivial. Use a
concrete type.

GOOD:

typescript
function first<T>(items: readonly T[]): T | undefined {
  return items[0];
}
T relates the input element type to the return type.

7.2 No Over-Constrained Generics
BAD:

typescript
function identity<T extends Record<string, unknown>>(x: T): T {
  return x;
}
The constraint adds nothing. It prevents callers from passing an
array, a primitive, or a class instance.

GOOD:

typescript
function identity<T>(x: T): T {
  return x;
}
7.3 Constrain Only What You Use
If the body accesses x.id, the constraint is { id: string }. If the
body does not access anything, there is no constraint.

7.4 Default Type Parameters
Use a default type parameter when there is a sensible common case:

typescript
type Result<T, E = Error> = { ok: true; value: T } | { ok: false; error: E };
7.5 No Conditional Types for Simple Problems
Conditional types are powerful and unreadable. If a conditional type
needs a comment to explain, replace it with two overloads, a union, or
a schema-driven type.

8. Narrowing and Type Guards
8.1 Prefer Narrowing Over Casting
TypeScript can often prove a type from the surrounding control flow.
Use typeof, instanceof, in, and discriminated unions instead of
casting.

8.2 Custom Type Guards
When narrowing on a structured shape, write a type guard:

typescript
function isUser(value: unknown): value is User {
  return (
    typeof value === "object" &&
    value !== null &&
    "id" in value &&
    typeof (value as { id: unknown }).id === "string"
  );
}
8.3 Schema Validation at Boundaries
At API, storage, and message boundaries, use the project's schema
library (zod, valibot, io-ts, ajv). Type guards for complex
shapes should be derived from schemas, not written by hand.

8.4 Exhaustiveness Checks
For discriminated unions, use a never check in the default branch:

typescript
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
This forces a compile error when a new variant is added and the switch
is not updated.

9. Utility Types
9.1 Use the Built-In Utility Types
The standard library provides Partial, Required, Readonly,
Pick, Omit, Record, Exclude, Extract, NonNullable,
ReturnType, Parameters, Awaited, InstanceType.

Do not re-implement them.

BAD:

typescript
type MyRecord = { [key: string]: string };
GOOD:

typescript
type MyRecord = Record<string, string>;
9.2 Avoid Deeply Nested Utility Types
A type like
Omit<Partial<Pick<User, "a" | "b">>, "b"> is a sign that the model
should be split. Define a named type:

typescript
type UserDraft = Pick<User, "a">;
10. Enums
10.1 Prefer String Unions Over enum
BAD:

typescript
enum Status {
  Active = "active",
  Inactive = "inactive",
}
GOOD:

typescript
type Status = "active" | "inactive";
String unions:

Serialize naturally to JSON.

Do not generate runtime code.

Work with const objects for iteration.

10.2 const Object for Iteration
When a runtime list of values is needed:

typescript
const STATUSES = ["active", "inactive"] as const;
type Status = (typeof STATUSES)[number];
10.3 No Numeric Enums
Numeric enums produce reverse mappings and are notoriously unsafe
(Status[0] compiles). Never use them.

10.4 No const enum
const enum has cross-module issues with modern bundlers and with
isolatedModules. Use as const objects or string unions instead.

11. Modules and Imports
11.1 No namespace
Use ES modules. namespace predates the module system and conflicts
with bundlers and isolatedModules.

11.2 No require in TypeScript
Use import. require defeats tree-shaking and type inference. The
only exception is dynamic import() for lazy loading.

11.3 Type-Only Imports
When importing only types, use import type:

typescript
import type { User } from "./types";
This ensures the import is erased at compile time and prevents runtime
cycles.

11.4 Avoid import * as X
Namespace imports prevent tree-shaking. Import named exports
explicitly, unless the module is genuinely a namespace.

11.5 Circular Imports
Circular imports are a design smell. If two modules need each other,
extract the shared type or function into a third module.

12. Function Signatures
12.1 Explicit Return Types on Public Functions
Public functions (exported from a module) have an explicit return type.
This prevents accidental widening and makes the contract readable.

Private functions may omit the return type if it is obvious.

12.2 Optional vs undefined
prop?: T and prop: T | undefined are not the same when
exactOptionalPropertyTypes is on. Match the project's convention.

12.3 Default Parameters Over undefined Checks
BAD:

typescript
function greet(name?: string) {
  name = name || "world";
  return `hello ${name}`;
}
GOOD:

typescript
function greet(name = "world") {
  return `hello ${name}`;
}
12.4 Overloads vs Unions
Overloads are justified when each overload has a distinct return type
tied to the input type. Otherwise, a single signature with a union is
simpler.

13. TypeScript-Specific Anti-Patterns
13.1 The as Chain
BAD: value as A as B as C to force a value through incompatible
types.
GOOD: Parse the value with a schema at the boundary, then work with the
typed result.

13.2 Object as a Type
BAD: function handle(x: Object)
GOOD: function handle(x: object) (lowercase), or a specific shape.

Object (uppercase) refers to the wrapper type. It allows almost
anything.

13.3 Function as a Type
BAD: function call(fn: Function)
GOOD: function call(fn: (...args: unknown[]) => unknown) or a specific
signature.

13.4 {} as a Type
BAD: function handle(x: {})
GOOD: function handle(x: object) or function handle(x: Record<string, unknown>).

{} matches almost every non-null value including primitives.

13.5 Single-Field Interfaces
BAD:

typescript
interface UserId { id: string; }
GOOD:

typescript
type UserId = string;
Or a branded type if the identity must be distinguished.

13.6 Deeply Nested Conditional Types
If a type uses conditional types three levels deep, no one on the team
can maintain it. Split into named intermediate types or replace with a
runtime schema.

13.7 Partial<T> Everywhere
BAD: function updateUser(data: Partial<User>).
This allows setting any field, including id, createdAt, and fields
the caller should not touch.

GOOD: function updateUser(data: UpdateUserInput), where
UpdateUserInput is an explicit type containing only the fields that
may change.

13.8 Type Assertions on JSON Responses
BAD:

typescript
const data = await response.json() as User;
GOOD:

typescript
const data = userSchema.parse(await response.json());
response.json() returns any. An assertion erases the need to
validate.

13.9 Casting Through unknown
BAD: value as unknown as Target.
GOOD: Find the actual type or write a type guard.

13.10 Mixing type and interface for the Same Entity
BAD: interface User in types.ts and type User = ... in
models.ts.
GOOD: One declaration per entity, one style across the codebase.

13.11 Treating null and undefined as Interchangeable
BAD: Returning null in one function and undefined in another for
"missing value".
GOOD: Pick one (usually undefined in TypeScript), and be consistent.

13.12 any in Function Signatures of Libraries
BAD: A wrapper around a third-party library that declares parameters as
any.
GOOD: Type the wrapper with the actual accepted shape. If the library's
types are wrong, wrap the library call and expose a typed function.

14. Response to Violation
If a previous response violated a rule here:



In the previous response, [specific rule] was violated. Correction:
[corrected code]
No justification. No apology paragraph. Fix and move on.