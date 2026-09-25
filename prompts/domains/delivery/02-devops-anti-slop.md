---
id: 02-devops-anti-slop
title: "DevOps Anti-Slop Layer"
lang: en
depends_on: ["_universal/00-style-guide.md", "_universal/00-master-anti-slop.md"]
category: domain
domain_type: delivery
version: 2
---

# DevOps Anti-Slop Layer

This file defines behavioral contracts specific to deployment, containerization, orchestration, and operational concerns. It sits in the delivery layer, below the universal anti-slop rules and above infrastructure-as-code or CI/CD pipeline patterns. It covers Docker, Kubernetes, deployment strategy, secrets management, health checks, observability, and rollback. It does not cover infrastructure-as-code tools like Terraform or Pulumi (see `02-infra-anti-slop.md`), CI/CD pipeline definitions (see `02-cicd-anti-slop.md`), or application-level code (see other delivery files).

A deployment is the bridge between code and production. Every configuration, image, and manifest is a contract with the runtime environment.

## Scope

This file applies to applications deployed as containers (Docker, Podman), orchestrated with Kubernetes, Docker Swarm, or managed platforms (ECS, Cloud Run, Fly.io), traditional deployments (systemd, PM2, bare metal), and serverless deployments (Lambda, Cloud Functions). The rules below are the minimum for any deployment. The examples use Docker and Kubernetes syntax where illustrative.

## Rule Severity

Severity follows `_universal/00-style-guide.md`.

## Contracts

A DevOps pipeline and runtime environment commit to six contracts. The table below maps each contract to the rules that enforce it.

| Contract | Description | Enforced By |
|---|---|---|
| Container Discipline | Containers are isolated, minimal, and run as non-root. | OPS-001 to OPS-009 |
| Orchestration Safety | Resources are bounded, probes are separated, and rollouts are safe. | OPS-010 to OPS-016 |
| Deployment Predictability | Artifacts are immutable, rollouts are controlled, and rollbacks are documented. | OPS-017 to OPS-022 |
| Secret Management | Secrets are never in code, images, or logs. | OPS-023 to OPS-026, OPS-029 |
| Observability | Logs are structured, metrics are collected, and alerts are actionable. | OPS-027 to OPS-032 |
| Recovery | Backups exist, are tested, and disaster recovery is documented. | OPS-033 to OPS-037 |

## Containers

### OPS-001 — Single Process Container

**MUST**

A container MUST run one process. Combining multiple processes (e.g., nginx + app + cron) in a single container is prohibited. If multiple processes are needed, they MUST be separate containers or separate services.

### OPS-002 — Multi-Stage Build Discipline

**SHOULD**

Multi-stage builds SHOULD be used to separate the build environment (compiler, dev dependencies) from the runtime environment (artifact only). For trivial scripts (e.g., 10 lines), a single stage is acceptable. Over-engineering MUST be avoided.

Example (illustrative, Dockerfile):
```dockerfile
FROM node:20 AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-slim
WORKDIR /app
COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules
CMD ["node", "dist/main.js"]
```

### OPS-003 — Base Image Pinning

**MUST**

Base image versions MUST be pinned to a specific version and tag (e.g., `node:20.11.1-alpine`). Using `latest` or unpinned tags is prohibited, as they move unpredictably and break reproducibility.

### OPS-004 — Non-Root User

**MUST**

Containers MUST NOT run as root. A dedicated non-root user MUST be created and used via the `USER` directive. Running as root inside a container is a privilege escalation risk.

Example (illustrative, Dockerfile):
```dockerfile
RUN addgroup --system app && adduser --system app --ingroup app
USER app
```

### OPS-005 — Dockerignore Requirement

**MUST**

Every project MUST have a `.dockerignore` file that excludes `.git`, `node_modules`, `dist` (if built inside), `.env`, test files, and local data. Copying the entire working directory into the image causes slow builds and leak risks.

### OPS-006 — Layer Caching Order

**MUST**

Dockerfile instructions MUST be ordered from least-frequently-changed to most-frequently-changed to maximize layer caching.

Example (illustrative, Dockerfile):
```dockerfile
COPY package*.json ./    # rarely changes
RUN npm ci               # cached if package.json unchanged
COPY . .                 # changes often
```

### OPS-007 — Image Secret Prohibition

**MUST NOT**

Secrets MUST NEVER be copied into the image (e.g., `COPY .env` or `ARG SECRET=...`). Secrets MUST come from the runtime environment or a secret manager.

### OPS-008 — Container Health Check

**MUST**

A `HEALTHCHECK` directive (or the platform's equivalent) MUST be added. The health check MUST verify the process is alive, not that every external dependency is healthy.

### OPS-009 — Standard Output Logging

**MUST**

Containers do not have a reliable filesystem. Logs MUST go to stdout and stderr. The orchestrator or container runtime collects them.

## Kubernetes

### OPS-010 — Kubernetes Scale Justification

**SHOULD NOT**

Kubernetes SHOULD NOT be used for a single container on a single server. Docker Compose, a systemd unit, or a managed platform is simpler and sufficient. Kubernetes is for orchestration at scale: multiple services, horizontal scaling, self-healing, and rolling deployments.

### OPS-011 — Resource Requests and Limits

**MUST**

Every container MUST have resource requests and limits defined:

- `resources.requests.cpu` and `.memory`: the minimum needed.
- `resources.limits.cpu` and `.memory`: the maximum allowed.

Without requests, the scheduler overcommits. Without limits, one pod can starve the node.

See MAS-040 in `_universal/00-master-anti-slop.md`.

### OPS-012 — Probe Separation

**MUST**

Startup, readiness, and liveness probes MUST be separated and configured correctly:

- **Startup**: has the process finished initializing?
- **Readiness**: is the process ready to receive traffic?
- **Liveness**: is the process still healthy?

The same check MUST NOT be used for all three. Liveness failures restart the pod; readiness failures remove it from the load balancer.

### OPS-013 — Kubernetes Tag Pinning

**MUST NOT**

The `latest` tag MUST NOT be used in Kubernetes manifests. Unpredictable rollouts occur when `imagePullPolicy: Always` is combined with `latest`. Specific version tags (e.g., `myapp:1.4.2`) MUST be used.

### OPS-014 — Graceful Shutdown Configuration

**MUST**

`terminationGracePeriodSeconds` MUST be set. The application MUST handle `SIGTERM` and finish in-flight requests before exiting.

### OPS-015 — External Secret Management

**SHOULD**

ConfigMaps MUST be used for non-sensitive configuration. For sensitive values, an external secret manager (Vault, AWS Secrets Manager) integrated via an operator or CSI driver SHOULD be preferred over native Kubernetes `Secret` objects. Secrets MUST NOT be committed to Git.

### OPS-016 — Pod Disruption Budget

**MUST**

For any service with more than one replica, a `PodDisruptionBudget` MUST be defined. This prevents the cluster from taking down all replicas at once during a node drain.

## Deployments

### OPS-017 — Immutable Artifacts

**MUST**

Every deployment MUST be a new artifact. Patching a running container in place is prohibited.

### OPS-018 — Rolling Deployment Pace

**MUST**

For stateless services, rollouts MUST occur one instance at a time. `maxSurge` and `maxUnavailable` MUST be configured to control the pace.

### OPS-019 — Advanced Deployment Strategy

**SHOULD**

For critical services, advanced strategies SHOULD be used: deploy alongside the current version and shift traffic gradually (canary), or switch entirely (blue-green).

### OPS-020 — Rollback Plan Documentation

**MUST**

Every deployment MUST have a documented rollback plan detailing:

- How to revert to the previous version.
- How long it takes.
- Whether a database migration is reversible.
- Who to notify.

A deployment without a rollback plan is a bet.

### OPS-021 — Migration Before Code

**MUST**

The safe deployment order for database changes MUST be followed:

1. Deploy the migration (add column, add index).
2. Deploy the code that uses it.
3. Remove the old column in a later migration.

Reversing this order causes runtime errors when new code hits an old schema.

### OPS-022 — Feature Flag Lifecycle

**MUST**

Feature flags MUST be used to decouple deployment from release for large features, behavior changes needing a kill switch, or A/B tests. Flags MUST NOT be left in the codebase forever; they MUST be removed when the feature is stable.

## Secrets Management

### OPS-023 — Repository Secret Prohibition

**MUST NOT**

Secrets MUST NEVER be committed to the repository. Secrets in Git history are secrets forever and MUST be rotated on exposure.

See MAS-009 in `_universal/00-master-anti-slop.md`.

### OPS-024 — Runtime Secret Injection

**MUST**

Secrets MUST be injected at runtime:

- Local: `.env` file, gitignored, loaded by the shell or the app.
- CI/CD: secret store provided by the platform.
- Production: a secret manager (Vault, AWS Secrets Manager, GCP Secret Manager).

### OPS-025 — Secret Rotation Policy

**MUST**

Every secret MUST have a rotation policy:

- API keys: rotate every 90 days or per policy.
- Database passwords: rotate on a schedule.
- Certificates: rotate before expiry, automatically where possible.

### OPS-026 — Least Privilege Access

**MUST**

Service accounts MUST have only the permissions they need. Database users MUST have access only to the tables and operations they use. Cloud IAM roles MUST be scoped to specific resources.

## Logging and Monitoring

### OPS-027 — Structured Logging

**MUST**

Logs MUST be structured (typically JSON). Fields MUST include `timestamp`, `level`, `service`, `requestId`, `userId`, `message`, and context-specific fields. String interpolation for logs is prohibited.

Example (illustrative):

BAD: `console.log("user " + userId + " did " + action)`.
GOOD: `logger.info({ userId, action }, "user action")`.

### OPS-028 — Production Log Levels

**MUST**

Log levels MUST be used correctly:

- `error`: something failed that needs attention.
- `warn`: something unexpected happened but the system recovered.
- `info`: normal operations (startup, shutdown, key events).
- `debug`: details for development.

Production MUST run at `info` or `warn`. `debug` is for local development.

### OPS-029 — Log Secret Redaction

**MUST NOT**

Tokens, passwords, and PII MUST NEVER appear in logs. Log redaction MUST be configured at the logger level, not trusted to every call site.

See MAS-009 in `_universal/00-master-anti-slop.md`.

### OPS-030 — Core Metrics Collection

**MUST**

Core metrics MUST be collected and exported to the project's chosen system (Prometheus, StatsD, CloudWatch):

- Request rate, error rate, duration (RED).
- Saturation, utilization, errors (USE).
- Business metrics (signups, orders, revenue).

### OPS-031 — Distributed Tracing

**SHOULD**

For multi-service systems, distributed tracing (e.g., OpenTelemetry) SHOULD be used to show the path of a request across services. Instrumentation MUST occur at the boundaries.

### OPS-032 — Actionable Alerts

**MUST**

Every alert MUST be a signal to a human and follow these rules:

- Every alert MUST have a runbook.
- Every alert MUST be actionable. If it cannot be acted on, it is noise.
- Alerts MUST target symptoms (error rate, latency), not causes (CPU usage).
- Alert fatigue kills response. Fewer, better alerts MUST be preferred.

## Backups and Recovery

### OPS-033 — Mandatory Backups

**MUST**

For any data that cannot be recreated, a backup MUST exist. No exceptions.

### OPS-034 — Backup Restore Testing

**MUST**

A backup that has never been restored is not a backup. The restore path MUST be tested regularly.

### OPS-035 — Off-Site Backup Storage

**MUST**

A backup in the same region as the primary is not a backup against regional failure. Backups MUST be stored in a different region or a different provider.

### OPS-036 — Retention Policy Definition

**MUST**

A retention policy MUST be defined and matched to the business requirement:

- Daily: 7 to 30 days.
- Weekly: 3 months.
- Monthly: 1 year.
- Yearly: 7 years (if required by compliance).

### OPS-037 — Disaster Recovery Documentation

**MUST**

A disaster recovery plan MUST be documented, detailing:

- What to do when the primary region fails.
- Who has the authority to declare a disaster.
- How long recovery takes (RTO).
- How much data can be lost (RPO).

## AI-Specific DevOps Discipline

### OPS-060 — Manifest and Image Verification

**MUST**

Before generating or modifying Kubernetes manifests, Dockerfiles, or cloud configurations, the assistant MUST verify that the base images, API versions, and resource quotas exist and are valid for the target environment. Invented API versions or image tags cause deployment failures that are invisible until runtime.

See MAS-036 in `_universal/00-master-anti-slop.md`.

### OPS-061 — Existing Pipeline Discovery

**MUST**

Before creating a new deployment script, CI/CD job, or infrastructure module, the assistant MUST search the project for an existing equivalent. Inventing parallel deployment paths creates configuration drift and security blind spots.

See MAS-035 in `_universal/00-master-anti-slop.md`.

### OPS-062 — Infrastructure Restraint

**SHOULD**

The assistant SHOULD NOT introduce complex orchestration tools (service meshes, advanced operators, multi-cluster setups) unless the project already uses them and the scale explicitly requires them.

See MAS-038 in `_universal/00-master-anti-slop.md`.

## Anti-Patterns

### OPS-040 — Untested Deployment

**MUST NOT**

Deploying without testing (e.g., `git push` to main triggers a deploy with no CI) is prohibited. CI MUST run tests; deployment MUST only occur on green.

### OPS-041 — Manual Deployment

**MUST NOT**

Manual deployments (e.g., SSH into the server and `git pull`) are prohibited. A reproducible deployment pipeline MUST be used.

### OPS-042 — Configuration Drift

**MUST NOT**

Servers or environments configured by hand lead to configuration drift. Infrastructure-as-code MUST be used to prevent this.

### OPS-043 — Shared Host Secret Exposure

**MUST NOT**

Secrets in environment variables on shared hosts (e.g., a shared CI variable visible to all jobs) are prohibited. Secrets MUST be scoped per environment and per job.

### OPS-044 — Single Point of Failure

**MUST NOT**

A single replica of a critical service is a single point of failure and MUST NOT be used. At least two replicas behind a load balancer MUST be deployed.

### OPS-045 — Unbounded Log Retention

**MUST NOT**

Logs kept forever with no rotation cause storage exhaustion. A retention policy (e.g., 30 days hot, 90 days cold, archive after) MUST be defined and enforced.

### OPS-046 — Tooling Overkill

**SHOULD NOT**

Over-monitoring a small service (e.g., five different observability tools for a 100-user app) SHOULD be avoided. Appropriate, minimal tooling SHOULD be selected.

### OPS-047 — Alert Fatigue

**MUST NOT**

Alerting on every error (e.g., paging for every 500 response) is prohibited. Alerts MUST trigger on error rates above a threshold for a sustained period.

### OPS-048 — Snowflake Server

**MUST NOT**

A server configured by hand and never rebuilt (a "snowflake" server) is prohibited. When it dies, nobody knows how to recreate it. Everything MUST be code.

### OPS-049 — Entrypoint Sudo

**MUST NOT**

Using `sudo` in a container entrypoint (e.g., `ENTRYPOINT ["sudo", "node", "app.js"]`) is prohibited. The container MUST run as a non-root user; no sudo is needed.

### OPS-050 — Bloated Image

**SHOULD NOT**

Docker images over 1 GB have slow pulls, slow deploys, and a large attack surface. Layers SHOULD be reviewed and unused tools removed.

### OPS-051 — Deployment Timing Discipline

**SHOULD**

Deployments SHOULD occur when people are available to respond to failures (e.g., avoiding Friday evenings). If the deployment process is fully automated and safe, any day works. If not, the process MUST be fixed.

## Response to Violation

When a rule in this file is violated, report:

Violation: OPS-{NNN}
Reason: {one-line reason}
Correction: {smallest fix}

For multiple violations, report each rule ID separately.

Do not replace a technical correction with a generic explanation.