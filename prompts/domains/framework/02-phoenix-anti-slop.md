---
id: 02-phoenix-anti-slop
title: "Phoenix Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-backend-anti-slop]
category: domain
domain_type: framework
version: 1
---
# Phoenix Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`, the architecture layer, and `domains/delivery/02-backend-anti-slop.md`. General backend rules remain inherited.

## 1. Phoenix Boundaries

1. Keep contexts as the public application boundary.
2. Keep controllers, channels, and LiveViews at interface boundaries.
3. Use changesets for external input and model invariants.
4. Keep Ecto queries inside contexts or repository adapters.
5. Use the endpoint and router conventions already present.
6. Reuse the existing authentication and authorization modules.
7. Keep supervision trees explicit and restart-safe.
8. Keep configuration in the project config files.
9. Use telemetry names already defined by the application.
10. Keep tests near the behavior they verify.
11. Do not add a second web or validation layer.
12. Use the existing Repo, endpoint, and channel helpers.
13. Keep public functions small and cohesive.
14. Report assumptions not confirmed from the repository.

## 2. Contexts and Ecto

15. Expose operations through a context module.
16. Keep schema and changeset details behind the context API.
17. Use `Repo.transaction` or `Ecto.Multi` for multi-write work.
18. Use preload or joins to prevent N+1 queries.
19. Keep external calls out of query functions.
20. Use database constraints for durable invariants.
21. Keep authorization close to the context operation.
22. Use `Repo.insert!` only when failure must stop the caller.
23. Keep list operations paginated or bounded.
24. Test context success, failure, and authorization paths.

### 2.1 Direct Repo Access from a Channel

BAD:
```elixir
def handle_in("update", %{"name" => name}, socket) do
  Repo.update!(socket.assigns.user, %{name: name})
  {:reply, :ok, socket}
end
```

GOOD:
```elixir
def handle_in("update", %{"user" => params}, socket) do
  case Accounts.update_user(socket.assigns.user, params) do
    {:ok, user} -> {:reply, :ok, assign(socket, :user, user)}
    {:error, changeset} -> {:reply, {:error, changeset}, socket}
  end
end
```

## 3. Controllers and LiveViews

25. Keep controller actions focused on plug, session, and response.
26. Validate body, path, query, and session values at the edge.
27. Use the central error renderer and status conventions.
28. Keep templates free of Repo calls.
29. Keep LiveView assigns bounded and serializable.
30. Load initial data in `mount`.
31. Handle events in `handle_event` with changesets.
32. Authorize mounts and events independently when needed.
33. Use navigation helpers for trusted local redirects.
34. Handle disconnected and reconnecting states.
35. Keep uploads and temporary data bounded.
36. Do not run long blocking work in the LiveView process.
37. Test invalid events and authorization failures.

### 3.1 Unbounded Assign

BAD:
```elixir
def mount(_params, _session, socket) do
  {:ok, assign(socket, :orders, Repo.all())}
end
```

GOOD:
```elixir
def mount(_params, _session, socket) do
  {:ok, assign(socket, :orders, Accounts.list_orders(limit: 50))}
end
```

### 3.2 LiveView Event Bypass

BAD:
```elixir
def handle_event("save", %{"name" => name}, socket) do
  {:ok, _} = Accounts.update_user(socket.assigns.user, %{name: name})
  {:noreply, socket}
end
```

GOOD:
```elixir
def handle_event("save", %{"user" => params}, socket) do
  case Accounts.update_user(socket.assigns.user, params) do
    {:ok, user} -> {:noreply, assign(socket, :user, user)}
    {:error, changeset} -> {:noreply, assign(socket, :changeset, changeset)}
  end
end
```

## 4. Channels and Presence

33. Keep `join`, message handlers, and `terminate` small.
34. Validate every channel message with a schema.
35. Authorize topic subscription and state changes.
36. Never trust a client-supplied user, tenant, or role.
37. Keep broadcast topics explicit and tenant-scoped.
38. Use Presence for ephemeral presence only.
39. Do not use Presence for durable permissions.
40. Make reconnect and duplicate messages idempotent.
41. Bound broadcasts and terminate owned processes.
42. Test authorization, disconnect, and duplicate delivery.

### 4.1 Presence as Authorization

BAD:
```elixir
def handle_info(%Phoenix.Socket.Broadcast{event: "presence_diff"}, socket) do
  {:push, :authorize, %{role: socket.assigns.role}, socket}
end
```

GOOD:
```elixir
def handle_in("change_role", %{"role" => role}, socket) do
  case Accounts.change_role(socket.assigns.user, role) do
    {:ok, _} -> {:reply, :ok, socket}
    {:error, reason} -> {:reply, {:error, reason}, socket}
  end
end
```

## 5. Errors, Supervision, and Operations

43. Map exceptions through the endpoint error handling.
44. Do not expose Repo, socket, or LiveView internals.
45. Log crashes with request and process context.
46. Keep telemetry event names stable and non-sensitive.
47. Do not swallow exits or messages.
48. Use supervision for restart behavior, not endless business retries.
49. Make external work retry-safe.
50. Close clients and subscribers in their owner.
51. Validate required configuration at startup.
52. Keep secrets out of logs and assigns.
53. Run formatter, tests, dialyzer, and build.
54. Keep the diff limited to Phoenix boundaries.

### 5.1 Process Leak

BAD:
```elixir
def handle_info(:tick, socket) do
  Process.sleep(60_000)
  {:noreply, socket}
end
```

GOOD:
```elixir
def handle_info(:tick, socket) do
  {:noreply, assign(socket, :last_tick, System.monotonic_time())}
end
```

## Domain-Specific Anti-Patterns

### A. Context Bypass

BAD:
```elixir
def handle_in("save", %{"name" => name}, socket) do
  Repo.update!(socket.assigns.user, %{name: name})
  {:reply, :ok, socket}
end
```

GOOD:
```elixir
def handle_in("save", %{"user" => params}, socket) do
  Accounts.update_user(socket.assigns.user, params)
end
```

### B. Unbounded LiveView Assign

BAD:
```elixir
{:ok, assign(socket, :events, Repo.all(Event))}
```

GOOD:
```elixir
{:ok, assign(socket, :events, Events.list(limit: 50))}
```

### C. Unvalidated Channel Message

BAD:
```elixir
def handle_in("rename", %{"name" => name}, socket), do: reply(socket, rename(socket.assigns.user, name))
```

GOOD:
```elixir
def handle_in("rename", %{"user" => params}, socket), do: Accounts.rename_user(socket.assigns.user, params, socket)
```

## 6. Response to Violation
1. Name the Phoenix context, channel, or LiveView boundary and preserve its contracts.
2. Add a focused test and run the formatter, tests, dialyzer, and build.
3. Report unverified assumptions; change no unrelated files and create no commit.
