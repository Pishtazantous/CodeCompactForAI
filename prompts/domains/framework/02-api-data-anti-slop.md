---
id: 02-api-data-anti-slop
title: "API & Data Fetching Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-frontend-anti-slop, 02-state-anti-slop]
category: domain
domain_type: framework
version: 2
---

# API & Data Fetching Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`,
`domains/framework/02-architecture-anti-slop.md`,
`domains/delivery/02-frontend-anti-slop.md`, and
`domains/framework/02-state-anti-slop.md`. Rules already covered in
those files are NOT repeated here.

This file covers rules specific to how a frontend talks to its
backend: layering, HTTP client configuration, response typing,
data-fetching patterns, mutations, error normalization, cache
invalidation, and authentication in requests. It is
framework-agnostic within the frontend ecosystem. It does NOT cover
state classification (see `02-state-anti-slop.md`),
framework-specific hooks (see the framework files), backend API
design (see `02-backend-anti-slop.md`), or the UI layer (see
`04-ui-design-system.md`).

Data flow between a frontend and a backend is where the most
expensive bugs live: stale caches, race conditions, silent failures,
and duplicated sources of truth. The rules below enforce a single,
predictable path for every byte that crosses the network.

## 1. Stack Assumptions

This file assumes:

- A frontend that talks to a backend over HTTP, GraphQL, or a
  similar transport.
- At least one HTTP client: native `fetch`, `axios`, `ky`, `got`,
  or a generated SDK.
- At least one data-fetching library: TanStack Query, SWR, Apollo
  Client, RTK Query, Vue Query, Svelte Query, or a meta-framework's
  built-in loader.

### Framework Lifecycle Contracts

Data fetching enforces six contracts. Every section below enforces
one or more of these.

#### Contract 1: Single HTTP Client

The application has one configured HTTP client. Every service uses
it. A second client is a second configuration, a second set of
interceptors, and a second source of divergence.

#### Contract 2: Layered Flow

Components consume hooks. Hooks consume services. Services consume
the HTTP client. Each layer has one responsibility and one direction
of dependency.

#### Contract 3: Validated Responses

Every response is parsed against a schema before use. The wire
format is not trusted; the runtime type is proven.

#### Contract 4: Explicit States

Every asynchronous operation has visible loading, error, and empty
states. A component that renders before data is ready is a component
that crashes.

#### Contract 5: Centralized Errors

Errors are normalized in one place. A network error, an HTTP error,
and a validation error have a consistent shape that the UI can
render.

#### Contract 6: Deterministic Cache

Every query has a stable key. Every mutation invalidates the queries
it affects. The cache converges to the truth without manual
intervention.

## 2. Layering

### 2.1 Components Never Call HTTP Directly

BAD:
```tsx
useEffect(() => {
  fetch("/api/users").then(r => r.json()).then(setUsers);
}, []);
```

GOOD:
```tsx
const { data: users } = useUsers();
```

Rationale: a component that calls `fetch` reimplements caching,
deduplication, and error handling. The data-fetching library already
solves these problems.

### 2.2 The Layered Path

```
Component -> Hook -> Service -> HTTP Client -> Backend
                       |
                       v
                 Types / Schemas
```

Every layer is a separate module. Every arrow is an import
direction.

### 2.3 Services Are Pure

A service function:

- Takes explicit arguments.
- Returns a typed value.
- Throws on failure, or returns a result object (match the project).
- Does no caching, no toast, no navigation, no console logging.

BAD:
```typescript
export async function getUser(id: string) {
  const response = await fetch(`/users/${id}`);
  const data = await response.json();
  if (!data) {
    toast.error("User not found");  // side effect in a service
  }
  return data as User;  // unvalidated cast
}
```

GOOD:
```typescript
export async function getUser(id: string): Promise<User> {
  const response = await httpClient.get(`/users/${id}`);
  return userSchema.parse(response.data);
}
```

### 2.4 Hooks Wrap the Service

A hook ties the service to the data-fetching library's cache and
lifecycle:

```typescript
export function useUser(id: string) {
  return useQuery({
    queryKey: ["user", id],
    queryFn: () => getUser(id),
  });
}
```

The hook decides cache keys, `staleTime`, and enabled conditions.
The component decides what to render.

### 2.5 Never Skip a Layer

A component that calls a service directly, or a service that calls
the data-fetching library, breaks the layering. Each layer talks
only to the layer below.

## 3. HTTP Client

### 3.1 One HTTP Client Instance

The project has one configured HTTP client. Every service uses it.

BAD: Each service creates its own client with its own base URL and
interceptors.

GOOD: One client in `lib/http`, imported by every service.

### 3.2 Configuration in One Place

Base URL, default headers, timeout, retry policy, and interceptors
are configured on the client instance.

BAD:
```typescript
httpClient.get("/users", { timeout: 5000, headers: { "X-App": "web" } });
```

GOOD:
```typescript
httpClient.get("/users");  // client already has timeout and headers
```

### 3.3 Auth Token Attached by Interceptor

The `Authorization` header is added by an interceptor, not manually
in every service function.

BAD:
```typescript
httpClient.get("/users", {
  headers: { Authorization: `Bearer ${getToken()}` },
});
```

GOOD:
```typescript
httpClient.get("/users");  // interceptor adds the header
```

Rationale: a manual header is forgotten in one place, and that one
endpoint fails silently.

### 3.4 Explicit Timeout

Every request has a timeout. A request without one hangs the UI
indefinitely if the backend never responds.

### 3.5 Never Concatenate URLs

BAD:
```typescript
httpClient.get("/users/" + id + "/posts?limit=" + limit);
```

GOOD:
```typescript
httpClient.get(`/users/${id}/posts`, { params: { limit } });
```

Rationale: the client handles encoding and parameter serialization.
Manual concatenation skips both.

### 3.6 No Business Logic in Interceptors

An interceptor handles cross-cutting concerns: auth, logging,
error normalization. It does not decide business rules.

BAD: An interceptor that redirects to `/onboarding` when the user
has not completed setup.

GOOD: The interceptor attaches auth and normalizes errors. A route
guard handles onboarding.

### 3.7 Bounded Retries

Retries are for network errors and 5xx responses. A 4xx response is
not retried.

BAD: A client that retries every failed request.

GOOD: Retry on network errors and 5xx, with exponential backoff and
a maximum attempt count.

## 4. Response Typing

### 4.1 Never Trust the Wire

An HTTP response is `unknown`. Every response is parsed through a
schema before use.

BAD:
```typescript
const user = (await response.json()) as User;
```

GOOD:
```typescript
const user = userSchema.parse(await response.json());
```

Rationale: the backend may change. A cast hides the mismatch. A
schema parse fails loudly at the boundary.

### 4.2 Schema at the Boundary

The schema is defined once, in a shared types or schemas module. The
service uses it. The hook returns the inferred type.

### 4.3 No `any` in Data Flow

If the response shape is unknown, use `unknown` and parse. If the
shape is known, type it. `any` disables type checking through the
entire downstream chain.

### 4.4 Match the Backend's Shape

If the backend returns `{ data: { user: {...} } }`, the service
unwraps to the domain type. Do not invent a different shape on the
frontend.

### 4.5 Validate Optional Fields

A field that is required in production but optional in staging
causes a runtime error. If the field is optional in the schema, the
code handles `undefined` explicitly.

### 4.6 Never Assert on JSON

BAD:
```typescript
const data = (await response.json()) as User;
```

`response.json()` returns `any`. An assertion erases the need to
validate.

### 4.7 Parse Once, Use Everywhere

The parse happens at the service boundary. Downstream code works
with the validated type. Do not parse the same response twice.

## 5. Data Fetching

### 5.1 Never `fetch` in a Component

Covered in 2.1.

### 5.2 Never Fetch in an Effect for Cached Data

If the project uses a data-fetching library, the library fetches. Do
not duplicate the fetch in an effect.

### 5.3 Query Keys Are Stable and Complete

BAD:
```typescript
useQuery({ queryKey: ["user"], queryFn: () => getUser(id) });
```

The key does not include `id`. Two different users share a cache
entry, and one user sees another's data.

GOOD:
```typescript
useQuery({ queryKey: ["user", id], queryFn: () => getUser(id) });
```

Every variable the query depends on is part of the key.

### 5.4 Handle Three States Explicitly

BAD:
```tsx
const { data } = useUsers();
return <Table rows={data} />;
```

The `data` is `undefined` on first render. The component crashes.

GOOD:
```tsx
const { data, isLoading, error } = useUsers();
if (isLoading) return <Spinner />;
if (error) return <ErrorState error={error} />;
if (!data || data.length === 0) return <EmptyState />;
return <Table rows={data} />;
```

### 5.5 `staleTime` Is a Decision

- `staleTime: 0`: always fresh.
- `staleTime: 60_000`: data that changes slowly (user profile).
- `staleTime: Infinity`: data that never changes during a session
  (country list).

Do not leave `staleTime` at its default without a reason.

### 5.6 Prefetch on Intent, Not on Load

Prefetch on hover, focus, or the next likely user action. Do not
prefetch every route on page load; the bandwidth is wasted on
routes the user never visits.

### 5.7 Deduplicate by Default

The data-fetching library deduplicates by query key. Do not disable
this unless there is a specific reason.

### 5.8 Dependent Queries Use `enabled`

BAD:
```typescript
const { data: user } = useUser(userId);
const { data: orders } = useOrders(user?.id);  // runs with undefined
```

GOOD:
```typescript
const { data: user } = useUser(userId);
const { data: orders } = useOrders(user?.id, { enabled: !!user?.id });
```

### 5.9 Parallel Fetches Where Possible

BAD:
```typescript
const user = await getUser(id);
const posts = await getPosts(id);
```

GOOD:
```typescript
const [user, posts] = await Promise.all([getUser(id), getPosts(id)]);
```

### 5.10 Never Fetch in a Loop

A fetch inside a `map` or `for` loop produces N requests. Fetch a
batch, or use a joined endpoint.

## 6. Mutations

### 6.1 Mutations Belong to the Data-Fetching Library

Mutations use the same library's `useMutation` (or equivalent).
They are not raw service calls from event handlers.

### 6.2 Invalidate, Do Not Manually Update

After a successful mutation, invalidate the affected queries.

BAD:
```typescript
await updateUser(id, data);
queryClient.setQueryData(["user", id], data);
```

GOOD:
```typescript
await updateUser(id, data);
queryClient.invalidateQueries({ queryKey: ["user", id] });
```

Rationale: manual updates drift from the server when validation,
defaults, or server-side timestamps are involved.

### 6.3 Optimistic Updates Are Opt-In

Optimistic updates are correct only when:

- The server is unlikely to reject the mutation.
- The rollback is straightforward.
- The user experience genuinely benefits.

Implement with `onMutate` (capture the previous state), `onError`
(rollback), and `onSettled` (invalidate to reconcile).

### 6.4 Mutations Return the Server's Response

A mutation's `onSuccess` receives the server's response. Use it when
the server returns updated data.

BAD: Assuming the client's payload is what the server stored.

### 6.5 Disable the Trigger During Submission

The submit button, the link, or whatever triggers the mutation is
disabled while `isPending` is true.

Rationale: double-submission creates duplicate records on the
server.

### 6.6 One Mutation Per Action

A single "save everything" mutation that updates user, settings, and
notifications is hard to invalidate and hard to roll back. Split
into one mutation per resource.

### 6.7 Idempotency Key for Critical Writes

A payment or order creation endpoint has an idempotency key. A
retry after a network failure does not create a second charge.

## 7. Error Handling

### 7.1 One Error Normalizer

The project has one function that turns any thrown error (HTTP
error, network failure, parse error) into a consistent shape:

```typescript
type AppError = {
  kind: "network" | "http" | "validation" | "unknown";
  status?: number;
  message: string;
  cause?: unknown;
};
```

Every layer that catches errors uses it.

### 7.2 HTTP Errors Are Failures

A 4xx response is a failure. The service throws, or returns an error
result. The component shows the error. Never treat a 404 or 500 as
"no data".

### 7.3 Network Errors Differ From Validation Errors

The user cannot fix a network error by changing input. The UI shows
a different message and a different action (Retry vs Fix).

### 7.4 Never `catch` and Do Nothing

BAD:
```typescript
try {
  await saveUser(data);
} catch (e) {
  // silence
}
```

GOOD:
```typescript
try {
  await saveUser(data);
} catch (error) {
  reportError(error);
  throw error;
}
```

### 7.5 Never `catch (e: any)`

`catch` receives `unknown` in TypeScript with
`useUnknownInCatchVariables`. Type-guard before using `.message` or
`.status`.

### 7.6 User-Facing Messages Differ From Logs

The raw server message may contain stack traces, internal paths, or
identifiers. Map server errors to user-facing messages.

BAD: Showing `"PostgresError: duplicate key value violates unique
constraint users_email_key"`.

GOOD: `"This email is already registered."`

### 7.7 Global Error Boundary

Unexpected render errors are caught by an error boundary. The
boundary reports to the project's error-tracking service and shows
a fallback UI.

### 7.8 Errors in Async Code Are Not Caught by Boundaries

A rejected promise in an effect is not caught by an error boundary.
Handle it explicitly or route it to an error state.

## 8. Cache Invalidation

### 8.1 Invalidation Strategy Is Explicit

For each mutation, list the query keys it invalidates. If the list
is not obvious, the query keys are too broad.

### 8.2 Prefer Broad Over None

Invalidating too much is slow but correct. Invalidating nothing is
fast but wrong. When unsure, invalidate broadly and measure.

### 8.3 Never Rely on Manual Cache Updates Alone

Manual cache updates (via `setQueryData`) bypass validation and
server-side computations. Use them only when an optimistic update is
required, and always follow with an invalidation.

### 8.4 Cache Eviction Is the Library's Job

Do not manually remove cache entries. Configure `gcTime` (or
`cacheTime`) and `staleTime`. The library handles eviction.

### 8.5 Invalidation After Logout

After logout, clear the query cache. Otherwise the next user sees
the previous user's data for a moment before the new fetch resolves.

## 9. URL and Query Params

### 9.1 The URL Is the Source of Truth for Resource Identity

Which user, which project, which filter, which page. The URL holds
it.

### 9.2 Read Query Params Through the Router

BAD:
```typescript
const params = new URLSearchParams(window.location.search);
```

GOOD:
```typescript
const [searchParams] = useSearchParams();
const page = Number(searchParams.get("page") ?? "1");
```

Rationale: `window.location` bypasses the router's cache and does
not trigger a re-render on change.

### 9.3 Validate Query Params

A `?page=abc` should not produce `NaN`. Parse and validate with the
project's schema library or with explicit defaults.

### 9.4 Never Store URL State in a Store

Covered in `02-state-anti-slop.md` section 4.5. Repeating: the URL
is the source of truth. Duplicating it in a store creates two
sources.

## 10. Authentication in Requests

### 10.1 Token in Interceptor

Covered in 3.3.

### 10.2 401 Handling Is Centralized

A 401 response triggers one central action: refresh the token, or
redirect to login. Not a per-component handler.

### 10.3 Token Refresh Is Deduplicated

If five requests fail with 401 simultaneously, the token refreshes
once, not five times. Use a shared promise for the refresh.

BAD:
```typescript
httpClient.interceptors.response.use(undefined, async (error) => {
  if (error.response?.status === 401) {
    const newToken = await refreshToken();  // five parallel refreshes
    return httpClient.request(error.config);
  }
});
```

GOOD:
```typescript
let refreshPromise: Promise<string> | null = null;

httpClient.interceptors.response.use(undefined, async (error) => {
  if (error.response?.status === 401) {
    refreshPromise ??= refreshToken();
    const newToken = await refreshPromise;
    refreshPromise = null;
    return httpClient.request(error.config);
  }
});
```

### 10.4 Never Retry a Mutation Automatically on 4xx

A POST that failed with 409 will fail again. Retry only network
errors and 5xx, with backoff, and only for idempotent operations.

### 10.5 Logout Clears All Cached Data

Covered in 8.5.

### 10.6 Never Send the Token in a Query String

Tokens in URLs are logged by proxies, stored in browser history, and
leaked via referrer headers. Always the `Authorization` header.

## 11. Anti-Patterns

### 11.1 Fetch in a Component

Covered in 2.1.

### 11.2 Fetch in `useEffect`

Covered in 5.2.

### 11.3 Manual Loading State

Reimplementing `isLoading`, `isError`, and `data` when the library
already tracks them.

BAD:
```tsx
const [loading, setLoading] = useState(false);
const [error, setError] = useState(null);
const [data, setData] = useState(null);
```

### 11.4 Manual Retry Logic

The HTTP client or the data-fetching library already retries.
Adding a `for` loop around a fetch duplicates the logic.

### 11.5 `try/catch` in Every Service Function

If the client has an interceptor that handles errors, individual
services do not need to. Centralize.

### 11.6 `console.log` in the API Layer

Use the project's logger or nothing. Console output ships to
production in most builds.

### 11.7 Type Assertion on Response

Covered in 4.1.

### 11.8 Pointless Wrappers

BAD:
```typescript
export const getUsers = () => httpClient.get("/users");
export const getPosts = () => httpClient.get("/posts");
```

Each wrapper adds a layer but no typing, no schema, and no error
handling. Add a service function when it does something: parse,
transform, unwrap, type.

### 11.9 Manual Cache

Any caching that does not go through the data-fetching library. It
will leak, stale, or race.

### 11.10 Error Handling per File

Every file catches errors differently. The user sees inconsistent
messages. Normalize once.

### 11.11 `try/catch` That Rethrows

BAD:
```typescript
try {
  return await getUser(id);
} catch (error) {
  throw error;
}
```

### 11.12 Toast Inside the Service

BAD: A service function that calls `toast.error("Failed")`.

GOOD: The service throws; the component decides whether to toast,
inline-error, or redirect.

Rationale: a toast in a service fires on every call site, including
background refetches, even when the user did not initiate the
request.

### 11.13 Missing `await` on a Service

BAD:
```typescript
function saveUser(data) {
  updateUser(data);  // returns a Promise, not awaited
}
```

The caller thinks the save completed. It did not.

### 11.14 Ignoring the Server's Response

BAD:
```typescript
await updateUser(data);
// assume the server stored exactly what was sent
```

The server may add `updatedAt`, normalize fields, or reject
silently. Use the server's response.

### 11.15 Fetching the Same Data in Sibling Components

Two components independently call `useUser(id)`. The data-fetching
library deduplicates. Without one, two requests are sent.

### 11.16 Not Handling Offline

A request that fails because the browser is offline is different
from a 500. The UI should distinguish them if the project cares
about offline users.

### 11.17 Over-Fetching

Fetching a full user object to render a name. Ask the backend for
the fields needed (`?fields=name`), or use a lighter endpoint.

### 11.18 Under-Fetching and Follow-Up Requests

Fetching a list, then fetching each item to render. Use a single
endpoint that returns what is needed, or a joined query.

### 11.19 Serial Requests When Parallel Is Possible

Covered in 5.9.

### 11.20 Hardcoded API Base URL

Covered in the frontend delivery file. Repeating: configuration, not
source.

### 11.21 Token in Query String

Covered in 10.6.

### 11.22 Missing `Content-Type` on POST

A POST without `Content-Type: application/json` sends a form-encoded
body. The server parses it as an empty object.

### 11.23 Double-Serialized Body

Sending an already-stringified JSON string as the body. The server
receives a string, not an object.

### 11.24 Ignoring `response.ok`

BAD:
```typescript
const response = await fetch(url);
const data = await response.json();  // succeeds on 404 HTML page
```

GOOD:
```typescript
if (!response.ok) throw new HttpError(response.status);
const data = await response.json();
```

Rationale: `fetch` does not reject on HTTP errors. A 404 or 500
response resolves normally.

### 11.25 No `Accept` Header

An endpoint that returns different formats needs `Accept`. Without
it, the client gets the server's default, which may not be what the
code expects.

### 11.26 Assuming JSON Response

Calling `response.json()` on an endpoint that returns HTML (an error
page from a proxy) throws a parse error that hides the real failure.

### 11.27 Not Cancelling In-Flight Requests

A component that unmounts while a request is in flight triggers a
state update on an unmounted component (React warning). The library
handles this; manual `fetch` does not.

### 11.28 Manual Request Deduplication

Two components fetch the same URL at the same time. Without the
library, two requests are sent.

### 11.29 Auth Token Read at Call Site

Covered in 3.3.

### 11.30 Mutating the HTTP Client at Runtime

Changing `httpClient.defaults.baseURL` from a component. The client
is configured once.

### 11.31 LocalStorage for Tokens

Tokens in `localStorage` are readable by any script on the page.
Use HTTP-only cookies for web, or Keychain/Keystore for mobile.

### 11.32 Interceptor That Swallows Errors

An interceptor that catches 5xx responses and returns a default
value. The caller cannot distinguish success from failure.

### 11.33 Retry on Non-Idempotent Request

A retry of a POST without an idempotency key creates duplicate
resources.

### 11.34 Duplicated Interceptors

Two interceptors that both add `Authorization`. The header is
duplicated.

### 11.35 No Request Timeout

Covered in 3.4.

### 11.36 Assuming a Specific Error Shape

BAD:
```typescript
catch (error) {
  toast.error(error.response.data.message);
}
```

If the server returns a different shape (a proxy's HTML error page),
this throws and hides the original error.

### 11.37 URL in the Wrong Place

BAD: `/users?id=42`.
GOOD: `/users/42`.

### 11.38 Mutating the Query Cache Directly

BAD: `queryClient.getQueryData(["users"]).push(newUser);`.

The cache is immutable. Use `setQueryData` with a new object.

### 11.39 Cache Key Collision

Two different queries share a key. The cache returns the wrong
data.

### 11.40 Not Invalidating After Logout

Covered in 8.5.

## 12. Response to Violation

If a previous response violated a rule here:

```
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

No justification. No apology paragraph. Fix and move on.
