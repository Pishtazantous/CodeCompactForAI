---
id: 02-infra-anti-slop
title: "Infrastructure Anti-Slop Layer"
lang: en
depends_on: ["_universal/00-style-guide.md", "_universal/00-master-anti-slop.md"]
category: domain
domain_type: delivery
version: 2
---

# Infrastructure Anti-Slop Layer

This file defines behavioral contracts specific to infrastructure-as-code (IaC). It sits in the delivery layer, below the universal anti-slop rules and above application deployment or CI/CD pipeline patterns. It covers state management, drift, idempotency, plan review, module design, and the discipline of treating infrastructure changes as production changes. It applies to Terraform, Pulumi, CloudFormation, CDK, and their equivalents. It does not cover application-level deployment rules (see `02-devops-anti-slop.md`) or pipeline definitions (see `02-cicd-anti-slop.md`).

Infrastructure is the foundation of the runtime environment. Every configuration change is a production change.

## Scope

This file applies to infrastructure-as-code tools including Terraform, OpenTofu, Pulumi (TypeScript, Python, Go, C#), AWS CloudFormation, CDK, Google Cloud Deployment Manager, Azure Bicep, ARM templates, and Ansible. The principles are tool-agnostic. The examples use Terraform/HCL syntax where illustrative.

## Rule Severity

Severity follows `_universal/00-style-guide.md`.

## Contracts

Infrastructure-as-code commits to seven contracts. The table below maps each contract to the rules that enforce it.

| Contract | Description | Enforced By |
|---|---|---|
| State Integrity | State is remote, locked, encrypted, and separated by environment. | INF-001 to INF-005, INF-034 |
| Plan Discipline | Every change is planned, reviewed, and cost-checked before application. | INF-006 to INF-010, INF-039, INF-041 |
| Modularity | Infrastructure is composed of single-responsibility, versioned modules. | INF-011 to INF-015, INF-032, INF-040 |
| Idempotency | Applying the same configuration twice produces no changes. | INF-016 to INF-018 |
| Drift Management | Drift is detected regularly and reconciled through code, not ignored. | INF-019 to INF-022 |
| Security & Least Privilege | Networks, IAM, and storage follow least privilege and encryption by default. | INF-026 to INF-030, INF-037 |
| Secret Management | Secrets are never in code, state, or logs. | INF-003, INF-023 to INF-025 |

## State Management

### INF-001 — Remote State Requirement

**MUST**

State MUST NEVER be stored on a developer's laptop. It MUST live in a remote backend (e.g., S3 + DynamoDB lock, GCS, Terraform Cloud, Pulumi Cloud). Local state loses track of reality the moment two people work on the same stack.

### INF-002 — State Locking

**MUST**

The remote backend MUST support locking. Without locking, two concurrent `apply` runs corrupt the state file. Native tool locking or external locks (e.g., DynamoDB for S3) MUST be used.

### INF-003 — State Secrecy

**MUST NOT**

State files contain secrets (database passwords, private keys, API tokens). The backend bucket MUST be encrypted and access-controlled. State files MUST NEVER be committed to Git.

### INF-004 — Environment State Separation

**MUST**

Production, staging, and development MUST have separate state files, in separate backends or separate prefixes. An apply in one environment MUST NEVER touch another.

### INF-005 — State Mutation Discipline

**MUST NOT**

State MUST NOT be edited by hand using a text editor. Tool commands (e.g., `terraform state rm`, `mv`, `import`) MUST be used as escape hatches.

## Plan Before Apply

### INF-006 — Mandatory Plan Review

**MUST**

A plan (e.g., `terraform plan`) MUST be executed and reviewed before every `apply`. A change that was not planned is a change that was not reviewed.

### INF-007 — Plan Inspection

**MUST**

The plan output MUST be inspected carefully for:

- Resources marked for destruction (`-` or `-/+`).
- Resources marked for replacement (forces new resource).
- Unexpected changes to unrelated resources.
- Changes to IAM, security groups, or networking.

If the plan shows unintended changes, the apply MUST be stopped.

### INF-008 — Production Auto-Approve Prohibition

**MUST NOT**

Auto-approve flags (e.g., `terraform apply -auto-approve`) MUST NOT be used in production pipelines. A manual approval gate or an explicit non-interactive mode with human sign-off upstream MUST be used.

### INF-009 — Saved Plan Execution

**SHOULD**

For large changes, the plan SHOULD be saved (e.g., `-out=tfplan`) and the saved plan applied. This guarantees the applied change matches the reviewed change exactly.

### INF-010 — Cost Preview

**SHOULD**

Where available (e.g., Infracost, AWS Cost Explorer preview), the cost delta SHOULD be shown before applying. A "small" change can quintuple the cloud bill.

## Module Design

### INF-011 — Module Single Responsibility

**MUST**

A module MUST have one responsibility. A module that creates a VPC, an EKS cluster, a database, and an S3 bucket is four modules and MUST be split and composed.

### INF-012 — Explicit Module Inputs

**MUST**

Every module input MUST have a type, a description, and a validation rule where applicable. Defaults MUST only be provided when they are genuinely the common case.

### INF-013 — Minimal Module Outputs

**MUST**

Only what consumers actually need MUST be outputted. Internal resource IDs MUST NOT be exposed unless a consumer explicitly requires them.

### INF-014 — Module Version Pinning

**MUST**

Modules MUST be referenced by explicit version. `main` or `latest` is not a version.

Example (illustrative, HCL):
```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.1.2"
}
```

### INF-015 — Root Module Abstraction

**SHOULD**

The root module SHOULD call other modules and SHOULD NOT directly create resources. The exception is trivial one-resource stacks.

## Idempotency

### INF-016 — Idempotent Application

**MUST**

Running `apply` on an unchanged configuration MUST produce no changes. If it produces changes, the configuration is non-deterministic and MUST be fixed. Common causes include timestamps in tags, random IDs generated at apply time, or ordering dependent on parallel execution.

### INF-017 — Conditional Script Execution

**MUST NOT**

Scripts (e.g., `null_resource` with `local-exec`) MUST NOT always run on every apply. Triggers or marker files MUST be used if the script must run only once or on specific changes.

### INF-018 — Deterministic Resource Naming

**MUST NOT**

Resource names MUST come from inputs, not from functions that regenerate on every run (e.g., `timestamp()` or `random_id`). If a name must be unique, it MUST be derived from a stable identifier. Regenerating names breaks references and forces recreation.

## Drift Detection

### INF-019 — Scheduled Drift Detection

**MUST**

A regular (weekly or daily) `plan` against production MUST be scheduled to detect drift. Console changes made by humans constitute drift.

### INF-020 — Console Change Prohibition

**MUST NOT**

Production infrastructure MUST NOT be changed via the cloud provider's web console. All changes MUST go through code, PR, plan, and apply. Console changes are invisible to the state and cause conflicts on the next apply.

### INF-021 — Resource Import Discipline

**MUST**

A resource that exists but is not in state MUST be imported (e.g., `terraform import`). It MUST NOT be recreated, as recreation destroys the existing resource and its data.

### INF-022 — Drift Reconciliation

**MUST NOT**

When drift is detected, the configuration or the resource MUST be reconciled. Adding an `ignore_changes` block to hide the drift is prohibited. A growing list of `ignore_changes` blocks means the configuration no longer describes reality.

## Secrets

### INF-023 — Code Secret Prohibition

**MUST NOT**

Secrets MUST NEVER be hardcoded in code (e.g., `variable "password" { default = "..." }` or hardcoded resource attributes). A secret manager (Vault, AWS Secrets Manager), a data source that reads from the manager at apply time, or pipeline environment variables MUST be used.

### INF-024 — Sensitive Output Masking

**MUST**

Outputs and variables that carry secrets MUST be marked as sensitive (e.g., `sensitive = true` in Terraform, `pulumi.secret()` in Pulumi). This prevents the value from appearing in plan output and logs.

### INF-025 — Code-Driven Secret Rotation

**MUST**

Secret rotation MUST be a code change with a plan and a review. Manual console actions for rotation are prohibited.

## Network and Security

### INF-026 — Public Port Restriction

**MUST NOT**

Security groups MUST NOT allow `0.0.0.0/0` on non-public ports (e.g., 5432 for Postgres, 22 for SSH). Specific CIDRs, bastion hosts, or SSM Session Manager MUST be used. Only ports 80 and 443 of a public load balancer MAY accept traffic from the world.

### INF-027 — IAM Least Privilege

**MUST**

IAM roles MUST have only the actions they need. Resource lists MUST be specific (e.g., a bucket ARN, not `"*"`). Wildcards MUST require a comment explaining why.

### INF-028 — Default Encryption

**MUST**

Encryption MUST be enabled by default for all storage and databases (e.g., S3 server-side encryption, RDS storage and backups, EBS volumes). Secrets MUST be encrypted at rest. If it requires a flag, the flag MUST be set.

### INF-029 — Audit and Flow Logging

**MUST**

Cloud audit logs (CloudTrail, Cloud Audit Logs, Activity Log) MUST be enabled. VPC flow logs MUST be enabled for network traffic. S3 access logging MUST be enabled where the bucket holds sensitive data.

### INF-030 — S3 Public Access Blocks

**MUST**

S3 buckets MUST have `block_public_acls`, `block_public_policy`, `ignore_public_acls`, and `restrict_public_buckets` enabled, unless the bucket is explicitly configured as a public website.

## AI-Specific Infrastructure Discipline

### INF-042 — Provider API Verification

**MUST**

Before using a cloud provider resource or attribute, the assistant MUST verify it exists in the pinned version of the provider. Provider APIs change between major versions. Invented attributes produce plan-time errors or silent misconfigurations.

See MAS-036 in `_universal/00-master-anti-slop.md`.

### INF-043 — Existing Module Discovery

**MUST**

Before writing a new infrastructure module or cloud architecture pattern, the assistant MUST search the project's registry or existing codebase for an equivalent module. Inventing parallel VPC or database modules creates configuration drift and duplicated maintenance.

See MAS-035 in `_universal/00-master-anti-slop.md`.

### INF-044 — Infrastructure Restraint

**SHOULD**

The assistant SHOULD NOT introduce complex multi-cloud setups, obscure managed services, or advanced networking topologies unless the project already uses them and the scale explicitly requires them.

See MAS-038 in `_universal/00-master-anti-slop.md`.

## Anti-Patterns

### INF-031 — State Splitting by Lifecycle

**MUST**

Monolithic state files that manage networking, databases, and applications together MUST NOT be used. State MUST be split by lifecycle (e.g., networking changes rarely, applications change daily) to prevent a failed plan from blocking all work.

### INF-032 — Configuration DRY Principle

**MUST NOT**

Copy-pasted configuration blocks across environments MUST NOT be used. A bugfix in one will be missed in the others. Modules MUST be extracted and reused.

### INF-033 — Dynamic Account and Region Resolution

**MUST NOT**

Account IDs and regions MUST NOT be hardcoded in modules. Data sources or variables set per environment MUST be used.

### INF-034 — State Backend Versioning and Backup

**MUST**

Even with remote state, the backend MUST have versioning and backups enabled. A corrupted state with no history is unrecoverable.

### INF-035 — Targeted Apply Restriction

**MUST NOT**

Targeted applies (e.g., `terraform apply -target=...`) MUST NOT be used as a regular workflow. They are escape hatches for emergencies. Using them habitually produces state that diverges from the configuration.

### INF-036 — Implicit Dependency Preference

**SHOULD**

Explicit `depends_on` SHOULD NOT be used as a crutch. When it appears frequently, the resource graph is not expressing dependencies naturally and the configuration SHOULD be investigated and refactored.

### INF-037 — Credential Isolation

**MUST NOT**

Credentials MUST NOT be shared across actors. CI, developers, and production MUST use separate IAM roles with least privilege.

### INF-038 — Provider Version Pinning

**MUST**

Provider versions MUST be pinned in a `required_providers` block. An unpinned provider can change behavior between applies.

Example (illustrative, HCL):
```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
```

### INF-039 — Plan Warning Inspection

**MUST**

Plan warnings and in-place update notices (e.g., `~ update in-place` on an RDS instance) MUST be read and understood. They may indicate an impending restart or downtime. The plan text MUST be read, not just its exit code.

### INF-040 — Module Documentation

**MUST**

Every module MUST have a README documenting its purpose, inputs, outputs, and examples. A module without documentation is a module that only its author understands.

### INF-041 — TOCTOU Plan Freshness

**MUST**

For critical infrastructure, the plan MUST be re-run immediately before apply to prevent Time-of-Check to Time-of-Use (TOCTOU) gaps. A plan run hours ago will not see changes made in the interim.

## Response to Violation

When a rule in this file is violated, report:

Violation: INF-{NNN}
Reason: {one-line reason}
Correction: {smallest fix}

For multiple violations, report each rule ID separately.

Do not replace a technical correction with a generic explanation.