---
id: 02-react-anti-slop
title: "React Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-frontend-anti-slop]
category: domain
domain_type: framework
version: 2
---

# React Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`,
`domains/framework/02-architecture-anti-slop.md`, and
`domains/delivery/02-frontend-anti-slop.md`. Rules already covered
in those files are NOT repeated here.

This file covers rules specific to React: components, hooks,
rendering, lists, context, refs, and React-specific performance
patterns. It does NOT cover framework-agnostic frontend rules (see
`02-frontend-anti-slop.md`), architecture rules (see
`02-architecture-anti-slop.md`), TypeScript rules (see
`02-typescript-anti-slop.md`), UI design rules (see
`04-ui-design-system.md`), or meta-framework rules (see
`02-nextjs-anti-slop.md`, `02-remix-anti-slop.md`).

React's model differs from Vue's, Svelte's, and Angular's. Rules
from those frameworks (reactivity, dependency tracking, watchers) do
not apply. This file describes React on its own terms.

## 1. Stack Assumptions

This layer assumes:

- React 18 or later.
- Function components with hooks.
- Either the automatic JSX runtime (`react-jsx`) or the classic one.
- A modern bundler (Vite, Next.js, Remix, or equivalent).

### Version Applicability

- **Minimum version**: React 18.0.
- **Features used in this file that require specific versions**:
  - `useId`: React 18+.
  - `useTransition`, `useDeferredValue`: React 18+.
  - Automatic batching in promises and timeouts: React 18+.
  - `useSyncExternalStore`: React 18+.
  - `use` hook: React 19+.
  - Server Components: React 19+ with a compatible meta-framework.
- **If the project uses React 17 or earlier**: concurrent features
  are unavailable. The remaining rules still apply.

Class components are not covered. If legacy class components exist,
follow their existing style. Do not convert them to function
components while working on unrelated tasks.

## 2. Framework Lifecycle Contracts

React enforces five contracts on the developer. Every rule below
enforces one or more of these.

### 2.1 Render Is Pure

The component function runs on every render and must have no side
effects. No mutation of external state, no I/O, no subscriptions
during render. Side effects belong in effects or event handlers.

### 2.2 Hooks Run in a Fixed Order

Hooks run in the order they are called, on every render. Conditional
or looped hook calls change the order and corrupt the internal
state. The rules-of-hooks lint enforces this; never disable it.

### 2.3 State Updates Are Asynchronous

`setState` schedules a re-render. The new value is not available in
the current closure. Reading state immediately after setting it
returns the old value.

### 2.4 Effects Run After Paint

`useEffect` runs after the browser paints. `useLayoutEffect` runs
before paint but blocks rendering. The choice between them is a
behavioral decision, not a preference.

### 2.5 Reconciliation Is Key-Based

React matches elements between renders using `key`. A missing or
unstable key causes full subtree remounts, losing state and focus.

## 3. Component Discipline

### 3.1 Function Components Only

New components are function components. Class components are legacy.

Rationale: hooks require function components; class components
cannot use hooks, and mixing the two models in one codebase produces
confusion.

### 3.2 One Component Per File

One exported component per file, matching the project's naming
convention (`UserCard.tsx` or `user-card.tsx`).

Rationale: colocation of file and component keeps search, refactor,
and import paths consistent.

### 3.3 Component Size

A component over 150 lines is usually doing more than one thing.

Rationale: a large component is hard to test in isolation and hard
to reason about. Split when each part has an independent
responsibility, not merely to reduce line count.

### 3.4 No Component Definition Inside a Component

BAD:
```tsx
function Parent() {
  function Child() { return <div />; }
  return <Child />;
}
```

GOOD:
```tsx
function Child() { return <div />; }

function Parent() {
  return <Child />;
}
```

Rationale: `Child` defined inside `Parent` is a new function on
every render. React treats it as a new component type and unmounts
the entire subtree, losing state and DOM.

### 3.5 Props Type Is Explicit

```tsx
interface UserCardProps {
  user: User;
  onSelect?: (user: User) => void;
}

function UserCard({ user, onSelect }: UserCardProps) { /* ... */ }
```

Rationale: explicit props make the contract readable and prevent
unintended prop additions.

### 3.6 No `React.FC`

```tsx
// Bad
const Card: React.FC<Props> = ({ title }) => { /* ... */ };

// Good
function Card({ title }: Props) { /* ... */ }
```

Rationale: `React.FC` adds implicit `children` (removed in newer
types) and hides the actual function signature from tooling.

### 3.7 `children` Typed Explicitly

```tsx
import type { ReactNode, PropsWithChildren } from "react";

function Card({ children }: PropsWithChildren<{ title: string }>) { /* ... */ }
```

Rationale: explicit `children` typing prevents accidental
acceptance of non-renderable values.

### 3.8 Compound Components

For components with fixed structural parts, use the compound
pattern.

```tsx
<Card>
  <Card.Header>User</Card.Header>
  <Card.Body>Details</Card.Body>
</Card>
```

Rationale: compound components avoid boolean flags that select
layout, and let the caller compose what they need.

## 4. Hooks Rules

### 4.1 Top-Level Only

Hooks run at the top level of a component or another hook. Never
inside loops, conditions, or nested functions.

BAD:
```tsx
function Component({ items }) {
  if (items.length > 0) {
    const [count, setCount] = useState(0); // breaks hook order
  }
}
```

GOOD:
```tsx
function Component({ items }) {
  const [count, setCount] = useState(0);
  if (items.length === 0) return null;
}
```

Rationale: React stores hook state in the order hooks are called.
A conditional hook changes the order between renders and corrupts
the state.

### 4.2 Custom Hooks Start With `use`

A custom hook is a function whose name starts with `use` and that
calls other hooks. Without the prefix, the linter cannot verify the
rules of hooks.

### 4.3 Custom Hook Used Once Is a Smell

A custom hook used in a single component and containing only one
`useState` does not earn its own file. Keep it inline.

Rationale: the abstraction adds a layer without reuse.

### 4.4 Dependency Arrays Are Complete

Every reactive value used inside `useEffect`, `useMemo`,
`useCallback`, or `useLayoutEffect` is in the dependency array.

If a dependency causes an infinite loop, the fix is to change the
logic, not to remove the dependency.

### 4.5 Never Suppress `exhaustive-deps` Without a Reason

```tsx
// eslint-disable-next-line react-hooks/exhaustive-deps -- run once on mount
useEffect(() => { fetchOnce(); }, []);
```

Rationale: the lint exists to catch missing dependencies. When it is
suppressed, a comment explains why.

### 4.6 Effects Clean Up

An effect that subscribes to anything (event listener, timer,
WebSocket, observer) returns a cleanup function.

BAD:
```tsx
useEffect(() => {
  window.addEventListener("resize", onResize);
}, []);
```

GOOD:
```tsx
useEffect(() => {
  window.addEventListener("resize", onResize);
  return () => window.removeEventListener("resize", onResize);
}, []);
```

### 4.7 Never Set State During Render

BAD:
```tsx
function Component({ items }) {
  const [sorted, setSorted] = useState([]);
  if (sorted.length !== items.length) {
    setSorted(items); // infinite loop risk
  }
}
```

Rationale: `setState` during render schedules another render. The
only valid exception is the "derived state from props" pattern with
a strict guard; if the code is not that pattern, remove it.

### 4.8 Never Mutate State

BAD:
```tsx
const [items, setItems] = useState<User[]>([]);
items.push(newItem); // no re-render, same array reference
```

GOOD:
```tsx
setItems(prev => [...prev, newItem]);
```

Rationale: React compares state by reference. A mutated array has
the same reference and no update is triggered.

### 4.9 Functional Updates When Depending on Previous State

BAD:
```tsx
setCount(count + 1);
```

If the update depends on the previous value, use the functional
form.

GOOD:
```tsx
setCount(c => c + 1);
```

Rationale: with batched updates, the closed-over `count` may be
stale.

### 4.10 `useRef` for Values That Do Not Trigger Renders

`useRef` is for:

- Mutable values that survive renders without causing re-renders
  (timer IDs, previous values, imperative handles).
- Direct DOM access for focus, scroll, or integrating a non-React
  library.

Rationale: a `useRef` update does not trigger a re-render. Using it
for something that should trigger a re-render is a bug.

### 4.11 `useLayoutEffect` Only When Required

`useLayoutEffect` runs synchronously before paint. It is needed only
when measuring the DOM and applying a fix before the user sees the
result.

Rationale: `useLayoutEffect` blocks rendering. Using it for the
common case (subscriptions, timers) slows every render.

### 4.12 `useMemo` and `useCallback` Only After Measuring

Covered in the frontend delivery file. Repeating: these are
performance tools, not correctness tools. The default is no
memoization.

## 5. Rendering

### 5.1 Render Is Pure

A component's render function does not:

- Mutate external state.
- Send network requests.
- Subscribe to events.
- Access `localStorage`, `document.cookie`, or similar.

Rationale: React may re-render a component without committing the
result (for example, when a parent's render is discarded). Side
effects in render fire anyway.

### 5.2 Conditional Rendering With `&&` Needs Boolean

BAD:
```tsx
{items.length && <List items={items} />}
```

When `items.length` is `0`, React renders `0` on the page.

GOOD:
```tsx
{items.length > 0 && <List items={items} />}
```

### 5.3 No Falsy-Value Leaks

A ternary with a falsy branch renders that value:

BAD:
```tsx
{condition ? <Component /> : null} // fine
{condition ? <Component /> : 0} // renders "0"
```

If a value is falsy but not renderable, convert to `null`.

### 5.4 Text Rendering

`<div>{count}</div>` renders the number. `<div>{obj}</div>` throws.
`<div>{bool}</div>` renders nothing. Be aware of which values are
renderable.

### 5.5 No Array Direct Children Without Keys

A list of elements renders correctly only if each has a stable
`key`. See section 6.

## 6. Lists and Keys

### 6.1 `key` Must Be Stable

BAD:
```tsx
{items.map((item, index) => <Row key={index} item={item} />)}
```

GOOD:
```tsx
{items.map(item => <Row key={item.id} item={item} />)}
```

Rationale: an index key breaks when the list reorders, inserts, or
deletes from the middle. React reuses the wrong component for the
wrong data.

### 6.2 No Random or Time-Based Keys

`key={Math.random()}` or `key={Date.now()}` forces every item to
remount on every render.

### 6.3 `key` on the Outermost Repeated Element

BAD:
```tsx
{items.map(item => <li><Row key={item.id} item={item} /></li>)}
```

GOOD:
```tsx
{items.map(item => <li key={item.id}><Row item={item} /></li>)}
```

Rationale: the key belongs to the element React repeats.

### 6.4 Fragment Keys

`<>...</>` cannot carry a `key`. Use `<React.Fragment key={...}>`
when a fragment is a list item.

## 7. Context

### 7.1 Context for Rare, Global Values

Context is for:

- Theme.
- Locale.
- Auth session (when the project does not use a store for it).
- Configuration that never changes during a session.

Rationale: a context value change re-renders every consumer.
Frequently changing values belong in a store with selectors.

### 7.2 Context Value Is Memoized

BAD:
```tsx
<AuthContext.Provider value={{ user, login, logout }}>
```

The object literal is a new value every render.

GOOD:
```tsx
const value = useMemo(() => ({ user, login, logout }), [user, login, logout]);
<AuthContext.Provider value={value}>
```

### 7.3 Split Contexts by Change Frequency

A single context that contains theme, user, and current tab
re-renders every consumer when any of them changes. Split into
separate contexts.

### 7.4 Custom Hook Over Raw Context

Export a `useAuth()` hook that reads the context and throws a clear
error when used outside the provider. The raw context cannot.

### 7.5 Context Is Not for Prop Drilling Fix

Two or three levels of prop passing are fine. Context is for
cross-cutting values, not for avoiding a few props.

## 8. Refs

### 8.1 `useRef` Is Not State

A `useRef` change does not trigger a re-render. If the UI must
update, use `useState`.

### 8.2 DOM Refs for Specific Operations

A DOM ref is for focus, scroll, or integrating a third-party
library. Direct DOM manipulation outside of these uses is a sign
that the component should render based on state.

### 8.3 Ref Forwarding

Primitives that wrap a DOM element forward the ref.

```tsx
const Input = forwardRef<HTMLInputElement, InputProps>(function Input(props, ref) {
  return <input ref={ref} {...props} />;
});
```

Rationale: consumers need to attach refs (for focus, measurement,
or library integration). Without forwarding, they cannot.

### 8.4 Callback Refs

A callback ref runs when the element mounts and unmounts. It is a
place for imperative setup and teardown of a third-party library.

## 9. Performance

### 9.1 No `React.memo` Without Measurement

`React.memo` prevents re-renders only when props are shallowly
equal. If the parent passes new objects or functions every render,
memoization does not help.

Rationale: `React.memo` adds a comparison cost on every render. Use
it only when a profile shows the component re-rendering
unnecessarily.

### 9.2 Stable Props for Memoized Children

BAD:
```tsx
<MemoChild onClick={() => handle(id)} />
```

A new function every render defeats memoization.

GOOD:
```tsx
const handleClick = useCallback(() => handle(id), [id]);
<MemoChild onClick={handleClick} />
```

Or pass data via attributes and use event delegation.

### 9.3 No Inline Object Props for Memoized Children

BAD:
```tsx
<MemoChild style={{ color: "red" }} />
```

The object is new every render.

GOOD: Hoist the object outside the component or use a CSS class.

### 9.4 `useMemo` for Genuinely Expensive Computation

A sort of 10,000 items, a complex grouping, or a tree build.
Arithmetic and small filters do not need memoization.

### 9.5 Virtualize Long Lists

Lists over 100 items with complex rows belong in a virtualizer
(`react-window`, `react-virtual`, `@tanstack/react-virtual`).

### 9.6 Lazy Load Routes and Heavy Components

`React.lazy` with `Suspense` for code-split routes and modals,
editors, and charts. Do not lazy-load small components.

### 9.7 Avoid Re-Rendering Distant Siblings

State that lives at a high level re-renders every child when it
changes. Push state down to the component that needs it, or use a
store with selectors.

### 9.8 `useDeferredValue` and `useTransition`

For expensive renders triggered by frequent updates (search input,
filter changes), `useDeferredValue` or `useTransition` keeps the
input responsive.

### 9.9 Batching Is Automatic

React 18 batches state updates in promises, timeouts, and native
event handlers. Do not manually batch unless the project targets
React 17.

## 10. Error Handling

### 10.1 Error Boundaries at Route Level

Every route is wrapped in an error boundary. A component error
renders a fallback, not a blank page.

### 10.2 Error Boundary Is a Class Component

Error boundaries are the one remaining use case for class
components.

```tsx
class ErrorBoundary extends React.Component<Props, State> {
  static getDerivedStateFromError(error: Error) { return { error }; }
  componentDidCatch(error: Error, info: React.ErrorInfo) {
    reportError(error, info);
  }
  render() { /* ... */ }
}
```

Rationale: hooks cannot catch render errors. The class API remains
the only option.

### 10.3 Errors in Event Handlers Are Not Caught by Boundaries

An error thrown in an event handler bypasses error boundaries. It
is reported to the global error handler (`window.onerror`).

### 10.4 Errors in Async Code Are Not Caught by Boundaries

A rejected promise in an effect is not caught by an error boundary.
Handle it explicitly or route it to an error state.

### 10.5 Report Errors

Every caught error goes to the project's error tracker (Sentry,
Rollbar) with context (component stack, user ID, request ID).

## 11. React-Specific Anti-Patterns

### 11.1 Conditional Hooks

Covered in 4.1.

### 11.2 Hook Calls in Loops

BAD:
```tsx
items.forEach(item => {
  const [state, setState] = useState(item); // different count each render
});
```

### 11.3 Missing Dependency in `useEffect`

A dependency array that omits a value used inside the effect. The
effect runs with stale values.

### 11.4 Extra Dependency in `useEffect`

A dependency that is not used inside the effect causes the effect
to re-run unnecessarily.

### 11.5 `useEffect` for Derived State

Covered in the frontend delivery file. Repeating: a `useEffect`
whose only job is to call a setter for a derived value is a
`useMemo` or a direct computation.

### 11.6 `useState` for Values From Props

BAD:
```tsx
function Component({ initialCount }: Props) {
  const [count, setCount] = useState(initialCount); // stale if prop changes
}
```

Use the prop directly, or reset with a `key`.

### 11.7 `useState` for Values From URL

Read from the router, not from a duplicated state. The URL is the
source of truth.

### 11.8 `useRef` for Render-Impacting Values

A ref does not trigger re-render. If the UI depends on the value,
use state.

### 11.9 `useLayoutEffect` for Subscriptions

A subscription does not need to block paint. Use `useEffect`.

### 11.10 `useMemo` for Correctness

Reaching for `useMemo` because a value must be stable for
correctness (not performance) is a design smell. Reconsider the
data flow.

### 11.11 `useCallback` Everywhere

Blanket memoization adds overhead and noise. Use it only when a
child is memoized and the callback identity matters.

### 11.12 `React.memo` on Everything

Covered in 9.1.

### 11.13 Inline Components in Props

BAD:
```tsx
<Route component={() => <Page />} />
```

A new component type every render forces a remount. Pass
`<Page />` or a stable reference.

### 11.14 Key on a Non-List Element

`<div key="x">` outside a list has no effect. Remove it.

### 11.15 Spreading Unknown Props

BAD:
```tsx
function Card(props) {
  return <div {...props} />; // forwards onClick, style, etc.
}
```

Spreading unknown props onto a DOM element forwards attributes that
React may not expect (`onChange` on a `<div>`), producing warnings
or unexpected behavior.

GOOD: Extract known props, forward the rest explicitly.

### 11.16 `dangerouslySetInnerHTML` With User Content

BAD:
```tsx
<div dangerouslySetInnerHTML={{ __html: userContent }} />
```

XSS. Sanitize with DOMPurify or use `textContent`.

### 11.17 `<img>` Without `alt`

Every image has an `alt`. Decorative images use `alt=""`.

### 11.18 `<div onClick>` Instead of `<button>`

A clickable `<div>` lacks keyboard activation and screen reader
semantics.

### 11.19 Controlled Input Without `onChange`

BAD:
```tsx
<input value={value} />
```

React warns that the input is read-only. Add an `onChange`, or use
`defaultValue` for uncontrolled.

### 11.20 Uncontrolled to Controlled Switch

An input whose `value` starts as `undefined` is uncontrolled, then
becomes controlled when a value arrives. Always pass a defined
initial value.

### 11.21 Mutating Props

BAD:
```tsx
function Child({ user }: Props) {
  user.name = "new"; // mutates the parent's object
}
```

Props are read-only. Emit an event or call a callback.

### 11.22 Using `index` in a Stable List

Covered in 6.1.

### 11.23 State Updates in a Loop

BAD:
```tsx
for (const item of items) setCount(c => c + 1);
```

Each update is batched but recomputes the reducer N times. Compute
the total and update once.

### 11.24 `useState` With a Function Initializer Only When Needed

`useState(() => computeExpensiveValue())` runs the function once.
`useState(computeExpensiveValue())` runs it on every render. Use the
function form when the computation is expensive.

### 11.25 `setState` in `useMemo`

A `useMemo` that calls a setter is a `useEffect` in disguise and
may fire during render.

### 11.26 Reading `window` During Render

`window.innerWidth` in the render body breaks SSR and causes
hydration mismatches. Read in an effect or a lazy initializer.

### 11.27 Suspense Without a Fallback

A `<Suspense>` without a `fallback` prop renders nothing when the
tree suspends. Always provide a fallback.

### 11.28 Lazy Component Without Suspense

A `React.lazy` component not wrapped in `<Suspense>` throws at
render time.

### 11.29 Key on a Component That Wraps Children

A `key` on a wrapper component remounts the wrapper and its
children. If only the children should reset, put the key on the
children.

### 11.30 Refs to Function Components

A function component cannot receive a ref without `forwardRef`. A
`ref` prop on a function component is a warning, not a ref.

### 11.31 Effects That Depend on Functions Defined in Render

A function defined in the component body changes identity on every
render. An effect that depends on it re-runs on every render.

GOOD: Define the function inside the effect, or wrap it in
`useCallback` with a stable dependency set.

### 11.32 `useReducer` for Simple State

A reducer with one action is a `useState` in disguise. Use the
simpler tool.

### 11.33 Context as a Global Store

Covered in 7.1. A context with dozens of values and frequent updates
is a store. Use a store with selectors.

### 11.34 Manual Reconciliation

Mutating the DOM directly to add or remove elements React owns.
React overwrites the change on the next render.

### 11.35 Bypassing the Error Boundary

A `try/catch` in an event handler that swallows the error prevents
the boundary from seeing it. Report and rethrow, or handle it
locally with UI feedback.

## 12. Response to Violation

If a previous response violated a rule here:

```
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

No justification. No apology paragraph. Fix and move on.
