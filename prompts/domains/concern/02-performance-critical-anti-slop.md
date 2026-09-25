---
id: 02-performance-critical-anti-slop
title: "Performance-Critical Anti-Slop Layer"
lang: en
depends_on: ["_universal/00-style-guide.md", "_universal/00-master-anti-slop.md"]
category: domain
domain_type: concern
version: 2
---

# Performance-Critical Anti-Slop Layer

This file defines behavioral contracts specific to performance-critical systems. It sits in the concern layer, below the universal anti-slop rules and alongside other cross-cutting concerns. It covers measurement discipline, frontend and backend optimization, resource management, caching, concurrency, and budget enforcement. It does not cover baseline frontend performance (see `02-frontend-anti-slop.md`), baseline database query performance (see `02-database-anti-slop.md`), language-specific memory management (see language files), or framework-specific rendering optimizations (see framework files).

For most projects, the baseline performance rules in the delivery and framework layers are sufficient. This file is for the subset of projects where a specific metric must be met and optimization decisions have measurable business or user consequences.

## When This File Applies

This file MUST be sent when at least one of the following objective criteria is met:

- The system is real-time or latency-sensitive (high-frequency trading, gaming, live collaboration, voice, video).
- The system is throughput-sensitive (batch processing, data pipelines, log aggregation).
- The system is resource-constrained (embedded, mobile, low-end edge devices).
- The system operates at large scale (millions of concurrent users, petabytes of data).
- The project is bound by a specific performance contract (SLO, SLA, frame budget, Core Web Vitals target).

This file does NOT apply to: internal tools with no strict latency requirements, early-stage prototypes without defined SLOs, or projects where baseline delivery-layer performance rules suffice. Optimize when there is a measurement, not before.

## Scope

This file applies to frontend applications, backend services, databases, and system-level architectures where performance is a first-class requirement. The principles are tool-agnostic. The examples use JavaScript/TypeScript, Go, Python, and SQL syntax where illustrative. Language-specific primitives (e.g., Go channels, Rust lifetimes) live in language files. Framework-specific hooks (e.g., React `useMemo`) live in framework files.

## Concern Budgets

Performance-critical projects MUST operate within these measurable thresholds:

| Concern | Threshold | Verification Method | Rule |
|---|---|---|---|
| LCP (Largest Contentful Paint) | < 2.5s | Lighthouse / WebPageTest | PERF-007 |
| INP (Interaction to Next Paint) | < 200ms | Lighthouse / CWV | PERF-007 |
| CLS (Cumulative Layout Shift) | < 0.1 | Lighthouse / CWV | PERF-007 |
| Main Thread Task Duration | < 50ms | Chrome DevTools Performance | PERF-009 |
| p99 API Latency | Defined per SLO (e.g., < 100ms) | APM / Distributed Tracing | PERF-018 |
| Cache Hit Rate | >= 80% | Cache Telemetry | PERF-020 |

## Rule Severity

Severity follows `_universal/00-style-guide.md`. Violations in this file typically result in degraded user experience, SLO breaches, or infrastructure cost overruns.

## Contracts

A performance-critical system commits to five contracts. The table below maps each contract to the rules that enforce it.

| Contract | Description | Enforced By |
|---|---|---|
| Measurement Discipline | Optimization is driven by profiler data in production-like environments, not assumptions. | PERF-001 to PERF-006 |
| Frontend Performance | Core Web Vitals are met, main thread is unblocked, and assets are optimized. | PERF-007 to PERF-017 |
| Backend Performance | Latency budgets are defined, queries are bounded, and concurrency is controlled. | PERF-018 to PERF-025 |
| Resource Management | Memory, CPU, and connections are bounded; backpressure is enforced. | PERF-026 to PERF-033, PERF-041 |
| Budget Enforcement | Performance budgets are enforced in CI and monitored in production. | PERF-034 to PERF-038 |

## Measurement Discipline

### PERF-001 — No Optimization Without Measurement

**MUST NOT**

Code MUST NOT be optimized without a profiler trace showing where the time is spent. The default state of any code is "not yet measured". Optimizing what the profile does not show as a bottleneck is prohibited.

### PERF-002 — Production-Like Measurement

**MUST**

Profiling MUST occur in an environment that matches production: same build (minified/bundled), same dataset size, same cache state, and same concurrency. Profiling in development mode (unminified JS, assertions on, cold caches) is misleading.

### PERF-003 — Explicit Budget Definition

**MUST**

A performance target MUST be a specific number (e.g., "p99 latency under 100ms", "60 FPS sustained", "Memory under 256 MB"). "Fast enough" is not a valid target.

### PERF-004 — Bottleneck Focus

**MUST**

Optimization MUST target the bottleneck identified by the profile. Optimizing the top 5% of operations when the top 1% consumes 80% of the time violates Amdahl's law.

### PERF-005 — Post-Change Measurement

**MUST**

An optimization MUST be measured after the change. The profile after the change MUST show the expected improvement; otherwise, the change MUST be reverted.

### PERF-006 — Optimization Cost Evaluation

**SHOULD**

Before applying an optimization, the trade-off between added complexity and speed gained SHOULD be evaluated. A marginal speedup that makes the code unreadable is usually a net loss.

## Frontend Performance

### PERF-007 — Core Web Vitals Baseline

**MUST**

Web frontends MUST meet the Core Web Vitals thresholds: LCP < 2.5s, INP < 200ms, CLS < 0.1. These are the baseline metrics for user experience and search ranking.

### PERF-008 — Frontend Metric Targets

**MUST**

Secondary metrics (TTFB, FCP, TBT, Bundle Size) MUST have defined targets for the project.

### PERF-009 — Main Thread Non-Blocking

**MUST NOT**

The main thread MUST NOT be blocked with long tasks (>50ms). Long tasks MUST be broken using `requestIdleCallback`, `scheduler.yield`, or chunking.

### PERF-010 — Layout Thrashing Prevention

**MUST NOT**

Synchronous layout thrashing (reading DOM geometry then writing DOM styles in a loop) MUST NOT occur. Reads and writes MUST be batched.

Example (illustrative, JavaScript):

BAD:
```javascript
for (const el of elements) {
  el.style.width = el.offsetWidth + 10 + "px"; // read, write, read, write
}
```

### PERF-011 — Image Optimization

**MUST**

Images MUST be served in modern formats (WebP, AVIF) with fallbacks. `width` and `height` MUST be specified to prevent CLS. `loading="lazy"` MUST be used for off-screen images. `srcset` and `sizes` MUST be used for responsive images. Serving oversized images (e.g., 4K for a 200px thumbnail) is prohibited.

### PERF-012 — Font Loading Discipline

**MUST**

Web fonts MUST use `font-display: swap` or `optional` to avoid invisible text. Fonts MUST be subset to the characters used. The primary font SHOULD be preloaded. System font stacks SHOULD be preferred when web fonts are unnecessary.

### PERF-013 — JavaScript Payload Minimization

**MUST**

JavaScript payloads MUST be minimized. Code MUST be split by route and heavy component. Full libraries MUST NOT be imported when a smaller alternative exists. `import *` from tree-shakeable libraries MUST NOT be used. Non-critical scripts MUST be deferred.

### PERF-014 — CSS Critical Path Discipline

**MUST**

Unused CSS MUST NOT be in the critical path. Deeply nested selectors and `!important` MUST be avoided. `will-change` MUST be used sparingly. Layout properties (`width`, `height`, `top`, `left`) MUST NOT be animated; `transform` and `opacity` MUST be used instead.

### PERF-015 — Third-Party Script Audit

**MUST**

Third-party scripts MUST be audited for byte size, parsing time, and main-thread blockage. They MUST be loaded after the critical path. Self-hosting SHOULD be considered.

### PERF-016 — Client Data Fetching Discipline

**MUST NOT**

The client MUST NOT fetch data the server already has, fetch in series what can be parallelized, refetch fresh data, or fetch on every mount when a cache suffices.

### PERF-017 — Frontend Memory Cleanup

**MUST**

Long-lived subscriptions (event listeners, WebSockets, observers) MUST be cleaned up on unmount. Detached DOM nodes MUST NOT be held in closures. Large data structures MUST be released when no longer needed.

## Backend Performance

### PERF-018 — Latency Budget Definition

**MUST**

Every endpoint MUST have a defined latency budget (e.g., Total: 100ms, DB: 30ms, External: 40ms, Logic: 20ms, Serialization: 10ms). Every part MUST be measured against its budget.

### PERF-019 — Database Query Discipline

**MUST**

Database queries MUST be optimized. N+1 queries (see `DB-017`), missing indexes on filter/sort columns, `SELECT *`, and deep `OFFSET` pagination (see `DB-019`) are prohibited. `EXPLAIN ANALYZE` MUST be run on production-sized data. Writes MUST be batched where possible. Connections MUST be pooled.

### PERF-020 — Caching Layer Discipline

**MUST**

Caching MUST occur at the right layer (CDN, application, DB). Invalidation MUST be precise. TTL MUST be defined for every cache. Cache stampedes (dogpiles) MUST be handled with locks or probabilistic early refresh. PII MUST NOT be cached without encryption and access control. Cache hit rates below 80% indicate misconfiguration.

### PERF-021 — Concurrency Discipline

**MUST**

Independent operations MUST be parallelized. Dependent operations MUST NOT be parallelized. CPU-bound tasks MUST use a bounded worker pool. Network and disk I/O MUST use asynchronous operations. Backpressure from downstream services MUST be respected.

### PERF-022 — Serialization Discipline

**MUST**

Serialization formats MUST match the performance requirement (JSON for general use, Protobuf/MessagePack for high throughput). Fields the client does not need MUST NOT be serialized. Double-serialization (JSON in JSON) MUST NOT occur. Text responses MUST be compressed (`gzip`, `brotli`).

### PERF-023 — Backend Memory Discipline

**MUST**

Entire tables MUST NOT be loaded into memory. Large responses MUST be streamed. Large result sets MUST be paginated. Heap allocation MUST be profiled; object churn in hot paths MUST be reduced. Buffers MUST be reused where the language supports it.

### PERF-024 — Startup Time Minimization

**MUST**

For serverless and CLI tools, startup time MUST be minimized. Non-boot dependencies MUST be lazy-loaded. Precompilation SHOULD be used. Network calls during startup MUST NOT occur.

### PERF-025 — CPU Hot Path Discipline

**MUST**

Hot paths MUST be profiled before micro-optimizing. Allocations in hot loops MUST be reduced. Regex MUST be compiled once and reused. Language-specific fast primitives MUST be used (avoiding reflection or dynamic dispatch where static works).

## Performance Patterns

### PERF-026 — Batching

**SHOULD**

Small operations SHOULD be combined into larger ones (e.g., one database round trip for 100 rows instead of 100 round trips).

### PERF-027 — Debounce and Throttle Discipline

**MUST**

Debouncing (run after user stops) MUST be used for search inputs. Throttling (run at most N times per interval) MUST be used for scroll handlers. The critical path of a user action MUST NOT be debounced.

### PERF-028 — Lazy Loading

**SHOULD**

Resources SHOULD be loaded on demand: images (`loading="lazy"`), components (dynamic `import()`), data (on visibility), and database relations (with N+1 caution).

### PERF-029 — Prefetching Discipline

**SHOULD**

Resources SHOULD be loaded before the user asks (e.g., next route on hover, DNS/TCP via `<link rel="preconnect">`). Bandwidth is a budget; everything MUST NOT be prefetched.

### PERF-030 — Memoization Discipline

**MUST**

Expensive computations MAY be memoized. Invalidation MUST occur when inputs change. Unbounded caches MUST NOT be used for memoization to prevent memory growth.

### PERF-031 — Streaming

**SHOULD**

Data SHOULD be sent as it is produced rather than buffered entirely (HTTP chunked, SSE, WebSocket frames, DB cursors).

### PERF-032 — Connection Reuse

**MUST**

Connections MUST be reused: HTTP keep-alive, database connection pooling, gRPC channels, and WebSockets for repeated small messages.

### PERF-033 — Backpressure Enforcement

**MUST**

When a producer is faster than a consumer, the producer MUST slow down. Unbounded queues lead to memory exhaustion. Backpressure MUST be applied at every boundary.

## Budget Enforcement

### PERF-034 — CI Budget Enforcement

**MUST**

Performance budgets MUST be enforced in CI (e.g., Lighthouse CI). The build MUST fail when the budget is exceeded.

### PERF-035 — Bundle Size Limits

**MUST**

A maximum bundle size MUST be set. Dependencies that push the bundle over the limit MUST fail the build.

### PERF-036 — Query Count Limits

**SHOULD**

Frameworks that support asserting a maximum query count per request in tests SHOULD use this feature to prevent N+1 regressions.

### PERF-037 — Regression Testing

**MUST**

A benchmark suite MUST run on every commit. Changes that regress performance beyond an acceptable threshold MUST fail the build.

### PERF-038 — Production Alerting

**MUST**

Production metrics (latency, error rate, throughput) MUST alert when they deviate from the SLO. Performance is a continuous property, not a one-time fix.

## Trade-Offs

### PERF-039 — Speed vs Readability Documentation

**MUST**

When a faster algorithm reduces readability, the trade-off MUST be documented in a comment referencing the benchmark.

### PERF-040 — Correctness Precedence

**MUST NOT**

Correctness MUST NOT be traded for speed. A fast wrong answer is worse than a slow right one.

### PERF-041 — Memory vs Speed Bounding

**MUST**

Caching trades memory for speed. Every cache MUST be bounded to prevent out-of-memory errors.

## AI-Specific Performance Discipline

### PERF-060 — Profiler Data Fabrication Prohibition

**MUST NOT**

The assistant MUST NOT invent profiler traces, benchmark results, or Big-O complexities for existing project code. If performance data is needed to justify an optimization, the assistant MUST instruct the user to run the profiler and provide the output.

See MAS-007 in `_universal/00-master-anti-slop.md`.

### PERF-061 — Existing Optimization Discovery

**MUST**

Before introducing a new caching layer, batching mechanism, or concurrency pool, the assistant MUST search the project for an existing equivalent. Inventing parallel performance infrastructure creates resource contention and cache invalidation bugs.

See MAS-035 in `_universal/00-master-anti-slop.md`.

### PERF-062 — Algorithmic Complexity Restraint

**SHOULD**

The assistant SHOULD NOT introduce complex, highly-optimized, low-level algorithms (e.g., custom memory allocators, lock-free data structures) unless the profiler explicitly identifies the current implementation as the bottleneck and the project's language/stack supports it safely.

See MAS-038 in `_universal/00-master-anti-slop.md`.

## Anti-Patterns

### PERF-042 — Premature Optimization

**MUST NOT**

Optimizing code that has not been measured is prohibited. The three rules of optimization are: measure, measure, measure.

### PERF-043 — Synchronous I/O in Async Servers

**MUST NOT**

Synchronous I/O (`fs.readFileSync`, blocking HTTP requests, blocking DB drivers) MUST NOT be used in an asynchronous runtime. Each blocks the entire worker.

### PERF-044 — Unbounded Queries

**MUST NOT**

Queries without a `LIMIT` (e.g., `SELECT * FROM events`) MUST NOT be executed on large tables. Pagination is mandatory.

### PERF-045 — Hot Path Regex Compilation

**MUST NOT**

Regular expressions MUST NOT be compiled on every call in a hot path. They MUST be compiled once and reused. Poorly written regex (ReDoS) MUST NOT be used on untrusted input.

### PERF-046 — Hot Path Excessive Logging

**MUST NOT**

Verbose logging (e.g., `logger.debug(JSON.stringify(request))`) MUST NOT occur on every request in a hot path. Logs MUST be sampled or level-gated.

### PERF-047 — Loop String Concatenation

**MUST NOT**

String concatenation in loops MUST NOT be used. The language's string builder or buffer MUST be used.

### PERF-048 — Array Reallocation in Loops

**SHOULD NOT**

Arrays SHOULD be preallocated (e.g., `make` in Go, `new Array(n)` in JS) when the size is known, to avoid repeated resizing in loops.

### PERF-049 — Over-Serialization

**MUST NOT**

Loading full ORM entities with dozens of relations to render a single field is prohibited. Projection queries MUST be used.

### PERF-050 — Uninvalidated Caches

**MUST NOT**

A cache that never invalidates serves stale data forever. Invalidation logic MUST be implemented.

### PERF-051 — Cache Stampede Prevention

**MUST**

When popular cache entries expire, concurrent requests MUST NOT all hit the backend simultaneously. Stampedes MUST be prevented via locks, probabilistic early refresh, or staggered TTLs.

### PERF-052 — Large Table Exact Counts

**MUST NOT**

`SELECT COUNT(*)` on tables with millions of rows MUST NOT be used. Approximate counts, cached counts, or counter tables MUST be used.

### PERF-053 — Deep OFFSET Pagination

**MUST NOT**

Deep pagination using `OFFSET` (e.g., `OFFSET 100000 LIMIT 20`) MUST NOT be used. Cursor-based pagination MUST be used. See `DB-019`.

### PERF-054 — Synchronous Large List Rendering

**MUST NOT**

Rendering thousands of rows to the DOM synchronously freezes the browser. Lists MUST be virtualized.

### PERF-055 — Unbounded Concurrency

**MUST NOT**

Unbounded concurrent operations (e.g., `Promise.all(urls.map(fetch))` with 100,000 URLs) MUST NOT be used. A bounded pool MUST be used.

### PERF-056 — Retry Storms

**MUST NOT**

Retries without exponential backoff and jitter MUST NOT be used. Failing downstream services trigger retry storms that worsen the failure. Circuit breakers MUST be used.

### PERF-057 — Thundering Herd on Startup

**MUST NOT**

Services MUST NOT immediately hammer dependencies on startup. Jittered delays or warmup routines MUST be used.

### PERF-058 — Micro-Optimization Over Macro

**MUST NOT**

Optimizing a 0.1ms function while the page takes 5s to load is prohibited. The biggest problem MUST be fixed first.

### PERF-059 — Wrong Metric Optimization

**MUST NOT**

Optimizing the wrong metric (e.g., reducing bundle size when the problem is server latency) is prohibited. The whole chain MUST be measured.

## Response to Violation

When a rule in this file is violated, report:

Violation: PERF-{NNN}
Reason: {one-line reason}
Correction: {smallest fix}

If the violation is a performance regression in already-shipped code, the correction MUST be accompanied by:

> "This may affect the SLO. Measure in the target environment before deploying."

For multiple violations, report each rule ID separately.

Do not replace a technical correction with a generic explanation.