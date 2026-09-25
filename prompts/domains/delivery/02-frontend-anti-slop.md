---
id: 02-frontend-anti-slop
title: "Frontend Anti-Slop Layer"
lang: en
depends_on: ["_universal/00-style-guide.md", "_universal/00-master-anti-slop.md"]
category: domain
domain_type: delivery
version: 4
---

# Frontend Anti-Slop Layer

This file defines behavioral contracts specific to frontend applications. It sits in the delivery layer, below the universal anti-slop rules and above framework-specific patterns. It covers component discipline, state ownership, data fetching, forms, routing, effects, performance, error handling, and configuration. It is framework-agnostic: React, Vue, Svelte, Solid, and Angular share these rules. It does not cover framework-specific patterns (see `domains/framework/`), language rules (see `domains/language/`), visual design (see `ui/04-ui-design-system.md`), or accessibility and performance in detail (see `domains/concern/`).

A frontend runs on a device the developer does not control, on a network that drops, with users who will click everything.

## Scope

This file applies to browser-based single-page and server-rendered applications, regardless of framework. Common stacks include React + Vite/Next.js/Remix, Vue + Vite/Nuxt, Svelte + Vite/SvelteKit, SolidJS, Angular, and Astro. The examples use TypeScript and JSX where illustrative. Framework-specific rules live in framework files. Language-specific rules live in language files. Visual rules live in the UI file.

## Rule Severity

Severity follows `_universal/00-style-guide.md`.

## Contracts

A frontend commits to nine contracts. The table below maps each contract to the rules that enforce it.

| Contract | Description | Enforced By |
|---|---|---|
| Component Boundaries | Every component has a single responsibility. Complex UIs are composed from small components. | FE-001 to FE-008 |
| State Ownership | Every piece of state has exactly one owner. State is not duplicated. | FE-009 to FE-014 |
| Data Flow Direction | Data flows in one direction. Server data comes through the data layer. | FE-012, FE-015 |
| Loading and Error States | Every asynchronous operation has a visible loading state and a visible error state. | FE-016, FE-083, FE-084 |
| Bundle Discipline | The bundle is measured and budgeted. No dependency is added without a size check. | FE-049, FE-051 |
| Resilience | Network failures, malformed responses, and unexpected states do not crash the UI. | FE-052 to FE-057 |
| Accessibility Baseline | Every interactive element is keyboard-reachable, labeled, and focus-visible. | FE-062 to FE-068 |
| Configuration Integrity | Environment-specific values come from configuration. No hardcoded URLs or secrets. | FE-058 to FE-061 |
| Build Reproducibility | The build is deterministic. The same source produces the same bundle. | FE-049 |

## Component Discipline

### FE-001 — Reference Before Creating

**MUST**

Before writing a new component, the assistant MUST:

1. Search the project's component folders for a similar component.
2. If something similar exists, use it.
3. If it is close but imperfect, report the gap and ask before replacing it.
4. Only create a new component when nothing close exists.

A duplicated `Button` is not a style preference. It is a future inconsistency.

### FE-002 — One Component Per File

**MUST**

One exported component per file. Small private helpers (a `Row` used only by `Table`) may live in the same file when the project's pattern allows.

### FE-003 — Component Size

**SHOULD**

A component over 150 lines is usually doing more than one thing. Split when each part has an independent responsibility. Do not split to reduce line count.

### FE-004 — Props Are Contracts

**MUST**

Props MUST be defined with an explicit type. `any` MUST NOT be used for props. Optional props MUST have a documented default. Unknown props MUST NOT be spread with `...rest` unless forwarding to a DOM element.

### FE-005 — Composition Over Configuration

**MUST**

Components MUST compose via slots or children rather than growing boolean flags or complex configuration objects for every layout combination.

Example (illustrative, JSX-style):

BAD:
```tsx
<Card
  title="User"
  subtitle="Details"
  showDivider
  actions={[...]}
  footer={<Button>Save</Button>}
/>
```

GOOD:
```tsx
<Card>
  <Card.Header>User</Card.Header>
  <Card.Body>Details</Card.Body>
  <Card.Footer>
    <Button>Save</Button>
  </Card.Footer>
</Card>
```

Boolean props that toggle layout fragments turn a component into a configuration language. Prefer composition.

### FE-006 — No Prop Drilling Beyond Two Levels

**MUST NOT**

If a prop passes through more than two components unchanged, the project's context or store MUST be used. A new pattern MUST NOT be added.

### FE-007 — No Component Definition Inside a Component

**MUST NOT**

A component MUST NOT be defined inside another component. Every render of the parent creates a new child, unmounting and remounting the subtree. Define the child outside, or inline its JSX.

Example (illustrative, JSX-style):

BAD:
```tsx
function Parent() {
  function Child() { return <div />; }
  return <Child />;
}
```

### FE-008 — Presentational and Container Separation

**SHOULD**

Presentational components SHOULD take props and render. Container components SHOULD fetch data and pass it down. Mixing the two makes both harder to test and reuse.

The distinction is not absolute. A component that both fetches and renders is acceptable when the fetching is trivial and the component is used in one place.

## State Ownership

### FE-009 — One Owner Per Piece of State

**MUST**

Every piece of state MUST have exactly one owner. Derived state MUST be computed, not stored.

Example (illustrative, JSX-style):

BAD:
```tsx
const [user, setUser] = useState<User | null>(null);
const [isAuthenticated, setIsAuthenticated] = useState(false);
// setIsAuthenticated must be kept in sync with setUser
```

GOOD:
```tsx
const [user, setUser] = useState<User | null>(null);
const isAuthenticated = !!user;
```

### FE-010 — Local State Before Global

**MUST**

Start with component-local state. Promote to a store only when a second unrelated component needs it.

BAD: A store slice for a single component's dropdown state.

GOOD: `useState` for the dropdown. Move to the store when a second component reads it.

### FE-011 — URL State for Shareable Data

**MUST**

Filters, pagination, selected tab, and search terms MUST belong in the URL. A URL the user can share is more useful than one that cannot.

### FE-012 — Server State in the Data Layer

**MUST**

Server data MUST belong in the data-fetching library, not in a store or component state.

Example (illustrative, JSX-style):

BAD:
```tsx
const [users, setUsers] = useState<User[]>([]);
useEffect(() => {
  fetch("/api/users").then(r => r.json()).then(setUsers);
}, []);
```

GOOD:
```tsx
const { data: users, isLoading, error } = useQuery({
  queryKey: ["users"],
  queryFn: fetchUsers,
});
```

The data layer owns caching, revalidation, and deduplication.

### FE-013 — No Derived State in Store

**MUST NOT**

If a value can be computed from other state, it MUST be computed where it is used. It MUST NOT be stored and kept in sync.

### FE-014 — Form State Is Local

**MUST**

Form state MUST be local by definition. It MUST belong to the form, not to the application store. Exception: a multi-step wizard that spans routes may use its own isolated store slice.

## Data Fetching

### FE-015 — Use the Project's Fetching Pattern

**MUST**

Every project has one pattern: `useQuery`, `useFetch`, SWR, Apollo, React Query, or the framework's loader. It MUST be used. `fetch` MUST NOT be called directly from a component.

Example (illustrative, JSX-style):

BAD:
```tsx
useEffect(() => {
  fetch("/api/users").then(r => r.json()).then(setUsers);
}, []);
```

GOOD:
```tsx
const { data } = useUsers();
```

### FE-016 — Handle Three States Explicitly

**MUST**

Every fetch MUST have loading, error, and empty states. Each MUST be rendered distinctly.

Example (illustrative, JSX-style):

BAD:
```tsx
const { data } = useQuery(...);
return <Table rows={data} />;
```

The `data` is `undefined` on first render. The component crashes.

GOOD:
```tsx
if (isLoading) return <Spinner />;
if (error) return <ErrorState error={error} />;
if (!data?.length) return <EmptyState />;
return <Table rows={data} />;
```

### FE-017 — Query Keys Are Stable and Complete

**MUST**

A query key MUST include every variable the query depends on.

Example (illustrative, JSX-style):

BAD:
```tsx
useQuery({ queryKey: ["user"], queryFn: () => getUser(id) });
```

Two different users share a cache entry.

GOOD:
```tsx
useQuery({ queryKey: ["user", id], queryFn: () => getUser(id) });
```

### FE-018 — No Manual Cache

**MUST NOT**

A manual cache MUST NOT be maintained in a store or a module-level map. The data-fetching library owns caching.

### FE-019 — Invalidate, Do Not Sync

**MUST**

After a mutation, the affected queries MUST be invalidated. The cache or a duplicate store MUST NOT be manually updated.

Example (illustrative, JSX-style):

BAD:
```tsx
await updateUser(data);
userStore.setState({ user: data });
```

GOOD:
```tsx
await updateUser(data);
queryClient.invalidateQueries({ queryKey: ["user", id] });
```

### FE-020 — No Waterfalls

**MUST NOT**

Sequential fetches where the second depends on the first are sometimes necessary. Parallel fetches where they could be independent MUST NOT be sequential.

Example (illustrative):

BAD:
```tsx
const user = await getUser(id);
const posts = await getPosts(id);
```

GOOD:
```tsx
const [user, posts] = await Promise.all([getUser(id), getPosts(id)]);
```

### FE-021 — Never Fetch in a Loop

**MUST NOT**

A fetch inside a `map` or `for` loop produces N requests and MUST NOT be used. Fetch a batch, or use a joined endpoint.

### FE-022 — Cancel Requests on Unmount

**MUST**

A request that resolves after the component unmounts triggers a state update on an unmounted component. The data-fetching library MUST handle this; manual `fetch` calls do not.

## Forms

### FE-023 — Use the Project's Form Library

**MUST**

The project's form library (`react-hook-form`, `formik`, `vee-validate`, or the framework's built-in) MUST be used. Form state MUST NOT be managed with `useState` per field.

### FE-024 — Every Input Has a Label

**MUST**

Every input MUST have a label. A placeholder is not a label. It disappears on typing and is not reliably announced by screen readers.

Example (illustrative, JSX-style):

BAD:
```tsx
<input placeholder="Email" />
```

GOOD:
```tsx
<label htmlFor="email">Email</label>
<input id="email" type="email" />
```

### FE-025 — Inline Validation Errors

**MUST**

Errors MUST appear next to the field, not in a global toast.

Example (illustrative, JSX-style):

BAD: A toast that says "Invalid form" without indicating which field.

GOOD:
```tsx
<label htmlFor="email">Email</label>
<input id="email" type="email" aria-invalid={!!error} aria-describedby="email-error" />
{error && <p id="email-error" role="alert">{error.message}</p>}
```

### FE-026 — No Submission While Submitting

**MUST**

The submit button MUST be disabled while the mutation is pending. Double submissions create duplicate records.

Example (illustrative, JSX-style):

BAD:
```tsx
<button onClick={handleSubmit}>Save</button>
```

GOOD:
```tsx
<button onClick={handleSubmit} disabled={isPending}>
  {isPending ? "Saving..." : "Save"}
</button>
```

### FE-027 — Reset on Success, Preserve on Failure

**MUST**

On success, the form MUST be reset or the user navigated away. On failure, the user's input MUST be kept. Losing input on a validation error is a bug.

### FE-028 — No Client-Only Validation

**MUST NOT**

Client validation is for UX. The server MUST validate again. A client-validated payload MUST NEVER be trusted.

### FE-029 — Autocomplete Attributes

**MUST**

The standard `autocomplete` values (`email`, `name`, `tel`, `current-password`, `new-password`, `one-time-code`) MUST be used. Password managers and assistive technologies use them.

## Routing

### FE-030 — Use the Project's Router

**MUST**

One router per project. A second router MUST NOT be introduced for a sub-section.

### FE-031 — URLs Describe State

**MUST**

A URL MUST be the address of a view. `/users/42/edit` not `/user?id=42&mode=edit`.

### FE-032 — Validate Route Params

**MUST**

A route param is a string, not a number or a UUID. It MUST be parsed and validated before use.

Example (illustrative, JSX-style):

BAD:
```tsx
const id = params.id; // string
await getUser(id); // API expects number
```

GOOD:
```tsx
const id = Number(params.id);
if (!Number.isInteger(id) || id <= 0) return <NotFound />;
```

### FE-033 — No String-Concatenated URLs

**MUST NOT**

String-concatenated URLs MUST NOT be used. Template literals or the router's path-building API MUST be used instead.

Example (illustrative):

BAD:
```tsx
router.push("/users/" + id + "/edit");
```

GOOD:
```tsx
router.push(`/users/${id}/edit`);
```

### FE-034 — Programmatic Navigation in Handlers

**MUST**

Navigation MUST happen in event handlers or effects, not during render.

Example (illustrative, JSX-style):

BAD:
```tsx
function Page() {
  if (!user) router.push("/login"); // navigation during render
  return <div />;
}
```

GOOD: A route guard, or a navigation in a `useEffect`.

### FE-035 — Prefetch on Intent

**SHOULD**

The next likely route SHOULD be prefetched on hover, focus, or intersection. Every route MUST NOT be prefetched on page load.

## Effects and Lifecycle

### FE-036 — Effects Are for Synchronization

**MUST**

An effect MUST synchronize the component with an external system: DOM APIs, network subscriptions, third-party widgets, timers. It MUST NOT be the place to transform data, derive values, or coordinate between siblings.

### FE-037 — Every Effect Has a Clear Dependency Set

**MUST**

Every reactive value used inside the effect MUST be in the dependency array. No missing dependencies, no extra ones added "just in case".

If a dependency causes an infinite loop, the fix is to change the logic, not to remove the dependency.

### FE-038 — Every Effect Cleans Up

**MUST**

An effect that subscribes to anything (event listener, timer, WebSocket, IntersectionObserver) MUST return a cleanup function.

Example (illustrative, JSX-style):

BAD:
```tsx
useEffect(() => {
  const onResize = () => setWidth(window.innerWidth);
  window.addEventListener("resize", onResize);
}, []);
```

The listener is never removed.

GOOD:
```tsx
useEffect(() => {
  const onResize = () => setWidth(window.innerWidth);
  window.addEventListener("resize", onResize);
  return () => window.removeEventListener("resize", onResize);
}, []);
```

### FE-039 — No Data Fetching in Effects

**MUST NOT**

Data fetching MUST belong in the data layer, not in an effect. See FE-015.

### FE-040 — Reacting to Your Own State Changes

**MUST NOT**

An effect MUST NOT react to a state change the same component caused. Navigate at the source.

Example (illustrative, JSX-style):

BAD:
```tsx
const [submitted, setSubmitted] = useState(false);
useEffect(() => {
  if (submitted) navigate("/done");
}, [submitted]);
```

GOOD:
```tsx
function handleSubmit() {
  // ...
  navigate("/done");
}
```

### FE-041 — Strict Mode Is Not a Bug

**MUST NOT**

React Strict Mode double-invokes effects in development to catch missing cleanup. An effect that breaks under double-invocation is broken. Strict Mode MUST NOT be disabled to make it pass.

## Performance

### FE-042 — Measure Before Optimizing

**MUST**

A performance change without a profile is a guess.

BAD: "This looks slow, let me memoize it."

GOOD: A DevTools Performance trace showing the bottleneck.

### FE-043 — Memoize Only After Measuring

**MUST NOT**

`useMemo`, `useCallback`, `React.memo`, `computed` caching: all have a cost. They MUST be added only after a profile shows a real problem.

The default is: no memoization.

### FE-044 — Virtualize Only Large Lists

**MUST**

Virtualization MUST be used only for 100+ items with complex rows. A 20-item list does not need it.

### FE-045 — Lazy Load Routes and Heavy Components

**MUST**

Routes MUST always be lazy. Heavy components (editors, charts, modals) MUST be lazy when they are not on the critical path.

A small component MUST NOT be lazy-loaded; the network round trip costs more than the code saves.

### FE-046 — No Blocking Work in Render

**MUST NOT**

A synchronous loop over 10,000 items during render blocks the main thread and MUST NOT be used. Break into chunks or offload to a worker.

### FE-047 — Images Have Dimensions

**MUST**

An `<img>` without `width` and `height` causes layout shift. Dimensions or an aspect ratio MUST be specified.

### FE-048 — Font Loading

**MUST**

`font-display: swap` or `optional` MUST be used. The primary font MUST be preloaded. Fonts MUST be subsetted to the characters used.

### FE-049 — Bundle Size Is Measured

**MUST**

The bundle analyzer MUST be run regularly. A new dependency that pushes over the budget MUST fail the build.

### FE-050 — Third-Party Scripts Are Audited

**MUST**

A single analytics script can add 200 ms to LCP. Every third-party script MUST be audited.

### FE-051 — No `import *` for Tree-Shakeable Libraries

**MUST NOT**

`import *` MUST NOT be used for tree-shakeable libraries. Named imports MUST be used instead.

Example (illustrative):

BAD:
```typescript
import * as _ from "lodash";
```

GOOD:
```typescript
import debounce from "lodash/debounce";
```

## Error Handling

### FE-052 — Error Boundaries at the Route Level

**MUST**

A route MUST be wrapped in an error boundary. An unhandled error in a child component MUST render a fallback, not a blank page.

### FE-053 — Errors Are Reported

**MUST**

Errors MUST be sent to the project's error tracker (Sentry, Rollbar) if one exists. A silent error is invisible.

### FE-054 — No Raw Server Errors to the User

**MUST NOT**

`error.message` from the server MUST NOT be displayed directly. It may contain a stack trace or an internal identifier. A user-facing message MUST be mapped from the error code.

### FE-055 — Network and Validation Errors Differ

**MUST**

A network error and a validation error MUST be treated differently. The user cannot fix a network error by changing input.

### FE-056 — Errors Are Contained

**MUST**

An error in one component MUST NOT crash the whole page. Error boundaries MUST isolate failures.

### FE-057 — Empty States Are Distinct From Errors

**MUST**

An empty list MUST NOT be rendered as an error. An empty state MUST be rendered with a clear message and a next action.

## Configuration

### FE-058 — No Hardcoded URLs

**MUST NOT**

Every API URL, base URL, and external service URL MUST come from configuration.

Example (illustrative):

BAD:
```typescript
fetch("https://api.example.com/users");
```

GOOD:
```typescript
fetch(`${import.meta.env.VITE_API_URL}/users`);
```

### FE-059 — Environment Variables Through a Config Module

**MUST**

Environment variables MUST be accessed through a config module that validates and exports typed values. Scattered environment variable lookups inside components MUST NOT be used.

### FE-060 — Feature Flags Are Explicit

**MUST**

A feature flag MUST be read from configuration, not hardcoded in a component.

### FE-061 — No Secrets in the Frontend

**MUST NOT**

Anything in the frontend bundle is public. API keys, tokens, and secrets MUST belong on the server.

BAD: `const apiKey = "sk-..."` in the frontend source.

GOOD: A server proxy that holds the key and authenticates requests.

## Accessibility Baseline

Detailed accessibility rules live in `domains/concern/02-accessibility-critical-anti-slop.md`. The baseline for every frontend:

### FE-062 — Keyboard Accessible

**MUST**

Every interactive element MUST be reachable and operable with keyboard only.

### FE-063 — Focus Visible

**MUST**

`:focus-visible` MUST show an indicator. `outline: none` without a replacement is forbidden.

### FE-064 — Labels

**MUST**

Every input MUST have a `<label>` or an `aria-label`. Every icon-only button MUST have an `aria-label`.

### FE-065 — Alt Text

**MUST**

Every image MUST have `alt` text. Decorative images MUST use `alt=""`. Functional images MUST describe the action.

### FE-066 — No Color-Only Signals

**MUST NOT**

Color MUST NOT be the only signal of state. Pair with an icon, a label, or a shape.

### FE-067 — Semantic HTML

**MUST**

`<button>`, `<a>`, `<input>`, `<nav>`, `<main>`, `<header>`, `<footer>` MUST be used. ARIA is a fallback, not a first choice.

Example (illustrative, JSX-style):

BAD:
```tsx
<div onClick={handleClick}>Save</div>
```

GOOD:
```tsx
<button onClick={handleClick}>Save</button>
```

### FE-068 — Modals Trap Focus

**MUST**

A modal MUST keep focus inside until it closes and MUST return focus to the trigger on close.

## AI-Specific Frontend Discipline

### FE-069 — Component Discovery Before Creation

**MUST**

Before creating any new component, the assistant MUST search the project's existing component directories. If a similar component exists, it MUST be used or extended. Inventing parallel components creates visual inconsistency and maintenance burden.

### FE-070 — Hook Pattern Verification

**MUST**

Before using a custom hook or utility function, the assistant MUST verify it exists in the project. Invented hook names produce "hook not found" errors or undefined behavior at runtime.

BAD: Using `useAuth()` when the project exports `useSession()`.

GOOD: Fetch the project's hooks directory first, then use the verified export.

### FE-071 — CSS Class Verification

**MUST**

Before using a CSS utility class or custom class, the assistant MUST verify the class exists in the project's stylesheet or Tailwind configuration. Invented classes produce no visual effect and are invisible at compile time.

### FE-072 — Existing Pattern Discovery

**MUST**

Before introducing a new pattern (state management, data fetching, styling), the assistant MUST search the project for an existing equivalent. If one exists, it MUST be used. Competing patterns fragment the codebase.

### FE-073 — Architecture Restraint

**SHOULD**

The assistant SHOULD NOT introduce architectural layers, design patterns, or abstractions that the project does not already use. A simple form does not need a state machine, a command pattern, or an event bus unless the project already uses them.

### FE-074 — Library API Verification

**MUST**

Before using a third-party library API, the assistant MUST verify the method exists in the installed version. Different library versions have different APIs. Invented methods produce runtime errors.

## Anti-Patterns

### FE-075 — Duplicate State

**MUST NOT**

The same value stored in a store, a component, and the URL is prohibited. See FE-009.

### FE-076 — Manual Loading State

**MUST NOT**

Reimplementing `isLoading`, `isError`, and `data` when the data library already tracks them is prohibited. See FE-015.

### FE-077 — Index as List Key

**MUST NOT**

Index as key is prohibited for dynamic lists.

Example (illustrative, JSX-style):

BAD:
```tsx
{items.map((item, i) => <Row key={i} />)}
```

GOOD:
```tsx
{items.map((item) => <Row key={item.id} />)}
```

Index as key is acceptable only for static lists.

### FE-078 — Conditional Hook Calls

**MUST NOT**

Conditional hook calls are prohibited. Hooks run in the same order on every render. Conditions go inside the hook, not around it.

BAD: `if (loggedIn) useEffect(...)`.

### FE-079 — Inline Function Props on Memoized Children

**MUST NOT**

A new function on every render defeats memoization and MUST NOT be passed to memoized children.

Example (illustrative, JSX-style):

BAD:
```tsx
<MemoChild onClick={() => handle(id)} />
```

### FE-080 — Context Value Without Memoization

**MUST NOT**

An object literal passed to a context provider is new every render, re-rendering every consumer, and MUST NOT be used without memoization.

Example (illustrative, JSX-style):

BAD:
```tsx
<AuthContext.Provider value={{ user, login, logout }}>
```

### FE-081 — Direct DOM Manipulation

**MUST NOT**

Direct DOM manipulation bypasses the framework's rendering model and MUST NOT be used.

Example (illustrative):

BAD:
```typescript
document.getElementById("root")!.innerHTML = "...";
```

GOOD: State-driven rendering.

### FE-082 — Unsafe HTML Rendering

**MUST NOT**

Rendering user content as raw HTML without sanitization is prohibited. See the security concern file. Sanitize or avoid.

### FE-083 — Missing Loading States

**MUST NOT**

A screen that shows nothing while data loads is prohibited. See FE-016.

### FE-084 — Missing Error States

**MUST NOT**

A screen that shows nothing when a request fails is prohibited. See FE-016.

### FE-085 — Empty State Treated as Error

**MUST NOT**

An empty list rendered as "something went wrong" is prohibited. Empty is not an error. See FE-057.

### FE-086 — Blocking Render

**MUST NOT**

A synchronous operation over 50 ms during render is prohibited. See FE-046.

### FE-087 — Missing Memoization When Needed

**MUST NOT**

A memoized child that re-renders because the parent passes new objects or functions every render is prohibited. See FE-079 and FE-080.

### FE-088 — Excessive Memoization

**MUST NOT**

`useMemo` and `useCallback` everywhere without measurement is prohibited. See FE-043.

### FE-089 — Inline Style for Static Styles

**MUST NOT**

Inline `style` for static styles is prohibited.

Example (illustrative, JSX-style):

BAD: `<div style={{ display: "flex", gap: 8 }} />`.

GOOD: A class or a styled component.

### FE-090 — Global CSS That Leaks

**MUST NOT**

A stylesheet without scoping that affects components outside its intended target is prohibited.

### FE-091 — Direct Window Access in Render

**MUST NOT**

`window.innerWidth` in the render body breaks SSR and causes hydration mismatches. Read in an effect or a hook.

### FE-092 — localStorage in Initial State

**MUST NOT**

Reading `localStorage` in a `useState` initializer breaks SSR. Read in an effect or use a client-only wrapper.

### FE-093 — No Error Boundary

**MUST NOT**

A single unhandled error blanks the whole app. Error boundaries MUST be used. See FE-052.

### FE-094 — Overuse of useReducer

**MUST NOT**

A `useReducer` for two related state values is not an improvement over two `useState` calls and MUST NOT be used.

### FE-095 — useState for Values That Never Change

**MUST NOT**

A constant stored in state is prohibited. Move it out of the component.

### FE-096 — Prop Drilling Through Context Providers

**MUST NOT**

Five nested providers for five values is prohibited. Combine or use a store.

### FE-097 — Re-fetching on Every Mount

**MUST NOT**

A component that refetches data on every mount instead of using the cache is prohibited.

### FE-098 — No Pagination or Virtualization

**MUST NOT**

A list that renders every item from a large dataset is prohibited. See FE-044.

### FE-099 — Uncontrolled Form Inputs With DefaultValue

**MUST NOT**

Mixing `defaultValue` and `value` on the same input is prohibited. The input switches between controlled and uncontrolled, producing a framework warning and unexpected behavior.

### FE-100 — Synchronous State Updates in a Loop

**MUST NOT**

Synchronous state updates in a loop are prohibited.

Example (illustrative, JSX-style):

BAD:
```tsx
for (const item of items) setCount(c => c + 1);
```

The state updates are batched but recompute the reducer N times. Compute once, set once.

### FE-101 — useEffect With Empty Deps for One-Time Setup

**MUST NOT**

`useEffect(() => { ... }, [])` runs once per component instance. If the setup depends on a prop, the deps array is wrong. See FE-037.

### FE-102 — No Suspense Boundary Around Lazy Components

**MUST NOT**

A lazy-loaded component without a `Suspense` boundary fails to render and MUST NOT be used.

## Response to Violation

When a rule in this file is violated, report:

Violation: FE-{NNN}
Reason: {one-line reason}
Correction: {smallest fix}

For multiple violations, report each rule ID separately.

Do not replace a technical correction with a generic explanation.