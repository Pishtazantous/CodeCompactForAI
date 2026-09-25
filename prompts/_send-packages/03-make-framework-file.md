---
id: 03-make-framework-file
title: "How to Generate a Framework File"
lang: en
category: helper
version: 2
---

# How to Generate a Framework File

Framework files capture rules specific to a framework: component
discipline, state, lifecycle, routing, data flow, and
framework-specific anti-patterns.

A framework file is NOT a general architecture guide. Architecture
rules (layering, dependency direction, folder structure, naming)
live in `02-architecture-anti-slop.md`. The framework file assumes
architecture and adds what is specific to the framework itself.

A framework file is NOT a language guide. Language rules (type
system, error handling, memory) live in the language files. The
framework file assumes the language and adds what is specific to
the framework.

A framework file is the file where the AI learns how to use this
framework idiomatically and which traps to avoid.

## When to Use This Guide

Use this guide when generating or regenerating a file under
`prompts/domains/framework/`.

Use it when:

- A new framework is added to the system.
- An existing framework file is too shallow and needs a rewrite.
- A framework version changes with breaking patterns worth
  documenting.

Do NOT use it when:

- Generating a language file (see `02-make-language-file.md`).
- Generating a delivery file (see `01-make-delivery-file.md`).
- Generating a concern file (see `04-make-concern-file.md`).
- Generating the architecture file itself (it is framework-
  agnostic and does not follow this guide).

## Files to Attach

### Required

- `_universal/00-master-anti-slop.md`
- `domains/framework/02-architecture-anti-slop.md`

Both are mandatory. Universal prevents repetition of common rules.
Architecture prevents repetition of layering, folder structure,
naming, and dependency rules.

### Required (1-2 examples from the same category)

Attach at least one, ideally two, existing framework files. See the
table below for framework-specific recommendations.

### Required (framework-related delivery)

For frontend frameworks, also attach:

- `domains/delivery/02-frontend-anti-slop.md`

For backend frameworks, also attach:

- `domains/delivery/02-backend-anti-slop.md`

For mobile frameworks, also attach:

- `domains/delivery/02-mobile-anti-slop.md`

For desktop frameworks, also attach:

- `domains/delivery/02-desktop-anti-slop.md`

Without the delivery file, the framework file will duplicate
component discipline, data fetching, and routing rules that belong
to the delivery layer.

### Optional

- A concern file if the framework has a natural concern (for
  example `02-accessibility-critical-anti-slop.md` for a UI
  framework).

## Reference Attachments by Framework

The following table tells you which existing framework files to
attach as references for each target. Attach two whenever possible.

| Target framework | Primary reference | Secondary reference |
|---|---|---|
| React | 02-react-anti-slop.md | 02-vue-anti-slop.md |
| Vue | 02-vue-anti-slop.md | 02-react-anti-slop.md |
| Svelte | 02-svelte-anti-slop.md | 02-vue-anti-slop.md |
| Solid | 02-solid-anti-slop.md | 02-react-anti-slop.md |
| Angular | 02-angular-anti-slop.md | 02-vue-anti-slop.md |
| Next.js | 02-nextjs-anti-slop.md | 02-remix-anti-slop.md |
| Nuxt | 02-nuxt-anti-slop.md | 02-nextjs-anti-slop.md |
| SvelteKit | 02-sveltekit-anti-slop.md | 02-svelte-anti-slop.md |
| Remix | 02-remix-anti-slop.md | 02-nextjs-anti-slop.md |
| Astro | 02-astro-anti-slop.md | 02-nextjs-anti-slop.md |
| Express | 02-express-anti-slop.md | 02-fastify-anti-slop.md |
| NestJS | 02-nestjs-anti-slop.md | 02-spring-anti-slop.md |
| Fastify | 02-fastify-anti-slop.md | 02-express-anti-slop.md |
| Django | 02-django-anti-slop.md | 02-rails-anti-slop.md |
| FastAPI | 02-fastapi-anti-slop.md | 02-flask-anti-slop.md |
| Flask | 02-flask-anti-slop.md | 02-fastapi-anti-slop.md |
| Rails | 02-rails-anti-slop.md | 02-django-anti-slop.md |
| Laravel | 02-laravel-anti-slop.md | 02-rails-anti-slop.md |
| Spring | 02-spring-anti-slop.md | 02-nestjs-anti-slop.md |
| ASP.NET Core | 02-dotnet-anti-slop.md | 02-spring-anti-slop.md |
| Gin | 02-gin-anti-slop.md | 02-fiber-anti-slop.md |
| Fiber | 02-fiber-anti-slop.md | 02-gin-anti-slop.md |
| Axum | 02-axum-anti-slop.md | 02-actix-anti-slop.md |
| Actix | 02-actix-anti-slop.md | 02-axum-anti-slop.md |
| Phoenix | 02-phoenix-anti-slop.md | 02-rails-anti-slop.md |
| React Native | 02-react-native-anti-slop.md | 02-react-anti-slop.md |
| Flutter | 02-flutter-anti-slop.md | 02-react-native-anti-slop.md |
| Electron | 02-electron-anti-slop.md | 02-tauri-anti-slop.md |
| Tauri | 02-tauri-anti-slop.md | 02-electron-anti-slop.md |

If the target framework is not listed, pick the two references
whose paradigm is closest. A component framework references another
component framework. A meta-framework references another
meta-framework. A backend framework references another backend
framework of the same shape.

## Additional Prompt Requirements

When filling in the master prompt for a framework file, insert the
following block under the `Mandatory Rules` section. This block
overrides the defaults for the framework category.

```
### Framework-Specific Requirements

Framework files must satisfy the following in addition to the
general rules:

1. Framework Lifecycle Contracts.

   The file MUST include a section that describes the framework's
   lifecycle contracts. These are the rules the framework enforces
   on the developer:

   - When code runs (mount, render, unmount, request lifecycle,
     init, shutdown).
   - What triggers re-execution (state change, props change,
     navigation, dependency change).
   - What is guaranteed vs what is not (order of execution, whether
     effects are skipped, whether components remount).
   - What the framework does automatically vs what the developer
     must do manually (cleanup, dependency tracking, state
     persistence).

   For a component framework, this is the component lifecycle. For
   a meta-framework, this is the request/render/hydration lifecycle
   plus any server-side lifecycle. For a backend framework, this is
   the request lifecycle and middleware order.

   Without this section, the AI applies rules from other frameworks
   that do not fit this framework's model.

2. Framework Boundaries.

   The opening paragraph MUST state clearly what this file does
   NOT cover, with references to sibling files. For example:

       This file does NOT cover:
       - Architecture rules (see 02-architecture-anti-slop.md).
       - Frontend delivery rules (see 02-frontend-anti-slop.md).
       - TypeScript rules (see 02-typescript-anti-slop.md).
       - UI design system rules (see 04-ui-design-system.md).

   Without boundaries, the file duplicates architecture, delivery,
   language, and UI rules.

3. Framework-Specific, Not General.

   Every rule MUST be specific to this framework. If a rule applies
   to any framework, it belongs in `02-architecture-anti-slop.md`
   or in the relevant delivery file.

   Test: change the framework name in the rule. If the rule still
   makes sense, it is not framework-specific.

   BAD (applies to any frontend framework):
       ### 4.2 Do Not Fetch in the Component Body

       Fetching data in the component body causes re-fetch on every
       render.

   GOOD (specific to React):
       ### 4.2 Do Not Fetch in the Component Body

       In React, code in the component body runs on every render.
       A fetch call there fires on every render, not once. Use
       `useEffect` with a dependency array, or a data-fetching
       library that deduplicates.

4. Rationale for Every Rule.

   Every rule MUST include a one-line rationale, even when the rule
   seems obvious.

   BAD:
       ### 3.1 No `useEffect` for Derived State

       Do not use `useEffect` to compute derived state.

   GOOD:
       ### 3.1 No `useEffect` for Derived State

       `useEffect` runs after render, so the component renders once
       with stale state, then re-renders with the new value. This
       causes a flash and an unnecessary render cycle. Compute
       derived values during render.

5. At Least 22 Anti-Patterns.

   The `Anti-Patterns` section MUST have at least 22 items, not 22
   rules total. Rules live in the earlier sections; the anti-pattern
   section is a list of concrete mistakes.

   Each anti-pattern has:
   - A short title.
   - A one-line explanation.
   - A BAD/GOOD code pair, unless the anti-pattern is purely
     structural (in which case a textual BAD/GOOD is acceptable).

   The count is 22 (higher than 20 for language, lower than 25 for
   delivery). Frameworks have more specific anti-patterns than
   languages but fewer than delivery types.

6. At Least 18 Rules with BAD/GOOD.

   Not 50% of rules. At least 18 concrete code examples in the
   entire file. This number is a floor, not a target.

   Framework rules are highly concrete: a hook that runs at the
   wrong time, a directive that does not do what the developer
   thinks. Examples are the primary way to convey these rules.

7. No Language Bleed.

   Do not include language-specific rules. Type system rules belong
   in the language files. Error handling syntax belongs in the
   language files.

   A framework file may mention a language feature when it is
   required by the framework (for example a TypeScript generic in a
   framework API), but the rule itself is framework-level.

8. No Delivery Bleed.

   Do not include rules that apply to any project of this delivery
   type. Component discipline for frontend, response shape for
   backend, and request lifecycle for a service belong in the
   delivery file.

   A framework file extends the delivery file with framework-
   specific implementations of those rules.
```

## Filling in the Master Prompt

Use this template for the metadata portion of the master prompt:

```
Path: prompts/domains/framework/02-<name>-anti-slop.md
id: 02-<name>-anti-slop
title: <Framework> Anti-Slop Layer
domain_type: framework
depends_on: [00-master-anti-slop, 02-architecture-anti-slop,
             <delivery file>, <language file if applicable>]

Coverage:
Rules specific to <framework>: <list 5-7 topics from the
Suggested Topics section below>.

NOT covered:
Architecture rules, delivery rules, language rules, UI design
system rules.
```

Then insert the `Additional Prompt Requirements` block above under
the `Mandatory Rules` section of the master prompt.

## Suggested Topics by Framework Paradigm

Use these as a starting set of sections. Adjust for the specific
framework.

### Frontend Component Frameworks

React, Vue, Svelte, Solid, Angular, Preact, Lit.

- Component discipline (composition, props, boundaries)
- Reactivity model (hooks, signals, runes)
- State ownership and lifting
- Rendering and lifecycle
- Side effects and cleanup
- Context, provide/inject, or DI
- Lists, keys, and reconciliation
- Framework-specific anti-patterns

### Meta-Frameworks

Next.js, Nuxt, SvelteKit, Remix, Astro.

- All of frontend component frameworks, plus:
- Server vs client boundaries
- Data fetching conventions
- Routing and layouts
- Caching and revalidation
- Server functions (actions, loaders, endpoints)
- Hydration discipline
- Framework-specific anti-patterns

### Backend Frameworks

Express, NestJS, Fastify, Django, FastAPI, Flask, Rails, Laravel,
Spring, ASP.NET Core, Gin, Fiber, Axum, Actix, Phoenix.

- Project structure
- Routing and controllers
- Middleware and pipelines
- Dependency injection (if the framework has one)
- Validation and serialization
- Error handling
- Configuration
- Framework-specific anti-patterns

### Mobile Frameworks

React Native, Flutter.

- Lifecycle and platform differences
- Navigation
- Native bridge usage
- Platform-specific code separation
- Performance on mobile
- Framework-specific anti-patterns

### Desktop Frameworks

Electron, Tauri.

- Process architecture
- IPC discipline
- Security model
- Native integration
- Auto-update
- Framework-specific anti-patterns

## Suggested Topics by Specific Framework

When the target framework is on this list, use the suggested topics
as the starting set.

### React

- Component discipline (one per file, size)
- Rules of hooks
- Dependency arrays
- Derived state (no `useState` for derived values)
- `useMemo` and `useCallback` only after measurement
- Context discipline
- List keys
- Rendering anti-patterns (inline components, conditional hooks)

### Vue

- `<script setup>` discipline
- `ref` vs `reactive`
- Computed over watchers
- `defineProps`, `defineEmits`, `defineModel`
- Reactivity loss on destructuring
- `provide`/`inject` vs stores
- Template anti-patterns (`v-if` with `v-for`)

### Svelte 5

- Runes (`$state`, `$derived`, `$effect`, `$props`)
- `$effect` discipline
- Snippets vs slots
- Store vs rune boundaries
- Component composition
- SvelteKit boundary separation

### Angular

- Standalone components
- Signals vs RxJS
- `OnPush` change detection
- DI with `inject()`
- Reactive forms vs template-driven
- RxJS operators (`switchMap`, `mergeMap`, `concatMap`)
- Unsubscribe discipline

### Next.js

- Server Components vs Client Components
- `"use client"` placement
- Data fetching in Server Components
- Route Handlers vs Server Actions
- Caching layers
- Metadata
- Hydration mismatch

### Nuxt

- Auto-imports discipline
- `useFetch` vs `useAsyncData`
- Server routes
- `runtimeConfig` public vs private
- Hydration mismatch
- Nuxt modules

### Express

- Route and middleware order
- Error middleware arity
- Async error handling
- Router modularity
- Response sending discipline
- Security middleware

### NestJS

- Modules and providers
- Constructor injection
- DTOs and validation pipes
- Guards, interceptors, pipes, filters
- Circular dependency avoidance
- Configuration via `ConfigService`

### Django

- Models and ORM discipline
- Views and templates
- URL routing
- Migrations
- Signals (sparingly)
- Settings and environment

### FastAPI

- Pydantic models
- Dependency injection
- Async discipline
- Response models
- Background tasks
- OpenAPI metadata

### Rails

- Convention over configuration
- ActiveRecord discipline
- Controllers and routes
- Migrations
- Callbacks (sparingly)
- Concerns and services

### Spring Boot

- Bean scopes and lifecycle
- Dependency injection
- Annotations discipline
- JPA and Hibernate
- Configuration and profiles
- Testing slices

### ASP.NET Core

- DI container and lifetimes
- Middleware pipeline order
- Minimal APIs vs controllers
- EF Core discipline
- Configuration and options
- Async discipline

### React Native

- Component and hook discipline (React rules apply)
- Navigation
- Platform-specific code
- Native modules
- Performance on mobile
- List optimization (`FlatList`)

### Flutter

- Widget discipline
- State management
- Platform channels
- Build and deployment
- Performance on mobile

### Electron

- Main / renderer split
- IPC with `contextBridge`
- Security model
- Auto-update
- Native menus

### Tauri

- Commands and permissions
- Rust backend, web frontend
- IPC model
- Security model
- Auto-update

## Verification

After receiving the file from the AI, verify:

1. Every item in the master prompt's self-audit checklist.
2. Every item in the `Framework-Specific Self-Audit` below.
3. The file is between 250 and 400 lines.
4. The file does not repeat rules from the attached sibling files.

If any item fails, request a revision from the AI rather than
saving a weak file.

## Framework-Specific Self-Audit

Before saving the generated file, verify every item:

Lifecycle Contracts:
- [ ] A section describes when code runs (mount, render,
      request lifecycle)
- [ ] The section describes what triggers re-execution
- [ ] The section describes what the framework guarantees vs what
      the developer must do
- [ ] The section is specific to this framework, not generic

Boundaries:
- [ ] The opening paragraph states what the file does NOT cover
- [ ] References to architecture, delivery, language, and UI files
      are present
- [ ] No rule belongs to another layer

Framework Specificity:
- [ ] Every rule is specific to this framework
- [ ] No rule would make sense with the framework name changed
- [ ] The framework name appears in the rule text where relevant

Rationale Discipline:
- [ ] Every rule has a one-line rationale
- [ ] The rationale explains why, not just what

Anti-Patterns:
- [ ] The Anti-Patterns section has at least 22 items
- [ ] Each item has a short title
- [ ] At least 12 items have a BAD/GOOD code pair

Code Examples:
- [ ] At least 18 rules in the file have BAD/GOOD code pairs
- [ ] Code blocks use a language tag (jsx, tsx, vue, svelte, etc.)
- [ ] Names are realistic
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
- [ ] No rule from `02-architecture-anti-slop.md` is repeated
- [ ] No rule from the delivery file is repeated
- [ ] No rule from the language file is repeated
- [ ] No rule from the attached sibling framework files is
      repeated
- [ ] References to other files have one-line summaries

If any item fails, ask the AI to revise the specific section. Do
not save a file that fails the self-audit.

## Common Failures

The following failures occur frequently when generating framework
files. Use this table during review.

| Failure | How to spot it | Fix |
|---|---|---|
| Architecture bleed | Includes layering, folder structure, naming | Move to architecture file |
| Delivery bleed | Includes component discipline for any framework | Move to delivery file |
| Language bleed | Includes `any`, `unwrap`, type system rules | Move to language file |
| Universal bleed | Includes "no TODO", "declare assumptions" | Delete; they are in Universal |
| Framework-agnostic rules | Rule makes sense with any framework name | Move to architecture or delete |
| No lifecycle section | Missing "when code runs" discussion | Request the section |
| Missing rationale | Rules say "do not" without "because" | Request rationale |
| Too few anti-patterns | Under 22 items | Request more |
| Shallow code examples | Under 18 BAD/GOOD pairs | Request concrete cases |
| Over-length | Over 400 lines | Split or trim |
| Version confusion | Mixes older and newer API of the framework | Pin a version, update |
| Wiki-style | Explains what the framework is | Remove; only rules |

## After the File Is Accepted

1. Save to `prompts/domains/framework/02-<name>-anti-slop.md`.
2. Update `prompts/README.md` to include the new file in the
   framework list.
3. If the framework has a dominant meta-framework (React → Next.js,
   Vue → Nuxt, Svelte → SvelteKit), generate the meta-framework
   file next.
4. If the framework has a dominant platform (React → React Native,
   Web → Electron), generate the platform file next when needed.

## Time Budget

Generating a framework file with a frontier model takes 4-7 minutes.
Review takes 10-15 minutes with the self-audit checklist. If review
takes longer than 20 minutes, the master prompt likely needs
refinement for future framework files.

## Reference Example

The example in `prompts/_send-packages/example-svelte/` shows the
workflow for a framework file. Follow the same workflow, with the
additional `Framework-Specific Requirements` block inserted into
the master prompt.
