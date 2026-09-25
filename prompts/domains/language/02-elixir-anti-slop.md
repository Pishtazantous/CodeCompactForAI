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

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
security anti-patterns, output format) are NOT repeated here.

This file covers rules specific to Elixir: OTP patterns, process
design, immutability, pattern matching, and the patterns that produce
supervisor crashes or message leaks. Framework rules (Phoenix) live
in `domains/framework/`.

## 1. Stack Assumptions

This layer assumes:

- Elixir 1.15 or later.
- Erlang/OTP 26 or later.
- Mix for builds.

## 2. Functional Core

### 2.1 Pure Functions First

Business logic is pure. Side effects (I/O, processes, time) are at
the boundaries.

BAD:
```elixir
def calculate_total(items) do
  rate = fetch_tax_rate()  # I/O in business logic
  Enum.reduce(items, 0, &(&1.price * (1 + rate) + &2))
end
```

GOOD:
```elixir
def calculate_total(items, tax_rate) do
  Enum.reduce(items, 0, &(&1.price * (1 + tax_rate) + &2))
end
```

### 2.2 Immutability

Elixir data is immutable. Do not try to mutate.

BAD: Expecting `list ++ [x]` to modify `list` in place.
GOOD: `new_list = list ++ [x]`.

### 2.3 Pipe Operator for Readability

BAD:
```elixir
Enum.sum(Enum.map(Enum.filter(items, & &1.active), & &1.price))
```

GOOD:
```elixir
items
|> Enum.filter(& &1.active)
|> Enum.map(& &1.price)
|> Enum.sum()
```

### 2.4 Pattern Matching Over Conditionals

BAD:
```elixir
def handle(result) do
  if is_tuple(result) && elem(result, 0) == :ok do
    elem(result, 1)
  else
    nil
  end
end
```

GOOD:
```elixir
def handle({:ok, value}), do: value
def handle({:error, _}), do: nil
```

### 2.5 Guard Clauses

BAD:
```elixir
def process(x) do
  if is_integer(x) and x > 0 do
    ...
  end
end
```

GOOD:
```elixir
def process(x) when is_integer(x) and x > 0 do
  ...
end
```

### 2.6 No Deeply Nested Cases

A `case` inside a `case` inside a `with` is hard to read. Extract
functions or use `with`.

### 2.7 `with` for Multi-Step Operations

```elixir
with {:ok, user} <- fetch_user(id),
     {:ok, account} <- fetch_account(user.account_id),
     {:ok, result} <- process(user, account) do
  {:ok, result}
else
  {:error, reason} -> {:error, reason}
end
```

## 3. Processes and OTP

### 3.1 Processes Are Cheap, Not Free

A process per user is fine. A process per message is not.

### 3.2 GenServer for State

A GenServer owns state. Direct calls to `:ets` or `Agent` are for
specific use cases.

### 3.3 Supervisor for Fault Tolerance

Every long-lived process is supervised. The supervisor restarts it
on crash.

BAD: `spawn_link(fn -> loop() end)` without supervision.
GOOD: A child spec in a supervisor tree.

### 3.4 Let It Crash

Do not catch every error. Let the supervisor restart the process
with clean state.

BAD:
```elixir
def handle_call(:bad_input, _from, state) do
  try do
    ...
  rescue
    _ -> {:reply, :error, state}
  end
end
```

GOOD: Match on the expected input; let unexpected input crash.

### 3.5 No Bare `spawn`

BAD: `spawn(fn -> ... end)`.
GOOD: `Task.start`, `Task.async`, or a supervised process.

### 3.6 `Task.async` Requires `Task.await`

BAD:
```elixir
Task.async(fn -> do_work() end)
# never awaited
```

The task leaks. Use `Task.start` for fire-and-forget, or await the
result.

### 3.7 Monitor for Cleanup

A process that links to another for a temporary operation uses
`Process.monitor` and handles `:DOWN`.

### 3.8 Message Leaks

A process that receives messages it never handles accumulates them.
Be explicit about the mailbox protocol.

## 4. Processes and State

### 4.1 No Global Mutable State

BAD: A named `Agent` used as a global counter.
GOOD: A supervised GenServer with a clear API.

### 4.2 ETS for Shared Read-Heavy Data

`:ets` is fast for reads. Writes are serialized. Use it when the
access pattern fits.

### 4.3 No Process Dictionary

`Process.put/get` is global mutable state per process. It hides
dependencies and complicates testing.

### 4.4 No `:global` Registry

`:global` is slow and has known issues. Use `Registry` or
`Phoenix.PubSub`.

## 5. Pattern Matching

### 5.1 Match in Function Heads

Covered in 2.4.

### 5.2 No `case` for Single-Pattern Match

BAD:
```elixir
case result do
  {:ok, value} -> value
end
```

GOOD: `{:ok, value} = result; value`.

### 5.3 Tagged Tuples

Use `{:ok, value}` and `{:error, reason}` consistently.

BAD: Returning a bare value on success and `nil` on failure.
GOOD: Tagged tuples.

### 5.4 `=~` for Regex Match

`=~` matches a string against a regex. It is not equality.

### 5.5 No Pattern Matching on Structs Without `%`

BAD: `def f(user) when user.name == "Alice"` (accesses the struct
without a match).
GOOD: `def f(%User{name: "Alice"} = user)`.

## 6. Error Handling

### 6.1 Tagged Tuples for Recoverable Errors

`{:ok, value}` / `{:error, reason}`.

### 6.2 Exceptions for Exceptional Cases

Raise for programmer errors (missing config, invalid state) and let
them crash the process.

### 6.3 Custom Exceptions

```elixir
defmodule AppError do
  defexception [:message]
end
```

### 6.4 `try`/`rescue` Sparingly

Prefer pattern matching. `rescue` is for library boundaries and
external calls.

### 6.5 Never `rescue _` Blindly

BAD: `rescue _ -> nil`.
GOOD: `rescue e in [SpecificError] -> handle(e)`.

### 6.6 `after` for Cleanup

`try`/`after` releases resources even when an exception occurs.

## 7. Elixir-Specific Anti-Patterns

### 7.1 Bare `spawn`

Covered in 3.5.

### 7.2 Unsupervised Process

Covered in 3.3.

### 7.3 `Process.sleep` in Tests

BAD: `Process.sleep(100)` to wait for async work.
GOOD: Use `assert_receive` with a timeout, or a synchronization
primitive.

### 7.4 `Task.await` With Default Timeout

The default timeout is 5 seconds. Long-running tasks need an
explicit timeout.

### 7.5 Blocking in a GenServer

BAD: A GenServer that does a long computation in `handle_call`,
blocking all other messages.

GOOD: Offload to a `Task` and reply asynchronously with
`GenServer.reply/2`.

### 7.6 State Accumulation Without Bound

A GenServer that keeps a growing list of events. Memory grows
forever.

### 7.7 Atoms From User Input

BAD: `String.to_atom(user_input)`.
GOOD: `String.to_existing_atom(user_input)`.

Atoms are not garbage-collected. Creating atoms from user input
exhausts the atom table.

### 7.8 `String.to_integer` on Untrusted Input

Raises on invalid input. Use `Integer.parse/1` and handle `:error`.

### 7.9 `Enum` on Large Streams

`Enum.map` materializes the entire list. Use `Stream.map` for lazy
evaluation.

BAD: `File.stream!("huge.log") |> Enum.map(&parse/1)`.
GOOD: `File.stream!("huge.log") |> Stream.map(&parse/1) |> Enum.take(100)`.

### 7.10 Nested `Enum.reduce`

A `reduce` inside a `reduce` is usually a sign the data should be
grouped first with `Enum.group_by`.

### 7.11 `if`/`else` Over Pattern Matching

Covered in 2.4.

### 7.12 Long Function Chains Without `|>`

Covered in 2.3.

### 7.13 Ignoring Compiler Warnings

Elixir's compiler warnings are precise. A project with warnings is a
project with latent bugs.

### 7.14 No Dialyzer

`dialyzer` catches type mismatches the compiler misses. Run it in
CI.

### 7.15 `Application.get_env` Everywhere

Reading config through `Application.get_env` in business logic
couples the code to the application environment. Pass
configuration as arguments.

### 7.16 `Module.concat` From User Input

BAD: `Module.concat([user_input])`.
GOOD: A lookup map with known modules.

### 7.17 `Code.eval_string`

Never. Executes arbitrary code.

### 7.18 `String.to_charlist` on User Input

`to_charlist` creates a list of integers. `String.to_atom` from a
charlist recreates the atom problem.

### 7.19 `Poison`/`Jason` Without a Schema

Decoding JSON into a map without validation. Use `Ecto` changesets
or a schema library.

### 7.20 Mixing `Task` and `GenServer`

A GenServer that spawns `Task.async` and awaits in the callback
blocks the server. Use `Task.Supervisor` and reply later.

### 7.21 Unbounded `Registry` Names

A `Registry` with keys generated per request grows forever. Cap or
clean up.

### 7.22 No Telemetry

Elixir has first-class telemetry. A production app without metrics
is a black box.

### 7.23 `Logger.debug` in Hot Paths

Logging has a cost. A debug log in a per-message path floods the
log.

### 7.24 `Enum.sort` on Unsorted Data

`Enum.sort` is O(n log n). For "is this sorted?" checks, use
`Enum.sort?`.

### 7.25 `Kernel.apply` Without a Reason

BAD: `apply(module, :function, args)` when the module is statically
known.
GOOD: `module.function(args)`.

`apply` hides the call from the analyzer.

## 8. Response to Violation

If a previous response violated a rule here:

```
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

No justification. No apology paragraph. Fix and move on.
