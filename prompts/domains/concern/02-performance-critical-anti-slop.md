---
id: 02-performance-critical-anti-slop
title: "Performance-Critical Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: concern
version: 1
---

# Performance-Critical Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
security anti-patterns, output format) are NOT repeated here.

This file is sent for projects where performance is a first-class
requirement with a measurable budget: high-frequency trading, gaming,
real-time collaboration, embedded systems, large data visualization,
media processing, and any product where latency or throughput directly
affects the user or the business.

For most projects, the baseline performance rules in
`domains/framework/02-react-anti-slop.md` and
`domains/delivery/02-frontend-anti-slop.md` are sufficient. This file
is for the subset of projects where a specific metric must be met and
optimization decisions have consequences.

## 1. When This File Applies

Send this file when the project is:

- Real-time or latency-sensitive (trading, gaming, live collaboration,
  voice, video).
- Throughput-sensitive (batch processing, data pipelines, log
  aggregation).
- Resource-constrained (embedded, mobile, low-end devices).
- Large-scale (millions of users, petabytes of data).
- Under a specific performance contract (SLO, SLA, frame budget).

If the project has no defined performance requirement, this file is
premature. Optimize when there is a measurement, not before.

## 2. The Discipline: Measure, Then Change

### 2.1 No Optimization Without Measurement

BAD: "This code looks slow. Let me rewrite it."
GOOD: A profiler trace showing where the time is spent.

The default state of any code is "not yet measured". Do not optimize
what you have not measured. Do not optimize what the profile does not
show as a bottleneck.

### 2.2 Measure in the Real Environment

Profiling in development mode is misleading:

- JavaScript builds are unminified and unbundled.
- Python is often run with assertions on.
- Go's race detector changes timings.
- Caches are cold.
- The dataset is small.

Measure in an environment that matches production: same build, same
dataset size, same cache state, same concurrency.

### 2.3 Define the Budget Before Optimizing

A performance target is a number:

- "First contentful paint under 1.5s on a 4G connection."
- "p99 latency under 100ms."
- "60 FPS sustained during interaction."
- "Memory under 256 MB."
- "Throughput of 10,000 requests per second per node."

Without a number, "fast enough" is a feeling.

### 2.4 Optimize the Bottleneck, Not the Code

A profile shows the distribution of time. Optimizing the top 5% may
not matter if the top 1% is 80% of the time. Amdahl's law applies.

### 2.5 Measure After the Change

An optimization that is not measured after the change is a guess. The
profile after must show the expected improvement, or the change is
reverted.

### 2.6 Cost of Optimization

Every optimization trades simplicity for speed. Before applying:

- How much complexity is added?
- How much of the speed is gained?
- Will the next developer understand it?
- Is the gain worth the cost?

A 5% speedup that makes the code unreadable is usually a net loss.

## 3. Frontend Performance

### 3.1 Core Web Vitals

- **LCP** (Largest Contentful Paint): under 2.5s.
- **INP** (Interaction to Next Paint): under 200ms.
- **CLS** (Cumulative Layout Shift): under 0.1.

These are the metrics Google uses. If the project is a web frontend,
they are the baseline.

### 3.2 Other Metrics

- **TTFB** (Time to First Byte): server responsiveness.
- **FCP** (First Contentful Paint): first visible content.
- **TBT** (Total Blocking Time): main-thread congestion.
- **Bundle size**: JavaScript transferred to the client.

Each metric has a target. Define them for the project.

### 3.3 Rendering

- Do not block the main thread with long tasks (>50ms).
- Break long tasks with `requestIdleCallback`, `scheduler.yield`, or
  chunking.
- Use `content-visibility: auto` for off-screen content.
- Use CSS containment (`contain: layout style paint`) for isolated
  subtrees.
- Avoid synchronous layout thrashing (read then write in a loop).

### 3.4 Images

- Serve modern formats (WebP, AVIF) with fallbacks.
- Specify `width` and `height` to prevent CLS.
- Use `loading="lazy"` for off-screen images.
- Use `srcset` and `sizes` for responsive images.
- Do not serve a 4K image for a 200px thumbnail.

### 3.5 Fonts

- `font-display: swap` or `optional` to avoid invisible text.
- Subset fonts to the characters used.
- Preload the primary font.
- Avoid web fonts when a system font stack works.

### 3.6 JavaScript

- Ship less of it.
- Code-split by route and by heavy component.
- Never import a full library when a smaller one exists.
- Never `import *` from a tree-shakeable library.
- Defer non-critical scripts.
- Prefer native browser APIs over polyfills for modern targets.

### 3.7 CSS

- No unused CSS in the critical path.
- Avoid deeply nested selectors (high specificity).
- Avoid `!important` (it forces re-evaluation).
- Use `will-change` sparingly; too many layers consume memory.
- Avoid animating layout properties (`width`, `height`, `top`,
  `left`). Animate `transform` and `opacity`.

### 3.8 Third-Party Scripts

Each third-party script is:

- Additional bytes.
- Additional parsing and execution time.
- A potential source of main-thread blockage.
- A privacy and security cost.

Audit them. Load them after the critical path. Consider
self-hosting.

### 3.9 Data Fetching on the Client

- Do not fetch data the server already has.
- Do not fetch in series what can be fetched in parallel.
- Do not refetch data that is fresh.
- Do not fetch on every mount when the cache would suffice.

### 3.10 Memory

- Long-lived subscriptions (event listeners, WebSockets, observers)
  are cleaned up on unmount.
- Detached DOM nodes are not held in closures.
- Large data structures are released when no longer needed.
- `WeakMap` and `WeakRef` where appropriate, not where unnecessary.

## 4. Backend Performance

### 4.1 Latency Budget

Define the latency budget for the endpoint:

- Total budget: p99 under 100ms.
- Database: 30ms.
- External services: 40ms.
- Business logic: 20ms.
- Serialization: 10ms.

Every part is measured. A part that exceeds its budget is the target.

### 4.2 Database Queries

- No N+1 (covered in `02-database-anti-slop.md`).
- Index every filter and sort column.
- Use `EXPLAIN ANALYZE` on production-sized data.
- Never `SELECT *`.
- Never `OFFSET` for deep pagination (use cursor).
- Batch writes where possible.
- Pool connections; do not open one per request.

### 4.3 Caching

- Cache at the right layer (CDN, application, database query cache).
- Invalidate precisely, not broadly.
- Define TTL for every cache.
- Handle cache stampede (dogpile) with a lock or a probabilistic
  early refresh.
- Never cache PII without encryption and access control.
- Measure cache hit rate; a cache below 80% is usually misconfigured.

### 4.4 Concurrency

- Do not process sequentially what can be parallel.
- Do not parallelize dependent operations.
- Use a bounded worker pool for CPU-bound tasks.
- Use asynchronous I/O for network and disk.
- Respect backpressure from downstream services.

### 4.5 Serialization

- JSON is fast enough for most cases. Protobuf, MessagePack, and
  FlatBuffers are faster but add complexity.
- Avoid serializing fields the client does not need.
- Avoid double-serialization (JSON in JSON).
- Response compression (`gzip`, `brotli`) is mandatory for text.

### 4.6 Memory

- Avoid loading entire tables into memory.
- Stream large responses.
- Paginate large result sets.
- Profile heap allocation; reduce object churn in hot paths.
- Reuse buffers where the language and framework support it.

### 4.7 Startup Time

- For serverless and CLI, startup time matters.
- Lazy-load what is not needed at boot.
- Precompile what can be precompiled.
- Avoid network calls during startup.

### 4.8 CPU

- Profile before micro-optimizing.
- Reduce allocations in hot loops.
- Avoid regex in hot paths; compile once, use many times.
- Use the language's fast primitives (avoid reflection, avoid dynamic
  dispatch where a static one works).

## 5. Profiling Tools

### 5.1 Frontend

- Chrome DevTools Performance panel.
- Lighthouse.
- WebPageTest.
- `performance.mark` and `performance.measure` for custom timings.
- React DevTools Profiler for React.
- Bundle analyzers (`webpack-bundle-analyzer`, `vite-bundle-visualizer`).

### 5.2 Backend

- Language-specific profilers: `pprof` (Go), `cProfile` /
  `py-spy` (Python), `clinic` / `--prof` (Node.js), `perf` (native),
  `JFR` (Java).
- Distributed tracing: OpenTelemetry, Jaeger, Tempo.
- APM: Datadog, New Relic, Elastic APM.

### 5.3 Database

- `EXPLAIN` and `EXPLAIN ANALYZE`.
- Slow query logs.
- `pg_stat_statements` (PostgreSQL).
- Query profilers in the ORM.

### 5.4 System

- `top`, `htop`, `iostat`, `vmstat`.
- Flame graphs.
- `strace` for syscall tracing.
- `tcpdump` for network.

## 6. Performance Patterns

### 6.1 Batching

Combine small operations into larger ones. One database round trip
for 100 rows beats 100 round trips.

### 6.2 Debouncing and Throttling

- Debounce: run after the user stops (search input).
- Throttle: run at most N times per interval (scroll handler).

Never debounce the critical path of a user action.

### 6.3 Lazy Loading

Load on demand:

- Images: `loading="lazy"`.
- Components: dynamic `import()`.
- Data: fetch when the section becomes visible.
- Database: fetch columns on access (ORM lazy loading), but beware
  N+1.

### 6.4 Prefetching

Load before the user asks:

- Prefetch the next route on hover.
- Prefetch DNS, TCP, TLS with `<link rel="preconnect">`.
- Prefetch resources with `<link rel="prefetch">`.
- Do not prefetch everything; bandwidth is a budget.

### 6.5 Memoization

Cache the result of an expensive computation. Invalidate when inputs
change. Beware memory growth with unbounded caches.

### 6.6 Concurrency

Run independent work in parallel. Do not run dependent work in
parallel.

### 6.7 Streaming

Send data as it is produced rather than buffering everything:

- HTTP chunked responses.
- Server-sent events.
- WebSocket frames.
- Database cursors.

### 6.8 Compression

`gzip` for text. `brotli` for smaller. `zstd` for very high
compression. Never compress already-compressed data (images, video).

### 6.9 Connection Reuse

- HTTP keep-alive.
- Database connection pooling.
- gRPC channels reused.
- WebSocket for repeated small messages.

### 6.10 Backpressure

When a producer is faster than a consumer, the producer must slow
down. Unbounded queues lead to memory exhaustion. Apply backpressure
at every boundary.

## 7. Performance Anti-Patterns

### 7.1 Premature Optimization

Optimizing code that has not been measured. The three rules of
optimization: measure, measure, measure.

### 7.2 `useMemo` and `useCallback` Everywhere

Covered in `02-react-anti-slop.md`. Repeating: memoization has a
cost. Use it after profiling.

### 7.3 Synchronous I/O in a Server

BAD: `fs.readFileSync`, `requests.get` (blocking), blocking database
drivers in an async runtime.

Each blocks the entire worker. On a busy server, this is catastrophic.

### 7.4 Unbounded Queries

BAD: `SELECT * FROM events` with no `LIMIT`. On a table with 10M
rows, this crashes the server.

Always paginate. Always.

### 7.5 N+1 Queries

Covered in `02-database-anti-slop.md`.

### 7.6 Regex in Hot Paths

A regex compiled once and used many times is fine. A regex compiled
on every call, or a poorly written regex (ReDoS), is not.

### 7.7 Excessive Logging in Hot Paths

BAD: `logger.debug(JSON.stringify(request))` on every request.
This serializes and writes on every call.

Log at the appropriate level. Sample verbose logs.

### 7.8 String Concatenation in Loops

Covered in `02-go-anti-slop.md` section 14.15. Applies to every
language: use the language's builder or buffer.

### 7.9 Array `push` Without Preallocation

In languages with preallocatable arrays (`make` in Go, `new
Array(n)` in JavaScript), preallocation avoids repeated resizing.

### 7.10 Over-Serialization

BAD: Loading a full ORM entity with 30 relations to render a name.
GOOD: A projection query that returns only the name.

### 7.11 Cache Without Invalidation

Covered in 4.3. Repeating: a cache that never invalidates is a cache
that serves stale data forever.

### 7.12 Cache Stampede

When a popular cache entry expires, hundreds of requests hit the
backend simultaneously to rebuild it. Prevent with:

- A lock (only one request rebuilds).
- Probabilistic early refresh.
- Staggered TTLs.

### 7.13 `SELECT COUNT(*)` on Large Tables

On a table with 100M rows, this is a full scan. Use approximate
counts (`pg_class.reltuples`), a cached count, or a separate
counter table.

### 7.14 Missing Index on Foreign Keys

Covered in `02-database-anti-slop.md` section 5.1.

### 7.15 Deep Pagination With `OFFSET`

`OFFSET 100000 LIMIT 20` scans 100,020 rows and returns 20. Use
cursor-based pagination (`WHERE id > last_id ORDER BY id LIMIT 20`).

### 7.16 Synchronous Rendering of Large Lists

Rendering 10,000 rows to the DOM freezes the browser. Virtualize.

### 7.17 Layout Thrashing

BAD:
javascript
for (const el of elements) {
  el.style.width = el.offsetWidth + 10 + "px"; // read, write, read, write
}
Each read forces a layout recalculation. Batch reads and writes.

7.18 Memory Leaks
Subscriptions, listeners, timers, closures holding large objects.
Each is a slow leak that grows over time.

7.19 Excessive Re-renders
Covered in 02-react-anti-slop.md and 02-state-anti-slop.md.

7.20 Unbounded Concurrency
BAD: await Promise.all(urls.map(fetch)) with 100,000 URLs. This
opens 100,000 connections.

GOOD: A bounded pool of 10-100 concurrent operations.

7.21 Retry Storms
A failing downstream service triggers retries. The retries add load,
making the failure worse. Use exponential backoff with jitter and a
circuit breaker.

7.22 Thundering Herd on Startup
A service starts and immediately hammers its dependencies. Use
jittered delays or a warmup.

7.23 Ignoring the Cost of Third-Party Scripts
A single analytics script can add 200ms to LCP. Audit them.

7.24 Micro-Optimizing Before Macro
Optimizing a 0.1ms function while the page takes 5s to load.

Fix the biggest problem first. Always.

7.25 Optimizing for the Wrong Metric
Reducing bundle size when the problem is server latency. Reducing
server latency when the problem is database queries. Measure the
whole chain.

8. Performance Budget Enforcement
8.1 Budget in CI
A performance budget that is not enforced regresses. Run Lighthouse
in CI. Fail the build when the budget is exceeded.

8.2 Bundle Size Limits
Set a maximum bundle size. A new dependency that pushes over the
limit fails the build.

8.3 Query Count Limits
Some frameworks (Rails, Django) can assert a maximum query count
per request in tests. Use it.

8.4 Regression Tests
A benchmark suite that runs on every commit. A change that regresses
performance by more than X% fails.

8.5 Alerting
Production metrics (latency, error rate, throughput) alert when they
deviate from the SLO. Performance is not a one-time fix; it is a
property that must be maintained.

9. Trade-Offs
9.1 Speed vs Readability
A faster algorithm is often less readable. Document the trade-off
in a comment. Reference the benchmark.

9.2 Speed vs Correctness
Never trade correctness for speed. A fast wrong answer is worse than
a slow right one.

9.3 Memory vs Speed
Caching trades memory for speed. Unbounded caches trade memory for
out-of-memory errors. Bound every cache.

9.4 Latency vs Throughput
Batching improves throughput but increases latency. Choose based on
the user's experience.

9.5 Consistency vs Availability
From the CAP theorem. Do not pretend the trade-off does not exist.

9.6 Developer Time vs Runtime
An optimization that saves 5ms but takes a week to implement and a
week to review may not be worth it. Ask the user.

10. Response to Violation
If a previous response violated a rule here:

text
In the previous response, [specific rule] was violated. Correction:
[corrected code]
No justification. No apology paragraph. Fix and move on.

If the violation is a performance regression in already-shipped
code, add a note: "This may affect the SLO. Measure in the target
environment before deploying."

text

---
