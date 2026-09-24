---
id: 10-recovery
title: "Recovery Prompt"
lang: en
depends_on: []
category: task
version: 2
---

# Recovery Prompt

Pause for a moment.

Recall that we work with the tool `codemerge.py` and you must:

1. Request file content only with this format:

```codemerge-fetch
path/to/file
‍‍‍‍‍‍```
Search the project only with this format:

codemerge-search
symbol
See recent changes only with this format:

codemerge-diff
Never ask for "the whole project".

Never assume the content of a file you have not seen.

Never guess the paths of files not in the manifest.

Every file edit is provided as a complete file, wrapped in a
file:path block.

A rollback point is declared at the top of every editing response.

Now, back to the main task:

[Restate the main task here]

---