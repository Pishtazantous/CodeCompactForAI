# CodeCompactForAI

| [English](README.md) | [فارسی](README.fa.md) |
|---|---|

A command-line tool for preparing software projects to send to AI models
without sending the entire codebase. Instead, you send a compact map and let
the AI decide which files it needs.

Reduces the amount of data sent to AI by a factor of 10 to 50, which lowers
cost and usually improves response accuracy.

## Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Generating Full Project Output](#generating-full-project-output)
- [Complete AI Workflow](#complete-ai-workflow)
- [Commands](#commands)
- [Common Options](#common-options)
- [Ignore File](#ignore-file)
- [Sensitive Files](#sensitive-files)
- [Prompt Structure](#prompt-structure)
- [Auxiliary Tools](#auxiliary-tools)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)
- [License](#license)
- [Compatibility](#compatibility)

## Prerequisites

- Python 3.9 or later (3.11+ recommended)
- Git (optional, but recommended)
- tiktoken (optional, for accurate token counting)

```bash
pip install tiktoken    # optional
```

## Quick Start

No installation is required. Copy the repository and run the commands.

```bash
# Verify the tool works
python codemerge.py --help
python codemerge.py langs

# Build a compact manifest of the project
python codemerge.py manifest --format md -o .ai/manifest.md

# Send .ai/manifest.md to the AI with the prompts described below
# After the AI requests files, fetch them
python codemerge.py fetch lib/api/auth.ts lib/api/client.ts -o .ai/bundle.txt
```

Then send `.ai/bundle.txt` to the AI.

## Generating Full Project Output

In some situations you need the whole project in a single file: an initial
context load, a backup, or an offline review. `codemerge.py` has four
methods for this, each suited to a different scenario.

### Method 1 — Manifest only (paths and symbols)

Sends the project structure without file contents.

```bash
# Text
python codemerge.py manifest --all-files -o .ai/manifest-full.txt

# Markdown
python codemerge.py manifest --all-files --format md -o .ai/manifest-full.md

# JSON
python codemerge.py manifest --all-files --format json -o .ai/manifest-full.json

# Without symbols and imports
python codemerge.py manifest --all-files --no-symbols --no-imports -o .ai/files-list.txt
```

`--all-files` ignores the language filter.

Typical size: 10 to 30 KB for a project with 200 files.

### Method 2 — Full content bundle

Includes the text of every selected file.

```bash
# First run: diff equals the entire project
python codemerge.py diff -o .ai/full_project.txt

# If diff has been run before and you want the whole project again
python codemerge.py diff --full --reset-state -o .ai/full_project.txt

# Without header
python codemerge.py diff --full --reset-state --no-header -o .ai/full_project.txt
```

`fetch` requires an explicit list of files, so it is not convenient for
"the whole project". `diff --full` selects every file automatically.

### Method 3 — Language-filtered bundle

For multi-language projects where you want only one language.

```bash
# TypeScript and JavaScript only
python codemerge.py diff --full --reset-state -l typescript,javascript -o .ai/ts-only.txt

# Python only
python codemerge.py diff --full --reset-state -l python -o .ai/backend.txt

# Markdown only
python codemerge.py diff --full --reset-state -l markdown -o .ai/docs.txt
```

### Method 4 — Custom file list

For cases where you have a precise list of files (such as `md-list.txt`).

```bash
# From a file list
python codemerge.py fetch --files-from md-list.txt -o .ai/bundle-custom.txt

# From stdin
Get-Content md-list.txt | python codemerge.py fetch --from-stdin -o .ai/bundle-custom.txt
```

### Warnings

Large outputs can exceed the AI context window. Most current models cap at
about 128K tokens, and an average Node.js project can exceed 100K tokens in
full-bundle mode. Every large bundle also multiplies the input cost of the
API request. As a rule of thumb, if a bundle exceeds 30,000 tokens, split it.

The `--allow-sensitive` flag includes `.env`, private keys, and other
credentials in the bundle. It should be used only when you are sure the
output will not be sent to a third party.

### Estimating Size and Cost

Before generating a full bundle, preview which files would be included:

```bash
python codemerge.py diff --dry-run --full
```

Sample output:

```text
[full] Would merge 47 file(s) into .ai/full_project.txt:
  codemerge.py  (60,234 bytes)
  docs/CHEATSHEET.md  (3,412 bytes)
  ...
Total changed size: 342,891 bytes
```

After generating, estimate tokens and cost:

```bash
python tools/estimate.py .ai/full_project.txt
python tools/estimate.py .ai/full_project.txt --model deepseek-chat
python tools/estimate.py .ai/full_project.txt --model gpt-4o
```

### Recommendations

| Scenario | Method |
|---|---|
| Small project (fewer than 30 files) | Method 2 (`diff --full`) |
| Medium project (30 to 100 files) | Method 1, then Method 4 |
| Large project (more than 100 files) | Method 1, or Method 3 |
| Multi-language project | Method 3, one language at a time |
| Archive or backup | Method 2 or 4 |
| First submission to AI | Method 1, then Method 4 |

### Combining with .codemergeignore

`.codemergeignore` rules apply to all four methods. To bypass them:

```bash
python codemerge.py diff --full --reset-state --no-ignore-file -o .ai/everything.txt
```

Combining `--no-ignore-file` with `--allow-sensitive` will include every
file in the project, including credentials. This should be avoided.

### Files Always Excluded

Even with `--all-files`, these never enter the bundle:

| Category | Examples |
|---|---|
| System folders | `.git`, `node_modules`, `__pycache__`, `dist`, `build` |
| Lock files | `package-lock.json`, `yarn.lock`, `poetry.lock` |
| Minified files | `*.min.js`, `*.min.css`, `*.map` |
| Binary files | images, fonts, archives |
| Sensitive files | `.env`, `*.pem`, `*.key`, `id_rsa` |
| Files over `--max-size` | default 100 MB |

To include sensitive files, use `--allow-sensitive`. Binary files cannot be
included by design. Lock files can be force-included with
`--include package-lock.json`.

## Complete AI Workflow

### Step 1 — Preparation

```powershell
# Optional but recommended: snapshot before starting
python tools/snapshot.py --label before-session

# Build the manifest
python codemerge.py manifest --format md -o .ai/manifest.md
```

### Step 2 — Send prompts to AI

Send the prompts in this order:

1. `prompts/01-system.md` — base rules
2. `prompts/01-system-append-2.md` — editing rules and output format
3. `prompts/02-manifest.md` together with the contents of `.ai/manifest.md`
4. `prompts/Anti-AI-Slop/00-master-anti-slop.md` — general anti-slop rules
5. `prompts/Expertise and Experience/00-anti-slop-core.md` — project rules
6. At most one of `prompts/Expertise and Experience/XX-*.md`
7. One task prompt: `prompts/03-bug-fix.md` through `prompts/08-explain-code.md`

Only one expertise file should be used per session. Combining two can cause
the AI to mix incompatible guidance.

### Step 3 — Receive the AI file request

The AI responds with:

````
```codemerge-fetch
lib/api/auth.ts
lib/api/client.ts
store/authStore.ts
```
````

Run:

```powershell
python codemerge.py fetch lib/api/auth.ts lib/api/client.ts store/authStore.ts -o .ai/bundle.txt

# Or from a file
python codemerge.py fetch --files-from requested.txt -o .ai/bundle.txt
```

### Step 4 — Send the bundle to the AI

Paste the contents of `.ai/bundle.txt` into the conversation.

### Step 5 — Apply AI changes

The AI responds with file blocks:

````
```file:lib/api/auth.ts
<full file content>
```
````

Save the response to `ai_response.md`, then:

```powershell
python tools/apply_ai_output.py ai_response.md --dry-run
python tools/apply_ai_output.py ai_response.md
.\tools\verify.ps1
```

### Step 6 — End of session

```powershell
python codemerge.py diff -o .ai/changes.txt
python tools/session_summary.py --last 1
```

### Step 7 — Next session

```powershell
python codemerge.py diff -o .ai/changes.txt
```

Send this along with `prompts/09-continue-session.md`.

## Commands

### manifest

```bash
python codemerge.py manifest [OPTIONS]
```

| Option | Description |
|---|---|
| `--format {text,md,json}` | Output format (default: text) |
| `--no-symbols` | Exclude functions and classes |
| `--no-imports` | Exclude imports |
| `--max-tokens N` | Soft token cap |

Examples:

```bash
python codemerge.py manifest -o .ai/manifest.txt
python codemerge.py manifest -l typescript -o .ai/manifest.txt
python codemerge.py manifest --format md -o .ai/manifest.md
python codemerge.py manifest --no-symbols --no-imports -o .ai/files.txt
```

### fetch

```bash
python codemerge.py fetch FILES... [OPTIONS]
```

| Option | Description |
|---|---|
| `FILES ...` | File paths relative to the project root |
| `--files-from FILE` | Read paths from a file |
| `--from-stdin` | Read paths from stdin |

Examples:

```bash
python codemerge.py fetch lib/api/auth.ts lib/api/client.ts -o .ai/bundle.txt
python codemerge.py fetch --files-from requested.txt -o .ai/bundle.txt
Get-Content requested.txt | python codemerge.py fetch --from-stdin -o .ai/bundle.txt
```

### diff

```bash
python codemerge.py diff [OPTIONS]
```

| Option | Description |
|---|---|
| `--state-file PATH` | State file path (default: `<output>.state.json`) |
| `--full` | Force full merge |
| `--reset-state` | Delete the state file before running |
| `--dry-run` | Show changes without writing |

Behavior:

| Scenario | Result |
|---|---|
| First run | Full mode |
| No changes | Prints `No changes since last run.` |
| File changed | Only that file |
| File deleted | Reported in the header |
| `.codemergeignore` changed | Automatically switches to full |

### search

```bash
python codemerge.py search PATTERN [OPTIONS]
```

| Option | Description |
|---|---|
| `PATTERN` | Regular expression or plain text |
| `--max-hits N` | Maximum results (default 500) |

Examples:

```bash
python codemerge.py search "handleLogin"
python codemerge.py search "function handle.*Login" -l typescript
python codemerge.py search UserRepository --output hits.txt
```

### langs

```bash
python codemerge.py langs
```

## Common Options

These options are available on `manifest`, `fetch`, `diff`, and `search`:

| Option | Description |
|---|---|
| `-l`, `--lang LANG [LANG ...]` | Language filter |
| `-o`, `--output FILE` | Output file |
| `-r`, `--root DIR` | Project root |
| `--max-size MB` | Maximum file size (default 100) |
| `--no-git` | Ignore Git |
| `--include PATTERN [...]` | Glob patterns to force-include |
| `--exclude PATTERN [...]` | Glob patterns to exclude |
| `--allow-sensitive` | Include sensitive files |
| `--all-files` | Ignore the language filter |
| `--no-header` | Do not write a header |
| `-q`, `--quiet` | Suppress the summary |
| `--ignore-file PATH` | Custom ignore file |
| `--no-ignore-file` | Do not read any ignore file |

## Ignore File

`.codemergeignore` at the project root uses gitignore syntax:

```gitignore
# Blog content
content/posts/
content/authors/

# Backup files
*.bak
*.tsbuildinfo

# codemerge outputs
manifest*.txt
project_source*.txt
codemerge.state.json

# Exception
!content/README.md
```

Supported patterns:

| Pattern | Meaning |
|---|---|
| `docs/` | Directory at any depth |
| `/config.json` | Root only |
| `*.min.js` | Glob |
| `**/snapshots/` | Directory at any depth |
| `!docs/README.md` | Exception |
| `# comment` | Comment |

## Sensitive Files

The following files never appear in the output unless `--allow-sensitive`
is used:

- `.env` and variants, except `.env.example`, `.env.sample`,
  `.env.template`, `.env.dist`
- `id_rsa`, `id_dsa`, `id_ecdsa`, `id_ed25519`
- `credentials.json`, `secrets.json`, `service-account.json`
- `*.pem`, `*.key`, `*.p12`, `*.pfx`, `*.jks`, `*.keystore`, `*.ppk`,
  `*.secret`, `*.crt`
- `.netrc`, `.pypirc`, `.htpasswd`, `.pgpass`

## Prompt Structure

```
prompts/
├── 01-system.md                    base rules (Persian)
├── 01-system-append-2.md           editing rules (English)
├── 02-manifest.md                  used with the manifest
├── 03-bug-fix.md                   task: bug fix
├── 04-feature.md                   task: add feature
├── 05-refactor.md                  task: refactor
├── 06-code-review.md               task: code review
├── 07-tests.md                     task: write tests
├── 08-explain-code.md              task: explain code
├── 09-continue-session.md          continue session
├── 10-recovery.md                  recovery when the AI goes off track
├── 11-limit-files.md               limit request scope
├── 12-long-response.md             manage long responses
├── 13-final-summary.md             final summary
├── 14-checklist.md                 checklist
├── Anti-AI-Slop/
│   └── 00-master-anti-slop.md      general anti-slop rules
├── Expertise and Experience/       expertise files (English)
│   ├── 00-anti-slop-core.md
│   ├── 01-frontend-architecture.md
│   ├── 02-typescript.md
│   └── ...
└── Expertise and Experience-FA/    expertise files (Persian)
```

Each prompt file starts with YAML frontmatter:

```yaml
---
id: 02-typescript
title: "TypeScript Expert"
lang: en
depends_on: []
category: expertise
version: 1
---
```

## Auxiliary Tools

Scripts in the `tools/` directory:

| Tool | Description |
|---|---|
| `snapshot.py` | Full snapshot of project files before major edits |
| `apply_ai_output.py` | Apply AI `file:` blocks to disk |
| `verify.ps1` / `verify.sh` | Run type-check, lint, tests, and build |
| `new_session.py` | Create a new session file |
| `session_summary.py` | Print recent session summaries |
| `estimate.py` | Estimate tokens and cost |
| `watch.py` | Run `diff` automatically when files change |
| `log_metrics.py` | Log AI workflow metrics |
| `setup_profile.ps1` | Install PowerShell shortcuts |
| `add_frontmatter.py` | Add YAML frontmatter to prompts |
| `fix_frontmatter_lang.py` | Fix the `lang` field in frontmatter |
| `diagnose_cheatsheet.py` | Detect missing files in a bundle |

Examples:

```powershell
# Snapshot
python tools/snapshot.py --label before-ai
python tools/snapshot.py --list
python tools/snapshot.py --restore before-ai

# Apply AI output
python tools/apply_ai_output.py ai_response.md --dry-run
python tools/apply_ai_output.py ai_response.md

# Verify
.\tools\verify.ps1
.\tools\verify.ps1 -SkipTests
.\tools\verify.ps1 -Only "type-check","lint"

# Session
python tools/new_session.py "auth refactor" --prev 02
python tools/session_summary.py --last 3

# Cost estimate
python tools/estimate.py .ai/bundle.txt --model deepseek-chat
```

## Testing

```bash
# Standard library
python -m unittest discover -s tests -v
python tests/test_codemerge.py

# With pytest (recommended)
pip install pytest
pytest tests/ -v
```

Tests cover `is_sensitive`, `IgnoreMatcher`, `extract_python`, `_extract_js`,
`write_bundle`, `compute_delta`, and `detect_lang`.

## Troubleshooting

### No source files found

- Check the selected language with `python codemerge.py langs`.
- Everything may be in `.codemergeignore`. Try `--no-ignore-file`.
- Try `--all-files`.

### Unknown language: xxx

Run `python codemerge.py langs` to see valid names.

### File exists in manifest but fetch rejects it

The file is probably binary, exceeds `--max-size`, or the path was given
relative to something other than the project root.

### diff always produces full output

The state file may not be writable, or `--root` changed between runs.

### Output is too large

```bash
python codemerge.py manifest --no-symbols --no-imports -o .ai/files.txt
python codemerge.py manifest --max-tokens 8000 -o .ai/manifest.txt
python codemerge.py diff --full -l typescript -o .ai/ts.txt
```

### Token count is inaccurate

```bash
pip install tiktoken
```

### grep does not work in PowerShell

Use `Select-String` instead:

```powershell
Select-String -Path .ai/manifest.txt -Pattern "apiGet"
(Select-String -Path .ai/manifest.txt -Pattern "^  function ").Count
```

### Persian text is garbled in PowerShell

PowerShell 5.1 does not read UTF-8 by default. Use:

```powershell
Get-Content prompts/01-system.md -Encoding UTF8
```

Or install PowerShell 7 or later.

## Project Structure

```
CodeCompactForAI/
├── codemerge.py
├── README.md
├── README.fa.md
├── md-list.txt
├── .codemergeignore
│
├── docs/
│   ├── CHEATSHEET.md
│   └── codemerge.md
│
├── prompts/
│   ├── 01-system.md
│   ├── 01-system-append-2.md
│   ├── 02-manifest.md
│   ├── 03-bug-fix.md through 08-explain-code.md
│   ├── 09-continue-session.md through 14-checklist.md
│   ├── Anti-AI-Slop/
│   ├── Expertise and Experience/
│   └── Expertise and Experience-FA/
│
├── tools/
│   ├── snapshot.py
│   ├── apply_ai_output.py
│   ├── verify.ps1 / verify.sh
│   ├── new_session.py
│   ├── session_summary.py
│   ├── estimate.py
│   ├── watch.py
│   ├── log_metrics.py
│   ├── setup_profile.ps1
│   ├── add_frontmatter.py
│   ├── fix_frontmatter_lang.py
│   └── diagnose_cheatsheet.py
│
└── tests/
    └── test_codemerge.py
```

## License

MIT

## Compatibility

- Python 3.9 or later
- Windows, macOS, Linux
- Bash, PowerShell, cmd


