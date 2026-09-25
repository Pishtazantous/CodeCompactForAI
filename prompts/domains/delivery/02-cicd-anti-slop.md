---
id: 02-cicd-anti-slop
title: "CI/CD Anti-Slop Layer"
lang: en
depends_on: ["_universal/00-style-guide.md", "_universal/00-master-anti-slop.md"]
category: domain
domain_type: delivery
version: 2
---

# CI/CD Anti-Slop Layer

This file defines behavioral contracts specific to continuous integration and continuous delivery pipelines. It sits in the delivery layer, below the universal anti-slop rules and above infrastructure-as-code or application deployment patterns. It covers pipeline stages, caching, secret masking, test selection, artifact handling, and deployment strategy. It does not cover application deployment rules (see `02-devops-anti-slop.md`) or infrastructure-as-code (see `02-infra-anti-slop.md`).

A CI/CD pipeline is the factory that produces production artifacts. Every stage, cache, and secret is a contract with the deployment process.

## Scope

This file applies to pipelines in GitHub Actions, GitLab CI, CircleCI, Jenkins, Buildkite, Azure Pipelines, Bitbucket Pipelines, and Drone. The principles are tool-agnostic. The examples use YAML syntax where illustrative.

## Rule Severity

Severity follows `_universal/00-style-guide.md`.

## Contracts

A CI/CD pipeline commits to six contracts. The table below maps each contract to the rules that enforce it.

| Contract | Description | Enforced By |
|---|---|---|
| Pipeline Structure | Stages fail fast, jobs are single-purpose, dependencies are explicit. | CI-001 to CI-005 |
| Caching Discipline | Dependencies are cached with lockfile-based keys, build outputs are not shared across branches. | CI-006 to CI-009 |
| Secret Management | Secrets are never echoed, masked, scoped per environment, and rotated. | CI-010 to CI-015 |
| Testing Discipline | Same tests run locally and in CI, flaky tests are eliminated, test data is isolated. | CI-016 to CI-020 |
| Artifact Management | Artifacts are built once, immutable, tagged with commit SHA, and signed. | CI-021 to CI-024 |
| Deployment Safety | Deployment is a separate job, environment-protected, with automated rollback and verification. | CI-025 to CI-030 |

## Pipeline Structure

### CI-001 — Fast-Fail Stage Ordering

**MUST**

Pipeline stages MUST be ordered from fastest to slowest, and from most likely to fail to least: lint, type check, unit tests, build, integration tests, end-to-end tests, deploy. A failure in an early stage MUST stop the pipeline before later stages run.

### CI-002 — Parallelism Cost Awareness

**SHOULD**

Independent jobs (lint and type-check, unit test shards, multiple platforms) SHOULD run in parallel. Parallelism has a cost (more runners, more minutes) and MUST be used when wall-clock time saved matters.

### CI-003 — Job Single Purpose

**MUST**

Every job MUST have a single purpose. Combined jobs (e.g., `build-and-test-and-deploy`) are prohibited. Separate jobs have separate logs, retry semantics, and resource usage.

Example (illustrative):

BAD: A single `build-and-test-and-deploy` job.
GOOD: `lint`, `test`, `build`, `deploy` as separate jobs.

### CI-004 — Explicit Job Dependencies

**MUST**

Job dependencies MUST be explicit. A deploy job MUST declare its dependency on the build job. Implicit reliance on execution order is prohibited.

### CI-005 — Deterministic Execution

**MUST**

The same commit MUST produce the same result. Random failures from race conditions, timing, or external state MUST NOT occur. Flaky tests are bugs and MUST NOT be retried into passing.

## Caching

### CI-006 — Dependency Caching

**MUST**

The package manager's directory MUST be cached (e.g., `~/.npm` or `node_modules` for npm, `~/.cache/pip` for pip, `~/go/pkg/mod` for Go, `~/.cargo/registry` and `target` for Cargo, `~/.m2/repository` for Maven). A cache miss costs minutes on every run.

### CI-007 — Cache Key Lockfile Hash

**MUST**

Cache keys MUST include the lockfile hash. Without the lockfile hash, the cache is stale after a dependency change and produces incorrect builds.

Example (illustrative, GitHub Actions):
```yaml
key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
```

### CI-008 — No Cross-Branch Artifact Caching

**MUST NOT**

Build artifacts MUST NOT be cached across branches. A build artifact from `main` MUST NOT be reused on a feature branch that changed source. Only inputs (dependencies) MUST be cached, not outputs.

### CI-009 — Cache Size Monitoring

**MUST**

Cache size MUST be monitored and pruned. Every CI provider has a cache size limit; exceeding it silently evicts older entries.

## Secrets in CI

### CI-010 — Secret Echo Prohibition

**MUST NOT**

Secrets MUST NEVER be echoed (e.g., `echo $API_KEY` in a step). Even "safe" commands like `env` print secrets. The value MUST be used directly in the tool that needs it.

### CI-011 — Log Masking Awareness

**MUST**

Registered secrets MUST be masked in logs by the CI provider (GitHub Actions, GitLab CI, etc.). Log masking is the safety net, not the primary defense, and MUST NOT be relied upon exclusively.

### CI-012 — Per-Environment Secret Scoping

**MUST**

Secrets MUST be scoped per environment, repository, and branch:

- A staging secret MUST NOT be available in production jobs.
- A repository secret MUST NOT be available to forks.
- A branch secret MUST NOT be available on PRs from forks.

The `pull_request` event from a fork does not have access to secrets by default. `pull_request_target` does and MUST be used with extreme care.

### CI-013 — Secret Rotation Schedule

**MUST**

Every secret in CI MUST have a rotation schedule. A secret that has been in CI for two years has likely leaked somewhere.

### CI-014 — Short-Lived Credentials

**SHOULD**

OIDC-based authentication (GitHub Actions to AWS, GCP, Azure) SHOULD be preferred over static access keys. The credential is issued per job and expires.

### CI-015 — Artifact Secret Prohibition

**MUST NOT**

Container images and build artifacts MUST NOT contain secrets. Build args MUST be used sparingly, and secrets MUST NEVER be baked into layers.

## Testing in CI

### CI-016 — Local Test Parity

**MUST**

A test that only passes in CI is a test with hidden dependencies. The developer MUST run the same command locally and in CI.

### CI-017 — Flaky Test Elimination

**MUST NOT**

A flaky test erodes trust in the suite. It MUST be fixed or removed. Adding `retry: 3` to bypass flakiness is prohibited.

### CI-018 — Test Sharding

**SHOULD**

Large test suites SHOULD split across parallel runners (shards). Each shard runs a subset, and coverage reports MUST be merged.

### CI-019 — Coverage Signal Discipline

**SHOULD**

Coverage SHOULD be reported as a signal, not a gate. A coverage of 100% with meaningless assertions is worse than 60% with real tests. A decrease in coverage on a PR is worth a comment, not a block.

### CI-020 — Test Data Isolation

**MUST**

Tests MUST NOT share state. Each test MUST create and clean up its own data. Parallel jobs MUST use separate databases or schemas.

## Build Artifacts

### CI-021 — Build Once Deploy Many

**MUST**

The artifact MUST be built once (a binary, a container image, a bundle), tagged with the commit SHA, and promoted through environments. Building again for staging and production is prohibited.

### CI-022 — Immutable Artifacts

**MUST**

Once published, an artifact MUST NEVER be overwritten. A version `1.4.2` MUST always refer to the same bytes.

### CI-023 — Commit SHA Tagging

**MUST**

Every artifact MUST be tagged with the commit SHA it was built from. Debugging a production issue requires knowing the exact source.

### CI-024 — Artifact Signing

**SHOULD**

Container images and binaries SHOULD be signed (e.g., Sigstore, Cosign). Consumers MUST verify the signature before running.

## Deployment in CI

### CI-025 — Separate Deploy Job

**MUST**

Deployment MUST be a separate job. Deploy MUST NOT occur in the same job that runs tests. The deploy job MUST depend on the test job and MUST run only on the target branch.

### CI-026 — Environment Protection

**MUST**

Production deploys MUST require:

- Manual approval (GitHub Environments, GitLab Protected Environments).
- Branch restrictions (only `main`).
- Reviewer requirements (one or two approvers).

### CI-027 — Automated Rollback

**MUST**

The pipeline MUST be able to roll back to the previous version. A rollback MUST be a re-run of a previously successful deploy, not an ad-hoc `kubectl` command.

### CI-028 — Migration Order

**MUST**

Database migrations MUST run before the new code. The old code MUST tolerate the new schema. See `02-devops-anti-slop.md` for deployment migration discipline.

### CI-029 — Post-Deploy Verification

**MUST**

After deployment, a smoke test MUST run against the new version. If it fails, the pipeline MUST automatically roll back.

### CI-030 — Failure Notification

**MUST**

A failed production deploy MUST notify the on-call channel. Silent failures are prohibited.

## AI-Specific CI/CD Discipline

### CI-050 — Pipeline Syntax Verification

**MUST**

Before generating or modifying a CI/CD configuration file, the assistant MUST verify that the syntax, stage names, and action references are valid for the target CI provider and version. Invented action names or syntax produce pipeline failures that are invisible until runtime.

See MAS-036 in `_universal/00-master-anti-slop.md`.

### CI-051 — Action and Plugin Verification

**MUST**

Before using a third-party action or plugin (e.g., `actions/checkout@v4`), the assistant MUST verify the action exists at the specified version. Invented actions or versions cause pipeline failures and supply chain risks.

See MAS-036 in `_universal/00-master-anti-slop.md`.

### CI-052 — Existing Pipeline Discovery

**MUST**

Before creating a new pipeline job or stage, the assistant MUST search the project's existing CI configuration for an equivalent job. Inventing parallel jobs for the same purpose creates maintenance burden and inconsistent outputs.

See MAS-035 in `_universal/00-master-anti-slop.md`.

## Anti-Patterns

### CI-031 — Secrets in YAML

**MUST NOT**

Secrets MUST NEVER be hardcoded in YAML files. Even in a private repository, secrets in Git history are permanent.

Example (illustrative, YAML):

BAD:
```yaml
- run: curl -H "Authorization: Bearer ghp_xxx" ...
```

GOOD:
```yaml
- run: curl -H "Authorization: Bearer ${{ secrets.TOKEN }}" ...
```

### CI-032 — Long-Running Pipeline

**SHOULD NOT**

A pipeline that takes 30 minutes per commit is a pipeline developers avoid. The slowest jobs SHOULD be profiled and optimized.

### CI-033 — Low Cache Hit Rate

**MUST NOT**

A cache that misses more than it hits (below 80%) is misconfigured. The key strategy MUST be reviewed and fixed.

### CI-034 — Missing Job Timeout

**MUST**

Every job MUST have a timeout. A hanging job consumes a runner for hours.

### CI-035 — Feature Branch Production Deploy

**MUST NOT**

Production deployment from feature branches is prohibited. Only `main` (or a release branch) MUST deploy to production.

### CI-036 — Network-Dependent Tests

**MUST NOT**

Unit tests MUST NOT call external services (e.g., `api.github.com`). Tests MUST use mocked or local servers. External services fail, and CI fails with them.

### CI-037 — Non-Reproducible Install

**MUST NOT**

Non-reproducible install commands MUST NOT be used in CI. `npm ci`, `yarn --frozen-lockfile`, `pip install --require-hashes`, and `go mod download` MUST be used instead of `npm install` to prevent lockfile updates.

### CI-038 — Exit Code Suppression

**MUST NOT**

Suppressing exit codes (e.g., `command || true` to make a failing step pass) is prohibited. The command MUST fail, or the error MUST be handled explicitly.

### CI-039 — Over-Frequent Heavy Tests

**SHOULD NOT**

Running a heavy end-to-end suite on every push SHOULD be avoided. Unit tests MUST run on every push; E2E tests SHOULD run on PR merge or a schedule.

### CI-040 — Stale Run Continuation

**MUST**

A new push to a branch MUST cancel the previous run. Otherwise, multiple runners process outdated commits.

### CI-041 — Single Point of Failure

**MUST NOT**

All pipelines depending on a single self-hosted runner is a single point of failure and MUST NOT be used. Multiple runners or a managed pool MUST be used.

### CI-042 — Pipeline Visibility

**MUST**

Every pipeline MUST have visibility via a status badge in the README and notifications on failure. A pipeline with no visibility is a pipeline nobody watches.

### CI-043 — Cross-Environment Secret Reuse

**MUST NOT**

Reusing the same secret value (e.g., `DATABASE_URL`) across staging and production is prohibited. Separate secrets per environment MUST be used with separate values.

### CI-044 — Broad Permissions

**MUST NOT**

Overly broad permissions (e.g., `permissions: write-all`) are prohibited. Permissions MUST be scoped to only what is needed (e.g., `permissions: contents: read, packages: write`).

### CI-045 — Deploy Script Anti-Pattern

**MUST NOT**

Ad-hoc deploy scripts (e.g., `deploy.sh` run with different flags by different developers) are prohibited. The pipeline MUST be the single source of truth for how a project is deployed.

### CI-046 — Environment Variable Shadowing

**MUST NOT**

Environment variables in CI that shadow secrets (e.g., setting `DATABASE_URL=localhost` in `env:` and forgetting the production override) are prohibited. Secrets MUST be set at the environment level, not the workflow level.

### CI-047 — No Artifact Retention Policy

**MUST**

An artifact retention policy MUST be defined (e.g., 30 days for test artifacts, 90 days for release artifacts, longer for compliance). Artifacts MUST NOT be kept forever.

### CI-048 — Manual Pipeline Steps

**MUST NOT**

Manual steps in the pipeline (e.g., "After the pipeline succeeds, SSH into the server and...") are prohibited. Every step MUST be in the pipeline.

### CI-049 — Missing PR Feedback

**MUST**

Every pipeline MUST provide feedback on the PR via status checks and comments on failure. The developer MUST NOT have to check the CI dashboard manually.

## Response to Violation

When a rule in this file is violated, report:

Violation: CI-{NNN}
Reason: {one-line reason}
Correction: {smallest fix}

For multiple violations, report each rule ID separately.

Do not replace a technical correction with a generic explanation.