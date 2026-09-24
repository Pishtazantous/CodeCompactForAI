---
id: 02-nextjs-anti-slop
title: "Next.js Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-frontend-anti-slop, 02-react-anti-slop]
category: domain
domain_type: framework
version: 1
---
# Next.js Anti-Slop Layer

Layered under the master, architecture, frontend, and React layers. This file
adds rules for the App Router, server components, server actions, caching, and
route boundaries. General security, output, and architecture rules remain in
their owning layers.

## 1. Stack Assumptions

1. Use the App Router for new applications unless the repository already
   standardizes on the Pages Router.
2. Read the installed Next.js version before using version-gated APIs.
3. Treat the file system route tree as the public routing contract.
4. Keep server-only secrets out of client modules and client bundles.
5. Confirm runtime, deployment adapter, and cache configuration before changing
   data-fetching behavior.
6. Use the repository's existing loading, error, and not-found boundaries.
7. Never add a second router, state library, or data-fetching library.
8. Keep route modules small enough that their data and presentation boundaries
   remain visible.

## 2. Component Discipline

1. Default to Server Components; add `"use client"` only at the smallest
   interactive boundary.
2. A client module must justify browser APIs, event handlers, or client state.
3. Pass serializable data across the server/client boundary.
4. Keep secrets, database handles, and server-only SDKs behind server modules.
5. Compose route layouts around pages; do not duplicate navigation in every
   page.
6. Keep layouts stable when their children can navigate independently.
7. Use `loading.tsx`, `error.tsx`, and `not-found.tsx` for the states they own.
8. Do not place a client provider around the entire application by default.
9. Name route files and exported components after their route responsibility.
10. Use dynamic imports for heavy client features only after measuring the
    cost of loading them on every visit.

## 3. Server and Client Boundaries

BAD:

```tsx
"use client";
import { db } from "@/server/db";

export function SaveButton({ id }: { id: string }) {
  return <button onClick={() => db.user.update({ where: { id } })}>Save</button>;
}
```

GOOD:

```tsx
import { updateUserName } from "@/app/users/actions";

export function SaveButton({ id }: { id: string }) {
  return <form action={updateUserName.bind(null, id)}><button>Save</button></form>;
}
```

1. Server actions are server-side entry points, not authorization.
2. Authenticate and authorize every action independently.
3. Revalidate the exact route or tag affected by a mutation.
4. Return serializable action results; do not return database entities.
5. Validate action input at the server boundary.
6. Use progressive enhancement when the form can complete without JavaScript.
7. Do not call a server action from render or use it as a data-fetching API.
8. Mark server-only dependencies with the repository's server boundary.

## 4. Rendering and Lifecycle

1. Keep pure layout and page composition free of browser globals.
2. Put browser-only initialization in a client component or effect with cleanup.
3. Never read cookies, headers, or search params when the route does not need
   request-specific data.
4. Select dynamic APIs deliberately; each one changes the rendering boundary.
5. Keep Suspense boundaries near the slow section, not around the entire page.
6. Do not use an effect to copy server data into client state unless the client
   needs a durable local interaction.
7. Stream slow data behind a meaningful loading state.
8. Handle aborted requests and stale navigations without showing stale errors.
9. Do not use `window`, `document`, or `localStorage` during server rendering.
10. Preserve accessibility and focus behavior when a boundary is replaced.

## 5. Routing Discipline

1. Use route groups, parallel routes, and intercepting routes only for a
   declared UX requirement.
2. Keep route params validated before they reach application code.
3. Use `generateMetadata` or the repository's metadata convention for pages
   that need it.
4. Keep route handlers small: authenticate, validate, invoke use case, map
   response.
5. Return an explicit response status for errors and redirects.
6. Do not use a route handler as a substitute for a server action when the
   operation is a page mutation.
7. Preserve cache semantics when changing search params or cookies.
8. Test direct loads, refreshes, back navigation, and failed navigations.
9. Do not navigate during render; use links, redirects, or event handlers.
10. Keep nested layouts from owning data that belongs to the page.

## 6. Data Fetching and Cache Rules

1. Use the repository's configured fetch wrapper and its error policy.
2. Make the cache choice explicit: static, dynamic, revalidated, or no store.
3. Do not invent a cache key or duplicate server data in a global store.
4. Deduplicate identical requests through the supported request memoization
   mechanism.
5. Use tagged invalidation for shared data and path revalidation for route
   output.
6. Never cache authenticated responses across users.
7. Avoid cache reads for mutations; write through the server boundary.
8. Keep pagination, filtering, and authorization server-side when sensitive.
9. Set bounded retries only for transient failures, with backoff.
10. Do not silently return stale data when freshness is a business invariant.

## 7. Domain-Specific Anti-Patterns

### 7.1 Client-Wrapped Data Fetching

BAD:

```tsx
"use client";
export function Page() {
  const [users, setUsers] = useState([]);
  useEffect(() => { fetch("/api/users").then(r => r.json()).then(setUsers); }, []);
  return <UserList users={users} />;
}
```

GOOD:

```tsx
import { listUsers } from "@/server/users";

export default async function Page() {
  const users = await listUsers();
  return <UserList users={users} />;
}
```

### 7.2 Uncached Personalized Data

BAD:

```ts
export default async function Account() {
  const user = await getUserFromCookie();
  return <Profile user={user} />;
}
```

GOOD:

```ts
import { noStore } from "next/cache";

export default async function Account() {
  noStore();
  const user = await getUserFromCookie();
  return <Profile user={user} />;
}
```

### 7.3 Mutation Without Invalidation

BAD:

```ts
"use server";
export async function saveProfile(input: FormData) {
  await repository.save(input);
}
```

GOOD:

```ts
"use server";
import { revalidatePath } from "next/cache";

export async function saveProfile(input: FormData) {
  await repository.save(input);
  revalidatePath("/settings/profile");
}
```

## 8. Performance Boundaries

1. Keep server components free of unnecessary client imports.
2. Avoid client waterfalls by fetching independent server data concurrently.
3. Put pagination and filtering before large serialization.
4. Use image and font optimization according to the installed Next version.
5. Do not add a client state store to server-owned data.
6. Use streaming only for genuinely slow sections.
7. Measure bundle impact before making every dependency client-side.

## 9. Response to Violation

If a previous response violated this file, use this structure:

```text
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

State only the violated rule and the correction. Do not add an apology
paragraph or unrelated explanation.
