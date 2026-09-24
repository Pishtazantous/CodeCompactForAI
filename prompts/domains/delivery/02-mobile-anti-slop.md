---
id: 02-mobile-anti-slop
title: "Mobile Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: delivery
version: 1
---

# Mobile Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
security anti-patterns, output format) are NOT repeated here.

This layer covers cross-platform mobile delivery: lifecycle, permissions,
offline behavior, background work, notifications, deep links, and release
readiness. Framework-specific behavior belongs to the React Native,
Flutter, or native platform layer. Sensitive-data rules belong to
`domains/concern/02-security-critical-anti-slop.md`.

## 1. Stack Assumptions

**1.1 Confirm the delivery matrix.** Identify target OS versions, native
or cross-platform stack, distribution channel, offline requirements,
background capabilities, and push provider before implementation.

**1.2 Assume process disposal.** The OS may suspend, terminate, and
recreate the process. In-memory state remains provisional until the
project's persistence layer confirms it.
**1.3 Use the declared target SDK.** Select an API supported by the
project's target SDK and minimum OS version. Every version-gated feature
has an explicit lower-version fallback.

## 2. Domain Contracts

**2.1 Define a platform capability matrix.** For every platform-dependent
feature, record supported OS versions, manifest or entitlement, runtime
permission, OS entry point, failure modes, and user-visible fallback.

**2.2 Model lifecycle states separately.** Cold start, active, inactive,
background, process restoration, and termination are different states. A
restored process rebuilds state from durable data, its incoming intent,
or an authoritative refresh.

**2.3 Assign one owner to each state.** Classify state as ephemeral UI, durable local, server-owned, or pending mutation. Multiple stores do not own the same value.
**2.4 Model permission outcomes.** Distinguish not-determined, granted,
denied-but-requestable, restricted, and policy-unavailable states. A
boolean is insufficient when outcomes require different responses.
## 3. Lifecycle and Permissions

**3.1 Make bootstrap idempotent.** Initialize services, databases,
listeners, and native bridges once per process. Repeated foreground
events do not register duplicate handlers.

**3.2 Separate restoration from persistence.** Saved navigation restores
where the user was. Durable storage restores business data. One mechanism
does not imitate the other.

**3.3 Give subscriptions an owner.** Release listeners, timers, sockets,
observers, and native callbacks from the owner that created them.
Cancellation is safe when called repeatedly.

**3.4 Treat external launches separately.** Launcher, notification, and
deep-link starts have different entry paths. Parse and validate the
payload before navigation, then preserve the destination across process
restoration.

**3.5 Request permission in context.** Request access after the user
initiates the feature. When the platform allows it, explain the benefit
and the result of denial before the system prompt.

**3.6 Request minimum access.** Declare only what the feature requires.
Prefer a lower-impact platform API, and never infer background access
from a foreground permission.

**3.7 Handle denial as a product state.** Read the current result before
protected I/O. Every denial path has an explanation and approved
fallback. Offer a settings route when appropriate, but never loop the
dialog.

**3.8 Match disclosures to the binary.** Purpose strings, privacy
declarations, permissions, and entitlements describe what the release
artifact actually does. Remove unused access.
## 4. Offline and Local Data

**4.1 Name the source of truth.** For each synchronized record, state
whether the server, local durable store, or pending queue is
authoritative. A cache does not silently overwrite newer server state.

**4.2 Treat connectivity as a hint.** Expose the product states it needs,
such as fresh, refreshing, offline, stale, conflicted, and failed. An
active network interface does not prove service reachability.

**4.3 Persist pending mutations.** An offline write that promises later
synchronization is stored durably before success is reported. It has a
stable identifier, operation type, creation time, and retry state.

**4.4 Make retry idempotent.** A retried mutation does not produce a
second remote effect. Use the backend's existing idempotency mechanism or
stable operation identifier.

**4.5 Surface conflicts.** Do not use last-write-wins unless the product
requires it. Re-fetch the authoritative record and ask the user when a
conflict cannot be resolved deterministically.

**4.6 Bound local storage.** Define eviction, maximum size, and retention
for caches, logs, downloads, and queued work. A storage failure does not
leave a partial write. Sensitive data follows
`domains/concern/02-security-critical-anti-slop.md`.

## 5. Background Work and Notifications

**5.1 Match the mechanism to delivery.** Use process-local asynchronous
work when cancellation is acceptable. Use a durable platform scheduler
when work survives process death. Use a foreground service only for a
user-visible continuous task allowed by current platform policy.

**5.2 Make jobs restartable.** Background work can be delayed, batched,
or cancelled. Every job is bounded, checkpointed when necessary, and
safe to retry.

**5.3 Avoid permanent polling.** Do not keep a socket, GPS receiver,
timer, or service alive only to wait for an event. Use the platform
mechanism intended for that event.

**5.4 Request notification consent first.** Ask for authorization in a
user-visible flow. Denial does not block unrelated features.

**5.5 Manage the token lifecycle.** Persist a valid token, replace it on
refresh, and unregister it on sign-out or device removal when tokens are
account-scoped.

**5.6 Keep payloads minimal and versioned.** A push payload contains only
what the notification needs. Unknown versions follow an explicit accept
or reject policy.

**5.7 Validate incoming routes.** Parse notification payloads, universal
links, app links, and custom URLs against a route allowlist. Validate
identifiers and authentication before navigation.

**5.8 Assume repeated delivery.** A tapped action is safe when delivered
again. Use a stable event identifier for operations requiring
deduplication. Test terminated, backgrounded, inactive, active,
signed-out, and wrong-account paths.

## 6. Release and Test Matrix

**6.1 Match the release artifact to the submission.** The production
build enables only declared capabilities, endpoints, and branding. Debug
and staging behavior does not enter the release artifact.

**6.2 Review capability changes together.** A new permission, background
mode, data category, or entitlement updates the manifest, privacy
metadata, purpose text, and user explanation in the same change.

**6.3 Test the required mobile matrix.** Cover the oldest supported OS
and device, every permission outcome, process restoration, offline and
timeout paths, duplicate background work, notifications in every launch
state, account switching, and the release build.

**6.4 Use real devices for platform behavior.** Emulators do not prove
permission, background, notification, sensor, store, or battery behavior.
Test affected behavior on a supported physical device.

## 7. Domain-Specific Anti-Patterns

### 7.1 Requesting Permission at Startup

BAD:
```kotlin
requestPermissionLauncher.launch(Manifest.permission.CAMERA)
```

GOOD:
```kotlin
captureButton.setOnClickListener {
    requestPermissionLauncher.launch(Manifest.permission.CAMERA)
}
```

The request is tied to the action that explains why access is needed.

### 7.2 Infinite Background Polling

BAD:
```kotlin
while (isRunning) {
    repository.syncPending()
    Thread.sleep(5_000)
}
```

GOOD:
```kotlin
val request = OneTimeWorkRequestBuilder<SyncWorker>()
    .setConstraints(networkRequired)
    .build()

WorkManager.getInstance(context).enqueueUniqueWork(
    "pending-sync",
    ExistingWorkPolicy.KEEP,
    request,
)
```

Durable work is scheduled instead of keeping the process alive forever.

### 7.3 Trusting a Notification Route

BAD:
```kotlin
val orderId = intent.getStringExtra("order_id")!!
router.openOrder(orderId)
```

GOOD:
```kotlin
val payload = NotificationPayloadParser.parse(intent)
if (payload is OrderRoute && session.isAuthenticated) {
    router.openOrder(payload.orderId)
}
```

The route is parsed, constrained, and checked against the current account.

## 8. Response to Violation

If a previous response violated this layer, name the violated rule and show the corrected permission, lifecycle, or routing code. Do not repeat universal rules or claim unperformed tests.
