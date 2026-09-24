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

Layered under `_universal/00-master-anti-slop.md`. Universal safety and scope
rules are not repeated. Infrastructure definitions are in the related
infrastructure layer.

## 1. Stack Assumptions

**1.1 Establish the delivery target.** Identify the service, artifact registry,
cluster, environment, Git workflow, and existing release controller.

**1.2 Follow existing manifests.** Reuse the repository's Docker, Kubernetes,
chart, and deployment conventions before creating new resources.

**1.3 Treat production as stateful.** A deployment changes running systems;
rollback and data compatibility are part of the change.

## 2. Domain Contracts

**2.1 Make the artifact immutable.** Tag builds with a reproducible revision
and deploy the same digest that passed verification.

**2.2 Separate desired and observed state.** Record the intended release and
verify running pods, services, and configuration against it.

**2.3 Roll back as a designed path.** Define health gates, compatibility
limits, and a tested command or controller for restoring the prior release.

**2.4 Protect credentials.** Inject secrets through the existing secret
manager; never bake them into images, manifests, logs, or CI variables.

## 3. Domain-Specific Rules

**3.1 Build minimal images.** Use a supported base, a non-root user where
possible, pinned dependency locks, and no build credentials in layers.

**3.2 Declare resource boundaries.** Set requests, limits, probes, and
termination behavior for every workload; test under realistic load.

**3.3 Gate deployment on health.** Require readiness, application tests,
migration checks, and rollout observation before promoting traffic.

**3.4 Make updates safe.** Use rolling or canary strategy according to the
project. Avoid a delete-and-recreate step without an explicit data plan.

**3.5 Preserve rollback compatibility.** Do not remove old fields, pods,
routing targets, or environment variables until the new release is proven.

**3.6 Observe each rollout.** Track revision, image digest, replica health,
latency, errors, and saturation with the existing telemetry system.

**3.7 Keep environments explicit.** Configuration differences are reviewed
values, not ad hoc edits in a running cluster.

**3.8 Limit privileged access.** Scope service accounts and deploy roles to
the operations the service needs.

**3.9 Test failure paths.** Cover bad image, readiness timeout, migration
failure, partial rollout, dependency outage, and rollback.

**3.25 Keep rollout settings reviewed.** Replicas, surge, limits, probes, and traffic policy have an owner and a capacity rationale.

**3.26 Protect release metadata.** Record source, digest, builder, approvals, and health evidence without credentials or customer data.

**3.27 Verify graceful drain.** Stop new traffic before termination and confirm in-flight work has a completion or retry path.

**3.28 Keep rollback reversible.** The prior artifact remains available until the new release meets its observation and recovery window.

**3.29 Test dependency outage.** Deployment and rollback behavior remain safe when registries, clusters, databases, or secret stores are unavailable.

**3.30 Verify artifact identity.** The deployment records and resolves the same immutable image digest.

**3.31 Observe rollout health.** Track readiness, errors, latency, and saturation before and after promotion.

**3.32 Keep recovery owned.** The rollback identity, target, and decision maker are documented and tested.

**3.33 Keep release records safe.** Store only revision, digest, health, and rollback evidence without credentials or customer data.

## 4. Domain-Specific Anti-Patterns

### 4.1 Mutable Image Tag

BAD:
```yaml
image: registry.example/app:latest
```

GOOD:
```yaml
image: registry.example/app@sha256:7f2c1b2d
```

Rollback identifies an exact artifact.

### 4.2 Secret in Environment Manifest

BAD:
```yaml
env:
  - name: DATABASE_PASSWORD
    value: "production-password"
```

GOOD:
```yaml
envFrom:
  - secretRef:
      name: app-runtime
```

Credentials are managed outside the image and manifest history.

### 4.3 Rollback by Deleting State

BAD:
```bash
kubectl delete deployment app
```

GOOD:
```bash
kubectl rollout undo deployment/app --to-revision=41
```

The controller restores the prior compatible release.

**3.10 Define migration ownership.** A schema or configuration migration names the operator, compatibility window, verification query, and recovery action.

**3.11 Check pod security.** Run as the least-privileged identity, mount only required filesystems, and prohibit privilege escalation in workload settings.

**3.12 Bound rollout exposure.** Use replica surge, partition, or traffic controls appropriate to capacity; never remove healthy capacity without a stated budget.

**3.13 Verify configuration drift.** Compare rendered configuration and feature flags with the intended release before declaring rollout complete.

**3.14 Exercise graceful shutdown.** Confirm active requests finish or cancel within the termination grace period and dependencies are not left with half-closed connections.

**3.15 Record deployment evidence.** Keep revision, digest, start time, health result, and rollback reference in the release record without secrets.

**3.16 Separate build and runtime secrets.** Build credentials are short-lived and unavailable to the final image or runtime process.

**3.17 Keep deployment declarative.** A rollout command may act on reviewed state, but the resulting configuration must remain represented in version control.

**3.18 Define health semantics.** Liveness, readiness, and startup checks answer different questions and must not use the same fragile signal.

**3.19 Respect capacity during termination.** Drain traffic before removing replicas and verify dependent jobs can finish or retry.

**3.20 Verify post-rollback state.** Check application health, database compatibility, queue depth, and cache behavior after restoring the prior release.

**3.21 Exercise incident rollback.** Run the rollback under a representative load and record elapsed time, data effects, and owner.

**3.22 Verify namespace ownership.** Namespaces, selectors, and service accounts match the owning service and do not collide with another environment.

**3.23 Keep images reproducible.** A rebuild from the same source and locked inputs produces the same tested content or a reviewed equivalent.

**3.24 Record image provenance.** Store source revision, builder, base digest, and scan result in the release evidence.

## 5. Response to Violation

If a prior response violated this layer, identify the deployment risk and
show the corrected artifact reference, health gate, secret source, or rollback
command. Do not claim a cluster operation was performed when it was not.
