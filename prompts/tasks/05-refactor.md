---
id: 05-refactor
title: "Task: Refactor"
lang: en
depends_on: []
category: task
version: 2
---

# Task: Refactor

## Refactor Goal

[e.g., separate database access from the controller]

## Scope

- Folders: [e.g., auth/, models/]
- Prohibited changes: [e.g., public API must not change]

## Success Criteria

- [ ] All existing tests pass
- [ ] External behavior does not change
- [ ] Duplicated code is removed or consolidated
- [ ] No new abstraction is introduced without the Rule of Three

## Instructions for the AI

1. Fetch the files in scope with `codemerge-fetch` (maximum 5 files
   per round).
2. Extract the dependency map: which file imports which, and where
   the coupling points are.
3. Summarize the refactor plan in five lines. Wait for confirmation
   before writing code.
4. Once approved, provide each changed file as a complete file.
5. At the end, list the changed imports and the new file paths.

## Before Editing

Declare at the top of your response:

> Rollback point: run `python tools/snapshot.py --label before-refactor`
> before applying these changes.

## Behavior Preservation

Refactoring changes structure, not behavior. If any behavior must
change to complete the refactor, stop and report. That is a separate
task.

## Test Requirement

If the code being refactored has no tests, report this before starting.
Characterization tests should be written first.