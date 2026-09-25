---
id: 02-cli-anti-slop
title: "CLI Anti-Slop Layer"
lang: en
depends_on: ["_universal/00-style-guide.md", "_universal/00-master-anti-slop.md"]
category: domain
domain_type: delivery
version: 3
---

# CLI Anti-Slop Layer

This file defines behavioral contracts specific to command-line tools. It sits in the delivery layer, below the universal anti-slop rules and above framework-specific parser patterns. It covers command design, argument parsing, exit codes, standard streams, signals, help text, configuration, and distribution. It does not cover application code (see other delivery files), language rules (see language files), framework rules (see framework files), or security and performance concerns in detail (see concern files).

A CLI is a program that runs unattended in scripts, in CI, and from a shell. Every behavior is a contract with the caller. The contract is the tool's public API.

## Scope

This file applies to CLIs distributed as standalone binaries (Go, Rust, C, C++), Node.js scripts, Python scripts, shell scripts, and bundled scripts via `pkg`, `pyinstaller`, `nexe`, or similar. The examples use POSIX shell conventions where illustrative. Parser library choices (commander, click, cobra, clap) live in framework files. Language-specific rules live in language files.

## Rule Severity

Severity follows `_universal/00-style-guide.md`.

## Contracts

A CLI commits to seven contracts. The table below maps each contract to the rules that enforce it.

| Contract | Description | Enforced By |
|---|---|---|
| Command Interface Stability | Once a flag, subcommand, or output format is documented, consumers depend on it. | CLI-001, CLI-002, CLI-079 |
| Exit Code Correctness | Exit codes carry success or failure. Scripts depend on this. | CLI-018 to CLI-021 |
| Stream Separation | Data goes to stdout. Diagnostics, progress, and errors go to stderr. | CLI-022 to CLI-027 |
| Non-Interactive by Default | A command in a script does not block waiting for input unless explicitly interactive. | CLI-045 to CLI-048 |
| Signal Safety | The tool handles SIGINT and SIGTERM by cleaning up and exiting conventionally. | CLI-034 to CLI-039 |
| Configuration Determinism | Given the same flags, environment, config, and inputs, the command produces the same output. | CLI-014 to CLI-017 |
| Reproducible Distribution | The installed version matches the source. The version is queryable. | CLI-028, CLI-053 to CLI-058 |

## Command Design

### CLI-001 — Single Responsibility Command

**MUST**

A CLI MUST do one thing. A binary that runs migrations, sends emails, and generates reports is three tools and MUST be split. Each subcommand MUST do one job.

### CLI-002 — Conventional Subcommand Structure

**MUST**

Subcommands MUST follow the conventional structure: `tool [global-flags] <command> [command-flags] [args]`. Global flags MUST precede the command. Command flags MUST follow it. Every subcommand MUST have its own `--help`.

### CLI-003 — Verb-Noun Subcommand Names

**MUST**

Subcommands MUST be verbs or verb-noun pairs. The name MUST tell the user what the command does.

Example (illustrative):

BAD: `tool users`, `tool data`, `tool thing`.

GOOD: `tool list-users`, `tool export-data`, `tool create-thing`.

### CLI-004 — No Overloaded Commands

**MUST NOT**

A subcommand that behaves differently based on multiple flags is hard to document and test. Separate commands MUST be used instead.

Example (illustrative):

BAD: `tool sync --from x --to y --mode full --direction both`.

GOOD: `tool sync-full` and `tool sync-incremental` as separate commands.

## Argument Parsing

### CLI-005 — Parser Library Usage

**MUST**

Hand-parsing `process.argv` or `sys.argv` beyond trivial cases MUST NOT be used. The language's standard or de-facto parser (`commander`, `yargs`, `click`, `typer`, `cobra`, `clap`, etc.) MUST be used.

See MAS-036 in `_universal/00-master-anti-slop.md`.

### CLI-006 — POSIX and GNU Convention Compliance

**MUST**

POSIX and GNU conventions MUST be followed:

- Short flags: `-h`, `-v`, `-f value`.
- Long flags: `--help`, `--verbose`, `--file value` or `--file=value`.
- Combined short flags: `-vf` only for flags that take no value.
- `--` terminates flag parsing; the rest are positional arguments.

A new convention MUST NOT be invented. Users expect POSIX.

### CLI-007 — Conventional Short Flags

**MUST**

Conventional short flags MUST be used for common options:

- `-h` for `--help`.
- `-v` for `--verbose` (or `--version`).
- `-V` for `--version` when `-v` is verbose.
- `-q` for `--quiet`.
- `-f` for `--file` or `--force` (not both in one tool).
- `-o` for `--output`.
- `-n` for `--dry-run` or `--no-...` (context-dependent).

### CLI-008 — Long Flags for Non-Conventional Options

**MUST**

A flag not in the conventional list MUST have only a long form. `--max-retries` does not need a short form.

### CLI-009 — Kebab-Case Flag Names

**MUST**

Flag names MUST be kebab-case. camelCase, PascalCase, or snake_case MUST NOT be used. GNU convention uses kebab-case.

Example (illustrative):

BAD: `--maxRetries`, `--MaxRetries`, `--max_retries`.

GOOD: `--max-retries`.

### CLI-010 — Boolean Flag Semantics

**MUST**

Boolean flags MUST be flags, not options. A boolean flag is present or absent. A `--no-` prefix MUST negate it.

Example (illustrative):

BAD: `--verbose true`, `--verbose=false`.

GOOD: `--verbose`, `--no-verbose`.

### CLI-011 — Argument Bracket Convention

**MUST**

Help text MUST match the standard bracket convention:

- `<file>` = required.
- `[file]` = optional.
- `<file...>` = one or more.
- `[file...]` = zero or more.

## Validation and Defaults

### CLI-012 — Argument Validation

**MUST**

Arguments come from the user and MUST be validated:

- Required arguments are present.
- Types match.
- Enumerated values are in the allowed set.
- File paths exist when they must.
- Mutually exclusive flags are not both set.

An invalid argument MUST produce a clear error and exit with code 2.

See MAS-037 in `_universal/00-master-anti-slop.md`.

### CLI-013 — Sensible Defaults

**SHOULD**

A tool SHOULD default to the common case. A tool that requires ten flags to do anything is unfriendly. Flags SHOULD be exposed for the uncommon case.

### CLI-014 — Configuration Precedence

**MUST**

Configuration MUST follow standard precedence, highest to lowest:

1. Command-line flags.
2. Environment variables.
3. Project config file (`.mytoolrc` in the current directory).
4. User config file (`~/.config/mytool/config`).
5. Built-in defaults.

The precedence MUST be documented in `--help` and followed consistently.

### CLI-015 — Environment Variable Naming

**MUST**

Environment variable names MUST be uppercase with a consistent prefix (e.g., `MYTOOL_API_KEY`). They MUST NOT collide with common variables (`PATH`, `HOME`, `USER`, `EDITOR`). Every env var MUST be documented in the help text.

### CLI-016 — Explicit Config Paths

**MUST**

The config file MUST have a documented default location. `--config <path>` MUST override it. `--no-config` MUST disable loading entirely.

### CLI-017 — Visible Config Loading

**MUST NOT**

Loading a config file from a surprising location confuses users. In verbose mode, the loaded config path MUST be printed to stderr.

## Exit Codes

### CLI-018 — Success and Failure Codes

**MUST**

Exit codes MUST follow the standard convention:

- `0`: success.
- `1`: general error.
- `2`: usage error (bad arguments).
- `64`-`78`: reserved by `sysexits.h` for specific failures.
- `126`: command found but not executable.
- `127`: command not found.
- `130`: terminated by SIGINT (128 + 2).
- `143`: terminated by SIGTERM (128 + 15).

### CLI-019 — Exit Code Stability

**MUST**

Scripts depend on exit codes. Changing an exit code from `1` to `2` breaks callers. Exit codes MUST be treated as a documented contract.

### CLI-020 — Distinct Failure Codes

**MUST**

Distinct failures MUST produce distinct codes.

Example (illustrative):

BAD: `1` for both "file not found" and "invalid JSON".

GOOD: `1` for general error, `2` for usage error, and a documented set of additional codes for specific failures.

### CLI-021 — Exit Code Documentation

**MUST**

The help text MUST list the exit codes the tool produces. Callers should not have to read the source.

## Standard Streams

### CLI-022 — Stream Separation

**MUST**

Program output that a caller might pipe MUST go to stdout. Logs, progress, and errors MUST go to stderr. A pipe between two tools MUST NOT receive progress messages.

Example (illustrative, Bash):

BAD:
```bash
echo "Processing file..." > output.txt
```

GOOD:
```bash
echo "Processing file..." >&2
```

### CLI-023 — Valid stderr on Success

**MUST**

A successful run may still produce warnings on stderr. stderr output MUST NOT be treated as failure by itself. Exit code `0` with stderr output is valid.

### CLI-024 — TTY Awareness

**MUST**

When stdout is a TTY, colored output, progress bars, and spinners MAY be used. When stdout is not a TTY, plain output with no progress and no colors MUST be used. ANSI codes in piped JSON output is a bug.

### CLI-025 — NO_COLOR Compliance

**MUST**

The `NO_COLOR` environment variable (https://no-color.org/) MUST be respected. A `--no-color` flag MUST also be provided. The flag MUST override the environment.

### CLI-026 — Secret Redaction

**MUST NOT**

Passwords, tokens, and keys MUST NEVER appear on either stdout or stderr, even in debug mode. They MUST be redacted in log output.

### CLI-027 — Stream Buffering

**MUST**

stdout is line-buffered when connected to a terminal and block-buffered when piped. A tool that writes a progress line and expects it to appear immediately MUST flush or write to stderr.

## Help and Documentation

### CLI-028 — Mandatory Help Command

**MUST**

`tool --help` MUST show the top-level commands and global flags. `tool <command> --help` MUST show the command's flags and arguments. Both MUST exit with code 0.

### CLI-029 — Help Text Structure

**MUST**

Help text MUST include:

- One-line summary.
- Usage line.
- Arguments with types and defaults.
- Options with types and defaults.
- At least one example.
- Exit codes.
- Environment variables that affect behavior.

### CLI-030 — Help Text Accuracy

**MUST**

If a flag is documented, it MUST work. If a flag works, it MUST be documented. Help text and behavior drift MUST be tested together.

### CLI-031 — Version Query

**MUST**

`tool --version` MUST print the version and exit 0. The format MUST be consistent across releases (common format: `tool 1.4.2`).

### CLI-032 — Working Examples

**MUST**

Every example in help text MUST actually run against the current version. Stale examples are worse than no examples.

### CLI-033 — Man Pages for Complex Tools

**SHOULD**

A tool with subcommands or many flags SHOULD ship a man page. The man page SHOULD be generated from the same source as `--help` when possible.

## Signals and Interruption

### CLI-034 — SIGINT Handling

**MUST**

On Ctrl+C (SIGINT), the tool MUST clean up (temp files, locks, partial output) and exit with code 130.

See MAS-040 in `_universal/00-master-anti-slop.md`.

### CLI-035 — SIGTERM Handling

**MUST**

On SIGTERM, the same cleanup MUST run and the tool MUST exit with code 143.

### CLI-036 — Signal Non-Ignore

**MUST NOT**

Ignoring SIGINT traps the user in a hanging process. It MUST NOT be ignored. A tool that must complete a critical section MUST defer the signal, not ignore it.

### CLI-037 — Exit Cleanup

**MUST**

A tool that creates temp files, acquires locks, or opens connections MUST clean up in a `finally` block or a signal handler.

### CLI-038 — Atomic Writes

**MUST**

A command that writes a file MUST either write it completely or leave the original unchanged. It MUST write to a temp file, then rename.

Example (illustrative):

BAD: Write directly to `output.json`; a crash mid-write leaves a corrupt file.

GOOD: Write to `output.json.tmp`, then `rename` to `output.json`.

### CLI-039 — Idempotent Cleanup

**MUST**

A signal handler that runs twice MUST NOT break. Signal handlers are not reentrant; a flag MUST be used to mark "cleanup in progress".

## Long-Running Operations

### CLI-040 — Progress on stderr

**MUST**

Progress bars, spinners, and status messages MUST go to stderr, never stdout. The stdout stream belongs to the actual output.

### CLI-041 — Progress TTY-Only

**MUST NOT**

When stderr is not a TTY, progress MUST NOT be emitted. Logs MUST replace progress in CI environments.

### CLI-042 — Start and End Reporting

**MUST**

A long-running command MUST print a "starting..." line at the start and a "done" line at the end on stderr. This allows a caller to see in logs what happened.

### CLI-043 — Interruptible Work

**MUST**

A long-running loop MUST check for interruption between iterations. SIGINT MUST cancel the loop, not just the current operation.

### CLI-044 — Network Operation Timeouts

**MUST**

Every network call MUST have a timeout. `--timeout <seconds>` MUST override the default. A command that hangs forever is a bug.

See MAS-040 in `_universal/00-master-anti-slop.md`.

## Non-Interactive by Default

### CLI-045 — No Interactive Prompts

**MUST**

A command MUST run to completion without user input. Interactive prompts MUST be opt-in.

Example (illustrative):

BAD: A command that asks for confirmation in CI.

GOOD: A command that requires `--force` for destructive actions, and only prompts when stdin is a TTY and `--no-input` is not set.

### CLI-046 — Global --no-input Flag

**MUST**

A global `--no-input` flag MUST disable all prompts. In its presence, the command MUST use defaults or fail clearly.

### CLI-047 — Destructive Action Confirmation

**MUST**

A destructive command (`delete`, `drop`, `overwrite`) MUST require one of:

- `--force` for non-interactive confirmation.
- A prompt when interactive.
- `--dry-run` as a default, with `--apply` to execute.

### CLI-048 — Mandatory Dry-Run

**MUST**

A destructive command MUST provide `--dry-run`. It MUST print what would happen without doing it. This is the safest way to preview.

## Configuration and Environment

### CLI-049 — Visible Configuration Sources

**MUST**

The tool MUST NOT read configuration from surprising places. Every config source MUST be documented in `--help`.

### CLI-050 — Visible Environment Overrides

**MUST**

If an environment variable overrides a flag, the help text MUST say so. Users debug faster when the source of a value is visible.

### CLI-051 — Sensible Working Directory

**MUST**

The tool MUST operate on the current directory by default. If it must operate elsewhere, `--dir` or `-C` MUST be provided (matching `git` and `make`).

### CLI-052 — No Global State Mutation

**MUST NOT**

A CLI invocation MUST NOT modify the user's shell environment, `PATH`, or files outside the project. If it must, it MUST ask first.

## Distribution and Packaging

### CLI-053 — Single Binary Preference

**SHOULD**

When possible, the tool SHOULD distribute as a single binary. Go, Rust, and C++ compile to a single binary. Node.js CLIs SHOULD bundle via `pkg`, `bun build --compile`, or `nexe`. Python CLIs SHOULD ship via `pipx`, `uv tool`, `pex`, or `zipapp`. The user SHOULD NOT need to install a runtime separately.

### CLI-054 — Versioned Releases

**MUST**

Every release MUST have a version number. The version MUST be queryable with `--version`.

### CLI-055 — Changelog Documentation

**MUST**

Every release MUST document what changed. Users need to know before upgrading.

### CLI-056 — No Auto-Update Without Consent

**MUST NOT**

If the tool auto-updates, it MUST do so with the user's consent, or on an explicit `tool update` command. Silent updates are hostile and MUST NOT be used.

### CLI-057 — Documented Install Path

**MUST**

The binary install location (`/usr/local/bin`, a package manager's prefix, or a user directory) MUST be documented. A tool that installs to a surprising location confuses users.

### CLI-058 — Clean Uninstall

**MUST**

An uninstall path MUST be provided or the package manager's uninstall MUST be documented. Files MUST NOT be left behind.

## AI-Specific CLI Discipline

### CLI-077 — Command Discovery Before Creation

**MUST**

Before creating a new subcommand or top-level CLI tool, the assistant MUST search the project for an existing equivalent. Inventing parallel commands creates interface fragmentation and user confusion.

See MAS-035 in `_universal/00-master-anti-slop.md`.

### CLI-078 — Parser Library API Verification

**MUST**

Before using a parser library method (flag definition, subcommand registration, middleware hook), the assistant MUST verify the API exists in the installed version. Different versions of `commander`, `clap`, `click`, and `cobra` have different APIs. Invented methods produce runtime errors that are invisible at compile time.

See MAS-036 in `_universal/00-master-anti-slop.md`.

### CLI-079 — Flag Conflict Verification

**MUST**

Before adding a new flag or short option, the assistant MUST verify no conflict with existing global or command-level flags. Flag collisions produce silent misbehavior that is difficult to debug.

## Anti-Patterns

### CLI-060 — Schema-Validated Config

**MUST NOT**

A config that accepts any key, silently ignoring typos, MUST NOT be used. A schema MUST be validated at startup. Unknown keys MUST be errors or warnings.

### CLI-061 — Deterministic Output

**MUST NOT**

Non-deterministic output (e.g., order depending on filesystem iteration) MUST NOT be produced. Output MUST be sorted deterministically.

### CLI-062 — Shell Agnosticism

**MUST NOT**

A tool MUST NOT assume a specific shell. It MUST work from any shell on the supported platforms (bash, zsh, fish, PowerShell where applicable).

### CLI-063 — Clear Error Messages

**MUST**

Error messages MUST include the path, the operation, and the reason. Generic errors like `Error: ENOENT` are prohibited.

Example (illustrative):

BAD: `Error: ENOENT`.

GOOD: `Error: config file not found at /path/to/.toolrc`.

### CLI-064 — Position-Independent Global Flags

**MUST**

Global flags MUST work before or after the subcommand. Position-dependent flags are a bug.

Example (illustrative):

BAD: `tool --verbose cmd arg1 arg2` where `--verbose` must come after `cmd`.

GOOD: Global flags work in either position.

### CLI-065 — Documented Hidden Flags

**MUST NOT**

Hidden global flags (e.g., `--config` that only works in one position, undocumented) MUST NOT exist. Placement MUST be documented, or flags MUST be position-independent.

### CLI-066 — Stdin Convention Compliance

**MUST**

A command MUST use an explicit `-` for stdin, matching `cat`, `grep`, and other Unix tools. Silently reading stdin when no file argument is given is prohibited.

### CLI-067 — Trailing Newline

**MUST**

Every line of output MUST end with `\n`. Output without a trailing newline breaks shell pipelines.

### CLI-068 — Pipe-Safe Exit Codes

**SHOULD**

When documenting pipeline patterns, `set -o pipefail` SHOULD be mentioned, or a `--log <path>` flag SHOULD be provided that writes to a file without a pipe to preserve exit codes.

### CLI-069 — Machine-Readable Output Format

**MUST**

A command that produces human-readable output by default MUST also provide a machine-readable format (`--format json` or `--format tsv`) for scripts.

### CLI-070 — Backward-Compatible Flag Renames

**MUST NOT**

Flag renames MUST NOT occur in minor versions. The old flag MUST be kept as an alias, deprecated, and removed only in the next major version.

Example (illustrative):

BAD: Renaming `--output` to `--out` in a minor release.

GOOD: Add `--out` as an alias, deprecate `--output`, remove in next major.

### CLI-071 — Single-Meaning Flags

**MUST**

A flag MUST have one meaning across all commands. `--force` MUST NOT mean "overwrite", "skip confirmation", and "continue on error" in different commands. Additional behavior MUST use additional flags (e.g., `--continue-on-error`).

### CLI-072 — Bounded Symlink Recursion

**MUST NOT**

Unbounded recursion on symlinks is prohibited. Symlinks MUST NOT be followed unless `--follow-symlinks` is set.

### CLI-073 — Wrapped Help Text

**MUST**

Help text MUST be wrapped to 80 columns and indented consistently. Lines over 120 characters that wrap badly in terminals are prohibited.

### CLI-074 — Stdin/Stdout Dash Support

**MUST**

A command MUST support `-` as stdin and stdout where applicable, matching Unix conventions. `tool parse -` MUST read stdin; `tool export -` MUST write stdout.

### CLI-075 — Parseable Version Output

**MUST**

`tool --version` MUST print a single line, parseable by a script. Empty or non-parseable version output is prohibited.

### CLI-076 — Silent Failure Prohibition

**MUST NOT**

A command MUST NOT fail without any message. The error MUST be printed to stderr and the process MUST exit non-zero.

See MAS-037 in `_universal/00-master-anti-slop.md`.

## Response to Violation

When a rule in this file is violated, report:

Violation: CLI-{NNN}
Reason: {one-line reason}
Correction: {smallest fix}

For multiple violations, report each rule ID separately.

Do not replace a technical correction with a generic explanation.