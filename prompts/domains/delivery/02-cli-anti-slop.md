---
id: 02-cli-anti-slop
title: "CLI Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: delivery
version: 1
---
# CLI Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules are not
repeated. Language and framework rules remain in their related layers.

## 1. Stack Assumptions

**1.1 Confirm the command surface.** Identify the executable name, supported
shells, target runtimes, configuration files, and platform matrix before
implementation.

**1.2 Prefer an existing parser.** Use the repository's argument parser,
configuration loader, and test conventions. Do not add a parser merely to
change formatting.

**1.3 Define machine and human modes.** Decide which output is data, which is
progress, and which is an error. Keep the distinction stable across commands.

## 2. Domain Contracts

**2.1 Parse before work.** Normalize arguments, resolve configuration, and
report invalid input before creating files, sending requests, or mutating
state.

**2.2 Use stable exit codes.** Reserve zero for success and document each
non-zero code. Do not return success when a required operation only partially
completed.

**2.3 Keep streams meaningful.** Write results to stdout, progress and
diagnostics to stderr, and keep stdout parseable. Do not mix banners with
machine output.

**2.4 Make help truthful.** Help lists supported commands, options, defaults,
required inputs, and examples that are exercised by tests.

**2.5 Make signals bounded.** Handle interruption, termination, and cleanup
once. Preserve already durable work and report unfinished operations clearly.

**2.6 Treat configuration as untrusted input.** Validate precedence,
environment names, paths, URLs, and sensitive values before using them.

## 3. Domain-Specific Rules

**3.1 Parse deterministically.** Reject unknown options unless the project
explicitly supports permissive parsing. Never silently ignore misspelled
flags.

**3.2 Bound every input.** Set limits for argument length, repeat counts,
payload size, and file size before allocating or reading unbounded data.

**3.3 Make operations restartable.** A retry must not duplicate a local write
or remote mutation unless the operation is explicitly repeatable.

**3.4 Avoid hidden prompting.** Interactive prompts require a TTY, a timeout,
and a non-interactive policy. Scripts must never hang waiting for input.

**3.5 Use atomic local writes.** Write to a temporary location, flush, and
rename according to the platform contract. Clean up failed temporary files.

**3.6 Keep output format explicit.** Support the repository's machine-readable
mode and document whether values are JSON, CSV, or line-delimited records.

**3.7 Respect terminal capabilities.** Avoid color when output is redirected;
never use terminal width to change semantic content.

**3.8 Include correlation context.** Errors identify the operation and safe
input context without printing tokens, passwords, or full sensitive values.

**3.9 Test boundary behavior.** Cover missing arguments, invalid values,
broken pipes, permissions, signals, interrupted writes, and non-TTY runs.

**3.22 Keep command help synchronized.** Update parser tests, shell completions, and examples in the same change as a flag.

**3.23 Bound diagnostics.** Emit one concise failure record for each command and avoid repeating a message for every attempted item.

**3.24 Make platform behavior explicit.** Record executable lookup, path normalization, and signal differences for each supported operating system.

**3.25 Separate dry-run output.** A dry run states the planned effect and does not perform a remote or filesystem mutation.

**3.26 Preserve command history safety.** Redact arguments that may contain credentials before they reach shell history or telemetry.

**3.30 Keep option parsing centralized.** Shared flags use one schema and one error path.

**3.31 Make output parsable.** Document record delimiters and stable field names for automation.

**3.32 Preserve shell safety.** Quote expansions and use argument arrays where the runtime supports them.

## 4. Domain-Specific Anti-Patterns

### 4.1 Logging to stdout

BAD:
```bash
echo "downloading" && curl "$URL" -o file
```

GOOD:
```bash
printf 'downloading\n' >&2
curl "$URL" -o file
```

The result stream remains safe for machine consumers.

### 4.2 Silent Argument Drift

BAD:
```bash
command --name value --verbse sync
```

GOOD:
```bash
command --name value --verbose sync
```

Unknown options fail before work begins.

### 4.3 Partial Failure Reported as Success

BAD:
```bash
for item in "$@"; do upload "$item" || true; done
```

GOOD:
```bash
for item in "$@"; do upload "$item" || exit 1; done
```

Exit status reflects the failed operation.

**3.10 Preserve discovery metadata.** Commands that create files record enough provenance to identify the command version, configuration profile, and target without embedding sensitive input.

**3.11 Keep subcommands consistent.** A subcommand inherits the same stream, exit, cancellation, and configuration rules as its parent; do not create a private contract for one command.

**3.12 Use a single top-level dispatcher.** Validate the complete invocation before selecting a subcommand so an invalid global option cannot enter a destructive path.

**3.13 Make defaults reviewable.** Print effective non-sensitive defaults in verbose or diagnostic modes, while keeping secrets redacted and machine output stable.

**3.14 Respect platform paths.** Normalize separators and working directories according to the supported OS without changing user-specified paths unexpectedly.

**3.15 Add failure tests.** Assert exact exit status, stderr text, cleanup, and no partial output for each documented failure category.

**3.16 Keep shell integration explicit.** Quote paths, preserve arguments, and avoid assuming a POSIX shell on Windows or a TTY on a service host.

**3.17 Make config precedence documented.** Show whether defaults, file, environment, and flags override one another; reject conflicting required sources.

**3.18 Preserve diagnostics.** Include command name, safe argument summary, duration, and cleanup result in verbose output.

**3.19 Keep secrets out of usage text.** Redact values in help, errors, traces, and copied environment information.

**3.20 Keep output deterministic where possible.** Sort map iteration and define locale and timezone when stable machine output is required.

**3.21 Test resource exhaustion.** Cover full disk, permission denied, broken pipe, timeout, cancellation, and unavailable network.

## 5. Response to Violation

If a previous response violated this layer, state the violated rule, show
the corrected command or code, and identify the changed stream, exit status,
or signal behavior. Do not repeat universal rules or claim unperformed tests.
