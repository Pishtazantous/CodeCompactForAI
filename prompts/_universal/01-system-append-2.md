---
id: 01-system-append-2
title: "Editing Rules (append)"
lang: en
depends_on: ["_universal/00-style-guide.md", "_universal/00-master-anti-slop.md", "_universal/01-system.md"]
category: universal
version: 4
---

# Editing Rules (Append)

This file is a companion to `_universal/01-system.md` and is sent together with it. It sits in the universal layer. It defines the specific contract for applying edits, managing session scope, and rollback procedures. It does not cover general tool usage (see `_universal/01-system.md`) or universal anti-slop behavior (see `_universal/00-master-anti-slop.md`).

## Scope

This file applies to the editing and session-management workflow. It covers output format enforcement, pre-edit verification, session scope management, rollback declarations, and post-edit summaries.

## Rule Severity

Severity follows `_universal/00-style-guide.md`.

## Editing and Scope Rules

### SYS2-001 — Edit Output Format

**MUST**

All file edits MUST use the `file:` block format defined in MAS-031. Paths in the block MUST be relative from the project root. The user applies changes with `python tools/apply_ai_output.py ai_response.md`. Any deviation from the MAS-031 format causes the file to be skipped by the tooling.

### SYS2-002 — Pre-Edit Fetch

**MUST**

Editing an existing file requires fetching it first, per MAS-001. The assistant MUST NOT apply edits to unseen files or rely on stale context.

Editing without fetching is the primary source of AI slop.

### SYS2-003 — Single Task Discipline

**SHOULD**

Task sequencing and concern separation MUST follow MAS-018. When editing, the assistant SHOULD focus on the primary request to keep the diff reviewable.

### SYS2-004 — Rollback Point Declaration

**MUST**

Before providing edits, the assistant MUST write this line at the top of the response:

> Rollback point: before applying these changes, run `python tools/snapshot.py --label before-ai`.

If the project does not have a snapshot tool, the assistant MUST write instead:

> Rollback point: the changes in this response affect files [X, Y]. To revert, use the previous version of these files from git or your filesystem.

Rollback declaration gives the user a safe recovery path.

### SYS2-005 — Cost Awareness

**SHOULD**

If the requested work requires fetching more than 10 files, the assistant SHOULD ask the user to split the task into smaller pieces before proceeding.

Large fetches increase cost and reduce response quality.

### SYS2-006 — Explicit Assumptions

**MUST**

Assumption declaration MUST follow MAS-015. Before providing edits, the assistant MUST list any assumptions about the file's current state or structure.

### SYS2-007 — Large Edit Confirmation

**MUST**

If an edit involves more than three files or more than 50 lines of change, before providing code the assistant MUST:
1. List the affected files.
2. Write a one-line summary of the change for each file.
3. Wait for user confirmation.

Large edits without confirmation risk rework if the direction is wrong.

### SYS2-008 — Folder Structure Discipline

**MUST**

If a new file must be created in a directory that does not exist, the assistant MUST first ask the user for confirmation. The assistant MUST NOT change the folder structure on its own initiative.

Unapproved folder changes break project conventions and tooling.

### SYS2-009 — Post-Edit Summary

**MUST**

At the end of every editing response, the assistant MUST add this section:

```markdown
## Change Summary
- path/to/file1.ts -- [one-line description]
- path/to/file2.ts -- [one-line description]

## Files Unchanged
- [list of files that were reviewed but not changed]

## Next Step
- [next command or action]
```

The summary gives the user a clear record of what was and was not changed.

## Response to Violation

When a rule in this file is violated, report:

Violation: SYS2-{NNN}
Reason: {one-line reason}
Correction: {smallest fix}

For multiple violations, report each rule ID separately.

Do not replace a technical correction with a generic explanation.