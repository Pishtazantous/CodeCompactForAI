---
id: 02-architecture-anti-slop
title: "Architecture Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: framework
version: 2
---

# Architecture Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
generic security, dependency addition, output format) are NOT
repeated here.

This file covers architectural principles that apply regardless of
framework, language, or delivery type: layering, dependency
direction, boundaries, folder structure, naming, composition, and
abstraction discipline. It is the base layer that every framework
file builds on. It does NOT cover framework-specific patterns (see
the sibling framework files), language rules (see the language
files), delivery rules (see the delivery files), or visual design
(see the UI files).

Architecture is the set of decisions that are expensive to reverse.
Every rule below is a decision that is cheaper to make correctly the
first time than to fix later.

## 1. Scope

This file is deliberately framework-agnostic. It applies to:

- Frontend applications (React, Vue, Svelte, Angular, Solid).
- Backend services (Express, NestJS, FastAPI, Django, Rails).
- Desktop and mobile applications.
- CLI tools and libraries.

Rules here describe how to organize a codebase, not how to use a
specific tool. When a rule conflicts with the project's existing
architecture, the project wins. Report the conflict instead of
silently diverging.

### Framework Lifecycle Contracts

Even though this file is framework-agnostic, it enforces five
architectural contracts that every codebase shares. Every section
below reinforces one or more of these.

#### Contract 1: Layers Are Real

Every file belongs to a layer. The layer determines what the file
may import and what may import it. A file that belongs to no layer
is unmaintainable.

#### Contract 2: Dependencies Point Inward

Inner layers (domain, business logic) do not depend on outer layers
(infrastructure, frameworks, I/O). The outer layers depend on the
inner ones.

#### Contract 3: Boundaries Are Explicit

Each module has a public API. Everything else is internal. Reaching
into another module's internals is forbidden.

#### Contract 4: Names Describe Purpose

A reader understands what a file does without opening it. Names are
the first layer of documentation and the only one that never goes
stale.

#### Contract 5: Abstraction Removes Code

An abstraction reduces total cognitive cost, not line count. A
refactor that replaces 100 lines of direct code with 100 lines of
indirect code is rearrangement, not abstraction.

## 2. Reference the Existing Architecture First

### 2.1 Read Before Writing

Before writing any new file, folder, or module:

1. Fetch two or three files from the layer you are about to modify.
2. Fetch one file from a layer above (if it consumes yours).
3. Fetch one file from a layer below (if you consume it).
4. Identify the naming, import, and dependency pattern.
5. Follow that pattern exactly.

Rationale: introducing a second architecture into a codebase that
already has one is the largest single source of structural slop.

### 2.2 No Architecture Without a Reason

If the project has no discernible pattern, stop and ask before
inventing one.

Rationale: a new architecture proposed by an AI on a Tuesday is
usually abandoned by Friday. Structure emerges from real needs, not
from a desire for order.

### 2.3 Consistency Beats Preference

If the project uses a pattern you would not choose, follow it
anyway. The cost of inconsistency is higher than the cost of an
imperfect pattern.

## 3. Layering Principles

### 3.1 Identify the Layers

Most projects have some version of these layers:

- **Entry**: where the application starts. CLI `main`, HTTP router,
  React `App`, `index.js`.
- **Interface**: how the outside world reaches the app. Routes,
  controllers, pages, commands, views.
- **Application**: orchestration. Use cases, services, handlers.
- **Domain**: business rules. Entities, value objects, pure
  functions.
- **Infrastructure**: external systems. Database adapters, HTTP
  clients, message queues, file storage.

Not every project needs all five. Small projects collapse Interface
and Application. Libraries collapse everything except Domain and
Infrastructure.

Rationale: the goal is not to have five layers. The goal is to have
a clear answer to "what does this file belong to?"

### 3.2 One Concern Per Layer

A file in the Interface layer does not contain SQL. A file in the
Domain layer does not import a framework. A file in the
Infrastructure layer does not contain business rules.

BAD:
```typescript
// domain/user.ts
import { db } from "../infra/database";

export function isActiveUser(id: string) {
  const row = db.query("SELECT active FROM users WHERE id = ?", [id]);
  return row.active === 1;
}
```

The Domain file knows about the database.

GOOD:
```typescript
// domain/user.ts
export interface UserRepository {
  findActive(id: string): Promise<boolean>;
}

export function isActiveUser(repo: UserRepository, id: string) {
  return repo.findActive(id);
}
```

The Domain file depends on an interface, not on the database.

### 3.3 Reference the Project's Layer Names

The project may use different names:

- `app/`, `pages/`, `routes/` for Interface.
- `services/`, `use-cases/`, `handlers/` for Application.
- `domain/`, `entities/`, `models/` for Domain.
- `infra/`, `adapters/`, `providers/` for Infrastructure.
- `lib/`, `utils/`, `shared/` for cross-cutting.

Match the project. Do not rename a folder to match a textbook.

### 3.4 No Cross-Layer Cycles

If layer A depends on layer B and layer B depends on layer A, the
layers are not layers. Either merge them or introduce a third module
both depend on.

Rationale: cycles make the codebase unanalyzable. A change to A may
require a change to B, which requires a change to A, and so on.

## 4. Dependency Direction

### 4.1 Dependencies Point Inward

The canonical direction:

```
Entry -> Interface -> Application -> Domain
                          |
                          v
                    Infrastructure
```

Entry depends on everything. Domain depends on nothing (or only on
its own types). Infrastructure depends on Domain abstractions, not
the other way around.

### 4.2 Never Import Upward

A Domain file importing from Infrastructure couples business rules
to a specific database or HTTP client.

BAD:
```typescript
// domain/order.ts
import { stripe } from "../infra/stripe";

export async function pay(order: Order) {
  return stripe.charges.create({ amount: order.total });
}
```

GOOD:
```typescript
// domain/order.ts
export interface PaymentGateway {
  charge(amount: number): Promise<PaymentResult>;
}

export async function pay(gateway: PaymentGateway, order: Order) {
  return gateway.charge(order.total);
}
```

The Domain layer declares what it needs. Infrastructure provides it.

### 4.3 Frameworks at the Edges

Frameworks (Express, React, NestJS, FastAPI) belong in the outer
layers. A pure function in the Domain layer does not import
`express`, `react`, or `fastapi`.

BAD:
```typescript
// domain/price.ts
import { Request } from "express";

export function calculatePrice(req: Request) {
  return req.body.quantity * 10;
}
```

GOOD:
```typescript
// domain/price.ts
export function calculatePrice(quantity: number): number {
  return quantity * 10;
}
```

### 4.4 Cross-Cutting Concerns via Middleware or Decorators

Logging, authentication, validation, and telemetry are
cross-cutting. They belong in:

- Middleware (HTTP, gRPC).
- Decorators (NestJS, TypeScript).
- Explicit calls from the Application layer.

They do not belong in the Domain layer. A `User.authenticate()`
method that logs is a Domain file doing Infrastructure work.

### 4.5 Dependency Inversion for the Domain

When the Domain needs something from Infrastructure, it declares an
interface. Infrastructure implements it. The wiring happens at
composition time (the entry point).

Rationale: the Domain layer defines the language of the problem.
Infrastructure adapts to it.

## 5. Boundaries

### 5.1 Explicit Module Boundaries

Each top-level module has a public API. Everything else is internal.

- TypeScript: `index.ts` or explicit exports from the module root.
- Python: `__all__` or `__init__.py` with explicit exports.
- Go: package boundaries (one folder, one package).
- Rust: `pub` items in the module's root.

Rationale: a module without a boundary is a folder that everything
can reach into.

### 5.2 No Deep Imports

BAD:
```typescript
import { formatAmount } from "@/features/billing/internal/helpers/format";
```

GOOD:
```typescript
import { formatAmount } from "@/features/billing";
```

Rationale: a deep import couples the consumer to the internal
structure of the module. Refactoring the module breaks the consumer.

### 5.3 Shared Code Is Earned

Before moving code into a `shared/` or `common/` folder:

1. Two or more modules use it.
2. The usage is stable, not a one-time reuse.
3. The code is genuinely generic, not domain-specific.

Rationale: a shared module with one consumer is a coupling that
makes the codebase harder to change.

### 5.4 No Bidirectional Module Dependencies

Two modules that depend on each other are not modules; they are one
module split by accident. Merge them or extract the shared piece.

### 5.5 Explicit Public API in Each Module

A module with no documented public API has no boundary. The
`index.ts` (or equivalent) is the contract.

BAD: `features/billing/index.ts` re-exports everything from every
internal file.

GOOD: `features/billing/index.ts` exports only what consumers need.

## 6. Folder Structure

### 6.1 No Premature Folder Creation

Create a folder when it holds at least three files.

BAD: A new project with `features/`, `modules/`, `domains/`,
`services/`, `shared/`, `core/`, `common/`, `utils/` all created on
day one.

GOOD: A new project with `src/` and whatever folders the code
actually needs.

Rationale: empty folders are structure slop. They signal an
architecture that has not been earned.

### 6.2 Feature or Layer, Not Both

Two valid organizations:

- **By layer**: `controllers/`, `services/`, `models/`.
- **By feature**: `billing/`, `auth/`, `notifications/`, each with
  its own layers inside.

Mixing them produces `controllers/billing/` and
`billing/controllers/` in the same codebase. Pick one.

### 6.3 No Folders Named After Design Patterns

BAD: `factories/`, `strategies/`, `observers/`, `singletons/`.

GOOD: `payments/`, `auth/`, `email/`. Name by domain, not by
pattern.

Rationale: a folder named after a pattern ages poorly. When the
pattern changes, the folder name lies.

### 6.4 Shallow Trees

A path like `src/components/forms/inputs/text/fields/validators/` is
a sign that the tree is built top-down instead of bottom-up.

Rule of thumb: three levels below `src/` should cover most projects.
Beyond five levels, the structure is wrong.

### 6.5 Colocate by Default

Files that change together live together:

- A component and its styles.
- A test and the file it tests.
- A service and the types it uses.

Rationale: scattering related files across distant folders does not
keep folders small; it keeps changes scattered.

### 6.6 No "utils" Folder That Grows Without Bound

A single `utils.ts` that grows to 500 lines becomes a dependency
magnet.

BAD: `utils/` with `formatDate.ts`, `parseUrl.ts`,
`sendEmail.ts`, `validatePassword.ts`.

GOOD: Each utility in the module where it is used, or split by
purpose (`format/`, `validation/`).

## 7. Naming

### 7.1 Names Describe Purpose, Not Type

BAD: `userService.ts`, `paymentManager.ts`, `orderController.ts`,
`notificationHelper.ts`.

GOOD: `createUser.ts`, `payOrder.ts`, `sendNotification.ts`,
`userLookup.ts`.

Rationale: `Service`, `Manager`, `Helper`, `Utility`, `Handler`,
`Controller`, `Processor`, `Wrapper`, `Factory` are filler words.
They do not describe what the thing does.

### 7.2 Verbs for Functions, Nouns for Data

- Functions: `getUser`, `calculateTotal`, `validateEmail`.
- Types and interfaces: `User`, `Order`, `EmailAddress`.
- Booleans: `isActive`, `hasPermission`, `canEdit`.

BAD: `function user() { ... }` returning a `User`.
BAD: `const active = true;` (active what?).

GOOD: `const isActive = true;`.

### 7.3 No Abbreviations Except Established Ones

`ctx`, `req`, `res`, `id`, `url`, `http`: fine.
`usr`, `mgr`, `svc`, `cfg`, `btn`, `lbl`: not fine.

### 7.4 Consistent Casing

Match the project's convention:

- `camelCase` files and identifiers in most JS/TS projects.
- `snake_case` in Python and many Go projects.
- `PascalCase` for React components and classes.
- `kebab-case` for CSS classes.

Do not mix. `createUser.ts` and `create_user.py` in the same project
is fine. `createUser.ts` and `create_user.ts` is not.

### 7.5 Plural for Collections, Singular for Items

Folders that hold many: `users/`. Files that define one: `user.ts`.
Pick a convention and apply it everywhere.

BAD: `users/` folder containing `user-repository.ts`,
`all-users.ts`, and `create-user.ts`. The folder says "many", the
files say "one".

GOOD: `users/` containing `repository.ts`, `list.ts`, `create.ts`.

### 7.6 No Names That Contradict the Layer

A file in `services/` named `UserRepository` is a category error.
The name and the layer must agree.

## 8. Composition Over Inheritance

### 8.1 Prefer Composition

Assemble behavior from small pieces. Inherit only when there is a
genuine "is-a" relationship and the base class is designed for
extension.

BAD:
```typescript
class BaseController {
  protected log(msg: string) { console.log(msg); }
  protected validate(data: unknown) { /* ... */ }
}

class UserController extends BaseController { /* ... */ }
```

GOOD:
```typescript
function withLogging<T extends (...args: any[]) => any>(handler: T): T {
  return ((...args) => {
    console.log(`calling ${handler.name}`);
    return handler(...args);
  }) as T;
}

const createUser = withLogging(createUserHandler);
```

### 8.2 Depth of Inheritance Is a Cost

An inheritance chain of three or more levels is hard to reason about.
Flatten to composition.

### 8.3 No Mixins Without a Reason

Mixins couple the mixin and the mixed-in class in both directions.
Prefer a function that takes a class and returns a decorated one.

### 8.4 Interfaces for Behavior

When two types share a method set, express it as an interface,
protocol, or trait. This allows composition without inheritance.

### 8.5 No Base Class for Convenience

A `BaseService` that provides helper methods is a base class for
convenience. Those helpers belong in a utility function or a
composed module.

## 9. Abstraction Discipline

### 9.1 Rule of Three

An abstraction is justified when it has at least three real usages.

BAD:
```typescript
function fetchAndParse<T>(url: string, schema: ZodSchema<T>): Promise<T> {
  // used in two places
}
```

GOOD: Inline in each place until a third usage appears.

Rationale: two usages with slightly different shapes are usually not
the same abstraction.

### 9.2 No Abstraction for Anticipated Change

"Maybe later we will need to swap the database" is not a reason to
introduce a repository interface today. Wait for the second
implementation.

### 9.3 No Abstraction Over Trivial Code

A wrapper around `localStorage.getItem` is not an improvement. It
hides a two-line API behind a five-line module.

### 9.4 Abstraction Must Remove Code

A refactor that replaces 100 lines of direct code with 100 lines of
indirect code plus a new file is rearrangement. An abstraction
reduces total cognitive cost.

### 9.5 No Interfaces for a Single Implementation

An `IUserRepository` with one implementation and no mock is
overhead. Wait for a second implementation or a test mock that
actually needs it.

### 9.6 Composition of Small Functions Over Deep Class Hierarchies

A function that composes three small functions is easier to test and
reason about than a class with a five-level hierarchy.

## 10. Configuration Flow

### 10.1 Configuration Flows Down

The application entry point reads configuration and passes it down.
Domain and Application layers receive what they need as arguments,
not by reading globals.

BAD:
```typescript
// domain/pricing.ts
export function calculatePrice(items: Item[]) {
  const taxRate = process.env.TAX_RATE; // hidden global
  return items.reduce((sum, i) => sum + i.price * (1 + taxRate), 0);
}
```

GOOD:
```typescript
// domain/pricing.ts
export function calculatePrice(items: Item[], taxRate: number) {
  return items.reduce((sum, i) => sum + i.price * (1 + taxRate), 0);
}

// entry point
const taxRate = Number(config.getOrThrow("TAX_RATE"));
```

### 10.2 No Hidden Configuration

A module that reads from a global config object is coupled to that
global. If the module is testable only when the global is set up,
the configuration is hidden.

### 10.3 Configuration Is Validated at Startup

Every required config value is checked at boot. A missing value
fails immediately, not at the first request that needs it.

### 10.4 Environment-Specific Values Are Not in Code

URLs, keys, feature flags, and connection strings come from
configuration, not from source.

## 11. Documentation of Architecture

### 11.1 Architecture Is Documented

A `docs/architecture.md` or a README section describes the layers,
the dependency direction, and the boundaries. A new contributor
reads it before writing code.

### 11.2 The Document Is Short

A 500-line architecture document is not read. A one-page summary
with links to examples is.

### 11.3 Diagrams Where Helpful

An ASCII or Mermaid diagram of the layers and their dependencies.
Not a screenshot of a whiteboard.

### 11.4 Updates With the Code

When the architecture changes, the document is updated in the same
commit. A stale architecture document is worse than none.

## 12. Anti-Patterns

### 12.1 The Everything Module

A single `utils.ts` (or `helpers.py`, or `common.go`) that grows to
500 lines and is imported by half the codebase. It becomes a
dependency magnet and a merge-conflict generator.

### 12.2 The God Object

A class or module that knows about every other part of the system.
Signs: it imports more than 10 modules, it has more than 20 public
methods, its test file is the largest in the repo.

### 12.3 The Leaky Abstraction

A wrapper that exposes details of what it wraps.

BAD: A `Database` class with a `getRawConnection()` method that
callers use to run raw SQL.

GOOD: The wrapper hides the connection. Callers use the methods.

### 12.4 The Premature Framework

Introducing a dependency-injection framework, an event bus, and a
plugin system into a project with no users. Frameworks are solutions
to problems at scale. At small scale, they are the problem.

### 12.5 The Two Architectures

Half the codebase uses `services/`, the other half uses
`use-cases/`. Both do the same thing. Choose one.

### 12.6 The Framework in the Domain

A `User` class that extends an ORM's `Model`, or a `PaymentService`
decorated with framework-specific annotations. The domain changes
when the framework changes.

### 12.7 The Import Chain

`a` imports `b` imports `c` imports `d` imports `a`. Circular
imports break tree-shaking and confuse type checkers.

### 12.8 The Barrel File

An `index.ts` re-exporting everything from a folder. It looks tidy
but breaks tree-shaking, creates circular-import opportunities, and
makes stack traces less informative.

### 12.9 The Global Singleton

A module-level mutable singleton that every caller mutates. Tests
that change it leak state to other tests. Concurrent requests race.

### 12.10 The Premature Microservice

Splitting a monolith into services before the monolith has a
measurable problem. The result is distributed transactions, network
failures, and twice the operational cost.

### 12.11 The Shared Types Folder Without Boundaries

`types/` containing every interface from every layer. The Domain
`User`, the API `UserDTO`, and the ORM `UserRecord` all live here.

### 12.12 The Refactor That Renames Everything

Renaming `Manager` to `Service` across 40 files in a single commit,
mixed with functional changes. The diff is unreviewable.

### 12.13 The Interface for Everything

An interface for a class that has one implementation and will never
have another. The interface adds a layer without a benefit.

### 12.14 The Base Class That Does Everything

A `BasePage` that provides routing, data fetching, error handling,
and rendering helpers. Subclasses use half of it.

### 12.15 The Type That Knows About the Database

A domain type with a `save()` method. The type now depends on the
persistence layer.

### 12.16 The Function That Takes a Config Object

```typescript
function process(data: unknown, options: {
  logLevel: string;
  retries: number;
  timeout: number;
  userAgent: string;
  ...
}) { /* uses one of the options */ }
```

Pass what the function uses.

### 12.17 The Wrapper Around a Wrapper

A `createUserService` that calls `userService.create` that calls
`userRepository.create` that calls `db.insert`. Each layer adds a
line and no value.

### 12.18 The Handler That Does Everything

An HTTP handler that validates input, queries the database, calls
external APIs, sends emails, and formats the response. One concern
per function.

### 12.19 The Module That Imports Everything

A `dashboard/` module that imports from `users/`, `orders/`,
`payments/`, `auth/`, and `notifications/`. The dashboard is a
composition; it should compose components, not reach into
internals.

### 12.20 The Feature Flag as Architecture

A feature flag that switches between two code paths with different
architectures. The flag becomes permanent.

### 12.21 The Deferred Refactor

A `// TODO: extract this` comment that lives for two years. If the
refactor is worth doing, do it now. If it is not, remove the TODO.

### 12.22 The Monorepo Without Boundaries

A monorepo where any package can import any other package. The
dependencies are implicit.

### 12.23 The Type-Safe Wrapper Without Types

A wrapper around a library that redeclares the library's API with
`any`.

### 12.24 The Unused Interface

An interface that exists because "we might swap the implementation".
No swap happened. The interface is dead weight.

### 12.25 The Naming Convention That Changes

`kebab-case` in old files, `camelCase` in new files, no migration.
Pick one, migrate the other.

## 13. Response to Violation

If a previous response violated a rule here:

```
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

No justification. No apology paragraph. Fix and move on.
