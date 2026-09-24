---
id: 02-sveltekit-anti-slop
title: "SvelteKit Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-frontend-anti-slop, 02-svelte-anti-slop]
category: domain
domain_type: framework
version: 1
---
# SvelteKit Anti-Slop Layer

Layered under the master, architecture, frontend, and Svelte layers. This file
adds rules for load functions, form actions, server routes, hooks, and route
boundaries in SvelteKit.

## 1. Stack Assumptions

1. Read the installed SvelteKit major version before using load, action, or
   response APIs.
2. Use the repository's adapter and deployment runtime.
3. Keep server-only code under the server boundary.
4. Use SvelteKit load and action contracts instead of duplicating them in
   component effects.
5. Match the project's generated types and route conventions.
6. Keep authentication and authorization on the server.
7. Do not add a second data-fetching or form library without permission.
8. Preserve the existing route organization.

## 2. Load Functions

1. Put route reads in `load` when the data is needed for navigation or SSR.
2. Use `+page.server.ts` for secrets and privileged server reads.
3. Use `+page.ts` only when the data can safely be exposed to the browser.
4. Return a serializable shape that represents the page contract.
5. Use `depends` when a custom fetch must be invalidated for a named dependency.
6. Handle redirects and errors with the version's supported return values.
7. Do not silently convert a failed request into an empty dataset.
8. Avoid fetching in a loop and batch related data.
9. Keep parent and child load data separate and intentional.
10. Test direct loads, invalidation, and unauthorized access.

BAD:

```ts
// +page.ts
export const load = async ({ fetch, params }) => ({
  user: await fetch(`/api/users/${params.id}`).then(response => response.json()),
});
```

GOOD:

```ts
// +page.server.ts
export const load = async ({ locals, params }) => {
  const user = await locals.users.get(params.id);
  if (!user) error(404, "User not found");
  return { user };
};
```

## 3. Form Actions

1. Use a named form action for mutations owned by a route.
2. Validate form data on the server.
3. Authenticate and authorize inside the action.
4. Return structured field and form errors that the page can render.
5. Do not expose internal exception text in an action response.
6. Make a successful action redirect or invalidate the affected load data.
7. Keep action logic in an application service when it is not route-specific.
8. Make repeated submissions safe or explicitly reject them.
9. Preserve entered values after validation failure.
10. Test no-JavaScript form submission.

BAD:

```ts
export const actions = {
  save: async ({ request }) => ({ ok: true, data: await request.json() }),
};
```

GOOD:

```ts
export const actions = {
  save: async ({ request, locals }) => {
    const input = await parseProfile(request.formData());
    await locals.profiles.update(locals.user.id, input);
    return { saved: true };
  },
};
```

## 4. Server Routes and Hooks

1. Keep `+server.ts` handlers transport-focused.
2. Validate method, content type, and parameters before business logic.
3. Use hooks for request-wide concerns such as correlation IDs and session
   context, not feature logic.
4. Keep authorization decisions in the feature boundary as well as the hook when
   the resource is protected.
5. Return explicit status codes and safe error bodies.
6. Do not let hooks swallow exceptions.
7. Keep adapter-specific APIs behind a small integration module.
8. Close streams and resources on every response path.

## 5. Component Data Flow

1. Read load data as the page contract rather than copying it into a store.
2. Keep page data separate from local form state.
3. Use stores only for cross-route or shared client state.
4. Do not fetch the same resource in a component after a successful load.
5. Handle loading and error UI at the route boundary.
6. Keep navigation state server-owned when it affects authorization.
7. Use invalidation after a mutation instead of manually patching several stores.
8. Preserve a clear empty state distinct from a failed state.

## 6. SSR and Hydration

1. Avoid browser globals in component initialization.
2. Keep server data serialization explicit.
3. Do not render a different first tree based on an unpaired client check.
4. Use deterministic values for hydration-sensitive markup.
5. Hydrate only the interactive islands the product needs.
6. Test JavaScript-disabled navigation and slow responses.
7. Keep error boundaries close to route data failures.
8. Avoid duplicate client fetches of data already loaded by the server.

## 7. Routing

1. Use generated route helpers and named navigation where available.
2. Validate dynamic route segments before calling application services.
3. Use load invalidation to refresh a page after an action.
4. Keep nested layouts stable and let children own page-specific data.
5. Do not concatenate unvalidated values into URLs.
6. Test direct entry, back navigation, and error redirects.
7. Use route groups only when ownership improves.
8. Do not duplicate auth checks in a way that can drift.

## 8. Security Boundaries

1. Never import server secrets into `+page.ts` or client modules.
2. Use server load and actions for privileged reads and writes.
3. Treat cookies and request data as untrusted.
4. Apply CSRF protection through the repository's framework convention.
5. Return user-safe validation errors.
6. Do not log tokens, passwords, or private payloads.
7. Keep authorization close to the resource operation.

## 9. Domain-Specific Anti-Patterns

### 9.1 Client-Only Data Fetch

BAD:

```svelte
<script>
  import { onMount } from "svelte";
  let user;
  onMount(async () => { user = await fetch("/api/user").then(r => r.json()); });
</script>
```

GOOD:

```ts
// +page.server.ts
export const load = async ({ locals }) => ({ user: await locals.users.current() });
```

### 9.2 Action Without Authorization

BAD:

```ts
export const actions = { remove: async ({ params }) => removeItem(params.id) };
```

GOOD:

```ts
export const actions = {
  remove: async ({ params, locals }) => {
    await locals.items.removeOwned(locals.user.id, params.id);
    return { removed: true };
  },
};
```

### 9.3 Action Data Without Validation

BAD:

```ts
export const actions = {
  save: async ({ request }) => ({ ok: await saveUnchecked(await request.json()) }),
};
```

GOOD:

```ts
export const actions = {
  save: async ({ request }) => {
    const input = profileSchema.parse(await request.json());
    return { ok: await saveProfile(input) };
  },
};
```

## 10. Response to Violation

If a previous response violated this file, use this structure:

```text
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

State the violated rule and corrected code without additional commentary.
