# CodeCompactForAI

A command-line tool for preparing software projects to send to AI models — without sending the entire project.

Instead of sending your whole codebase to AI, you first send a **compact map** and let the AI decide which files it needs. Result: **10 to 50 times less** data sent, lower cost, and more accurate responses.

---

## Table of Contents

1. [Quick Intro](#quick-intro)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [Generating Full Project Output](#generating-full-project-output)
6. [Complete AI Workflow](#complete-ai-workflow)
7. [codemerge.py Commands](#codemergepy-commands)
8. [Common Options](#common-options)
9. [Ignore File](#ignore-file)
10. [Sensitive Files](#sensitive-files)
11. [Prompt Structure](#prompt-structure)
12. [Auxiliary Tools](#auxiliary-tools)
13. [Testing](#testing)
14. [Troubleshooting](#troubleshooting)
15. [Project Structure](#project-structure)

---

## Quick Intro

`codemerge.py` is a single-file Python script that does four things:

| Command | Description |
|---|---|
| `manifest` | Build a compact project map (paths + imports + functions + classes) |
| `fetch` | Fetch full content of a specific list of files |
| `diff` | Fetch only files changed since the last run |
| `search` | Search for a symbol across the whole project |

Alongside these, there is a set of auxiliary tools in `tools/` for snapshots, applying AI output, verification, session management, and more.

---

## Prerequisites

- **Python 3.9+** (recommended: 3.11+)
- **Git** (optional, but recommended)
- **tiktoken** (optional, for accurate token counting)

```bash
pip install tiktoken    # optional
```

---

## Installation

No installation needed. Copy the project and use the commands.

```bash
# Health check
python codemerge.py --help
python codemerge.py langs
```

---

## Quick Start

Three commands to get started:

```bash
# 1. Build project map
python codemerge.py manifest --format md -o .ai/manifest.md

# 2. Send .ai/manifest.md to AI
#    (with suitable prompts — see "Complete AI Workflow")

# 3. After AI responds, fetch the requested files
python codemerge.py fetch lib/api/auth.ts lib/api/client.ts -o .ai/bundle.txt
```

Then send `.ai/bundle.txt` to the AI.

---

## Generating Full Project Output

Sometimes you need the whole project — not just selected files — in a single output file. For example:
- Initial context load for an AI that needs the complete picture (small projects)
- Archive or backup before major changes
- Offline review or transfer to another system
- Building a bundle for specific files (e.g., TypeScript only)

`codemerge.py` has four methods for this. Each method fits a different scenario.

### Method 1 — Full project manifest (list + symbols only)

**Best for:** Quickly sending the entire project structure to AI without file contents.

```bash
# Text format
python codemerge.py manifest --all-files -o .ai/manifest-full.txt

# Markdown format (AI-friendly)
python codemerge.py manifest --all-files --format md -o .ai/manifest-full.md

# JSON format (automation-friendly)
python codemerge.py manifest --all-files --format json -o .ai/manifest-full.json

# Most compact (no symbols and no imports)
python codemerge.py manifest --all-files --no-symbols --no-imports -o .ai/files-list.txt
```

**Note:** `--all-files` ignores the language filter and includes every text file.

**Typical size:** For a project with 200 files, around 10 to 30 KB.

### Method 2 — Full project content bundle (all file texts included)

**Best for:** Small projects or initial context loading.

```bash
# First run: diff = entire project (no prior state)
python codemerge.py diff -o .ai/full_project.txt

# If you've run diff before and want the whole project again:
python codemerge.py diff --full --reset-state -o .ai/full_project.txt

# Without headers (file contents only)
python codemerge.py diff --full --reset-state --no-header -o .ai/full_project.txt
```

**Why `diff` instead of `fetch`?** Because `fetch` requires an explicit list of files, and for "the whole project" you'd have to build the complete list yourself. Meanwhile, `diff` with `--full` selects all files automatically.

### Method 3 — Full bundle with language filtering

**Best for:** Multi-language projects where you want only one language.

```bash
# TypeScript / JavaScript only
python codemerge.py diff --full --reset-state -l typescript,javascript -o .ai/ts-only.txt

# Python only (backend)
python codemerge.py diff --full --reset-state -l python -o .ai/backend.txt

# Markdown only (documentation)
python codemerge.py diff --full --reset-state -l markdown -o .ai/docs.txt
```

### Method 4 — Full bundle from a specific list (custom list)

**Best for:** When you have an exact list of desired files (like `md-list.txt`).

```bash
# From file list
python codemerge.py fetch --files-from md-list.txt -o .ai/bundle-custom.txt

# From stdin
Get-Content md-list.txt | python codemerge.py fetch --from-stdin -o .ai/bundle-custom.txt
```

This is the most common method in the current project, since `md-list.txt` contains the exact list of 47 important project files.

---

### Warnings and Limitations

> ⚠️ **Output can be very large.** For projects with more than 50 files, the output may be several megabytes.

> ⚠️ **It can exceed the AI context window.** Current models have roughly 128K token contexts. An average Node.js project can be 100K+ tokens.

> ⚠️ **It increases API cost.** Every request with a large bundle multiplies the input cost several times.

> ⚠️ **`--allow-sensitive` is dangerous.** Misusing this flag causes `.env` and private keys to be included in the bundle and sent to AI.

**Golden rule:** If the bundle is over 30,000 tokens, split it into smaller parts.

---

### Estimating Size and Cost Before Generating

**Before generating full output, estimate its size:**

```bash
# Preview the list of files that would be merged (without writing)
python codemerge.py diff --dry-run --full

# Sample output:
# [full] Would merge 47 file(s) into .ai/full_project.txt:
#   codemerge.py  (60,234 bytes)
#   docs/CHEATSHEET.md  (3,412 bytes)
#   ...
# Total changed size: 342,891 bytes
```

**After generating, estimate tokens and cost:**

```bash
# Estimate tokens (if tiktoken is installed)
python tools\estimate.py .ai/full_project.txt

# Estimate cost for a specific model
python tools\estimate.py .ai/full_project.txt --model deepseek-chat
python tools\estimate.py .ai/full_project.txt --model gpt-4o
python tools\estimate.py .ai/full_project.txt --model claude-sonnet-4
```

---

### Practical Recommendations

| Scenario | Recommended Method |
|---|---|
| Small project (< 30 files) | Method 2 (`diff --full`) |
| Medium project (30-100 files) | Method 1 (manifest) + Method 4 (selective fetch) |
| Large project (> 100 files) | Method 1 (manifest) only, or Method 3 (language filter) |
| Multi-language project | Method 3 (each language separately) |
| Archive or backup | Method 2 or 4 (depending on need) |
| Initial AI submission | Method 1 (map) → then request from AI → Method 4 |

---

### Combining with `.codemergeignore`

`.codemergeignore` rules apply to **all methods**. For example, if you ignore `content/posts/`, it will not appear in any of the methods above.

To ignore ignore rules (e.g., to get a truly complete bundle):

```bash
python codemerge.py diff --full --reset-state --no-ignore-file -o .ai/everything.txt
```

> ⚠️ Using `--no-ignore-file` together with `--allow-sensitive` is **very dangerous**. Only use it in highly controlled environments.

---

### What Is Always Excluded (even in full mode)

Even with `--all-files`, these never enter the bundle:

| Category | Examples |
|---|---|
| System folders | `.git`, `node_modules`, `__pycache__`, `dist`, `build` |
| Lock files | `package-lock.json`, `yarn.lock`, `poetry.lock` |
| Minified files | `*.min.js`, `*.min.css`, `*.map` |
| Binary files | images, fonts, compressed files |
| Sensitive files | `.env`, `*.pem`, `*.key`, `id_rsa` |
| Large files | above `--max-size` (default: 100 MB) |

To include sensitive files: `--allow-sensitive` (very risky).
For binary files: there is no way — the tool deliberately excludes them.
For lock files: `--include package-lock.json` (force-include only).

---

## Complete AI Workflow

### Step 1 — Preparation

```powershell
# Snapshot before starting (optional, but recommended)
python tools\snapshot.py --label before-session

# Build manifest in Markdown format
python codemerge.py manifest --format md -o .ai\manifest.md
```

### Step 2 — Send prompts to AI

Copy and send the prompts to the AI in this order:

1. `prompts/01-system.md` — base rules
2. `prompts/01-system-append-2.md` — editing rules and output format
3. `prompts/02-manifest.md` + contents of `.ai/manifest.md`
4. `prompts/Anti-AI-Slop/00-master-anti-slop.md` — general anti-slop rules
5. `prompts/Expertise and Experience/00-anti-slop-core.md` — project-specific anti-slop rules
6. **At most one** of `prompts/Expertise and Experience/XX-*.md` — required expertise
7. One task: `prompts/03-bug-fix.md` through `prompts/08-explain-code.md`

> **Ironclad rule:** Never combine two expertise files in a single session.

### Step 3 — Receive AI request

The AI responds in this format:

```
```codemerge-fetch
lib/api/auth.ts
lib/api/client.ts
store/authStore.ts
```
```

You run it with:

```powershell
python codemerge.py fetch lib/api/auth.ts lib/api/client.ts store/authStore.ts -o .ai\bundle.txt
```

Or from a file:

```powershell
# Save the list in requested.txt
python codemerge.py fetch --files-from requested.txt -o .ai\bundle.txt
```

### Step 4 — Send bundle to AI

Copy the contents of `.ai/bundle.txt` into the conversation.

### Step 5 — Apply AI changes

The AI responds in this format:

```
```file:lib/api/auth.ts
<full file content>
```
```

Save the response to `ai_response.md` and run:

```powershell
# Preview
python tools\apply_ai_output.py ai_response.md --dry-run

# Apply
python tools\apply_ai_output.py ai_response.md

# Verify health
.\tools\verify.ps1
```

### Step 6 — End the session

```powershell
# Save state for future diff
python codemerge.py diff -o .ai\changes.txt

# Session summary
python tools\session_summary.py --last 1
```

### Step 7 — Next session

```powershell
# Send only changes to AI
python codemerge.py diff -o .ai\changes.txt
```

Along with `prompts/09-continue-session.md`.

---

## codemerge.py Commands

### `manifest` — Project map

```bash
python codemerge.py manifest [OPTIONS]
```

| Option | Description |
|---|---|
| `--format {text,md,json}` | Output format (default: `text`) |
| `--no-symbols` | Exclude functions/classes |
| `--no-imports` | Exclude imports |
| `--max-tokens N` | Soft token cap |

**Examples:**

```bash
# Full map
python codemerge.py manifest -o .ai/manifest.txt

# TypeScript only
python codemerge.py manifest -l typescript -o .ai/manifest.txt

# Markdown format (AI-friendly)
python codemerge.py manifest --format md -o .ai/manifest.md

# Compact
python codemerge.py manifest --no-symbols --no-imports -o .ai/files.txt
```

### `fetch` — Fetch file contents

```bash
python codemerge.py fetch FILES... [OPTIONS]
```

| Option | Description |
|---|---|
| `FILES ...` | File paths (relative to root) |
| `--files-from FILE` | Read list from file |
| `--from-stdin` | Read list from stdin |

**Examples:**

```bash
python codemerge.py fetch lib/api/auth.ts lib/api/client.ts -o .ai/bundle.txt

python codemerge.py fetch --files-from requested.txt -o .ai/bundle.txt

Get-Content requested.txt | python codemerge.py fetch --from-stdin -o .ai/bundle.txt
```

### `diff` — Changes only

```bash
python codemerge.py diff [OPTIONS]
```

| Option | Description |
|---|---|
| `--state-file PATH` | State path (default: `<output>.state.json`) |
| `--full` | Full merge |
| `--reset-state` | Delete state before running |
| `--dry-run` | Show changes only |

**Behavior:**

| Scenario | Result |
|---|---|
| First run | `full` mode (whole project) |
| No changes | `No changes since last run.` |
| File changed | Only that file |
| File deleted | Reported in header |
| `.codemergeignore` changed | Automatically switches to `full` |

### `search` — Symbol search

```bash
python codemerge.py search PATTERN [OPTIONS]
```

| Option | Description |
|---|---|
| `PATTERN` | regex or plain text |
| `--max-hits N` | Maximum results (default: 500) |

**Example:**

```bash
python codemerge.py search "handleLogin"
python codemerge.py search "function handle.*Login" -l typescript
python codemerge.py search UserRepository --output hits.txt
```

### `langs` — List languages

```bash
python codemerge.py langs
```

---

## Common Options

All of these work in `manifest`, `fetch`, `diff`, and `search`:

| Option | Description |
|---|---|
| `-l`, `--lang LANG [LANG ...]` | Select language(s) |
| `-o`, `--output FILE` | Output file name |
| `-r`, `--root DIR` | Project root |
| `--max-size MB` | Maximum file size (default: 100) |
| `--no-git` | Ignore Git |
| `--include PATTERN [...]` | Glob patterns for force-include |
| `--exclude PATTERN [...]` | Glob patterns for exclusion |
| `--allow-sensitive` | Include sensitive files |
| `--all-files` | Ignore language filter |
| `--no-header` | No header in output |
| `-q`, `--quiet` | Suppress summary |
| `--ignore-file PATH` | Custom ignore file |
| `--no-ignore-file` | Ignore ignore files |

---

## Ignore File

The `.codemergeignore` file at the project root uses gitignore syntax:

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

**Supported syntax:**

| Pattern | Meaning |
|---|---|
| `docs/` | Folder at any depth |
| `/config.json` | Root only |
| `*.min.js` | glob |
| `**/snapshots/` | Folder at any depth |
| `!docs/README.md` | Exception |
| `# comment` | Comment |

---

## Sensitive Files

These files **never** appear in the output (unless `--allow-sensitive` is used):

- `.env` and its variants (except `.env.example`, `.env.sample`, `.env.template`, `.env.dist`)
- `id_rsa`, `id_dsa`, `id_ecdsa`, `id_ed25519`
- `credentials.json`, `secrets.json`, `service-account.json`
- `*.pem`, `*.key`, `*.p12`, `*.pfx`, `*.jks`, `*.keystore`, `*.ppk`, `*.secret`, `*.crt`
- `.netrc`, `.pypirc`, `.htpasswd`, `.pgpass`

---

## Prompt Structure

```
prompts/
├── 01-system.md                    ← base rules (Persian)
├── 01-system-append-2.md           ← editing rules (English)
├── 02-manifest.md                  ← used with manifest
├── 03-bug-fix.md                   ← task: bug fix
├── 04-feature.md                   ← task: add feature
├── 05-refactor.md                  ← task: refactor
├── 06-code-review.md               ← task: code review
├── 07-tests.md                     ← task: write tests
├── 08-explain-code.md              ← task: explain code
├── 09-continue-session.md          ← continue session
├── 10-recovery.md                  ← recovery when AI goes off track
├── 11-limit-files.md               ← limit request scope
├── 12-long-response.md             ← manage long responses
├── 13-final-summary.md             ← final summary
├── 14-checklist.md                 ← checklist
├── Anti-AI-Slop/
│   └── 00-master-anti-slop.md      ← general anti-slop rules
├── Expertise and Experience/       ← expertise files (English)
│   ├── 00-anti-slop-core.md
│   ├── 01-frontend-architecture.md
│   ├── 02-typescript.md
│   ├── ...
│   └── 12-accessibility.md
└── Expertise and Experience-FA/    ← expertise files (Persian)
    └── (mirror of English versions)
```

Every prompt file starts with **YAML frontmatter**:

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

---

## Auxiliary Tools

The `tools/` folder contains these scripts:

| Tool | Description |
|---|---|
| `snapshot.py` | Full project snapshot before major edits |
| `apply_ai_output.py` | Apply AI output (`file:` blocks) to disk |
| `verify.ps1` / `verify.sh` | Run type-check, lint, tests, build |
| `new_session.py` | Create a new session file |
| `session_summary.py` | Print recent session summaries |
| `estimate.py` | Estimate tokens and cost |
| `watch.py` | Auto-run `diff` on file changes |
| `log_metrics.py` | Log AI workflow metrics |
| `setup_profile.ps1` | Install PowerShell shortcuts |
| `add_frontmatter.py` | Add YAML frontmatter to prompts |
| `fix_frontmatter_lang.py` | Fix `lang` in frontmatter |
| `diagnose_cheatsheet.py` | Detect missing files in bundle |

### Usage Examples

```powershell
# Snapshot
python tools\snapshot.py --label before-ai
python tools\snapshot.py --list
python tools\snapshot.py --restore before-ai

# Apply AI output
python tools\apply_ai_output.py ai_response.md --dry-run
python tools\apply_ai_output.py ai_response.md

# Verify
.\tools\verify.ps1
.\tools\verify.ps1 -SkipTests
.\tools\verify.ps1 -Only "type-check","lint"

# Session
python tools\new_session.py "auth refactor" --prev 02
python tools\session_summary.py --last 3

# Cost estimate
python tools\estimate.py .ai\bundle.txt --model deepseek-chat
```

---

## Testing

The project has unit tests:

```bash
# Run tests
python -m unittest discover -s tests -v

# Or directly
python tests/test_codemerge.py

# Or with pytest (recommended)
pip install pytest
pytest tests/ -v
```

Test coverage includes:

- `is_sensitive` — detecting sensitive files
- `IgnoreMatcher` — gitignore patterns
- `extract_python` — extracting Python symbols (AST)
- `_extract_js` — extracting JS/TS symbols (including 3-level generics, arrow functions with object return)
- `write_bundle` — writing bundle with/without header
- `compute_delta` — computing diff changes
- `detect_lang` — detecting language from extension

---

## Troubleshooting

### `No source files found`

- The selected language is wrong → `python codemerge.py langs`
- All files are in `.codemergeignore` → try `--no-ignore-file`
- Try `--all-files`

### `Unknown language: xxx`

Check the language name with `python codemerge.py langs`.

### File exists in manifest but is rejected by fetch

- It is probably binary
- Or its size exceeds `--max-size`
- Or you gave the path relative to root incorrectly

### `diff` is always full

- State was not saved → check the write path
- `--root` changed between runs

### Output is too large

```bash
# Smaller manifest
python codemerge.py manifest --no-symbols --no-imports -o .ai/files.txt

# With token limit
python codemerge.py manifest --max-tokens 8000 -o .ai/manifest.txt

# One language only
python codemerge.py diff --full -l typescript -o .ai/ts.txt
```

### Token count is inaccurate

```bash
pip install tiktoken
```

### `grep` does not work in PowerShell

Use `Select-String` instead:

```powershell
Select-String -Path .ai\manifest.txt -Pattern "apiGet"
(Select-String -Path .ai\manifest.txt -Pattern "^  function ").Count
```

### Persian text is garbled in PowerShell

PowerShell 5.1 does not read UTF-8 by default. Use `-Encoding UTF8`:

```powershell
Get-Content prompts\01-system.md -Encoding UTF8
```

Or install PowerShell 7+.

---

## Project Structure

```
CodeCompactForAI/
├── codemerge.py                    ← main tool
├── README.md                       ← this file (English)
├── README.fa.md                    ← Persian version
├── md-list.txt                     ← list of important files
├── .codemergeignore                ← ignore rules
│
├── docs/
│   ├── CHEATSHEET.md
│   └── codemerge.md                ← full Persian guide
│
├── prompts/                        ← AI prompts
│   ├── 01-system.md
│   ├── 01-system-append-2.md
│   ├── 02-manifest.md
│   ├── 03..08-*.md
│   ├── 09..14-*.md
│   ├── Anti-AI-Slop/
│   ├── Expertise and Experience/
│   └── Expertise and Experience-FA/
│
├── tools/                          ← auxiliary tools
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

---

## License

MIT

## Compatibility

- Python 3.9+
- Windows, macOS, Linux
- Bash, PowerShell, cmd
