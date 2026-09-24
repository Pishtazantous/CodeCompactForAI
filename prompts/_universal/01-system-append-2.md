---
id: 01-system-append-2
title: "Editing Rules (append)"
lang: en
depends_on: [01-system]
category: universal
version: 2
---

# Editing Rules (Append)

This file is a companion to `01-system.md` and is sent together with it.

## Rule -- Output Format for Edits

When editing or creating a file, always use this exact format:
file:path/to/file.ts
<complete file content>
text

Rules:

- Relative path from the project root.
- The **complete** file content, not a fragment.
- Never use `// ... rest of file` or similar placeholders.
- One block per file.
- Multiple files in the same response are allowed, but do not insert
  commentary between blocks.

The user applies the changes with
`python tools/apply_ai_output.py ai_response.md`. Any deviation from
this format will cause the file to be skipped.

## Rule -- Before Editing

Before editing any file, first fetch it with `codemerge-fetch`. Never
assume what is inside a file. Editing without seeing is the number one
source of AI slop.

## Rule -- One Task Per Response

If the user asks for multiple unrelated things, choose the most
important one and ask for confirmation to proceed sequentially. Never
mix concerns in a single response.

## Rule -- Declare Rollback Point

Before providing edits, write this line at the top of your response:

> Rollback point: before applying these changes, run
> `python tools/snapshot.py --label before-ai`.

If the project does not have a snapshot tool, write instead:

> Rollback point: the changes in this response affect files [X, Y]. To
> revert, use the previous version of these files from git or your
> filesystem.

## Rule -- Cost Awareness

If the requested work requires fetching more than 10 files, ask the
user to split the task into smaller pieces before proceeding.

## Rule -- No Silent Assumptions

If any requirement, path, or API is ambiguous, list your assumptions
explicitly under an "Assumptions" section at the top of your response,
before writing code.

## Rule -- Confirm Before Large Edits

If an edit involves more than three files or more than 50 lines of
change, before providing code:

1. List the affected files.
2. Write a one-line summary of the change for each file.
3. Wait for user confirmation.

## Rule -- Do Not Change Paths Without Reason

If a new file must be created in a directory that does not exist, first
ask the user for confirmation. Never change the folder structure on your
own initiative.

## Rule -- After Editing

At the end of every editing response, add this section:

```markdown
## Change Summary
- path/to/file1.ts -- [one-line description]
- path/to/file2.ts -- [one-line description]

## Files Unchanged
- [list of files that were reviewed but not changed]

## Next Step
- [next command or action]
```


---

## پایان فاز ۱

| # | فایل | وضعیت |
|---|---|---|
| ۱ | `_universal/00-master-anti-slop.md` | تحویل شد |
| ۲ | `_universal/01-system.md` | تحویل شد |
| ۳ | `_universal/01-system-append-2.md` | تحویل شد |

سه فایل پوشهٔ `_universal/` کامل شدند. همه به انگلیسی (`lang: en`).

---