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

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
security anti-patterns, output format) are NOT repeated here.

This file covers rules specific to realtime systems: WebSocket, SSE,
long-polling, message ordering, delivery guarantees, backpressure,
reconnection, and the patterns that produce stuck connections or lost
messages. Event-driven architecture (queues, consumers) is covered in
this file where it intersects with realtime user-facing systems.

## 1. Stack Assumptions

This layer applies to:

- WebSocket servers and clients (native, Socket.IO, ws).
- Server-Sent Events.
- Long-polling fallbacks.
- WebRTC data channels (signaling, not media).
- gRPC streaming.
- MQTT for IoT.
- Message queues feeding realtime updates (Kafka, RabbitMQ, Redis
  Pub/Sub, NATS).

## 2. Connection Lifecycle

### 2.1 Authenticate Before the First Message

Authenticate at connection time (token in the handshake, a first
auth message), not on every subsequent message. The connection is
then trusted for its lifetime.

BAD: Sending the token with every WebSocket message.
GOOD: Auth during the handshake; the connection carries identity.

### 2.2 Handle Reconnection

Every realtime client reconnects automatically after a network drop.
Exponential backoff with jitter.

### 2.3 Resubscribe After Reconnect

A reconnected client re-subscribes to its channels. The server does
not remember subscriptions across disconnects.

### 2.4 State Recovery After Reconnect

If the client missed messages during the disconnect, it fetches a
snapshot or replays from a cursor. The client does not assume it saw
everything.

### 2.5 Heartbeats

A heartbeat (ping/pong) detects half-open connections. A connection
without traffic for N seconds is closed.

### 2.6 Clean Disconnect

The client sends a close message with a reason code. The server
releases resources tied to the connection.

### 2.7 Graceful Server Shutdown

On shutdown, the server:

1. Stops accepting new connections.
2. Sends a close frame to existing clients with a "server going away"
   code.
3. Waits for clients to disconnect (with a timeout).
4. Closes remaining connections.

Clients see a clean signal and reconnect to another instance.

## 3. Delivery Guarantees

### 3.1 At-Most-Once, At-Least-Once, Exactly-Once

Pick one explicitly:

- **At-most-once**: fire and forget. Messages may be lost.
- **At-least-once**: messages may be delivered more than once.
  Requires idempotent handling.
- **Exactly-once**: end-to-end deduplication with sequence numbers.
  Expensive; rarely needed.

Most realtime systems use at-least-once with client-side
deduplication.

### 3.2 Message IDs

Every message has a unique ID. The client deduplicates by ID.

### 3.3 Sequence Numbers

For ordered streams, each message carries a monotonically increasing
sequence number. The client detects gaps and requests replay.

### 3.4 Acknowledgments

For critical messages, the client sends an ack. The server retries
unacked messages within a window.

### 3.5 No Silent Drops

A dropped message is logged and, where possible, reported to the
sender.

## 4. Ordering

### 4.1 Per-Stream Ordering

Messages are ordered within a stream (a chat room, a user's updates).
Across streams, no order is guaranteed.

### 4.2 Single Writer Per Stream

To preserve order, only one server process writes to a stream. Use
a partition key (user ID, room ID) routed to the same worker.

### 4.3 Client-Side Reordering

If messages can arrive out of order (WebSocket over TCP is ordered
per connection, but multiple connections are not), the client
buffers and reorders by sequence number.

### 4.4 Timestamps Are Not Order

A message's `created_at` is not a reliable order. Clocks drift, and
two messages may share a timestamp. Use sequence numbers.

## 5. Backpressure

### 5.1 Slow Consumers

A slow client cannot keep up with the message rate. The server:

- Buffers up to a limit.
- Drops messages beyond the limit, or
- Disconnects the client.

Do not buffer without bound.

### 5.2 Buffer Limits

Every server-side buffer has a maximum size. A message beyond the
limit triggers a policy:

- Drop oldest.
- Drop newest.
- Disconnect.
- Apply flow control.

### 5.3 Flow Control

For protocols that support it (WebSocket does not natively), the
client signals readiness. Otherwise, the server tracks the send
buffer size and pauses when it grows.

### 5.4 No Broadcast to Unbounded Audience

A room with 100,000 members and a message every second is 100,000
messages per second. Partition or shard.

## 6. Reconnection and Resume

### 6.1 Resume Token

The client receives a resume token. On reconnect, it sends the token
and receives messages since its last position.

### 6.2 Replay Window

The server retains messages for a bounded time (5 minutes, 1 hour).
A client disconnected longer than the window receives a snapshot.

### 6.3 Snapshot Endpoint

A separate endpoint provides the current state. The client calls it
after a long disconnect.

### 6.4 Consistent Snapshot

The snapshot includes a sequence number. Subsequent messages resume
from that number.

## 7. Presence

### 7.1 Presence Is Eventually Consistent

Presence (who is online) is not a hard guarantee. A user may appear
online for a few seconds after disconnect.

### 7.2 Heartbeat-Based

Presence is derived from heartbeats. A user without a heartbeat for
N seconds is offline.

### 7.3 Broadcast Presence Changes Sparingly

Presence updates every keystroke are noise. Debounce or batch.

### 7.4 Presence Storage

Presence state is in fast storage (Redis, in-memory), not a relational
database. It changes constantly and is short-lived.

## 8. Scaling

### 8.1 Sticky Sessions or a Pub/Sub Layer

When multiple server instances handle WebSocket connections:

- Load balancer with sticky sessions, OR
- A pub/sub layer (Redis, NATS) that broadcasts messages between
  instances.

Pub/sub is preferred; sticky sessions complicate deploys.

### 8.2 Connection Limits Per Instance

Each server instance has a maximum connection count. Beyond it, the
load balancer routes new connections elsewhere.

### 8.3 Graceful Deploy

Rolling deploys drain connections from the old instance before
shutting it down.

### 8.4 Client Reconnect to Another Instance

Clients reconnect to any instance. State is not tied to the
connection.

## 9. Realtime-Specific Anti-Patterns

### 9.1 No Heartbeat

A half-open connection is not detected. The client thinks it is
connected; the server thinks it is connected. Messages are silently
lost.

### 9.2 No Reconnect Logic

The client does not reconnect after a network drop. The user must
refresh.

### 9.3 Unbounded Send Buffer

Covered in 5.2.

### 9.4 No Message IDs

The client cannot deduplicate. On reconnect, it processes the same
message twice.

### 9.5 Timestamps as Order

Covered in 4.4.

### 9.6 Auth Only at Login

The connection is established before login, and the server trusts any
message on it. Auth must be at connection time.

### 9.7 Broadcasting to All Clients

BAD: A global broadcast for a message meant for one user.
GOOD: Targeted delivery by user ID or channel.

### 9.8 No Rate Limit on Connections

A client that opens 10,000 connections from one IP. Rate-limit and
cap per-IP connection count.

### 9.9 No Backpressure

Covered in 5.1.

### 9.10 Subscriptions Without Cleanup

A server-side subscription (a database listener, a Redis channel)
that is not removed on disconnect. The subscription list grows
forever.

### 9.11 Blocking the Event Loop

A synchronous operation in the message handler blocks all other
connections on the same thread.

### 9.12 Message Size Unbounded

A client sends a 100 MB message. The server buffers it. Cap message
size.

### 9.13 No Auth on Reconnect

The client reconnects with the same connection token without
re-authenticating. If the token expired, the connection should be
rejected.

### 9.14 State in Memory Only

Presence and subscriptions only in one instance's memory. On restart,
all state is lost.

### 9.15 No Logging

A connection issue with no logs. Debugging is impossible.

### 9.16 Message Ordering Across Partitions

Two partitions of the same stream deliver out of order. The consumer
must handle it, or the producer must partition by the ordering key.

### 9.17 Retries Without Dedup

At-least-once delivery without message IDs produces duplicates. The
consumer must deduplicate.

### 9.18 Fan-Out Without Fan-In

A producer sends to 1,000 subscribers directly. The producer's load
scales with subscribers. Use a broker.

### 9.19 No Connection Metrics

No visibility into active connections, message rate, or error rate.
Scaling is guesswork.

### 9.20 Polling Instead of Pushing

A client that polls every second. The server load scales with clients.
Use a push protocol.

### 9.21 Long-Polling for Everything

Long-polling is a fallback. If WebSocket or SSE is available, use it.

### 9.22 Sending the Full State

BAD: Sending the entire document on every change.
GOOD: Sending deltas or operations. The client applies them.

### 9.23 No Versioning of the Realtime Protocol

The message format changes. Old clients break. Version the protocol.

### 9.24 Cross-Origin Without Auth

A WebSocket connection accepts any origin. Without an origin check,
a malicious site can open a connection on the user's behalf.

Check the `Origin` header against an allowlist during handshake.

## 10. Response to Violation

If a previous response violated a rule here:

```
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

No justification. No apology paragraph. Fix and move on.
