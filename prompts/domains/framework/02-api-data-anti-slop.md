---
id: 02-api-data-anti-slop
title: "API & Data Fetching Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop]
category: domain
domain_type: framework
version: 1
---

# API & Data Fetching Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md` and
`domains/framework/02-architecture-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
security anti-patterns, output format) and architectural rules
(layering, dependency direction, folder structure, naming) are NOT
repeated here.

This file covers rules specific to how a frontend application talks to
its backend: the layering between components and HTTP, error handling,
caching, mutation, and the patterns that produce silent failures.
State management rules live in `domains/framework/02-state-anti-slop.md`.
Framework-specific rules (React Query, SWR) are referenced as examples
but do not constrain the project to a specific library.

## 1. Stack Assumptions

This layer assumes:

- A frontend application that talks to a backend over HTTP, GraphQL, or
  a similar transport.
- At least one HTTP client in the project: native `fetch`, `axios`,
  `ky`, `got`, or a generated SDK.
- At least one data-fetching library in the project: TanStack Query,
  SWR, Apollo Client, RTK Query, Vue Query, or the framework's built-in
  data loader (Remix, SvelteKit, Next.js server components).

If the project does not use a data-fetching library and calls `fetch`
directly in components, that is the first anti-pattern to fix. Report
it before writing new code in the same style.

## 2. Layering

### 2.1 Components Never Call HTTP Directly

BAD:
tsx
useEffect(() => {
  fetch("/api/users").then(r => r.json()).then(setUsers);
}, []);
GOOD:

tsx
const { data: users } = useUsers();
The component consumes a hook. The hook consumes a service. The service
consumes the HTTP client. Each layer has one reason to change.

2.2 The Layered Path
A well-layered frontend data flow:

text
Component -> Hook -> Service -> HTTP Client -> Backend
                       |
                       v
                 Types / Schemas
Every layer is a separate module. Every arrow is an import direction.

2.3 Service Layer Is Pure
A service function:

Takes explicit arguments.

Returns a typed value.

Throws on failure (or returns a result object; match the project).

Does no caching, no toast, no navigation, no logging to the console.

typescript
export async function getUser(id: string): Promise<User> {
  const response = await httpClient.get(`/users/${id}`);
  return userSchema.parse(response.data);
}
2.4 Hook Layer Wraps the Service
A hook ties the service to the data-fetching library's cache and
lifecycle:

typescript
export function useUser(id: string) {
  return useQuery({
    queryKey: ["user", id],
    queryFn: () => getUser(id),
  });
}
The hook decides cache keys, staleTime, and dependencies. The
component decides only what to render.

2.5 Never Skip a Layer
A component that calls a service directly, or a service that calls the
data-fetching library, breaks the layering. Each layer talks only to
the layer below.

3. HTTP Client Discipline
3.1 One HTTP Client Instance
The project has one configured HTTP client (an axios instance, a
ky instance, or a wrapper around fetch). Every service uses it.

BAD: Each service creates its own client with its own base URL and
interceptors.
GOOD: One client in lib/http, imported by every service.

3.2 Configuration Belongs in One Place
Base URL, default headers, timeout, retry policy, and interceptors are
configured on the client instance, not repeated at call sites.

3.3 Auth Token Attached by Interceptor
The Authorization header is added by an interceptor, not manually in
every service function.

BAD:

typescript
httpClient.get("/users", { headers: { Authorization: `Bearer ${token}` } });
GOOD:

typescript
httpClient.get("/users"); // interceptor adds the header
3.4 Timeout Is Explicit
Every request has a timeout. A request without one hangs the UI
indefinitely if the backend never responds.

3.5 Never Construct URLs by Concatenation
BAD:

typescript
httpClient.get("/users/" + id + "/posts?limit=" + limit);
GOOD:

typescript
httpClient.get(`/users/${id}/posts`, { params: { limit } });
The client handles encoding.

4. Response Typing
4.1 Never Trust the Wire
An HTTP response is unknown. Every response is parsed through a
schema before use.

BAD:

typescript
const user = (await response.json()) as User;
GOOD:

typescript
const user = userSchema.parse(await response.json());
4.2 Schema at the Boundary
The schema is defined once, in a shared types or schemas module.
The service uses it. The hook returns the inferred type.

4.3 No any in Data Flow
If the response shape is unknown, use unknown and parse. If the
shape is known, type it. any disables type checking through the
entire downstream chain.

4.4 Match the Backend's Shape, Do Not Invent
If the backend returns { data: { user: {...} } }, the service
unwraps to the domain type. Do not invent a different shape on the
frontend.

5. Data Fetching
5.1 Never fetch in a Component
Covered in 2.1. Repeating because it is the most common issue.

5.2 Never Fetch in an Effect for Cached Data
If the project uses a data-fetching library, the library fetches. Do
not duplicate the fetch in an effect.

5.3 Query Keys Are Stable and Complete
BAD:

typescript
useQuery({ queryKey: ["user"], queryFn: () => getUser(id) });
The key does not include id. Two different users share a cache entry.

GOOD:

typescript
useQuery({ queryKey: ["user", id], queryFn: () => getUser(id) });
Every variable the query depends on is part of the key. Missing
variables produce stale or wrong data.

5.4 Never Disable the Query by Default
BAD:

typescript
useQuery({ queryKey: ["user"], queryFn: fetchUser, enabled: false });
If the query is always disabled, the hook is a promise wrapper in
disguise. Fetch where the data is needed.

5.5 Handle Loading, Error, and Empty States
BAD:

tsx
const { data } = useUsers();
return <Table rows={data} />;
The data is undefined on first render. The component crashes.

GOOD:

tsx
const { data, isLoading, error } = useUsers();
if (isLoading) return <Spinner />;
if (error) return <ErrorState error={error} />;
if (!data || data.length === 0) return <EmptyState />;
return <Table rows={data} />;
5.6 Prefetch on Intent, Not on Load
Prefetching every route on page load wastes bandwidth and delays the
initial render. Prefetch on hover, on focus, or on the next likely
user action.

5.7 Deduplicate by Default
The data-fetching library deduplicates by query key. Do not disable
this unless there is a specific reason.

5.8 staleTime Is a Decision, Not a Default
staleTime: 0 for data that must always be fresh.

staleTime: 60_000 for data that changes slowly (user profile,
settings).

staleTime: Infinity for data that never changes during a session
(a static list of countries).

Do not leave staleTime at its default without a reason.

6. Mutations
6.1 Mutations Belong to the Data-Fetching Library
Mutations use the same library's useMutation (or equivalent). They
are not raw service calls from event handlers.

6.2 Invalidate, Do Not Manually Update
After a successful mutation, invalidate the affected queries. Let the
library refetch.

BAD:

typescript
await updateUser(id, data);
queryClient.setQueryData(["user", id], data);
GOOD:

typescript
await updateUser(id, data);
queryClient.invalidateQueries({ queryKey: ["user", id] });
Manual updates drift from the server when validation, defaults, or
server-side timestamps are involved.

6.3 Optimistic Updates Are Opt-In
Optimistic updates are correct only when:

The server is unlikely to reject the mutation.

The rollback is straightforward.

The user experience genuinely benefits.

Implement with onMutate (capture the previous state), onError
(rollback), and onSettled (invalidate to reconcile).

6.4 Mutations Return the Server's Response
A mutation's onSuccess receives the server's response. Use it when
the server returns updated data. Do not assume the client's payload is
what the server stored.

6.5 Disable the Trigger During Submission
The submit button, the link, or whatever triggers the mutation is
disabled while isPending is true. Double-submission causes duplicate
records on the server.

6.6 One Mutation Per Action
A single "save everything" mutation that updates user, settings, and
notifications is hard to invalidate and hard to roll back. Split into
one mutation per resource.

7. Error Handling
7.1 One Error Normalizer
The project has one function that turns any thrown error (HTTP error,
network failure, parse error) into a consistent shape:

typescript
type AppError = {
  kind: "network" | "http" | "validation" | "unknown";
  status?: number;
  message: string;
  cause?: unknown;
};
Every layer that catches errors uses it.

7.2 HTTP Errors Are Not Exceptions to Ignore
A 4xx response is a failure. The service throws (or returns an error
result). The component shows the error. Never treat a 404 or 500 as
"no data".

7.3 Network Errors Are Distinct From Validation Errors
The user cannot fix a network error by changing input. The UI shows a
different message and a different action (Retry vs Fix).

7.4 Never catch and Do Nothing
BAD:

typescript
try {
  await saveUser(data);
} catch (e) {
  // silence
}
GOOD:

typescript
try {
  await saveUser(data);
} catch (error) {
  reportError(error);
  throw error;
}
7.5 Never catch (e: any)
catch receives unknown in TypeScript with useUnknownInCatchVariables.
Type-guard before using .message or .status.

7.6 Error Messages Are User-Facing
The raw server message may contain stack traces, internal paths, or
identifiers. Map server errors to user-facing messages.

BAD: Showing "PostgresError: duplicate key value violates unique constraint users_email_key" to the user.
GOOD: "This email is already registered."

7.7 Global Error Boundary
Unexpected render errors are caught by an error boundary. The boundary
reports to the project's error-tracking service and shows a fallback
UI. Do not rely on the browser's default error page.

8. Cache Invalidation
8.1 Invalidation Strategy Is Explicit
For each mutation, list which query keys it invalidates. If the list
is not obvious, the query keys are too broad.

8.2 Prefer Broad Invalidation Over None
Invalidating too much is slow but correct. Invalidating nothing is
fast but wrong. When unsure, invalidate broadly and measure.

8.3 Never Rely on Manual Cache Updates Alone
Manual cache updates (via setQueryData) bypass validation and
server-side computations. Use them only when an optimistic update is
required, and always follow with an invalidation.

8.4 Cache Eviction Is the Library's Job
Do not manually remove cache entries. Configure gcTime (or
cacheTime in older libraries) and staleTime. The library handles
eviction.

9. URL and Query Params
9.1 The URL Is the Source of Truth for Resource Identity
Which user, which project, which filter, which page. The URL holds it.

9.2 Read Query Params Through the Router
BAD:

typescript
const params = new URLSearchParams(window.location.search);
GOOD:

typescript
const [searchParams] = useSearchParams();
const page = Number(searchParams.get("page") ?? "1");
The router is the single source. window.location bypasses it.

9.3 Validate Query Params
A ?page=abc should not produce NaN. Parse and validate with the
project's schema library or with explicit defaults.

9.4 Never Store the URL's State in a Store
Covered in 02-state-anti-slop.md section 3.5. Repeating: the URL is
the source of truth. Duplicating it in a store creates two sources.

10. Authentication in Requests
10.1 Token in Interceptor, Not at Call Site
Covered in 3.3.

10.2 401 Handling Is Centralized
A 401 response triggers one central action: refresh the token, or
redirect to login. Not a per-component handler.

10.3 Token Refresh Is Deduplicated
If five requests fail with 401 simultaneously, the token refreshes
once, not five times. Use a shared promise for the refresh.

10.4 Never Retry a Mutation Automatically on 4xx
A POST that failed with 409 will fail again. Retry only network errors
and 5xx, with backoff, and only for idempotent operations.

10.5 Logout Clears All Cached Data
After logout, clear the query cache. Otherwise the next user sees the
previous user's data for a moment before the new fetch resolves.

11. API & Data Anti-Patterns
11.1 Fetch in useEffect Without Cleanup
Covered in 2.1. The effect runs on every relevant render, races
between responses, and never cancels.

11.2 Manual Loading State
BAD:

tsx
const [loading, setLoading] = useState(false);
const [error, setError] = useState(null);
const [data, setData] = useState(null);
The data-fetching library already tracks these three. Do not
reimplement.

11.3 Manual Retry Logic
The HTTP client or the data-fetching library already retries. Adding
a for loop around a fetch duplicates the logic and produces
unexpected request counts.

11.4 try/catch in Every Service Function
If the client has an interceptor that handles errors, individual
services do not need to. Centralize.

11.5 console.log in the API Layer
Use the project's logger (or nothing). Console output ships to
production in most builds.

11.6 Type Assertion on Response
Covered in 4.1.

11.7 Pointless Wrappers
BAD:

typescript
export const getUsers = () => httpClient.get("/users");
export const getPosts = () => httpClient.get("/posts");
export const getComments = () => httpClient.get("/comments");
Each wrapper adds a layer but no typing, no schema, and no error
handling. Add a service function when it does something: parse,
transform, unwrap, type.

11.8 Manual Cache
Any caching that does not go through the data-fetching library. It
will leak, stale, or race. Let the library own caching.

11.9 Error Handling per File
Every file catches errors differently. The user sees inconsistent
messages. Normalize once.

11.10 try/catch That Rethrows
BAD:

typescript
try {
  return await getUser(id);
} catch (error) {
  throw error;
}
This adds nothing. Remove it.

11.11 Toast Inside the Service
BAD: A service function that calls toast.error("Failed").
GOOD: The service throws; the component decides whether to toast,
inline-error, or redirect.

A toast in a service fires on every call site, including background
refetches, even when the user did not initiate the request.

11.12 Missing await on a Promise-Returning Service
BAD:

typescript
function saveUser(data) {
  updateUser(data); // returns a Promise, not awaited
}
The caller thinks the save completed. It did not.

11.13 Ignoring the Server's Response
BAD:

typescript
await updateUser(data);
// assume the server stored exactly what was sent
The server may add updatedAt, normalize fields, or reject silently.
Use the server's response.

11.14 Fetching the Same Data in Sibling Components
Two components independently call useUser(id). The data-fetching
library deduplicates. Without one, two requests are sent.

11.15 Not Handling Offline
A request that fails because the browser is offline is different from
a 500. The UI should distinguish them if the project cares about
offline users.

11.16 Over-Fetching
Fetching a full user object to render a name. Ask the backend for the
fields needed (?fields=name), or use a lighter endpoint.

11.17 Under-Fetching and Follow-Up Requests
Fetching a list, then fetching each item to render. Use a single
endpoint that returns what is needed, or a joined query.

11.18 Serial Requests When Parallel Is Possible
BAD:

typescript
const user = await getUser(id);
const posts = await getPosts(id);
const comments = await getComments(id);
If the three are independent, fire them in parallel:

typescript
const [user, posts, comments] = await Promise.all([
  getUser(id), getPosts(id), getComments(id),
]);
Do not parallelize dependent requests.

11.19 Never Hardcode the API Base URL
Covered in 3.1. Environment variables per deployment.

11.20 Never Send the Token in a Query String
Tokens in URLs are logged by proxies, stored in browser history, and
leaked via referrer headers. Always the Authorization header.

12. Response to Violation
If a previous response violated a rule here:

text
In the previous response, [specific rule] was violated. Correction:
[corrected code]
No justification. No apology paragraph. Fix and move on.



---
