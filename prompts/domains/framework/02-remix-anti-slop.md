---
id: 02-remix-anti-slop
title: "Remix Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-frontend-anti-slop, 02-react-anti-slop]
category: domain
domain_type: framework
version: 1
---
# Remix Anti-Slop Layer

Layered under the master, architecture, frontend, and React layers. This file
adds rules for Remix loaders, actions, nested routes, progressive enhancement,
and resource routes.

## 1. Stack Assumptions

1. Read the installed Remix version and route-module conventions before coding.
2. Use Remix loaders and actions for route-owned reads and mutations.
3. Keep the React layer responsible for component behavior, not data transport.
4. Use the existing server and deployment adapter.
5. Keep secrets in server loaders, actions, and server modules.
6. Do not add a second router, form library, or data cache.
7. Preserve nested-route ownership and outlet boundaries.
8. Do not migrate routes while making an unrelated fix.

## 2. Loaders

1. A loader owns reads needed before rendering its route.
2. Keep loaders focused on transport and application-use-case calls.
3. Return serializable data with stable field names.
4. Handle authorization and not-found results explicitly.
5. Use response headers or the repository's caching mechanism deliberately.
6. Do not return a database entity with sensitive fields.
7. Do not fetch the same resource in a loader and a component effect.
8. Use parallel data loading for independent requests.
9. Preserve parent loader data when child routes update.
10. Test unauthorized, missing, and upstream failure paths.

BAD:

```ts
export async function loader() {
  return db.user.findMany();
}
```

GOOD:

```ts
export async function loader({ request }: LoaderFunctionArgs) {
  await requireUser(request);
  return { projects: await listProjectsForUser(await currentUserId(request)) };
}
```

## 3. Actions

1. Use actions for mutations owned by a route.
2. Authenticate and authorize inside every action.
3. Validate form data or request input before the use case.
4. Return field errors and form errors with stable status semantics.
5. Redirect after a successful mutation when the next page is known.
6. Use `useFetcher` for independent mutations that should not navigate.
7. Do not return raw exceptions to the browser.
8. Make repeated submission safe or reject it with a clear result.
9. Keep action logic in an application service when shared across routes.
10. Test no-JavaScript submission and direct POST requests.

BAD:

```ts
export async function action({ request }) {
  await db.user.delete({ where: { id: new URL(request.url).searchParams.get("id") } });
  return null;
}
```

GOOD:

```ts
export async function action({ request }) {
  const userId = await requireUserId(request);
  const form = await request.formData();
  const projectId = ProjectId.parse(form.get("projectId"));
  await deleteOwnedProject(userId, projectId);
  return redirect("/projects");
}
```

## 4. Nested Routes

1. Keep layout routes responsible for shared navigation and boundaries.
2. Keep index routes responsible for the URL's primary data.
3. Let child loaders own child data when reuse and invalidation require it.
4. Avoid fetching a parent resource in every child.
5. Use parent outlet boundaries rather than copying layouts.
6. Preserve error boundaries at the narrowest route that can recover.
7. Keep route filenames and path ownership aligned.
8. Test nested navigation, back history, and failed child loads.

## 5. Progressive Enhancement

1. Use real forms and links for critical navigation and mutations.
2. Make the action path work without client JavaScript.
3. Do not require `useEffect` to make a form function.
4. Use `useFetcher` for non-navigating submissions.
5. Preserve focus and pending feedback without blocking the document.
6. Do not use a client-only modal as the only route to a destructive action.
7. Handle a direct request with the same validation and authorization path.
8. Test JavaScript disabled for the critical flow.

BAD:

```tsx
<button onClick={() => fetch("/delete", { method: "POST" })}>Delete</button>
```

GOOD:

```tsx
<Form method="post" action="/projects"><button type="submit">Delete</button></Form>
```

## 6. Resource Routes

1. Use resource routes for non-HTML responses with an explicit purpose.
2. Set the correct content type and status.
3. Validate the request method and payload.
4. Authorize every protected resource route.
5. Set cache and content-disposition headers deliberately.
6. Do not return a full route component from a resource route.
7. Close streams and external clients on every path.
8. Test direct access and malformed requests.

## 7. Data, State, and UI

1. Keep loader data in the route contract.
2. Keep action result state in `useActionData` or `useFetcher` data.
3. Do not duplicate server data in a global store.
4. Keep form state local and reset it according to the action result.
5. Use the React rules for effects, keys, and context.
6. Handle loading, error, and empty states explicitly.
7. Keep navigation in links and event handlers.
8. Avoid rendering raw server error messages.

## 8. Headers and Caching

1. Set private caching for personalized data.
2. Use public caching only for data safe for every visitor.
3. Set Vary headers when representation depends on request headers.
4. Invalidate the relevant route or data cache after a mutation.
5. Do not cache a mutation response as if it were a document.
6. Keep cache policy consistent between loader and action boundaries.
7. Test stale and invalidation behavior for critical data.

## 9. Domain-Specific Anti-Patterns

### 9.1 Loader With Business Rules

BAD:

```ts
export async function loader({ request }) {
  const user = await db.user.findUnique({ where: { id: id(request) } });
  return user && user.role === "admin" ? user : null;
}
```

GOOD:

```ts
export async function loader({ request }) {
  const actor = await requireUser(request);
  return { account: await findAccountForActor(actor) };
}
```

### 9.2 Client-Only Mutation

BAD:

```tsx
const deleteProject = () => fetch(`/projects/${id}`, { method: "DELETE" });
```

GOOD:

```tsx
<Form method="post" action={`/projects/${id}`}><button>Delete</button></Form>
```

### 9.3 Unvalidated Redirect Target

BAD:

```ts
return redirect(request.url);
```

GOOD:

```ts
const target = returnPathSchema.parse(form.get("returnTo"));
return redirect(target);
```

## 10. Response to Violation

If a previous response violated this file, use this structure:

```text
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

State the rule and correction only.
