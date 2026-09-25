---
id: 00-style-guide
title: "Prompt File Style Guide"
lang: en
depends_on: []
category: universal
version: 3
---

# Prompt File Style Guide

This file defines the writing conventions for all prompt files in the repository. It sits above domain, UI, project, task, and helper files. It covers rule IDs, severity, structure, duplication, conflict resolution, and review signals. It does not define domain behavior. `QUALITY-CHECKLIST.md` evaluates files against this guide.

## Scope

This guide applies to all Markdown files under `prompts/`. It governs how rules are written and reviewed. It does not define project-specific conventions, task instructions, or send-package workflow.

## Rule Severity

This file is the source of severity semantics. Other files SHOULD use one line:

> Severity follows `_universal/00-style-guide.md`.

## Why This Style

Three problems motivate the style:

1. **Rules are not quotable.** Without IDs, referring to a rule in a review, task, or test requires pasting the whole rule.
2. **Rules have no severity.** Treating every rule as equally important produces either paralysis or dismissal.
3. **Rules are not testable.** A reviewer cannot decide whether a deviation is a violation without knowing what MUST, SHOULD, and MAY mean in this system.

The style below solves all three.

## RFC 2119 Keywords

Every behavioral rule carries one of five keywords. The keywords have the meanings below.

### MUST

A hard requirement. Violating it produces a broken, incorrect, unsafe, or inconsistent result. A MUST is a rule the system will enforce.

- The AI MUST follow it.
- Reviewers MUST flag violations.
- Automated tests SHOULD cover it when mechanically testable.

A MUST requirement MUST NOT be downgraded to SHOULD merely because automated testing is difficult.

MUST MUST be reserved for correctness, safety, security, explicit system contracts, or required behavior. Do not increase the number of MUST rules merely to satisfy a numerical target.

### MUST NOT

A hard prohibition. The inverse of MUST.

### SHOULD

A strong default. Deviation is allowed when a specific reason exists and is documented. A SHOULD is a rule the system expects to see followed unless there is a reason.

- The AI SHOULD follow it.
- Reviewers SHOULD ask for the reason when it is not followed.
- The reason MUST be visible in the code or the response.

### SHOULD NOT

A strong discouragement. The inverse of SHOULD.

### MAY

A permitted option. The project chooses based on its own conventions.

- Both choices are valid.
- Consistency matters more than the choice.

### Prefer / Avoid

"Prefer X" and "Avoid Y" are allowed as informal guidance in prose, but they are not formal rules. If a preference is a rule, it uses MUST, SHOULD, or MAY.

### Severity Integrity

Severity MUST reflect the actual consequence of violating the rule. If violation only affects style, local preference, or optional ergonomics, use SHOULD or MAY.

## Rule IDs

### Format

Every behavioral rule in a prompt file has an ID of the form `{PREFIX}-{NNN}`.

- `PREFIX`: a short uppercase identifier registered in the Prefix Registry.
- `NNN`: a zero-padded three-digit number starting at `001`.

Rule headings use:

```markdown
### {PREFIX}-{NNN} — {Short Title}
```

Examples: `MAS-001`, `BE-024`, `RT-083`, `RTL-042`, `QC-001`.

Behavioral rules are rules that constrain observable prompt behavior, generated output, repository structure, or review outcomes. Meta-authoring conventions in this Style Guide MAY be referenced by section heading when they define how rules are written rather than observable behavior.

### Prefix Registry

The prefix is registered in this file. New files claim a prefix here before adding rules. The Prefix Registry is the source of truth.

| File | Prefix |
|---|---|
| `_universal/00-style-guide.md` | `SG` |
| `_universal/00-master-anti-slop.md` | `MAS` |
| `_universal/01-system.md` | `SYS` |
| `_universal/01-system-append-2.md` | `SYS2` |
| `domains/delivery/02-backend-anti-slop.md` | `BE` |
| `domains/delivery/02-frontend-anti-slop.md` | `FE` |
| `domains/delivery/02-mobile-anti-slop.md` | `MOB` |
| `domains/delivery/02-cli-anti-slop.md` | `CLI` |
| `domains/delivery/02-library-anti-slop.md` | `LIB` |
| `domains/delivery/02-database-anti-slop.md` | `DB` |
| `domains/delivery/02-devops-anti-slop.md` | `OPS` |
| `domains/delivery/02-infra-anti-slop.md` | `INF` |
| `domains/delivery/02-cicd-anti-slop.md` | `CI` |
| `domains/delivery/02-data-pipeline-anti-slop.md` | `DP` |
| `domains/delivery/02-ml-system-anti-slop.md` | `ML` |
| `domains/delivery/02-llm-system-anti-slop.md` | `LLM` |
| `domains/delivery/02-realtime-anti-slop.md` | `RT` |
| `domains/delivery/02-blockchain-anti-slop.md` | `BC` |
| `domains/delivery/02-embedded-anti-slop.md` | `EMB` |
| `domains/delivery/02-game-anti-slop.md` | `GAME` |
| `domains/delivery/02-browser-extension-anti-slop.md` | `EXT` |
| `domains/delivery/02-desktop-anti-slop.md` | `DSK` |
| `domains/language/02-typescript-anti-slop.md` | `TS` |
| `domains/language/02-javascript-anti-slop.md` | `JS` |
| `domains/language/02-python-anti-slop.md` | `PY` |
| `domains/language/02-go-anti-slop.md` | `GO` |
| `domains/language/02-rust-anti-slop.md` | `RS` |
| `domains/language/02-java-kotlin-anti-slop.md` | `JK` |
| `domains/language/02-csharp-anti-slop.md` | `CS` |
| `domains/language/02-swift-anti-slop.md` | `SW` |
| `domains/language/02-ruby-anti-slop.md` | `RB` |
| `domains/language/02-php-anti-slop.md` | `PHP` |
| `domains/language/02-elixir-anti-slop.md` | `EX` |
| `domains/language/02-cpp-anti-slop.md` | `CPP` |
| `domains/framework/02-architecture-anti-slop.md` | `ARCH` |
| `domains/framework/02-react-anti-slop.md` | `REACT` |
| `domains/framework/02-vue-anti-slop.md` | `VUE` |
| `domains/framework/02-angular-anti-slop.md` | `ANG` |
| `domains/framework/02-nextjs-anti-slop.md` | `NEXT` |
| `domains/framework/02-nuxt-anti-slop.md` | `NUXT` |
| `domains/framework/02-nestjs-anti-slop.md` | `NEST` |
| `domains/framework/02-express-anti-slop.md` | `EXP` |
| `domains/framework/02-state-anti-slop.md` | `STATE` |
| `domains/framework/02-api-data-anti-slop.md` | `API` |
| `domains/framework/02-django-anti-slop.md` | `DJANGO` |
| `domains/framework/02-fastapi-anti-slop.md` | `FASTAPI` |
| `domains/framework/02-flask-anti-slop.md` | `FLASK` |
| `domains/framework/02-spring-anti-slop.md` | `SPRING` |
| `domains/framework/02-rails-anti-slop.md` | `RAILS` |
| `domains/framework/02-laravel-anti-slop.md` | `LARAVEL` |
| `domains/framework/02-gin-anti-slop.md` | `GIN` |
| `domains/framework/02-axum-anti-slop.md` | `AXUM` |
| `domains/framework/02-dotnet-anti-slop.md` | `DOTNET` |
| `domains/framework/02-flutter-anti-slop.md` | `FLUTTER` |
| `domains/framework/02-react-native-anti-slop.md` | `RN` |
| `domains/framework/02-electron-anti-slop.md` | `ELECTRON` |
| `domains/concern/02-security-critical-anti-slop.md` | `SEC` |
| `domains/concern/02-accessibility-critical-anti-slop.md` | `A11Y` |
| `domains/concern/02-performance-critical-anti-slop.md` | `PERF` |
| `domains/concern/02-testing-anti-slop.md` | `TEST` |
| `ui/04-ui-design-system.md` | `UI` |
| `ui/05-ui-rtl-persian.md` | `RTL` |
| `projects/<name>/00-anti-slop-core.md` | `PRJ` |
| `tasks/*.md` | `TSK` |
| `QUALITY-CHECKLIST.md` | `QC` |

The `SG` prefix is reserved for this Style Guide. The `QC` prefix is reserved for formal meta-rules in `QUALITY-CHECKLIST.md`.

If the same prefix is shared by multiple files, the numbering sequence MUST remain unique across that prefix.

### Numbering

Rule numbering is an identity mechanism, not a visual sequence.

- The first rule uses `001`.
- Rule IDs MUST be unique within a prefix.
- Rule IDs MUST be monotonically assigned within a prefix.
- New rules MUST receive the next unassigned three-digit number greater than the highest previously assigned number for that prefix.
- Existing Rule IDs MUST NOT be reused.
- Existing Rule IDs MUST NOT be renumbered.
- Gaps are allowed when a rule has been retired.
- Fractional or hierarchical identifiers such as `BE-024.1`, `BE-024-A`, or `BE-024.1.2` MUST NOT be introduced.
- Visual grouping and topical ordering do not change Rule IDs.

### Retirement

A retired rule's number is listed in the file's `## Retired Rules` section with a one-line reason.

The number MUST NOT be reassigned.

Gaps caused by retirement are valid and MUST NOT be fixed by renumbering.

## Rule Structure

Every behavioral rule follows the same structure.

### Minimal Form

```markdown
### {PREFIX}-{NNN} — {Short Title}

**{MUST | MUST NOT | SHOULD | SHOULD NOT | MAY}**

{Body: 1 to 5 sentences.}

{Code example, table, or list when helpful.}
```

### The Short Title

- Title is a noun phrase, not a sentence.
- Title is 2 to 6 words.
- Title is not a command ("Do not use X") but a subject ("X Discipline").

BAD: `### BE-024 — Do Not Use SELECT *`

GOOD: `### BE-024 — SELECT Star Discipline`

### The Severity Keyword

The keyword is on its own line, in bold, immediately after the title.

### The Body

The body:

- Explains what the rule requires.
- Explains why with a one-line rationale.
- Gives an example when the rule is non-obvious.

The body does not:

- Repeat the rule.
- Explain the obvious.
- Reference tools or frameworks not mentioned in the file.

### Code Examples

Code examples use fenced blocks with a language tag. Paired examples use `BAD:` and `GOOD:`.

BAD:

```typescript
const user = response as User;
```

GOOD:

```typescript
const user = userSchema.parse(response);
```

Code examples SHOULD be used when they materially improve understanding or when the rule is implementation-oriented.

Non-code policy, process, ownership, or architectural rules MUST NOT be forced to include code examples when no code-visible behavior exists.

### Rule Granularity

One rule, one requirement. If a rule contains independent requirements joined by "and" or "or", split it.

BAD: `BE-024 — Validate Input And Escape Output`

GOOD: `BE-024 — Input Validation` and `BE-025 — Output Encoding`

### Rule Ordering

Rules are grouped by topic under `##` sections. Within a section, rules are ordered logically: fundamental rules first, edge cases later.

Rule IDs remain stable even when rules are moved within the file.

## File Structure

A standard prompt file contains the sections that match its purpose. Do not create empty sections merely to satisfy a template.

### Frontmatter

```yaml
---
id: <id>
title: "<Title>"
lang: en
depends_on: [<dependencies>]
category: <category>
domain_type: <type>   # only for domain files
version: <n>
---
```

- `id` is the stable file identifier. It is not a Rule ID. It SHOULD be kebab-case and SHOULD match the lowercased file name without extension.
- `title` is human-readable and quoted.
- `lang` MUST be `en` for prompt files.
- `depends_on` MUST be a list. Use `[]` when there are no dependencies.
- `category` MUST be one of: `universal`, `domain`, `ui`, `project`, `task`, `helper`.
- `version` MUST be a positive integer.
- For domain files, use:

```yaml
category: domain
domain_type: <delivery|language|framework|concern>
```

- `domain_type` MUST NOT be present when `category` is not `domain`.
- `domain_type` MUST NOT be used as the value of `category`.

### H1 Title

`# <Title>` matches the frontmatter's `title` field.

### Opening Paragraph

3 to 5 lines stating:

- Where the file sits in the architecture.
- What the file covers.
- What the file does NOT cover.
- Related files, when appropriate.

Avoid long introductory essays.

### Scope Section

`## Scope` lists what the file applies to. For domain files, this is where Stack Assumptions live.

### Severity Section

`## Rule Severity` restates the MUST/SHOULD/MAY definitions only if the file is likely to be read alone. In most files, a single line suffices:

> Severity follows `_universal/00-style-guide.md`.

### Contracts Section

For delivery, framework, concern, and UI files, a `## Contracts` section lists the contracts the file enforces. Each contract maps to one or more rule sections.

### Rule Sections

Rule sections group rules by topic. Each section is an H2. Each rule inside is an H3.

### Anti-Patterns Section

`## Anti-Patterns` lists rules with `MUST NOT` or `SHOULD NOT` severity. Every anti-pattern is a rule with an ID.

### Response to Violation

Files that define behavioral rules end with `## Response to Violation`. The heading is not numbered.

```markdown
## Response to Violation

When a rule in this file is violated, report:

Violation: {PREFIX}-{NNN}
Reason: {one-line reason}
Correction: {smallest fix}

For multiple violations, report each rule ID separately.

Do not replace a technical correction with a generic explanation.
```

Governance documents that do not define behavioral Rule IDs MAY omit this section rather than creating an empty or artificial template.

### Retired Rules

`## Retired Rules` lists retired IDs with one-line reasons. Omit this section if no rules have been retired.

## Length and Coverage Targets

Length, rule count, and example count are heuristic signals, not hard acceptance gates.

Files have target ranges. A file far outside the range is a signal for review.

| Category | Typical line range |
|---|---|
| Universal | 200–400 |
| Delivery | 250–450 |
| Language | 250–450 |
| Framework | 250–450 |
| Concern | 250–450 |
| UI (general) | 250–450 |
| UI (RTL/Persian) | 350–700 |
| Project | 60–180 |
| Task | 30–150 |

A file MUST NOT be rejected solely because it is outside the target range if coverage, clarity, and rationale are documented.

Files with a justified reason may exceed or fall below the typical range. The reason SHOULD be documented.

Artificial rules, artificial examples, or filler content created only to reach a numeric target MUST NOT be accepted.

### Rule and Example Count

Rule count SHOULD be determined by the actual behavioral requirements of the file.

A file SHOULD contain enough rules to define its required behavior clearly, but it MUST NOT add artificial rules solely to satisfy a numerical target.

Examples SHOULD be used when they materially improve understanding or when the rule is implementation-oriented.

Non-code policy, process, ownership, or architectural rules MUST NOT be forced to include code examples when no code-visible behavior exists.

## Non-Duplication

### One Authoritative Home

Every rule is written in exactly one file. Rules in Universal are not repeated in Domain. Rules in Domain are not repeated in Project.

### Cross-Reference Format

When a file needs to mention a rule from another file:

> See `{PREFIX}-{NNN}` in `{file}`.

Do not restate the rule. Do not paraphrase it. Reference it.

## Conflict Resolution

When two files define a rule for the same topic:

1. A more specific file may refine, clarify, or strengthen a broader rule.
2. A specific file MUST NOT weaken or contradict a broader `MUST` or `MUST NOT` requirement when that requirement protects correctness, safety, security, or shared system contracts.
3. A specific file may impose stricter requirements when its scope legitimately requires them.
4. If equally specific rules conflict, the higher severity governs.
5. If an equally severe rule replaces another rule, the old rule MUST be retired and referenced.
6. If the conflict remains unresolved, the higher-level contract remains authoritative until explicitly changed.

Specificity is a mechanism for specialization, not a way to override fundamental correctness or safety requirements.

## Language and Tone

- Files are written in English.
- No emoji.
- No marketing language.
- No apology.
- No filler.
- No vague statements.
- No motivational prose.

Prefer concise technical language.

## Deprecated Patterns

The following patterns were used in older versions of files. They are deprecated.

| Deprecated | Replacement |
|---|---|
| `BAD:` / `GOOD:` without rule IDs | Rule IDs + BAD/GOOD |
| "Never do X" as prose | A `MUST NOT` rule with an ID |
| "Always do Y" as prose | A `MUST` rule with an ID |
| Section numbers only | Semantic headings and rule IDs for behavioral rules |
| Numbered `## N. Response to Violation` heading | `## Response to Violation` |
| Long paragraphs of explanation | Short body + example |
| Fractional Rule IDs such as `BE-024.1` | Next unassigned three-digit Rule ID |
| Renumbering after retirement | Keep stable IDs and document retired gaps |
| Hard numeric rule counts as sole acceptance | Coverage-based review with heuristic targets |
| Restating a rule in multiple files | One authoritative home plus cross-reference |

Older files are migrated to the new style as they are rewritten.

## Changelog of This Guide

- **Version 3**: Standardized the rule heading separator to an em dash. Added `QC` to the Prefix Registry. Clarified category values, file `id`, `depends_on`, and `domain_type` absence. Clarified governance documents and Response to Violation scope. Added severity integrity, shared-prefix numbering, protected-contract conflict resolution, and anti-padding guidance.
- **Version 2**: Removed fractional Rule IDs. Changed numbering to unique, monotonically assigned, append-only IDs. Converted length and count targets into heuristic signals. Clarified conflict resolution to protect mandatory safety and correctness rules. Clarified MUST testability. Clarified `category: domain` and `domain_type` usage.
- **Version 1**: Initial release. Defined RFC 2119 keywords, rule ID format, file structure, and migration rules.