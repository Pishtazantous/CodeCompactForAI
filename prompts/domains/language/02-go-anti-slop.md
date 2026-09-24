---
id: 02-go-anti-slop
title: "Go Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: language
version: 1
---

# Go Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
security anti-patterns, output format) are NOT repeated here.

This file covers rules specific to Go: error handling, goroutines,
context, interfaces, and the common patterns that produce silent bugs.
Framework rules (Gin, Fiber, Echo, chi) live in `domains/framework/`.

## 1. Stack Assumptions

This layer assumes:

- Go 1.21 or later. If the project targets an earlier version, some
  features (`slog`, `min`/`max` builtins, `slices`/`maps` packages) are
  unavailable.
- Modules (`go.mod`) are used. GOPATH mode is not assumed.
- The project follows the standard Go formatting (`gofmt`) and vet
  rules. No exceptions.

## 2. Formatting and Tooling

### 2.1 `gofmt` Is Non-Negotiable

All Go code is formatted with `gofmt` (or `go fmt`, which runs it). Do
not hand-align, do not fight tabs, do not introduce a different style.

### 2.2 `go vet` Must Pass

Every code change passes `go vet`. Never suppress a `go vet` warning by
restructuring code to hide it. Fix the cause.

### 2.3 Linters

Match the project's linter set (`golangci-lint`, `staticcheck`,
`errcheck`, `govulncheck`). Do not add `//nolint` directives without a
specific reason comment.

### 2.4 Import Grouping

Standard library, then third-party, then local. Blank line between
groups. The linter handles ordering; follow it.

### 2.5 Never Use Dot Imports

`import . "fmt"` pollutes the namespace and makes symbol origins
ambiguous. Never.

### 2.6 Never Use Blank Identifier Imports Without a Reason

`import _ "net/http/pprof"` triggers side effects. Acceptable only when
the package is explicitly designed for this (drivers, profilers). Add
a comment explaining why the blank import is needed.

## 3. Naming

### 3.1 Short Names for Short Scopes

Loop variables, small helpers, and short-lived receivers use short
names (`i`, `n`, `c`, `ctx`). Long names for long scopes.

### 3.2 MixedCaps, Never Underscores

`userID`, `HTTPServer`, `parseURL` -- not `user_id`, `HttpServer`,
`parse_url`. Acronyms stay uppercase.

### 3.3 No Getter Prefix

BAD: `func (u *User) GetName() string`
GOOD: `func (u *User) Name() string`

Setters may use `Set` when needed for clarity (`SetName`).

### 3.4 Interface Naming

A single-method interface is named `<Method>er`:
`Reader`, `Writer`, `Stringer`, `Closer`. Do not invent `IReader` or
`ReaderInterface`.

### 3.5 Package Names

- Short, lowercase, single word: `http`, `user`, `auth`.
- Never `util`, `common`, `helpers`, `models`, `base`.
- Avoid stutter: `user.User` is fine, `user.UserService` stutters if the
  package already provides context.

## 4. Error Handling

### 4.1 Errors Are Values

`error` is a return value, not an exception. Never panic for ordinary
control flow. Never ignore an error silently.

### 4.2 Always Check Returned Errors

BAD:
go
f, _ := os.Open(path)
GOOD:

go
f, err := os.Open(path)
if err != nil {
    return fmt.Errorf("open %s: %w", path, err)
}
_ for an error is acceptable only when the error is genuinely
irrelevant (rare, and must have a comment).

4.3 Wrap With %w, Not %v
%v loses the error chain and defeats errors.Is / errors.As. Use
%w when the caller might need to inspect the underlying error.

BAD:

go
return fmt.Errorf("load config: %v", err)
GOOD:

go
return fmt.Errorf("load config: %w", err)
4.4 Use errors.Is and errors.As
BAD:

go
if err == os.ErrNotExist { ... }
GOOD:

go
if errors.Is(err, os.ErrNotExist) { ... }
errors.Is walks the wrapped chain. errors.As extracts a specific
error type.

4.5 Sentinel Errors for Known Conditions
Define package-level sentinel errors:

go
var ErrNotFound = errors.New("not found")
Callers check with errors.Is(err, ErrNotFound).

4.6 Custom Error Types for Context
When an error needs to carry data, define a struct:

go
type ValidationError struct {
    Field string
    Msg   string
}
func (e *ValidationError) Error() string {
    return fmt.Sprintf("%s: %s", e.Field, e.Msg)
}
Extract with errors.As.

4.7 Never Compare Error Strings
BAD: if err.Error() == "not found" { ... }
GOOD: if errors.Is(err, ErrNotFound) { ... }

String comparison breaks on wrapping, translation, and message changes.

4.8 Do Not Log and Return
Either log and handle, or return and let the caller log. Doing both
produces duplicate log lines and obscures the caller's decision.

BAD:

go
if err != nil {
    log.Printf("failed: %v", err)
    return err
}
GOOD:

go
if err != nil {
    return fmt.Errorf("do work: %w", err)
}
4.9 panic Only for Programmer Errors
panic is for unreachable states, invariant violations, and init-time
failures. Never for user input, network errors, or anything a caller
can handle.

Library code should almost never panic. If it must, document it.

4.10 recover Only in Top-Level Handlers
recover is used at goroutine boundaries (HTTP middleware, worker
loops) to prevent one bad request from crashing the process. Never as
a general-purpose error handler.

4.11 Return Early, Not Deeply
BAD:

go
if ok {
    if valid {
        if !cancelled {
            doWork()
        }
    }
}
GOOD:

go
if !ok { return }
if !valid { return }
if cancelled { return }
doWork()
5. Context
5.1 context.Context Is the First Parameter
go
func Fetch(ctx context.Context, url string) (*Response, error)
Never second, never after other parameters, never stored in a struct.

5.2 Never Store Context in a Struct
Context is per-request. A struct that stores a context couples its
lifetime incorrectly and causes cancellation leaks.

5.3 Propagate Context
Pass ctx to every downstream call that accepts one: HTTP client,
database query, another service function.

BAD:

go
func Handle(ctx context.Context) {
    resp, err := http.Get(url) // no ctx
}
GOOD:

go
func Handle(ctx context.Context) {
    req, _ := http.NewRequestWithContext(ctx, "GET", url, nil)
    resp, err := http.DefaultClient.Do(req)
}
5.4 Do Not Create Contexts Without a Reason
context.Background() in main or in tests: correct.
context.Background() in a handler: wrong, use the passed-in ctx.

5.5 Always Cancel Contexts
context.WithCancel and context.WithTimeout return a cancel
function. Always defer cancel(), even on the success path, to release
resources.

BAD:

go
ctx, _ := context.WithTimeout(parent, 5*time.Second)
GOOD:

go
ctx, cancel := context.WithTimeout(parent, 5*time.Second)
defer cancel()
5.6 Never Use context.WithValue for Business Data
WithValue is for request-scoped metadata (trace IDs, auth tokens,
request IDs). Never for passing optional parameters to avoid changing
a signature.

6. Goroutines and Concurrency
6.1 Every Goroutine Has a Stop Condition
A goroutine that runs forever without a way to stop is a leak. Every
goroutine either:

Returns when its work is done, or

Selects on ctx.Done() and returns on cancellation, or

Reads from a channel that is closed by the sender.

6.2 Know When a Goroutine Ends
Before go func() { ... }(), answer: how does this goroutine stop?
If the answer is not obvious, the design is wrong.

6.3 Prefer errgroup Over Manual WaitGroups
golang.org/x/sync/errgroup combines sync.WaitGroup with error
propagation and context cancellation.

go
g, ctx := errgroup.WithContext(ctx)
g.Go(func() error { return fetchA(ctx) })
g.Go(func() error { return fetchB(ctx) })
if err := g.Wait(); err != nil { ... }
6.4 Never Share Mutable State Without Synchronization
If two goroutines read and write the same variable, use:

A sync.Mutex / sync.RWMutex,

A channel,

sync/atomic for simple counters,

Or restructure so each goroutine owns its data.

6.5 Channels Are for Ownership Transfer
Use channels to pass ownership of data between goroutines, not to
protect a shared variable. If a variable is protected by a channel,
a mutex is often clearer.

6.6 Buffered vs Unbuffered
Unbuffered: sender blocks until receiver reads.

Buffered: sender blocks when the buffer is full.

Choose deliberately. make(chan T, 1) is a common pattern for
"signal without blocking". Unbounded buffering is never an option;
pick a size with a reason.

6.7 Close Only From the Sender
Never close a channel from the receiver. Never close a channel twice.
Never close a channel that has multiple senders unless they coordinate.

6.8 select Needs a ctx.Done() Case
BAD:

go
select {
case msg := <-inbox:
    handle(msg)
case <-ticker.C:
    flush()
}
Without a ctx.Done() case, this loop cannot be cancelled.

GOOD:

go
select {
case msg := <-inbox:
    handle(msg)
case <-ticker.C:
    flush()
case <-ctx.Done():
    return ctx.Err()
}
6.9 sync.WaitGroup Correct Usage
wg.Add(n) before starting the goroutines.

wg.Done() via defer inside the goroutine.

wg.Wait() after all go statements.

Calling Add after Wait has started is a race.

6.10 Timeouts on All External Calls
Every HTTP call, database query, and external operation has a timeout
or a context with a deadline. A call without a timeout hangs forever if
the peer never responds.

7. Interfaces
7.1 Define Interfaces Where They Are Used
The consumer defines the interface, not the producer. A package that
provides a service should return a concrete type.

BAD: A UserService package defining a UserService interface and
returning it.
GOOD: A UserService package returning *Service, and the caller
defining the small interface it actually needs.

7.2 Small Interfaces
The best interfaces have one or two methods. io.Reader, io.Writer,
fmt.Stringer, error -- all one method.

A five-method interface is usually a design smell. Split it.

7.3 Accept Interfaces, Return Structs
Functions accept the smallest interface they need and return concrete
types. This keeps callers free to compose.

7.4 Never Define an Interface for a Single Implementation
If there is only one implementation and no test mock is needed, the
interface is overhead. Wait until a second implementation or a mock
appears.

7.5 No interface{} / any in Public APIs
any erases types. If a function must accept anything, use generics or
define a small interface with the methods it actually needs.

7.6 Type Assertions Need the Two-Value Form
BAD:

go
val := x.(string) // panics if x is not a string
GOOD:

go
val, ok := x.(string)
if !ok { return fmt.Errorf("expected string, got %T", x) }
Or use a type switch for multiple cases.

8. Generics
8.1 Generics Are for Containers and Algorithms
Generics are appropriate for:

Container types (List[T], Set[T]).

Algorithms that operate on any element type (Map, Filter,
Reduce).

Type-safe wrappers.

8.2 Do Not Generic-ify Existing Concrete Code
A function that works on int and is called once does not become
better by adding a type parameter. Generics add cognitive load; use
them when the abstraction is real.

8.3 Constraints From cmp and slices
Use the standard constraints (cmp.Ordered, comparable) and the
standard packages (slices, maps) instead of reimplementing them.

8.4 No Constraint Without a Use
BAD:

go
func Identity[T any](x T) T { return x }
This is fine but trivial. Do not add constraints the body does not
use.

9. Slices and Maps
9.1 Preallocate When the Size Is Known
BAD:

go
var items []Item
for _, x := range inputs {
    items = append(items, convert(x))
}
GOOD:

go
items := make([]Item, 0, len(inputs))
for _, x := range inputs {
    items = append(items, convert(x))
}
9.2 nil Slice vs Empty Slice
var s []T is nil.

s := []T{} is empty but non-nil.

Both have len(s) == 0.

nil slices marshal to null in JSON; empty slices marshal to [].

Choose deliberately, especially at API boundaries.

9.3 Never Take the Address of a Loop Variable Before Go 1.22
In Go 1.21 and earlier, the loop variable is reused across iterations.
Taking &v in a loop gives the same pointer every time.

BAD (pre-1.22):

go
for _, v := range items {
    ptrs = append(ptrs, &v) // all point to the same variable
}
GOOD:

go
for _, v := range items {
    v := v
    ptrs = append(ptrs, &v)
}
Or upgrade to Go 1.22+, where each iteration has its own variable.

9.4 Maps Are Not Safe for Concurrent Use
Concurrent reads are fine. Any write requires sync.RWMutex,
sync.Map, or single-goroutine ownership.

9.5 delete on a Missing Key Is a No-Op
delete(m, k) does not panic if k is missing. Check with v, ok := m[k] when you need to distinguish.

9.6 Copy Slices When Passing to Untrusted Code
A slice shares the underlying array. If the callee may modify it, pass
a copy:

go
copied := make([]T, len(src))
copy(copied, src)
10. Structs and Methods
10.1 Pointer vs Value Receivers
Use pointer receivers when the method mutates the receiver, when the
struct is large, or when consistency requires it.

Use value receivers for small, immutable types (a Point, a
Money).

Never mix pointer and value receivers for the same type.

10.2 Zero Value Should Be Useful
A struct's zero value should be usable without an explicit constructor.
var mu sync.Mutex works. var buf bytes.Buffer works. Aim for this.

10.3 Constructors Return *T
If a constructor is needed, it returns *T:

go
func NewClient(cfg Config) *Client { ... }
10.4 No Embedding for Convenience
Embedding promotes methods and fields. Use it when the embedded type is
genuinely part of the outer type. Do not embed to avoid writing a few
delegating methods; that is composition by accident.

10.5 Keep Structs Focused
A struct with more than 15 fields is often several structs. Group
related fields into sub-structs.

11. JSON and Serialization
11.1 Struct Tags Must Match the Contract
Every field that crosses an API boundary has a json:"..." tag. Match
the exact casing the API expects.

BAD:

go
type User struct {
    ID   int    // serializes as "ID"
    Name string // serializes as "Name"
}
GOOD:

go
type User struct {
    ID   int    `json:"id"`
    Name string `json:"name"`
}
11.2 omitempty Has Surprising Behavior
omitempty omits zero values: 0, "", false, nil, empty slices
and maps. If a 0 value is meaningful (count, price), do not use
omitempty. Use a pointer or a custom marshaler.

11.3 Decode Into a Pointer for Optional Fields
BAD:

go
type Patch struct {
    Name string `json:"name"` // cannot distinguish missing from ""
}
GOOD:

go
type Patch struct {
    Name *string `json:"name"` // nil means missing
}
11.4 Never Trust encoding/json With Huge Payloads
json.Decoder with io.LimitReader prevents unbounded memory use:

go
dec := json.NewDecoder(io.LimitReader(r, maxBytes))
11.5 interface{} Fields in JSON Are a Smell
A field typed any accepts any JSON shape and pushes validation to
runtime. Use a concrete type or json.RawMessage when deferring
parsing is necessary.

12. Time
12.1 Always Use Timezones
time.Now() returns a local time. Store times in UTC.

BAD:

go
createdAt := time.Now()
GOOD:

go
createdAt := time.Now().UTC()
12.2 Never Serialize Times Without a Format
time.Time marshals to RFC3339 by default. If the project uses a
different format, override with a custom marshaler or a wrapper type.
Never lose the timezone.

12.3 time.Sleep in Production Code
time.Sleep blocks the goroutine and cannot be cancelled. Use
time.After with select and ctx.Done():

go
select {
case <-time.After(delay):
    // proceed
case <-ctx.Done():
    return ctx.Err()
}
13. Testing
13.1 Table-Driven Tests
Match the project's convention. If it uses table-driven tests, follow.

13.2 t.Parallel() Where Appropriate
If the test is independent and the project uses t.Parallel(), use it.
Never parallelize tests that share state.

13.3 t.Cleanup Over defer
t.Cleanup runs even if the test fails via t.Fatal, which defer
does not. Use t.Cleanup for test resource release.

13.4 No Network in Unit Tests
HTTP calls, database connections, and external services belong in
integration tests. Unit tests use fakes or httptest.

13.5 Golden Files for Large Outputs
For complex outputs, store expected results in testdata/*.golden and
compare. Do not embed huge expected strings in the test file.

14. Go-Specific Anti-Patterns
14.1 Ignoring Errors
Covered in 4.2. The most common Go bug.

14.2 Goroutine Leaks
Covered in 6.1 and 6.2. The second most common Go bug.

14.3 defer Inside a Loop
BAD:

go
for _, path := range paths {
    f, _ := os.Open(path)
    defer f.Close() // runs only at function exit
}
With a thousand iterations, a thousand file handles stay open.

GOOD: Extract the loop body into a function, or close explicitly
inside the loop.

14.4 time.After in a select Loop
time.After allocates a timer that is not garbage collected until it
fires. In a loop that runs frequently, this leaks timers.

BAD:

go
for {
    select {
    case <-time.After(1 * time.Second):
        // ...
    }
}
GOOD:

go
ticker := time.NewTicker(1 * time.Second)
defer ticker.Stop()
for {
    select {
    case <-ticker.C:
        // ...
    }
}
14.5 sync.Mutex Copied by Value
A struct containing a mutex must be passed by pointer. Copying the
struct copies the mutex, and the two copies no longer protect the same
data.

BAD:

go
type Counter struct {
    mu sync.Mutex
    n  int
}
func (c Counter) Inc() { c.mu.Lock(); ... } // copies the mutex
GOOD:

go
func (c *Counter) Inc() { c.mu.Lock(); ... }
14.6 interface{} Casting Without Check
Covered in 7.6.

14.7 Returning Uninitialized Pointers
BAD:

go
func New() *Config {
    var c *Config
    return c // nil, no error
}
Return a value, a nil with a comment, or an error. Never a silent nil.

14.8 Channel Direction Not Specified
BAD:

go
func produce(ch chan int) { ... }
GOOD:

go
func produce(ch chan<- int) { ... }  // send only
func consume(ch <-chan int) { ... }  // receive only
Directional channels document intent and prevent mistakes.

14.9 init() With Side Effects
init() runs at package load. Side effects (network calls, file I/O)
there break testing and startup time. Keep init() for registration
only.

14.10 Global Variables
Module-level var is mutable global state. Prefer dependency
injection through function arguments or struct fields. Exceptions:
Err* sentinels, config constants, and sync.Once guarded singletons.

14.11 log.Fatal Outside main
log.Fatal calls os.Exit(1), which skips deferred functions. Library
code must return errors, not exit the process.

14.12 http.DefaultClient Without Timeout
http.DefaultClient has no timeout. A slow peer hangs the goroutine
forever.

BAD:

go
resp, err := http.Get(url)
GOOD:

go
client := &http.Client{Timeout: 10 * time.Second}
req, _ := http.NewRequestWithContext(ctx, "GET", url, nil)
resp, err := client.Do(req)
14.13 Forgetting to Close http.Response.Body
Every http.Response must have its body closed:

go
resp, err := client.Do(req)
if err != nil { return err }
defer resp.Body.Close()
Without the close, the connection pool leaks.

14.14 %v in Log Messages for Errors
%v prints the message. %+v on a wrapped error may print the chain
depending on the error library. Use the project's logging convention.
For slog:

go
slog.Error("failed", "err", err)
slog handles errors specially.

14.15 String Concatenation in a Loop
BAD:

go
var s string
for _, x := range items {
    s += x
}
This is O(n^2). Use strings.Builder:

go
var b strings.Builder
for _, x := range items {
    b.WriteString(x)
}
s := b.String()
14.16 append to a nil Map
BAD: var m map[string]int; m["x"] = 1 -- panics.
GOOD: m := make(map[string]int) or m := map[string]int{}.

14.17 Comparing Structs With == When They Contain Slices or Maps
Structs with slice, map, or function fields cannot be compared with
==. Compile error is clear, but the fix is often to use
reflect.DeepEqual in tests, or explicit field comparison.

14.18 Context in a Struct
Covered in 5.2. Repeating because it is common.

14.19 Unbuffered Channel Deadlock
BAD:

go
ch := make(chan int)
ch <- 1 // blocks forever, no receiver
Every unbuffered send needs a concurrent receiver.

14.20 time.Parse Without a Format Error Check
time.Parse returns an error. Do not discard it.

14.21 Implicit Interface Satisfaction Without Compile-Time Check
To ensure a type satisfies an interface, add:

go
var _ io.Reader = (*MyReader)(nil)
This fails at compile time if the method set drifts.

15. Response to Violation
If a previous response violated a rule here:

text
In the previous response, [specific rule] was violated. Correction:
[corrected code]
No justification. No apology paragraph. Fix and move on.

text

---
