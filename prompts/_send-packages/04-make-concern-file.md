---
id: 04-make-concern-file
title: "How to Generate a Concern File"
lang: en
category: helper
version: 2
---

# How to Generate a Concern File

Concern files are for projects where a specific constraint is
first-class, not an afterthought: security-critical, accessibility-
critical, performance-critical, i18n-critical, testing,
refactoring, observability.

A concern file is NOT a general best-practices file. General rules
for security, accessibility, and performance belong in the delivery
file that owns them (for example, security rules for a backend
belong in the backend delivery file).

A concern file applies only when:

- The project has a legal or regulatory obligation tied to the
  concern.
- The project has a measurable budget (WCAG level, p95 latency,
  error rate, frame budget).
- The concern has a dedicated audience (screen-reader users for
  accessibility, auditors for security, SREs for observability).
- A single mistake in the concern can cause harm beyond the
  project (data breach, injury, financial loss, legal liability).

If none of these applies, the concern file is premature. Sending it
for every project dilutes its signal and wastes context.

## When to Use This Guide

Use this guide when generating or regenerating a file under
`prompts/domains/concern/`.

Use it when:

- A project is added where a concern is first-class.
- An existing concern file is too shallow and needs a rewrite.
- The concern has new regulatory or technical requirements.

Do NOT use it when:

- Generating a language file (see `02-make-language-file.md`).
- Generating a delivery file (see `01-make-delivery-file.md`).
- Generating a framework file (see `03-make-framework-file.md`).

## Files to Attach

### Required

- `_universal/00-master-anti-slop.md`

This file is mandatory. Without it, the AI cannot avoid duplicating
universal rules (especially the security section in Universal §2.4).

### Required (1-2 examples from the same category)

Attach at least one, ideally two, existing concern files. See the
table below for concern-specific recommendations.

### Optional (delivery context)

If the concern is tied to a specific delivery type, attach the
delivery file:

- `domains/delivery/02-frontend-anti-slop.md` for accessibility and
  i18n concerns.
- `domains/delivery/02-backend-anti-slop.md` for security and
  observability concerns.
- `domains/delivery/02-mobile-anti-slop.md` for mobile performance
  concerns.

Without the delivery file, the concern file may repeat rules that
belong to the delivery layer.

## Reference Attachments by Concern

The following table tells you which existing concern files to attach
as references for each target. Attach two whenever possible.

| Target concern | Primary reference | Secondary reference |
|---|---|---|
| security-critical | 02-security-critical-anti-slop.md | 02-observability-anti-slop.md |
| accessibility-critical | 02-accessibility-critical-anti-slop.md | 02-i18n-critical-anti-slop.md |
| performance-critical | 02-performance-critical-anti-slop.md | 02-observability-anti-slop.md |
| i18n-critical | 02-i18n-critical-anti-slop.md | 02-accessibility-critical-anti-slop.md |
| testing | 02-testing-anti-slop.md | 02-refactoring-anti-slop.md |
| refactoring | 02-refactoring-anti-slop.md | 02-testing-anti-slop.md |
| observability | 02-observability-anti-slop.md | 02-security-critical-anti-slop.md |
| privacy-critical | 02-security-critical-anti-slop.md | 02-observability-anti-slop.md |
| compliance-critical | 02-security-critical-anti-slop.md | 02-observability-anti-slop.md |
| cost-critical | 02-observability-anti-slop.md | 02-performance-critical-anti-slop.md |

If the target concern is not listed, pick the two references whose
purpose is closest. A new concern about safety references security
and observability. A new concern about reliability references
observability and performance.

## Additional Prompt Requirements

When filling in the master prompt for a concern file, insert the
following block under the `Mandatory Rules` section. This block
overrides the defaults for the concern category.

```
### Concern-Specific Requirements

Concern files must satisfy the following in addition to the
general rules:

1. When This File Applies.

   The file MUST include a section titled "When This File Applies"
   that states the objective criteria for sending this file.

   The criteria must be objective, not subjective. "When security
   matters" is not a criterion. "When the project handles PII,
   credentials, or financial data" is.

   Each criterion is one of:
   - A regulatory obligation (PCI-DSS, GDPR, HIPAA, WCAG AA).
   - A measurable budget (p99 latency under 100 ms, LCP under
     2.5 s).
   - A dedicated audience (screen-reader users, auditors).
   - A harm vector (data breach, injury, financial loss).

   The section ends with a statement of when the file does NOT
   apply. This prevents the file from being sent to every project
   and diluting its signal.

2. Concern Budgets.

   The file MUST include a section titled "Concern Budgets" that
   states the measurable thresholds for this concern:

   - What is measured (metric name, unit).
   - The target (a specific number, not "fast" or "accessible").
   - The failure threshold (when the metric is out of budget).
   - The measurement method (tool, process, frequency).

   For a security concern, the budget might be: "zero known high-
   severity CVEs in dependencies at release time, measured by
   `npm audit` or equivalent."

   For an accessibility concern: "WCAG 2.2 AA compliance, verified
   by automated tooling plus keyboard-only walkthrough."

   For a performance concern: "LCP under 2.5 s, INP under 200 ms,
   CLS under 0.1, measured by Lighthouse on a throttled connection."

   Without a budget, the concern is a feeling, not a constraint.

3. Concern Boundaries.

   The opening paragraph MUST state clearly what this file does
   NOT cover, with references to sibling files. For example:

       This file does NOT cover:
       - General security rules for every project (see Universal
         section 2.4).
       - Backend-specific security (see 02-backend-anti-slop.md).
       - Authentication and authorization in detail (see the
         backend delivery file).

   Without boundaries, the concern file duplicates delivery,
   language, and framework rules.

4. Concern-Specific, Not General.

   Every rule MUST be specific to a project where this concern is
   first-class. If a rule applies to any project, it belongs in
   Universal or in the relevant delivery file.

   Test: would a project without this concern follow the same
   rule? If yes, the rule is not specific to the concern.

   BAD (applies to any project):
       ### 3.1 Validate Input

       Validate all user input before using it.

   GOOD (specific to security-critical):
       ### 3.1 Validate Input at Trust Boundaries

       In a security-critical system, every input that crosses a
       trust boundary is validated against an allowlist (not a
       blocklist). A blocklist is always incomplete; an allowlist
       is enforceable. Validate at the boundary, not deep in the
       application.

5. Rationale for Every Rule.

   Every rule MUST include a one-line rationale, even when the rule
   seems obvious. The rationale helps the model generalize the rule
   to cases the file does not cover.

   For concerns, the rationale often references an attack, a legal
   requirement, or a measured failure mode.

6. At Least 20 Anti-Patterns.

   The `Anti-Patterns` section MUST have at least 20 items, not 20
   rules total. Rules live in the earlier sections; the anti-pattern
   section is a list of concrete mistakes.

   Each anti-pattern has:
   - A short title.
   - A one-line explanation.
   - A BAD/GOOD code pair, unless the anti-pattern is operational
     (in which case a textual BAD/GOOD is acceptable).

   Concern anti-patterns are often subtle: a control that looks
   right but is bypassable, a cache that leaks PII, an accessible
   component that fails at 200% zoom.

7. At Least 18 Rules with BAD/GOOD.

   Not 50% of rules. At least 18 concrete examples in the entire
   file. This number is a floor, not a target.

   Concern rules are highly concrete: a specific misconfiguration,
   a specific WCAG failure, a specific latency bug. Examples are
   the primary way to convey these rules.

8. No Delivery Bleed.

   Do not include rules that apply to any project of the delivery
   type. A security concern does not restate the backend's input
   validation rules; it extends them.

   A concern file extends the delivery file with concern-specific
   practices.
```

## Filling in the Master Prompt

Use this template for the metadata portion of the master prompt:

```
Path: prompts/domains/concern/02-<name>-anti-slop.md
id: 02-<name>-anti-slop
title: <Name> Anti-Slop Layer
domain_type: concern
depends_on: [00-master-anti-slop]

Coverage:
Rules for projects where <concern> is a first-class requirement.
Covers <list 5-7 topics from the Suggested Topics section below>.

NOT covered:
General delivery rules, language rules, framework rules. This file
assumes the reader has already seen the relevant delivery file.
```

Then insert the `Additional Prompt Requirements` block above under
the `Mandatory Rules` section of the master prompt.

## Suggested Topics by Concern Paradigm

Use these as a starting set of sections. Adjust for the specific
concern.

### Safety Concerns

Security, privacy, compliance, safety-critical.

- When the file applies (objective criteria)
- Threat model
- Trust boundaries
- Controls and their bypass vectors
- Auditing and logging
- Incident response
- Regulatory references
- Anti-patterns (bypassable controls, silent failures)

### Quality Concerns

Accessibility, i18n, performance, reliability.

- When the file applies (objective criteria)
- Budget (measurable thresholds)
- Baseline requirements
- Testing methodology
- Automation and tooling
- Common failures
- Anti-patterns (compliant-looking but broken)

### Process Concerns

Testing, refactoring, observability.

- When the file applies
- Practice discipline
- Tooling and configuration
- Coverage vs value
- Failure modes
- Common mistakes
- Anti-patterns (tests that lie, refactors that change behavior)

### Cost Concerns

Cost-critical, budget-critical.

- When the file applies
- Unit economics
- Measurement and attribution
- Budgets and alerts
- Optimization hierarchy
- Anti-patterns (hidden costs, unbounded growth)

## Suggested Topics by Specific Concern

When the target concern is on this list, use the suggested topics
as the starting set.

### security-critical

- When this file applies (PII, credentials, financial data, auth)
- Threat modeling (assets, adversaries, surfaces)
- Authentication (password hashing, sessions, tokens, MFA)
- Authorization (object-level, function-level, deny-by-default)
- Input validation and output encoding
- Data protection (encryption at rest, in transit, secrets)
- Cryptography discipline
- Dependency and supply chain
- Error messages and information disclosure
- Logging and monitoring
- Anti-patterns (trust client, IDOR, mass assignment, SSRF)

### accessibility-critical

- When this file applies (legal obligation, first-class audience)
- WCAG principles and levels
- Semantic HTML
- Keyboard accessibility
- Focus management
- Screen reader support
- Visual accessibility (contrast, motion, resize)
- Forms and interactive components
- Testing (automated + manual + user)
- Anti-patterns (removed focus, fake buttons, ARIA misuse)

### performance-critical

- When this file applies (measurable budget)
- Measure before optimizing
- Performance budgets (frontend, backend, database)
- Profiling tools and methods
- Frontend performance (LCP, INP, CLS)
- Backend performance (latency, throughput)
- Database performance (query plans, N+1)
- Caching and invalidation
- Anti-patterns (premature optimization, unbounded queries)

### i18n-critical

- When this file applies (multiple locales, RTL, legal)
- Locale detection and fallback
- Translation key discipline
- Pluralization rules
- Date, number, and currency formatting
- RTL/LTR handling
- Bidirectional layout
- Testing across locales
- Anti-patterns (concatenated strings, hardcoded formats)

### testing

- When this file applies (quality gates, regulated software)
- Test pyramid
- Isolation and independence
- Fixtures and factories
- Flakiness and determinism
- Coverage vs value
- CI integration
- Anti-patterns (flaky tests, snapshot abuse, implementation tests)

### refactoring

- When this file applies (legacy code, safety-critical changes)
- Characterization tests
- Small steps
- Behavior preservation
- Strangler fig pattern
- No behavior change in the same commit
- Rollback and review
- Anti-patterns (rewrite as refactor, rename with logic change)

### observability

- When this file applies (production systems, SLIs)
- Logs (structure, levels, fields)
- Metrics (RED, USE)
- Traces (spans, context propagation)
- SLIs, SLOs, error budgets
- Alerts (symptom-based, actionable)
- Dashboards
- Anti-patterns (log spam, metric explosion, alert fatigue)

## Verification

After receiving the file from the AI, verify:

1. Every item in the master prompt's self-audit checklist.
2. Every item in the `Concern-Specific Self-Audit` below.
3. The file is between 220 and 380 lines (concern files are often
   shorter than delivery files but longer than language files).
4. The file does not repeat rules from the attached sibling files
   or from the delivery file.

If any item fails, request a revision from the AI rather than
saving a weak file.

## Concern-Specific Self-Audit

Before saving the generated file, verify every item:

When This File Applies:
- [ ] A section titled "When This File Applies" exists
- [ ] The criteria are objective, not subjective
- [ ] At least three criteria are listed
- [ ] The section states when the file does NOT apply

Concern Budgets:
- [ ] A section titled "Concern Budgets" exists
- [ ] The metric is named with a unit
- [ ] The target is a specific number
- [ ] The failure threshold is stated
- [ ] The measurement method is described

Boundaries:
- [ ] The opening paragraph states what the file does NOT cover
- [ ] References to Universal, delivery, and other layers exist
- [ ] No rule belongs to another layer

Concern Specificity:
- [ ] Every rule is specific to a project where the concern is
      first-class
- [ ] No rule would apply to a project without the concern
- [ ] The rationale references a budget, a legal requirement, or
      a specific harm

Rationale Discipline:
- [ ] Every rule has a one-line rationale
- [ ] The rationale explains why, not just what

Anti-Patterns:
- [ ] The Anti-Patterns section has at least 20 items
- [ ] Each item has a short title
- [ ] At least 10 items have a BAD/GOOD code pair

Code Examples:
- [ ] At least 18 rules in the file have BAD/GOOD code pairs
- [ ] Code blocks use a language tag
- [ ] Names are realistic
- [ ] Examples are 5-15 lines

Structural:
- [ ] Frontmatter is complete
- [ ] Opening paragraph is 3-5 lines
- [ ] At least 11 sections total
- [ ] Response to Violation section matches the fixed template
- [ ] Entire file is in English
- [ ] No emoji

Non-Duplication:
- [ ] No rule from Universal is repeated
- [ ] No rule from the delivery file is repeated
- [ ] No rule from the language file is repeated
- [ ] No rule from the framework file is repeated
- [ ] No rule from the attached sibling concern files is repeated
- [ ] References to other files have one-line summaries

If any item fails, ask the AI to revise the specific section. Do
not save a file that fails the self-audit.

## Common Failures

The following failures occur frequently when generating concern
files. Use this table during review.

| Failure | How to spot it | Fix |
|---|---|---|
| No "When This File Applies" | Missing the section | Request it |
| Subjective criteria | "When security matters" | Make objective |
| No budgets | No measurable thresholds | Request them |
| Delivery bleed | Rules apply to any backend/frontend | Move to delivery file |
| Universal bleed | Includes "validate input" generically | Delete or reference Universal |
| Concern-agnostic rules | Rule applies without the concern | Move to delivery or delete |
| Missing rationale | Rules say "do not" without "because" | Request rationale |
| Too few anti-patterns | Under 20 items | Request more |
| Shallow code examples | Under 18 BAD/GOOD pairs | Request concrete cases |
| Over-length | Over 400 lines | Split or trim |
| Regulatory hand-waving | References GDPR without specifics | Ask for the specific rule |
| Tool-specific without reason | Names a tool as the only option | Generalize or document |

## After the File Is Accepted

1. Save to `prompts/domains/concern/02-<name>-anti-slop.md`.
2. Update `prompts/README.md` to include the new file in the
   concern list.
3. Add the file to the relevant project templates under
   `prompts/projects/` if the concern applies.
4. If the concern has a measurable budget, consider adding it to
   the project's CI or monitoring.

## Time Budget

Generating a concern file with a frontier model takes 3-6 minutes.
Review takes 10-15 minutes with the self-audit checklist. If review
takes longer than 20 minutes, the master prompt likely needs
refinement for future concern files.

## Reference Example

The example in `prompts/_send-packages/example-svelte/` shows the
workflow for a framework file. Follow the same workflow, with the
additional `Concern-Specific Requirements` block inserted into the
master prompt.

## A Note on Concern Multiplication

Do not create a new concern file for every possible constraint.
Each concern file increases the context size of the projects it is
sent to. A project should have at most two or three concerns.

Before creating a new concern, ask:

- Is the concern first-class, or a good practice?
- Does the concern have a measurable budget?
- Does the concern have a dedicated audience?
- Would a mistake in the concern cause harm beyond the project?

If any answer is no, the concern belongs in the delivery file, not
in a separate concern file.
