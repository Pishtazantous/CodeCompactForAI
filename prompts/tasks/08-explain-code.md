---
id: 08-explain-code
title: "Task: Explain Code"
lang: en
depends_on: []
category: task
version: 2
---

# Task: Explain Code

## Goal

[e.g., understand how the authentication system works]

## Instructions for the AI

1. From the manifest, select the relevant files.
2. Fetch their content with `codemerge-fetch`.
3. Explain:
   - The overall flow from input to output
   - The role of each file and function
   - The interaction with external systems (DB, API, cache)
   - Weak points, bottlenecks, or design concerns
4. Use an ASCII diagram when it clarifies the explanation.
5. If the code is confusing, say so. Do not invent an intent the
   code does not express.

## Output Format

Explanation in prose, with code excerpts only when necessary to
illustrate a point. No file edits.