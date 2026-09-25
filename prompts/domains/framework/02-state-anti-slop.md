---
id: 02-state-anti-slop
title: "State Management Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-frontend-anti-slop]
category: domain
domain_type: framework
version: 2
---

# State Management Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`,
`domains/framework/02-architecture-anti-slop.md`, and
`domains/delivery/02-frontend-anti-slop.md`. Rules already covered
in those files are NOT repeated here.

This file covers rules specific to client-side state management:
classifying state, choosing the right tool, avoiding duplicate
sources of truth, and preventing unnecessary re-renders. It is
framework-agnostic within the frontend ecosystem. It does NOT cover
data fetching (see `02-api-data-anti-slop.md`), framework-specific
state patterns (React `useState`, Vue `ref`, Svelte runes — see the
framework files), or the UI layer (see `04-ui-design-system.md`).

State is the most common source of frontend bugs. A value stored in
the wrong place, duplicated across two locations, or updated without
the UI knowing is a class of bug that no type system catches. The
rules below enforce a single source of truth for every value.

## 1. Stack Assumptions

This file assumes:

- A frontend application (React, Vue, Svelte, Angular, Solid).
- At least one state tool: component state, a global store
  (Zustand, Redux Toolkit, Pinia, Jotai, NgRx, Svelte stores), and
  a data-fetching library (TanStack Query, SWR, Apollo).
- A router that owns URL state.

The examples use React syntax. The principles are framework-
agnostic. Framework-specific hooks and primitives live in the
framework files. The data-fetching library's caching rules live in
`02-api-data-anti-slop.md`.

## 2. Framework Lifecycle Contracts

State management enforces six contracts. Every section below
enforces one or more of these.

### Contract 1: Single Source of Truth

Every piece of state has exactly one owner. A value stored in two
places drifts. The drift is silent and produces bugs that are hard
to reproduce.

### Contract 2: Explicit Ownership

The location of state is a deliberate decision: local, URL, store,
or server cache. A value that is "somewhere" is a value that no one
understands.

### Contract 3: Unidirectional Updates

State updates flow through defined actions, setters, or mutations.
No component mutates another component's state directly.

### Contract 4: Derived, Not Duplicated

A value that can be computed from other state is computed, not
stored. Stored derived values drift from their source.

### Contract 5: Minimal Subscription

A component subscribes to the smallest slice of state it needs.
Subscribing to more than necessary causes unnecessary re-renders.

### Contract 6: Bounded Lifetime

Every store, cache, and context has a defined lifecycle. State that
persists beyond its useful life is a leak.

## 3. State Classification

### 3.1 The Six Categories

Every piece of state belongs to exactly one category. The category
determines the tool.

| Category | Description | Tool |
|---|---|---|
| Local UI | Used by one component and its children | Component state |
| Form | Values and validation of a form | Form library |
| Server | Data fetched from a backend | Data-fetching library |
| Global UI | Cross-route UI state (theme, sidebar) | Global store |
| Session | Authenticated user, permissions | Global store + persistence |
| URL | State that must be shareable | Router / search params |

### 3.2 Classify Before Coding

Before adding state, answer: which category is this? If the answer
is "it depends", the state is doing two things. Split it.

Rationale: the wrong category produces the wrong tool, and the wrong
tool produces a bug the type system cannot catch.

### 3.3 Global Is Not a Safe Default

If the answer is "I will put it in the global store to be safe", the
answer is wrong. Global is a coupling decision, not a safety net.

Rationale: a value in the global store is visible everywhere and
mutable from everywhere. That is a liability, not a feature.

### 3.4 Server State Is Not Client State

Server data belongs in the data-fetching library. It has its own
cache, its own lifecycle, and its own revalidation rules. A global
store that duplicates it will drift.

BAD:
```typescript
const useUserStore = create(() => ({ user: null, setUser: ... }));

// And also:
const { data: user } = useQuery({ queryKey: ["user"], queryFn: fetchUser });
```

Two sources of truth. One is stale.

GOOD: One source. The query owns the server data. The store owns
client-only state.

## 4. Choosing the Tool

### 4.1 Component State for Component State

A value used by one component and its direct children belongs in
the component.

Rationale: moving a single-component value to a store adds coupling
without benefit.

### 4.2 Form Library for Forms

A form with more than two fields uses the project's form library
(`react-hook-form`, `formik`, `vee-validate`). Do not reimplement
form state with `useState` per field.

Rationale: form libraries handle validation, dirty tracking,
field-level re-renders, and submission state. Reimplementing them
is a large amount of code for no benefit.

### 4.3 Data-Fetching Library for Server Data

Everything that comes from the backend goes through the
data-fetching library. This includes:

- REST calls.
- GraphQL queries.
- WebSocket messages that represent data.
- Local storage that mirrors server state.

Rationale: the library handles caching, revalidation, refetching,
and error states. Duplicating this in the store reimplements a
solved problem poorly.

### 4.4 Global Store for Cross-Route Client State

A store is justified when the state is:

- Used by two or more components in different parts of the tree, AND
- Not server data, AND
- Not form data.

Typical examples: theme, sidebar collapse, current workspace, a
multi-step wizard in progress.

### 4.5 URL for Shareable State

State that another user should see when they open the same URL
belongs in the URL: filters, pagination, selected tab, search query,
sort order.

BAD: The current page number in a global store.

GOOD: The current page number in `?page=2`, so the URL is
shareable.

### 4.6 Server as the Source of Truth

If the state can be recomputed from the server, do not store it
locally. Recompute, or let the data-fetching library cache it.

## 5. Store Discipline

### 5.1 One Store With Slices

BAD: Ten separate stores, one per feature.

GOOD: One store with topic-based slices, or two or three stores for
genuinely distinct concerns (auth, UI, workspace).

Rationale: a store per feature produces a graph of stores that must
be coordinated. Fewer, larger stores with clear slices are simpler.

### 5.2 No Redux Ceremony in a Lighter Library

BAD: Actions, reducers, dispatchers replicated in a Zustand store.

GOOD: Simple functions that call `set`.

Rationale: copying Redux's ceremony into a lighter library discards
the library's advantage.

### 5.3 Selectors Return Only What Is Needed

BAD:
```typescript
const store = useStore();
const user = store.user;
```

GOOD:
```typescript
const user = useStore(s => s.user);
```

Rationale: subscribing to the whole store re-renders on every
change, even changes the component does not read.

### 5.4 Actions Mutate the Store, Nothing Else

Components dispatch actions. Actions update the store. Nothing else
mutates the store.

BAD: A component that writes directly to `store.user = x`.

Rationale: a direct write bypasses the action and the invariants it
enforces.

### 5.5 Flat Store Shape

A store with nested objects three levels deep is hard to update and
hard to type. Flatten the shape or use IDs and separate maps.

BAD:
```typescript
{ workspace: { project: { board: { columns: { ... } } } } }
```

GOOD:
```typescript
{ workspaceId, projectId, boardId, columns: Record<string, Column> }
```

### 5.6 No Derived State in the Store

If a value can be computed from other store values, compute it in
the selector, not in the store.

BAD:
```typescript
{ items: [], total: 0, updateTotal() { /* ... */ } }
```

GOOD:
```typescript
{ items: [] }
// Selector: const total = useStore(s => s.items.length);
```

### 5.7 No Event Bus in a Store

A store with an `events` array or a `notify` method is a message
bus pretending to be a store. Use the framework's event system.

## 6. Server State

### 6.1 Never Duplicate Server Data in a Store

BAD:
```typescript
const useUserStore = create(() => ({ user: null, setUser: ... }));
const { data: user } = useQuery(...);
```

Two sources of truth. When one updates, the other is stale.

### 6.2 Invalidate, Do Not Sync

When a mutation changes server data, invalidate the affected
queries. Do not manually update a duplicate store.

BAD:
```typescript
await updateUser(data);
userStore.setState({ user: data });
```

GOOD:
```typescript
await updateUser(data);
queryClient.invalidateQueries({ queryKey: ["user", id] });
```

### 6.3 Optimistic Updates in the Query Cache

When an optimistic update is justified, apply it to the query cache,
not to a duplicate store. The data-fetching library provides
`onMutate`, `onError`, and `onSettled` for this.

### 6.4 Server State in URL

State that identifies which server resource is being viewed belongs
in the URL: `/users/42`, `?filter=active`. The data-fetching
library reads the URL, not a store.

### 6.5 Cache Keys Are Query Keys

If the project uses a data-fetching library, the cache key is the
query key. Do not invent a second caching scheme in a store.

## 7. Derived State

### 7.1 Compute in Render

If a value can be computed from props or state during render,
compute it there. Do not store it, do not update it in an effect.

BAD:
```typescript
const [count, setCount] = useState(0);
const [double, setDouble] = useState(0);
useEffect(() => { setDouble(count * 2); }, [count]);
```

GOOD:
```typescript
const [count, setCount] = useState(0);
const double = count * 2;
```

Rationale: the effect runs after render, so the component renders
twice: once with a stale `double`, once with the new value. The
extra render is visible to the user as a flash.

### 7.2 Memoize Expensive Derivations Only

For a genuinely expensive computation (large sort, complex
grouping), memoize with `useMemo` or the framework's equivalent.
For arithmetic and small filters, no memoization.

### 7.3 No Derived State in the Store

Covered in 5.6.

### 7.4 No Duplicate State

If two pieces of state must stay in sync, one is derived.

BAD:
```typescript
{ user: null, isAuthenticated: false }
```

GOOD:
```typescript
{ user: null }
// const isAuthenticated = !!user;
```

### 7.5 No Storing What Props Can Compute

BAD:
```typescript
function Component({ items }: Props) {
  const [count, setCount] = useState(items.length);
  // setCount must be kept in sync with items
}
```

GOOD:
```typescript
function Component({ items }: Props) {
  const count = items.length;
}
```

## 8. Persistence

### 8.1 Persist Only What Must Survive Reload

Persistence is a feature, not a default.

Persist:

- Auth tokens (in secure storage).
- User preferences (theme, language).
- Draft form data the user expects to recover.

Do not persist:

- Server data (the cache handles its own lifecycle).
- Ephemeral UI state (sidebar open, current tab).
- Anything derived.

### 8.2 Explicit Allowlist

BAD:
```typescript
persist(store, { name: "app" });
```

GOOD:
```typescript
persist(store, {
  name: "app",
  partialize: (state) => ({ theme: state.theme, locale: state.locale }),
});
```

Rationale: the default persist writes the whole store. Adding a
field to the store silently adds it to storage.

### 8.3 Versioned Persistence Schema

When the persisted shape changes, old data in the user's browser
must migrate or be discarded.

Rationale: a browser that loads the new app with old persisted data
crashes on the first read.

### 8.4 Never Persist Secrets

Tokens, passwords, and personal data belong in secure HTTP-only
cookies, not in `localStorage` or `IndexedDB`.

Exception: mobile apps use Keychain/Keystore, not the general
storage API.

### 8.5 Clear on Logout

On logout, clear user-specific persisted state. The next user should
not see the previous user's data.

## 9. Re-render Discipline

### 9.1 Smallest Subscription

Covered in 5.3.

### 9.2 Selector Returns a Stable Shape

BAD:
```typescript
const user = useStore(s => ({ name: s.name, email: s.email }));
```

The object is new every call. The selector re-renders on every
store change.

GOOD:
```typescript
const name = useStore(s => s.name);
const email = useStore(s => s.email);
```

Or use the library's shallow-equality option if it provides one.

### 9.3 Context Value Is Memoized

BAD:
```typescript
<AuthContext.Provider value={{ user, login, logout }}>
```

The object literal creates a new value every render, re-rendering
all consumers.

GOOD:
```typescript
const value = useMemo(() => ({ user, login, logout }), [user, login, logout]);
<AuthContext.Provider value={value}>
```

### 9.4 Split Context by Change Frequency

Theme changes rarely. Auth changes occasionally. UI state changes
often. Three contexts with three change frequencies.

Rationale: one context forces every consumer to re-render on any
change, including changes the consumer does not read.

### 9.5 `React.memo` Only After Measurement

Covered in the React framework file. Repeating: memoization has a
cost. Add it only when a profile shows the problem.

## 10. State Transitions

### 10.1 Explicit State Machine for Complex Flows

A multi-step flow (checkout, onboarding, wizard) has a state
machine, explicit or implicit. Make it explicit.

BAD:
```typescript
const [step, setStep] = useState(0);
const [isLoading, setIsLoading] = useState(false);
const [error, setError] = useState<string | null>(null);
// twelve combinations, most invalid
```

GOOD:
```typescript
type State =
  | { kind: "idle" }
  | { kind: "submitting" }
  | { kind: "success"; data: Result }
  | { kind: "error"; message: string };
```

Rationale: a discriminated union makes invalid combinations
impossible.

### 10.2 No Boolean Soup

BAD:
```typescript
const [isLoading, setIsLoading] = useState(false);
const [isError, setIsError] = useState(false);
const [isSuccess, setIsSuccess] = useState(false);
// all three can be true
```

GOOD: A single status field or a discriminated union.

### 10.3 Reset State on Route Change

A wizard whose state persists after the user leaves the route
surprises them on return. Reset on route change unless persistence
is intentional.

### 10.4 No Global Loading Flags

A single `isLoading` in the global store for every network call.
Two concurrent calls produce wrong loading states.

GOOD: Loading state per query or per operation.

### 10.5 No Global Error Flags

Same as 10.4 for errors. A single `error` in the store cannot
distinguish which operation failed.

## 11. Store Design

### 11.1 Actions Have Meaningful Names

BAD: `setState`, `update`, `handle`.

GOOD: `login`, `logout`, `addToCart`, `clearCart`.

### 11.2 Actions Are Atomic

An action does one thing. An action that logs in, fetches the user
profile, and navigates to the dashboard is three actions.

### 11.3 No Side Effects in Actions Without a Plan

An action that calls the API has a defined error path and a defined
loading state. Without them, the UI cannot show what is happening.

### 11.4 Async Actions Have Explicit States

BAD:
```typescript
async function login(credentials: Credentials) {
  const user = await api.login(credentials);
  set({ user });
}
```

GOOD:
```typescript
async function login(credentials: Credentials) {
  set({ status: "loading" });
  try {
    const user = await api.login(credentials);
    set({ user, status: "success" });
  } catch (error) {
    set({ error: normalizeError(error), status: "error" });
  }
}
```

### 11.5 No Two Stores Owning the Same Thing

If two stores share a concept (a `user` in an auth store and a
`currentUser` in a profile store), one is derived or they must be
merged.

### 11.6 Store Slices Have Clear Boundaries

A slice's state and actions belong together. A slice that imports
from another slice's state is a sign the slices should be one or
the concept should move.

## 12. Anti-Patterns

### 12.1 `useEffect` to Sync Two States

Covered in 7.1.

### 12.2 Server Data in the Store

Covered in 6.1.

### 12.3 Derived State in the Store

Covered in 5.6.

### 12.4 Duplicate State Across Layers

The same value in a component, a store, and the URL.

### 12.5 Store as a Cache

Covered in 6.5.

### 12.6 Store as an Event Bus

Covered in 5.7.

### 12.7 Global Store for Local UI

A dropdown's open state in the global store.

### 12.8 Global Store for Form State

Covered in the frontend delivery file. Repeating: form state is
local.

### 12.9 Context for Frequently Changing Values

A context value that changes on every keystroke re-renders every
consumer.

### 12.10 Context as Prop Drilling Fix

Covered in the React framework file.

### 12.11 Whole-Store Subscription

Covered in 5.3.

### 12.12 Selector Returning a New Object Every Call

Covered in 9.2.

### 12.13 Context Value Not Memoized

Covered in 9.3.

### 12.14 Persisting the Whole Store

Covered in 8.2.

### 12.15 No Versioned Persistence

Covered in 8.3.

### 12.16 Persisting Secrets

Covered in 8.4.

### 12.17 Not Clearing on Logout

Covered in 8.5.

### 12.18 Boolean Soup

Covered in 10.2.

### 12.19 Loading State in the Global Store

Covered in 10.4.

### 12.20 Error State in the Global Store

Covered in 10.5.

### 12.21 Actions With Side Effects and No Error Path

Covered in 11.3.

### 12.22 Async Action Without Loading State

Covered in 11.4.

### 12.23 Two Stores Owning the Same Concept

Covered in 11.5.

### 12.24 Store Slices That Import Each Other

Covered in 11.6.

### 12.25 Manual Cross-Store Synchronization

Two stores subscribe to each other to keep values in sync. Either
merge them or remove the duplication.

### 12.26 Redux Pattern in Zustand

Covered in 5.2.

### 12.27 Deeply Nested Store Updates

BAD:
```typescript
set(state => ({
  ...state,
  workspace: {
    ...state.workspace,
    project: {
      ...state.project,
      board: { ...state.project.board, name },
    },
  },
}));
```

Flatten the shape or use immutable-update helpers.

### 12.28 Store Without Actions

A store with public fields and a `set` method that accepts anything.
The store has no invariants.

BAD:
```typescript
const useStore = create((set) => ({
  user: null,
  set: (patch) => set(patch),
}));
// useStore.getState().set({ user: "not a user object" });
```

GOOD: Named actions that enforce the shape.

### 12.29 `useState` for Values That Never Change

A constant stored in state. Move it outside the component.

### 12.30 Recomputing Expensive Derived Values Every Render

A filter over 10,000 items computed during every render without
memoization.

### 12.31 Store Without a Version

When the store shape changes, persisted data breaks. Version the
store and migrate.

### 12.32 Zustand Store With `persist` and No `partialize`

Covered in 8.2.

### 12.33 Redux Store Without Slices

A single reducer with 50 action types. Split into slices.

### 12.34 Redux Actions That Do I/O

Redux actions are pure. I/O goes in thunks or middleware.

### 12.35 Jotai Atom for Global Server State

An atom that fetches from the API and stores the result. Use the
data-fetching library instead.

### 12.36 Pinia Store With Mutable Public State

A Pinia store whose `state` is mutated directly by components.

### 12.37 Svelte Store Without a Setter

A `writable` store whose value is mutated directly:
```typescript
storeValue.set(newValue);  // OK
storeValue.subscribe(v => { v.items.push(...); });  // mutation, no notify
```

### 12.38 NgRx Effect Without Error Handling

An effect that calls an API without a `catchError` and a failure
action.

### 12.39 Signals for Event Streams

Signals are for state. Streams of events (typing, scroll, WebSocket
messages) belong in an observable or a subscription.

### 12.40 State That Belongs in the URL

Covered in 4.5.

### 12.41 Store Provider Rerender

A store provider that re-renders every consumer because its value
is a new object every render.

### 12.42 State Duplication Between Tabs

The same state stored in two browser tabs. Use `BroadcastChannel` or
accept that tabs are independent.

### 12.43 Global `isAuthenticated` Boolean

A boolean duplicated from `user`. Use `!!user`.

### 12.44 Store Without a Type

A JS store whose shape is documented only in a comment.

### 12.45 Manual Garbage Collection of Store State

A timer that clears store state after N minutes. The store has no
defined lifecycle.

## 13. Response to Violation

If a previous response violated a rule here:

```
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

No justification. No apology paragraph. Fix and move on.
