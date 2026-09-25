---
id: 02-devops-anti-slop
title: "DevOps Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: delivery
version: 1
---

# DevOps Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
security anti-patterns, output format) are NOT repeated here.

This file covers rules specific to deployment, containerization,
infrastructure, and operational concerns: Docker, Kubernetes,
deployment strategy, secrets, health checks, and rollback. Rules
specific to infrastructure-as-code tools (Terraform, Pulumi) live in
`domains/delivery/02-infra-anti-slop.md`. CI/CD pipeline rules live in
`domains/delivery/02-cicd-anti-slop.md`.

## 1. Stack Assumptions

This layer applies to:

- Applications deployed as containers (Docker, Podman).
- Applications orchestrated with Kubernetes, Docker Swarm, or a
  managed platform (ECS, Cloud Run, Fly.io).
- Traditional deployments (systemd, PM2, bare metal).
- Serverless deployments (Lambda, Cloud Functions).

The rules below are the minimum for any deployment. Pick the ones
that apply to the project's target.

## 2. Containers

### 2.1 One Process Per Container

A container runs one process. Not nginx + app + cron. If multiple
processes are needed, they are separate containers (or separate
services).

### 2.2 Multi-Stage Builds When Appropriate

A build stage with the compiler and a runtime stage with the artifact:

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

For a 10-line script, a single stage is fine. Do not over-engineer.

### 2.3 Pin Base Image Versions

BAD: `FROM node:latest`.
GOOD: `FROM node:20.11.1-alpine`.

`latest` moves under your feet. Pin to a specific version and update
deliberately.

### 2.4 Non-Root User

BAD: `USER root` (or no `USER` directive, which defaults to root).
GOOD:
```dockerfile
RUN addgroup --system app && adduser --system app --ingroup app
USER app
```

Running as root inside a container is a privilege escalation risk.

### 2.5 `.dockerignore`

Every project has a `.dockerignore` that excludes:

- `.git`
- `node_modules`
- `dist` (if built inside)
- `.env`
- Test files
- Local data

Copying the entire working directory into the image is a slow build
and a leak risk.

### 2.6 Layer Caching

Order Dockerfile instructions from least-frequently-changed to
most-frequently-changed:

```dockerfile
COPY package*.json ./    # rarely changes
RUN npm ci               # cached if package.json unchanged
COPY . .                 # changes often
```

Reversing this invalidates the install cache on every code change.

### 2.7 No Secrets in the Image

Never `COPY .env` or `ARG SECRET=...`. Secrets come from the runtime
environment or a secret manager. See section 5.

### 2.8 Health Check

Add a `HEALTHCHECK` directive (or the platform's equivalent). The
health check verifies the process is alive, not that every dependency
is healthy.

### 2.9 Log to stdout/stderr

Containers do not have a reliable filesystem. Logs go to stdout and
stderr. The orchestrator collects them.

## 3. Kubernetes

### 3.1 Do Not Use Kubernetes for One Container

A single container on a single server does not need Kubernetes. Docker
Compose, a systemd unit, or a managed platform is simpler and
sufficient.

Kubernetes is for orchestration at scale: multiple services,
horizontal scaling, self-healing, and rolling deployments.

### 3.2 Resource Requests and Limits

Every container has:

- `resources.requests.cpu` and `.memory`: the minimum needed.
- `resources.limits.cpu` and `.memory`: the maximum allowed.

Without requests, the scheduler overcommits. Without limits, one pod
can starve the node.

### 3.3 Liveness, Readiness, Startup Probes

- **Startup**: has the process finished initializing?
- **Readiness**: is the process ready to receive traffic?
- **Liveness**: is the process still healthy?

Do not use the same check for all three. Liveness failures restart
the pod; readiness failures remove it from the load balancer.

### 3.4 No `latest` Tags

BAD: `image: myapp:latest`.
GOOD: `image: myapp:1.4.2`.

The `latest` tag in Kubernetes with `imagePullPolicy: Always` causes
unpredictable rollouts.

### 3.5 Graceful Shutdown

Set `terminationGracePeriodSeconds`. The app handles `SIGTERM` and
finishes in-flight requests before exiting.

### 3.6 ConfigMaps and Secrets

- ConfigMaps for non-sensitive configuration.
- Secrets for sensitive values. Prefer an external secret manager
  (Vault, AWS Secrets Manager) integrated via an operator or CSI
  driver over Kubernetes `Secret` objects.
- Do not commit Secrets to Git.

### 3.7 Pod Disruption Budget

For any service with more than one replica, define a
`PodDisruptionBudget`. This prevents the cluster from taking down
all replicas at once during a node drain.

## 4. Deployments

### 4.1 Immutable Deployments

Every deployment is a new artifact. Never patch a running container.

### 4.2 Rolling Deployments

For stateless services, roll out one instance at a time. `maxSurge`
and `maxUnavailable` control the pace.

### 4.3 Blue-Green or Canary

For critical services, deploy alongside the current version, shift
traffic gradually (canary), or switch entirely (blue-green).

### 4.4 Rollback Plan

Every deployment has a documented rollback:

- How to revert to the previous version.
- How long it takes.
- Whether a database migration is reversible.
- Who to notify.

A deployment without a rollback plan is a bet.

### 4.5 Database Migrations Before Code

The safe order:

1. Deploy the migration (add column, add index).
2. Deploy the code that uses it.
3. Remove the old column in a later migration.

Reversing this order causes runtime errors when new code hits an old
schema.

### 4.6 Feature Flags

A feature flag decouples deployment from release. The code ships
disabled, and the flag enables it. Use them for:

- Large features that ship in increments.
- Behavior changes that need a kill switch.
- A/B tests.

Do not leave flags forever. Remove them when the feature is stable.

## 5. Secrets Management

### 5.1 Never in the Repository

Covered in `00-master-anti-slop.md` section 2.4. Repeating: secrets
in Git history are secrets forever. Rotate on exposure.

### 5.2 Environment Variables at Runtime

- Local: `.env` file, gitignored, loaded by the shell or the app.
- CI/CD: secret store provided by the platform.
- Production: a secret manager (Vault, AWS Secrets Manager, GCP
  Secret Manager).

### 5.3 Secret Rotation

Every secret has a rotation policy:

- API keys: rotate every 90 days or per policy.
- Database passwords: rotate on a schedule.
- Certificates: rotate before expiry, automatically where possible.

### 5.4 Least Privilege

- A service account has only the permissions it needs.
- Database users have only the tables and operations they use.
- Cloud IAM roles are scoped to specific resources.

## 6. Logging and Monitoring

### 6.1 Structured Logs

Logs are JSON. Fields include `timestamp`, `level`, `service`,
`requestId`, `userId`, `message`, and context-specific fields.

BAD: `console.log("user " + userId + " did " + action)`.
GOOD: `logger.info({ userId, action }, "user action")`.

### 6.2 Log Levels

- `error`: something failed that needs attention.
- `warn`: something unexpected happened but the system recovered.
- `info`: normal operations (startup, shutdown, key events).
- `debug`: details for development.

Production runs at `info` or `warn`. `debug` is for local.

### 6.3 Never Log Secrets

Covered in `00-master-anti-slop.md` section 2.4. Repeating: tokens,
passwords, and PII never appear in logs. Log redaction is
configured at the logger level, not trusted to every call site.

### 6.4 Metrics

Collect:

- Request rate, error rate, duration (RED).
- Saturation, utilization, errors (USE).
- Business metrics (signups, orders, revenue).

Export to Prometheus, StatsD, CloudWatch, or the project's chosen
system.

### 6.5 Tracing

For multi-service systems, distributed tracing (OpenTelemetry) shows
the path of a request across services. Instrument at the boundaries.

### 6.6 Alerts

An alert is a signal to a human. Rules:

- Every alert has a runbook.
- Every alert is actionable. If it cannot be acted on, it is noise.
- Alert on symptoms (error rate, latency), not causes (CPU usage).
- Alert fatigue kills response. Fewer, better alerts.

## 7. Backups and Recovery

### 7.1 Backups Are Mandatory

For any data that cannot be recreated, there is a backup. No
exceptions.

### 7.2 Backups Are Tested

A backup that has never been restored is not a backup. Test the
restore path regularly.

### 7.3 Backups Are Off-Site

A backup in the same region as the primary is not a backup against
regional failure. Store in a different region or a different provider.

### 7.4 Retention Policy

Define how long backups are kept:

- Daily: 7 to 30 days.
- Weekly: 3 months.
- Monthly: 1 year.
- Yearly: 7 years (if required by compliance).

Match the policy to the business requirement.

### 7.5 Disaster Recovery Plan

Document:

- What to do when the primary region fails.
- Who has the authority to declare a disaster.
- How long recovery takes (RTO).
- How much data can be lost (RPO).

## 8. DevOps-Specific Anti-Patterns

### 8.1 Deploying Without Testing

BAD: `git push` to main triggers a deploy with no CI.
GOOD: CI runs tests; deploy only on green.

### 8.2 Manual Deployments

BAD: SSH into the server and `git pull`.
GOOD: A deployment pipeline that is reproducible.

### 8.3 Config Drift

The server was set up manually, and now nobody knows what is on it.
Infrastructure-as-code prevents this (see `02-infra-anti-slop.md`).

### 8.4 No Health Check

BAD: A container without a health check.
GOOD: A `/health` endpoint or a `HEALTHCHECK` directive.

### 8.5 No Graceful Shutdown

BAD: `kill -9` on deploy.
GOOD: `SIGTERM`, wait for in-flight requests, then exit.

### 8.6 Running as Root in Container

Covered in 2.4.

### 8.7 Secrets in Environment Variables on Shared Hosts

BAD: `SECRET=...` in a shared CI variable visible to all jobs.
GOOD: Scoped secrets per environment, per job.

### 8.8 Long-Lived `latest` Tags

Covered in 3.4.

### 8.9 No Resource Limits

Covered in 3.2.

### 8.10 Single Point of Failure

BAD: One replica of the critical service.
GOOD: At least two replicas, behind a load balancer.

### 8.11 Unbounded Log Retention

BAD: Logs kept forever with no rotation.
GOOD: A retention policy (30 days hot, 90 days cold, archive after).

### 8.12 Over-Monitoring for a Small Service

BAD: Five tools (Prometheus, Grafana, Loki, Sentry, UptimeRobot) for
a 100-user app.
GOOD: Two appropriate tools.

### 8.13 Alert on Every Error

BAD: A page for every 500 response.
GOOD: Alert on error rate above a threshold, for a sustained period.

### 8.14 Snowflake Servers

A server configured by hand and never rebuilt. When it dies, nobody
knows how to recreate it. Everything is code.

### 8.15 `sudo` in Entrypoint

BAD: `ENTRYPOINT ["sudo", "node", "app.js"]`.
GOOD: The container runs as a non-root user; no sudo needed.

### 8.16 No Rollback Strategy

Covered in 4.4.

### 8.17 Deploying on Friday

Not a technical rule, but a cultural one: deploy when people are
available to respond to failures. If the deployment process is safe,
any day works. If not, fix the process.

### 8.18 Docker Image Over 1 GB

A bloated image has slow pulls, slow deploys, and a large attack
surface. Review layers and remove unused tools.

### 8.19 Copying Source Without `.dockerignore`

Covered in 2.5.

### 8.20 No Logs From a Container

BAD: The app writes to a file inside the container.
GOOD: The app writes to stdout/stderr. The container runtime captures
it.

## 9. Response to Violation

If a previous response violated a rule here:

```
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

No justification. No apology paragraph. Fix and move on.
