---
id: 03-bug-fix
title: "Task: Bug Fix"
lang: en
depends_on: []
category: task
version: 2
---

# Task: Bug Fix

## Bug Description

[Describe the bug: what happens, what was expected]

## Error Message (if any)
[Full error text and stack trace]


## Reproduction Steps

1. ...
2. ...
3. ...

## Instructions for the AI

1. Based on the manifest, identify the files where the bug likely
   lives. State your hypothesis before fetching.
2. Fetch only those files with `codemerge-fetch` (maximum 3 files).
3. Once received, analyze the root cause, not just the symptom. A
   patch that hides the symptom is not a fix.
4. Provide the solution as complete files, not diffs.
5. If another file is needed, request it in the same response.

## Before Editing

Before providing any edit, declare at the top of your response:

> Rollback point: run `python tools/snapshot.py --label before-bugfix`
> before applying these changes.

If the project has no snapshot tool, list the files that will be
changed and instruct the user to back them up manually.

## Assumptions

If the bug description is ambiguous, list your assumptions under an
"Assumptions" heading before writing code. Do not guess silently.

## Out of Scope

Do not fix unrelated issues you notice while investigating. Report
them at the end as observations, and wait for instruction.