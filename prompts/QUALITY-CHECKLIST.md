---
id: quality-checklist
title: "Quality Checklist for All Prompt Files"
lang: en
depends_on: ["_universal/00-style-guide.md"]
category: helper
version: 3
---

# Quality Checklist for All Prompt Files

This document is the acceptance and review reference for every file in the `prompts/` system. The Style Guide answers how prompt files are written. This checklist answers whether a file is acceptable. It does not redefine writing conventions. If this checklist and `_universal/00-style-guide.md` appear to conflict, stop review and reconcile the two documents.

## Scope

This checklist applies to all prompt files under `prompts/`. It defines review requirements, category checks, common failures, and verification steps. It does not define domain behavior, project conventions, task-specific content, or send-package generation workflow.

## Formal Quality Rules

### QC-001 — Checklist Authority

**MUST**

This checklist MUST evaluate files against `_universal/00-style-guide.md`. It MUST NOT introduce writing conventions, Rule ID semantics, severity semantics, or conflict rules that contradict the Style Guide. This keeps acceptance review consistent with the governing specification.

### QC-002 — Heuristic Signals

**MUST NOT**

Reviewers MUST NOT accept or reject a file solely because rule count, example count, anti-pattern count, section count, or line count falls outside a target range. Numeric signals exist to prompt a coverage review, not to force padding, trimming, or artificial rules.

### QC-003 — Architecture Verification

**MUST**

Reviewers MUST verify that behavioral rules use registered prefixes, monotonic Rule IDs, correct severity keywords, short noun-phrase titles, rationale where non-obvious, and one requirement per rule. This ensures traceability, reviewability, and testability.

### QC-004 — Protected Contract Precedence

**MUST NOT**

Reviewers MUST NOT accept a more specific file that weakens or contradicts a broader `MUST` or `MUST NOT` requirement protecting correctness, safety, security, or shared system contracts. Specificity may specialize, not override protected contracts.

### QC-005 — Violation Reporting Verification

**MUST**

Reviewers MUST verify that files defining behavioral rules end with `## Response to Violation` and use the standard format. Governance documents without behavioral Rule IDs MAY omit the section to avoid empty or artificial templates.

## How to Use This Checklist

1. Identify the category of the file being reviewed.
2. Apply the Universal Checklist (Part 1) to every file.
3. Apply the matching Category Checklist (Part 2).
4. Cross-reference the Common Failures (Part 3) for known pitfalls.
5. Use the Verification Process (Part 4) before merging.
6. If the file fails any required item, use the When a File Fails process (Part 5).

Items marked `REQUIRED` are mandatory acceptance checks. Items marked `SIGNAL` are heuristic review signals. When a signal is far outside its typical range, review coverage, duplication, and rationale before deciding.

The checklists in the send-package guides (`prompts/_send-packages/*.md`) are workflow subsets of this document for acceptance purposes. When a send-package guide and this checklist disagree about acceptance, this checklist wins. When this checklist and the Style Guide disagree, reconcile them before accepting files.

## Part 1 — Universal Checklist

Every file in `prompts/`, regardless of category, must satisfy the following required checks unless a check explicitly says it applies only to certain files.

### Frontmatter

- [ ] REQUIRED: Has YAML frontmatter delimited by `---`.
- [ ] REQUIRED: `id` is present, kebab-case, and is the stable file identifier. It SHOULD match the lowercased file name without extension. It is not a Rule ID.
- [ ] REQUIRED: `title` is present, in double quotes, human-readable.
- [ ] REQUIRED: `lang: en` (all prompt files are English).
- [ ] REQUIRED: `depends_on` is present as a list (empty `[]` if none).
- [ ] REQUIRED: `category` is one of: `universal`, `domain`, `ui`, `project`, `task`, `helper`.
- [ ] REQUIRED: `version` is a positive integer.

For domain files, additionally:

- [ ] REQUIRED: `domain_type` is one of: `delivery`, `language`, `framework`, `concern`.

For non-domain files:

- [ ] REQUIRED: `domain_type` is absent.

### Language and Style

- [ ] REQUIRED: Entire file is in English.
- [ ] REQUIRED: No emoji anywhere, including headings, examples, and code comments.
- [ ] REQUIRED: No marketing language ("blazing fast", "robust", "seamless", "cutting-edge", "state-of-the-art", "best-in-class").
- [ ] REQUIRED: No filler phrases ("it's important to note", "please keep in mind", "as we all know").
- [ ] REQUIRED: No apology language ("sorry", "unfortunately").
- [ ] REQUIRED: No vague or motivational prose.
- [ ] REQUIRED: Use concise technical language.
- [ ] REQUIRED: No emoji-as-bullet. Use `-`, `*`, or numbered lists.

### Structure

- [ ] REQUIRED: Has an H1 title matching the `title` field (or a close variant).
- [ ] REQUIRED: Uses `##` headings for top-level sections.
- [ ] REQUIRED: Uses `###` for subsections.
- [ ] REQUIRED: No skipped heading levels (`#` to `###` without `##`).
- [ ] REQUIRED: Opening paragraph explains architecture position, coverage, non-coverage, and related files where appropriate.
- [ ] REQUIRED: Standard sections are present when relevant to the file's purpose: `Scope`, `Rule Severity`, `Contracts`, rule sections, `Anti-Patterns`, `Response to Violation`, and `Retired Rules`.
- [ ] REQUIRED: No empty sections are created merely to satisfy a template.
- [ ] SIGNAL: Semantic headings are preferred over section numbering. Section numbering is not an acceptance gate.

### Rules

- [ ] REQUIRED: Every behavioral rule is operational: a visible behavior, a specific pattern, or an explicit prohibition.
- [ ] REQUIRED: Every behavioral rule has a Rule ID in the form `{PREFIX}-{NNN}`.
- [ ] REQUIRED: The prefix is registered in `_universal/00-style-guide.md`.
- [ ] REQUIRED: Rule IDs are unique and monotonically assigned within the prefix.
- [ ] REQUIRED: If a prefix is shared by multiple files, the numbering sequence remains unique across that prefix.
- [ ] REQUIRED: No fractional or hierarchical Rule IDs such as `BE-024.1`, `BE-024-A`, or `BE-024.1.2`.
- [ ] REQUIRED: Retired Rule IDs are not reused.
- [ ] REQUIRED: Rule titles are short noun phrases, normally 2–6 words, and are not commands.
- [ ] REQUIRED: The severity keyword is on its own line in bold immediately after the rule title.
- [ ] REQUIRED: One rule represents one requirement. Independent requirements are split.
- [ ] REQUIRED: No philosophical rules ("write clean code").
- [ ] REQUIRED: No vague rules ("be careful", "use common sense").
- [ ] REQUIRED: No rules that reference tools or frameworks not mentioned in the file.
- [ ] REQUIRED: Every rule with a non-obvious rationale includes a one-line explanation.
- [ ] REQUIRED: Severity matches consequence. `MUST` is not inflated for importance.
- [ ] REQUIRED: Mechanically testable `MUST` rules SHOULD have automated checks; non-mechanical `MUST` rules MUST have a review or verification method.

### Code Examples

- [ ] REQUIRED: Code blocks use a language tag (`typescript`, `python`, `go`, `yaml`, `sql`, `bash`, `text`, etc.).
- [ ] REQUIRED: Names in examples are realistic (`user`, `order`, `fetchUser`), not `foo`, `bar`, `baz`.
- [ ] REQUIRED: `BAD:` and `GOOD:` are used for paired examples.
- [ ] REQUIRED: No comments inside examples that restate the code.
- [ ] REQUIRED: Non-code policy, process, ownership, or architectural rules are not forced to include code examples.
- [ ] SIGNAL: Examples are usually 5–15 lines unless the context requires more.

### Non-Duplication

- [ ] REQUIRED: Every rule has one authoritative home.
- [ ] REQUIRED: No rule from `_universal/00-master-anti-slop.md` is repeated. Reference it instead.
- [ ] REQUIRED: No rule from another file in the same category is repeated.
- [ ] REQUIRED: References to rules use the form: `See {PREFIX}-{NNN} in {file}.`
- [ ] REQUIRED: References point to files that exist in the repository.

### Conflict and Hierarchy

- [ ] REQUIRED: A more specific file refines, clarifies, or strengthens a broader rule; it does not silently override it.
- [ ] REQUIRED: A specific file does not weaken or contradict a broader `MUST` or `MUST NOT` requirement protecting correctness, safety, security, or shared system contracts.
- [ ] REQUIRED: Stricter requirements are allowed when the specific scope legitimately requires them.
- [ ] REQUIRED: If equally specific rules conflict, the higher severity governs.
- [ ] REQUIRED: If an equally severe rule replaces another rule, the old rule is retired and referenced.
- [ ] REQUIRED: If a conflict remains unresolved, the higher-level contract remains authoritative until explicitly changed.

### Response to Violation

- [ ] REQUIRED for files that define behavioral rules: The file ends with `## Response to Violation`.
- [ ] REQUIRED: The heading is not numbered.
- [ ] REQUIRED: The section uses the fixed template:

```markdown
## Response to Violation

When a rule in this file is violated, report:

Violation: {PREFIX}-{NNN}
Reason: {one-line reason}
Correction: {smallest fix}

For multiple violations, report each rule ID separately.

Do not replace a technical correction with a generic explanation.
```

Governance documents without behavioral Rule IDs MAY omit this section.

### Completeness

- [ ] REQUIRED: File is complete, no truncation.
- [ ] REQUIRED: No `TODO`, `FIXME`, `...`, `<!-- more -->`, or `rest of file` markers.
- [ ] REQUIRED: No `<!-- FILL IN -->` markers (except in templates under `projects/` and `_send-packages/`).
- [ ] REQUIRED: All file references (`see X.md`) point to existing files.

## Part 2 — Category Checklists

The following checklists are additional. A file must pass the Universal Checklist AND its category checklist.

### 2.1 — Universal Layer Files (`_universal/`)

These files are the source of truth for universal behavior. They are not project-specific.

- [ ] REQUIRED: The file describes rules for all projects, not a specific one.
- [ ] REQUIRED: No language, framework, or tool is named as required except as clearly marked examples.
- [ ] REQUIRED: The file is stable: changes are rare and deliberate.
- [ ] REQUIRED: `00-master-anti-slop.md` remains authoritative for universal anti-slop behavior. Do not hardcode its internal structure in reviews.
- [ ] SIGNAL: Length is usually near 200–400 lines.

### 2.2 — Delivery Files (`domains/delivery/`)

- [ ] REQUIRED: Includes a contracts section, such as `## Contracts` or `## Delivery Contracts`.
- [ ] REQUIRED: The opening paragraph states what the file does NOT cover.
- [ ] REQUIRED: No framework-specific rule is present. Reference framework files.
- [ ] REQUIRED: No language-specific rule is present. Reference language files.
- [ ] REQUIRED: Anti-patterns are rules with IDs and severity.
- [ ] SIGNAL: Length is usually near 250–450 lines.
- [ ] SIGNAL: Rule, example, and anti-pattern counts are sufficient to cover the delivery domain without padding.

### 2.3 — Language Files (`domains/language/`)

- [ ] REQUIRED: Rules are language-specific. Framework-specific rules are referenced, not restated.
- [ ] REQUIRED: Includes Stack Assumptions. Version Applicability appears there when version differences affect rule applicability.
- [ ] REQUIRED: Every rule has a rationale.
- [ ] SIGNAL: Includes a traps-from-other-languages section when cross-language habits are a realistic risk.
- [ ] SIGNAL: Length is usually near 250–450 lines.
- [ ] SIGNAL: Rule and example counts are sufficient without artificial expansion.

### 2.4 — Framework Files (`domains/framework/`)

- [ ] REQUIRED: Includes a section describing the framework's lifecycle contracts.
- [ ] REQUIRED: Every rule is framework-specific. The "change the name" test passes.
- [ ] REQUIRED: Architecture rules are referenced when architectural constraints apply. Do not restate architecture rules.
- [ ] REQUIRED: No language-specific rule is present. Reference language files.
- [ ] REQUIRED: No delivery-specific rule is present. Reference delivery files.
- [ ] SIGNAL: Length is usually near 250–450 lines.
- [ ] SIGNAL: Rule and anti-pattern counts are sufficient without artificial expansion.

### 2.5 — Concern Files (`domains/concern/`)

- [ ] REQUIRED: Includes a `When This File Applies` section with objective criteria.
- [ ] REQUIRED: Includes concern budgets or measurable thresholds when the concern is measurable. If no threshold is possible, the file defines objective review criteria.
- [ ] REQUIRED: Every rule is concern-specific. The "does it apply without the concern?" test passes.
- [ ] REQUIRED: The opening paragraph states what the file does NOT cover.
- [ ] SIGNAL: Length is usually near 250–450 lines.
- [ ] SIGNAL: Rule and example counts are sufficient without artificial expansion.

### 2.6 — Project Files (`projects/<name>/`)

- [ ] REQUIRED: Includes a `Project Metadata` section.
- [ ] REQUIRED: Includes a `Tool Inventory` section with a concise shape per tool.
- [ ] REQUIRED: Every convention has a reference path to a real file.
- [ ] REQUIRED: Every anti-pattern has an evidence path.
- [ ] REQUIRED: Every constraint has a source.
- [ ] REQUIRED: No `<!-- FILL IN -->` markers remain, or they are replaced by `<!-- NOT YET FILLED: <reason> -->`.
- [ ] REQUIRED: No rule from a domain file is repeated.
- [ ] SIGNAL: Length is usually near 60–180 lines.

### 2.7 — UI File Set (`ui/`)

The `ui/` folder contains a set of files, not a single file. Two files make up the set:

- `04-ui-design-system.md` — universal visual rules (all projects with a UI).
- `05-ui-rtl-persian.md` — RTL and Persian-specific rules (only projects whose primary language is Persian, Arabic, Hebrew, or Urdu).

Both files are versioned together. A change to the design system that affects RTL rules requires a review of both.

#### 2.7a — `04-ui-design-system.md`

This is the base file for every project that has a UI.

- [ ] REQUIRED: Includes a design-system contracts section.
- [ ] REQUIRED: Includes a token discipline section.
- [ ] REQUIRED: Includes an RTL and bidirectional layouts section that either covers the topic briefly or explicitly refers to `05-ui-rtl-persian.md`.
- [ ] REQUIRED: No framework-specific rule is present.
- [ ] REQUIRED: No delivery-specific rule is present.
- [ ] REQUIRED: No concern-specific rule is present.
- [ ] REQUIRED: No Persian-specific rule is present beyond the brief RTL reference.
- [ ] SIGNAL: Length is usually near 250–450 lines.
- [ ] SIGNAL: Visual anti-pattern coverage is sufficient without padding.

#### 2.7b — `05-ui-rtl-persian.md` (for RTL projects)

This file is sent only for projects whose primary language is Persian, Arabic, Hebrew, or Urdu. It does not replace `04-ui-design-system.md`; both are sent together.

- [ ] REQUIRED: Includes an RTL contracts section.
- [ ] REQUIRED: Includes sections for Direction Setup, Logical Properties, Typography, Text Alignment, Icons, Numbers and Dates, Forms, Bidirectional Text, Layouts, and Testing.
- [ ] REQUIRED: Every rule is RTL- or Persian-specific. The "does it apply to an LTR English project?" test fails.
- [ ] REQUIRED: No rule from `04-ui-design-system.md` is repeated.
- [ ] REQUIRED: No framework-specific rule is present.
- [ ] REQUIRED: No delivery-specific rule is present.
- [ ] REQUIRED: No concern-specific rule is present.
- [ ] REQUIRED: The file states explicitly that it complements, not replaces, `04-ui-design-system.md`.
- [ ] SIGNAL: Length is usually near 350–700 lines.
- [ ] SIGNAL: Anti-pattern and example coverage is sufficient without padding.

#### 2.7c — The UI Set Rule

- [ ] REQUIRED: There is exactly one `04-ui-design-system.md` in the system.
- [ ] REQUIRED: There is at most one `05-ui-rtl-persian.md` in the system.
- [ ] REQUIRED: No other UI files exist unless a new category is added through Part 6.
- [ ] REQUIRED: If a project needs distinct branding, the branding goes in the project file, not in a new UI file.

### 2.8 — Task Files (`tasks/`)

- [ ] REQUIRED: Follows the fixed task template.
- [ ] REQUIRED: Has a `Description` section.
- [ ] REQUIRED: Has an `Instructions for the AI` section.
- [ ] REQUIRED: Has an `Output Format` section.
- [ ] REQUIRED: References the rollback point rule where edits are involved.
- [ ] REQUIRED: Does not contain task-specific content if it is a template.
- [ ] SIGNAL: Length is usually near 30–150 lines.

### 2.9 — Helper Files (`_send-packages/`, `QUALITY-CHECKLIST.md`)

- [ ] REQUIRED: Describes workflow or acceptance, not the content of generated files.
- [ ] REQUIRED: References the master prompt where applicable.
- [ ] REQUIRED: Lists required attachments when the helper describes a package.
- [ ] REQUIRED: Includes a self-audit or verification section when the helper directs generation or review.
- [ ] REQUIRED: No rule that belongs in a domain file is present.
- [ ] REQUIRED: Governance documents may define meta-rules or verification criteria. If they define behavioral rules, those rules follow the Style Guide.

## Part 3 — Common Failures

The following are frequent failures across all categories. Use this table during review.

| Failure | Symptom | Fix |
|---|---|---|
| Universal bleed | Repeats "no TODO", "declare assumptions", "no over-engineering" | Delete; reference `_universal/00-master-anti-slop.md` |
| Domain bleed | Includes rules from another domain category | Move to the correct file |
| Language bleed | Framework file mentions `any`, `Option`, `unwrap` | Move to language file |
| Framework bleed | Delivery file mentions React, Django, Express | Move to framework file |
| Delivery bleed | Framework file describes component discipline | Move to delivery file |
| Concern bleed | Delivery file repeats security or performance rules | Reference concern file |
| UI bleed | Frontend delivery file mentions gradients, tokens | Move to UI file |
| Persian bleed | Generic UI file mentions Jalali, ZWNJ | Move to `05-ui-rtl-persian.md` |
| Philosophy rule | "Write clean code", "be consistent" | Replace with an operational rule |
| Vague rule | "Use good judgment" | Replace with a specific behavior |
| Missing rationale | Rule says "do not" without "because" | Add one-line rationale |
| Placeholder left | `<!-- FILL IN -->`, `TODO`, `...` | Fill or remove |
| Emoji | `✅`, `❌`, `🚫`, `⚠️` | Replace with `GOOD:` / `BAD:` or plain text |
| Marketing tone | "blazing fast", "robust" | Remove |
| Missing language tag | Code block without ` ```typescript ` | Add the tag |
| Unrealistic names | `foo`, `bar`, `baz` | Rename to `user`, `order` |
| Missing Rule ID | Behavioral rule has no `{PREFIX}-{NNN}` | Assign the next valid Rule ID |
| Fractional Rule ID | `BE-024.1` or `BE-024-A` | Assign the next unassigned three-digit ID |
| Reused Rule ID | Retired number appears again | Assign a new ID and document retirement |
| Non-monotonic ID | Rule inserted between existing numbers | Move rule to next available number |
| Command title | `Do Not Trust Input` | Use a noun phrase such as `Input Validation` |
| Combined rule | One rule validates, sanitizes, and logs | Split into independent rules |
| Inflated MUST | Style preference marked MUST | Downgrade to SHOULD or MAY |
| Missing severity keyword | Rule body has no MUST/SHOULD/MAY | Add the correct keyword |
| Weakened protected contract | Specific file relaxes universal safety MUST | Remove relaxation; strengthen or clarify only |
| Duplicate rule | Same rule appears twice | Keep one authoritative home, reference it |
| Broken reference | `see X.md` where X does not exist | Fix or remove |
| Old violation template | Narrative apology template | Use the standard Rule ID template |
| Missing Response to Violation | Required file lacks the section | Add the standard section |
| Empty template section | Section added only to satisfy template | Remove or fill with real content |
| Wrong category | `category: expertise` instead of `domain` | Fix the frontmatter |
| Wrong domain_type | `domain_type: technical` | Use one of the four valid values |
| Unexpected domain_type | `domain_type` present in helper/UI/project/task | Remove it |
| Missing version | `version` absent | Add `version: 1` or bump appropriately |
| Language not en | `lang: fa` in a prompt file | Change to `lang: en` |
| Missing depends_on | Frontmatter lacks `depends_on` | Add `depends_on: []` or dependencies |
| Length/count signal | Far outside typical range | Review coverage; do not pad or trim solely for the number |
| Missing contracts | Delivery/framework/UI file lacks contracts | Add contracts if the file enforces contracts |
| Missing lifecycle contracts | Framework file without lifecycle section | Add it if lifecycle affects behavior |
| Missing version applicability | Language file without version applicability | Add it when version differences matter |
| Missing applicability criteria | Concern file without criteria | Add objective criteria |
| Missing RTL reference | `04-ui-design-system.md` without pointer to RTL file | Add reference |
| Missing logical properties | RTL file without logical-properties section | Add it |
| Missing bidi isolation | RTL file without bidirectional-text section | Add it |

## Part 4 — Verification Process

Before merging any file into the system, follow this process.

### Step 1 — Frontmatter Check

Open the file. Verify the frontmatter against the Universal Checklist. If any required field is missing or wrong, stop and fix it.

### Step 2 — Structural Check

Scroll through the file. Verify:

- Heading hierarchy is correct.
- The opening paragraph states scope and non-coverage.
- Required sections are present for the file's purpose.
- No placeholder markers remain.
- The file ends with `## Response to Violation` when required.

### Step 3 — Rule Architecture Check

Read the file. For every rule, ask:

- Is it operational?
- Does it have a valid Rule ID?
- Does it have a correct severity keyword?
- Does it have a short noun-phrase title?
- Is it one requirement?
- Does it have a rationale when non-obvious?
- Does it belong in this file, or in another layer?
- Is it already covered elsewhere?

If a rule fails any required check, fix or remove it.

### Step 4 — Cross-Reference and Hierarchy Check

Open the files listed in `depends_on`. Search for overlap.

If a rule appears in two files, delete it from the lower layer and reference the higher layer.

For the UI set specifically:

- If a rule in `05-ui-rtl-persian.md` also appears in `04-ui-design-system.md`, remove it from one and reference the other.
- If a Persian-specific rule appears in `04-ui-design-system.md`, move it to `05-ui-rtl-persian.md`.

Verify that no specific file weakens a protected universal `MUST` or `MUST NOT`.

### Step 5 — Category Checklist

Apply the specific category checklist (Part 2). Every required item must pass.

### Step 6 — Common Failures Scan

Scan the Common Failures table (Part 3). Verify none of the failures are present.

### Step 7 — Length and Count Review

Run:

```bash
wc -l <file>
```

Use the count as a signal. If the file is far outside the typical range, review whether:

- coverage is missing;
- rules are duplicated;
- content is padded;
- the file has a documented reason.

Do not trim or expand only to satisfy the number.

### Step 8 — Emoji and Unicode Scan

Run:

```bash
grep -P '[\x{1F300}-\x{1F9FF}\x{2600}-\x{27BF}]' <file>
```

Any match is a failure. Remove the emoji.

### Step 9 — Placeholder Scan

Run:

```bash
grep -nE '(TODO|FIXME|\.\.\.|<!-- FILL IN -->)' <file>
```

Any match is a failure, unless the file is a project template or a send-package guide.

### Step 10 — Persian Content Scan

For files other than `05-ui-rtl-persian.md`, run:

```bash
grep -P '[\x{0600}-\x{06FF}]' <file>
```

Any match in a non-RTL file indicates Persian bleed. Move the content to `05-ui-rtl-persian.md` or remove it.

For `05-ui-rtl-persian.md` itself, verify the Persian examples use correct punctuation (`،`, `؟`, `«»`) and ZWNJ where required.

### Step 11 — Verification Method Review

For every `MUST` rule, verify that there is a plausible verification method:

- automated check, lint, type check, test, or script for mechanically testable rules;
- review criteria, architectural reasoning, or manual verification for non-mechanical rules.

Tests provide evidence of compliance. They do not change rule severity.

### Step 12 — Sign-Off

If all required checks pass and signals have been reviewed, the file is ready. Commit it. Update `prompts/README.md` if the file adds a new entry to a list.

## Part 5 — When a File Fails

Not every file passes the first time. The following process keeps the system from accumulating weak files.

### Case 1 — One or Two Items Fail

Fix them directly in the file. No need to regenerate.

Examples:

- Missing rationale on a rule: add the rationale.
- Emoji in a heading: remove it.
- Wrong `category`: fix the frontmatter.

### Case 2 — Structural Failures

If the file is missing a required section, or a section is too shallow, the file needs more than a patch.

Options:

- Regenerate with a refined prompt.
- Rewrite the weak section manually.

Do not save a file with a missing required section.

### Case 3 — Duplication Failures

If a rule appears in two files, decide where it belongs:

- If it is universal, it stays in Universal and is removed from the other files.
- If it is domain-specific, it stays in the correct domain file.
- If it is project-specific, it stays in the project file.
- If it is RTL-specific, it stays in `05-ui-rtl-persian.md`.

Then update all affected files. Duplication is not a local fix.

### Case 4 — Category Mismatch

If a file is in the wrong category (for example, a framework file placed in `delivery/`), move it. Update all `depends_on` references across the system.

If a Persian-specific rule ends up in `04-ui-design-system.md`, move it to `05-ui-rtl-persian.md`.

### Case 5 — Irredeemable File

If a file cannot be fixed without a full rewrite, delete it. A missing file is better than a misleading one. Regenerate from scratch with the appropriate send-package guide.

## Part 6 — Adding a New Category

If the system gains a new category of files (for example, a new `patterns/` folder, or a new `ui/06-*.md` file), update this checklist.

The new category must define:

1. The folder path.
2. The `category` value in the frontmatter.
3. Its relationship to existing categories (complement or replacement).
4. The required sections that make the category meaningful.
5. The typical length range as a signal.
6. The typical rule and example coverage as signals.
7. The category-specific tests that determine whether a rule belongs in this category.

Add a section to Part 2 with a checklist for the new category. Update Part 1 if any universal rule needs a category-specific variation.

### 6.1 — Adding a New UI File

A new UI file (`ui/06-*.md`) is justified only when:

- The new file covers a distinct audience or locale (for example, `06-ui-japanese.md` for Japanese typography and layout rules).
- The new file is orthogonal to `04-ui-design-system.md` and `05-ui-rtl-persian.md`.
- The new file follows the same set pattern: sent alongside, not instead of, `04-ui-design-system.md`.

Adding a new UI file requires:

1. Updating section 2.7 to include the new file.
2. Adding a bullet to `2.7c — The UI Set Rule` listing the new file.
3. Adding the file's `depends_on` entry in the appropriate project files.
4. Adding the file to `prompts/README.md`.

Do not create a new UI file when the rules could be added to an existing file. The set should stay small.

## Part 7 — Versioning This Document

This checklist is versioned. Bump the version when:

- A new category is added.
- A required acceptance rule changes.
- A common failure is added or removed.
- A verification step changes.

Bump the major version when a change invalidates previously accepted files. Bump the minor version when a change adds a new requirement without invalidating existing files.

The version is in the frontmatter (`version:`). The history of changes is visible through git.

### Version History

- **Version 3**: Aligned with Style Guide version 3. Removed hard numeric acceptance gates. Converted counts and lengths into heuristic signals. Updated length ranges. Added Rule ID, severity, granularity, conflict-resolution, and verification-method checks. Replaced the Response to Violation template. Added `depends_on` and formal QC meta-rules.
- **Version 2**: Added the UI file set (`04-ui-design-system.md` + `05-ui-rtl-persian.md`). Section 2.7 split into 2.7a, 2.7b, and 2.7c. Added Persian-specific checks. Added UI and Persian failures.
- **Version 1**: Initial release.

## Part 8 — Relationship to Send Packages and Style Guide

The send-package guides (`prompts/_send-packages/*.md`) describe the process for generating new files. This checklist describes the acceptance requirements those files must meet.

The two documents serve different purposes:

- **Send packages**: how to generate.
- **This checklist**: what counts as accepted.

When a send-package guide and this checklist disagree about acceptance, this checklist wins. Update the send package to match.

The Style Guide is the governing specification for how prompt files are written. This checklist verifies files against that specification. It MUST NOT contradict the Style Guide. If a contradiction is found, stop migration and correct both documents.

## Part 9 — Quick Reference

For day-to-day review, the following is the minimum bar. If any required item here fails, the file is not ready.

Universal minimum for any file:

- Correct frontmatter.
- English only, no emoji.
- Operational rules only.
- Valid Rule IDs for behavioral rules.
- Correct severity keywords.
- One requirement per rule.
- Every non-obvious rule has a rationale.
- Response to Violation section when required.
- No duplication of Universal or sibling rules.
- No placeholders.

Category-specific expectations:

- **Delivery**: contracts, non-coverage statement, no framework/language bleed.
- **Language**: language-specific rules, version applicability when relevant, rationale.
- **Framework**: lifecycle contracts, framework-specific rules, architecture references.
- **Concern**: applicability criteria, budgets or objective thresholds.
- **Project**: metadata, tools inventory, evidence paths.
- **UI base (`04-ui-design-system.md`)**: contracts, token discipline, RTL reference.
- **UI RTL (`05-ui-rtl-persian.md`)**: RTL contracts, logical properties, bidi isolation, Persian-specific coverage.
- **Task**: follows the fixed template.
- **Helper**: describes workflow or acceptance, not domain content.

The UI set:

- One `04-ui-design-system.md` in the system. Sent to every project with a UI.
- At most one `05-ui-rtl-persian.md` in the system. Sent to projects whose primary language is Persian, Arabic, Hebrew, or Urdu.
- Both are sent together for RTL projects.
- Branding goes in the project file, not in a new UI file.

If a file meets the universal required checks and its category required checks, and its heuristic signals have been reviewed, it is ready.

## Response to Violation

When a rule in this file is violated, report:

Violation: QC-{NNN}
Reason: {one-line reason}
Correction: {smallest fix}

For multiple violations, report each rule ID separately.

Do not replace a technical correction with a generic explanation.