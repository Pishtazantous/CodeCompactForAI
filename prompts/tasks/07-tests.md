---
id: 07-tests
title: "Task: Write Tests"
lang: en
depends_on: []
category: task
version: 2
---

# Task: Write Tests

## Scope

[e.g., functions in auth/login.py]

## Test Framework

[e.g., pytest, vitest, jest]

## Instructions for the AI

1. Fetch the target file and existing test files with
   `codemerge-fetch`.
2. Identify the project's test style (arrange-act-assert, given-when-
   then, table-driven, etc.). Match it exactly.
3. Write tests for:
   - The happy path
   - Error cases
   - Edge cases (empty input, boundary values, large input)
   - External dependencies mocked per the project's convention
4. Provide the complete test file.
5. If a refactor of the source is needed to make it testable, propose
   it but do not implement it in this task.

## Test Quality

- Each test has a descriptive name.
- Each test asserts something specific.
- Tests are independent of each other.
- No test relies on execution order.
- No test sleeps; use fake timers if needed.

## Output Format

Complete test files, not fragments. One `file:path` block per test
file.