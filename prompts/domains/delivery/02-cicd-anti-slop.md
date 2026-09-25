---
id: 02-cicd-anti-slop
title: "CI/CD Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: delivery
version: 1
---

# CI/CD Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
security anti-patterns, output format) are NOT repeated here.

This file covers rules specific to continuous integration and
continuous delivery: pipeline stages, caching, secret masking, test
selection, artifact handling, and deployment strategy. Application
deployment rules live in `domains/delivery/02-devops-anti-slop.md`.
Infrastructure rules live in `domains/delivery/02-infra-anti-slop.md`.

## 1. Stack Assumptions

This layer applies to pipelines in:

- GitHub Actions
- GitLab CI
- CircleCI
- Jenkins
- Buildkite
- Azure Pipelines
- Bitbucket Pipelines
- Drone

The principles are tool-agnostic. YAML syntax varies.

## 2. Pipeline Structure

### 2.1 Stages That Fail Fast

Order stages from fastest to slowest, and from most likely to fail to
least:

1. Lint
2. Type check
3. Unit tests
4. Build
5. Integration tests
6. End-to-end tests
7. Deploy

A failure in stage 1 stops the pipeline before stage 2 runs. Do not
waste five minutes on a build when the lint fails in 10 seconds.

### 2.2 Parallelism When It Is Free

Independent jobs run in parallel:

- Lint and type-check can run simultaneously.
- Unit tests split across shards.
- Multiple platforms (Linux, macOS, Windows) in parallel.

Parallelism has a cost (more runners, more minutes). Use it when the
wall-clock time saved matters.

### 2.3 One Job, One Purpose

BAD: A single `build-and-test-and-deploy` job.
GOOD: `lint`, `test`, `build`, `deploy` as separate jobs.

Separate jobs have separate logs, separate retry semantics, and
separate resource usage.

### 2.4 Dependencies Are Explicit

A deploy job depends on the build job. Do not rely on execution order
implicitly.

### 2.5 Deterministic

The same commit produces the same result. No random failures from
race conditions, timing, or external state.

Flaky tests are bugs. Do not retry them into passing.

## 3. Caching

### 3.1 Cache Dependencies

Cache the package manager's directory:

- npm: `~/.npm` or `node_modules`.
- pip: `~/.cache/pip` or the virtualenv.
- Go: `~/go/pkg/mod` and the build cache.
- Cargo: `~/.cargo/registry` and `target`.
- Maven: `~/.m2/repository`.

A cache miss costs minutes on every run.

### 3.2 Cache Keys Include the Lockfile Hash

```yaml
key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
```

Without the lockfile hash, the cache is stale after a dependency
change and produces incorrect builds.

### 3.3 Never Cache Build Artifacts Across Branches

A build artifact from `main` must not be reused on a feature branch
that changed source. Cache only inputs (dependencies), not outputs.

### 3.4 Cache Size Limits

Every CI provider has a cache size limit. Exceeding it silently evicts
older entries. Monitor cache size and prune.

## 4. Secrets in CI

### 4.1 Never Echo Secrets

BAD: `echo $API_KEY` in a step.
GOOD: Use the value directly in the tool that needs it.

Even "safe" commands like `env` print secrets.

### 4.2 Mask Logs

GitHub Actions, GitLab CI, and others mask registered secrets in logs.
This is the safety net, not the primary defense. Do not rely on it.

### 4.3 Scope Secrets Per Environment

- A secret for staging is not available in production jobs.
- A secret for one repository is not available to forks.
- A secret for one branch is not available on PRs from forks.

GitHub Actions: `pull_request` from a fork does not have access to
secrets by default. `pull_request_target` does; use it with extreme
care.

### 4.4 Rotate Secrets

A secret that has been in CI for two years has leaked somewhere. Set
a rotation schedule.

### 4.5 Short-Lived Credentials Over Static

Prefer OIDC-based authentication (GitHub Actions to AWS, GCP, Azure)
over static access keys. The credential is issued per job and expires.

### 4.6 No Secrets in Build Artifacts

A container image built in CI must not contain secrets. Use build args
sparingly, and never bake secrets into layers.

## 5. Testing in CI

### 5.1 Run the Same Tests Locally

A test that only passes in CI is a test with hidden dependencies. The
developer runs the same command locally.

### 5.2 Fail on Flaky Tests

A flaky test is worse than no test. It erodes trust in the suite.
Fix it or remove it. Do not add `retry: 3`.

### 5.3 Test Sharding

Large test suites split across parallel runners. Each shard runs a
subset. Merge coverage reports.

### 5.4 Coverage Without Obsession

Report coverage as a signal, not a gate. A coverage of 100% with
meaningless assertions is worse than 60% with real tests.

A decrease in coverage on a PR is worth a comment, not a block.

### 5.5 Test Data Isolation

Tests do not share state. Each test creates and cleans up its own
data. Parallel jobs use separate databases or schemas.

## 6. Build Artifacts

### 6.1 Build Once, Deploy Many

Build the artifact once (a binary, a container image, a bundle), tag
it with the commit SHA, and promote the same artifact through
environments.

BAD: Build again for staging and for production.
GOOD: One artifact, promoted.

### 6.2 Immutable Artifacts

Once published, an artifact is never overwritten. A version `1.4.2`
always refers to the same bytes.

### 6.3 Tag With Commit SHA

Every artifact is tagged with the commit SHA it was built from.
Debugging a production issue requires knowing the exact source.

### 6.4 Sign Artifacts

Container images and binaries are signed (Sigstore, Cosign). Consumers
verify the signature before running.

## 7. Deployment in CI

### 7.1 Deploy Is a Separate Job

Do not deploy in the same job that runs tests. The deploy job depends
on the test job and runs only on the target branch.

### 7.2 Environment Protection

Production deploys require:

- Manual approval (GitHub Environments, GitLab Protected Environments).
- Branch restrictions (only `main`).
- Reviewer requirements (one or two approvers).

### 7.3 Rollback Is a Job, Not a Manual Step

The pipeline can roll back to the previous version. A rollback is a
re-run of a previously successful deploy, not an ad-hoc `kubectl`
command.

### 7.4 Migration Order

Database migrations run before the new code. The old code must tolerate
the new schema. See `02-devops-anti-slop.md` section 4.5.

### 7.5 Post-Deploy Verification

After deploy, run a smoke test against the new version. If it fails,
roll back automatically.

### 7.6 Notify on Failure

A failed production deploy notifies the on-call channel. Silent
failures are the worst.

## 8. CI/CD-Specific Anti-Patterns

### 8.1 Secrets in YAML

BAD:
```yaml
- run: curl -H "Authorization: Bearer ghp_xxx" ...
```
GOOD:
```yaml
- run: curl -H "Authorization: Bearer ${{ secrets.TOKEN }}" ...
```

Even in a private repository, secrets in Git history are permanent.

### 8.2 Long-Running Pipelines

A pipeline that takes 30 minutes per commit is a pipeline developers
avoid. Profile the slowest jobs and fix them.

### 8.3 Rebuilding Dependencies Every Run

Covered in 3.1.

### 8.4 Cache Hit Rate Below 80%

A cache that misses more than it hits is misconfigured. Check the key
strategy.

### 8.5 No Timeout on Jobs

A hanging job consumes a runner for hours. Set a timeout on every
job.

### 8.6 Deploy From Feature Branches

BAD: Any branch can deploy to production.
GOOD: Only `main` (or a release branch) deploys to production.

### 8.7 No Rollback

Covered in 7.3.

### 8.8 Tests That Depend on Network

BAD: A unit test that calls `api.github.com`.
GOOD: A test with a mocked or local server.

External services fail; CI fails with them.

### 8.9 `npm install` Instead of `npm ci`

BAD: `npm install` in CI. It may update the lockfile.
GOOD: `npm ci` for a reproducible install. Same for `yarn --frozen-lockfile`, `pip install --require-hashes`, `go mod download`.

### 8.10 Ignoring Exit Codes

BAD: `command || true` to make a failing step pass.
GOOD: Let it fail, or handle the error explicitly.

### 8.11 Running Everything on Every Commit

BAD: A 40-minute end-to-end suite on every push.
GOOD: Unit tests on every push; E2E on PR merge or a schedule.

### 8.12 No Cancellation of Stale Runs

A new push to a branch cancels the previous run. Otherwise, five
runners process five commits that are all outdated except the last.

### 8.13 Single Point of Failure

BAD: All pipelines depend on one self-hosted runner.
GOOD: Multiple runners, or a managed pool.

### 8.14 Deploy Without Approval

Covered in 7.2.

### 8.15 No Visibility

BAD: A pipeline with no status badge, no notifications, and no
dashboard.
GOOD: A status badge in the README, notifications on failure.

### 8.16 Reused Secrets Across Environments

BAD: The same `DATABASE_URL` in staging and production.
GOOD: Separate secrets per environment, with separate values.

### 8.17 Overly Broad Permissions

BAD: A CI job with `permissions: write-all`.
GOOD: `permissions: contents: read, packages: write` and only what is
needed.

### 8.18 Deploy Scripts in the Repository

BAD: A `deploy.sh` that everyone runs with different flags.
GOOD: A pipeline that is the single source of truth for how a project
is deployed.

### 8.19 Environment Variables in CI That Shadow Secrets

BAD: A workflow that sets `DATABASE_URL=localhost` in `env:` and
forgets the production override.
GOOD: Secrets set at the environment level, not the workflow level.

### 8.20 No Artifact Retention Policy

BAD: Artifacts kept forever.
GOOD: 30 days for test artifacts, 90 days for release artifacts,
longer for compliance.

### 8.21 Manual Steps in the Pipeline

BAD: "After the pipeline succeeds, SSH into the server and..."
GOOD: Every step is in the pipeline.

### 8.22 No Feedback on PR

BAD: The developer has to check the CI dashboard manually.
GOOD: A status check on the PR, a comment on failure.

### 8.23 Pipeline That Only Works on `main`

A pipeline that fails on feature branches is a pipeline that was not
designed for the workflow developers actually use.

### 8.24 Tests That Require a Specific Order

BAD: Test A populates a database that test B reads.
GOOD: Each test is independent.

### 8.25 No Cost Awareness

CI minutes cost money. A pipeline that runs 1,000 times per day for
a project with 5 developers is burning budget. Optimize.

## 9. Response to Violation

If a previous response violated a rule here:

```
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

No justification. No apology paragraph. Fix and move on.
