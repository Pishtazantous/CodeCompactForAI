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