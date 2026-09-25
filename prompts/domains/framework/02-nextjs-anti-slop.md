---
id: 02-nextjs-anti-slop
title: "Next.js Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-frontend-anti-slop, 02-react-anti-slop]
category: domain
domain_type: framework
version: 2
---

# Next.js Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`,
`domains/framework/02-architecture-anti-slop.md`,
`domains/delivery/02-frontend-anti-slop.md`, and
`domains/framework/02-react-anti-slop.md`. Rules already covered in
those files are NOT repeated here.

This file covers rules specific to Next.js 14+ with the App Router:
Server and Client Components, data fetching, caching, route
handlers, server actions, metadata, and rendering modes. It does NOT
cover general React rules (see `02-react-anti-slop.md`), generic
frontend rules (see `02-frontend-anti-slop.md`), state management
(see `02-state-anti-slop.md`), or API data-fetching patterns that
apply to all frameworks (see `02-api-data-anti-slop.md`).

Next.js's defining feature is the server/client boundary. Every
rule in this file exists because the code runs in two environments,
and code that ignores the boundary breaks in production.

## 1. Stack Assumptions

This layer assumes:

- Next.js 14 or later with the App Router.
- React 18 or later.
- Server Components as the default.
- TypeScript when the project uses it.

### Version Applicability

- **Minimum version**: Next.js 14.0.
- **Features used in this file that require specific versions**:
  - App Router: Next.js 13.4+ (stable).
  - `async` `params` and `searchParams`: Next.js 15+.
  - Server Actions: Next.js 14+ (stable).
  - Partial Prerendering: Next.js 14+ (experimental) / 15+
    (preview).
  - `after()` from `next/server`: Next.js 15+.
- **If the project uses the Pages Router**: treat the routing,
  data-fetching, and metadata sections as legacy. Do not migrate
  without instruction.

## 2. Framework Lifecycle Contracts

Next.js enforces six contracts on the developer. Every section below
enforces one or more of these.

### Contract 1: Server First

Every component is a Server Component unless marked `"use client"`.
Server Components render on the server, ship no JavaScript to the
client, and can access the database directly.

### Contract 2: Explicit Client Boundary

The `"use client"` directive marks a boundary. Everything imported
by that file becomes client-side JavaScript. The directive
propagates through the import graph.

### Contract 3: Hydration Must Match

The server's HTML and the client's first render must produce
identical output. Any mismatch triggers a re-render and a console
warning, and often a visible flash.

### Contract 4: Caching Is Layered

Next.js has four caches: request memoization, the data cache, the
full route cache, and the router cache. Each has a different
lifecycle. Invalidating the wrong one leaves stale data.

### Contract 5: Route Segments Are Independent

A layout persists across navigation. A page re-renders. A
`loading.tsx` streams while the page's data loads. A `error.tsx`
catches errors in its segment.

### Contract 6: Params Are Promises

In Next.js 15+, `params` and `searchParams` are `Promise` objects.
They must be awaited before use.

## 3. Server and Client Components

### 3.1 Server by Default

Every component is a Server Component unless marked `"use client"`.

Rationale: Server Components reduce the client bundle, can access
the database, and can fetch data without exposing credentials.

### 3.2 `"use client"` Only When Required

The directive is required for:

- `useState`, `useReducer`, `useEffect`, `useRef`.
- Event handlers (`onClick`, `onChange`).
- Browser APIs (`window`, `document`, `localStorage`).
- Third-party libraries that use any of the above.

If a component does none of these, it is a Server Component.

### 3.3 Push `"use client"` Down

BAD: Adding `"use client"` to a top-level page because one button
inside needs interactivity.

GOOD: Extract the interactive part into a small Client Component.

Rationale: the `"use client"` directive marks the file and all its
imports. Adding it high in the tree pulls the entire subtree into
the client bundle.

### 3.4 Client Components Accept Server Components as Children

A Client Component cannot import a Server Component, but it can
accept one as `children`.

```tsx
"use client";

export function Tabs({ children }: { children: React.ReactNode }) {
  const [active, setActive] = useState(0);
  return <div>{children}</div>;
}
```

The parent (Server Component) passes Server Components as
`children`.

### 3.5 No Server-Only Imports in Client Components

A Client Component cannot import from `fs`, `crypto`, a database
client, or any server-only package.

BAD:
```tsx
"use client";
import { readFile } from "fs/promises";  // build error
```

GOOD: Fetch the data in a Server Component and pass it as a prop.

### 3.6 `server-only` Package for Shared Modules

A module that must never reach the client uses `import
"server-only";` at the top. The build fails if a Client Component
imports it.

### 3.7 Never Pass Functions to Client Components

A Server Component cannot pass a function as a prop to a Client
Component. Functions are not serializable.

BAD:
```tsx
// Server Component
<ClientButton onClick={() => console.log("clicked")} />
```

GOOD:
```tsx
// Client Component
"use client";
export function ClientButton() {
  const handleClick = () => console.log("clicked");
  return <button onClick={handleClick}>Click</button>;
}
```

### 3.8 Serializable Props Only

Server Components pass serializable props to Client Components:
strings, numbers, booleans, `null`, arrays, plain objects, Dates,
Maps, Sets. Not class instances, not functions, not Symbols.

## 4. Data Fetching

### 4.1 Fetch in Server Components

Default: fetch in Server Components. No `useEffect`, no client-side
loading state.

```tsx
async function Page() {
  const user = await getUser(id);
  return <Profile user={user} />;
}
```

Rationale: the fetch happens on the server, the data arrives with
the HTML, and no loading flash occurs.

### 4.2 Parallel Fetches

BAD:
```tsx
const user = await getUser(id);
const posts = await getPosts(id);
```

GOOD:
```tsx
const [user, posts] = await Promise.all([getUser(id), getPosts(id)]);
```

### 4.3 `cache()` for Repeated Fetches

A function called multiple times during a request is memoized with
React's `cache`:

```tsx
import { cache } from "react";

export const getUser = cache(async (id: string) => {
  return db.users.findById(id);
});
```

Rationale: without `cache`, the same fetch runs once per component
that calls it during the same request.

### 4.4 Next.js `fetch` Caching Options

Next.js extends `fetch` with caching:

- Default: cached indefinitely (in static rendering).
- `{ cache: "no-store" }`: always fresh.
- `{ next: { revalidate: 60 } }`: cached for 60 seconds.
- `{ next: { tags: ["user"] } }`: tagged for invalidation.

Pick deliberately. The default is not always what you want.

### 4.5 Client-Side Fetching for User-Specific Data

Authenticated or session-specific data is fetched in Client
Components or Route Handlers, not Server Components, unless the
session is available server-side.

### 4.6 No Waterfalls

A Server Component that awaits a fetch, renders a Client Component
that fetches again, then renders another Server Component that
fetches. Each step waits for the previous.

Fetch in parallel where possible, or move the fetch up.

### 4.7 Streaming With Suspense

A slow Server Component blocks the entire page. Wrap it in
`<Suspense>` to stream the fast parts first.

```tsx
<Suspense fallback={<Skeleton />}>
  <SlowComponent />
</Suspense>
```

### 4.8 No Fetch in Client Components for Data the Server Has

If the Server Component already fetched the user, do not fetch it
again in a Client Component. Pass it as a prop.

## 5. Caching

### 5.1 Understand the Four Caches

- **Request Memoization**: `fetch` calls in one render pass.
- **Data Cache**: `fetch` results across requests.
- **Full Route Cache**: static rendering of a route.
- **Router Cache**: client-side cache of visited routes.

Each has a different lifecycle and invalidation method.

### 5.2 `revalidatePath` After Mutations

After a mutation that affects a route, call `revalidatePath`:

```typescript
"use server";
export async function createUser(formData: FormData) {
  await db.users.create(/* ... */);
  revalidatePath("/users");
}
```

### 5.3 `revalidateTag` for Granular Invalidation

Tag the fetch, then invalidate by tag:

```typescript
const user = await fetch(`/api/users/${id}`, {
  next: { tags: [`user-${id}`] },
});

// Later:
revalidateTag(`user-${id}`);
```

### 5.4 `dynamic = "force-dynamic"` Explicitly

If a page must always be fresh, opt out of caching explicitly:

```tsx
export const dynamic = "force-dynamic";
```

### 5.5 No Infinite Cache Without Invalidation

A page cached forever with no invalidation shows stale data forever.

### 5.6 Never Cache Authenticated Content on the Server

BAD: A Server Component fetching `/api/me` with a cache option. The
cached response is served to other users.

GOOD: `{ cache: "no-store" }` for user-specific data, or fetch in a
Client Component.

## 6. Routing

### 6.1 File-Based Routing

- `app/page.tsx`: home.
- `app/users/page.tsx`: `/users`.
- `app/users/[id]/page.tsx`: `/users/:id`.
- `app/users/[id]/edit/page.tsx`: `/users/:id/edit`.

### 6.2 Layouts Persist

`layout.tsx` wraps child routes and persists across navigations.
State in a layout is preserved.

### 6.3 `loading.tsx` for Streaming

A `loading.tsx` file provides an instant loading UI while the page
streams.

### 6.4 `error.tsx` for Errors

An `error.tsx` file provides an error boundary for a route segment.
It is a Client Component.

### 6.5 `not-found.tsx` for 404

A `not-found.tsx` file renders when `notFound()` is called or a
route is not matched.

### 6.6 Dynamic Params Are Promises

In Next.js 15+, `params` and `searchParams` are `Promise` objects.
Await them.

BAD:
```tsx
export default function Page({ params }: { params: { id: string } }) {
  return <div>{params.id}</div>;  // undefined in Next.js 15
}
```

GOOD:
```tsx
export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <div>{id}</div>;
}
```

### 6.7 Route Groups

`(group)` folders organize routes without affecting the URL. Use
them for layout sharing.

### 6.8 Parallel Routes

`@slot` folders render multiple pages in the same layout. Use them
for dashboards and modals.

### 6.9 Intercepting Routes

`(..)` prefixes intercept a route and render it in the current
context (a modal over a list). Use them for the "open detail without
losing list state" pattern.

## 7. Route Handlers

### 7.1 `route.ts` for API Endpoints

```typescript
// app/api/users/route.ts
export async function GET(request: Request) {
  const users = await db.users.findMany();
  return Response.json(users);
}
```

### 7.2 Method Handlers

Export `GET`, `POST`, `PUT`, `PATCH`, `DELETE` as named functions.

### 7.3 No Server Actions in Route Handlers

Route Handlers are for external API consumers. Server Actions are
for form submissions and internal mutations.

### 7.4 Streaming Responses

Route Handlers can stream responses with a `ReadableStream`.

### 7.5 Caching Is Opt-In

Route Handlers are not cached by default in Next.js 14+.

```typescript
export const dynamic = "force-static";
```

For a cached Route Handler.

### 7.6 Validate Input

A Route Handler receives untrusted input. Validate with a schema
before use.

## 8. Server Actions

### 8.1 Server Actions Are for Mutations

```typescript
"use server";
export async function createUser(formData: FormData) {
  const name = formData.get("name") as string;
  // ...
  revalidatePath("/users");
}
```

### 8.2 Validate Input

A Server Action receives untrusted input. Validate with a schema
before using.

BAD:
```typescript
"use server";
export async function createUser(formData: FormData) {
  await db.users.create({ name: formData.get("name") });  // unvalidated
}
```

GOOD:
```typescript
"use server";
export async function createUser(formData: FormData) {
  const parsed = createUserSchema.parse({
    name: formData.get("name"),
  });
  await db.users.create(parsed);
}
```

### 8.3 `revalidatePath` or `revalidateTag` After Mutation

A mutation invalidates the cache. Without it, the UI shows stale
data.

### 8.4 Return Values Are Serializable

Server Actions return serializable data. Not class instances, not
functions.

### 8.5 No Secrets in Client-Callable Actions

A Server Action is exposed to the client. Do not assume it is
private. Authenticate and authorize inside.

### 8.6 `useFormStatus` for Pending States

```tsx
"use client";
import { useFormStatus } from "react-dom";

function SubmitButton() {
  const { pending } = useFormStatus();
  return <button disabled={pending}>Save</button>;
}
```

### 8.7 `useActionState` for Form Feedback

```tsx
"use client";
import { useActionState } from "react";

const [state, formAction] = useActionState(createUser, null);
```

## 9. Metadata and SEO

### 9.1 Static `metadata` Export

```tsx
export const metadata = {
  title: "User Profile",
  description: "...",
};
```

### 9.2 `generateMetadata` for Dynamic

```tsx
export async function generateMetadata({ params }) {
  const { id } = await params;
  const user = await getUser(id);
  return { title: user.name };
}
```

### 9.3 `metadataBase` in Root Layout

Set `metadataBase` in the root layout for absolute URLs in OG
images.

### 9.4 `metadata` Is Server-Only

`metadata` is for Server Components. In a Client Component, lift
the metadata to a parent Server Component.

### 9.5 `viewport` and `themeColor` Separately

Next.js 14+ splits `viewport` and `themeColor` from `metadata`:

```tsx
export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};
```

## 10. Images and Fonts

### 10.1 `next/image`

```tsx
import Image from "next/image";

<Image src="/hero.jpg" alt="" width={800} height={600} />
```

Provides optimization, lazy loading, and CLS prevention.

### 10.2 `next/font`

```tsx
import { Inter } from "next/font/google";

const inter = Inter({ subsets: ["latin"] });
```

Self-hosts fonts, avoids layout shift.

### 10.3 Remote Images Need `remotePatterns`

`next.config.js` lists allowed image hosts.

## 11. Configuration

### 11.1 `next.config.js` Changes Are Deliberate

A change to `next.config.js` affects every route. Document the
reason.

### 11.2 Environment Variables

- `NEXT_PUBLIC_*` for client-accessible values.
- Other variables are server-only.

BAD: `NEXT_PUBLIC_API_SECRET` in the client bundle.

### 11.3 No Secrets in `NEXT_PUBLIC_*`

Anything prefixed with `NEXT_PUBLIC_` is inlined into the client
bundle. It is public.

### 11.4 `output` Mode Is Explicit

`output: "standalone"` for Docker, `"export"` for static, or default
for a Node.js server. Match the deployment target.

## 12. Anti-Patterns

### 12.1 `"use client"` at the Top

Covered in 3.3.

### 12.2 `useEffect` for Data Fetching

Covered in 4.1.

### 12.3 `getServerSideProps` in App Router

Removed in the App Router. Use async Server Components.

### 12.4 `getStaticProps` in App Router

Removed. Use `fetch` with cache options.

### 12.5 Route Handler and Server Action Duplication

Both fetch the same data. Extract to a shared function.

### 12.6 Server-Only Code in Client Components

Covered in 3.5.

### 12.7 Awaiting Waterfall

Covered in 4.6.

### 12.8 No `loading.tsx`

A slow page without a streaming loading state blocks navigation.

### 12.9 No `error.tsx`

An error crashes the page instead of showing a fallback.

### 12.10 `dynamic = "force-dynamic"` Everywhere

Disables all caching. Slow and expensive.

### 12.11 `<a>` Instead of `<Link>`

BAD: `<a href="/users">Users</a>`.

GOOD: `<Link href="/users">Users</Link>`.

Rationale: `<a>` triggers a full page reload; `<Link>` does
client-side navigation.

### 12.12 `<img>` Instead of `next/image`

Covered in 10.1.

### 12.13 No Font Optimization

Loading fonts via a `<link>` to Google Fonts. Use `next/font`.

### 12.14 `metadata` in a Client Component

`metadata` is for Server Components only.

### 12.15 Server Actions Without `"use server"`

A function that looks like an action but has no directive. The
client cannot call it.

### 12.16 Leaking Server Secrets Through Props

BAD: Passing `process.env.API_SECRET` as a prop to a Client
Component.

### 12.17 Not Handling `params` Promise in Next.js 15

Covered in 6.6.

### 12.18 `useRouter` in a Server Component

`useRouter` is client-only. Use `redirect()` from
`next/navigation` in Server Components.

### 12.19 Middleware Doing Heavy Work

Middleware runs on every request (edge or Node). A database query in
middleware adds latency to every route.

### 12.20 No Suspense Boundary

Covered in 4.7.

### 12.21 Overuse of Server Actions for Reads

Server Actions are for mutations. Reads happen in Server Components.

### 12.22 `router.refresh()` Instead of Revalidation

`router.refresh()` refetches the entire page. Prefer targeted
`revalidateTag`.

### 12.23 No Loading UI for Forms

A form submission without a pending state feels broken.

### 12.24 Client Component for Entire Page

A page with `"use client"` loses all Server Component benefits.

### 12.25 Ignoring the Bundle Analyzer

`@next/bundle-analyzer` shows what is in the client bundle. Run it
regularly.

### 12.26 Cache Invalidation Only in Development

The `revalidate` option set in development but the production build
uses the default. Verify the production behavior.

### 12.27 Assuming `fetch` Caches in Client Components

Next.js's `fetch` cache options apply only to Server Components.
Client-side `fetch` uses the browser's cache.

### 12.28 Storing Auth Tokens in `localStorage`

Covered in `02-api-data-anti-slop.md` section 11.31. Use HTTP-only
cookies.

### 12.29 Middleware Redirect Loops

A middleware that redirects unauthenticated users to `/login`, but
`/login` is also protected. The redirect loops.

### 12.30 Missing `key` in Server-Rendered Lists

Same as React. See `02-react-anti-slop.md` section 6.1.

### 12.31 Passing Non-Serializable Props

Covered in 3.7 and 3.8.

### 12.32 Using `window` in a Server Component

BAD: `window.location.href` in a Server Component.

GOOD: `headers()` from `next/headers`.

### 12.33 `cookies()` Without `await` in Next.js 15

`cookies()` returns a Promise in Next.js 15+. Await it.

### 12.34 Direct `process.env` Reads in Components

Read config through a typed module, not scattered
`process.env.NEXT_PUBLIC_*` lookups.

### 12.35 Missing `Suspense` for `useSearchParams`

`useSearchParams()` requires a `Suspense` boundary in a
statically-rendered page, or the page becomes dynamic.

### 12.36 Client Component Fetching Static Data

A Client Component that fetches a country list on every mount. Move
it to a Server Component.

### 12.37 No Streaming for Slow Data

A page that awaits every fetch before rendering. Use `<Suspense>` to
stream the fast parts first.

### 12.38 `revalidatePath("/")` for Everything

Invalidating the root path invalidates every route. Use specific
paths or tags.

### 12.39 No `not-found.tsx`

A route that calls `notFound()` without a `not-found.tsx` uses the
default Next.js 404 page.

### 12.40 Mutating Data in a Server Component

A Server Component that writes to the database during render. Server
Components are for reads. Use a Server Action or a Route Handler.

## 13. Response to Violation

If a previous response violated a rule here:

```
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

No justification. No apology paragraph. Fix and move on.
