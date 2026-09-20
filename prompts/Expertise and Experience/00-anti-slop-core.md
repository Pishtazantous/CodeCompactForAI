---
id: 00-anti-slop-core
title: "Core Anti-Slop Layer"
lang: en
depends_on: []
category: expertise
version: 1
---

# Core Anti-Slop Layer (Project-Specific)

Always send this file alongside any expertise prompt. Rules here apply to
**all** domains.

## General Project Rules

### 1. Reference Existing Code First
Before writing anything new, fetch 2–3 similar examples from the project using
`codemerge-fetch`. If a pattern exists, **follow it exactly**, even if you know
a "better" pattern elsewhere.

### 2. Minimal Change Principle
Each task must change **only what was requested**. If you spot unrelated issues,
**report them** but **do not change them** without permission.

### 3. No Premature Abstraction
Rule of three: any helper must be usable **at least 3 times** in the current
codebase to justify its existence. Abstraction for "possible future needs" is slop.

### 4. No TODO / FIXME / HACK
If something needs improvement:
- Do it now, or
- Explicitly state why you didn't.

No `// TODO` allowed in final code.

### 5. Comments in Project Language
If the project uses Persian comments, use Persian. If English, use English.
JSDoc is always English.

### 6. Full File, Not Fragments
When changing a file, provide the **complete file content**. Fragments are
dangerous for merges.

### 7. Admit When You Don't Know
If you're unsure whether an API exists, **ask** or **search**. Inventing APIs is
the cardinal sin of AI.

### 8. State the Change Scope Explicitly
At the start of every response, write:
- Which files you will change
- What you will **not** change

### 9. Mention Required Setup
If new code needs package installs, env vars, or migrations, state them clearly
under "Next steps".

### 10. Don't Write Tests Unless Asked
If the task isn't "write tests", don't write tests. If you think tests are
needed, **suggest** but don't add them yourself.

## Response to Violation

If a previous response violated these rules:

```
"In the previous response, [rule] was violated. Correction:"
[corrected code]
```

No justification, no long apology. Fix it directly.
