---
id: 02-svelte-anti-slop
title: "Svelte Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-frontend-anti-slop]
category: domain
domain_type: framework
version: 1
---
# Svelte Anti-Slop Layer

Layered under the master, architecture, and frontend layers. This file adds
rules for Svelte components, runes and legacy reactivity, stores, transitions,
events, and browser resources.

## 1. Stack Assumptions

1. Read the installed Svelte major version before choosing reactivity APIs.
2. Match the repository's compiler and accessibility settings.
3. Use the existing router and data layer.
4. Keep browser-only code behind lifecycle or event boundaries.
5. Keep stores for shared state, not for every local value.
6. Do not add a second reactivity system.

## 2. Component and Props

1. Keep component files focused on a reusable interface and behavior.
2. Type exported props with the project's TypeScript pattern.
3. Use explicit defaults for optional props.
4. Declare dispatched events with typed custom events.
5. Do not mutate a prop or a value owned by a parent.
6. Use snippets or slots for composition when supported.
7. Keep DOM attribute fallthrough intentional.
8. Test updates, destroy, and error paths.

BAD:

```svelte
<script>
  export let user;
  user.name = "Changed";
</script>
```

GOOD:

```svelte
<script>
  export let user;
  const dispatch = createEventDispatcher();
  function rename() { dispatch("rename", user.id); }
</script>
<button on:click={rename}>Rename</button>
```

## 3. Reactivity Discipline

1. Use runes for new Svelte 5 code only when the repository has adopted them.
2. Use `$state` for local mutable state and `$derived` for computed state.
3. Use `$effect` only for synchronization with external systems.
4. Do not derive state in an effect when a derived expression is sufficient.
5. Keep reactive updates close to the state owner.
6. Do not use `$state` for a value that is immutable server data.
7. Read legacy store syntax from the installed compiler rules, not memory.
8. Avoid mutation that hides a new reference from legacy subscriptions.
9. Keep async updates cancellation-aware when a component can be destroyed.
10. Do not update global state from a component without an explicit contract.

BAD:

```svelte
<script>
  let firstName = "Ada";
  let displayName = "";
  $: displayName = firstName.toUpperCase();
</script>
```

GOOD:

```svelte
<script>
  let firstName = $state("Ada");
  let displayName = $derived(firstName.toUpperCase());
</script>
```

## 4. Stores

1. Use a writable store for shared mutable state.
2. Use a readable store when consumers must not write.
3. Use derived stores for state computed from another store.
4. Keep store names semantic and expose the smallest public surface.
5. Use `$store` subscriptions only where the component owns the lifetime.
6. Do not store fetched server data in a global store when a data layer exists.
7. Keep store updates immutable so subscribers can detect changes.
8. Do not write to a store from a derived store.

BAD:

```ts
export const users = writable([]);
users.push(user);
```

GOOD:

```ts
export const users = writable<User[]>([]);
export function addUser(user: User) { users.update(current => current.concat(user)); }
```

## 5. Effects and Lifecycle

1. Use effects for DOM measurement, subscriptions, timers, and integrations.
2. Return cleanup from every effect that owns a resource.
3. Do not fetch data in an effect when a parent boundary owns the request.
4. Keep browser APIs out of module initialization when SSR is possible.
5. Use `onMount` for client-only setup and clean it on destroy.
6. Do not leave an interval, observer, or listener running after destroy.
7. Handle race conditions when a prop changes rapidly.

BAD:

```svelte
<script>
  onMount(() => { window.setInterval(refresh, 1000); });
</script>
```

GOOD:

```svelte
<script>
  onMount(() => {
    const timer = window.setInterval(refresh, 1000);
    return () => window.clearInterval(timer);
  });
</script>
```

## 6. Events and Data Flow

1. Dispatch semantic events with a small payload.
2. Keep callbacks in the parent when the child reports intent.
3. Bind only to values the component needs.
4. Use stores or context only for deliberate boundaries.
5. Keep route data out of a general-purpose store.
6. Handle loading, empty, and error states explicitly.
7. Use the repository's stale-result guard.
8. Do not fetch in each row of a list.
9. Keep navigation in event handlers, not initial reactive statements.

## 7. Transitions

1. Use transitions only when they communicate state or spatial continuity.
2. Prefer the repository's reduced-motion and accessibility conventions.
3. Keep duration and delay bounded.
4. Animate transform or opacity when possible.
5. Ensure an entering element does not trap focus or hide an error.
6. Use keyed each blocks for identity-sensitive list transitions.
7. Do not add global motion for decoration alone.
8. Test keyboard navigation while a transition is active.

BAD:

```svelte
{#if visible}<section transition:fly={{ y: 200, duration: 4000 }}>Panel</section>{/if}
```

GOOD:

```svelte
{#if visible}<section transition:fly={{ duration: 180 }}>Panel</section>{/if}
```

## 8. Routing and SSR

1. Use the existing SvelteKit or router navigation APIs.
2. Validate route parameters before requests.
3. Keep server-only modules out of client bundles.
4. Guard browser globals during SSR.
5. Use links for navigable elements and event handlers for programmatic actions.
6. Test direct load, back navigation, and failed requests.
7. Keep layout state separate from page data.

## 9. Domain-Specific Anti-Patterns

### 9.1 Shared State Without Contract

BAD:

```ts
export const state = writable({ token: "", draft: "" });
```

GOOD:

```ts
export const session = writable<Session | null>(null);
export const draft = writable<Draft>({ title: "" });
```

### 9.2 Effect Used as Computed State

BAD:

```svelte
<script>
  let total = 0;
  $: total = price * quantity;
</script>
```

GOOD:

```svelte
<script>
  let price = $state(0);
  let quantity = $state(0);
  let total = $derived(price * quantity);
</script>
```

### 9.3 Store Update Without a Stable Owner

BAD:

```ts
export const draft = writable({ title: "" });
```

GOOD:

```ts
export function createDraftStore() {
  return writable({ title: "" });
}
```

## 10. Response to Violation

If a previous response violated this file, use this structure:

```text
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

Name the rule and show the correction. Do not justify the old implementation.
