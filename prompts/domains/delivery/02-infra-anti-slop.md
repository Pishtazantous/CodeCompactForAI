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

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
security anti-patterns, output format) are NOT repeated here.

This file covers rules specific to infrastructure-as-code: state
management, drift, idempotency, plan review, and the discipline of
treating infrastructure changes as production changes. It applies to
Terraform, Pulumi, CloudFormation, CDK, and their equivalents.
Application-level deployment rules live in
`domains/delivery/02-devops-anti-slop.md`. Pipeline rules live in
`domains/delivery/02-cicd-anti-slop.md`.

## 1. Stack Assumptions

This layer applies to:

- Terraform and OpenTofu
- Pulumi (TypeScript, Python, Go, C#)
- AWS CloudFormation and CDK
- Google Cloud Deployment Manager
- Azure Bicep and ARM templates
- Ansible and similar configuration tools

The principles are tool-agnostic. The syntax varies.

## 2. State Management

### 2.1 Remote State

State is never stored on a developer's laptop. It lives in a remote
backend:

- Terraform: S3 + DynamoDB lock, GCS, Terraform Cloud.
- Pulumi: Pulumi Cloud or a self-hosted backend.
- CloudFormation: managed by AWS automatically.

Local state loses track of reality the moment two people work on the
same stack.

### 2.2 State Locking

The remote backend supports locking. Without locking, two concurrent
`apply` runs corrupt the state file.

For Terraform + S3, use DynamoDB for locks. For other backends, use
the tool's native locking.

### 2.3 State Is Sensitive

State files contain secrets (database passwords, private keys, API
tokens). The backend bucket is encrypted and access-controlled.
Never commit state files to Git.

### 2.4 Separate State Per Environment

Production, staging, and development have separate state files, in
separate backends (or separate prefixes). A `terraform apply` in one
environment must never touch another.

### 2.5 Never Edit State by Hand

`terraform state rm`, `mv`, `import` are the escape hatches. Direct
file edits are not. If the state is wrong, use the tool's commands,
not a text editor.

## 3. Plan Before Apply

### 3.1 Always Review the Plan

`terraform plan` (or the equivalent) before every `apply`. A change
that was not planned is a change that was not reviewed.

### 3.2 Read the Plan Carefully

Look for:

- Resources marked for destruction (`-` or `-/+`).
- Resources marked for replacement (forces new resource).
- Unexpected changes to unrelated resources.
- Changes to IAM, security groups, or networking.

If the plan shows something you did not intend, stop. Do not apply.

### 3.3 No Auto-Approve in Production

BAD: `terraform apply -auto-approve` in a production pipeline.
GOOD: A manual approval gate, or an explicit non-interactive mode
with human sign-off upstream.

### 3.4 Saved Plans

For large changes, save the plan (`-out=tfplan`) and apply the saved
plan. This guarantees the applied change matches the reviewed change.

### 3.5 Cost Preview

Where available (Infracost, AWS Cost Explorer preview), show the cost
delta before applying. A "small" change can quintuple the bill.

## 4. Module Design

### 4.1 One Module, One Responsibility

A module that creates a VPC, an EKS cluster, a database, and an
S3 bucket is four modules. Compose them.

### 4.2 Inputs Are Explicit

Every module input has:

- A type.
- A description.
- A validation rule where applicable.
- A default only when the default is genuinely the common case.

### 4.3 Outputs Are the Public API

Only output what consumers actually need. Do not expose internal
resource IDs unless a consumer requires them.

### 4.4 Versioned Modules

Reference modules by version:

```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.1.2"
}
```

`main` or `latest` is not a version.

### 4.5 No Resources at the Root

The root module calls modules. It does not directly create resources.
The exception is trivial one-resource stacks, and even then a module
is cleaner.

## 5. Idempotency

### 5.1 Apply Twice, Same Result

Running `apply` on an unchanged configuration produces no changes.
If it does, the configuration is non-deterministic.

Common causes:

- Timestamps in resource names or tags.
- Random IDs generated at apply time.
- Ordering that depends on parallel execution.

### 5.2 No Scripts That Always Run

A `null_resource` with a `local-exec` that always fires will run on
every apply. Use `triggers` or a marker file if the script must run
once.

### 5.3 Deterministic Naming

Resource names come from inputs, not from `timestamp()` or
`random_id` that regenerates. If a name must be unique, derive it
from a stable identifier.

## 6. Drift Detection

### 6.1 Plan Regularly

A weekly or daily `plan` against production detects drift. A console
change made by a person is drift.

### 6.2 No Console Changes in Production

BAD: An engineer resizes an instance in the console "just this once".
GOOD: The change goes through code, PR, plan, apply.

Console changes are invisible to the state, and the next apply
reverts them or produces a conflict.

### 6.3 Import, Do Not Recreate

A resource that exists but is not in state is imported:

```bash
terraform import aws_s3_bucket.example my-bucket-name
```

Recreating it destroys the existing resource and any data.

### 6.4 Reconcile, Do Not Ignore

When drift is detected, reconcile the configuration or the resource.
Do not add an `ignore_changes` block to hide the drift.

## 7. Secrets

### 7.1 No Secrets in Code

Never `variable "password" { default = "..." }`. Never a resource
attribute with a hardcoded secret.

Use:

- A secret manager (Vault, AWS Secrets Manager, GCP Secret Manager).
- A data source that reads from the manager at apply time.
- Environment variables for the pipeline.

### 7.2 Mark Sensitive Outputs

Terraform: `sensitive = true` on outputs and variables that carry
secrets. Pulumi: `pulumi.secret()` on values.

This prevents the value from appearing in plan output and logs.

### 7.3 Rotate Secrets Through Code

A secret rotation is a code change with a plan and a review, not a
manual console action.

## 8. Network and Security

### 8.1 No `0.0.0.0/0` on Non-Public Ports

BAD: A security group with `cidr_blocks = ["0.0.0.0/0"]` on port
5432 (Postgres) or 22 (SSH).
GOOD: A specific CIDR or a bastion host or SSM Session Manager.

Only port 80 and 443 of a public load balancer accept traffic from
the world.

### 8.2 Least Privilege IAM

- A role has only the actions it needs.
- The resource list is specific (a bucket ARN, not `"*"`).
- Wildcards require a comment explaining why.

### 8.3 Encryption by Default

- S3 buckets: server-side encryption enabled.
- RDS: storage encrypted, backups encrypted.
- EBS volumes: encrypted.
- Secrets: encrypted at rest.

Encryption is not optional. If it requires a flag, set the flag.

### 8.4 Logging and Audit

- CloudTrail (AWS), Cloud Audit Logs (GCP), Activity Log (Azure)
  enabled.
- VPC flow logs for network traffic.
- S3 access logging where the bucket holds sensitive data.

### 8.5 Public Access Blocks

S3 buckets: `block_public_acls`, `block_public_policy`,
`ignore_public_acls`, `restrict_public_buckets` all enabled unless
the bucket is explicitly a public website.

## 9. Infrastructure-Specific Anti-Patterns

### 9.1 Local State

Covered in 2.1. The single most common infrastructure mistake.

### 9.2 No Locking

Covered in 2.2.

### 9.3 `ignore_changes` Everywhere

A growing list of `ignore_changes` blocks means the configuration no
longer describes reality. Remove the block, reconcile the resource.

### 9.4 Console-Driven Infrastructure

Covered in 6.2.

### 9.5 Monolithic State

A single state file that manages VPC, EKS, IAM, and applications.
Any change touches everything, and a failed plan blocks all work.

Split by lifecycle: networking changes rarely, applications change
daily. Separate states.

### 9.6 Copy-Pasted Configuration

The same 200-line VPC block in four environments. A bugfix in one is
missed in the others. Extract a module.

### 9.7 `random_id` for Resource Names

BAD: `name = "app-${random_id.suffix.hex}"`.
GOOD: A stable name derived from the environment and purpose.

`random_id` regenerates when the resource is recreated, changing the
name and breaking references.

### 9.8 Hardcoded Account IDs and Regions

BAD: `account_id = "123456789012"` in every module.
GOOD: A data source or a variable set per environment.

### 9.9 No State Backup

Even with remote state, the backend needs versioning and backups. A
corrupted state with no history is unrecoverable.

### 9.10 Apply Without Plan

Covered in 3.1.

### 9.11 `-target` as a Habit

`terraform apply -target=...` is an escape hatch for emergencies. As a
workflow, it produces state that diverges from the configuration.

### 9.12 Depends_on as a Crutch

Explicit `depends_on` is sometimes necessary. When it appears
frequently, the resource graph is not expressing dependencies
naturally. Investigate.

### 9.13 No Environments

BAD: One stack that serves as both staging and production.
GOOD: Separate environments, separate state, separate credentials.

### 9.14 Shared Credentials

BAD: One AWS access key used by CI, developers, and production.
GOOD: Separate IAM roles per actor, with least privilege.

### 9.15 Provider Version Unpinned

BAD: No `required_providers` block.
GOOD:
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

An unpinned provider can change behavior between applies.

### 9.16 Ignoring the Plan Warning

A plan that says `~ update in-place` on an RDS instance may mean a
restart. Read the plan, not just its exit code.

### 9.17 No Documentation

A module with no README is a module that only its author understands.
Every module has a README with purpose, inputs, outputs, and examples.

### 9.18 Time-of-Check to Time-of-Use Gaps

A plan run at 10:00 and an apply at 14:00 will not see changes made
in between. For critical infrastructure, re-plan immediately before
apply.

## 10. Response to Violation

If a previous response violated a rule here:

```
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

No justification. No apology paragraph. Fix and move on.
