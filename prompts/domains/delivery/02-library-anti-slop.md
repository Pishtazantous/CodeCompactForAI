---
id: 02-library-anti-slop
title: "Library Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: delivery
version: 2
---

# Library Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
generic security, dependency addition, output format) are NOT
repeated here.

This file covers rules specific to publishing a library for other
developers: public API design, semantic versioning, backwards
compatibility, tree-shaking, distribution, and the discipline of
treating consumers as users. It does NOT cover application code
(see the relevant delivery file), language rules (see the language
files), framework rules (see the framework files), or security and
performance concerns (see the concern files).

A library's public API is a contract. Every change is a breaking
change until proven otherwise.

## 1. Stack Assumptions

This file applies to libraries published through any package
registry:

- npm (JavaScript, TypeScript)
- PyPI (Python)
- crates.io (Rust)
- Go modules (Go)
- Maven Central (Java, Kotlin)
- NuGet (C#)
- RubyGems (Ruby)
- Packagist (PHP)
- Hex (Elixir)

The examples use TypeScript and Python. The principles are
language-agnostic. Language-specific rules (type system, error
syntax) live in `domains/language/`. Build and publish tooling lives
in the project's CI configuration.

## 2. Delivery Contracts

A library commits to five contracts. Every section below enforces
one or more of these.

### 2.1 API Stability

Once published under version `X.Y.Z`, the public API at that version
is frozen. Consumers depend on it. Changing it requires a new major
version.

### 2.2 Semantic Versioning

The version number communicates compatibility. `MAJOR.MINOR.PATCH`:

- MAJOR: incompatible API change.
- MINOR: new functionality, backwards-compatible.
- PATCH: backwards-compatible bug fix.

The version is not a marketing tool. It is a compatibility signal.

### 2.3 Tree-Shakability

A bundler can drop unused exports. A library that ships as a single
non-shakeable blob forces consumers to pay for code they do not use.

### 2.4 Side-Effect Freedom

Importing a module does not perform I/O, mutate global state, or
register listeners. Side effects happen only when the consumer
calls an explicit function.

### 2.5 Distribution Integrity

The published artifact matches the source. What was tested is what
was shipped. Lockfiles and checksums verify this.

## 3. Public API Design

### 3.1 Every Export Is a Contract

An exported function, class, type, or constant is used by someone.
Once published, it cannot change without a major version bump.
Before exporting anything, ask: is this needed by consumers?

### 3.2 Minimal Surface

BAD: A library that exports 50 functions for 10 use cases.

GOOD: A library that exports the 10 functions actually needed.

Every additional export is a maintenance cost and a compatibility
burden. Start small. Add on demand.

### 3.3 No Accidental Exports

BAD:
```typescript
export * from "./internal/helpers";
```

GOOD:
```typescript
export { parseConfig } from "./config";
export { validate } from "./validate";
```

TypeScript's `"exports"` field, Python's `__all__`, and Go's
package boundary prevent accidental exports. Use them.

### 3.4 One Entry Point

Most libraries have one entry point: `"main"`, `"module"`,
`"types"`, or a single `"exports"` field in `package.json`; a
public module in Python; `lib.rs` in Rust.

Multiple entry points (for example `my-lib/react` alongside
`my-lib/core`) are acceptable when the sub-packages have distinct
dependency sets. Each additional entry point is a new compatibility
surface.

### 3.5 Stable Naming

Renaming an export is a breaking change. Pick names carefully.

BAD: `doStuff`, `handleThing`, `process2`.

GOOD: `parseConfig`, `validateInput`, `formatOutput`.

### 3.6 No Leaking Internal Types

BAD:
```typescript
// Returns an internal type that is not exported.
export function createClient(): InternalClient { ... }
```

GOOD:
```typescript
export interface Client { ... }
export function createClient(): Client { ... }
```

If the type is part of the signature, it is part of the API. Export
it or return a primitive.

## 4. Semantic Versioning

### 4.1 Strict SemVer

Follow `MAJOR.MINOR.PATCH` exactly. Do not use pre-release suffixes
for marketing. Do not skip numbers for marketing.

BAD: `1.0.0-beta-marketing-preview`.

GOOD: `1.0.0-rc.1` for a release candidate, `1.0.0` for the release.

### 4.2 What Counts as Breaking

Anything that changes the contract:

- Renaming an export.
- Changing a function signature.
- Changing a return type in a way that breaks existing code.
- Removing an export.
- Making a previously optional parameter required.
- Changing behavior in a way consumers depend on.
- Raising the minimum supported language or runtime version.

Even if "nobody uses that", it is breaking. Wait for a major
version.

### 4.3 Pre-1.0 Is Different, Not Free

Before 1.0, minor versions may break. Document this in the README.
Once 1.0 is published, the contract is enforced. Do not stay in 0.x
to avoid the discipline of 1.0.

### 4.4 Deprecation Before Removal

A deprecated export is kept for at least one major version:

1. Announce the deprecation in a minor release.
2. Mark it `@deprecated` in the type system or docstring.
3. Log a warning when used, if the runtime supports it.
4. Remove it in the next major.

Removing without a deprecation cycle surprises consumers.

### 4.5 Changelog

Every release has a changelog entry, categorized as: Added, Changed,
Deprecated, Removed, Fixed, Security. Follow the Keep a Changelog
convention. Consumers read this before upgrading.

## 5. Backwards Compatibility

### 5.1 Add, Do Not Modify

The safest change is adding a new export or a new optional
parameter. The riskiest is changing an existing signature.

### 5.2 Default Values Over Required Parameters

BAD:
```typescript
export function parse(input: string, options: ParseOptions): Result { ... }
```

GOOD:
```typescript
export function parse(input: string, options: ParseOptions = {}): Result { ... }
```

Consumers that pass nothing keep working.

### 5.3 Accept More, Return Less

Accepting a union where a single type was accepted before is
backwards-compatible. Returning a union where a single type was
returned before is breaking.

### 5.4 No Unexpected Side Effects

A function named `parse` does not mutate global state, write to
disk, or send network requests. If it does, it is not `parse`; it
is `parseAndSave`. Names must reflect behavior.

### 5.5 Error Types Are Part of the API

If consumers catch a specific error, changing the error type is
breaking. Introduce a new error as a subclass of the old one when
possible.

### 5.6 Runtime Compatibility

If the library claims to support Node.js 18+, it is tested on
Node.js 18. A feature that requires 20+ in the source breaks the
claim.

## 6. Tree-Shaking and Bundle Size

### 6.1 `sideEffects: false`

For npm packages with no side effects, set `"sideEffects": false`
in `package.json`. Bundlers then drop unused imports.

If some files have side effects (CSS, polyfills), list them:

```json
"sideEffects": ["./dist/polyfill.js", "*.css"]
```

### 6.2 ES Modules

Ship ESM (`"type": "module"` or dual `"exports"`). CommonJS-only
packages cannot be tree-shaken.

### 6.3 Named Exports Over Default

BAD:
```typescript
export default { parse, stringify, validate };
```

Consumers import the whole object. Bundlers cannot tree-shake.

GOOD:
```typescript
export function parse() { ... }
export function stringify() { ... }
export function validate() { ... }
```

### 6.4 No Barrel Files With Deep Imports

An `index.js` that re-exports everything from `./internal/*`
defeats tree-shaking. Consumers who import one thing pull in
everything.

### 6.5 No `import * as` for Internal Use

Import named exports. `import * as _` prevents bundlers from
pruning.

### 6.6 Measure the Cost of Dependencies

Before adding a dependency, measure:

- Bytes added to the consumer's bundle.
- Whether a smaller alternative exists.
- Whether the dependency is tree-shakeable.
- License compatibility.

A library that adds 200 KB for a 10-line utility is not a good
library.

### 6.7 No Unconditional Polyfills

A library that ships a polyfill for every environment forces
modern environments to download dead code. Gate polyfills behind
environment checks or a separate entry point.

## 7. Dependency Discipline

### 7.1 Every Dependency Is a Cost

Every dependency of a library becomes a dependency of every
consumer. The cost compounds. Before adding a dependency, ask
whether the standard library or a 20-line implementation suffices.

### 7.2 Peer Dependencies for Framework Libraries

BAD:
```json
"dependencies": { "react": "^18.0.0" }
```

This installs a second React if the consumer already has one.

GOOD:
```json
"peerDependencies": { "react": ">=17.0.0" }
```

### 7.3 Wide Version Ranges for Peer Dependencies

A peer dependency on `react: "18.2.0"` fails when the consumer is on
`18.3.0`. Use a range that includes compatible versions.

### 7.4 Runtime Dependencies Pinned or Ranged

Match the ecosystem's convention. npm uses `^`, Python uses `>=`
with upper bounds, Rust uses `~` or `^`. Do not pin to an exact
version unless the project's policy requires it.

### 7.5 No Dev Dependencies at Runtime

Dev dependencies are for building and testing. A runtime import of
a dev dependency fails in the consumer's environment.

### 7.6 Audited Dependencies

Run `npm audit`, `pip-audit`, `cargo audit`, or the ecosystem's
equivalent in CI. A vulnerable transitive dependency is a
vulnerability of the library.

### 7.7 Minimal Transitive Surface

A dependency that brings 30 transitive packages adds 30 attack
vectors. Inspect what a dependency pulls in before adding it.

## 8. Testing a Library

### 8.1 Public API Tests

Every exported function has a test. The tests are the
specification.

### 8.2 Compatibility Tests

Run the test suite against the minimum supported runtime version
and the latest. A feature that works on Node 20 may fail on Node
18.

### 8.3 Type Tests

If the library has types (TypeScript, Python stubs, Rust traits),
test them:

BAD: Types are compiled but never checked against consumer code.

GOOD: A `test-d.ts` file using `tsd` or `expect-type`, or a
`mypy` check on a consumer sample.

Type regressions are breaking changes.

### 8.4 Test the Published Artifact

Before releasing, install the packed artifact in a fresh project
and run a smoke test. Bugs from missing files in `"files"` or
incorrect `"exports"` are only caught this way.

```bash
npm pack
cd /tmp/smoke-test
npm init -y
npm install /path/to/package.tgz
node -e "require('mylib').parse('x')"
```

### 8.5 No Network in Tests

Unit tests for a library do not call real services. Use fakes or
local servers.

### 8.6 Golden Files for Serialization

If the library serializes or parses a format, test against golden
files. A change in output is a breaking change and must be
reviewed.

## 9. Documentation

### 9.1 README Structure

- One-line description.
- Installation.
- Minimal usage example.
- API reference (or link to it).
- Compatibility matrix (runtimes, versions).
- License.

### 9.2 Examples That Run

Every example in the README is tested. A stale example is worse
than no example because it erodes trust.

### 9.3 API Documentation

Every export is documented with:

- What it does.
- Parameters, with types.
- Return value.
- Thrown errors.
- At least one example.

### 9.4 Migration Guide

Every major version has a migration guide. What changed, why, and
how to update consumer code. A migration guide turns a painful
upgrade into a mechanical one.

### 9.5 Version Compatibility Table

State which versions of the language, runtime, and key peers are
supported. Consumers check this before upgrading.

## 10. Distribution and Packaging

### 10.1 What Goes in the Package

Only what consumers need: compiled output, types, README, LICENSE,
CHANGELOG.

BAD: Tests, examples, editor configs, and source maps are shipped.

GOOD: `"files"` field in `package.json`, `include`/`exclude` in
`pyproject.toml`, or the equivalent manifest field lists exactly
what is published.

### 10.2 Source Maps

Ship source maps if debugging consumer code is a common need. Omit
if the library is small and the source is not a commercial asset.

### 10.3 License

Every package has a LICENSE file. The license in `package.json` or
the manifest matches the file.

### 10.4 Publish Is Not a Manual Step

A release is a CI job, not a developer's laptop. The release
pipeline:

1. Runs the tests.
2. Builds the artifact.
3. Publishes to the registry.
4. Tags the git commit.
5. Creates a release note.

Manual publishes drift and are hard to reproduce.

### 10.5 Pre-Release Tags

Pre-releases (alpha, beta, rc) are published under a tag
(`next`, `beta`, `rc`) that is not `latest`. Consumers opt in
explicitly.

## 11. Configuration and Runtime

### 11.1 No Global Configuration

A library that reads from a global config object is coupled to it.
Consumers cannot use two instances with different configs.

BAD:
```typescript
let apiUrl = "https://default";
export function setApiUrl(url: string) { apiUrl = url; }
```

GOOD:
```typescript
export interface Config { apiUrl: string; }
export function createClient(config: Config): Client { ... }
```

### 11.2 No Environment Variables

A library that reads `process.env.API_KEY` inside a function
surprises consumers and breaks in environments without env vars.

If env vars are read, they are read once at initialization and
documented. Better: accept configuration explicitly.

### 11.3 No Hidden Initialization

BAD: A library that starts a background timer on import.

GOOD: An explicit `start()` function that the consumer calls.

### 11.4 Lazy Initialization

The library performs heavy work (parse config, open connection)
only on first use, not on import. Import is cheap.

## 12. Error Types

### 12.1 Exported Error Types

Every error the library throws is either a standard error or an
exported custom error. Consumers catch them by type, not by string.

BAD:
```typescript
throw new Error("invalid config");
```

GOOD:
```typescript
export class ConfigError extends Error {}
throw new ConfigError("invalid config");
```

### 12.2 No String Matching

Consumers must not match on error messages. Messages are for
humans. Types and codes are for code.

### 12.3 Documented Errors

Every function that throws documents what it throws and under what
conditions. Error behavior is part of the public API.

## 13. Anti-Patterns

### 13.1 Exporting Everything

BAD: `export * from "./internal"`.

GOOD: Explicit exports of the intended public API.

### 13.2 Mutable Global State

BAD: A module-level cache that all consumers share.

GOOD: A factory that returns a new instance with its own state.

### 13.3 Requiring a Specific Framework

BAD: A "utility" library that imports React.

GOOD: A framework-agnostic core plus a framework-specific adapter
package.

### 13.4 Peer Dependencies as Dependencies

BAD: React in `dependencies` of a React library. Two React copies
end up in the consumer's bundle.

GOOD: React in `peerDependencies` with a wide range.

### 13.5 Silent Version Bumps

BAD: A patch release that changes behavior.

GOOD: A minor or major release with a changelog entry.

### 13.6 Breaking Changes Without a Major

The most damaging library mistake. Wait for a major version.

### 13.7 No Types

BAD: A JavaScript library with no type definitions.

GOOD: Types bundled, or a `@types/...` package maintained in sync.

### 13.8 Types That Lie

BAD: A type that says `string` but the function can return
`undefined`.

GOOD: The type matches the runtime behavior.

### 13.9 Shipping Source Without a Build

BAD: A TypeScript library that publishes `.ts` files and expects
consumers to compile them.

GOOD: Ship compiled `.js` + `.d.ts`, or use a bundler that handles
it.

### 13.10 Shipping Without `files` or `.npmignore`

BAD: Publishing that includes tests, examples, and editor configs.

GOOD: An explicit `"files"` field listing only what consumers need.

### 13.11 Optional Dependencies Without Fallback

BAD: `try { require("optional") } catch {}` with no fallback path.

GOOD: A documented behavior when the optional dependency is
missing.

### 13.12 Async Initialization

BAD: The consumer must `await lib.init()` before using anything.

GOOD: Lazy initialization on first use.

### 13.13 Environment Assumptions

BAD: The library assumes `window` exists (breaks in Node), or
Node's `fs` exists (breaks in browser).

GOOD: Explicit environment checks with clear errors.

### 13.14 No Error Context

BAD: `throw new Error("invalid")`.

GOOD: `throw new ConfigError("missing field: apiKey")`.

### 13.15 Console Output in a Library

BAD: `console.log("loaded")` in library code.

GOOD: No output. The consumer decides whether to log.

### 13.16 Locking to a Specific Dependency Version

BAD: `"dependencies": { "lodash": "4.17.21" }` (exact pin).

GOOD: `"dependencies": { "lodash": "^4.17.0" }`.

Exact pins in a library force every consumer to deduplicate
manually.

### 13.17 No Minimum Runtime Documented

BAD: A library that works on Node 14 but does not say so.

GOOD: `"engines": { "node": ">=18" }` in `package.json` and a
README section.

### 13.18 Polyfilling Globals

BAD: A library that assigns `global.fetch = ...` on import.

GOOD: The library uses the environment's `fetch` and documents the
requirement.

### 13.19 Barrel Files

BAD: `index.js` re-exporting everything from every subdirectory.

GOOD: Import from the specific module.

### 13.20 Default Exports

BAD:
```typescript
export default function parse() { ... }
```

Consumers rename it on import. Tooling cannot follow it. Bundlers
have a harder time.

GOOD: Named exports.

### 13.21 Class-Based APIs Without a Reason

BAD: A library that requires `new Client()` for a stateless
function.

GOOD: A function that does the work. Use classes only when state
must be encapsulated.

### 13.22 Configuration Objects That Are Mutated

BAD: A config object passed by the consumer, then mutated by the
library.

GOOD: The library copies the config or accepts it as read-only.

### 13.23 Silent Failures

BAD: A function that returns `undefined` on error, without a
reason.

GOOD: Throw an error, or return a documented sentinel.

### 13.24 Non-Deterministic Output

BAD: A serializer whose output depends on object key iteration
order.

GOOD: Deterministic output, tested against golden files.

### 13.25 Time-Dependent Behavior

BAD: A function whose output depends on `Date.now()` without an
injectable clock.

GOOD: Accept a `now` parameter or a `Clock` interface.

### 13.26 Locale-Dependent Behavior

BAD: Using `toLocaleString()` in a library that formats numbers.

GOOD: Accept a locale parameter, or use a locale-independent
format.

### 13.27 Logging in a Library

BAD: `console.log`, `print`, or writing to stdout from a library.

GOOD: The consumer provides a logger, or the library returns
diagnostics.

### 13.28 Throw on Missing Optional Input

BAD: Throwing when an optional config field is absent.

GOOD: A documented default.

### 13.29 Deeply Nested Options

BAD: `{ retry: { delay: { initial: 100, max: 5000 } } }`.

GOOD: `{ retryDelayMs: 100, retryMaxDelayMs: 5000 }`.

Nested options are harder to document and default.

### 13.30 No Deprecation Warnings

BAD: A deprecated function silently continues working until it is
removed.

GOOD: The function logs a warning on use, referencing the
replacement and the removal version.

## 14. Response to Violation

If a previous response violated a rule here:

```
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

No justification. No apology paragraph. Fix and move on.
