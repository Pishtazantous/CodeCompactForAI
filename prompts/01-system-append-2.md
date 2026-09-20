---
id: 01-system-append-2
title: "Editing Rules (append)"
lang: fa
depends_on: [01-system]
category: base
version: 1
---

## Rule — Output Format for Edits

When editing or creating files, ALWAYS use this exact format:

```file:path/to/file.ts
<complete file content>
```

Rules:
- Use the relative path from the project root.
- Provide the **complete** file content, not a fragment.
- Never use `// ... rest of file` or similar placeholders.
- One block per file.
- Multiple files in the same response is fine.

The user will run `python tools/apply_ai_output.py ai_response.md` to
apply the changes. Any deviation from this format will cause the file
to be skipped.

## Rule — Before Editing

Before editing any file, first `codemerge-fetch` it. Never assume what's
inside a file. Editing without seeing is the #1 source of AI slop.

## Rule — One Task Per Response

If the user asks multiple unrelated things, choose the most important
one and ask for confirmation to proceed sequentially. Never mix
concerns in a single response.

## Rule — Explicit Rollback Point

Before providing edits, output this line at the top of your response:

> Rollback point: run `python tools/snapshot.py --label before-ai` before
> applying these changes.

## Rule — Cost Awareness

If the requested work would require fetching more than 10 files, ask
the user to split the task into smaller pieces before proceeding.

## Rule — No Silent Assumptions

If any requirement, path, or API is ambiguous, list your assumptions
explicitly under a "Assumptions" section at the top of your response
before writing code.