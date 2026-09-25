---
id: 02-astro-anti-slop
title: "Astro Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-frontend-anti-slop]
category: domain
domain_type: framework
version: 1
---
# Astro Anti-Slop Layer

Layered under the master, architecture, and frontend layers. This file adds Astro page, island, content-collection, rendering, and hydration rules.

## 1. Stack Assumptions

1. Read the installed Astro major version before using collection or island APIs.
2. Use Astro's server-rendered default for content-first pages.
3. Use framework components only where interactive behavior is required.
4. Keep islands small and independently owned.
5. Use the repository's content schema and data-fetching boundary.
6. Do not add a client-side router when Astro pages are sufficient.
7. Keep secrets in server endpoints or server-rendering modules.
8. Match the repository's output and adapter configuration.

## 2. Pages and Components

1. Keep `.astro` pages focused on layout, content, and server composition.
2. Extract repeated UI into components with typed props.
3. Use `.astro` components for static presentation and framework components for stateful interaction.
4. Keep frontmatter free of unrelated business logic.
5. Do not turn every page into a client component.
6. Keep accessibility semantics in the server-rendered tree.
7. Use explicit slots and named slots when composition is dynamic.
8. Keep styles scoped to their component unless the design system requires a global token file.

BAD:

```astro
---
const response = await fetch("/api/users");
const users = await response.json();
---
<ul>{users.map((user) => <li>{user.name}</li>)}</ul>
<script>
  const users = JSON.parse(document.body.dataset.users);
</script>
```

GOOD:

```astro
---
import UserList from "../components/UserList.astro";
const users = await listUsers();
---
<UserList users={users} />
```

## 3. Islands Architecture

1. Hydrate only controls that need browser state or event handling.
2. Choose the narrowest supported client directive for each island.
3. Keep island props serializable.
4. Do not pass an entire server data graph to an interactive component.
5. Keep island state local unless multiple islands require shared state.
6. Avoid hydrating a static list for a CSS-only interaction.
7. Place the client boundary at the interactive subtree, not the page root, when possible.
8. Measure bundle and hydration cost before adding another island.

BAD:

```astro
---
import Dashboard from "../components/Dashboard.tsx";
---
<Dashboard client:load data={entireApplicationState} />
```

GOOD:

```astro
---
import { getEntry } from "astro:content";
import Counter from "../components/Counter.tsx";
const entry = await getEntry("counters", "home");
if (!entry) return Astro.redirect("/404");
---
<Counter client:idle initialCount={entry.data.count} />
```

```tsx
import { useState } from "react";
export default function Counter({ initialCount }: { initialCount: number }) {
  const [count, setCount] = useState(initialCount);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```

Each island owns its mutable state and never reads or writes shared application state.

## 4. Data Fetching

1. Fetch during server rendering when data is needed for the initial page.
2. Use a repository-level data module for endpoint, schema, and error policy.
3. Handle loading and failure states for interactive islands.
4. Avoid fetching in every list item.
5. Set bounded timeouts and cache headers according to data sensitivity.
6. Do not expose private server responses to a client island.
7. Use a client data library only when interaction requires it.
8. Keep pagination and filtering in the server or adapter boundary.

## 5. Content Collections

1. Define collection schemas in the repository's content configuration.
2. Validate frontmatter and content fields before rendering.
3. Keep collection names and entry files consistent with the configured loader.
4. Query collections through a small content data boundary.
5. Do not import an entire collection when one entry is needed.
6. Keep generated content types checked in the project's validation command.
7. Handle missing or invalid entries explicitly.
8. Do not use collections as an untyped database for mutable application data.

BAD:

```ts
const posts = await getCollection("blog");
return posts.map(post => <Post data={post.data} />);
```

GOOD:

```ts
const posts = await getCollection("blog", ({ data }) => data.published);
const post = await getEntry("blog", slug);
if (!post) return Astro.redirect("/404");
return <Post data={post.data} />;
```

## 6. Server Endpoints and Rendering

1. Keep `src/pages/api` handlers transport-focused.
2. Validate request method and payload at the endpoint boundary.
3. Use server-only configuration for secrets.
4. Authenticate and authorize protected endpoints.
5. Return explicit status codes and safe errors.
6. Do not expose filesystem paths or stack traces.
7. Close external resources on every response path.
8. Use server rendering for personalized pages when the adapter supports it.

## 7. Styling and Assets

1. Use design tokens from the existing design system.
2. Keep images and fonts on Astro's asset and font APIs when available.
3. Provide dimensions for images that affect layout.
4. Do not load a full component framework for one static section.
5. Keep client scripts small and purpose-specific.
6. Avoid global scripts that affect every page without a project reason.
7. Preserve reduced-motion and focus behavior.

## 8. Routing and Metadata

1. Use Astro's file-based routes and dynamic parameter validation.
2. Keep layouts stable and page content route-specific.
3. Generate metadata through the repository's supported API.
4. Do not construct unvalidated URLs.
5. Test direct loads, missing entries, and server errors.
6. Keep redirects explicit and avoid redirect loops.
7. Preserve canonical URLs and language settings.

## 9. Domain-Specific Anti-Patterns

### 9.1 Hydrating the Page Shell

BAD:

```astro
---
import PageShell from "../components/PageShell.tsx";
---
<PageShell client:load><main>Static article</main></PageShell>
```

GOOD:

```astro
---
import LikeButton from "../components/LikeButton.tsx";
---
<main><h1>Static article</h1><LikeButton client:idle articleId={article.id} /></main>
```

### 9.2 Unvalidated Collection Data

BAD:

```ts
const entry = await getEntry("docs", slug);
if (!entry) return Astro.redirect("/404");
return <Doc data={entry.data} />;
```

GOOD:

```ts
import { z } from "astro:content";

const postSchema = z.object({
  title: z.string().min(1),
  published: z.boolean(),
  count: z.number().int().nonnegative(),
});

const entry = await getEntry("blog", slug);
if (!entry) return Astro.redirect("/404");
const data = postSchema.parse(entry.data);
return <Post data={data} />;
```

The parse result is the only data passed to the component. A collection schema
or an equivalent guard belongs at the content boundary, not only in a page.

### 9.3 Island State Leaking Across Pages

BAD:

```astro
<Counter client:load count={applicationState.count} />
```

GOOD:

```astro
---
import { getEntry } from "astro:content";
const entry = await getEntry("counters", "home");
if (!entry) return Astro.redirect("/404");
---
<Counter client:visible count={entry.data.count} />
```

## 10. Response to Violation

If a previous response violated this file, use this structure:

```text
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

Identify the rule and show the correction. Do not add an apology paragraph.
