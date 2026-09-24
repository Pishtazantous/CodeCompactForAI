---
id: 02-frontend-anti-slop
title: "Frontend Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: delivery
version: 1
---

# Frontend Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
security anti-patterns, output format) are NOT repeated here.

This file covers rules specific to frontend applications: component
discipline, state, data fetching, forms, routing, effects, performance,
error handling, and configuration. It is framework-agnostic: rules that
depend on a specific framework (React, Vue, Angular, Svelte) live in
`domains/framework/`.

## 1. Stack Assumptions

This layer applies to browser-based single-page applications and
server-rendered frontends, regardless of framework. Common stacks:

- React + Vite / Next.js / Remix
- Vue + Vite / Nuxt
- Angular
- Svelte + Vite / SvelteKit
- SolidJS
- Astro

Framework-specific rules live in `domains/framework/`. Language-specific
rules live in `domains/language/`. This file covers only what is common
to all frontend applications.

## 2. Component Discipline

### 2.1 Reference Before Creating

Before writing a new component:

1. Search the project's component directory for similar components.
2. If something similar exists, use it.
3. If it is close but imperfect, report the gap and ask before replacing
   it.
4. Only create a new component when nothing close exists.

### 2.2 One Component Per File

Unless the project organizes differently, one component per file. Small
co-located helpers (sub-components, hooks, style files) are fine when the
project's pattern uses them.

### 2.3 Props Are Contracts

- Define props with explicit types (TypeScript, PropTypes, or the
  project's equivalent).
- Never use `any` for props.
- Optional props must have a documented default.
- Never spread unknown props with `...rest` unless forwarding to a DOM
  element.

### 2.4 No Prop Drilling Beyond Two Levels

If props pass through more than two components unchanged, use the
project's context or store pattern. Do not add a new pattern.

### 2.5 Component Size

A component that exceeds 150 lines is usually doing more than one thing.
Split it only when each part has an independent responsibility, not
merely to reduce line count.

## 3. State Management

- Use the project's existing state solution. Never mix two.
- Local UI state belongs in the component. Global state belongs in the
  project's global store.
- Server data belongs in the project's data-fetching library, never in
  the global store.
- Never put derived state in the store. Compute it where it is used.
- Never duplicate state. If two pieces of state must stay in sync, one
  of them is derived.
- Never store what can be derived from props, URL, or other state.

## 4. Data Fetching

- Follow the project's fetching pattern (React Query, SWR, Apollo,
  native fetch wrapped in a service).
- Never call `fetch` (or `axios`) directly inside a component if the
  project wraps it in hooks or services.
- Handle three states explicitly: loading, error, empty. Never silently
  render nothing when data is missing.
- Never hardcode API URLs. Use the project's environment or config
  layer.
- Never fetch in a loop. Batch or paginate.
- Every query has a cache key strategy matching the project's
  convention.
- Never refetch data that is already fresh unless the task explicitly
  requires it.

## 5. Forms

- Use the project's form library (`react-hook-form`, `formik`,
  `vee-validate`, or equivalent).
- Every input has an associated `<label>` (visible or via
  `aria-label`).
- Validation errors appear inline, near the field, not in a global
  toast.
- Never submit while a submission is in flight.
- Never trust client-side validation as the only line of defense.
- Reset form state on success, preserve it on failure.
- Disable the submit button during submission; do not merely hide the
  error.

## 6. Routing and Navigation

- Use the project's router. Never introduce a second one.
- Route parameters must be validated before use.
- Never construct URLs by string concatenation. Use the router's API.
- Back navigation must be tested with an empty history.
- Never navigate during render. Navigate in event handlers or effects.
- Never rely on the browser's back button for critical flows without a
  fallback.

## 7. Effects and Lifecycle

- Effects run after render. Never use them for derived state.
- Every effect has a clear cleanup function if it subscribes to
  anything (event listeners, timers, sockets, observers).
- Every effect has correct dependencies. No missing dependencies, no
  extra ones added "just in case".
- Never put an async function directly in an effect without wrapping
  and calling it.
- Never use an effect to fetch data that could be fetched at a higher
  level or through the project's data layer.
- Never use an effect to synchronize state that could be computed.

## 8. Performance

- Never import a full library when a lighter alternative already exists
  in the project.
- Never use `import * as X from '...'` for tree-shakeable libraries.
- Never import a whole module when a named export suffices.
- Lazy-load routes and heavy components the way the project does.
- Memoize only when there is a measured problem. Blanket `useMemo` /
  `useCallback` / `React.memo` is a smell, not a solution.
- Never render a list without a stable key. Use the item's ID, not the
  index, unless the list is static and never reorders.
- Never virtualize a short list. Virtualization is for 100+ items.
- Never split code for a component under 50 lines unless the project's
  pattern requires it.

## 9. Error Handling

- Every async operation has an error path.
- Errors are shown to the user, not swallowed.
- Errors are reported to the project's error-tracking service (Sentry,
  Rollbar, or equivalent), if one exists.
- Never show a raw error message from the server to the user.
- Never show a stack trace.
- Network errors and validation errors are handled differently. A
  network error is not a form error.

## 10. Accessibility (Baseline)

Detailed accessibility rules live in
`domains/concern/02-accessibility-critical-anti-slop.md` when the project
requires them. The baseline for every frontend:

- Every interactive element is keyboard-reachable.
- Every button, link, and input has a visible focus indicator.
- Icon-only buttons have an `aria-label`.
- Every input has an associated label.
- Images have meaningful `alt` text, or `alt=""` if decorative.
- Color is never the only signal of state.
- Heading hierarchy is correct. One `<h1>` per page.
- Modals have `role="dialog"`, `aria-modal`, focus trap, and close on
  Escape.

## 11. Environment and Configuration

- Never hardcode URLs, keys, or feature flags.
- Read environment values through the project's config module, not
  directly from `import.meta.env` or `process.env` in components.
- Every new environment variable must be:
  - Added to `.env.example` (or equivalent)
  - Documented in the project's configuration reference
  - Listed in the response's "Next Steps"
- Never commit `.env` or files containing secrets.

## 12. Language and i18n

- Follow the project's i18n strategy:
  - If the project uses an i18n library, use it. Never hardcode
    user-facing strings.
  - If the project hardcodes strings in one language, follow that.
- Never mix RTL and LTR inside a single component unless intentional
  (for example, an LTR input inside an RTL page).
- Numbers, dates, and currencies follow the project's formatting
  helpers.

## 13. Domain-Specific Anti-Patterns

### 13.1 Fetching in a Component

BAD: A component that calls `fetch` in an effect and stores the result
in local state.
GOOD: A hook or service that wraps the fetch, and a data-fetching
library that manages cache and revalidation.

### 13.2 Derived State in `useState`

BAD: Storing `fullName` in state and updating it in an effect.
GOOD: Computing `fullName` from `firstName` and `lastName` during
render.

### 13.3 God Component

BAD: A 500-line component that fetches data, manages forms, renders
lists, and handles routing.
GOOD: A page component that composes data hooks, form components, and
presentational components.

### 13.4 Global Store for Server Data

BAD: Storing fetched users in a global store and manually syncing them.
GOOD: Using the project's data-fetching library with its cache.

### 13.5 Index as Key in a Reorderable List

BAD: `{items.map((item, i) => <Row key={i} />)}` for a sortable list.
GOOD: `{items.map((item) => <Row key={item.id} />)}`.

### 13.6 Inline Functions in Memoized Props

BAD: `<Child onClick={() => handle(id)} />` when `Child` is memoized.
GOOD: A stable callback via the project's convention, or a
`data-*` attribute with event delegation.

### 13.7 Conditional Hooks

BAD: `if (isLoggedIn) { useEffect(...) }`
GOOD: Always call hooks at the top level; put the condition inside.

### 13.8 String-Concatenated URLs

BAD: `router.push('/users/' + id + '/edit')`
GOOD: `router.push({ name: 'user-edit', params: { id } })` or the
project's equivalent.

### 13.9 Toast for Form Errors

BAD: A form that shows validation errors in a global toast.
GOOD: Inline errors under each field, associated with the input.

### 13.10 Ignoring Loading and Error States

BAD: `const { data } = useQuery(...); return <Table rows={data} />`
GOOD: Explicit handling of `isLoading`, `error`, and empty state.

### 13.11 Debouncing Synchronous Operations

BAD: Debouncing a local state update that does not trigger I/O.
GOOD: Debouncing only inputs that trigger network calls, expensive
renders, or persistence.

### 13.12 Animations Without a Reason

BAD: Adding `transition-all` or `animate-pulse` globally.
GOOD: Transitioning specific properties, and only where the change
communicates something.

## 14. Response to Violation

If a previous response violated a rule here:
In the previous response, [specific rule] was violated. Correction:
[corrected code]

text

No justification. No apology paragraph. Fix and move on.