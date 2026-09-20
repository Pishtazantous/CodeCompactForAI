# Complete Guide to `codemerge.py`

## Final version with full support for TypeScript, Object Literal, Generic Types, and `.codemergeignore`

---

## Table of Contents

1. [Introduction](#introduction)
2. [Installation and Prerequisites](#installation-and-prerequisites)
3. [AI Workflow](#ai-workflow)
4. [Commands](#commands)
5. [Common Options](#common-options)
6. [Language Support](#language-support)
7. [`.codemergeignore` File](#codemergeignore-file)
8. [Sensitive Files](#sensitive-files)
9. [Complete Examples](#complete-examples)
10. [Troubleshooting](#troubleshooting)
11. [Ready-to-Use Prompts for AI](#ready-to-use-prompts-for-ai)

---

## Introduction

`codemerge.py` is a command-line tool that prepares software projects for submission to AI models (DeepSeek, ChatGPT, Claude, etc.). Instead of sending the entire project, you first send a **compact map** of the project structure, then the AI decides which files it needs.

### Advantages
- **10 to 50 times less** data sent compared to sending the whole project
- **Accurate symbol extraction** for TypeScript/JavaScript (including generics, arrow functions, object literals)
- **Support for 40+ programming languages**
- **No external dependencies** (Python 3.8+ only)
- **Four separate commands**: manifest, fetch, diff, search
- **`.codemergeignore` support** for precise file control

---

## Installation and Prerequisites

### Prerequisites
- Python 3.8 or higher
- (Optional) Git
- (Optional) `pip install tiktoken` for accurate token counting

### Installation
Just place the `codemerge.py` file in the project root. No package installation needed.

```bash
# Verify installation
python codemerge.py --help
```

---

## AI Workflow

```
┌──────────────────────────────────────────────────────────────┐
│  Step 1: Create Manifest                                      │
│    python codemerge.py manifest -o manifest.txt               │
│                                                              │
│  Step 2: Send manifest.txt to AI                             │
│                                                              │
│  Step 3: AI responds: "send auth/login.py and lib/api.ts"   │
│                                                              │
│  Step 4: Create Bundle with requested files                   │
│    python codemerge.py fetch auth/login.py lib/api.ts \       │
│        -o bundle.txt                                          │
│                                                              │
│  Step 5: Send bundle.txt to AI                               │
│                                                              │
│  Step 6: In next session, only changes                       │
│    python codemerge.py diff -o bundle.txt                     │
└──────────────────────────────────────────────────────────────┘
```

---

## Commands

### 1. `manifest` — Build Project Map

```bash
python codemerge.py manifest [OPTIONS]
```

Output includes path, language, line count, size, sha, imports, and list of functions/classes.

**Specific Options:**

| Option | Description |
|---|---|
| `--format {text,md,json}` | Output format (default: `text`). |
| `--no-symbols` | Only file list without functions/classes. |
| `--no-imports` | Exclude imports from output. |
| `--max-tokens N` | Soft token cap. If exceeded, symbols are removed. |

**Examples:**

```bash
# Full manifest in text format
python codemerge.py manifest -o manifest.txt

# TypeScript/JavaScript only
python codemerge.py manifest -l typescript,javascript -o manifest_ts.txt

# Markdown format (suitable for sending to AI)
python codemerge.py manifest --format md -o manifest.md

# JSON format (suitable for automation tools)
python codemerge.py manifest --format json -o manifest.json

# Most compact
python codemerge.py manifest --no-symbols --no-imports -o files.txt

# With token limit
python codemerge.py manifest --max-tokens 8000 -o manifest.txt
```

**Sample `text` output:**

```
# Project Manifest
# Generated: 2026-09-19T23:08:22
# Root: /home/user/myproject
# Files: 208
# ------------------------------------------------------------

=== nextjs-banking/lib/api/auth.ts  [typescript 1222L 33.3K sha=7a2a7b2a] ===
  imports: axios, ./client
  function parseJwt<T = any>(token: string): T | null
  function getTokenExpiry(token: string): number | null
  function loginUser(email: string, password: string): Promise<LoginResponse>
  function registerUser(email: string, password: string, fullName: string, username: string, mobile: string): Promise<RegisterResponse>
  interface LoginResponse
  interface LoginRequest
  ...

=== nextjs-banking/lib/admin/auth.ts  [typescript 31L 1007B sha=26a31a5c] ===
  imports: ./api, @/types/admin
  object adminAuthApi
    . login(data: LoginRequest)
    . logout()
    . register(data: RegisterAdminRequest)
    . activate(adminId: string)
    . revokeAdminTokens(adminId: string)

=== nextjs-banking/app/admin/page.tsx  [typescript 431L 18.7K sha=b663eb9f] ===
  imports: react, next/link, @/lib/admin/reports, lucide-react, sonner, recharts
  function fmtNum(value: number)
  function StatCard({ label, value, icon, accent, href, trend, sub }: ...)
  function QuickActionCard({ title, description, href, icon, accent }: ...)
  function AdminDashboardPage()
    . fetchMonthly()
```

---

### 2. `fetch` — Fetch Requested Files

```bash
python codemerge.py fetch [FILES ...] [OPTIONS]
```

**Specific Options:**

| Option | Description |
|---|---|
| `FILES ...` | File paths (relative to project root). |
| `--files-from FILE` | Read list from file (one path per line, `#` for comments). |
| `--from-stdin` | Read list from standard input. |

**Examples:**

```bash
# Direct with arguments
python codemerge.py fetch auth/login.py lib/api/auth.ts -o bundle.txt

# From file list
python codemerge.py fetch --files-from requested.txt -o bundle.txt

# From STDIN
echo "auth/login.py
lib/api/auth.ts" | python codemerge.py fetch --from-stdin -o bundle.txt
```

**Sample `requested.txt`:**

```
# AI response:
auth/login.py
lib/api/auth.ts
lib/api/client.ts
store/authStore.ts
```

---

### 3. `diff` — Only Changes Since Last Run

```bash
python codemerge.py diff [OPTIONS]
```

The first run acts like `fetch` on the whole project and creates a state. Subsequent runs only report changed, added, and deleted files.

**Specific Options:**

| Option | Description |
|---|---|
| `--state-file PATH` | Custom state path. Default: `<output>.state.json`. |
| `--full` | Full merge (updates state). |
| `--reset-state` | Delete state before running. |
| `--dry-run` | Show changed files only. |

**Examples:**

```bash
# First run
python codemerge.py diff -o bundle.txt

# Subsequent run: only changes
python codemerge.py diff -o bundle.txt

# Force full
python codemerge.py diff --full -o bundle.txt

# Preview
python codemerge.py diff --dry-run
```

**Behavior in Scenarios:**

| Scenario | Result |
|---|---|
| First run (no state) | `full` mode — whole project. |
| No changes | Message `No changes since last run.` |
| `a.py` changed | Only `a.py` in output. |
| `b.py` deleted | Reported in header. |
| `c.py` added | Written in output. |
| `.codemergeignore` changed | Automatically switches to `full`. |

---

### 4. `search` — Search for a Symbol

```bash
python codemerge.py search PATTERN [OPTIONS]
```

**Specific Options:**

| Option | Description |
|---|---|
| `PATTERN` | Regex or plain text pattern. |
| `--max-hits N` | Maximum results (default: 500). |

**Examples:**

```bash
python codemerge.py search verify_password
python codemerge.py search "function handle.*Login" -l typescript
python codemerge.py search UserRepository --output hits.txt
```

---

### 5. `langs` — List Supported Languages

```bash
python codemerge.py langs
```

---

## Common Options

These options work in all commands (except `langs`):

| Option | Description |
|---|---|
| `-l`, `--lang LANG [LANG ...]` | Select language(s). Comma or space separated. |
| `-o`, `--output FILE` | Output file name. |
| `-r`, `--root DIR` | Project root. |
| `--max-size MB` | Maximum file size (default: 100). |
| `--no-git` | Ignore Git and scan directly. |
| `--include PATTERN [...]` | Glob patterns to force inclusion. |
| `--exclude PATTERN [...]` | Glob patterns for exclusion. |
| `--allow-sensitive` | Include sensitive files. |
| `--all-files` | Ignore language filter. |
| `--no-header` | No header in output. |
| `-q`, `--quiet` | Suppress final summary. |
| `--ignore-file PATH` | Custom ignore file. |
| `--no-ignore-file` | Ignore all ignore files. |

---

## Language Support

### Extraction Quality

| Language | Class | Function | Method | Imports | Quality |
|---|---|---|---|---|---|
| **Python** | ✅ AST | ✅ AST | ✅ AST | ✅ | Excellent |
| **TypeScript** | ✅ | ✅ | ✅ | ✅ | Excellent |
| **JavaScript** | ✅ | ✅ | ✅ | ✅ | Excellent |
| **Vue / Svelte** | ✅ | ✅ | ✅ | ✅ | Excellent |
| **Java** | ✅ | ✅ | ✅ | ✅ | Good |
| **C#** | ✅ | ✅ | ✅ | ✅ | Good |
| **C++ / C** | ✅ | ✅ | ✅ | ✅ | Good |
| **Go** | ✅ | ✅ | ✅ | ✅ | Excellent |
| **Rust** | ✅ | ✅ | ✅ | ✅ | Excellent |
| **Ruby** | ✅ | ✅ | ✅ | ✅ | Good |
| **PHP** | ✅ | ✅ | ✅ | ✅ | Good |
| **Kotlin** | ✅ | ✅ | ✅ | ✅ | Good |
| **Swift** | ✅ | ✅ | ✅ | ✅ | Good |
| **Dart** | ✅ | ✅ | ✅ | ✅ | Good |
| **Scala** | ✅ | ✅ | ✅ | ✅ | Good |

### TypeScript/JavaScript Features

- ✅ Arrow functions with multi-statement body
- ✅ Type parameters (`function foo<T>(...)`)
- ✅ Return types (simple and object literal)
- ✅ Multi-line signatures
- ✅ Balanced nested parens in params
- ✅ Object literals with methods
- ✅ Scope tracking (nested functions under parent)
- ✅ Interface/Enum/Type alias
- ✅ Auto-filter hooks (`useState`, `useEffect`, etc. don't create noise)

---

## `.codemergeignore` File

The ignore file lives at the project root and uses gitignore syntax.

### Recommended Example for Next.js Projects

```gitignore
# ============ .codemergeignore ============

# Blog content (read-only)
content/posts/
content/authors/
content/categories/

# Backup files
*.bak
*.tsbuildinfo

# codemerge outputs
manifest*.txt
project_source*.txt
codemerge.state.json
check.ps1

# Generated files
public/sitemap*.xml
public/robots.txt
public/images/

# Large and public files
public/telegram-web-app.js

# Server install scripts
scripts/install-*.sh

# Side config files
next-sitemap.config.js
postcss.config.js
```

### Supported Syntax

| Pattern | Description |
|---|---|
| `docs/` | Folder at any depth |
| `/config.json` | Root only |
| `*.min.js` | glob pattern |
| `**/snapshots/` | Folder at any depth |
| `!docs/README.md` | negation (exception) |
| `# comment` | Comment |

### Complex Examples

```gitignore
# Remove all tests
tests/
**/*.spec.ts
**/*.test.ts

# Exception
!tests/integration/api.spec.ts

# Personal files
*.local
TODO.private.md
```

---

## Sensitive Files

These files **never** appear in the output (unless `--allow-sensitive` is used):

- `.env` and its variants (except `.env.example`, `.env.sample`, `.env.template`, `.env.dist`)
- `id_rsa`, `id_dsa`, `id_ecdsa`, `id_ed25519`
- `credentials.json`, `secrets.json`, `service-account.json`
- `*.pem`, `*.key`, `*.p12`, `*.pfx`, `*.jks`, `*.keystore`, `*.ppk`, `*.secret`, `*.crt`
- `.netrc`, `.pypirc`, `.htpasswd`, `.pgpass`

---

## Complete Examples

### Scenario 1: Starting a New Project

```bash
# Step 1: Build manifest for AI
python codemerge.py manifest -l typescript,javascript -o manifest.txt

# Step 2: AI says send these files:
#   lib/api/auth.ts
#   lib/api/client.ts
#   store/authStore.ts

# Step 3: Create bundle
python codemerge.py fetch lib/api/auth.ts lib/api/client.ts store/authStore.ts -o bundle.txt

# Step 4: Send bundle.txt
```

### Scenario 2: Continuing in Next Session

```bash
# Only changes from last run
python codemerge.py diff -o changes.txt

# Send changes.txt which includes only changed files
```

### Scenario 3: Investigating a Specific Bug

```bash
# Search for function across project
python codemerge.py search "handleLogin"

# Result:
# lib/api/auth.ts:172: export const loginUser = async ...
# app/auth/login/page.tsx:45: const handleLogin = ...

# Send related files
python codemerge.py fetch lib/api/auth.ts app/auth/login/page.tsx -o bundle.txt
```

### Scenario 4: Multi-Language Project

```bash
# Backend only (Python)
python codemerge.py manifest -l python -o backend.txt

# Frontend only (TypeScript)
python codemerge.py manifest -l typescript -o frontend.txt
```

### Scenario 5: Recommended Folder Structure

```
.ai/
├── manifest.txt           # project map
├── bundle.txt             # files sent to AI
├── bundle.state.json      # diff state
└── sessions/
    ├── 01-auth-refactor.md
    └── 02-payment-fix.md
```

For this structure:

```bash
mkdir -p .ai
python codemerge.py manifest -o .ai/manifest.txt
python codemerge.py diff -o .ai/bundle.txt --state-file .ai/state.json
```

---

## Troubleshooting

### `No source files found`
- The selected language is wrong. Check with `python codemerge.py langs`.
- All files are in `.codemergeignore`.
- Try `--all-files`.

### `Unknown language: xxx`
Check the language name with `python codemerge.py langs`.

### File exists in manifest but is rejected by `fetch`
- It is probably binary.
- Or its size exceeds `--max-size`.
- Or you gave the path relative to root incorrectly.

### `diff` is always full
- State was not saved. Check the write path.
- Or `--root` changed between runs.

### Output is too large
```bash
# Smaller manifest
python codemerge.py manifest --no-symbols --no-imports -o manifest.txt

# With token limit
python codemerge.py manifest --max-tokens 8000 -o manifest.txt
```

### Token count is inaccurate
```bash
pip install tiktoken
```

### `grep` doesn't work in PowerShell
Use `Select-String` instead:
```powershell
Select-String -Path manifest.txt -Pattern "apiGet"
(Select-String -Path manifest.txt -Pattern "^  function ").Count
```

---

## Ready-to-Use Prompts for AI

### Prompt 1: Start Session

```
You are a senior software engineer working with the codemerge.py tool.

This tool has four commands:
- manifest: build compact project map
- fetch: fetch content of specific files
- diff: fetch only changed files
- search: search for a symbol in the project

Rules:
1. At first, you only have the manifest.
2. To fetch file content, use this format:

```codemerge-fetch
path/to/file1.ts
path/to/file2.ts
```

3. For search:

```codemerge-search
symbol_name
```

4. Never ask for the "whole project".

I am sending the manifest now. Until you receive it, confirm.
```

### Prompt 2: Send Manifest

```
The project manifest is below. Please:
1. Give a 5-10 line summary of the project structure.
2. Wait for my command.

--- start manifest ---
[content]
--- end manifest ---
```

### Prompt 3: Bug Fix

```
# Task: Bug Fix

## Bug Description
[problem description]

## Error Message
[error text]

## Instructions
1. Based on the manifest, guess where the bug is.
2. Request only those files using codemerge-fetch.
3. Analyze the root cause.
4. Provide the solution.
```

### Prompt 4: Continue Session

```
# Continue Session

## Previous Session Summary
[summary]

## Applied Changes
[description]

## codemerge diff output
[content of bundle.txt from diff]

## Current Task
[new task]
```

### Prompt 5: Recovery When AI Goes Off Track

```
Please pause for a moment.

Remember:
1. To fetch files, use codemerge-fetch.
2. To search, use codemerge-search.
3. For changes, use codemerge-diff.
4. Never ask for the "whole project".

Now back to the main task:
[task]
```

---

## Summary

| Feature | Status |
|---|---|
| Manifest with paths and functions | ✅ |
| Fetch file list | ✅ |
| Diff from last run | ✅ |
| Search | ✅ |
| Language selection | ✅ |
| TypeScript + 15 languages support | ✅ |
| Generic type parameters | ✅ |
| Object literals | ✅ |
| Scope tracking | ✅ |
| `.codemergeignore` | ✅ |
| Sensitive files | ✅ |
| No external dependencies | ✅ |

With this tool, the data sent to AI is typically **10 to 50 times less** than sending the whole project, while the AI has full visibility into the project structure.

---

**Version:** 1.0 Final  
**License:** MIT  
**Compatibility:** Python 3.8+
