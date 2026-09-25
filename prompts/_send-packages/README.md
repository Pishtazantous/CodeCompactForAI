---
id: send-packages-readme
title: "Send Packages for Generating Domain Files"
lang: en
category: helper
version: 1
---

# Send Packages

This folder contains the tooling for generating new anti-slop domain
files using an external AI assistant.

Each "send package" tells you:

1. Which reference files to attach to the AI conversation.
2. Which prompt to send.
3. How to verify the output.

## Structure

- `master-prompt.md` -- the master prompt template. Fill in the
  `<<FILL IN>>` markers and send.
- `01-make-delivery-file.md` -- guide for generating a delivery file.
- `02-make-language-file.md` -- guide for generating a language file.
- `03-make-framework-file.md` -- guide for generating a framework file.
- `04-make-concern-file.md` -- guide for generating a concern file.
- `05-make-project-file.md` -- guide for generating a project file.
- `06-make-ui-file.md` -- guide for generating a UI file.
- `example-svelte/` -- a complete worked example.

## Workflow

1. Choose the category of the file you want to generate.
2. Open the corresponding guide.
3. Attach the reference files listed in the guide.
4. Fill in the master prompt with the file's metadata.
5. Send to the AI.
6. Verify the output against the checklist in the master prompt.
7. If accepted, save the file to its target path.

## Rules

- One file per AI conversation. Do not generate two files in one chat.
- Always attach `00-master-anti-slop.md`. Without it, the AI cannot
  avoid duplicating universal rules.
- Attach at least one sibling file. Without it, the AI cannot match
  style or avoid overlap.
- Verify the output before saving. See the checklist in the master
  prompt.

## When to Use

Use this workflow when:

- You need a domain file that does not yet exist.
- An existing domain file is too weak and needs a rewrite.
- You are adding a new language, framework, or concern to the system.

## When NOT to Use

Do not use this workflow for:

- Universal files (`00-master-anti-slop.md`, `01-system.md`).
  These are the source of truth and are not generated.
- Task files (`tasks/*.md`). These follow a fixed template.
- Project files (`projects/*/00-anti-slop-core.md`). These are
  templates with `<!-- FILL IN -->` sections.

## Quality Bar

Every generated file must pass the self-audit checklist at the end of
the master prompt. If it does not, regenerate. Do not save a file that
fails the checklist.
