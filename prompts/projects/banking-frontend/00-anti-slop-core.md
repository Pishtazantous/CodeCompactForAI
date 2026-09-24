---
id: 00-anti-slop-core
title: "Core Anti-Slop Layer - banking-frontend"
lang: en
depends_on: [00-master-anti-slop, 02-frontend-anti-slop, 02-typescript-anti-slop]
category: project
version: 1
---

# Core Anti-Slop Layer - banking-frontend

Layered under `_universal/00-master-anti-slop.md` and the relevant
domain layers. Universal and domain rules are NOT repeated here.

This file contains ONLY rules specific to this repository: its tools,
its patterns, its known anti-patterns, and the reading order that must
be respected before editing any file.

Fill in the sections marked `<!-- FILL IN -->` before the first AI
session on this project. Incomplete sections weaken the layer.

## 1. This Repository's Tools

The tools below are the ones every new piece of code must use. Never
introduce a second one for the same purpose.

### 1.1 Framework and Build

<!-- FILL IN: confirm the exact versions and setup. -->

- UI framework and version:
- Build tool:
- Package manager:
- TypeScript version:
- Target browsers (browserslist):

### 1.2 Routing

<!-- FILL IN: which router is used and how are routes defined? -->

- Router library and version:
- Route definition location:
- Nested route pattern:
- Route parameter validation:
- Lazy loading of routes:

### 1.3 Data Fetching

<!-- FILL IN: which data-fetching library is used? -->

- Library (TanStack Query / SWR / Apollo / native fetch):
- Where query hooks live:
- Query key conventions:
- `staleTime` default:
- `gcTime` default:
- Where the HTTP client lives (e.g. `src/lib/http.ts`):

### 1.4 State Management

<!-- FILL IN: which state tool is used and where do stores live? -->

- Global store library (Zustand / Redux Toolkit / Jotai / Context):
- Store location:
- Store slicing convention:
- Persistence strategy (which stores persist, which do not):
- Selector conventions:

### 1.5 Forms

<!-- FILL IN: which form library is used and how is validation done? -->

- Form library (react-hook-form / formik / native):
- Validation library (zod / yup / valibot):
- Where form schemas live:
- Error display pattern (inline / summary / toast):

### 1.6 Styling

<!-- FILL IN: which styling solution is used? -->

- Styling approach (Tailwind / CSS Modules / styled-components):
- Tailwind config location:
- Design tokens source (`theme.ts`, CSS variables, tokens package):
- Variant library (class-variance-authority / tailwind-variants):
- Class-merge helper (`cn`, `clsx`, `tailwind-merge`):
- Icon library (lucide-react / heroicons / phosphor):

### 1.7 Component Library

<!-- FILL IN: which primitives exist and where? -->

- Primitive components location (`components/ui/`):
- List of available primitives:
- Pattern library (shadcn/ui / Radix / custom):
- Storybook or component explorer (if any):

### 1.8 Testing

<!-- FILL IN: which test framework and how are tests structured? -->

- Test framework (Vitest / Jest):
- Component testing library (Testing Library):
- E2E framework (Playwright / Cypress), if any:
- Test file location and naming:
- How to run tests:

### 1.9 Internationalization

<!-- FILL IN: i18n and RTL setup. -->

- i18n library (react-i18next / next-intl / custom):
- Default language:
- RTL support (yes/no):
- Direction attribute strategy:
- Number and date formatting helpers:

### 1.10 Configuration

<!-- FILL IN: how does the app read configuration? -->

- Environment file location:
- How env vars are accessed (`import.meta.env` / config module):
- Required env vars list:
- `.env.example` location:

## 2. This Repository's Patterns

### 2.1 Folder Layout

<!-- FILL IN: what is the folder structure?
     Example (feature-based):
       src/
         app/            -- app shell, routing
         features/       -- feature modules
         components/     -- shared components
           ui/           -- primitives
         lib/            -- utilities, http client, helpers
         hooks/          -- shared hooks
         stores/         -- global stores
         types/          -- shared types
         styles/         -- global styles, tokens
-->

- App shell and routing:
- Feature modules:
- Shared components:
- Primitives:
- Utilities and helpers:
- Shared hooks:
- Global stores:
- Shared types:
- Styles and tokens:

### 2.2 Naming Conventions

<!-- FILL IN: exact naming rules. -->

- File names for components:
- File names for hooks:
- File names for utilities:
- Component names:
- Hook names:
- Store names:
- Type and interface names:
- CSS class naming (if not Tailwind):
- Test file naming:

### 2.3 Import Style

<!-- FILL IN: absolute vs relative imports, aliases, ordering. -->

- Absolute imports:
- Aliases (e.g. `@/`):
- Import order:
- Type-only imports:
- Barrel files (allowed / not allowed):

### 2.4 Component Patterns

<!-- FILL IN: how are components written in this repo? -->

- Function component style (declaration vs arrow):
- Props type (`interface Props` vs `type Props`):
- Default exports vs named exports:
- `React.FC` usage (yes/no):
- Children prop typing:
- `forwardRef` conventions:
- Compound component pattern usage:

### 2.5 Data Flow

<!-- FILL IN: how does data move through the app? -->

- Fetch pattern (component -> hook -> service -> http):
- Where service functions live:
- Where queries are defined:
- Where mutations are defined:
- How cache invalidation is triggered:
- How errors are surfaced to the user (toast / inline / banner):

### 2.6 UI States

<!-- FILL IN: how are loading, error, and empty states rendered? -->

- Loading state pattern (skeleton / spinner):
- Error state pattern:
- Empty state pattern:
- Error boundary location:
- Global toast/notification system:

## 3. Known Anti-Patterns in This Repo

<!-- FILL IN as discovered. Each entry is a pattern that exists in
     old code and must NOT be propagated to new code. If you touch an
     old file with one of these, migrate it or report it. -->

- <!-- Example:
  Some older components use `useEffect` + `fetch` for data. New
  components must use the React Query hooks in `src/features/*/api`.
-->

- <!-- Example:
  Some forms use `useState` per field instead of `react-hook-form`.
  New forms must use `react-hook-form` with the zod schema.
-->

- <!-- Example:
  Older pages hardcode Persian strings. New pages must use the i18n
  helper `t(...)`. -->

- <!-- Example:
  Some buttons use raw Tailwind classes instead of the `Button`
  primitive. New code must use the primitive. -->

## 4. Required Reading Before Editing

Before editing any file in this repository, fetch in this order:

1. The file itself.
2. A sibling component or hook in the same feature folder.
3. The primitive being used, if the change touches UI.
4. The data-fetching hook or store the file depends on.
5. The type definition shared by the above.

Fetching order matters. Reading the file first prevents you from
assuming its shape from the manifest.

## 5. Constraints Specific to This Repository

<!-- FILL IN: any constraints that are unique to this project. -->

- Accessibility target (WCAG level):
- Performance budget (LCP, INP, CLS targets):
- Supported browsers and minimum versions:
- Supported languages and locales:
- Compliance requirements (e.g. PCI-DSS for card forms, GDPR for PII):
- Third-party services that must not be replaced:

## 6. Response to Violation

If a previous response violated a rule here:
In the previous response, [specific rule] was violated. Correction:
[corrected code]

text

No justification. No apology paragraph. Fix and move on.