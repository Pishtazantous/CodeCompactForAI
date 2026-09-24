---
id: 02-solid-anti-slop
title: "SolidJS Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-frontend-anti-slop]
category: domain
domain_type: framework
version: 1
---
# SolidJS Anti-Slop Layer

Layered under the master, architecture, and frontend layers. This file adds
rules for Solid signals, memos, resources, stores, fine-grained reactivity, and
components that avoid a virtual DOM.

## 1. Stack Assumptions

1. Read the installed Solid major version before using control-flow or resource
   APIs.
2. Use Solid's fine-grained primitives instead of a virtual-DOM compatibility
   pattern.
3. Keep components synchronous unless a resource or event requires async work.
4. Use the existing router and data layer.
5. Keep domain logic independent from JSX and Solid-specific helpers.
6. Do not add React state, effects, or memoization assumptions.
7. Match the repository's server rendering and hydration configuration.
8. Do not introduce a second reactivity model.

## 2. Components and JSX

1. Components are functions that run once for their reactive scope.
2. Do not call a component as if it were a regular constructor.
3. Keep JSX expressions reactive by reading signals in the expression.
4. Do not destructure a signal's value and expect later updates to be observed.
5. Use props as reactive values when the child needs live updates.
6. Keep event handlers close to the state they update.
7. Use `For` or `Index` according to identity and measurement needs.
8. Keep lists keyed by stable identifiers, not indexes.
9. Use `Show`, `Switch`, and `Match` for conditional UI.
10. Keep each component within one ownership boundary.

BAD:

```tsx
function Counter() {
  const [count, setCount] = createSignal(0);
  const doubled = count * 2;
  return <button onClick={() => setCount(count + 1)}>{doubled}</button>;
}
```

GOOD:

```tsx
function Counter() {
  const [count, setCount] = createSignal(0);
  const doubled = createMemo(() => count() * 2);
  return <button onClick={() => setCount(c => c + 1)}>{doubled()}</button>;
}
```

## 3. Signals Discipline

1. Use a signal for an independently reactive value.
2. Use a store for a coherent object of reactive fields.
3. Use `createMemo` for derived state with meaningful dependencies.
4. Read a signal with its getter inside the reactive consumer.
5. Use functional setters when the next value depends on the previous value.
6. Do not store a signal's value in another plain variable.
7. Do not wrap every primitive in a signal without a reactive consumer.
8. Keep setters close to the event or use case that owns the transition.
9. Use `batch` for a deliberate multi-signal update.
10. Keep signal names semantic and avoid `state` for every value.

## 4. Memos and Resources

1. Use `createMemo` for derived state, not as a blanket performance cache.
2. Ensure a memo's dependencies are read through signal getters.
3. Use `createResource` for asynchronous data owned by a component boundary.
4. Give resources stable sources and explicit loading and error states.
5. Avoid creating a resource for data that can be loaded at the route boundary.
6. Use `Suspense` only around the consumer that needs the pending resource.
7. Do not fetch in every list item or component instance.
8. Handle stale sources when parameters change.
9. Keep resource fetches cancellation-aware when the version supports it.
10. Do not place secrets in a client resource.

## 5. Stores

1. Use a store for related state that must update as one object.
2. Use `produce` or the repository's immutable update pattern for nested state.
3. Keep store fields typed at the public boundary.
4. Do not mutate a store outside its owning update operation.
5. Use a selector or fine-grained consumer for high-frequency values.
6. Do not put server data in a global store when a resource or data layer owns it.
7. Keep store actions semantic and separate from rendering.
8. Do not expose an unbounded store to the whole application by accident.

## 6. Effects and Lifecycle

1. Use `createEffect` to synchronize with external systems.
2. Do not derive values in an effect when a memo expresses the dependency.
3. Provide cleanup for subscriptions, observers, timers, and DOM integrations.
4. Keep effects outside render-only computations.
5. Handle rapid dependency changes without stale writes.
6. Do not use an effect for a local click update.
7. Keep browser APIs behind client-only boundaries during SSR.
8. Test destroy and re-run behavior.

BAD:

```tsx
const [name, setName] = createSignal("");
const [upper, setUpper] = createSignal("");
createEffect(() => setUpper(name().toUpperCase()));
```

GOOD:

```tsx
const [name, setName] = createSignal("");
const upper = createMemo(() => name().toUpperCase());
```

## 7. Fine-Grained Rendering

1. Keep signal reads in the smallest expression that needs them.
2. Do not wrap a whole component in a broad reactive object for one field.
3. Prefer targeted child props for high-frequency values.
4. Use stores with selectors for grouped state.
5. Avoid recreating large objects inside JSX expressions on every update.
6. Do not use a virtual-DOM memoization wrapper as the default.
7. Profile before adding `memo`, `createMemo`, or `batch`.
8. Keep list identity stable for reconciliation and measurement.

## 8. Routing and Data

1. Use the repository's Solid router for navigation.
2. Validate dynamic route parameters before requests.
3. Keep route data in loaders, resources, or the existing data layer.
4. Handle loading, error, and empty states explicitly.
5. Cancel or ignore stale route requests.
6. Do not fetch in a component effect when a route boundary owns the data.
7. Use real links for progressive navigation where supported.
8. Test direct load, back navigation, and failed requests.

## 9. Domain-Specific Anti-Patterns

### 9.1 Reading Signals During Setup Only

BAD:

```tsx
function View() {
  const [user] = createSignal({ name: "Ada" });
  const name = user().name;
  return <p>{name}</p>;
}
```

GOOD:

```tsx
function View(props: { user: User }) {
  return <p>{props.user.name}</p>;
}
```

### 9.2 Global Store for Server Data

BAD:

```tsx
const [users, setUsers] = createSignal([]);
fetchUsers().then(setUsers);
```

GOOD:

```tsx
const users = createResource(() => fetchUsers());
```

### 9.3 Effect as Derived State

BAD:

```tsx
createEffect(() => setVisible(open() && items().length > 0));
```

GOOD:

```tsx
const visible = createMemo(() => open() && items().length > 0);
```

## 10. Response to Violation

If a previous response violated this file, use this structure:

```text
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

State the rule and show the correction. Do not add an apology paragraph.
