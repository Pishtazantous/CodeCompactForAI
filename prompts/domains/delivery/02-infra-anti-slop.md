---
id: 02-infra-anti-slop
title: "Infrastructure Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: delivery
version: 1
---
# Infrastructure Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules are not
repeated. Deployment execution belongs to the related DevOps layer.

## 1. Stack Assumptions

**1.1 Inventory the boundary.** Identify cloud, account, region, network,
identity provider, state backend, and supported tool versions.

**1.2 Review before change.** Read the existing modules, provider versions,
and remote-state convention before editing infrastructure code.

**1.3 Use the repository's module boundaries.** Keep network, compute,
storage, identity, and observability resources in their established files.

## 2. Domain Contracts

**2.1 State ownership is explicit.** Every resource names the stack, module,
backend, key, and lifecycle owner.

**2.2 Declarative intent is the source.** Remote changes must be represented
in code; ad hoc console fixes are temporary and must be reconciled.

**2.3 Drift is a signal.** Detect and explain drift before applying another
change. Never include unrelated drift in a feature diff.

**2.4 Secrets stay external.** State may reference secret identifiers, not
secret values.

**2.5 Idempotency is required.** Reapplying the same plan must converge to
the same intended resources without destructive replacement.

## 3. Domain-Specific Rules

**3.1 Pin provider and module versions.** Use the versions already supported
by the project; avoid unreviewed upgrades in a feature change.

**3.2 Use narrow, named state.** Select remote backends and locking behavior
appropriate to the team and environment.

**3.3 Import only proven state.** Review state before import and keep an
export for recovery when a migration changes ownership.

**3.4 Make replacements safe.** Set explicit create-before-destroy, retain,
and deletion policies where supported.

**3.5 Bind network identity explicitly.** Security groups, routes, endpoints,
and private access must follow the project network design.

**3.6 Encrypt and classify data.** Configure provider encryption and lifecycle
retention for storage, logs, snapshots, and backups.

**3.7 Validate inputs.** Enforce naming, region, size, quota, and policy
limits before expensive plan application.

**3.8 Review plans as code.** Inspect the generated plan for replacement,
deletion, policy, and public exposure changes.

**3.9 Document emergency access.** State how operators recover from lost
credentials, failed modules, or corrupted state without editing resources.

**3.25 Make policy checks explicit.** Naming, access, encryption, and retention rules are enforced by the existing policy system.

**3.26 Keep state portable.** A state migration records backend, locking, version, backup, and restore steps before ownership changes.

**3.27 Review blast radius.** A plan identifies public, destructive, privileged, and data-loss changes before approval.

**3.28 Verify local tooling.** Format, validate, plan, and policy checks pass with the repository's pinned tools before review.

**3.29 Exercise recovery paths.** Test failed apply, unavailable backend, lost lock, and restored state under a controlled environment.

**3.30 Review plan impact.** Identify replacement, deletion, public exposure, and privilege changes before apply.

**3.31 Keep state recoverable.** Back up, lock, version, and restore procedures are documented and tested.

**3.32 Verify observed state.** Confirm provider resources and policy after apply instead of trusting exit status alone.

## 4. Domain-Specific Anti-Patterns

### 4.1 Console-Only Repair

BAD:
```yaml
network_rule:
  action: allow
  source: 0.0.0.0/0
```

GOOD:
```yaml
network_rule:
  action: allow
  source: app_security_group.id
```

Desired state remains reviewable and repeatable.

### 4.2 Secret Value in State

BAD:
```terraform
db_password = "production-password"
```

GOOD:
```terraform
db_password = data.vault_secret.database.value
```

The state stores a reference while the provider handles the secret.

### 4.3 Destructive Drift Correction

BAD:
```bash
terraform apply -replace=db_instance
```

GOOD:
```bash
terraform plan -target=db_instance
```

Drift is inspected before a potentially destructive operation.

**3.10 Separate environments.** State keys, modules, and remote backends are isolated by environment and protected by the repository's access policy.

**3.11 Review generated plans.** A plan must be inspected for public endpoints, broad IAM, data destruction, and provider-default changes before approval.

**3.12 Make dependencies explicit.** Module versions, provider constraints, and bootstrap ordering are pinned and tested from a clean state.

**3.13 Protect state access.** Locking, versioning, and backup responsibilities are documented; no engineer needs broad console credentials for routine work.

**3.14 Validate quotas before apply.** Check region availability, object count, address space, and provider quotas for the complete plan.

**3.15 Test recovery.** Exercise module disable, failed apply, lost lock, and restored state procedures before relying on them during an incident.

**3.16 Review identity boundaries.** Service accounts, human roles, and workload identities have separate trust assumptions and review owners.

**3.17 Keep public exposure intentional.** Ingress, APIs, databases, and storage endpoints have explicit network policy and authentication decisions.

**3.18 Version provider configuration.** Pin required provider features and document the supported upgrade path separately from code changes.

**3.19 Protect backups.** Encrypt backups, test restore, record retention, and avoid copying secrets into an unclassified artifact.

**3.20 Tag resources consistently.** Use the repository's naming and ownership tags so cost, incident, and access review remain possible.

**3.21 Check output after apply.** Verify the observed resource state, not only the command exit status, before closing the change.

**3.22 Keep changes composable.** A module change has a reviewable plan boundary and does not depend on an unrelated resource replacement.

**3.23 Validate destructive intent.** Replacement, deletion, and public exposure changes require an explicit reason and approval path.

**3.24 Verify local equivalence.** Run the repository's formatter, policy, plan, and targeted checks before proposing an apply.

## 5. Response to Violation

If a prior response violated this layer, state the ownership, state, drift,
idempotency, or secret problem and provide the corrected declarative change.
Do not apply infrastructure changes or invent a provider result.
