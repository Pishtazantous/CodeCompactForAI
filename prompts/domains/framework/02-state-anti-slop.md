---
id: 02-state-anti-slop
title: "State Management Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop]
category: domain
domain_type: framework
version: 1
---

# State Management Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md` and
`domains/framework/02-architecture-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
security anti-patterns, output format) and architectural rules
(layering, dependency direction, folder structure, naming) are NOT
repeated here.

This file covers rules specific to client-side state management:
classifying state, choosing the right tool, and avoiding the patterns
that produce stale data, duplicate sources of truth, and unnecessary
re-renders. It is framework-agnostic within the frontend ecosystem:
it applies to React, Vue, Svelte, Solid, and Angular, though examples
use React syntax. React-specific rules live in
`domains/framework/02-react-anti-slop.md`. Data-fetching rules live in
`domains/framework/02-api-data-anti-slop.md`.

## 1. Stack Assumptions

This layer assumes:

- A single-page application or a server-rendered application with
  client-side interactivity.
- At least one state tool in the project: component state (`useState`,
  `ref`, signals), a global store (Zustand, Redux Toolkit, Pinia,
  Jotai, NgRx, Svelte stores), and a data-fetching library (TanStack
  Query, SWR, Apollo, Vue Query).
- The project has an established pattern for each category. This file
  does not prescribe a specific library.

If the project uses only one tool (for example, only React Query and
`useState`), the rules still apply: the classification is about the
*kind* of state, not the number of libraries.

## 2. State Classification

Every piece of state belongs to exactly one category. The category
determines the tool.

### 2.1 The Six Categories

| Category | Description | Typical tool |
|---|---|---|
| Local UI | State used by one component or its children | Component state |
| Form | Values and validation of a form | Form library |
| Server | Data fetched from a backend | Data-fetching library |
| Global UI | Cross-route UI state (theme, sidebar) | Global store |
| Session | Authenticated user, permissions | Global store + persistence |
| URL | State that must be shareable or bookmarkable | Router / search params |

### 2.2 The Cardinal Rule

Server state and client state are not the same. Never store server data
in a global client store. The data-fetching library owns its cache,
its revalidation, and its invalidation. A global store that duplicates
it will drift.

### 2.3 Classification Is Explicit

Before adding state, answer: which category is this? If the answer is
"it depends", the state is doing two things. Split it.

If the answer is "I will put it in the global store to be safe", the
answer is wrong. Global is not a safe default; it is a coupling
decision.

## 3. Choosing the Tool

### 3.1 Component State for Component State

A value used by one component and its direct children belongs in the
component. `useState`, `useReducer`, `ref`, or the framework's
equivalent.

### 3.2 Form Library for Forms

A form with more than two fields uses the project's form library
(`react-hook-form`, `formik`, `vee-validate`, or equivalent). Do not
reimplement form state with `useState` per field. Do not reimplement
validation.

### 3.3 Data-Fetching Library for Server Data

Everything that comes from the backend goes through the data-fetching
library. This includes:

- REST calls
- GraphQL queries
- WebSocket messages that represent data
- Local storage that mirrors server state

The library handles caching, revalidation, refetching, and error
states. Do not duplicate this in the store.

### 3.4 Global Store for Cross-Route Client State

A store is justified when the state is:

- Used by two or more components in different parts of the tree, AND
- Not server data, AND
- Not form data.

Typical examples: theme, sidebar collapse, current workspace, a
multi-step wizard in progress.

### 3.5 URL for Shareable State

State that another user should see when they open the same URL belongs
in the URL: filters, pagination, selected tab, search query, sort order.

BAD: Storing the current page number in a global store.
GOOD: Storing it in `?page=2` so the URL is shareable.

### 3.6 Server as the Source of Truth

If the state can be recomputed from the server, do not store it
locally. Recompute, or let the data-fetching library cache it.

## 4. Store Discipline

### 4.1 One Store With Slices, or a Few Stores

BAD: Ten separate stores, one per feature.
GOOD: One store with topic-based slices, or two or three stores for
genuinely distinct concerns (auth, UI, workspace).

The number of stores should not grow with the number of features. If it
does, the store is being used as a global variable bag.

### 4.2 No Redux Pattern in Zustand (or Its Equivalent)

BAD: Actions, reducers, dispatchers replicated in a Zustand store.
GOOD: Simple functions that call `set`.

Copying Redux's ceremony into a lighter library discards the library's
advantage.

### 4.3 No `useStore` Without a Selector

BAD:
tsx
const store = useStore();
const user = store.user;
GOOD:

tsx
const user = useStore(s => s.user);
Subscribing to the whole store re-renders on every change, even
unrelated ones.

4.4 Actions Mutate the Store, Nothing Else
Components dispatch actions. Actions update the store. Nothing else
mutates the store.

A component that writes directly to store.user = x bypasses the
action and the invariants it enforces.

4.5 Store Shape Is Flat
A store with nested objects three levels deep is hard to update and
hard to type. Flatten the shape, or use IDs and separate maps.

BAD:

tsx
{ workspace: { project: { board: { columns: { ... } } } } }
GOOD:

tsx
{ workspaceId, projectId, boardId, columns: Record<string, Column> }
4.6 No Derived State in the Store
If a value can be computed from other store values, compute it in the
selector, not in the store.

BAD:

tsx
{ items: [], total: 0, updateTotal() { ... } }
GOOD:

tsx
{ items: [] }
// Selector: const total = useStore(s => s.items.length);
5. Server vs Client State
5.1 Never Duplicate Server Data in a Store
BAD:

tsx
const useUserStore = create(() => ({ user: null, setUser: ... }));
// And also:
const { data: user } = useQuery(...);
Now two sources of truth exist. When one updates, the other is stale.

GOOD: One source. If the data is server data, the query owns it. If it
is client data, the store owns it. They do not share.

5.2 Invalidate, Do Not Sync
When a mutation changes server data, invalidate the affected queries.
Do not manually update the store to match.

BAD:

tsx
await updateUser(data);
userStore.setState({ user: data });
GOOD:

tsx
await updateUser(data);
queryClient.invalidateQueries({ queryKey: ["user", id] });
5.3 Optimistic Updates
When an optimistic update is justified, apply it to the query cache,
not to a duplicate store. The data-fetching library provides
onMutate, onError, and onSettled for this.

5.4 Server State in URL
State that identifies which server resource is being viewed belongs
in the URL: /users/42, ?filter=active. The data-fetching library
reads the URL, not a store.

6. Persistence
6.1 Persist Only What Must Survive Reload
Persistence is a feature, not a default. Persist:

Auth tokens (in secure storage, never localStorage for sensitive
tokens; see the security layer).

User preferences (theme, language).

Draft form data that the user expects to recover.

Do not persist:

Server data (the cache handles its own lifecycle).

Ephemeral UI state (sidebar open, current tab).

Anything derived.

6.2 Explicit Allowlist for Persistence
Persist specific keys, not the whole store.

BAD:

tsx
persist(store, { name: "app" });
GOOD:

tsx
persist(store, {
  name: "app",
  partialize: (state) => ({ theme: state.theme, locale: state.locale }),
});
6.3 Persistence Schema Is Versioned
When the persisted shape changes, old data in the user's browser must
migrate or be discarded. Use the library's version and migrate
options.

6.4 Never Persist Secrets
Tokens, passwords, and personal data belong in secure HTTP-only
cookies, not in localStorage or IndexedDB. If the project uses
localStorage for tokens, report it as a security issue and let the
user decide.

7. Derived State
7.1 Compute in Render
If a value can be computed from props or state during render, compute
it there. Do not store it, do not update it in an effect.

BAD:

tsx
const [count, setCount] = useState(0);
const [double, setDouble] = useState(0);
useEffect(() => { setDouble(count * 2); }, [count]);
GOOD:

tsx
const [count, setCount] = useState(0);
const double = count * 2;
7.2 Memoize Expensive Derivations Only
For a genuinely expensive computation (large sort, complex grouping),
useMemo or the framework's equivalent. For arithmetic and small
filters, no memoization.

7.3 No Derived State in the Store
Covered in 4.6.

7.4 No Duplicate State
If two pieces of state must stay in sync, one of them is derived.
Remove it or derive it.

BAD:

tsx
{ user: null, isAuthenticated: false }
GOOD:

tsx
{ user: null }
// const isAuthenticated = !!user;
8. Re-render Discipline
8.1 Subscribe to the Smallest Slice
Selectors return only what the component needs. Do not select the
whole store.

BAD:

tsx
const { user, theme, sidebar } = useStore();
GOOD:

tsx
const theme = useStore(s => s.theme);
8.2 Selector Returns a Stable Shape
BAD:

tsx
const user = useStore(s => ({ name: s.name, email: s.email }));
The object is new every call. The selector re-renders on every store
change.

GOOD:

tsx
const name = useStore(s => s.name);
const email = useStore(s => s.email);
Or use the library's shallow-equality option if it provides one.

8.3 Context Value Is Memoized
Covered in 02-react-anti-slop.md section 5.3. Repeating because it
is the single most common cause of store-adjacent performance issues.

8.4 Split Context by Change Frequency
Theme changes rarely. Auth changes occasionally. UI state changes
often. Three contexts with three change frequencies. One context forces
every consumer to re-render on any change.

9. State Management Anti-Patterns
9.1 The Global Store as a Dumping Ground
Every new piece of state is added to the store "in case it is needed
elsewhere". The store grows to hundreds of keys, and no one knows what
owns what.

Start with component state. Promote to the store when a second
unrelated consumer appears.

9.2 The Store as a Cache
Storing fetched data in the store because "the store is faster". The
data-fetching library already caches. The store duplicates and drifts.

9.3 The Store as an Event Bus
A store with an events array, a notify method, or pub/sub
semantics. This is a message bus pretending to be a store.

If components need to react to events, use the framework's event
system (React state + effects, Vue watchers, Svelte stores with
subscriptions). Do not build an event bus.

9.4 The Store Mirroring the Server
Every server field has a corresponding store field. Mutations update
the store, then call the server, or vice versa. The two drift
constantly.

The data-fetching library owns server data. The store owns client
state. They do not mirror each other.

9.5 The Store With Reducers and Actions in a Non-Redux Library
Covered in 4.2. Copying Redux ceremony into Zustand, Pinia, or Jotai
defeats their purpose.

9.6 Manual Cross-Store Synchronization
Two stores subscribe to each other to keep values in sync. This is a
merge waiting to happen. Either merge them or remove the duplication.

9.7 useState in a List
BAD: A parent component holds an array of children, each child has
useState for its own data, and the parent needs to read the
children's state.

State lives at the lowest common ancestor. If the parent needs it,
the parent owns it. If the parent does not need it, children own it
and the parent reads on demand.

9.8 Effect-Synchronized State
Two states synchronized by an effect. Every synchronization is a bug
waiting for an edge case. Derive one from the other.

9.9 Server Data in Component State
BAD:

tsx
const [users, setUsers] = useState([]);
useEffect(() => { fetchUsers().then(setUsers); }, []);
This reimplements a cache with no revalidation, no error handling, and
no deduplication. Use the project's data-fetching library.

9.10 Mutable Store Without Notification
A store that is mutated directly (not through a setter) does not
notify subscribers. Components read stale data and never re-render.
Always go through the library's set API.

9.11 Form State in a Global Store
Form state is local by definition. It belongs to the form, not to the
application. Putting it in the store creates coupling between forms
and unrelated pages.

Exception: multi-step wizards that span routes. Even then, isolate the
wizard state in its own store slice.

9.12 Deeply Nested Store Updates
BAD:

tsx
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
Flatten the shape, or use a library with immutable-update helpers
(Immer, the store's own helpers).

9.13 Persisting Derived or Server Data
Covered in 6. Persisting user from the store means the next session
starts with stale user data until the fetch completes.

9.14 State That Belongs in the URL
Filters, pagination, and search terms in a store rather than the URL.
The user cannot share the view, the back button breaks, and a refresh
loses the state.

9.15 Two Sources of Truth
Any two pieces of state that represent the same thing. This is not one
anti-pattern; it is the category that all the above belong to. When
you see duplication, delete one.

10. Response to Violation
If a previous response violated a rule here:

text
In the previous response, [specific rule] was violated. Correction:
[corrected code]
No justification. No apology paragraph. Fix and move on.

text

---