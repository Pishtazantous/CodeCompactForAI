---
id: 09-continue-session
title: "Continue Session"
lang: en
depends_on: []
category: task
version: 2
---

# Continue Session

## Previous Session Summary
[paste the summary the AI gave at the end of the previous session]



## Changes Since Then

[Short description: what you did manually, if anything]

## Output of `codemerge diff`
[paste the content of changes.txt, produced by
python codemerge.py diff -o changes.txt]



## Current Task

[The new task]

## Instructions

1. First, analyze the changes and state whether they match the
   description. If anything looks unexpected, say so.
2. Then proceed with the current task.
3. If more files are needed, request them with `codemerge-fetch`.
4. Do not assume the project state from the previous session's memory.
   The diff and the manifest are the source of truth.