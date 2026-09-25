---
id: 02-cli-anti-slop
title: "CLI Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: delivery
version: 2
---

# CLI Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
generic security, dependency addition, output format) are NOT
repeated here.

This file covers rules specific to command-line tools: command
design, argument parsing, exit codes, standard streams, signals,
help text, configuration, and distribution. It does NOT cover
application code (see other delivery files), language rules (see
the language files), framework rules (see the framework files), or
security and performance concerns (see the concern files).

A CLI is a program that runs unattended in scripts, in CI, and from
a shell. Every behavior is a contract with the caller. The
contract is the tool's public API.

## 1. Stack Assumptions

This file applies to CLIs distributed as:

- Standalone binaries (Go, Rust, C, C++).
- Node.js scripts (`#!/usr/bin/env node`).
- Python scripts (`#!/usr/bin/env python3`).
- Shell scripts.
- Bundled scripts via `pkg`, `pyinstaller`, `nexe`, or similar.

The examples use POSIX shell conventions. The principles are
language-agnostic. Parser library choices (commander, click, cobra,
clap) live in the framework files. Language-specific rules live in
the language files.

## 2. Delivery Contracts

A CLI commits to seven contracts. Every section below enforces one
or more of these.

### 2.1 Command Interface Stability

Once a flag, subcommand, or output format is documented, consumers
depend on it. Changing it requires a major version bump.

### 2.2 Exit Code Correctness

Exit codes carry success or failure. A zero exit means success; a
non-zero exit means failure. Scripts depend on this.

### 2.3 Stream Separation

Data goes to stdout. Diagnostics, progress, and errors go to
stderr. The separation allows piping without corruption.

### 2.4 Non-Interactive by Default

A command that runs in a script does not block waiting for input
unless explicitly in interactive mode.

### 2.5 Signal Safety

The tool handles SIGINT and SIGTERM by cleaning up and exiting
with the conventional code.

### 2.6 Configuration Determinism

Given the same flags, environment, config files, and inputs, the
command produces the same output.

### 2.7 Reproducible Distribution

The installed version matches the source version. The version is
queryable with `--version`.

## 3. Command Design

### 3.1 One Command, One Job

A CLI does one thing. `git` is a suite of commands, each doing one
thing. A binary named `mytool` that runs migrations, sends emails,
and generates reports is three tools.

### 3.2 Conventional Subcommand Structure

`tool [global-flags] <command> [command-flags] [args]`.

Global flags precede the command. Command flags follow it. Every
subcommand has its own `--help`. This structure matches `git`,
`docker`, and `kubectl`, so it is already familiar.

### 3.3 Verb-Noun Subcommand Names

Subcommands are verbs or verb-noun pairs.

BAD: `tool users`, `tool data`, `tool thing`.

GOOD: `tool list-users`, `tool export-data`, `tool create-thing`.

The name tells the user what the command does.

### 3.4 No Overloaded Commands

A subcommand that behaves differently based on multiple flags is
hard to document and hard to test.

BAD: `tool sync --from x --to y --mode full --direction both`.

GOOD: `tool sync-full` and `tool sync-incremental` as separate
commands, with shared config.

## 4. Argument Parsing

### 4.1 Use a Parser Library

Hand-parsing `process.argv` or `sys.argv` beyond trivial cases
leads to inconsistent help, missing validation, and bugs.

Use the language's standard or de-facto parser: `commander`,
`yargs`, `cac`, `argparse`, `click`, `typer`, `cobra`, `pflag`,
`clap`, `optparse`.

### 4.2 Follow POSIX and GNU Conventions

- Short flags: `-h`, `-v`, `-f value`.
- Long flags: `--help`, `--verbose`, `--file value` or
  `--file=value`.
- Combined short flags: `-vf` only for flags that take no value.
- `--` terminates flag parsing; the rest are positional arguments.

Do not invent a new convention. Users expect POSIX.

### 4.3 Short Flags for Common Options

The conventional short flags:

- `-h` for `--help`.
- `-v` for `--verbose` (or `--version` in some tools).
- `-V` for `--version` when `-v` is verbose.
- `-q` for `--quiet`.
- `-f` for `--file` or `--force` (do not use both in one tool).
- `-o` for `--output`.
- `-n` for `--dry-run` or `--no-...` (context-dependent).

### 4.4 Long Flags for Everything Else

A flag not in the conventional list has only a long form.
`--max-retries` does not need a short form.

### 4.5 Kebab-Case Flag Names

BAD: `--maxRetries`, `--MaxRetries`, `--max_retries`.

GOOD: `--max-retries`.

GNU convention uses kebab-case.

### 4.6 Boolean Flags Are Flags, Not Options

BAD: `--verbose true`, `--verbose=false`.

GOOD: `--verbose`, `--no-verbose`.

A boolean flag is present or absent. A `--no-` prefix negates it.

### 4.7 Required Arguments Have No Brackets

In help text:

- `<file>` = required.
- `[file]` = optional.
- `<file...>` = one or more.
- `[file...]` = zero or more.

Match the convention. Do not invent.

## 5. Validation and Defaults

### 5.1 Validate All Arguments

Arguments come from the user. Validate:

- Required arguments are present.
- Types match (number where a number is expected).
- Enumerated values are in the allowed set.
- File paths exist when they must.
- Mutually exclusive flags are not both set.

An invalid argument produces a clear error and exits with code 2.

### 5.2 Sensible Defaults

A tool that requires ten flags to do anything is unfriendly. Default
to the common case. Expose flags for the uncommon case.

### 5.3 Configuration Precedence

Standard precedence, highest to lowest:

1. Command-line flags.
2. Environment variables.
3. Project config file (`.mytoolrc` in the current directory).
4. User config file (`~/.config/mytool/config`).
5. Built-in defaults.

Document the precedence in `--help`. Follow it consistently.

### 5.4 Environment Variable Names

- Uppercase with a consistent prefix: `MYTOOL_API_KEY`.
- Never collide with common variables (`PATH`, `HOME`, `USER`,
  `EDITOR`).
- Document every env var in the help text.

### 5.5 Explicit Config Paths

The config file has a documented default location. `--config
<path>` overrides it. `--no-config` disables loading entirely.

### 5.6 No Silent Config Loading

Loading a config file from a surprising location confuses users.
Print the loaded config path to stderr in verbose mode.

## 6. Exit Codes

### 6.1 Zero for Success, Non-Zero for Failure

- `0`: success.
- `1`: general error.
- `2`: usage error (bad arguments).
- `64`-`78`: reserved by `sysexits.h` for specific failures.
- `126`: command found but not executable.
- `127`: command not found.
- `130`: terminated by SIGINT (128 + 2).
- `143`: terminated by SIGTERM (128 + 15).

### 6.2 Exit Codes Are Public API

Scripts depend on exit codes. Changing an exit code from `1` to `2`
breaks callers. Treat exit codes as documented contract.

### 6.3 Distinct Codes for Distinct Failures

BAD: `1` for both "file not found" and "invalid JSON".

GOOD: `1` for general error, `2` for usage error, and a documented
set of additional codes for specific failures.

### 6.4 Document the Codes

The help text lists the exit codes the tool produces. Callers should
not have to read the source.

## 7. Standard Streams

### 7.1 stdout for Data, stderr for Everything Else

BAD:
```bash
echo "Processing file..." > output.txt
```

GOOD:
```bash
echo "Processing file..." >&2
```

Program output that a caller might pipe goes to stdout. Logs,
progress, and errors go to stderr. A pipe between two tools must
not receive progress messages.

### 7.2 Exit 0 With stderr Output Is Valid

A successful run may still produce warnings on stderr. Do not treat
any stderr output as failure.

### 7.3 Respect `isatty`

When stdout is a TTY, use colored output, progress bars, and
spinners. When stdout is not a TTY, use plain output, no progress,
no colors.

A JSON output piped to `jq` with ANSI codes is a bug.

### 7.4 `--no-color` and `NO_COLOR`

Respect the `NO_COLOR` environment variable (see
https://no-color.org/). Also provide `--no-color` as a flag. The
flag overrides the environment.

### 7.5 No Secrets on stdout or stderr

Passwords, tokens, and keys never appear on either stream, even in
debug mode. Redact them in log output.

### 7.6 Buffering

stdout is line-buffered when connected to a terminal and
block-buffered when piped. A tool that writes a progress line and
expects it to appear immediately must flush or write to stderr.

## 8. Help and Documentation

### 8.1 Every Command Has `--help`

`tool --help` shows the top-level commands and global flags.
`tool <command> --help` shows the command's flags and arguments.
Both exit with code 0.

### 8.2 Help Text Structure

- One-line summary.
- Usage line.
- Arguments with types and defaults.
- Options with types and defaults.
- At least one example.
- Exit codes.
- Environment variables that affect behavior.

### 8.3 No Help That Lies

If a flag is documented, it works. If a flag works, it is
documented. Help text and behavior drift; test them together.

### 8.4 `--version`

`tool --version` prints the version and exits 0. The format is
consistent across releases. A common format is `tool 1.4.2`.

### 8.5 Examples That Work

Every example in help text must actually run against the current
version. Stale examples are worse than no examples.

### 8.6 Man Pages for Complex Tools

A tool with subcommands or many flags ships a man page. The man
page is generated from the same source as `--help` when possible.

## 9. Signals and Interruption

### 9.1 Handle SIGINT Gracefully

On Ctrl+C, the tool cleans up (temp files, locks, partial output)
and exits with code 130.

### 9.2 Handle SIGTERM

On SIGTERM, the same cleanup runs and the tool exits with code 143.

### 9.3 Never Ignore Signals

Ignoring SIGINT traps the user in a hanging process. Never do it.
A tool that must complete a critical section defers the signal, not
ignores it.

### 9.4 Clean Up on Exit

A tool that creates temp files, acquires locks, or opens
connections cleans up in a `finally` block or a signal handler.

### 9.5 Atomic Writes

A command that writes a file either writes it completely or leaves
the original unchanged. Write to a temp file, then rename.

BAD: Write directly to `output.json`; a crash mid-write leaves a
corrupt file.

GOOD: Write to `output.json.tmp`, then `rename` to `output.json`.

### 9.6 Idempotent Cleanup

A signal handler that runs twice must not break. Signal handlers
are not reentrant; use a flag to mark "cleanup in progress".

## 10. Long-Running Operations

### 10.1 Progress to stderr

Progress bars, spinners, and status messages go to stderr. Never
stdout. The stdout stream belongs to the actual output.

### 10.2 Progress Only on TTY

When stderr is not a TTY, do not emit progress. Logs replace
progress in CI environments.

### 10.3 Report Start and End

A long-running command prints a "starting..." line at the start and
a "done" line at the end. The lines go to stderr. This allows a
caller to see in logs what happened.

### 10.4 Interruptible Work

A long-running loop checks for interruption between iterations.
SIGINT cancels the loop, not just the current operation.

### 10.5 Timeout for Network Operations

Every network call has a timeout. `--timeout <seconds>` overrides
the default. A command that hangs forever is a bug.

## 11. Non-Interactive by Default

### 11.1 No Interactive Prompts

A command runs to completion without user input. Interactive
prompts are opt-in.

BAD: A command that asks for confirmation in CI.

GOOD: A command that requires `--force` for destructive actions,
and only prompts when stdin is a TTY and `--no-input` is not set.

### 11.2 `--no-input` Flag

A global `--no-input` flag disables all prompts. In its presence,
the command uses defaults or fails clearly.

### 11.3 Destructive Actions Require Confirmation

A destructive command (`delete`, `drop`, `overwrite`) requires one
of:

- `--force` for non-interactive confirmation.
- A prompt when interactive.
- `--dry-run` as a default, with `--apply` to execute.

### 11.4 `--dry-run` for Every Destructive Command

A destructive command provides `--dry-run`. It prints what would
happen without doing it. This is the safest way to preview.

## 12. Configuration and Environment

### 12.1 No Hidden Config

The tool does not read configuration from surprising places. Every
config source is documented in `--help`.

### 12.2 Environment Overrides Are Visible

If an environment variable overrides a flag, the help text says so.
Users debug faster when the source of a value is visible.

### 12.3 Sensible Working Directory Behavior

The tool operates on the current directory by default. If it must
operate elsewhere, provide `--dir` or `-C` (matching `git` and
`make`).

### 12.4 No Global State Mutation

A CLI invocation does not modify the user's shell environment,
`PATH`, or files outside the project. If it must, ask first.

## 13. Distribution and Packaging

### 13.1 Single Binary When Possible

- Go, Rust, and C++ compile to a single binary.
- Node.js CLIs bundle via `pkg`, `bun build --compile`, or `nexe`,
  or ship with a `node_modules`.
- Python CLIs ship via `pipx`, `uv tool`, `pex`, or `zipapp`.

The user should not need to install a runtime separately if
avoidable.

### 13.2 Versioned Releases

Every release has a version number. The version is queryable with
`--version`.

### 13.3 Changelog

Every release documents what changed. Users need to know before
upgrading.

### 13.4 No Auto-Update Without Consent

If the tool auto-updates, it does so with the user's consent, or
on an explicit `tool update` command. Silent updates are hostile.

### 13.5 Install Path

Document where the binary is installed (`/usr/local/bin`, a package
manager's prefix, or a user directory). A tool that installs to a
surprising location confuses users.

### 13.6 Uninstall

Provide an uninstall path or document the package manager's
uninstall. Do not leave files behind.

## 14. Anti-Patterns

### 14.1 No `--help`

A CLI without `--help` is unusable without reading the source.

### 14.2 Exit Code Always 0

BAD: A failing command that exits 0 "to not scare users".

GOOD: Exit non-zero on failure. Scripts depend on this.

### 14.3 Errors to stdout

BAD: `console.log("Error: file not found")`.

GOOD: `console.error("Error: file not found")`.

Piped output that includes error text is a bug.

### 14.4 Colors When Piped

BAD: ANSI codes in a JSON output meant for `jq`.

GOOD: Detect `isatty`, disable colors when piped.

### 14.5 Silent Failure

BAD: A command that fails without any message.

GOOD: Print the error to stderr and exit non-zero.

### 14.6 Interactive by Default

BAD: A command that prompts for input in CI.

GOOD: Non-interactive by default. Interactive only via
`--interactive`.

### 14.7 Inconsistent Flag Names

BAD: `--output` in one command, `--out` in another, `-o` in a
third.

GOOD: One name across all commands.

### 14.8 Destructive Without Confirmation

BAD: `tool clean` deletes the cache without asking.

GOOD: `tool clean` asks, or requires `--force`, or defaults to
`--dry-run`.

### 14.9 Progress Bars on Piped Output

BAD: A spinner written to stdout that ends up in a JSON file.

GOOD: Progress on stderr, and only when stderr is a TTY.

### 14.10 Config File Without a Schema

BAD: A config that accepts any key, silently ignoring typos.

GOOD: A schema, validated at startup. Unknown keys are errors or
warnings.

### 14.11 Version Without a Query

BAD: The user cannot tell which version is installed.

GOOD: `--version` prints the version in a parseable format.

### 14.12 Non-Deterministic Output

BAD: A command whose output order depends on filesystem iteration
order.

GOOD: Sort output deterministically.

### 14.13 Assuming a Shell

BAD: A tool that only works in bash on Linux.

GOOD: A tool that works from any shell on the supported platforms.

### 14.14 Unclear Error Messages

BAD: `Error: ENOENT`.

GOOD: `Error: config file not found at /path/to/.toolrc`.

Include the path, the operation, and the reason.

### 14.15 No `--dry-run`

BAD: A destructive command with no way to preview.

GOOD: `--dry-run` prints what would happen without doing it.

### 14.16 Argument Reordering

BAD: `tool --verbose cmd arg1 arg2` where `--verbose` must come
after `cmd`.

GOOD: Global flags work before or after the subcommand.

### 14.17 Hidden Global Flags

BAD: A `--config` flag that only works when placed before the
subcommand, undocumented.

GOOD: Document placement, or make flags position-independent.

### 14.18 Environment Variables Without Prefix

BAD: An env var `API_KEY` that collides with other tools.

GOOD: `MYTOOL_API_KEY`.

### 14.19 Reading stdin Without a Flag

BAD: A command that silently reads stdin when no file argument is
given.

GOOD: An explicit `-` for stdin, matching `cat`, `grep`, and other
Unix tools.

### 14.20 Output Without a Trailing Newline

BAD: A command that prints a value with no newline, breaking shell
pipelines.

GOOD: Every line ends with `\n`.

### 14.21 Losing Exit Code Through a Pipe

BAD: `tool | tee log.txt` where the exit code of `tee` masks the
exit code of `tool`.

GOOD: Document the pattern with `set -o pipefail`, or provide a
`--log <path>` flag that writes to a file without a pipe.

### 14.22 Mixed stdout and stderr

BAD: A command that writes some output to stdout and some to
stderr, with no rule.

GOOD: A documented rule: data to stdout, everything else to
stderr.

### 14.23 Human-Readable Default, No Machine Format

BAD: A command that only outputs aligned text.

GOOD: A `--format json` (or `tsv`) for scripts. Default can stay
human-readable.

### 14.24 Breaking Flag Renames in Minor Versions

BAD: Renaming `--output` to `--out` in a minor release.

GOOD: Add `--out` as an alias, deprecate `--output`, remove it in
the next major.

### 14.25 Overloaded `--force`

BAD: `--force` means "overwrite", "skip confirmation", and
"continue on error" in different commands.

GOOD: One flag, one meaning. Add `--continue-on-error` if needed.

### 14.26 Unbounded Recursion on Symlinks

BAD: A `tool sync` that follows symlinks and recurses infinitely.

GOOD: Do not follow symlinks unless `--follow-symlinks` is set.

### 14.27 No Progress for Long Operations

BAD: A command that runs for 10 minutes with no output. The user
thinks it is hung.

GOOD: Progress to stderr, or at least a "working..." line at the
start.

### 14.28 Help Text That Fits the Terminal

BAD: Help text with lines over 120 characters that wrap badly.

GOOD: Help text wrapped to 80 columns, indented consistently.

### 14.29 No Support for `-` as stdin/stdout

BAD: A command that only accepts file paths.

GOOD: `tool parse -` reads stdin; `tool export -` writes stdout.
This matches Unix conventions.

### 14.30 Publishing Without Version in Output

BAD: `tool --version` prints nothing or a non-parseable string.

GOOD: `tool --version` prints a single line, parseable by a script.

## 15. Response to Violation

If a previous response violated a rule here:

```
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

No justification. No apology paragraph. Fix and move on.
