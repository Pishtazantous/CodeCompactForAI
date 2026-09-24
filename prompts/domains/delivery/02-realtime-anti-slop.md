---
id: 02-realtime-anti-slop
title: "Realtime Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: delivery
version: 1
---
# Realtime Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules are not
repeated. Service and data contracts use the related layers.

## 1. Stack Assumptions

**1.1 Name the transport and topology.** Identify WebSocket, SSE, MQTT, or
project transport; connection ownership; broker; and reconnect behavior.

**1.2 Define event meaning.** Every event has a stable type, version, key,
timestamp, producer, and consumer contract.

**1.3 Establish delivery requirements.** Specify acceptable loss, duplicate
handling, ordering scope, latency target, and retention.

## 2. Domain Contracts

**2.1 Delivery is explicit.** Choose at-most-once, at-least-once, or
exactly-once effects and implement the corresponding idempotency boundary.

**2.2 Ordering is scoped.** Guarantee order only where required, such as one
aggregate or partition; never promise global order casually.

**2.3 Backpressure is a control path.** A slow consumer slows or disconnects
before memory grows without bound.

**2.4 Reconnection is a state transition.** Resume, replay, deduplicate, and
reset the connection state explicitly.

## 3. Domain-Specific Rules

**3.1 Heartbeat every direction.** Detect dead peers with bounded intervals
and timeouts; avoid busy polling.

**3.2 Bound queues.** Set queue length, batch size, memory budget, and
overflow behavior for producer, broker, and consumer.

**3.3 Use sequence numbers.** Detect gaps, duplicates, stale events, and
replay windows using per-stream or per-aggregate metadata.

**3.4 Make handlers idempotent.** Store the event identifier or processed
sequence before applying a durable side effect where possible.

**3.5 Clean up subscriptions.** Every connection, timer, and listener has a
single owner and a repeatable release operation.

**3.6 Authenticate before subscribing.** Authorize channel and event access;
do not trust a client-provided room identifier.

**3.7 Preserve partial failure.** Define acknowledgement timing, retry
behavior, and recovery for a failed projection or side effect.

**3.8 Paginate replay.** Bound catch-up reads and expose a snapshot or cursor
when a client cannot safely resume from a live stream.

**3.9 Test network reality.** Cover disconnect, reconnect, duplicate, gap,
slow consumer, broker restart, permission revocation, and clock skew.

**3.10 Track connection health.** Measure active connections, queue depth,
drop rate, reconnect rate, lag, and heartbeat failures.

**3.25 Define stream identity.** Connection, stream, partition, sequence, and event identifiers have separate documented meanings.

**3.26 Bound fan-out.** Topic, history, and subscription limits are enforced before accepting a client request.

**3.27 Make replay authorized.** Reconnect and catch-up paths repeat the same sender, topic, and event authorization checks.

**3.28 Measure lag end to end.** Publish, broker, consumer, and delivery stages have separate latency and backlog metrics.

**3.29 Test dependency failure.** Broker restart, leader change, expired credentials, consumer crash, and reconnect storms have defined outcomes.

**3.30 Make delivery semantics explicit.** Scope loss, duplicates, ordering, replay, and acknowledgement to a stream or aggregate.

**3.31 Bound slow consumers.** Queue, payload, fan-out, history, and shutdown limits produce an explicit outcome.

**3.32 Measure recovery.** Cursor, lag, gap, heartbeat, reconnect, and dependency failures remain observable.

**3.33 Keep recovery evidence.** Cursor, lag, gap, heartbeat, reconnect, and dependency outcomes remain observable.

## 4. Domain-Specific Anti-Patterns

### 4.1 Unbounded Send Queue

BAD:
```typescript
socket.send(payload);
```

GOOD:
```typescript
if (outbox.length >= MAX_PENDING) {
  await closeWithReason("backpressure");
}
outbox.push(payload);
```

A slow peer cannot exhaust process memory.

### 4.2 Acknowledge Before Durable Work

BAD:
```typescript
await db.insert(event);
channel.ack(event.id);
```

GOOD:
```typescript
await db.insertOnce(event);
channel.ack(event.id);
```

The effect is safe to retry before acknowledgement.

### 4.3 Assuming Global Ordering

BAD:
```typescript
events.sort((a, b) => Date.now() - b.timestamp);
```

GOOD:
```typescript
events = mergeBySequence(events, streamCursors);
```

Ordering is enforced for the documented sequence scope.

**3.11 Define reconnect backoff.** Use bounded jittered backoff with a cap, reset it only after a healthy connection, and expose terminal failure.

**3.12 Validate clock assumptions.** Use server or sequence time where event timestamps are not trusted; do not use client wall clock for ordering.

**3.13 Bound event payloads.** Enforce maximum size, nesting, and text length before parsing or forwarding an event.

**3.14 Make recovery visible.** Track cursor, lag, gap, and replay status so a client can distinguish fresh data from recovered data.

**3.15 Exercise dependency loss.** Test broker restart, partition leader change, expired credentials, consumer crash, and reconnect storms.

**3.16 Make replay safe.** A replay uses the same authorization checks and event schema as the original stream.

**3.17 Bound subscriptions.** A client cannot subscribe to unbounded topics, history, or fan-out without an explicit limit.

**3.18 Handle renegotiation.** A protocol or schema change has a negotiated version and an explicit compatibility path.

**3.19 Keep heartbeat payloads small.** Heartbeats carry only liveness and optional diagnostic metadata, never business secrets.

**3.20 Make shutdown observable.** Drain or cancel active handlers within a deadline and record unfinished work and cursors.

**3.21 Test race boundaries.** Run concurrent publish, subscribe, reconnect, revoke, and shutdown cases with deterministic clocks where possible.

**3.22 Make reconnect idempotent.** A reconnecting client either resumes from a known cursor or requests a fresh snapshot; it does not merge unknown state silently.

**3.23 Measure end-to-end lag.** Include publish, broker, consumer, and render stages so a healthy connection does not hide backlog.

**3.24 Review retention impact.** A long replay window is a storage and privacy decision with an explicit owner and deletion path.

## 5. Response to Violation

If a prior response violated this layer, name the delivery, ordering,
backpressure, heartbeat, or cleanup defect and show the corrected protocol.
Do not claim realtime guarantees without stating their scope.
