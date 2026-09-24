---
id: 02-nuxt-anti-slop
title: "Nuxt Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-frontend-anti-slop, 02-vue-anti-slop]
category: domain
domain_type: framework
version: 1
---
# Nuxt Anti-Slop Layer

Layered under the master, architecture, frontend, and Vue layers. This file
adds Nuxt server routes, composables, runtime configuration, auto-imports,
data fetching, and rendering boundaries.

## 1. Stack Assumptions

1. Read the installed Nuxt major version before using data and server APIs.
2. Use the repository's server rendering and deployment target.
3. Keep secrets in server runtime configuration only.
4. Use the existing Vue and Nuxt state boundaries; do not add a second router.
5. Prefer Nuxt's data primitives when they match the project's version.
6. Keep page components thin and place shared behavior in composables.
7. Follow the existing directory conventions before adding a layer.
8. Do not add a server endpoint when a server action or page boundary owns the
   operation.

## 2. Components and Pages

1. Keep pages responsible for route data and composition.
2. Extract reusable UI into components with typed props and emits.
3. Use `<script setup lang="ts">` when the repository uses it.
4. Keep browser-only APIs inside client-only components or lifecycle hooks.
5. Use the project's route middleware and page transitions.
6. Do not make every component a client island; Nuxt server rendering is the
   default.
7. Keep layout, page, and component ownership explicit.
8. Handle loading, error, and empty states at the nearest useful boundary.

BAD:

```vue
<script setup>
const users = ref([]);
onMounted(async () => { users.value = await $fetch("/api/users"); });
</script>
```

GOOD:

```vue
<script setup lang="ts">
const { data: users, status, error } = await useFetch<User[]>("/api/users");
</script>
```

## 3. Runtime Configuration

1. Read public configuration through the repository's Nuxt configuration layer.
2. Keep private values in server-only configuration and validate them at startup.
3. Do not expose a database URL, signing key, or internal token to the browser.
4. Use environment names already defined by the project.
5. Do not branch on `process.env` throughout components.
6. Keep runtime configuration typed and documented.
7. Do not use a public flag to hide a server authorization decision.
8. Verify the production build does not contain private values.

## 4. Server Routes

1. Keep server routes thin: parse input, call an application function, map output.
2. Validate parameters and bodies before reaching a service.
3. Authenticate and authorize every protected endpoint.
4. Return stable status codes and error bodies.
5. Do not return internal exceptions or stack traces.
6. Keep route files aligned with domain routes, not page components.
7. Use runtime config for server dependencies.
8. Make external calls timeout-bounded and cancellation-aware.

BAD:

```ts
export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, "id");
  return db.query(`select * from users where id = ${id}`);
});
```

GOOD:

```ts
export default defineEventHandler(async (event) => {
  const id = UserId.parse(getRouterParam(event, "id"));
  return getUser(id);
});
```

## 5. Data Fetching

1. Use `useFetch` for declarative component data with Nuxt's request and key
   behavior.
2. Use `useAsyncData` when a function or promise is the natural data source.
3. Do not call both for the same request without a deliberate cache reason.
4. Set an explicit key for data used outside its first component.
5. Handle errors without turning a failed request into an empty successful state.
6. Cancel or ignore stale results when route parameters change.
7. Avoid fetching in loops; batch or paginate.
8. Keep authenticated responses out of shared public caches.
9. Use `refresh` or `clear` according to the ownership and freshness contract.
10. Do not duplicate server data in a global store.

BAD:

```vue
<script setup>
const data = ref(null);
watch(() => route.params.id, async id => { data.value = await $fetch(`/users/${id}`); }, { immediate: true });
</script>
```

GOOD:

```vue
<script setup lang="ts">
const route = useRoute();
const { data, error, status } = await useFetch(() => `/api/users/${route.params.id}`);
</script>
```

## 6. Auto-imports

1. Use Nuxt auto-imports for the symbols the project intentionally enables.
2. Do not create a local symbol with the same name and expect a silent override.
3. Keep generated import behavior visible in editor and lint configuration.
4. Do not rely on auto-imports for ambiguous third-party helpers.
5. Explicitly import symbols when ambiguity would make ownership unclear.
6. Keep auto-import configuration minimal and review it with the team.
7. Do not add a helper to the global import list for one feature.
8. Follow the repository's type-generation and build checks.

## 7. State and Reactivity

1. Keep route and server data in Nuxt data primitives.
2. Keep local UI state in the component.
3. Use shared state only when multiple distant components own the same value.
4. Do not mutate `useState` values in place without following the project's
   update contract.
5. Use `computed` for derived values.
6. Clean up event listeners, timers, and observers in the owning component.
7. Use the repository's persistence plugin instead of direct local storage.
8. Keep SSR-safe access to browser globals.

## 8. Rendering and Middleware

1. Use server rendering for content that does not need a client boundary.
2. Use route middleware for authentication or navigation policy, not data fetching.
3. Keep middleware side effects idempotent.
4. Do not navigate during setup without a documented redirect contract.
5. Define page metadata and SEO values through Nuxt's supported APIs.
6. Preserve focus and scroll behavior across route changes.
7. Avoid global CSS and plugins for a single component's behavior.
8. Test direct navigation, refresh, and failure states.

## 9. Domain-Specific Anti-Patterns

### 9.1 Secret in Public Runtime Config

BAD:

```ts
runtimeConfig: { public: { databaseUrl: process.env.DATABASE_URL } }
```

GOOD:

```ts
runtimeConfig: { databaseUrl: process.env.DATABASE_URL, public: { appName: "App" } }
```

### 9.2 Client Fetch on Every Route

BAD:

```vue
<script setup>
onMounted(() => $fetch("/api/dashboard"));
</script>
```

GOOD:

```vue
<script setup lang="ts">
const { data, status, error } = await useFetch("/api/dashboard");
</script>
```

### 9.3 Global Auto-import Sprawl

BAD:

```ts
export default defineNuxtConfig({ imports: { dirs: ["lib", "utils", "features", "components"] } });
```

GOOD:

```ts
export default defineNuxtConfig({ imports: { dirs: ["composables"] } });
```

## 10. Response to Violation

If a previous response violated this file, use this structure:

```text
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

Identify the rule and show the correction. Do not add an apology paragraph.
