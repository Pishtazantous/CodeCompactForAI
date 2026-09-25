---
id: 02-vue-anti-slop
title: "Vue Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-frontend-anti-slop]
category: domain
domain_type: framework
version: 2
---

# Vue Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`,
`domains/framework/02-architecture-anti-slop.md`, and
`domains/delivery/02-frontend-anti-slop.md`. Rules already covered
in those files are NOT repeated here.

This file covers rules specific to Vue 3: `<script setup>`,
reactivity, props and emits, slots, `provide`/`inject`, template
discipline, and lifecycle. It does NOT cover framework-agnostic
frontend rules (see `02-frontend-anti-slop.md`), architecture rules
(see `02-architecture-anti-slop.md`), TypeScript rules (see
`02-typescript-anti-slop.md`), or Nuxt-specific rules (see
`02-nuxt-anti-slop.md`).

Vue's reactivity model differs from React's. Rules from React (hooks
ordering, dependency arrays, memoization) do not apply and must not
be carried over. This file describes Vue on its own terms.

## 1. Stack Assumptions

This layer assumes:

- Vue 3.4 or later.
- Composition API with `<script setup>`.
- Vite or another modern bundler.
- TypeScript when the project uses it.

If the project uses Vue 2 or the Options API, treat those as
legacy. Do not migrate without instruction. Rules in this file
apply to new Composition API code; existing Options API code
follows its own style.

## 2. Framework Lifecycle Contracts

Vue enforces four contracts on the developer. Every rule below
enforces one or more of these.

### 2.1 Setup Runs Once

The `<script setup>` block runs once per component instance, before
the first render. It does not re-run on state changes.

### 2.2 Reactivity Tracks at Access Time

Vue's reactivity tracks property access during render, not
declaration. A value read during render is reactive; a value copied
into a local variable during setup is not, unless it is a ref or
the reactive object is used directly.

### 2.3 Effects Run After Render

`watch`, `watchEffect`, and lifecycle hooks run after the component
renders. They do not block render.

### 2.4 Template Is Reactive

The template re-evaluates when any reactive value it reads changes.
A template that reads no reactive values does not re-render.

## 3. Component Structure

### 3.1 Single-File Components

Every component is a `.vue` file with `<script setup>`, `<template>`,
and optionally `<style scoped>`.

```vue
<script setup lang="ts">
import { ref } from "vue";
const count = ref(0);
</script>

<template>
  <button @click="count++">{{ count }}</button>
</template>

<style scoped>
button { padding: 0.5rem 1rem; }
</style>
```

Splitting a component into three files (`template.vue`,
`script.ts`, `style.css`) is possible but unusual. Match the
project.

### 3.2 Fixed Block Order

`<script setup>` first, `<template>` second, `<style scoped>` last.
The order is convention; keeping it consistent reduces cognitive
load.

### 3.3 Component File Naming

Two conventions exist: `PascalCase.vue` (`UserCard.vue`) and
`kebab-case.vue` (`user-card.vue`). Pick one per project and use it
everywhere. Both are common; consistency matters more than the
choice.

### 3.4 Props With `defineProps`

```vue
<script setup lang="ts">
interface Props {
  title: string;
  count?: number;
}
const props = defineProps<Props>();
</script>
```

Use the type-only form in TypeScript projects. The runtime form
(`defineProps({ title: String })`) is for JavaScript projects.

### 3.5 Defaults With `withDefaults`

```vue
<script setup lang="ts">
const props = withDefaults(defineProps<Props>(), {
  count: 0,
});
</script>
```

Without defaults, an optional prop is `undefined` at runtime even
if the type says otherwise.

### 3.6 Emits With `defineEmits`

```vue
<script setup lang="ts">
const emit = defineEmits<{
  submit: [value: string];
  cancel: [];
}>();
</script>
```

Every event the component emits is declared. Undeclared events
appear as fallthrough attributes and confuse consumers.

### 3.7 `defineModel` for `v-model`

Vue 3.4+:

```vue
<script setup lang="ts">
const model = defineModel<string>();
</script>

<template>
  <input v-model="model" />
</template>
```

Replaces the manual `props.modelValue` plus
`emit("update:modelValue")` boilerplate.

### 3.8 Expose Only What Is Needed

```vue
<script setup lang="ts">
function focus() { /* ... */ }
defineExpose({ focus });
</script>
```

The parent uses a template ref to call `focus()`. Expose the
minimum surface.

## 4. Reactivity

### 4.1 `ref` for Primitives, `reactive` for Objects

`ref` wraps a single value (primitive or object) and requires
`.value` in script. `reactive` wraps an object and does not.

Prefer `ref` for consistency. `reactive` loses reactivity when
destructured.

### 4.2 No Destructuring `reactive`

BAD:
```typescript
const state = reactive({ count: 0, name: "" });
const { count } = state; // count is a plain number, not reactive
```

GOOD:
```typescript
const state = reactive({ count: 0, name: "" });
// Use state.count directly, or:
const { count } = toRefs(state);
```

### 4.3 `computed` for Derived Values

BAD:
```typescript
const fullName = ref("");
watch([first, last], () => {
  fullName.value = `${first.value} ${last.value}`;
});
```

GOOD:
```typescript
const fullName = computed(() => `${first.value} ${last.value}`);
```

A `watch` that only updates a `ref` from other refs is a
`computed` in disguise. It also causes an extra render.

### 4.4 `computed` Is Read-Only by Default

To allow writes, provide a setter:

```typescript
const fullName = computed({
  get: () => `${first.value} ${last.value}`,
  set: (value) => {
    [first.value, last.value] = value.split(" ");
  },
});
```

Writable computed is appropriate for a value with a natural
inverse. It is not a replacement for methods.

### 4.5 `watch` Over `watchEffect` When the Source Is Known

`watch` takes an explicit source. `watchEffect` auto-tracks.
Explicit sources are clearer and prevent accidental dependencies.

BAD:
```typescript
watchEffect(() => {
  if (user.value) loadOrders(user.value.id);
});
```

GOOD:
```typescript
watch(() => user.value?.id, (id) => {
  if (id) loadOrders(id);
});
```

### 4.6 Never Watch to Derive

Any `watch` whose only side effect is `someRef.value = ...` is a
`computed`. See 4.3.

### 4.7 `deep: true` Only When Necessary

Deep watching a large object re-checks every nested property on
every change. It is expensive.

BAD:
```typescript
watch(bigState, () => { /* ... */ }, { deep: true });
```

GOOD: Watch a specific field, or use `computed` to extract the
value.

### 4.8 `immediate: true` When Initial State Matters

A `watch` without `immediate` does not fire on the initial value.
If the handler must run on mount, use `immediate: true` or
`watchEffect`.

### 4.9 No Reactive Mutation Across Boundaries

A child component that mutates a prop (an object passed from the
parent) is a bug in the parent-child contract. Emit an event or use
`v-model`. See 8.5.

## 5. Template Discipline

### 5.1 `v-if` vs `v-show`

- `v-if` creates/destroys the element.
- `v-show` toggles `display: none`.

Use `v-if` for conditions that change rarely (route-specific UI,
auth state). Use `v-show` for frequent toggles (dropdowns, tabs).

### 5.2 `:key` on Every `v-for`

BAD:
```vue
<li v-for="(item, i) in items" :key="i">{{ item.name }}</li>
```

GOOD:
```vue
<li v-for="item in items" :key="item.id">{{ item.name }}</li>
```

Index as key is acceptable only when the list is static. Any
reorder, insert, or delete breaks the reconciliation.

### 5.3 No `v-if` and `v-for` on the Same Element

Vue 3 evaluates `v-if` before `v-for` on the same element, so the
`v-if` cannot see the loop variable.

BAD:
```vue
<li v-for="item in items" v-if="item.active">{{ item.name }}</li>
```

GOOD:
```vue
<template v-for="item in items" :key="item.id">
  <li v-if="item.active">{{ item.name }}</li>
</template>
```

Or filter with a `computed`.

### 5.4 No Complex Expressions in Template

BAD:
```vue
{{ items.filter(i => i.active).map(i => i.name).join(", ") }}
```

GOOD:
```vue
{{ activeNames }}
```
```typescript
const activeNames = computed(() =>
  items.value.filter(i => i.active).map(i => i.name).join(", ")
);
```

Templates run on every render. Complex expressions there are hard
to read and easy to duplicate.

### 5.5 `v-model` on Components Uses `defineModel`

See 3.7. Do not reimplement `modelValue` manually unless the
project's Vue version predates `defineModel`.

### 5.6 No `v-html` on Untrusted Content

BAD:
```vue
<div v-html="userContent" />
```

GOOD:
```vue
<div v-html="sanitizedContent" />
```
with `sanitizedContent = DOMPurify.sanitize(userContent)`.

`v-html` bypasses Vue's escaping. XSS follows.

### 5.7 Short, Single-Concern Templates

A template over 100 lines is doing too much. Extract a
sub-component.

## 6. Slots and Composition

### 6.1 Named Slots Over Conditional Props

BAD:
```vue
<Card :showHeader="true" :title="t" :showFooter="true" />
```

GOOD:
```vue
<Card>
  <template #header>{{ t }}</template>
  Body content
  <template #footer>...</template>
</Card>
```

Slot-based composition lets the caller decide the layout.

### 6.2 Fallback Content in Slots

```vue
<slot name="header">Default header</slot>
```

Every slot has a sensible fallback so the component works without
the caller providing it.

### 6.3 Scoped Slots for Data Transfer

```vue
<slot :user="user" :onSelect="handleSelect" />
```

Consumers destructure the slot props:

```vue
<UserList v-slot="{ user, onSelect }">
  <div @click="onSelect(user)">{{ user.name }}</div>
</UserList>
```

### 6.4 `$slots` for Conditional Layout

```vue
<header v-if="$slots.header">
  <slot name="header" />
</header>
```

Do not render an empty wrapper when the slot is not provided.

## 7. Provide / Inject

### 7.1 For Dependency Passing, Not Global State

`provide`/`inject` passes dependencies down a component tree. It is
not a global store. Global state belongs in Pinia (or the project's
store).

### 7.2 Typed Injection Keys

```typescript
import type { InjectionKey, Ref } from "vue";

export const userKey: InjectionKey<Ref<User | null>> = Symbol("user");
```

Provide:

```typescript
provide(userKey, user);
```

Inject:

```typescript
const user = inject(userKey, ref(null));
```

### 7.3 Default Values

`inject` returns `undefined` if no provider exists. Always provide
a default, or throw a clear error if the injection is required.

```typescript
const user = inject(userKey);
if (!user) throw new Error("userKey not provided");
```

### 7.4 Provide Refs, Not Values

BAD:
```typescript
provide("theme", theme.value); // static value, not reactive
```

GOOD:
```typescript
provide("theme", theme); // ref stays reactive
```

### 7.5 Read-Only Injections When Possible

If consumers should not mutate the provided value, provide a
`readonly()` wrapper:

```typescript
provide(userKey, readonly(user));
```

## 8. Props and Events

### 8.1 Props Are Read-Only

BAD:
```vue
<script setup>
props.title = "New";
</script>
```

GOOD: Emit an event, or use `defineModel`.

Vue's prop system is one-way. Mutation is a contract violation.

### 8.2 Array and Object Props Are Shared by Reference

A parent passing an object prop shares the reference. If the child
mutates it, the parent sees the change. This is not reactivity; it
is aliasing.

If the child needs a local copy, copy it explicitly in a `ref`.

### 8.3 Emit Names Are kebab-case in Template, camelCase in Script

```vue
<script setup>
emit("updateUser", user); // camelCase in script
</script>

<template>
  <Child @update-user="onUpdate" /> <!-- kebab-case in template -->
</template>
```

Vue normalizes both. Pick one convention and use it consistently.

### 8.4 Declare All Emitted Events

An event not declared in `defineEmits` falls through to the root
element as a native listener. This causes subtle bugs and a Vue
warning.

### 8.5 No Fallthrough for Known Attributes

Vue's attribute fallthrough is convenient but hides intent. If the
child uses `inheritAttrs: false`, document which attributes it
handles.

## 9. Lifecycle

### 9.1 `onMounted` for DOM and Setup

`onMounted` runs after the component's DOM is created. Use it for
DOM measurements, third-party library initialization, and
subscriptions.

Do not use it for data that could be fetched before render (see
`02-frontend-anti-slop.md`).

### 9.2 `onUnmounted` for Cleanup

Every subscription, timer, or listener set up in `onMounted` (or
`<script setup>`) is cleaned up in `onUnmounted`.

BAD:
```typescript
onMounted(() => {
  window.addEventListener("resize", onResize);
});
```

GOOD:
```typescript
onMounted(() => {
  window.addEventListener("resize", onResize);
});
onUnmounted(() => {
  window.removeEventListener("resize", onResize);
});
```

### 9.3 `<Suspense>` for Top-Level `await`

`<script setup>` with top-level `await` requires a parent
`<Suspense>` boundary. Without it, the component does not render.

### 9.4 `<KeepAlive>` for Route State

`<KeepAlive>` preserves component state across route changes. Use
it for tabs and wizards. Do not use it for pages that must reset.

## 10. Performance

### 10.1 `v-memo` Only for Proven Hot Paths

`v-memo` skips re-rendering when the dependency array is unchanged.
It is powerful but easy to misuse. Use it only after profiling
shows a hot render.

### 10.2 `v-once` for Truly Static Content

`v-once` renders once and never updates. Use it for content that
genuinely never changes. Do not use it as a shortcut.

### 10.3 `shallowRef` for Large Opaque Objects

For a large object whose internal changes do not need reactivity
(a parsed document, a non-Vue class instance), use `shallowRef` or
`shallowReactive`. Deep reactivity on a large object is expensive.

### 10.4 `computed` Caching

`computed` caches its value until dependencies change. A method
call in the template re-runs on every render. Prefer `computed`
for derived values used in templates.

### 10.5 `v-for` With `:key` Is Not Optional

See 5.2. A missing or unstable key causes full re-renders of the
list.

### 10.6 Lazy Components

For heavy components not needed on first render, use
`defineAsyncComponent`:

```typescript
const HeavyChart = defineAsyncComponent(() => import("./HeavyChart.vue"));
```

Do not lazy-load a small component; the network round trip costs
more than the code saves.

## 11. Anti-Patterns

### 11.1 Destructuring `reactive`

Covered in 4.2. The destructured values are not reactive.

### 11.2 `watch` for Derived State

Covered in 4.3. Use `computed`.

### 11.3 Index as `:key`

Covered in 5.2.

### 11.4 `v-if` and `v-for` on Same Element

Covered in 5.3.

### 11.5 Prop Mutation

Covered in 8.1.

### 11.6 `this` in `<script setup>`

`this` is `undefined` in `<script setup>`. Use refs and props.

### 11.7 Mixing Options API and Composition API

A component with both `data()` and `<script setup>` confuses tooling
and readers. One style per component.

### 11.8 Module-Scope `ref` in a `.vue` File

BAD:
```vue
<script setup>
import { ref } from "vue";
const users = ref([]); // shared across all instances
</script>
```

GOOD: A Pinia store, or `provide`/`inject`, or declare inside the
setup scope.

Module-level refs in a `.vue` file are shared across every instance
of the component. This is almost never intended.

### 11.9 `computed` With Side Effects

A `computed` that mutates state or performs I/O is a bug. Use
`watch`.

### 11.10 `nextTick` for Arbitrary Delays

`nextTick` waits for the DOM to update. It is not a general-purpose
delay. Using it as one causes race conditions.

### 11.11 Template Refs Without `ref(null)`

BAD:
```typescript
let inputEl;
onMounted(() => { inputEl.value.focus(); });
```

GOOD:
```typescript
const inputEl = ref<HTMLInputElement | null>(null);
onMounted(() => { inputEl.value?.focus(); });
```

Without `ref(null)`, the ref is not reactive and is not assigned by
the template.

### 11.12 `v-html` With Untrusted Input

Covered in 5.6.

### 11.13 Global State in Module Scope

Covered in 11.8.

### 11.14 `watch` Without `immediate` When Initial Value Matters

A watch that must run on mount without `immediate: true` never runs.

### 11.15 Multiple Watches on the Same Source

Combine into one watch, or use `watchEffect`.

### 11.16 `defineProps` Without Defaults for Optional Props

An optional prop without a default is `undefined` at runtime even
if the type says `number`. Use `withDefaults`.

### 11.17 Emitting Undeclared Events

Covered in 8.4.

### 11.18 Slot Content Without Fallback

Covered in 6.2.

### 11.19 `<router-view>` Without `:key`

A `<router-view>` without a `:key` reuses the component instance
across routes with the same name. This is usually correct but
occasionally wrong. Be aware.

### 11.20 `v-model` on a Read-Only Computed

A `computed` without a setter cannot be used with `v-model`. This
throws at runtime.

### 11.21 Missing `scoped` on Styles

A `<style>` without `scoped` leaks globally. Use `scoped` by
default. Deep-scoping (`:deep()`) is opt-in.

### 11.22 `!important` in Component Styles

If `!important` is needed, the specificity is wrong. Fix the cause
or use `:deep()` instead.

### 11.23 Direct Store Access Without Setup

Pinia stores must be called inside `setup` or another store action.
Calling a store outside setup loses reactivity.

### 11.24 `watchEffect` for a Known Source

Covered in 4.5. Use `watch` when the source is known.

### 11.25 Deep Watching Large State

Covered in 4.7.

### 11.26 `reactive` for a Single Value

BAD:
```typescript
const count = reactive({ value: 0 });
```

GOOD:
```typescript
const count = ref(0);
```

`reactive` is for objects, not for wrapping a single value.

### 11.27 Replacing the Whole `reactive` Object

Replacing a `reactive` object's reference loses reactivity:

BAD:
```typescript
let state = reactive({ count: 0 });
state = reactive({ count: 1 }); // the original proxy is lost
```

Use `ref` for a value that is replaced, or mutate the properties
of the reactive object.

### 11.28 `v-for` Without a Stable Parent Key

A `<template v-for>` needs a `:key` on the template tag, not on the
child, when the child is conditional. See 5.3.

### 11.29 `defineExpose` With Too Much

Exposing every method and property invites the parent to reach in.
Expose the minimum.

### 11.30 Forgetting `<Suspense>` Around Async Setup

A component with top-level `await` in `<script setup>` does not
render without a parent `<Suspense>`.

## 12. Response to Violation

If a previous response violated a rule here:

```
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

No justification. No apology paragraph. Fix and move on.
