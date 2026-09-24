---
id: 02-library-anti-slop
title: "Library Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: delivery
version: 1
---
# Library Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules are not
repeated. Public API and compatibility details require project evidence.

## 1. Stack Assumptions

**1.1 Identify consumers.** Establish supported language versions, module
formats, environments, bundlers, and package entry points before changing
exports.

**1.2 Preserve the package contract.** Treat exported types, runtime values,
errors, and documented behavior as compatibility surface.

**1.3 Inspect distribution rules.** Check package exports, build targets,
side-effect declarations, and test matrix before adding a new entry point.

## 2. Domain Contracts

**2.1 Design a smallest public API.** Export only behavior required by the
current consumers. Keep helpers private until a demonstrated need exists.

**2.2 Make breaking changes deliberate.** A removal, rename, narrowed type,
or changed default requires an explicit major-version decision.

**2.3 Preserve runtime and type compatibility together.** Do not update
declarations while leaving generated artifacts or conditional exports stale.

**2.4 Make side effects observable.** Importing a module must not perform
network, filesystem, process, or global mutation unless the contract says so.

**2.5 Support documented environments.** Avoid APIs unavailable in the
lowest supported runtime or browser target.

## 3. Domain-Specific Rules

**3.1 Freeze public snapshots.** Keep API review or type tests that fail when
an exported signature changes unintentionally.

**3.2 Follow semantic versioning.** Additive compatible work remains minor;
breaking behavior belongs in the next major version.

**3.3 Avoid implicit mutation.** Return new values or require an explicit
mutation API; do not alter caller-owned objects by surprise.

**3.4 Keep tree shaking viable.** Prefer named exports, side-effect-free
modules, and direct imports. Do not add a barrel that defeats bundler pruning.

**3.5 Separate entry points.** Keep browser, server, and native code behind
declared conditions when their dependencies differ.

**3.6 Make errors actionable.** Use typed, stable error categories and avoid
leaking internal paths or provider messages in public contracts.

**3.7 Deprecate in stages.** Announce a replacement, keep a migration window,
and measure remaining usage before removal.

**3.8 Test consumers.** Cover public imports, package resolution, type
checking, bundling, and the lowest supported runtime.

**3.9 Audit dependencies.** Do not silently add, upgrade, or duplicate a
runtime dependency; report the compatibility and bundle impact.

**3.22 Keep generated outputs synchronized.** Publish declarations, source maps, and package metadata from the same reviewed source revision.

**3.23 Document ownership.** Every exported resource states whether the caller or library closes it and how cancellation affects it.

**3.24 Preserve error categories.** Keep error classes stable even when internal providers change, so consumers do not parse messages.

**3.25 Test module resolution.** Verify the package from a packed artifact with the supported runtime, bundler, and conditional-export modes.

**3.26 Review size impact.** Measure install size and initialization cost when adding a public dependency or export path.

**3.30 Keep exports intentional.** Review every public symbol with a named consumer or stated compatibility contract.

**3.31 Bound package startup.** Avoid import-time network, process, or filesystem work unless explicitly documented.

**3.32 Test lowest runtime.** Verify every supported runtime and module resolution mode before release.

## 4. Domain-Specific Anti-Patterns

### 4.1 Default Export Leaking the Implementation

BAD:
```typescript
export default function internalQueue(options = {}) {
  return new Map(Object.entries(options));
}
```

GOOD:
```typescript
export function createQueue<T>(initial: readonly T[] = []): Queue<T> {
  return new QueueImpl(initial);
}
```

The public contract exposes a deliberate, typed surface.

### 4.2 Import-Time Network Side Effect

BAD:
```typescript
import { readConfig } from "./config";
readConfig("production");
```

GOOD:
```typescript
import { readConfig } from "./config";
const config = await readConfig("production");
```

The module can be imported, tested, and tree-shaken without I/O.

### 4.3 Silent Signature Break

BAD:
```typescript
export function parse(value: string, strict = false) {
  return strict ? value : value.trim();
}
```

GOOD:
```typescript
export function parse(value: string, options: ParseOptions = {}) {
  return options.strict ? value : value.trim();
}
```

The new contract is explicit and reviewed as an API change.

**3.10 Review generated declarations.** Check declaration output, source maps, and package contents for accidental exports or omitted files before release.

**3.11 Preserve cancellation semantics.** An abort, timeout, or disposed resource has a documented result and does not leave a library-owned handle active.

**3.12 Keep examples executable.** Examples use the supported public API, declare their environment, and avoid private imports that package consumers cannot resolve.

**3.13 Track ownership of callbacks.** Callback frequency, exceptions, cancellation, and cleanup are part of the contract when a library invokes user code.

**3.14 Bound configurable limits.** Defaults for size, retries, timeouts, and concurrency are conservative and documented rather than unlimited.

**3.15 Test package installation.** Validate the packed artifact in a clean consumer with the declared module resolution, not only from the repository workspace.

**3.16 Document runtime ownership.** State whether a caller owns returned resources, listeners, files, sockets, and cancellation handles.

**3.17 Keep callbacks deterministic.** Do not invoke user callbacks while internal locks are held unless the contract explicitly requires it.

**3.18 Guard reentrancy.** A callback may call the library again only when the public contract supports reentrant use.

**3.19 Preserve error identity.** Callers can distinguish cancellation, validation, conflict, and dependency errors without parsing message text.

**3.20 Keep serialization explicit.** Version formats and reject ambiguous or unknown encodings rather than guessing.

**3.21 Test old consumers.** Exercise the lowest supported language and module mode before releasing a public contract change.

## 5. Response to Violation

If a prior response violated this layer, name the compatibility risk, show
the corrected public declaration, and state whether versioning, exports,
side effects, or tests changed. Do not claim a package build without running
the repository's validator.
