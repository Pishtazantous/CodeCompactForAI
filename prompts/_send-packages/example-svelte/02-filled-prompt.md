---
id: example-svelte-filled-prompt
title: "Example: Filled Master Prompt for Svelte"
lang: en
category: helper
version: 1
---

# Example: Filled Master Prompt for Svelte

This is the filled-in master prompt for generating
`02-svelte-anti-slop.md`. Use it as a template for other files.

---

## PROMPT STARTS HERE

# Task: Generate a Single Anti-Slop Prompt File

## Your Role

You are generating ONE markdown file for a layered anti-slop prompt
system used by AI coding assistants. This system constrains AI
behavior during coding sessions. You are NOT writing application code.
You are writing a rule file.

## Context of the System

The system has four layers:

- Layer 1 (Universal): language/framework-agnostic rules, always sent.
- Layer 2 (Domain): specialized rules in four sub-categories:
  - delivery: what you build
  - language: what language
  - framework: what framework
  - concern: what specialized constraint
- Layer 3 (Project): repository-specific rules.
- Layer 4 (UI): visual design rules.

Golden rule: each rule appears in EXACTLY ONE layer. If a rule belongs
in Layer 1, it is not repeated in Layer 2. If it belongs in Layer 2, it
is not repeated in Layer 3.

## Files Attached to This Conversation

Read all attached files before generating. They are:

1. `00-master-anti-slop.md` -- the universal layer. Do NOT repeat any
   rule from this file.
2. `02-architecture-anti-slop.md` -- framework-agnostic architecture
   rules. Do NOT repeat its rules.
3. `02-vue-anti-slop.md` -- a sibling framework file. Do NOT repeat
   its rules.
4. `02-react-anti-slop.md` -- another sibling framework file. Do NOT
   repeat its rules.
5. `02-frontend-anti-slop.md` -- the frontend delivery file. Do NOT
   repeat its rules.

If any attached file is missing or unreadable, stop and ask.

## File to Generate

- Path: prompts/domains/framework/02-svelte-anti-slop.md
- id: 02-svelte-anti-slop
- title: Svelte Anti-Slop Layer
- domain_type: framework
- depends_on: [00-master-anti-slop, 02-architecture-anti-slop,
              02-frontend-anti-slop]
- Coverage: Rules specific to Svelte 5: runes reactivity, component
  discipline, stores, actions, transitions, and SvelteKit integration
  basics.
- NOT covered: General frontend delivery rules, general architecture
  rules, TypeScript language rules, SvelteKit-specific routing and
  server routes (belongs to a future 02-sveltekit-anti-slop.md), UI
  design system rules.

## Mandatory Rules

### Language and Style

- The entire file is in ENGLISH.
- No emoji. Use `BAD:` and `GOOD:` for code examples.
- Technical, direct tone. No marketing language.
- Every rule must be operational.
- If a rule's rationale is not obvious, add one line explaining it.

### Structure (Mandatory)

[Same structure as master-prompt.md]

### Length

- Minimum: 220 lines
- Maximum: 400 lines
- Target: 280-320 lines

### Code Examples

- At least 50% of the rules must include a BAD/GOOD code pair.
- Code blocks use `svelte` or `typescript` as the language tag.
- Use realistic names (user, order, count).
- Keep examples minimal (5-15 lines each).

### Non-Duplication Rules

- Do NOT repeat any rule from `00-master-anti-slop.md`.
- Do NOT repeat any rule from `02-architecture-anti-slop.md`,
  `02-vue-anti-slop.md`, `02-react-anti-slop.md`, or
  `02-frontend-anti-slop.md`.
- If you need to reference a sibling's rule, write:
  "Covered in `<file>`: `<one-line summary>`."

### Output Format

````
```file:prompts/domains/framework/02-svelte-anti-slop.md
<complete file content>
```
````

One block. No commentary. No truncation. No placeholders.

### Response to Violation (Fixed Template)

[Same as master-prompt.md]

## Self-Audit Before Sending

[Same as master-prompt.md]

## Start

Generate the file now.

## PROMPT ENDS HERE
