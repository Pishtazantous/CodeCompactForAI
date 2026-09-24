---
id: 04-feature
title: "Task: Add Feature"
lang: en
depends_on: []
category: task
version: 2
---

# Task: Add Feature

## Feature Description

[Detailed description of the new feature]

## Requirements

- [Requirement 1]
- [Requirement 2]
- [Requirement 3]

## Scope

- Affected folders (initial estimate): [...]
- Prohibited changes: [e.g., public API must not change]

## Instructions for the AI

1. First, use `codemerge-search` to find related symbols in the
   project. Report what you find before proceeding.
2. Based on the results, list the files that must be created or
   changed.
3. Fetch the content of existing files with `codemerge-fetch`
   (maximum 5 files per round).
4. Once received, write the new code following the project's existing
   style. Match naming, imports, and layout exactly.
5. If a new file is needed, provide its complete content.
6. If a new API surface is needed, define the types first, then the
   implementation.

## Before Editing

Declare at the top of your response:

> Rollback point: run `python tools/snapshot.py --label before-feature`
> before applying these changes.

## Assumptions

If the requirements are ambiguous, list assumptions explicitly before
writing code:
Assumptions:

...

...


## Out of Scope

Do not implement features that were not requested. If you notice a
natural extension, report it and wait.