---
id: 02-architecture-anti-slop
title: "Architecture Anti-Slop Layer"
lang: en
depends_on: ["_universal/00-style-guide.md", "_universal/00-master-anti-slop.md"]
category: domain
domain_type: framework
version: 3
---

# Architecture Anti-Slop Layer

This file defines architectural principles that apply regardless of framework, language, or delivery type. It sits in the framework layer as the base architectural contract that every framework-specific file builds on. It covers layering, dependency direction, boundaries, folder structure, naming, composition, and abstraction discipline. It does not cover framework-specific patterns (see sibling framework files), language rules (see language files), delivery rules (see delivery files), or visual design (see UI files).

Architecture is the set of decisions that are expensive to reverse. Every rule below is a decision that is cheaper to make correctly the first time than to fix later.

## Scope

This file is deliberately framework-agnostic. It applies to frontend applications (React, Vue, Svelte, Angular, Solid), backend services (Express, NestJS, FastAPI, Django, Rails), desktop and mobile applications, CLI tools, and libraries. The rules describe how to organize a codebase, not how to use a specific tool. The examples use TypeScript syntax where illustrative, but the principles apply to any language.

When a rule conflicts with the project's existing architecture, the project wins. The conflict MUST be reported instead of silently diverging.

## Rule Severity

Severity follows `_universal/00-style-guide.md`.

## Contracts

A codebase commits to five architectural contracts. The table below maps each contract to the rules that enforce it.

| Contract | Description | Enforced By |
|---|---|---|
| Layers Are Real | Every file belongs to a layer that determines its import boundaries. | ARCH-004 to ARCH-007 |
| Dependencies Point Inward | Inner layers do not depend on outer layers. | ARCH-008 to ARCH-012 |
| Boundaries Are Explicit | Each module has a public API; reaching into internals is forbidden. | ARCH-013 to ARCH-017 |
| Names Describe Purpose | Names are the first layer of documentation and never go stale. | ARCH-024 to ARCH-029 |
| Abstraction Removes Code | Abstractions reduce cognitive cost, not line count. | ARCH-035 to ARCH-040 |

## Reference the Existing Architecture

### ARCH-001 — Read Before Writing

**MUST**

Before writing any new file, folder, or module, the assistant MUST:

1. Fetch two or three files from the layer to be modified.
2. Fetch one file from a layer above (if it consumes yours).
3. Fetch one file from a layer below (if you consume it).
4. Identify the naming, import, and dependency pattern.
5. Follow that pattern exactly.

Introducing a second architecture into a codebase that already has one is the largest single source of structural slop.

### ARCH-002 — No Architecture Without a Reason

**MUST NOT**

If the project has no discernible pattern, the assistant MUST NOT invent one without explicit approval. Structure emerges from real needs, not from a desire for order.

### ARCH-003 — Consistency Over Preference

**MUST**

If the project uses a pattern the assistant would not choose, the assistant MUST follow it anyway. The cost of inconsistency is higher than the cost of an imperfect pattern.

## Layering Principles

### ARCH-004 — Layer Identification

**SHOULD**

Most projects SHOULD identify their layers explicitly:

- **Entry**: where the application starts (CLI `main`, HTTP router, React `App`).
- **Interface**: how the outside world reaches the app (routes, controllers, pages).
- **Application**: orchestration (use cases, services, handlers).
- **Domain**: business rules (entities, value objects, pure functions).
- **Infrastructure**: external systems (DB adapters, HTTP clients, queues).

Not every project needs all five. The goal is a clear answer to "what does this file belong to?", not a quota.

### ARCH-005 — One Concern Per Layer

**MUST**

A file in the Interface layer MUST NOT contain SQL. A file in the Domain layer MUST NOT import a framework. A file in the Infrastructure layer MUST NOT contain business rules.

Example (illustrative, TypeScript):

BAD:
```typescript
// domain/user.ts
import { db } from "../infra/database";
export function isActiveUser(id: string) {
  const row = db.query("SELECT active FROM users WHERE id = ?", [id]);
  return row.active === 1;
}
```

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

### ARCH-006 — Project Layer Name Adherence

**MUST**

The project's existing layer names MUST be matched. Common alternatives (`app/`, `pages/`, `services/`, `use-cases/`, `domain/`, `entities/`, `infra/`, `adapters/`, `lib/`, `shared/`) MUST be preserved. Renaming a folder to match a textbook is prohibited.

### ARCH-007 — No Cross-Layer Cycles

**MUST NOT**

If layer A depends on layer B and layer B depends on layer A, they MUST either be merged or a third module both depend on MUST be introduced. Cycles make the codebase unanalyzable.

## Dependency Direction

### ARCH-008 — Inward Dependency Direction

**MUST**

Dependencies MUST point inward:

```
Entry → Interface → Application → Domain
                           ↓
                     Infrastructure
```

Entry depends on everything. Domain depends on nothing (or only on its own types). Infrastructure depends on Domain abstractions, not the other way around.

### ARCH-009 — No Upward Imports

**MUST NOT**

A Domain file MUST NOT import from Infrastructure. Upward imports couple business rules to a specific database or HTTP client.

Example (illustrative, TypeScript):

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

### ARCH-010 — Framework at the Edges

**MUST**

Frameworks (Express, React, NestJS, FastAPI) MUST belong in the outer layers. A pure function in the Domain layer MUST NOT import `express`, `react`, or `fastapi`.

### ARCH-011 — Cross-Cutting Concern Placement

**MUST**

Logging, authentication, validation, and telemetry MUST be placed in middleware, decorators, or explicit calls from the Application layer. They MUST NOT be placed in the Domain layer. A `User.authenticate()` method that logs is a Domain file doing Infrastructure work.

### ARCH-012 — Dependency Inversion for Domain

**MUST**

When the Domain needs something from Infrastructure, the Domain MUST declare an interface, Infrastructure MUST implement it, and wiring MUST happen at composition time (the entry point). The Domain layer defines the language of the problem; Infrastructure adapts to it.

## Boundaries

### ARCH-013 — Explicit Module Boundaries

**MUST**

Each top-level module MUST have a public API. Everything else is internal. Language-specific boundary mechanisms MUST be used: `index.ts` for TypeScript, `__all__` or `__init__.py` for Python, package boundaries for Go, and `pub` items in the module's root for Rust.

### ARCH-014 — No Deep Imports

**MUST NOT**

Deep imports into a module's internal structure MUST NOT be used.

Example (illustrative, TypeScript):

BAD: `import { formatAmount } from "@/features/billing/internal/helpers/format";`
GOOD: `import { formatAmount } from "@/features/billing";`

A deep import couples the consumer to the internal structure of the module. Refactoring the module breaks the consumer.

### ARCH-015 — Shared Code Discipline

**MUST**

Code MUST NOT be moved into a `shared/` or `common/` folder until: (1) two or more modules use it, (2) the usage is stable, not a one-time reuse, and (3) the code is genuinely generic, not domain-specific. A shared module with one consumer is a coupling that makes the codebase harder to change.

### ARCH-016 — No Bidirectional Module Dependencies

**MUST NOT**

Two modules that depend on each other are not modules; they are one module split by accident. They MUST be merged or the shared piece extracted.

### ARCH-017 — Explicit Public API

**MUST**

A module's entry file (e.g., `index.ts`) MUST export only what consumers need. A module with no documented public API has no boundary. Re-exporting everything from every internal file is prohibited.

## Folder Structure

### ARCH-018 — No Premature Folder Creation

**MUST NOT**

A folder MUST NOT be created until it holds at least three files. Empty folders are structure slop that signal an architecture that has not been earned. A new project with `features/`, `modules/`, `domains/`, `services/`, `shared/`, `core/`, `common/`, `utils/` all created on day one is prohibited.

### ARCH-019 — Feature or Layer Organization

**MUST**

Organization MUST follow one consistent pattern: either by layer (`controllers/`, `services/`, `models/`) or by feature (`billing/`, `auth/`, each with its own layers inside). Mixing them produces `controllers/billing/` and `billing/controllers/` in the same codebase and MUST NOT be done.

### ARCH-020 — No Pattern-Named Folders

**MUST NOT**

Folders MUST NOT be named after design patterns (e.g., `factories/`, `strategies/`, `observers/`, `singletons/`). Folders MUST be named by domain (e.g., `payments/`, `auth/`, `email/`). A folder named after a pattern ages poorly.

### ARCH-021 — Shallow Directory Trees

**SHOULD**

Directory trees SHOULD be shallow. Three levels below `src/` SHOULD cover most projects. Beyond five levels, the structure is usually wrong and SHOULD be flattened.

### ARCH-022 — Colocation by Default

**SHOULD**

Files that change together SHOULD live together: a component and its styles, a test and the file it tests, a service and the types it uses. Scattering related files across distant folders keeps changes scattered.

### ARCH-023 — No Unbounded Utils Folder

**MUST NOT**

A single `utils.ts` that grows to 500 lines MUST NOT exist. Utilities MUST be placed in the module where they are used, or split by purpose (`format/`, `validation/`). An unbounded `utils/` folder becomes a dependency magnet.

## Naming

### ARCH-024 — Purpose-Based Naming

**MUST**

Names MUST describe purpose, not type. Filler words like `Service`, `Manager`, `Helper`, `Utility`, `Handler`, `Controller`, `Processor`, `Wrapper`, `Factory` MUST NOT be used.

Example (illustrative):

BAD: `userService.ts`, `paymentManager.ts`, `orderController.ts`.
GOOD: `createUser.ts`, `payOrder.ts`, `userLookup.ts`.

### ARCH-025 — Part-of-Speech Naming Discipline

**MUST**

Functions MUST use verbs (`getUser`, `calculateTotal`), types and interfaces MUST use nouns (`User`, `Order`), and booleans MUST use predicates (`isActive`, `hasPermission`, `canEdit`).

### ARCH-026 — Abbreviation Discipline

**MUST NOT**

Non-established abbreviations (`usr`, `mgr`, `svc`, `cfg`, `btn`, `lbl`) MUST NOT be used. Established abbreviations (`ctx`, `req`, `res`, `id`, `url`, `http`) are acceptable.

### ARCH-027 — Consistent Casing

**MUST**

The project's casing convention MUST be matched consistently. Mixing conventions within the same layer or language is prohibited.

### ARCH-028 — Collection/Item Naming

**MUST**

Folders that hold many items MUST use plural names (`users/`), and files that define one MUST use singular names (`user.ts`). The convention MUST be applied everywhere.

### ARCH-029 — Layer-Consistent Naming

**MUST**

A file's name MUST agree with its layer. A file in `services/` named `UserRepository` is a category error and MUST NOT exist.

## Composition Over Inheritance

### ARCH-030 — Composition Preference

**SHOULD**

Behavior SHOULD be assembled from small pieces. Inheritance SHOULD only be used when there is a genuine "is-a" relationship and the base class is designed for extension.

### ARCH-031 — Inheritance Depth Limit

**MUST NOT**

An inheritance chain of three or more levels MUST NOT be used. It MUST be flattened to composition.

### ARCH-032 — No Mixins Without Reason

**MUST NOT**

Mixins MUST NOT be used without a documented reason. They couple the mixin and the mixed-in class in both directions. A function that takes a class and returns a decorated one is preferred.

### ARCH-033 — Interfaces for Behavior

**SHOULD**

When two types share a method set, an interface, protocol, or trait SHOULD be used to express the contract. This allows composition without inheritance.

### ARCH-034 — No Convenience Base Classes

**MUST NOT**

A base class that exists only to provide helper methods MUST NOT be used. Those helpers MUST be placed in a utility function or a composed module.

## Abstraction Discipline

### ARCH-035 — Rule of Three

**MUST**

An abstraction MUST be justified by at least three real usages. Two usages with slightly different shapes are usually not the same abstraction; the code MUST be inlined until a third usage appears.

### ARCH-036 — No Anticipatory Abstraction

**MUST NOT**

"Maybe later we will need to swap the database" is not a reason to introduce a repository interface today. Abstraction for anticipated change MUST NOT be introduced. The second implementation MUST be waited for.

### ARCH-037 — No Trivial Abstraction

**MUST NOT**

A wrapper around a trivial API (e.g., `localStorage.getItem`) MUST NOT be used. It hides a two-line API behind a five-line module without reducing cognitive cost.

### ARCH-038 — Abstraction Must Reduce Cost

**MUST**

An abstraction MUST reduce total cognitive cost, not line count. A refactor that replaces 100 lines of direct code with 100 lines of indirect code plus a new file is rearrangement, not abstraction.

### ARCH-039 — No Single-Implementation Interfaces

**MUST NOT**

An interface with one implementation and no mock (e.g., `IUserRepository`) MUST NOT exist unless a test mock actually needs it. The interface adds a layer without a benefit.

### ARCH-040 — Function Composition Over Deep Hierarchies

**SHOULD**

A function that composes three small functions SHOULD be preferred over a class with a five-level hierarchy. Composition is easier to test and reason about.

## Configuration Flow

### ARCH-041 — Downward Configuration Flow

**MUST**

Configuration MUST flow down. The application entry point reads configuration and passes it down. Domain and Application layers MUST receive what they need as arguments, not by reading globals.

Example (illustrative, TypeScript):

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
```

### ARCH-042 — No Hidden Configuration

**MUST NOT**

A module MUST NOT read from a global config object. If the module is testable only when the global is set up, the configuration is hidden and MUST be made explicit.

### ARCH-043 — Startup Configuration Validation

**MUST**

Every required configuration value MUST be validated at boot. A missing value MUST fail immediately, not at the first request that needs it.

### ARCH-044 — No Environment Values in Code

**MUST NOT**

URLs, keys, feature flags, and connection strings MUST NOT be in source code. They MUST come from configuration.

See MAS-009 in `_universal/00-master-anti-slop.md`.

## Architecture Documentation

### ARCH-045 — Architecture Documentation

**MUST**

The project MUST have an architecture document (`docs/architecture.md` or README section) that describes the layers, the dependency direction, and the boundaries. New contributors MUST read it before writing code.

### ARCH-046 — Short Documentation

**SHOULD**

The architecture document SHOULD be a one-page summary with links to examples. A 500-line architecture document is not read.

### ARCH-047 — Diagram Discipline

**SHOULD**

An ASCII or Mermaid diagram of the layers and their dependencies SHOULD be included. Screenshots of whiteboards SHOULD NOT be used.

### ARCH-048 — Co-Update Documentation

**MUST**

When the architecture changes, the document MUST be updated in the same commit. A stale architecture document is worse than none.

## AI-Specific Architecture Discipline

### ARCH-060 — Existing Architecture Discovery

**MUST**

Before proposing a new folder, module, or architectural pattern, the assistant MUST search the project for existing equivalents. Inventing parallel structures creates the "Two Architectures" anti-pattern and fragments the codebase.

See MAS-035 in `_universal/00-master-anti-slop.md`.

### ARCH-061 — Project Convention Verification

**MUST**

Before creating a new module or file, the assistant MUST verify the project's naming, casing, and folder conventions by reading existing files. Inventing new conventions violates ARCH-003 (Consistency Over Preference).

See MAS-036 in `_universal/00-master-anti-slop.md`.

### ARCH-062 — Complexity Restraint

**SHOULD**

The assistant SHOULD NOT introduce architectural complexity (DI frameworks, event buses, plugin systems, microservices) unless the project already uses them and the scale explicitly requires them.

See MAS-038 in `_universal/00-master-anti-slop.md`.

## Anti-Patterns

### ARCH-049 — Everything Module

**MUST NOT**

A single `utils.ts` (or `helpers.py`, or `common.go`) that grows to 500 lines and is imported by half the codebase MUST NOT exist. It becomes a dependency magnet and a merge-conflict generator.

### ARCH-050 — God Object

**MUST NOT**

A class or module that imports more than 10 modules, has more than 20 public methods, or has the largest test file in the repo MUST NOT exist. It MUST be split by responsibility.

### ARCH-051 — Leaky Abstraction

**MUST NOT**

A wrapper that exposes details of what it wraps (e.g., a `Database` class with a `getRawConnection()` method) MUST NOT exist. The wrapper MUST hide the underlying implementation.

### ARCH-052 — Premature Framework

**MUST NOT**

Introducing a dependency-injection framework, an event bus, and a plugin system into a project with no users MUST NOT occur. Frameworks are solutions to problems at scale; at small scale, they are the problem.

### ARCH-053 — Two Architectures

**MUST NOT**

Half the codebase using `services/` and the other half using `use-cases/` for the same purpose MUST NOT exist. One pattern MUST be chosen and applied everywhere.

### ARCH-054 — Framework in the Domain

**MUST NOT**

A domain class that extends an ORM's `Model` or a service decorated with framework-specific annotations MUST NOT exist. The domain changes when the framework changes.

### ARCH-055 — Circular Imports

**MUST NOT**

Import chains like `a` → `b` → `c` → `a` MUST NOT exist. They break tree-shaking and confuse type checkers.

### ARCH-056 — Barrel Files

**MUST NOT**

An `index.ts` re-exporting everything from a folder MUST NOT exist. It breaks tree-shaking, creates circular-import opportunities, and makes stack traces less informative.

### ARCH-057 — Global Singleton

**MUST NOT**

A module-level mutable singleton that every caller mutates MUST NOT exist. Tests that change it leak state to other tests, and concurrent requests race.

### ARCH-058 — Premature Microservice

**MUST NOT**

Splitting a monolith into services before the monolith has a measurable problem MUST NOT occur. The result is distributed transactions, network failures, and twice the operational cost.

### ARCH-059 — Shared Types Without Boundaries

**MUST NOT**

A `types/` folder containing every interface from every layer (the Domain `User`, the API `UserDTO`, and the ORM `UserRecord` all living together) MUST NOT exist. Types MUST be scoped to their layer.

### ARCH-070 — Massive Rename Refactor

**MUST NOT**

Renaming `Manager` to `Service` across 40 files in a single commit mixed with functional changes MUST NOT occur. The diff is unreviewable. Refactors MUST be separated from functional changes.

### ARCH-071 — Domain Type With Persistence

**MUST NOT**

A domain type with a `save()` method MUST NOT exist. The type then depends on the persistence layer, violating ARCH-009.

### ARCH-072 — Mega Options Object

**MUST NOT**

A function that takes a massive `options` object with dozens of fields when it only uses one MUST NOT exist. The function MUST accept only what it uses.

### ARCH-073 — Wrapper Around a Wrapper

**MUST NOT**

A `createUserService` that calls `userService.create` that calls `userRepository.create` that calls `db.insert` MUST NOT exist. Each layer MUST add value, not just indirection.

### ARCH-074 — Handler That Does Everything

**MUST NOT**

An HTTP handler that validates input, queries the database, calls external APIs, sends emails, and formats the response MUST NOT exist. One concern MUST be assigned per function.

### ARCH-075 — Module That Imports Everything

**MUST NOT**

A `dashboard/` module that imports from `users/`, `orders/`, `payments/`, `auth/`, and `notifications/` MUST NOT exist. The dashboard is a composition; it MUST compose components, not reach into internals.

### ARCH-076 — Feature Flag as Architecture

**MUST NOT**

A feature flag that switches between two code paths with different architectures MUST NOT exist. The flag becomes permanent and the architecture becomes bifurcated.

### ARCH-077 — Deferred Refactor

**MUST NOT**

A `// TODO: extract this` comment that lives for years MUST NOT exist. If the refactor is worth doing, it MUST be done now. If it is not, the TODO MUST be removed.

### ARCH-078 — Monorepo Without Boundaries

**MUST NOT**

A monorepo where any package can import any other package MUST NOT exist. Dependencies MUST be explicit and bounded.

### ARCH-079 — Type-Safe Wrapper Without Types

**MUST NOT**

A wrapper around a library that redeclares the library's API with `any` MUST NOT exist. The wrapper defeats its own purpose.

### ARCH-080 — Inconsistent Naming Convention

**MUST NOT**

`kebab-case` in old files and `camelCase` in new files with no migration MUST NOT exist. One convention MUST be picked and the other migrated.

## Response to Violation

When a rule in this file is violated, report:

Violation: ARCH-{NNN}
Reason: {one-line reason}
Correction: {smallest fix}

For multiple violations, report each rule ID separately.

Do not replace a technical correction with a generic explanation.