---
id: 01-make-delivery-file
title: "How to Generate a Delivery File"
lang: en
category: helper
version: 2
---

# How to Generate a Delivery File

Delivery files describe what kind of system is being built: backend,
frontend, mobile, CLI, library, database, DevOps, infrastructure,
CI/CD, data pipeline, ML system, LLM system, realtime, blockchain,
embedded, game, browser extension, desktop.

A delivery file is NOT a general guide to the domain. It focuses on
the operational rules that apply when building this kind of system.
If a rule is common to every project, it belongs in Universal. If a
rule is common to every backend, it belongs in the backend delivery
file. The delivery file holds only what is specific to the delivery
type itself.

A delivery file is the primary file that defines what "done" means
for this kind of system. It is where the AI learns what quality
looks like for this delivery type.

## When to Use This Guide

Use this guide when generating or regenerating a file under
`prompts/domains/delivery/`.

Use it when:

- A new delivery type is added to the system.
- An existing delivery file is too shallow and needs a rewrite.
- A delivery type gains new tooling worth documenting.

Do NOT use it when:

- Generating a language file (see `02-make-language-file.md`).
- Generating a framework file (see `03-make-framework-file.md`).
- Generating a concern file (see `04-make-concern-file.md`).

## Files to Attach

### Required

- `_universal/00-master-anti-slop.md`

This file is mandatory. Without it, the AI cannot avoid duplicating
universal rules, and the generated file will overlap with the
universal layer.

### Required (1-2 examples from the same category)

Attach at least one, ideally two, existing delivery files that are
accepted as good. See the table below for delivery-specific
recommendations.

### Optional

- A concern file if the delivery type has a natural concern (for
  example `02-security-critical-anti-slop.md` for a payments
  system).

## Reference Attachments by Delivery Type

The following table tells you which existing delivery files to
attach as references for each target. Attach two whenever possible.

| Target delivery | Primary reference | Secondary reference |
|---|---|---|
| backend | 02-backend-anti-slop.md | 02-database-anti-slop.md |
| frontend | 02-frontend-anti-slop.md | 02-backend-anti-slop.md |
| mobile | 02-mobile-anti-slop.md | 02-frontend-anti-slop.md |
| cli | 02-cli-anti-slop.md | 02-library-anti-slop.md |
| library | 02-library-anti-slop.md | 02-cli-anti-slop.md |
| database | 02-database-anti-slop.md | 02-backend-anti-slop.md |
| devops | 02-devops-anti-slop.md | 02-infra-anti-slop.md |
| infrastructure | 02-infra-anti-slop.md | 02-devops-anti-slop.md |
| cicd | 02-cicd-anti-slop.md | 02-devops-anti-slop.md |
| data-pipeline | 02-data-pipeline-anti-slop.md | 02-database-anti-slop.md |
| ml-system | 02-ml-system-anti-slop.md | 02-data-pipeline-anti-slop.md |
| llm-system | 02-llm-system-anti-slop.md | 02-ml-system-anti-slop.md |
| realtime | 02-realtime-anti-slop.md | 02-backend-anti-slop.md |
| blockchain | 02-blockchain-anti-slop.md | 02-security-critical-anti-slop.md |
| embedded | 02-embedded-anti-slop.md | 02-cpp-anti-slop.md |
| game | 02-game-anti-slop.md | 02-realtime-anti-slop.md |
| browser-extension | 02-browser-extension-anti-slop.md | 02-frontend-anti-slop.md |
| desktop | 02-desktop-anti-slop.md | 02-frontend-anti-slop.md |

If the target delivery type is not listed, pick the two references
whose operational shape is closest. A batch system references a
data pipeline. A service references a backend. A tool references
a CLI.

## Additional Prompt Requirements

When filling in the master prompt for a delivery file, insert the
following block under the `Mandatory Rules` section. This block
overrides the defaults for the delivery category.

```
### Delivery-Specific Requirements

Delivery files must satisfy the following in addition to the
general rules:

1. Delivery-Specific Contracts.

   The file MUST include a section titled "Delivery Contracts" or
   an equivalent heading that lists the operational contracts the
   delivery type commits to.

   For a backend, contracts include request/response shape, status
   codes, error format, pagination, idempotency, and versioning.

   For a frontend, contracts include component boundaries, state
   ownership, data fetching patterns, and routing conventions.

   For a CLI, contracts include argument shape, exit codes, stream
   behavior, and signal handling.

   For a data pipeline, contracts include idempotency, backfill
   semantics, schema evolution, and delivery guarantees.

   For an ML system, contracts include train/serve parity, feature
   computation, evaluation metrics, and model versioning.

   The contracts section is where the delivery type declares what
   it promises. Other sections enforce those promises.

2. Delivery Boundaries.

   The opening paragraph MUST state clearly what this file does NOT
   cover, with references to sibling files. For example:

       This file does NOT cover:
       - Language-specific rules (see the language files).
       - Framework-specific rules (see the framework files).
       - General security, accessibility, or performance rules
         (see the concern files).

   Without boundaries, the file grows without limit and duplicates
   other layers.

3. Rationale for Every Rule.

   Every rule MUST include a one-line rationale, even when the rule
   seems obvious. The rationale helps the model generalize the rule
   to cases the file does not cover.

   BAD:
       ### 2.4 Status Codes

       Use the correct status code.

   GOOD:
       ### 2.4 Status Codes

       The status code is part of the API contract. Clients depend
       on it to decide whether to retry, surface an error, or
       proceed. A wrong code is a breaking change.

4. At Least 25 Anti-Patterns.

   The `Anti-Patterns` section MUST have at least 25 items, not 25
   rules total. Rules live in the earlier sections; the anti-pattern
   section is a list of concrete mistakes.

   Each anti-pattern has:
   - A short title.
   - A one-line explanation.
   - A BAD/GOOD code pair, unless the anti-pattern is purely
     operational (in which case a textual BAD/GOOD is acceptable).

   The higher count (25 vs 20 for other categories) reflects the
   breadth of delivery types. A backend has dozens of concrete
   anti-patterns; a CLI has a different dozens. The anti-pattern
   section is where this breadth lives.

5. At Least 20 Rules with BAD/GOOD.

   Not 50% of rules. At least 20 concrete code examples in the
   entire file. This number is a floor, not a target.

   If the file has fewer than 20 code examples, it is likely too
   abstract and needs concrete cases.

6. No Framework Bleed.

   Delivery files describe the delivery type, not the framework.
   If a rule mentions React hooks, Django models, or Express
   middleware, it belongs in a framework file.

   A delivery file may mention a framework name to illustrate a
   point, but the rule itself must be framework-agnostic.

   Exception: a delivery type that is inherently tied to a
   framework (React Native to React) may reference the framework
   as a dependency, but the rules remain framework-level, not
   framework-specific.
```

## Filling in the Master Prompt

Use this template for the metadata portion of the master prompt:

```
Path: prompts/domains/delivery/02-<name>-anti-slop.md
id: 02-<name>-anti-slop
title: <Name> Anti-Slop Layer
domain_type: delivery
depends_on: [00-master-anti-slop]

Coverage:
Rules specific to <delivery type>: <list 5-7 topics from the
Suggested Topics section below>.

NOT covered:
Language rules, framework rules, generic concern rules.
<related delivery types> belong in their own files.
```

Then insert the `Additional Prompt Requirements` block above under
the `Mandatory Rules` section of the master prompt.

## Suggested Topics by Delivery Paradigm

Use these as a starting set of sections. Adjust for the specific
delivery type.

### Service Delivery

Backend, realtime, LLM system, blockchain.

- Contracts (request, response, error)
- Input validation
- Error handling
- Authentication and authorization
- Persistence and data flow
- Concurrency and background work
- Logging and observability
- Deployment and health

### Interface Delivery

Frontend, mobile, desktop, browser extension.

- Component discipline
- State ownership
- Data fetching
- Forms and user input
- Routing and navigation
- Error and loading states
- Performance and bundle size
- Platform integration

### Tool Delivery

CLI, library.

- Public interface (flags, exports)
- Contracts (exit codes, semver)
- Error reporting
- Stream behavior (CLI) or side-effect discipline (library)
- Configuration
- Distribution and packaging
- Backwards compatibility
- Help and documentation

### Data Delivery

Database, data pipeline, ML system.

- Schema and contracts
- Idempotency
- Migrations and schema evolution
- Quality and validation
- Backfills and reprocessing
- Monitoring and alerting
- Lineage and versioning
- Cost and retention

### Operations Delivery

DevOps, infrastructure, CI/CD.

- Resource definition
- State management
- Plan and review
- Secrets and security
- Rollout and rollback
- Health and monitoring
- Cost and cleanup
- Drift detection

### Low-Level Delivery

Embedded, game.

- Resource budgets (memory, CPU, frame)
- Determinism and reproducibility
- Concurrency primitives
- Memory management
- Communication protocols
- Error handling without exceptions
- Testing on target
- Debugging facilities

## Suggested Topics by Specific Delivery

When the target delivery type is on this list, use the suggested
topics as the starting set.

### backend

- Contracts (request, response, error shape)
- Input validation
- Error handling and status codes
- Authentication and authorization
- Database and persistence
- Async and concurrency
- Logging
- Configuration
- Migrations
- Rate limiting and resource protection
- API documentation

### frontend

- Component discipline
- State ownership
- Data fetching
- Forms
- Routing
- Effects and lifecycle
- Performance
- Error handling
- Environment and configuration
- Language and i18n

### mobile

- Lifecycle and state restoration
- Permissions
- Offline and network handling
- Platform UI conventions
- Storage and security
- Push notifications
- App store compliance
- Performance on low-end devices

### cli

- Command structure
- Argument parsing
- Exit codes
- Standard streams (stdout, stderr)
- Signals and interruption
- Help and documentation
- Configuration precedence
- Distribution and packaging

### library

- Public API design
- Semantic versioning
- Backwards compatibility
- Tree-shaking and bundle size
- Testing the public API
- Documentation
- Distribution and packaging

### database

- Schema design
- Migrations
- Indexes
- Query discipline
- Transactions and isolation
- Data types
- Access control
- Backup and recovery

### devops

- Containers
- Orchestration
- Deployment strategy
- Secrets
- Health checks
- Logging and monitoring
- Rollback
- Backup and recovery

### infrastructure

- State management
- Modules
- Plan and review
- Drift detection
- Secrets
- Network and security
- Idempotency

### cicd

- Pipeline structure
- Caching
- Secrets
- Testing
- Artifacts
- Deployment
- Rollback
- Notifications

### data-pipeline

- Idempotency
- Backfills
- Schema evolution
- Late and out-of-order data
- DAG design
- Data quality
- Storage and cost
- Lineage

### ml-system

- Data splitting and leakage
- Feature engineering
- Training reproducibility
- Evaluation
- Model versioning
- Serving
- Monitoring and drift
- Retraining

### llm-system

- Prompt design
- Prompt injection
- Retrieval-augmented generation
- Evaluation
- Cost control
- Reliability and fallbacks
- Streaming
- Tool use

### realtime

- Connection lifecycle
- Delivery guarantees
- Ordering
- Backpressure
- Reconnection
- Presence
- Scaling
- Protocol versioning

### blockchain

- Security (reentrancy, oracles, flash loans)
- Gas optimization
- Upgradeability
- Testing (fork, fuzz, invariant)
- Deployment
- Ownership and access control

### embedded

- Memory discipline
- Real-time constraints
- Interrupts
- Concurrency
- Power management
- Communication
- Firmware updates
- Debugging on target

### game

- Frame budget
- Entity and component systems
- Game loop and determinism
- Networking
- Asset pipeline
- Audio
- Performance and profiling
- Testing and tooling

### browser-extension

- Manifest discipline
- Service worker
- Content scripts
- Message passing
- Storage
- UI
- Publishing

### desktop

- Process architecture
- Security
- File system
- Native integration
- Updates
- Performance
- Platform conventions

## Verification

After receiving the file from the AI, verify:

1. Every item in the master prompt's self-audit checklist.
2. Every item in the `Delivery-Specific Self-Audit` below.
3. The file is between 250 and 400 lines.
4. The file does not repeat rules from the attached sibling files.

If any item fails, request a revision from the AI rather than saving
a weak file.

## Delivery-Specific Self-Audit

Before saving the generated file, verify every item:

Contracts:
- [ ] A section titled "Delivery Contracts" or equivalent exists
- [ ] The contracts reflect the delivery type's operational shape
- [ ] Other sections enforce the contracts

Boundaries:
- [ ] The opening paragraph states what the file does NOT cover
- [ ] References to sibling files are present
- [ ] No rule belongs to another layer

Rationale Discipline:
- [ ] Every rule has a one-line rationale
- [ ] The rationale explains why, not just what

Anti-Patterns:
- [ ] The Anti-Patterns section has at least 25 items
- [ ] Each item has a short title
- [ ] At least 15 items have a BAD/GOOD code pair

Code Examples:
- [ ] At least 20 rules in the file have BAD/GOOD code pairs
- [ ] Code blocks use a language tag
- [ ] Names are realistic
- [ ] Examples are 5-15 lines

Structural:
- [ ] Frontmatter is complete
- [ ] Opening paragraph is 3-5 lines
- [ ] At least 13 sections total
- [ ] Response to Violation section matches the fixed template
- [ ] Entire file is in English
- [ ] No emoji

Non-Duplication:
- [ ] No rule from Universal is repeated
- [ ] No rule from the attached sibling files is repeated
- [ ] No framework-specific rule is present
- [ ] No language-specific rule is present
- [ ] References to other files have one-line summaries

If any item fails, ask the AI to revise the specific section. Do not
save a file that fails the self-audit.

## Common Failures

The following failures occur frequently when generating delivery
files. Use this table during review.

| Failure | How to spot it | Fix |
|---|---|---|
| Framework bleed | Mentions React, Django, Express | Move to framework file |
| Language bleed | Mentions `any`, `unwrap`, `Option` | Move to language file |
| Concern bleed | Repeats security, accessibility, performance rules | Reference the concern file |
| Universal bleed | Includes "no TODO", "declare assumptions" | Delete; they are in Universal |
| No contracts section | Missing "Delivery Contracts" heading | Request the section |
| Missing rationale | Rules say "do not" without "because" | Request rationale |
| Too few anti-patterns | Under 25 items | Request more |
| Shallow code examples | Under 20 BAD/GOOD pairs | Request concrete cases |
| Over-length | Over 400 lines | Split or trim |
| Overly generic | Rules apply to any delivery type | Move to Universal or delete |

## After the File Is Accepted

1. Save to `prompts/domains/delivery/02-<name>-anti-slop.md`.
2. Update `prompts/README.md` to include the new file in the
   delivery list.
3. If the delivery type has a dominant language, confirm the
   language file exists.
4. If the delivery type has a dominant framework, confirm the
   framework file exists or generate it next.

## Time Budget

Generating a delivery file with a frontier model takes 4-7 minutes
(delivery files are the longest domain files because of the
anti-pattern count). Review takes 10-15 minutes with the self-audit
checklist. If review takes longer than 20 minutes, the master
prompt likely needs refinement for future delivery files.

## Reference Example

The example in `prompts/_send-packages/example-svelte/` shows the
workflow for a framework file. The same workflow applies to
delivery files, with the additional `Delivery-Specific
Requirements` block inserted into the master prompt.
