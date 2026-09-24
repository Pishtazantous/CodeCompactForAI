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

Layered under `_universal/00-master-anti-slop.md`. Universal rules are not
repeated. Deployment behavior is coordinated with the DevOps layer.

## 1. Stack Assumptions

**1.1 Identify the authoritative pipeline.** Confirm the repository, CI
provider, branch protections, required checks, artifact registry, and deploy
environment.

**1.2 Preserve existing jobs.** Reuse the current runner image, package
manager, test commands, and release conventions unless a task requires a
documented change.

**1.3 Treat CI as a security boundary.** Untrusted forks, pull requests,
build scripts, logs, and caches may contain hostile input.

## 2. Domain Contracts

**2.1 Stages have clear gates.** Install, verify, package, publish, and deploy
have explicit inputs and conditions. A failed required gate stops promotion.

**2.2 Builds are reproducible.** Pin lockfiles, toolchains, and base images;
publish immutable artifacts and their source revision.

**2.3 Secrets are scoped and masked.** Use the provider's secret store,
minimize exposure, and never print secret values or untrusted environment
dumps.

**2.4 Rollback is available.** Keep the previous artifact and a deployment
mechanism that can restore it without rebuilding an unknown source.

## 3. Domain-Specific Rules

**3.1 Cache narrowly.** Key caches by lockfile, toolchain, and compatible OS
or architecture. Never cache credentials, mutable test output, or secrets.

**3.2 Protect untrusted pull requests.** Do not expose write-capable secrets
or privileged runners to fork jobs. Restrict network and package publishing
permissions.

**3.3 Pin action and image versions.** Use reviewed versions appropriate to
the repository; do not track an untrusted moving tag for security-critical
steps.

**3.4 Fail closed on missing tools.** Verify required runtimes and versions
before running the build rather than installing arbitrary latest tools.

**3.5 Keep logs useful.** Log stage, revision, duration, and test counts while
redacting tokens, cookies, environment values, and private artifacts.

**3.6 Use least privilege.** Give jobs only the registry, cloud, and package
permissions required for their stage.

**3.7 Separate verification from publication.** A test job cannot publish a
release artifact that has not passed the required checks.

**3.8 Make retries safe.** Re-running a job may republish an immutable tag or
retry a migration; define deduplication and recovery.

**3.9 Verify release artifacts.** Check checksum or digest, provenance, and
the deployed revision before promotion.

**3.10 Record rollback ownership.** Name who may deploy, who may approve,
and which command restores the previous release.

**3.25 Keep promotion artifacts immutable.** The deploy job consumes the exact digest produced by the verified build job.

**3.26 Record gate evidence.** Store safe revision, test summary, digest, and approval data with a defined retention period.

**3.27 Restrict runner access.** Untrusted jobs cannot read production secrets, privileged metadata, or mutable release credentials.

**3.28 Make retries idempotent.** Re-running publication or migration steps uses a deduplication key and an explicit recovery result.

**3.29 Test release recovery.** Exercise failed gates, expired credentials, registry outage, cancellation, and rollback with the real permissions model.

**3.30 Gate every promotion.** Required checks, approvals, and environment policy are evaluated before deployment.

**3.31 Verify the artifact.** Compare source revision, digest, provenance, and tested output at each boundary.

**3.32 Preserve rollback evidence.** The previous release and the identity that restores it remain available.

**3.33 Protect release evidence.** Keep revision, digest, gate result, approval, and rollback target without secrets.

## 4. Domain-Specific Anti-Patterns

### 4.1 Secret Printed by Debug Flag

BAD:
```yaml
run: env | tee build.env
```

GOOD:
```yaml
run: node scripts/build.js
```

Logs do not dump the entire environment.

### 4.2 Shared Cache Across Branches

BAD:
```yaml
cache: key: build
```

GOOD:
```yaml
cache: key: build-${{ hashFiles('package-lock.json') }}
```

A cache hit cannot hide stale or hostile source output.

### 4.3 Deploy Before Required Gate

BAD:
```yaml
needs: build
```

GOOD:
```yaml
needs: [build, test, security-scan]
```

Promotion waits for every required verification.

**3.11 Constrain network access.** Permit only required registries and APIs in build jobs; deny production networks from untrusted test code.

**3.12 Validate artifacts before deploy.** Compare the artifact digest, provenance, and source revision at the deployment boundary.

**3.13 Handle cancellation safely.** A cancelled job stops new side effects, preserves diagnostics, and does not leave a partially published release marked successful.

**3.14 Use explicit environments.** Production deployment requires the configured approval, identity, and branch or tag policy.

**3.15 Retain release history.** Store enough metadata to identify what was tested, published, deployed, and rolled back without retaining secrets.

**3.16 Keep job identities narrow.** Fork jobs, maintenance jobs, and release jobs have different token scopes and network policy.

**3.17 Check dependency provenance.** Pin lockfiles and verify the source of external actions, packages, and build images.

**3.18 Preserve failed-job evidence.** Upload only safe test reports, logs, and diagnostics with clear retention rules.

**3.19 Avoid mutable environments.** A release promotion consumes a verified artifact and does not rebuild from a moving branch.

**3.20 Verify rollback permissions.** The rollback identity and target are available even when the primary deploy credential is unavailable.

**3.21 Test pipeline failure.** Simulate missing tools, expired secrets, dependency outage, cache miss, and interrupted publication.

**3.22 Keep promotion auditable.** Every promotion records the source revision, artifact digest, approver policy, and target environment.

**3.23 Preserve reproducibility.** The release can be rebuilt or verified from the recorded source, lockfile, toolchain, and build inputs.

**3.24 Treat a failed gate as release-blocking.** Do not weaken a required check to make a pipeline green without a reviewed decision.

## 5. Response to Violation

If a prior response violated this layer, identify the stage, cache, secret,
permission, or rollback defect and show the corrected workflow. Do not report
a pipeline as passing without evidence from an actual run.
