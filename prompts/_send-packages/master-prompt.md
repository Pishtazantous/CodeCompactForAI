---
id: master-prompt
title: "Master Prompt for Generating Domain Files"
lang: en
category: helper
version: 1
---

# Master Prompt for Generating Domain Files

Copy this prompt into a new AI conversation. Fill in every `<<FILL IN>>`
marker. Attach the reference files listed in the category-specific
guide before sending.

---

## PROMPT STARTS HERE

# Task: Generate a Single Anti-Slop Prompt File

## Your Role

You are generating ONE markdown file for a layered anti-slop prompt
system used by AI coding assistants. This system constrains AI behavior
during coding sessions. You are NOT writing application code. You are
writing a rule file.

## Context of the System

The system has four layers:

- Layer 1 (Universal): language/framework-agnostic rules, always sent.
- Layer 2 (Domain): specialized rules in four sub-categories:
  - delivery: what you build (backend, frontend, mobile, CLI, ...)
  - language: what language (TypeScript, Python, Go, ...)
  - framework: what framework (React, Vue, Express, ...)
  - concern: what specialized constraint (security, performance, ...)
- Layer 3 (Project): repository-specific rules.
- Layer 4 (UI): visual design rules.

Golden rule: each rule appears in EXACTLY ONE layer. If a rule belongs
in Layer 1, it is not repeated in Layer 2. If it belongs in Layer 2, it
is not repeated in Layer 3.

## Files Attached to This Conversation

Read all attached files before generating. They are:

1. `00-master-anti-slop.md` -- the universal layer. Do NOT repeat any
   rule from this file.
2. `<<FILL IN: name of sibling file 1>>` -- a sibling domain file.
   Do NOT repeat its rules.
3. `<<FILL IN: name of sibling file 2>>` -- a sibling domain file
   for style reference.
4. `<<FILL IN: additional file if needed>>` -- optional.

If any attached file is missing or unreadable, stop and ask. Do not
proceed with a guess.

## File to Generate

- Path: <<FILL IN: e.g. prompts/domains/framework/02-svelte-anti-slop.md>>
- id: <<FILL IN: e.g. 02-svelte-anti-slop>>
- title: <<FILL IN: e.g. Svelte Anti-Slop Layer>>
- domain_type: <<FILL IN: delivery | language | framework | concern>>
- depends_on: <<FILL IN: e.g. [00-master-anti-slop, 02-architecture-anti-slop, 02-frontend-anti-slop]>>
- Coverage (2-3 lines): <<FILL IN: what this file covers>>
- NOT covered (2-3 lines): <<FILL IN: what belongs in other files,
  with file names>>

## Mandatory Rules

### Language and Style

- The entire file is in ENGLISH.
- No emoji. Use `BAD:` and `GOOD:` for code examples.
- Technical, direct tone. No marketing language ("blazing fast",
  "robust", "seamless", "cutting-edge" are forbidden).
- Every rule must be operational: a visible behavior, a specific
  pattern, or an explicit prohibition. No philosophical rules.
- If a rule's rationale is not obvious, add one line explaining it.

### Structure (Mandatory)

The file MUST have this structure, in this order:

1. YAML frontmatter with exactly these fields:
   - id
   - title (quoted)
   - lang: en
   - depends_on: [...]
   - category: domain
   - domain_type: <<FILL IN>>
   - version: 1

2. Title as H1: `# <<TITLE>> Anti-Slop Layer`

3. Opening paragraph (3-5 lines) stating:
   - Which layers this file sits under
   - That universal rules are NOT repeated here
   - What the file covers
   - What it does NOT cover, with references to sibling files

4. Section `## 1. Stack Assumptions` (10-20 lines):
   - Versions of the language/framework/tooling
   - Supported platforms
   - What this file assumes the reader already knows

5. Sections `## 2.` through `## N.` -- Core Topics
   - At least 10 sections total
   - Each section covers one topic
   - Each section has 2-5 rules or 2-5 sub-points
   - At least 50% of sections include a BAD/GOOD pair

6. Section `## N+1. <Name> Anti-Patterns`:
   - Minimum 20 items
   - Each item is numbered (N.1, N.2, ...)
   - Each item has a short description (1-2 lines)
   - At least 10 items include a BAD/GOOD code pair

7. Final section `## N+2. Response to Violation`:
   - Use EXACTLY this text:

```
If a previous response violated a rule here:

```
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

No justification. No apology paragraph. Fix and move on.
```

### Length

- Minimum: 400 lines
- Maximum: 600 lines
- Target: 480-540 lines

If the file would exceed 480 lines, the topic is too broad. Report
this to the user instead of generating an oversized file.

### Code Examples

- At least 50% of the rules must include a BAD/GOOD code pair.
- Code blocks must have a language tag (`typescript`, `python`, `go`,
  `yaml`, `sql`, `svelte`, `vue`, etc.).
- Use realistic names (user, order, fetchUser, createOrder). Never
  `foo`, `bar`, or `baz`.
- Keep examples minimal (5-15 lines each).

### Non-Duplication Rules

- Do NOT repeat any rule from `00-master-anti-slop.md`. That file
  covers: fabrication, fake completion, over-engineering, silent
  assumptions, concern mixing, security sloppiness (generic),
  dependency addition, output format, communication, language, and
  self-audit.
- Do NOT repeat rules from the sibling files attached. If you need to
  reference a sibling's rule, write:
  "Covered in `<file>`: `<one-line summary>`."
  Do not restate the rule.
- If a rule seems to belong to two layers, decide the single layer it
  fits best and put it only there.

### Output Format

Provide the file in this exact format:

````
```file:<<FULL PATH>>
<complete file content>
```
````

One block. No commentary before or after. No truncation. No
placeholders (`...`, `TODO`, `rest of file`, `<!-- more -->`).

### Response to Violation (Fixed Template)

Use exactly this section at the end of the file:

## <N>. Response to Violation

If a previous response violated a rule here:

```
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

No justification. No apology paragraph. Fix and move on.

## Self-Audit Before Sending

Before sending the file, verify every item below. If any box is
unchecked, fix it before sending.

Frontmatter:
- [ ] id is correct
- [ ] title is quoted
- [ ] lang: en
- [ ] depends_on is complete
- [ ] category: domain
- [ ] domain_type is correct
- [ ] version: 1

Structure:
- [ ] Opening paragraph is 3-5 lines
- [ ] Stack Assumptions section exists
- [ ] At least 12 sections total
- [ ] Anti-Patterns section has 20+ items
- [ ] Response to Violation section is exactly as specified

Quality:
- [ ] Length is between 220 and 400 lines
- [ ] At least 50% of rules have BAD/GOOD examples
- [ ] All code blocks have a language tag
- [ ] No emoji anywhere
- [ ] Entire file is English
- [ ] No philosophical rules without operational behavior

Non-duplication:
- [ ] No rule from Universal is repeated
- [ ] No rule from a sibling file is repeated
- [ ] References to other files have one-line summaries
- [ ] No reference to files not attached

Output:
- [ ] File is complete, no truncation
- [ ] Output is wrapped in exactly one `file:` block
- [ ] No commentary outside the `file:` block

## Start

Generate the file now. Do not ask clarifying questions. Make
reasonable assumptions and proceed. If a critical piece of information
is missing, state it in a one-line note before the `file:` block, then
proceed with the most reasonable assumption.

## PROMPT ENDS HERE
```
