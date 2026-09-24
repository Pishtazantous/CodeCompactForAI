---
id: 02-vue-anti-slop
title: "Vue Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-frontend-anti-slop]
category: domain
domain_type: framework
version: 1
---
# Vue Anti-Slop Layer

Layered under the master, architecture, and frontend layers. This file adds
rules for Vue components, the Composition API, reactivity, props, emits, and
provide/inject. General frontend rules are not repeated.

## 1. Stack Assumptions

1. Use the repository's supported Vue major version and build mode.
2. Prefer `<script setup lang="ts">` for new single-file components when the
   project uses it.
3. Keep composition functions free of framework-wide singleton assumptions.
4. Use Vue Router and the repository's data layer; do not introduce another
   router or cache.
5. Read the installed version before using API, compiler, or reactivity options.
6. Keep domain rules independent from Vue runtime objects.
7. Match the repository's Options API or Composition API boundary.

## 2. Component and Props

1. Declare props with a typed `defineProps` contract when TypeScript is active.
2. Use `withDefaults` or an equivalent explicit default policy for optional props.
3. Keep emits named and typed with `defineEmits`.
4. Validate or normalize input at the component boundary that owns the event.
5. Avoid mutating a prop, including nested prop objects.
6. Use slots when content is composition; use props when content is data.
7. Keep attribute fallthrough intentional and test the resulting DOM.
8. Do not spread unknown attributes into a component that does not accept them.
9. Keep components focused on one responsibility; extract only reusable behavior.
10. Use stable keys for reorderable lists.

BAD:

```vue
<script setup lang="ts">
const props = defineProps<{ user: { name: string } }>();
props.user.name = "Updated";
</script>
```

GOOD:

```vue
<script setup lang="ts">
const props = defineProps<{ user: { name: string } }>();
const emit = defineEmits<{ rename: [name: string] }>();
</script>
<template><button @click="emit('rename', 'Updated')">{{ user.name }}</button></template>
```

## 3. Composition API Discipline

1. Keep `setup` focused on wiring; move substantial behavior into named
   composables.
2. A composable is reusable behavior, not a bag of state.
3. Return readonly state when callers must not mutate it.
4. Accept reactive inputs explicitly; do not read globals implicitly.
5. Clean up watchers, event listeners, observers, and timers on unmount.
6. Keep composable names aligned with the behavior they expose.
7. Do not return a giant object containing every ref in the component.
8. Keep lifecycle hooks close to the resource they own.
9. Avoid watchers when a computed value expresses the dependency directly.
10. Keep async race handling explicit with cancellation or request identity.

## 4. Reactivity Rules

1. Use `ref` for primitive values and replaceable reactive values.
2. Use `reactive` for grouped mutable objects when replacement is not needed.
3. Use `computed` for derived state; never duplicate a computed in a ref.
4. Do not destructure a reactive object if updates must remain observable.
5. Use `toRefs` only when preserving child reactivity is intentional.
6. Treat `reactive` and `ref` unwrapping in templates as a deliberate API choice.
7. Do not mutate a ref's `.value` through a lost alias.
8. Do not use watchers to synchronize two independent sources of truth.
9. Batch expensive derivations or move them to a boundary that needs them.
10. Test updates after async callbacks and component unmount.

BAD:

```ts
const firstName = ref("Ada");
const displayName = ref("");
watch(firstName, value => { displayName.value = value.toUpperCase(); });
```

GOOD:

```ts
const firstName = ref("Ada");
const displayName = computed(() => firstName.value.toUpperCase());
```

## 5. Watchers and Lifecycle

1. A watcher must have a named source and an intentional side effect.
2. Provide cleanup for subscriptions and asynchronous effects.
3. Use `onMounted` for client integration, not for deriving state.
4. Use `onUnmounted` or an effect cleanup to release every resource.
5. Do not await inside `onMounted` without handling rejection and cancellation.
6. Keep route watchers from issuing duplicate requests for equivalent params.
7. Stop a long-running timer when its owning component is destroyed.
8. Do not register global listeners in module scope.

## 6. Emits and Parent Contracts

1. Emit semantic events, not component implementation details.
2. Keep event payloads small, typed, and serializable where practical.
3. Use `v-model` only when the parent and child genuinely share that contract.
4. Do not emit an event and mutate local state in ways that create two sources of
   truth.
5. Handle missing optional event data explicitly.
6. Test keyboard and pointer paths for every interactive event.

BAD:

```vue
<button @click="isOpen = false; $emit('close', $event.target)">Close</button>
```

GOOD:

```vue
<button @click="close">Close</button>
```

```ts
function close() {
  isOpen.value = false;
  emit("close");
}
```

## 7. Provide and Inject

1. Use provide/inject for a stable, intentional cross-cutting contract.
2. Give the injection key a type and a clear owner.
3. Provide defaults only when absence is a supported state.
4. Keep injected values narrow; do not expose a feature's entire store.
5. Define the provider close to the subtree that needs it.
6. Do not use provide/inject to hide a missing architecture boundary.
7. Make singleton state explicit; do not accidentally create disconnected
   providers.
8. Test missing-provider behavior for components that require it.

## 8. Routing and Data

1. Use Vue Router APIs for paths, params, query values, and navigation.
2. Validate route params before using them in requests.
3. Keep route components responsible for route data, not a global utility bag.
4. Handle loading, empty, and error states explicitly.
5. Cancel or ignore stale requests when params change quickly.
6. Use the repository's composable or query layer for server data.
7. Do not fetch in a watcher when a route loader or setup boundary is correct.
8. Preserve browser history semantics after mutations.

## 9. Templates and Rendering

1. Keep template expressions readable; move complex work to computed functions.
2. Use `v-if` and `v-for` according to Vue's version-specific rules; do not
   put `v-if` on the same element as a `v-for` unless the version permits it.
3. Use `v-show` only when the element should remain in the DOM.
4. Keep keys stable and independent of array positions.
5. Avoid inline object creation in hot paths unless profiling justifies it.
6. Use `v-memo` only for a measured optimization and with a valid dependency
   list.
7. Keep accessibility attributes on semantic elements.
8. Do not mutate props from template expressions.

## 10. Domain-Specific Anti-Patterns

### 10.1 Global Mutable State

BAD:

```ts
export const state = reactive({ user: null, draft: "" });
```

GOOD:

```ts
export function useSessionStore() {
  const session = ref<Session | null>(null);
  return { session };
}
```

### 10.2 Watcher Fetch Loop

BAD:

```ts
watch(query, async value => {
  results.value = await search(value);
});
watch(results, () => { query.value = results.value[0]?.term ?? ""; });
```

GOOD:

```ts
const results = ref<SearchResult[]>([]);
const requestId = ref(0);
watch(query, async value => {
  const current = ++requestId.value;
  const next = await search(value);
  if (current === requestId.value) results.value = next;
});
```

### 10.3 Prop Mutation in a Child

BAD:

```vue
<script setup lang="ts">
const props = defineProps<{ count: number }>();
function increment() { props.count += 1; }
</script>
```

GOOD:

```vue
<script setup lang="ts">
const props = defineProps<{ count: number }>();
const emit = defineEmits<{ increment: [] }>();
</script>
<button @click="emit('increment')">{{ count }}</button>
```

## 11. Response to Violation

If a previous response violated this file, use this structure:

```text
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

Name the violated rule and show the correction. Do not defend the old code.
