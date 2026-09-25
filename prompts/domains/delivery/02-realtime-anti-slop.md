---
id: 02-realtime-anti-slop
title: "Realtime Anti-Slop Layer"
lang: en
depends_on: ["_universal/00-style-guide.md", "_universal/00-master-anti-slop.md"]
category: domain
domain_type: delivery
version: 2
---

# Realtime Anti-Slop Layer

This file defines behavioral contracts specific to realtime systems. It sits in the delivery layer, below the universal anti-slop rules and above framework-specific networking patterns. It covers WebSocket, SSE, long-polling, message ordering, delivery guarantees, backpressure, reconnection, and the patterns that produce stuck connections or lost messages. Event-driven architecture (queues, consumers) is covered where it intersects with realtime user-facing systems. It does not cover general backend API rules (see `02-backend-anti-slop.md`) or data pipeline streaming (see `02-data-pipeline-anti-slop.md`).

A realtime system is a continuous contract between client and server. Every connection, message, and reconnect is a guarantee of state synchronization.

## Scope

This file applies to WebSocket servers and clients (native, Socket.IO, ws), Server-Sent Events (SSE), long-polling fallbacks, WebRTC data channels (signaling), gRPC streaming, MQTT for IoT, and message queues feeding realtime updates (Kafka, RabbitMQ, Redis Pub/Sub, NATS). The principles are protocol-agnostic. The examples use WebSocket and generic message formats where illustrative.

## Rule Severity

Severity follows `_universal/00-style-guide.md`.

## Contracts

A realtime system commits to six contracts. The table below maps each contract to the rules that enforce it.

| Contract | Description | Enforced By |
|---|---|---|
| Connection Lifecycle | Connections are authenticated, heartbeat-monitored, and gracefully terminated. | RT-001 to RT-007 |
| Delivery Guarantees | Delivery semantics are explicit, messages are identifiable, and drops are logged. | RT-008 to RT-012 |
| Message Ordering | Streams maintain order via sequence numbers and single-writer partitions. | RT-013 to RT-016 |
| Backpressure & Scaling | Buffers are bounded, slow consumers are handled, and broadcasts are sharded. | RT-017 to RT-020, RT-029 to RT-032 |
| State Recovery | Clients resume from tokens or snapshots without losing or duplicating state. | RT-021 to RT-024 |
| Presence Discipline | Presence is eventually consistent, heartbeat-derived, and stored in fast memory. | RT-025 to RT-028 |

## Connection Lifecycle

### RT-001 — Connection-Time Authentication

**MUST**

Authentication MUST occur at connection time (e.g., token in the handshake or a first auth message). The connection is then trusted for its lifetime. Sending authentication tokens with every subsequent message is prohibited.

### RT-002 — Automatic Reconnection

**MUST**

Every realtime client MUST reconnect automatically after a network drop using exponential backoff with jitter.

### RT-003 — Post-Reconnect Resubscription

**MUST**

A reconnected client MUST re-subscribe to its channels. The server MUST NOT assume it remembers subscriptions across disconnects.

### RT-004 — Post-Disconnect State Recovery

**MUST**

If the client missed messages during a disconnect, it MUST fetch a snapshot or replay from a cursor. The client MUST NOT assume it saw everything during the outage.

### RT-005 — Heartbeat Enforcement

**MUST**

A heartbeat mechanism (ping/pong) MUST be implemented to detect half-open connections. A connection without traffic for a defined interval MUST be closed.

### RT-006 — Clean Disconnect Protocol

**MUST**

The client MUST send a close message with a reason code. The server MUST release resources tied to the connection immediately upon clean disconnect.

### RT-007 — Graceful Server Shutdown

**MUST**

On shutdown, the server MUST:

1. Stop accepting new connections.
2. Send a close frame to existing clients with a "server going away" code.
3. Wait for clients to disconnect (with a timeout).
4. Close remaining connections.

Clients see a clean signal and reconnect to another instance.

## Delivery Guarantees

### RT-008 — Explicit Delivery Guarantee

**MUST**

The delivery semantic MUST be explicitly chosen and documented:

- **At-most-once**: fire and forget. Messages may be lost.
- **At-least-once**: messages may be delivered more than once. Requires idempotent handling.
- **Exactly-once**: end-to-end deduplication with sequence numbers.

Most realtime systems MUST use at-least-once with client-side deduplication.

### RT-009 — Message ID Requirement

**MUST**

Every message MUST have a unique ID. The client MUST deduplicate by ID.

### RT-010 — Sequence Number Ordering

**MUST**

For ordered streams, each message MUST carry a monotonically increasing sequence number. The client MUST detect gaps and request replay.

### RT-011 — Critical Message Acknowledgment

**MUST**

For critical messages, the client MUST send an acknowledgment (ack). The server MUST retry unacked messages within a defined window.

### RT-012 — Drop Logging and Reporting

**MUST NOT**

Messages MUST NOT be dropped silently. A dropped message MUST be logged and, where possible, reported to the sender.

## Ordering

### RT-013 — Per-Stream Ordering Guarantee

**MUST**

Messages MUST be ordered within a stream (e.g., a chat room, a user's updates). Across streams, no order is guaranteed.

### RT-014 — Single Writer Per Stream

**MUST**

To preserve order, only one server process MUST write to a stream. A partition key (user ID, room ID) MUST be routed to the same worker.

### RT-015 — Client-Side Reordering

**MUST**

If messages can arrive out of order (e.g., multiple connections), the client MUST buffer and reorder by sequence number.

### RT-016 — Timestamp Ordering Prohibition

**MUST NOT**

A message's `created_at` timestamp MUST NOT be used as a reliable order. Clocks drift, and two messages may share a timestamp. Sequence numbers MUST be used.

## Backpressure

### RT-017 — Slow Consumer Policy

**MUST**

When a client cannot keep up with the message rate, the server MUST apply a policy: buffer up to a limit, drop messages beyond the limit, or disconnect the client. Unbounded buffering is prohibited.

### RT-018 — Bounded Server Buffers

**MUST**

Every server-side buffer MUST have a maximum size. A message beyond the limit MUST trigger a defined policy (drop oldest, drop newest, disconnect, or apply flow control).

### RT-019 — Flow Control Implementation

**SHOULD**

For protocols that support it, the client SHOULD signal readiness. Otherwise, the server MUST track the send buffer size and pause when it grows.

### RT-020 — Unbounded Broadcast Prohibition

**MUST NOT**

Broadcasting to an unbounded audience (e.g., a room with 100,000 members receiving a message every second) MUST NOT be handled by a single process. The load MUST be partitioned or sharded.

## Reconnection and Resume

### RT-021 — Resume Token Usage

**MUST**

The client MUST receive a resume token. On reconnect, it MUST send the token and receive messages since its last position.

### RT-022 — Bounded Replay Window

**MUST**

The server MUST retain messages for a bounded time (e.g., 5 minutes, 1 hour). A client disconnected longer than the window MUST receive a snapshot instead of a replay.

### RT-023 — State Snapshot Endpoint

**MUST**

A separate endpoint MUST provide the current state. The client MUST call it after a long disconnect.

### RT-024 — Snapshot Sequence Consistency

**MUST**

The snapshot MUST include a sequence number. Subsequent messages MUST resume from that number.

## Presence

### RT-025 — Eventual Consistency of Presence

**MUST**

Presence (who is online) MUST be treated as eventually consistent. A user may appear online for a few seconds after disconnect. Hard guarantees MUST NOT be promised.

### RT-026 — Heartbeat-Derived Presence

**MUST**

Presence MUST be derived from heartbeats. A user without a heartbeat for a defined interval MUST be marked offline.

### RT-027 — Presence Update Debouncing

**MUST NOT**

Presence updates on every keystroke or minor action MUST NOT be broadcast. Updates MUST be debounced or batched.

### RT-028 — Fast Storage for Presence

**MUST**

Presence state MUST be stored in fast storage (Redis, in-memory). It MUST NOT be stored in a relational database, as it changes constantly and is short-lived.

## Scaling

### RT-029 — Multi-Instance Message Routing

**MUST**

When multiple server instances handle connections, a pub/sub layer (Redis, NATS) MUST broadcast messages between instances. Sticky sessions MAY be used but complicate deploys and SHOULD be avoided.

### RT-030 — Instance Connection Limits

**MUST**

Each server instance MUST have a maximum connection count. Beyond it, the load balancer MUST route new connections elsewhere.

### RT-031 — Connection Draining on Deploy

**MUST**

Rolling deploys MUST drain connections from the old instance before shutting it down.

### RT-032 — Stateless Connection Routing

**MUST**

Clients MUST be able to reconnect to any instance. State MUST NOT be tied to a specific connection or instance memory.

## AI-Specific Realtime Discipline

### RT-060 — Protocol API Verification

**MUST**

Before using a realtime library API (e.g., Socket.IO events, WebSocket close codes, gRPC streaming methods), the assistant MUST verify the method exists in the installed version. Invented events or close codes produce silent connection failures.

See MAS-036 in `_universal/00-master-anti-slop.md`.

### RT-061 — Existing Realtime Pattern Discovery

**MUST**

Before creating a new pub/sub channel, WebSocket handler, or message broker consumer, the assistant MUST search the project for an existing equivalent. Inventing parallel realtime channels creates split-brain state and message loss.

See MAS-035 in `_universal/00-master-anti-slop.md`.

### RT-062 — Concurrency and State Restraint

**SHOULD**

The assistant SHOULD NOT introduce complex distributed state machines or custom consensus protocols for presence and ordering unless the project already uses them and the scale explicitly requires them.

See MAS-038 in `_universal/00-master-anti-slop.md`.

## Anti-Patterns

### RT-033 — Targeted Delivery Requirement

**MUST NOT**

A global broadcast for a message meant for one user or a specific channel is prohibited. Delivery MUST be targeted by user ID or channel.

### RT-034 — Connection Rate Limiting

**MUST**

Connection attempts MUST be rate-limited and capped per IP. A client opening thousands of connections from one IP MUST be blocked.

### RT-035 — Subscription Cleanup

**MUST**

Server-side subscriptions (database listeners, Redis channels) MUST be removed on disconnect. The subscription list MUST NOT grow forever.

### RT-036 — Event Loop Non-Blocking

**MUST NOT**

Synchronous operations in the message handler MUST NOT block the event loop. Blocking the loop drops all other connections on the same thread.

### RT-037 — Message Size Capping

**MUST**

Message size MUST be capped. A client sending a massive message MUST NOT be allowed to exhaust the server's buffer.

### RT-038 — Reconnect Token Validation

**MUST**

The client MUST re-authenticate or validate the connection token on reconnect. If the token expired, the connection MUST be rejected.

### RT-039 — Ephemeral State Persistence

**MUST NOT**

Presence and subscriptions MUST NOT be stored only in one instance's memory if high availability is required. On restart, all state is lost. Fast, shared storage MUST be used.

### RT-040 — Connection Telemetry Logging

**MUST**

Connection events, drops, and errors MUST be logged. A connection issue with no logs makes debugging impossible.

### RT-041 — Partition Ordering Key

**MUST**

If a stream is partitioned, the producer MUST partition by the ordering key. Two partitions of the same stream delivering out of order MUST be handled by the consumer or prevented by the producer.

### RT-042 — Retry Deduplication

**MUST**

At-least-once delivery without message IDs produces duplicates. The consumer MUST deduplicate retries.

### RT-043 — Broker-Mediated Fan-Out

**MUST NOT**

A producer sending directly to thousands of subscribers (fan-out without fan-in) is prohibited. The producer's load scales with subscribers. A broker MUST be used.

### RT-044 — Connection Metrics Visibility

**MUST**

Active connections, message rate, and error rate MUST be visible as metrics. Scaling without metrics is guesswork.

### RT-045 — Push Protocol Preference

**SHOULD**

Push protocols (WebSocket, SSE) SHOULD be preferred over polling. A client polling every second causes server load to scale linearly with clients.

### RT-046 — Long-Polling Fallback Discipline

**SHOULD**

Long-polling SHOULD only be used as a fallback. If WebSocket or SSE is available, it MUST be used.

### RT-047 — Delta State Transmission

**MUST NOT**

Sending the entire document or state on every change is prohibited. Deltas or operations MUST be sent, and the client MUST apply them.

### RT-048 — Protocol Versioning

**MUST**

The realtime message format MUST be versioned. Changing the format without versioning breaks old clients.

### RT-049 — Origin Header Validation

**MUST**

A WebSocket connection MUST NOT accept any origin. The `Origin` header MUST be checked against an allowlist during handshake to prevent cross-site WebSocket hijacking.

## Response to Violation

When a rule in this file is violated, report:

Violation: RT-{NNN}
Reason: {one-line reason}
Correction: {smallest fix}

For multiple violations, report each rule ID separately.

Do not replace a technical correction with a generic explanation.