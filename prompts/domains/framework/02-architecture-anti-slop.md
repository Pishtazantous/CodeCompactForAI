---
id: 02-architecture-anti-slop
title: "Architecture Anti-Slop Layer (Framework-Agnostic)"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: framework
version: 1
---

# Architecture Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
security anti-patterns, output format) are NOT repeated here.

This file covers architectural principles that apply regardless of
framework, language, or delivery type: layering, dependency direction,
boundaries, folder structure, naming, and composition. Framework-
specific patterns (React hooks, Vue reactivity, Express middleware)
live in the sibling files in this folder.

## 1. Scope

This file is deliberately framework-agnostic. It applies to:

- Frontend applications (React, Vue, Svelte, Angular)
- Backend services (Express, NestJS, FastAPI, Django)
- Desktop and mobile applications
- CLI tools and libraries

Rules here describe how to organize a codebase, not how to use a
specific tool. If a rule conflicts with the project's existing
architecture, the project wins. Report the conflict instead of
silently diverging.

## 2. Reference the Existing Architecture First

Before writing any new file, folder, or module:

1. Fetch two or three files from the layer you are about to modify.
2. Fetch one file from a layer above (if it consumes yours).
3. Fetch one file from a layer below (if you consume it).
4. Identify the naming, import, and dependency pattern.
5. Follow that pattern exactly.

If the project has no discernible pattern, stop and ask before
inventing one. Introducing an architecture into a codebase that
already has one is the largest single source of structural slop.

## 3. Layering Principles

### 3.1 Identify the Layers

Most projects, regardless of framework, have some version of these
layers:

- **Entry** -- where the application starts. CLI `main`, HTTP router,
  React `App`, `index.js`.
- **Interface** -- how the outside world reaches the app. Routes,
  controllers, pages, commands, views.
- **Application** -- orchestration. Use cases, services, handlers.
- **Domain** -- business rules. Entities, value objects, pure functions.
- **Infrastructure** -- external systems. Database adapters, HTTP
  clients, message queues, file storage.

Not every project needs all five. Small projects collapse Interface
and Application. Libraries collapse everything except Domain and
Infrastructure.

The goal is not to have five layers. The goal is to have a clear
answer to: "what does this file belong to?"

### 3.2 One Concern Per Layer

A file in the Interface layer does not contain SQL. A file in the
Domain layer does not import a framework. A file in the Infrastructure
layer does not contain business rules.

When you cannot decide what layer a file belongs to, the file is
probably doing two things. Split it.

### 3.3 Reference the Project's Layer Names

The project may use different names:

- `app/`, `pages/`, `routes/` -- Interface
- `services/`, `use-cases/`, `handlers/` -- Application
- `domain/`, `entities/`, `models/` -- Domain
- `infra/`, `adapters/`, `providers/` -- Infrastructure
- `lib/`, `utils/`, `shared/` -- cross-cutting

Match the project. Do not rename a folder to match a textbook.

### 3.4 No Cross-Layer Cycles

If layer A depends on layer B, and layer B depends on layer A, the
layers are not layers. Either merge them or introduce a third module
both depend on.

Detect cycles by looking at imports. If a file imports from a folder
that imports from this file's folder, the architecture is broken.

## 4. Dependency Direction

### 4.1 Dependencies Point Inward

The canonical direction:
Entry -> Interface -> Application -> Domain
|
v
Infrastructure

text

Entry depends on everything. Domain depends on nothing (or only on
its own types). Infrastructure depends on Domain abstractions, not
the other way around.

### 4.2 Never Import Upward

A Domain file importing from Infrastructure is an architectural
violation. It couples business rules to a specific database or HTTP
client.

BAD: `domain/user.ts` imports `pg` (the PostgreSQL driver).
GOOD: `domain/user.ts` defines a `UserRepository` interface, and
`infra/postgres/user-repository.ts` implements it.

### 4.3 Framework at the Edges

Frameworks (Express, React, NestJS, FastAPI) belong in the outer
layers. A pure function in the Domain layer does not import
`express`, `react`, or `fastapi`.

If a Domain file imports a framework type, either:

- Move the framework code up, or
- Define a framework-independent interface in Domain and adapt in
  Infrastructure.

### 4.4 Cross-Cutting Concerns

Logging, authentication, validation, and telemetry are cross-cutting.
They belong in:

- Middleware (HTTP, gRPC), or
- Decorators, or
- Explicit calls from the Application layer.

Never sprinkled through the Domain layer. A `User.authenticate()`
method that logs is a Domain file doing Infrastructure work.

## 5. Boundaries

### 5.1 Explicit Module Boundaries

Each top-level module has a public API. Everything else is internal.

- TypeScript: `index.ts` or explicit `export` from the module root.
- Python: `__all__` or `__init__.py` with explicit exports.
- Go: package boundaries (one folder, one package).

Do not reach into another module's internal files. Import through the
public API.

### 5.2 No Deep Imports Into Another Module

BAD:
typescript
import { helper } from "@/features/billing/internal/helpers/format";
GOOD:

typescript
import { formatAmount } from "@/features/billing";
If the helper is needed outside billing, it belongs in a shared
module or in the public API of billing.

5.3 Shared Code Is Earned, Not Assumed
A "shared" or "common" or "utils" folder attracts everything. Before
moving code into shared:

Two or more modules use it.

The usage is stable (not a one-time reuse).

The code is genuinely generic (not domain-specific).

If any of these is false, keep the code in its current module.

6. Folder Structure Anti-Slop
6.1 No Premature Folder Creation
Create a folder when it holds at least three files. Empty folders,
folders with one file, and folders created "for the future" are
structure slop.

BAD: A new project with features/, modules/, domains/,
services/, shared/, core/, common/, utils/ all created on
day one.
GOOD: A new project with src/ and whatever folders the code
actually needs.

6.2 No Feature-vs-Layer Mixed Mess
Two valid organizations:

By layer: controllers/, services/, models/.

By feature: billing/, auth/, notifications/, each with
its own layers inside.

Mixing them produces controllers/billing/ and billing/controllers/
in the same codebase. Pick one and use it everywhere.

6.3 No Folder Named After a Design Pattern
BAD: factories/, strategies/, observers/, singletons/.
GOOD: payments/, auth/, email/. Name by domain, not by
pattern.

6.4 No Deeply Nested Folders
A path like src/components/forms/inputs/text/fields/validators/ is
a sign that the tree is built top-down instead of bottom-up. Flatten
until the nesting reflects real ownership.

Rule of thumb: three levels below src/ should cover most projects.
Beyond five levels, something is wrong with the structure.

6.5 Colocate by Default
Files that change together live together:

A component and its styles.

A test and the file it tests.

A service and the types it uses.

Do not scatter related files across distant folders "to keep folders
small". Small folders with scattered files are not an improvement.

7. Naming Anti-Slop
7.1 Names Describe Purpose, Not Type
BAD: userService.ts, paymentManager.ts, orderController.ts,
notificationHelper.ts.
GOOD: createUser.ts, payOrder.ts, sendNotification.ts,
userLookup.ts.

Service, Manager, Helper, Utility, Handler, Controller,
Processor, Wrapper, Factory are filler words. They do not
describe what the thing does.

7.2 Verbs for Functions, Nouns for Data
Functions: getUser, calculateTotal, validateEmail.

Types and interfaces: User, Order, EmailAddress.

Booleans: isActive, hasPermission, canEdit.

BAD: function user() { ... } returning a User.
BAD: const active = true; (active what?).
GOOD: const isActive = true;.

7.3 No Abbreviations Except Well-Established Ones
ctx, req, res, id, url, http -- fine.
usr, mgr, svc, cfg, btn, lbl -- not fine.

7.4 Consistent Casing
Match the project's convention:

camelCase files and identifiers in most JS/TS projects.

snake_case in Python and many Go projects.

PascalCase for React components and classes in many languages.

kebab-case for CSS classes and sometimes for file names.

Do not mix. createUser.ts and create_user.py in the same project
is fine. createUser.ts and create_user.ts in the same project is
not.

7.5 Singular vs Plural
Folders and files that hold a single entity are singular (user.ts).
Folders that hold many are plural (users/). Pick a convention and
apply it everywhere.

7.6 No Names That Contradict
BAD: users/ folder containing user-repository.ts,
all-users.ts, and create-user.ts. The folder says "many", the
files say "one".
GOOD: users/ containing repository.ts, list.ts, create.ts.
The folder names the domain; the files name the actions.

8. Composition vs Inheritance
8.1 Prefer Composition
Assemble behavior from small pieces. Inherit only when there is a
genuine "is-a" relationship and the base class is designed for
extension.

BAD: A BaseController that every controller extends to get shared
methods.
GOOD: A withAuth(handler) function that wraps any handler.

8.2 Depth of Inheritance Is a Cost
An inheritance chain of three or more levels is hard to reason about.
Flatten to composition.

8.3 No Mixins Without a Reason
Mixins couple the mixin and the mixed-in class in both directions.
Prefer a function that takes the class and returns a decorated one,
or a composition over mixins.

8.4 Interfaces for Behavior
When two types share a method set, express it as an interface (or a
protocol, or a trait). This allows composition without inheritance.

9. Abstraction Discipline
9.1 Rule of Three
An abstraction is justified when it has at least three real usages.
Two usages with slightly different shapes are usually not the same
abstraction.

9.2 No Abstraction for Anticipated Change
"Maybe later we will need to swap the database" is not a reason to
introduce a repository interface today. Wait for the second
implementation.

9.3 No Abstraction Over Trivial Code
A wrapper around localStorage.getItem is not an improvement. It
hides a two-line API behind a five-line module.

9.4 Abstraction Must Remove Code, Not Move It
A refactor that replaces 100 lines of direct code with 100 lines of
indirect code plus a new file is not an abstraction. It is
rearrangement. An abstraction reduces total cognitive cost, not line
count.

10. Configuration and Environment
10.1 Configuration Flows Down
The application entry point reads configuration and passes it down.
Domain and Application layers receive what they need as arguments,
not by reading globals.

BAD: domain/pricing.py reads os.environ["TAX_RATE"].
GOOD: domain/pricing.py takes tax_rate: float as an argument.
The entry point reads the env var and passes it.

10.2 No Hidden Configuration
A module that reads from a global config object is coupled to that
global. If the module is testable only when the global is set up, the
configuration is hidden.

11. Architecture Anti-Patterns
11.1 The Everything Module
A single utils.ts (or helpers.py, or common.go) that grows to
500 lines and is imported by half the codebase. It becomes a
dependency magnet and a merge-conflict generator.

Split it by purpose. Name each piece after what it does.

11.2 The God Object
A class or module that knows about every other part of the system.
Signs: it imports more than 10 modules, it has more than 20 public
methods, its test file is the largest in the repo.

Split by responsibility.

11.3 The Leaky Abstraction
A wrapper that exposes details of what it wraps. A Database class
with a getRawConnection() method that callers use to run SQL. The
abstraction provides no value.

Either remove the wrapper or hide the internals.

11.4 The Premature Framework
Introducing a dependency-injection framework, an event bus, and a
plugin system into a project that does not yet have users.

Frameworks are solutions to problems at scale. At small scale, they
are the problem.

11.5 The Two Architectures
Half the codebase uses services/ and the other half uses
use-cases/. Both do the same thing. New code follows whichever the
author read last.

Choose one, migrate the other, do not add a third.

11.6 The Framework in the Domain
A User class that extends an ORM's Model base class, or a
PaymentService decorated with framework-specific annotations.

This couples business rules to infrastructure. When the framework
changes, the domain changes. When the domain is tested, the framework
must be loaded.

11.7 The Import Chain
a imports b imports c imports d imports a. Circular imports
break tree-shaking, confuse type checkers, and indicate that a module
is doing too much or belongs somewhere else.

Extract the shared piece into a fourth module.

11.8 The Barrel File
index.ts re-exporting everything from a folder. It looks tidy but:

Breaks tree-shaking (the bundler cannot tell what is used).

Creates circular-import opportunities.

Makes stack traces less informative.

Import from the specific file.

11.9 The Global Singleton
A module-level mutable singleton that every caller mutates. Tests
that change it leak state to other tests. Concurrent requests race.

If a singleton is genuinely needed (a connection pool, a logger),
expose it through the framework's DI or through an explicit
initialization function called by the entry point. Never a bare
export const globalThing = ... that callers mutate.

11.10 The Premature Microservice
Splitting a monolith into services before the monolith has a
measurable problem. The result is distributed transactions, network
failures, and twice the operational cost.

Extract a service when a specific team, scaling need, or deployment
cadence requires it.

11.11 The Shared Types Folder Without Boundaries
types/ containing every interface from every layer. The Domain
User and the API UserDTO and the ORM UserRecord all live here,
and nobody knows which to import.

Separate types by layer and colocate them with the code that owns
them.

11.12 The Refactor That Renames Everything
Renaming Manager to Service across 40 files in a single commit,
mixed with functional changes. The diff is unreviewable, and if
something breaks, git bisect is useless.

Renames and behavior changes go in separate commits.

12. Response to Violation
If a previous response violated a rule here:

text
In the previous response, [specific rule] was violated. Correction:
[corrected code]
No justification. No apology paragraph. Fix and move on.


---