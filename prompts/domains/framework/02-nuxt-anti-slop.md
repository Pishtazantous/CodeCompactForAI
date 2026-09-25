---
id: 02-nuxt-anti-slop
title: "Nuxt Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-frontend-anti-slop, 02-vue-anti-slop]
category: domain
domain_type: framework
version: 2
---

# Nuxt Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`,
`domains/framework/02-architecture-anti-slop.md`,
`domains/delivery/02-frontend-anti-slop.md`, and
`domains/framework/02-vue-anti-slop.md`. Rules already covered in
those files are NOT repeated here.

This file covers rules specific to Nuxt 3 and later: auto-imports,
data fetching composables, server routes, `runtimeConfig`, Nitro
engine, hydration, and rendering modes. It does NOT cover general
Vue rules (see `02-vue-anti-slop.md`), framework-agnostic frontend
rules (see `02-frontend-anti-slop.md`), architecture rules (see
`02-architecture-anti-slop.md`), or UI design rules (see
`04-ui-design-system.md`).

Nuxt's defining feature is the server/client boundary. Every rule in
this file exists because the codebase runs in two environments, and
code that ignores that boundary breaks in production.

## 1. Stack Assumptions

This layer assumes:

- Nuxt 3.10 or later.
- Vue 3 Composition API with `<script setup>`.
- Nitro server engine.
- TypeScript when the project uses it.

If the project uses Nuxt 2, treat it as legacy. Do not migrate
without instruction. Rules in this file apply to new Nuxt 3 code.

## 2. Framework Lifecycle Contracts

Nuxt enforces five contracts on the developer. Every rule below
enforces one or more of these.

### 2.1 Code Runs Twice

By default, a page or component renders on the server (during SSR)
and then hydrates on the client. Any code in `<script setup>` that
runs at setup time runs in both environments.

### 2.2 Hydration Must Match

The DOM produced by the server must match the DOM produced by the
client's first render. A mismatch causes a hydration error and a
re-render, losing performance and causing flicker.

### 2.3 Auto-Imports Are Global

Vue APIs, Nuxt composables, and files in `composables/`, `utils/`,
and `components/` are auto-imported. There is no explicit import
list to consult.

### 2.4 Server Routes Run on the Server Only

`server/api/*` and `server/routes/*` run in Node.js. Browser APIs
and client-only libraries are not available.

### 2.5 Configuration Is Layered

`runtimeConfig.public` is serialized to the client. Everything else
stays on the server. The boundary is enforced at build time.

## 3. Auto-Imports

### 3.1 Trust Nuxt's Auto-Imports

Nuxt auto-imports Vue APIs (`ref`, `computed`, `watch`), Nuxt
composables (`useFetch`, `useState`, `useRoute`), and files in
`composables/`, `utils/`, and `components/`.

BAD:
```typescript
import { ref } from "vue";
import { useFetch } from "#app";
```

GOOD:
```typescript
const count = ref(0);
const { data } = await useFetch("/api/users");
```

Explicit imports of auto-imported symbols are noise.

### 3.2 Auto-Import Sources Are Fixed

Only `composables/`, `utils/`, and `components/` are auto-imported.
Code in other directories requires explicit imports.

### 3.3 No Conflicting Names

Two files in `composables/` exporting the same name cause a
collision. Nuxt warns; the last one wins silently. Rename one.

### 3.4 No Auto-Imports in Server-Only Context

Server routes do not auto-import composables that depend on the
client. `useState`, `useRoute`, and similar client-aware helpers do
not work in `server/api/`.

### 3.5 Components Auto-Import Is Directory-Aware

`components/UserCard.vue` is `<UserCard />`. `components/user/Card.vue`
is `<UserCard />` as well (directory becomes prefix). Match the
project's convention.

## 4. Data Fetching

### 4.1 `useFetch` for URL-Based Fetches

```typescript
const { data, pending, error } = await useFetch("/api/users");
```

`useFetch` runs on the server during SSR and on the client during
navigation. It serializes the result into the payload so the client
does not re-fetch on hydration.

### 4.2 `useAsyncData` for Custom Fetchers

```typescript
const { data } = await useAsyncData("users", () => myCustomFetch());
```

Use when the fetcher is not a simple URL call (a GraphQL client, a
local computation wrapped in a promise).

### 4.3 Never Fetch in `onMounted`

BAD:
```vue
<script setup>
onMounted(async () => {
  const res = await fetch("/api/users");
  users.value = await res.json();
});
</script>
```

This runs only on the client and re-fetches what the server already
had. It also causes a loading flash.

GOOD:
```vue
<script setup>
const { data: users } = await useFetch("/api/users");
</script>
```

### 4.4 `await` on Setup-Time Fetches

BAD:
```vue
<script setup>
const { data } = useFetch("/api/users"); // not awaited
</script>
```

Without `await`, the SSR render completes before the data is ready.
The page renders empty, then hydrates with data.

GOOD:
```vue
<script setup>
const { data } = await useFetch("/api/users");
</script>
```

### 4.5 Unique `key` for `useAsyncData`

Two `useAsyncData` calls with the same key share cache. Use unique
keys, or pass `{ key: ... }` explicitly.

BAD:
```typescript
const { data: users } = await useAsyncData(() => fetchUsers());
const { data: posts } = await useAsyncData(() => fetchPosts());
// both use the same auto-generated key
```

GOOD:
```typescript
const { data: users } = await useAsyncData("users", () => fetchUsers());
const { data: posts } = await useAsyncData("posts", () => fetchPosts());
```

### 4.6 `lazy: true` for Non-Blocking Fetches

`useFetch` with `{ lazy: true }` does not block navigation. The
page renders immediately; data arrives later.

Use it for content below the fold or for secondary panels.

### 4.7 `server: false` for Client-Only Data

`useFetch` with `{ server: false }` skips the SSR fetch. Use for
user-specific data that is not available server-side (localStorage
preferences, geolocation).

### 4.8 `refresh` for Revalidation

After a mutation, call `refresh()` on the relevant `useFetch`:

```typescript
const { data, refresh } = await useFetch("/api/users");

async function addUser(user: User) {
  await $fetch("/api/users", { method: "POST", body: user });
  await refresh();
}
```

### 4.9 `$fetch` for Events, `useFetch` for Data

`$fetch` is for one-time fetches (event handlers, server-side logic).
`useFetch` is for data tied to a component's lifecycle.

BAD:
```vue
<button @click="loadUsers">Load</button>
<script setup>
async function loadUsers() {
  const { data } = await useFetch("/api/users"); // wrong tool
}
</script>
```

GOOD:
```typescript
async function loadUsers() {
  const data = await $fetch("/api/users");
}
```

### 4.10 `useLazyFetch` and `useLazyAsyncData`

`useLazyFetch` is `useFetch` with `{ lazy: true }`. Both are valid
spellings. Match the project.

### 4.11 No `axios` When `$fetch` Exists

Nuxt's `$fetch` is built on `ofetch`. It handles JSON, base URLs,
and interceptors. Adding `axios` duplicates functionality and adds
bundle size.

## 5. Server Routes

### 5.1 `server/api/` for HTTP Endpoints

```typescript
// server/api/users.get.ts
export default defineEventHandler(async (event) => {
  const users = await db.users.findMany();
  return users;
});
```

### 5.2 Method Suffixes

- `users.get.ts` for GET.
- `users.post.ts` for POST.
- `users/[id].delete.ts` for DELETE on a parameterized route.

The suffix determines the HTTP method. A file without a suffix
handles all methods.

### 5.3 Validate Input

```typescript
export default defineEventHandler(async (event) => {
  const body = await readValidatedBody(event, schema.parse);
  // ...
});
```

Never trust `event.body`, `getQuery(event)`, or `getRouterParam(event)`
without validation.

### 5.4 Never Expose Server Secrets

A server route has access to `process.env`. Do not return secrets to
the client. Do not include them in error messages.

### 5.5 `server/middleware/` for Cross-Cutting

Middleware runs on every server request. Keep it fast. Auth checks
and CORS belong here.

### 5.6 `server/utils/` for Shared Server Logic

Functions used by multiple server routes live here. They are
auto-imported within the server context.

### 5.7 No Client Code in Server Routes

Server routes run in Node.js. `window`, `document`, and
`localStorage` are unavailable. Browser-only libraries fail at
runtime.

### 5.8 `defineEventHandler` Always

A server route is exported via `defineEventHandler` or
`defineLazyEventHandler`. A bare async function is not recognized.

### 5.9 Error Handling With `createError`

```typescript
throw createError({
  statusCode: 404,
  statusMessage: "User not found",
});
```

`createError` produces a consistent error response. A raw `throw`
leaks the stack in development and is opaque in production.

### 5.10 No Blocking Work in Server Routes

A CPU-heavy loop blocks the Node.js event loop for all concurrent
requests. Offload to a worker or a background job.

## 6. Runtime Configuration

### 6.1 `runtimeConfig` for Secrets

```typescript
export default defineNuxtConfig({
  runtimeConfig: {
    apiSecret: "", // server-only
    public: {
      apiBase: "/api",
    },
  },
});
```

Top-level keys are server-only. `public` is serialized to the client.

### 6.2 `useRuntimeConfig` in Code

```typescript
const config = useRuntimeConfig();
config.public.apiBase; // available both sides
config.apiSecret;      // server-only, undefined on client
```

Accessing a server-only value from the client returns `undefined`,
not an error. Treat missing values as a bug.

### 6.3 Never Put Secrets in `public`

BAD:
```typescript
runtimeConfig: {
  public: {
    apiSecret: "sk-...", // serialized to the client bundle
  },
}
```

GOOD:
```typescript
runtimeConfig: {
  apiSecret: process.env.API_SECRET,
}
```

The `public` section is written into the client JavaScript. It is
public.

### 6.4 Environment Variables at Runtime

`runtimeConfig` reads from environment variables with the `NUXT_`
prefix at runtime. Do not bake values into the build.

## 7. Rendering Modes

### 7.1 SSR by Default

Nuxt renders on the server and hydrates on the client. This is the
default and the recommended mode for most content.

### 7.2 `<ClientOnly>` for Browser-Only Content

```vue
<ClientOnly>
  <BrowserOnlyComponent />
</ClientOnly>
```

Use for content that depends on `window`, `document`, or a
third-party script that fails during SSR.

### 7.3 `process.client` / `process.server` for Logic

```typescript
if (process.client) {
  window.localStorage.setItem("key", value);
}
```

Use for logic, not for rendering. Rendering differences cause
hydration mismatches.

### 7.4 Common Hydration Mismatches

- `Date.now()` or `Math.random()` in render.
- `window` or `localStorage` access during setup.
- Different content server-side vs client-side.
- Non-deterministic iteration order.

Fix by moving the value to `onMounted`, wrapping in `<ClientOnly>`,
or ensuring the value is stable.

### 7.5 `ssr: false` for SPA Mode

Set in `nuxt.config.ts` for a pure SPA. Rare. Prefer SSR for
content and SPA for authenticated apps where SEO does not matter.

### 7.6 Prerender Static Routes

```typescript
nitro: {
  prerender: {
    routes: ["/", "/about", "/pricing"],
  },
}
```

Prerendering is faster than SSR for static content.

### 7.7 Route Rules for Per-Route Rendering

```typescript
routeRules: {
  "/": { prerender: true },
  "/dashboard/**": { ssr: false },
  "/api/**": { cors: true },
}
```

Different routes can render differently. This is Nuxt's hybrid
rendering.

## 8. Middleware

### 8.1 Route Middleware

`middleware/auth.ts` runs before a route. Use for auth checks.

```typescript
export default defineNuxtRouteMiddleware((to) => {
  const auth = useAuthStore();
  if (!auth.isAuthenticated) return navigateTo("/login");
});
```

### 8.2 Global Middleware

`middleware/*.global.ts` runs on every route. Use sparingly. A
global middleware that does heavy work slows every navigation.

### 8.3 Server Middleware

`server/middleware/` runs on every server request. Different from
route middleware. Use for CORS, auth headers, request logging.

### 8.4 No Heavy Work in Middleware

Route middleware runs on every matching navigation, both server
and client. Database queries there slow every page.

### 8.5 Return, Do Not Fall Through

A route middleware that should redirect returns `navigateTo(...)`.
Returning nothing continues the navigation.

## 9. State Management

### 9.1 `useState` for SSR-Safe State

```typescript
const user = useState<User | null>("user", () => null);
```

`useState` is Nuxt's SSR-friendly state. It serializes to the
payload and hydrates on the client.

### 9.2 No Module-Scope `ref` for SSR State

BAD:
```typescript
// composables/useUser.ts
const user = ref<User | null>(null); // shared across all requests
export function useUser() { return user; }
```

Module-scope refs are shared across every request on the server.
One user's data leaks to another. This is a security issue.

GOOD:
```typescript
export function useUser() {
  return useState<User | null>("user", () => null);
}
```

### 9.3 Pinia for Complex State

For state with actions, getters, and multiple related slices, use
Pinia. It is Nuxt-aware and handles SSR correctly.

### 9.4 No Client-Only State in Setup

`localStorage` and `sessionStorage` are unavailable during SSR.
Access them in `onMounted` or with `<ClientOnly>`.

## 10. SEO and Metadata

### 10.1 `useHead` for Static Metadata

```typescript
useHead({
  title: "User Profile",
  meta: [{ name: "description", content: "..." }],
});
```

### 10.2 `useSeoMeta` for SEO Fields

```typescript
useSeoMeta({
  title: "User Profile",
  ogTitle: "User Profile",
  description: "...",
  ogImage: "https://example.com/og.png",
});
```

`useSeoMeta` validates the field names and produces correct OG and
Twitter tags.

### 10.3 `definePageMeta` for Route Metadata

```typescript
definePageMeta({
  middleware: ["auth"],
  layout: "dashboard",
});
```

`definePageMeta` is a compiler macro. It must be called at the top
level of a page component, not inside a function.

### 10.4 `metadataBase` for Absolute URLs

Set `app.head.meta` or `app.head.link` in `nuxt.config.ts` for
canonical URLs and OG images.

## 11. Assets and Images

### 11.1 `~/assets/` for Build-Processed Assets

Assets in `~/assets/` are processed by Vite (hashed, optimized).
`~/public/` files are served as-is.

### 11.2 `public/` for Static Files

`public/favicon.ico` is served at `/favicon.ico`. Files here are
not processed.

### 11.3 Nuxt Image Module

Use `@nuxt/image` for responsive images:

```vue
<NuxtImg src="/hero.jpg" width="800" height="600" alt="" />
```

It handles optimization, lazy loading, and CLS prevention.

## 12. Auto-Import Collisions

### 12.1 No File Named Like a Vue API

A file `composables/ref.ts` shadows Vue's `ref`. Never do this.

### 12.2 No Component Named Like an HTML Element

A component `Button.vue` is fine. A component `Link.vue` may
conflict with `<NuxtLink>` in templates. Use specific names.

### 12.3 Prefix Composables When Ambiguous

`composables/useUser.ts` is fine. `composables/user.ts` may not be.
Composables start with `use`.

## 13. Anti-Patterns

### 13.1 `onMounted` for Data Fetching

Covered in 4.3.

### 13.2 `fetch` Instead of `useFetch`

Covered in 4.1.

### 13.3 Hydration Mismatch

Covered in 7.4.

### 13.4 Secrets in `public` Runtime Config

Covered in 6.3.

### 13.5 Auto-Import Name Collision

Two files in `composables/` exporting the same name.

### 13.6 `definePageMeta` in a Child Component

`definePageMeta` only works in pages. Using it elsewhere is silently
ignored.

### 13.7 Missing `key` on `useAsyncData`

Covered in 4.5.

### 13.8 `useAsyncData` Without `await`

Covered in 4.4.

### 13.9 Client-Only Code During SSR

Covered in 7.4.

### 13.10 Global Middleware for Auth

Auth belongs in per-route middleware. A global middleware runs on
public routes too.

### 13.11 No Error Page

Missing `error.vue` at the app root. Errors fall back to a generic
page.

### 13.12 Missing `<NuxtLayout>` in `app.vue`

A custom `app.vue` without `<NuxtLayout>` ignores layouts. Layouts
still load but are not rendered.

### 13.13 Vue `ref` Instead of Nuxt `useState`

Covered in 9.2.

### 13.14 Module-Scope Mutable State

Covered in 9.2. This is a security issue: state leaks between
requests.

### 13.15 Ignoring `useHead`

A page without `useHead` or `useSeoMeta` has no title or OG tags.

### 13.16 Missing `<NuxtLink>` Prefetch

`<NuxtLink>` prefetches on visibility. Disabling prefetch globally
slows navigation.

### 13.17 Nested `useFetch` in Loops

A `useFetch` inside `v-for` fetches per item. Fetch a batch instead.

### 13.18 Server Routes Without Validation

Covered in 5.3.

### 13.19 No Error Handling in Server Routes

A server route that throws a raw error produces an opaque 500.
Use `createError`.

### 13.20 Not Using Nuxt Modules

Nuxt has official modules for image, font, content, SEO, PWA.
Reinventing them wastes effort and bundle size.

### 13.21 `process.client` in Render

`process.client` inside a template causes hydration mismatch.
Use `<ClientOnly>` for conditional rendering.

### 13.22 `onMounted` for Local Storage

Reading `localStorage` in `onMounted` is fine for logic but not for
values that shape the initial render. Use `<ClientOnly>` or accept
the post-hydration update.

### 13.23 No TypeScript Config

Nuxt supports TypeScript. A `.js` `nuxt.config` misses type
checking for the config itself.

### 13.24 Ignoring Nitro Presets

Deploying to a platform without the right Nitro preset causes
runtime failures. Set `nitro.preset` or use the platform's adapter.

### 13.25 No `app.config.ts` for Public Build-Time Config

`app.config.ts` is for reactive build-time config that is the same
on both sides. `runtimeConfig` is for runtime config. Use each for
its purpose.

### 13.26 `$fetch` in Setup Without `await`

`$fetch` in setup without `await` produces a promise that resolves
after render. Use `useFetch`/`useAsyncData` instead.

### 13.27 Duplicate Fetches

Two components fetch the same data with different keys. Use
`useAsyncData` with a shared key, or a Pinia store.

### 13.28 `useRoute` in `server/api`

`useRoute` is a client-aware composable. In server routes, use
`getQuery`, `getRouterParam`, and `readBody`.

### 13.29 `ref` From `vue` in a Server Route

Vue refs do not work on the server. Server routes return plain
values.

### 13.30 Manual `useState` Serialization

`useState` handles serialization. Do not call `JSON.stringify`
manually on state passed to the payload.

## 14. Response to Violation

If a previous response violated a rule here:

```
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

No justification. No apology paragraph. Fix and move on.
