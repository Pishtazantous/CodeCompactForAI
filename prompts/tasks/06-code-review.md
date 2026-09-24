---
id: 06-code-review
title: "Task: Code Review"
lang: en
depends_on: []
category: task
version: 2
---

# Task: Code Review

## Review Scope

[e.g., the payment module]

## Review Focus

- [ ] Logic bugs
- [ ] Security issues (injection, XSS, CSRF, auth bypass)
- [ ] Performance issues (re-render, memory leak, N+1 query)
- [ ] SOLID or DRY violations
- [ ] Duplicated code
- [ ] Missing tests
- [ ] Accessibility issues (if UI)

## Instructions for the AI

1. From the manifest, select the files relevant to the scope.
2. Fetch their content with `codemerge-fetch`.
3. For each issue found, report:
   - File path
   - Line number
   - One-line description
   - Suggested fix
4. Prioritize:
   - Critical: security, data loss, correctness
   - Important: performance, maintainability, test gaps
   - Minor: style, naming, cosmetic

## Output Format

Report findings as a list, ordered by priority. Do not rewrite code
unless asked. The task is review, not edit.

If a finding is uncertain, say so. False positives erode trust in
the review.