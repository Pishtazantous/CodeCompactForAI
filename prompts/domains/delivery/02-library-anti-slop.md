---
id: 02-library-anti-slop
title: "Library Anti-Slop Layer"
lang: en
depends_on: ["_universal/00-style-guide.md", "_universal/00-master-anti-slop.md"]
category: domain
domain_type: delivery
version: 3
---

# Library Anti-Slop Layer

This file defines behavioral contracts specific to publishing a library for other developers. It sits in the delivery layer, below the universal anti-slop rules and above language-specific or framework-specific patterns. It covers public API design, semantic versioning, backwards compatibility, tree-shaking, distribution, and the discipline of treating consumers as users. It does not cover application code (see the relevant delivery file), language rules (see language files), framework rules (see framework files), or security and performance concerns in detail (see concern files).

A library's public API is a contract. Every change is a breaking change until proven otherwise.

## Scope

This file applies to libraries published through any package registry (npm, PyPI, crates.io, Go modules, Maven Central, NuGet, RubyGems, Packagist, Hex). The examples use TypeScript, Python, and JSON where illustrative. Language-specific rules live in language files. Build and publish tooling lives in the project's CI configuration.

## Rule Severity

Severity follows `_universal/00-style-guide.md`.

## Contracts

A library commits to five contracts. The table below maps each contract to the rules that enforce it.

| Contract | Description | Enforced By |
|---|---|---|
| API Stability | Once published under version X.Y.Z, the public API is frozen. Changing it requires a new major version. | LIB-001, LIB-008, LIB-011 |
| Semantic Versioning | The version number communicates compatibility strictly via MAJOR.MINOR.PATCH. | LIB-010 to LIB-014 |
| Tree-Shakability | A bundler can drop unused exports. The library does not force consumers to pay for unused code. | LIB-021 to LIB-027 |
| Side-Effect Freedom | Importing a module does not perform I/O, mutate global state, or register listeners. | LIB-024, LIB-053, LIB-065 |
| Distribution Integrity | The published artifact matches the source. What was tested is what was shipped. | LIB-038, LIB-046, LIB-049 |

## Public API Design

### LIB-001 — Export as Contract

**MUST**

Every exported function, class, type, or constant is a contract with consumers. Once published, it MUST NOT change without a major version bump. Before exporting anything, the necessity for consumers MUST be verified.

### LIB-002 — Minimal Surface

**MUST**

The public API surface MUST be minimal. Every additional export is a maintenance cost and a compatibility burden. The library MUST start small and add exports on demand.

Example (illustrative):

BAD: A library that exports 50 functions for 10 use cases.
GOOD: A library that exports the 10 functions actually needed.

### LIB-003 — No Accidental Exports

**MUST NOT**

Wildcard exports (e.g., `export * from "./internal"`) MUST NOT be used. Exports MUST be explicit. Language-specific boundaries (TypeScript's `"exports"` field, Python's `__all__`, Go's package boundary) MUST be used to prevent accidental exports.

### LIB-004 — Entry Point Discipline

**MUST**

Most libraries MUST have one entry point. Multiple entry points are acceptable only when sub-packages have distinct dependency sets. Each additional entry point is a new compatibility surface and MUST be justified.

### LIB-005 — Stable Naming

**MUST**

Export names MUST be stable. Renaming an export is a breaking change. Names MUST be descriptive and professional.

Example (illustrative):

BAD: `doStuff`, `handleThing`, `process2`.
GOOD: `parseConfig`, `validateInput`, `formatOutput`.

### LIB-006 — No Leaking Internal Types

**MUST NOT**

Internal types MUST NOT leak into the public API signature. If a type is part of a public signature, it is part of the API and MUST be exported, or a primitive/public interface MUST be returned instead.

Example (illustrative, TypeScript):

BAD:
```typescript
export function createClient(): InternalClient { ... }
```

GOOD:
```typescript
export interface Client { ... }
export function createClient(): Client { ... }
```

## Semantic Versioning

### LIB-010 — Strict SemVer

**MUST**

Semantic Versioning (`MAJOR.MINOR.PATCH`) MUST be followed exactly. Pre-release suffixes MUST NOT be used for marketing. Version numbers MUST NOT be skipped for marketing.

Example (illustrative):

BAD: `1.0.0-beta-marketing-preview`.
GOOD: `1.0.0-rc.1` for a release candidate, `1.0.0` for the release.

### LIB-011 — Breaking Change Definition

**MUST**

Any change that alters the public contract MUST be treated as breaking and require a MAJOR version bump. This includes renaming exports, changing signatures, changing return types incompatibly, removing exports, making optional parameters required, changing relied-upon behavior, or raising the minimum supported runtime version. "Nobody uses that" is not a valid excuse to bypass a major version.

### LIB-012 — Pre-1.0 Discipline

**MUST**

Before 1.0, minor versions may break, but this MUST be documented in the README. Once 1.0 is published, the contract is enforced. Staying in `0.x` indefinitely to avoid the discipline of `1.0` MUST NOT be used as a strategy.

### LIB-013 — Deprecation Before Removal

**MUST**

A deprecated export MUST be kept for at least one major version. The deprecation MUST be announced in a minor release, marked `@deprecated` in the type system or docstring, and log a warning when used (if the runtime supports it). It MUST only be removed in the next major version.

### LIB-014 — Changelog Maintenance

**MUST**

Every release MUST have a changelog entry, categorized as: Added, Changed, Deprecated, Removed, Fixed, Security. The Keep a Changelog convention MUST be followed.

## Backwards Compatibility

### LIB-015 — Add, Do Not Modify

**SHOULD**

Adding a new export or a new optional parameter SHOULD be preferred over modifying an existing signature. Modifying existing signatures is the riskiest change.

### LIB-016 — Default Values Over Required Parameters

**MUST**

When adding parameters to an existing function, they MUST have default values or be part of an optional configuration object. Making a new parameter required is a breaking change.

Example (illustrative, TypeScript):

BAD:
```typescript
export function parse(input: string, options: ParseOptions): Result { ... }
```

GOOD:
```typescript
export function parse(input: string, options: ParseOptions = {}): Result { ... }
```

### LIB-017 — Accept More, Return Less

**MUST**

Accepting a union where a single type was accepted before is backwards-compatible. Returning a union where a single type was returned before is breaking. Input types MAY be widened; output types MUST NOT be widened incompatibly.

### LIB-018 — No Unexpected Side Effects

**MUST NOT**

Functions MUST NOT perform unexpected side effects. A function named `parse` MUST NOT mutate global state, write to disk, or send network requests. Names MUST reflect behavior accurately.

### LIB-019 — Error Type Stability

**MUST**

Error types are part of the API. If consumers catch a specific error, changing the error type is breaking. New errors MUST be introduced as subclasses of the old one when possible.

### LIB-020 — Runtime Compatibility

**MUST**

If the library claims to support a specific runtime version (e.g., Node.js 18+), it MUST be tested on that version. Using features that require a newer version in the source code breaks the compatibility claim.

## Tree-Shaking and Bundle Size

### LIB-021 — Side Effects Declaration

**MUST**

For npm packages with no side effects, `"sideEffects": false` MUST be set in `package.json`. If some files have side effects (CSS, polyfills), they MUST be explicitly listed.

### LIB-022 — ES Modules Distribution

**MUST**

Libraries MUST ship as ES Modules (`"type": "module"` or dual `"exports"`). CommonJS-only packages cannot be tree-shaken effectively.

### LIB-023 — Named Exports Preference

**MUST**

Named exports MUST be preferred over default exports. Default exports force consumers to import the whole object or rename on import, hindering tree-shaking and tooling analysis.

Example (illustrative, TypeScript):

BAD:
```typescript
export default { parse, stringify, validate };
```

GOOD:
```typescript
export function parse() { ... }
export function stringify() { ... }
```

### LIB-024 — No Deep Barrel Files

**MUST NOT**

Barrel files (`index.js`) that re-export everything from deep internal directories MUST NOT be used. They defeat tree-shaking by pulling in the entire library when a consumer imports one item.

### LIB-025 — No Internal Wildcard Imports

**MUST NOT**

`import * as _` MUST NOT be used for internal library code. Named imports MUST be used to allow bundlers to prune unused code.

### LIB-026 — Dependency Cost Measurement

**MUST**

Before adding a dependency, its cost MUST be measured: bytes added to the consumer's bundle, availability of smaller alternatives, tree-shakability, and license compatibility. Adding massive dependencies for trivial utilities is prohibited.

See MAS-038 in `_universal/00-master-anti-slop.md`.

### LIB-027 — Conditional Polyfills

**MUST NOT**

Unconditional polyfills MUST NOT be shipped. A library MUST NOT force modern environments to download dead code. Polyfills MUST be gated behind environment checks or placed in a separate entry point.

## Dependency Discipline

### LIB-028 — Dependency as Cost

**MUST**

Every dependency of a library becomes a dependency of every consumer. Before adding a dependency, the standard library or a minimal custom implementation MUST be considered.

### LIB-029 — Peer Dependencies for Frameworks

**MUST**

Framework libraries MUST use `peerDependencies` for the framework itself, not `dependencies`. Installing a second copy of a framework (e.g., React) in the consumer's bundle is a critical bug.

### LIB-030 — Wide Peer Dependency Ranges

**MUST**

Peer dependencies MUST use wide version ranges that include compatible versions (e.g., `>=17.0.0`). Pinning to an exact minor/patch version causes unnecessary resolution failures for consumers.

### LIB-031 — Runtime Dependency Ranges

**MUST**

Runtime dependencies MUST use ecosystem-standard ranges (e.g., `^` in npm, `>=` with upper bounds in Python). Exact version pins MUST NOT be used in libraries, as they force consumers to manually deduplicate.

### LIB-032 — No Dev Dependencies at Runtime

**MUST NOT**

Runtime code MUST NOT import dev dependencies. Dev dependencies are for building and testing; importing them causes failures in the consumer's environment.

### LIB-033 — Dependency Auditing

**MUST**

Dependency audits (`npm audit`, `pip-audit`, `cargo audit`) MUST be run in CI. A vulnerable transitive dependency is a vulnerability of the library.

### LIB-034 — Minimal Transitive Surface

**MUST**

The transitive dependency tree MUST be inspected before adding a new dependency. A dependency that brings dozens of transitive packages adds unnecessary attack vectors and bloat.

## Testing a Library

### LIB-035 — Public API Tests

**MUST**

Every exported function MUST have a test. The tests serve as the specification for the public API.

### LIB-036 — Compatibility Tests

**MUST**

The test suite MUST run against the minimum supported runtime version and the latest version. Features that work on the latest version may fail on the minimum supported version.

### LIB-037 — Type Tests

**MUST**

If the library has types (TypeScript, Python stubs, Rust traits), they MUST be tested against consumer code patterns (e.g., using `tsd`, `expect-type`, or `mypy`). Type regressions are breaking changes.

### LIB-038 — Published Artifact Testing

**MUST**

Before releasing, the packed artifact MUST be installed in a fresh project and smoke-tested. Bugs from missing files in `"files"` or incorrect `"exports"` are only caught this way.

### LIB-039 — No Network in Unit Tests

**MUST NOT**

Unit tests for a library MUST NOT call real external services. Fakes or local servers MUST be used.

### LIB-040 — Golden Files for Serialization

**MUST**

If the library serializes or parses a format, it MUST be tested against golden files. A change in output is a breaking change and MUST be reviewed explicitly.

## Documentation

### LIB-041 — README Structure

**MUST**

The README MUST include a one-line description, installation instructions, a minimal usage example, an API reference (or link), a compatibility matrix, and the license.

### LIB-042 — Executable Examples

**MUST**

Every example in the README MUST be tested and runnable. Stale examples erode trust and are worse than no examples.

### LIB-043 — API Documentation Completeness

**MUST**

Every export MUST be documented with its purpose, parameters (with types), return value, thrown errors, and at least one example.

### LIB-044 — Migration Guides

**MUST**

Every major version MUST include a migration guide detailing what changed, why, and how to update consumer code.

### LIB-045 — Version Compatibility Table

**MUST**

The supported versions of the language, runtime, and key peer dependencies MUST be explicitly documented.

## Distribution and Packaging

### LIB-046 — Package Contents Restriction

**MUST**

Only what consumers need MUST be published (compiled output, types, README, LICENSE, CHANGELOG). Tests, examples, editor configs, and source maps MUST be excluded using manifest fields (e.g., `"files"` in `package.json`, `include`/`exclude` in `pyproject.toml`).

### LIB-047 — Source Map Discipline

**SHOULD**

Source maps SHOULD be shipped if debugging consumer code is a common need. They MAY be omitted if the library is small and the source is a commercial asset.

### LIB-048 — License Inclusion

**MUST**

Every package MUST include a LICENSE file. The license declared in the manifest MUST match the file.

### LIB-049 — Automated Publishing

**MUST**

Publishing MUST be a CI job, not a manual step from a developer's laptop. The release pipeline MUST run tests, build the artifact, publish to the registry, tag the commit, and create release notes.

### LIB-050 — Pre-Release Tags

**MUST**

Pre-releases (alpha, beta, rc) MUST be published under a specific tag (e.g., `next`, `beta`) that is not `latest`. Consumers MUST opt in explicitly.

## Configuration and Runtime

### LIB-051 — No Global Configuration

**MUST NOT**

Libraries MUST NOT read from or mutate global configuration objects. Consumers MUST be able to use multiple instances with different configurations via factories or explicit config parameters.

### LIB-052 — No Hidden Environment Variables

**MUST NOT**

Libraries MUST NOT read environment variables (e.g., `process.env.API_KEY`) inside functions. If env vars are read, they MUST be read once at initialization and explicitly documented. Explicit configuration parameters are preferred.

### LIB-053 — No Hidden Initialization

**MUST NOT**

Importing a library MUST NOT start background timers, open connections, or perform heavy work. Initialization MUST be explicit (via a `start()` function) or lazy (on first use).

### LIB-054 — Lazy Initialization

**MUST**

Heavy work (parsing config, opening connections) MUST be deferred until first use. Importing the library MUST be cheap.

## Error Types

### LIB-055 — Exported Custom Errors

**MUST**

Every custom error the library throws MUST be exported. Consumers MUST be able to catch errors by type, not by string matching.

Example (illustrative, TypeScript):

BAD: `throw new Error("invalid config");`
GOOD: `export class ConfigError extends Error {}`

### LIB-056 — No String Matching for Errors

**MUST NOT**

Error messages are for humans. Consumers MUST NOT be forced to match on error message strings. Error types and codes MUST be used for programmatic handling.

### LIB-057 — Documented Error Behavior

**MUST**

Every function that throws MUST document what it throws and under what conditions. Error behavior is part of the public API.

## AI-Specific Library Discipline

### LIB-074 — Export Verification Before Creation

**MUST**

Before creating a new public export or module, the assistant MUST search the library's existing API for an equivalent function. Inventing parallel utilities fragments the API surface and breaks the minimal surface contract.

See MAS-035 in `_universal/00-master-anti-slop.md`.

### LIB-075 — Dependency API Verification

**MUST**

Before using a third-party dependency's API in the library's source code, the assistant MUST verify the method exists in the installed version specified in `package.json`/`pyproject.toml`. Invented methods produce runtime errors for consumers that are invisible during library compilation.

See MAS-036 in `_universal/00-master-anti-slop.md`.

### LIB-076 — Ecosystem Convention Verification

**MUST**

Before defining package manifests, entry points, or build scripts, the assistant MUST verify the standard conventions for the target registry (npm, PyPI, crates.io). Invented manifest fields cause publishing failures or un-tree-shakeable bundles.

## Anti-Patterns

### LIB-058 — Framework Agnosticism

**MUST NOT**

A "utility" library MUST NOT import a specific framework (e.g., React) unless it is explicitly a framework adapter. Framework-agnostic cores MUST be separated from framework-specific adapters.

### LIB-059 — Type Definitions Requirement

**MUST**

Libraries written in dynamically typed languages MUST provide type definitions (e.g., bundled `.d.ts` files or a maintained `@types/...` package).

### LIB-060 — Type Accuracy

**MUST**

Type definitions MUST accurately reflect runtime behavior. A type that claims `string` but returns `undefined` at runtime is a critical bug.

### LIB-061 — Compiled Distribution

**MUST NOT**

Libraries MUST NOT ship raw source files (e.g., `.ts`, `.py` without build steps) and expect consumers to compile them. Compiled artifacts (`.js`, `.d.ts`, `.pyc`) MUST be shipped.

### LIB-062 — Optional Dependency Fallback

**MUST**

If an optional dependency is used, a documented fallback or clear error MUST be provided when the dependency is missing. Silent failures on missing optional dependencies are prohibited.

### LIB-063 — Environment Agnosticism

**MUST NOT**

Libraries MUST NOT assume a specific environment (e.g., assuming `window` exists in Node, or `fs` exists in the browser). Explicit environment checks with clear errors MUST be used.

### LIB-064 — No Console Output

**MUST NOT**

Libraries MUST NOT write to `console.log`, `print`, or stdout. The consumer MUST decide whether to log. Diagnostics MUST be returned or an injectable logger MUST be accepted.

### LIB-065 — No Global Polyfills

**MUST NOT**

Libraries MUST NOT polyfill globals (e.g., assigning `global.fetch = ...` on import). The environment's native APIs MUST be used, and requirements MUST be documented.

### LIB-066 — Functional Preference

**SHOULD**

Functions SHOULD be preferred over class-based APIs for stateless operations. Classes MUST only be used when state encapsulation is strictly required.

### LIB-067 — Config Immutability

**MUST NOT**

Configuration objects passed by the consumer MUST NOT be mutated by the library. The library MUST copy the config or treat it as read-only.

### LIB-068 — Explicit Failure

**MUST NOT**

Functions MUST NOT fail silently (e.g., returning `undefined` on error without a reason). Errors MUST be thrown, or a documented sentinel value MUST be returned.

See MAS-037 in `_universal/00-master-anti-slop.md`.

### LIB-069 — Deterministic Output

**MUST**

Serialization and formatting functions MUST produce deterministic output. Output MUST NOT depend on object key iteration order or other non-deterministic runtime factors.

### LIB-070 — Injectable Clock

**MUST**

Functions whose output depends on time MUST accept an injectable clock or `now` parameter. Relying implicitly on `Date.now()` makes testing and deterministic behavior impossible.

### LIB-071 — Locale Independence

**MUST**

Libraries that format numbers or dates MUST NOT use locale-dependent behavior implicitly (e.g., `toLocaleString()`). A locale parameter MUST be accepted, or a locale-independent format MUST be used.

### LIB-072 — Optional Input Defaults

**MUST NOT**

Libraries MUST NOT throw errors when optional configuration fields are absent. Documented defaults MUST be applied.

### LIB-073 — Flat Configuration

**SHOULD**

Configuration objects SHOULD be flat. Deeply nested options (e.g., `{ retry: { delay: { initial: 100 } } }`) are harder to document, type, and default.

## Response to Violation

When a rule in this file is violated, report:

Violation: LIB-{NNN}
Reason: {one-line reason}
Correction: {smallest fix}

For multiple violations, report each rule ID separately.

Do not replace a technical correction with a generic explanation.