---
id: 02-elixir-anti-slop
title: "Elixir Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: language
version: 1
---
# Elixir Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. This layer covers OTP
process design, supervision, message contracts, and immutable data. Phoenix
or other framework rules remain in their own files.

## 1. Scope and Assumptions
1. Read `mix.exs`, the Elixir and OTP release targets, and existing child
   specifications before selecting a process or library.
2. Match the project's supervision strategy and telemetry conventions.
3. Do not add a dependency, child process, or GenServer when a plain
   function, immutable data structure, or existing process is sufficient.

## 2. OTP Process Design
4. Give each long-lived process one responsibility and an owner. A process
   that owns unrelated caches, sockets, and business rules is difficult to
   reason about and test.
5. Use a GenServer for serialized mutable state, not as a substitute for
   pure functions. Keep `handle_*` clauses small and explicit.
6. Define the process message protocol with concrete structs or a shared
   module. Do not send undocumented tuples to arbitrary processes.
7. Return explicit results for commands. A cast is fire-and-forget; do not use
   it when the caller needs success, failure, or a reply.
8. Set process names only when ownership is unique and intentional. Avoid
   global names that make test isolation and multi-tenant operation fragile.

## 3. Supervision
9. Put supervised processes under the appropriate supervisor with a restart
   intensity that matches their failure behavior.
10. Use `one_for_one` only when children are independent; use `one_for_all`
    when a shared invariant genuinely requires coordinated restart.
11. Make child startup explicit and bounded. Do not start an unbounded
    supervisor from a process or request handler.
12. A supervisor's job is restart strategy, not application business logic.
13. Do not trap exits or link manual processes when an OTP lifecycle is the
    intended ownership model.

## 4. Pattern Matching
14. Match on the smallest structure that makes invalid states unrepresentable.
    Prefer structs and maps with required keys over tuple position access.
15. Use multiple clauses to handle distinct outcomes; do not collapse errors,
    timeouts, and cancellation into `:ok`.
16. Match external input at the boundary and convert it to an internal type.
    Do not pass unvalidated maps through every function.
17. Use pin operators when a value is already bound and must be compared, not
    rebound accidentally.

## 5. Processes, Mailboxes, and Timeouts
18. Keep the mailbox small. A process doing unbounded work can receive faster
    than it can reply; apply backpressure at the caller or redesign the queue.
19. Use `Task.Supervisor` for bounded concurrent work and await the task. Do
    not leave unlinked tasks running after their request ends.
20. Propagate cancellation and use `Task.shutdown` or an application-specific
    stop signal for cooperative workers.
21. Use timeouts intentionally and handle `:exit` and `:timeout` separately
    when they require different recovery.
22. Do not use `Process.sleep` as a synchronization primitive. Use messages,
    monitors, or a supervisor-aware mechanism.

## 6. Immutability and Side Effects
23. Pass immutable data between processes. Do not mutate shared maps, lists, or
    structs in place; transformations return new values.
24. Keep `IO`, HTTP, database, and filesystem effects at the edge of a
    process or service. Pure decision functions should remain testable.
25. Do not store ETS or process state without an owner, cleanup path, and
    documented consistency model.
26. Do not put secrets in process state or logs; use the project's configured
    secret mechanism.

## 7. Types, Guards, and Error Handling
27. Use specs for public behavior when the project does so, and validate
    external values before they enter domain functions.
28. Guards describe cheap, total conditions. Do not put remote calls, message
    sends, or complex database work in guards.
29. Match on `{:ok, value}` and `{:error, reason}` rather than discarding a
    tagged tuple with an underscore.
30. Never rescue an exception to hide process failure. Let a supervisor or the
    caller apply the documented restart and retry policy.

## 8. Verification Checklist
31. Test normal operation, invalid messages, timeout, caller timeout, worker
    failure, and supervisor restart behavior.
32. Inspect mailbox growth and process count under representative load.
33. Run `mix format --check-formatted`, the configured compiler checks, and
    tests when those commands exist in the project.
34. Report exact commands and results; do not claim unrun checks passed.

35. Inspect supervision trees for children that restart indefinitely without a
    configured intensity limit.
36. Verify every call has a timeout and that timeout differs from a normal
    domain error in handling and telemetry.
37. Check process names and ETS keys for tenant and node isolation.
39. Exercise invalid messages and crash-loop limits in supervision tests.
40. Confirm process names and ETS keys are isolated across tenants and nodes.
41. Record supervisor restart and timeout behavior.

41. Inspect supervision trees for bounded restart intensity.
42. Verify every call has a meaningful timeout.
43. Handle timeout separately from domain failure.
44. Check process names for node and tenant isolation.
45. Review ETS ownership and cleanup paths.
46. Confirm telemetry excludes secrets.
47. Run the configured formatter, compiler, and tests.
48. Exercise crash loops and worker failure.
49. Record supervisor and mailbox observations.
50. Keep guards free of messages and remote calls.
51. Review task shutdown for deterministic completion.

## Domain-Specific Anti-Patterns

### 9.1 Hidden Process State
BAD:
```elixir
defmodule Cache do
  use GenServer
  def put(k, v), do: GenServer.cast(__MODULE__, {:put, k, v})
end
```
GOOD:
```elixir
defmodule Cache do
  use GenServer
  def put(server, key, value), do: GenServer.call(server, {:put, key, value})
end
```

### 9.2 Permissive Matching
BAD:
```elixir
def handle({:ok, value}), do: {:reply, value}
```
GOOD:
```elixir
def handle({:ok, %Job{status: :ready} = job}), do: {:reply, {:ok, job}, %{}}
```

### 9.3 Unbounded Mailboxes
BAD:
```elixir
def handle_info({:job, job}, state), do: {:noreply, queue(job, state)}
```
GOOD:
```elixir
def handle_info({:job, job}, state) do
  case queue(job, state) do
    {:ok, next} -> {:noreply, next}
    {:error, :full} -> {:stop, :backpressure}
  end
end
```

## 10. Response to Violation
Identify the process, module, file, and numbered rule that was violated. Explain
whether the failure is message loss, mailbox growth, restart coupling, or
invalid data. Make the smallest correction and preserve the process contract.
Refer to the master layer rather than repeating it. If a supervision strategy
or dependency changes, state the operational impact before editing.
Report the exact checks that were run.
