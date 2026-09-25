---
id: 02-rust-anti-slop
title: "Rust Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: language
version: 1
---

# Rust Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
security anti-patterns, output format) are NOT repeated here.

This file covers rules specific to Rust: ownership, borrowing, error
handling, lifetimes, unsafe code, and the patterns that produce
correct-looking code with hidden costs or panics. Framework rules
(Axum, Actix, Tauri) live in `domains/framework/`.

## 1. Stack Assumptions

This layer assumes:

- Rust 2021 edition or later.
- `cargo` as the build tool.
- The project uses `clippy` and `rustfmt`. Both pass before commit.

## 2. Error Handling

### 2.1 No `unwrap` in Production

BAD: `let file = File::open(path).unwrap();`.
GOOD: `let file = File::open(path)?;` or explicit handling.

`unwrap` and `expect` panic. A panic in a library propagates to the
caller; a panic in a server thread may crash the process.

`expect` is acceptable when the invariant is proven and the message
explains it:

```rust
let home = std::env::var("HOME").expect("HOME must be set");
```

Even then, prefer returning an error unless the invariant is truly
absolute.

### 2.2 No `panic!` for Expected Errors

BAD: `if input.is_empty() { panic!("empty input"); }`.
GOOD: Return `Err(InputError::Empty)`.

Panics are for bugs, not for bad input.

### 2.3 Use `Result<T, E>` for Fallible Operations

Every function that can fail returns `Result`. Never a sentinel value
like `-1` or `null`.

### 2.4 `?` Operator

The `?` operator propagates errors. Use it liberally.

```rust
fn load(path: &Path) -> Result<Config, ConfigError> {
    let content = fs::read_to_string(path)?;
    let config = toml::from_str(&content)?;
    Ok(config)
}
```

### 2.5 Error Types Are Descriptive

BAD: `Result<T, String>`.
GOOD: `Result<T, ConfigError>` where `ConfigError` is an enum.

Library errors implement `std::error::Error`. Application errors can
use `anyhow::Error`.

### 2.6 `thiserror` for Library Errors

```rust
#[derive(thiserror::Error, Debug)]
pub enum ConfigError {
    #[error("file not found: {0}")]
    NotFound(PathBuf),
    #[error("invalid format")]
    Format(#[from] toml::de::Error),
}
```

### 2.7 `anyhow` for Application Errors

In binaries, `anyhow::Result<T>` with context:

```rust
use anyhow::Context;

let config = load(&path).context("failed to load config")?;
```

Do not use `anyhow` in library crates that others depend on.

## 3. Ownership and Borrowing

### 3.1 Borrow by Default, Own When Necessary

BAD:
```rust
fn process(data: String) -> String { ... }
```

This forces the caller to give up ownership.

GOOD:
```rust
fn process(data: &str) -> String { ... }
```

This borrows.

### 3.2 `&str` Over `&String`, `&[T]` Over `&Vec<T>`

`&str` accepts `String`, `&str`, and string literals. `&String` only
accepts `&String`.

BAD: `fn parse(input: &String)`.
GOOD: `fn parse(input: &str)`.

Same for `&[T]` over `&Vec[T]`, and `&Path` over `&PathBuf`.

### 3.3 Clone When You Mean It

BAD: Cloning to satisfy the borrow checker without understanding why.
GOOD: Restructure the ownership.

`clone()` is not a bug, but a reflexive `clone()` often hides a
design issue.

### 3.4 Explicit Lifetimes Only When Needed

Rust elides lifetimes in most cases. Do not annotate when elision
works.

BAD:
```rust
fn first<'a>(items: &'a [i32]) -> &'a i32 { &items[0] }
```

GOOD:
```rust
fn first(items: &[i32]) -> &i32 { &items[0] }
```

### 3.5 `Cow` for Maybe-Owned Data

```rust
use std::borrow::Cow;

fn normalize(input: &str) -> Cow<str> {
    if input.contains(' ') {
        Cow::Owned(input.replace(' ', "_"))
    } else {
        Cow::Borrowed(input)
    }
}
```

Avoids allocation when no change is needed.

### 3.6 No `Rc<RefCell<T>>` Without a Reason

`Rc<RefCell<T>>` allows shared mutable state but trades compile-time
checks for runtime panics. A `borrow_mut` conflict panics at runtime.

Prefer restructuring to pass ownership or use message passing.

## 4. Unsafe Code

### 4.1 Every `unsafe` Block Has a Safety Comment

```rust
// SAFETY: `ptr` is valid for `len` bytes, aligned, and not aliased
// for the duration of this call, as guaranteed by the caller.
let slice = unsafe { std::slice::from_raw_parts(ptr, len) };
```

The comment explains the invariant that makes the unsafe block
correct.

### 4.2 Minimize the Unsafe Surface

Wrap unsafe code in a safe function that enforces the invariants.
Callers never see `unsafe`.

### 4.3 Run Miri

`cargo +nightly miri test` catches undefined behavior in unsafe code
that regular tests miss.

### 4.4 No Unsafe for Performance Without Measurement

BAD: "This is faster if I skip the bounds check."
GOOD: A benchmark proving the difference, and a proof that the index
is in bounds.

### 4.5 Unsafe Is Not a Bug

Some code genuinely needs unsafe: FFI, low-level data structures,
performance-critical kernels. The rule is not "never unsafe"; it is
"every unsafe block is justified, isolated, and tested."

## 5. Concurrency

### 5.1 Message Passing Over Shared State

Prefer channels (`mpsc`, `crossbeam`) over `Arc<Mutex<T>>`.

### 5.2 `Arc<Mutex<T>>` When Shared Mutable State Is Genuine

A global cache, a shared counter. Use `parking_lot::Mutex` when
performance matters.

### 5.3 Hold Locks Briefly

A lock held across an `.await` (in async code) or a long operation
blocks other tasks.

BAD:
```rust
let guard = mutex.lock().unwrap();
some_async_operation().await;  // holds the lock across await
```

### 5.4 Async-Aware Locks

In async code, use `tokio::sync::Mutex`, not `std::sync::Mutex`,
when the lock is held across `.await`.

### 5.5 No Blocking in Async

`std::thread::sleep`, blocking I/O, and CPU-heavy loops block the
runtime. Use `tokio::time::sleep`, async I/O, and `spawn_blocking`.

### 5.6 Bounded Channels

Unbounded channels grow without limit under load. Use bounded
channels and apply backpressure.

### 5.7 `Send` and `Sync` Are Intentional

Types that cross thread boundaries implement `Send`/`Sync`. Never
`unsafe impl Send` without a proof.

## 6. Traits

### 6.1 `impl Trait` Over Generics When the Type Is Not Named

BAD:
```rust
fn process<T: Iterator<Item = i32>>(iter: T) { ... }
```

GOOD:
```rust
fn process(iter: impl Iterator<Item = i32>) { ... }
```

Both are monomorphized, but `impl Trait` is clearer when the type is
not otherwise used.

### 6.2 `dyn Trait` for Runtime Dispatch

Use `Box<dyn Trait>` or `&dyn Trait` when the concrete type is
chosen at runtime. The cost is a vtable lookup; the benefit is
flexibility.

### 6.3 No Trait for a Single Implementation

A trait with one implementor is a design smell unless the trait is
part of a public API that will have more implementors.

### 6.4 Object Safety

A trait with generic methods or `Self` return types is not
object-safe. Do not use `dyn Trait` for such traits.

### 6.5 `From` and `Into`

Implement `From<T>` for `U` to get `Into<U>` for free. Do not
implement both.

### 6.6 No `Deref` for Inheritance

`Deref` is for smart pointers (`Box`, `Rc`, `Arc`). Using it to fake
inheritance produces surprising method resolution.

## 7. Macros

### 7.1 Macros Are a Last Resort

A function or generic is almost always clearer. Macros hide the flow
of control and complicate debugging.

### 7.2 `macro_rules!` for Simple Cases

Declarative macros for pattern-based code generation. Readable and
easy to debug.

### 7.3 Proc Macros for Complex Cases

Procedural macros (`#[derive]`, attribute, function-like) for
deriving traits or generating substantial code. They compile slowly
and are hard to debug.

### 7.4 Macro Hygiene

Declarative macros should be hygienic (do not introduce identifiers
that clash with user code). Use `$crate::` to refer to the crate's
items.

### 7.5 Document Macro Inputs

A macro's documentation shows the accepted forms and the expansion.

## 8. Cargo and Dependencies

### 8.1 Minimal Dependencies

Every dependency adds compile time and attack surface. Before adding:

- Is there a standard library solution?
- Is the crate maintained?
- Does it have a permissive license?
- How many transitive dependencies does it bring?

### 8.2 Feature Flags for Optional Functionality

A crate that pulls in `tokio` for a feature that only half the users
need should gate it behind a feature.

### 8.3 `Cargo.lock` for Binaries, Not for Libraries

- Binaries commit `Cargo.lock`.
- Libraries do not (or commit it but it is ignored by dependents).

### 8.4 Version Ranges

BAD: `serde = "1.0.200"` (exact pin).
GOOD: `serde = "1"` (compatible range).

Cargo's semver rules handle the rest.

### 8.5 `cargo update` Deliberately

A lockfile update is a change. Review it, test it, commit it.

### 8.6 `cargo audit`

Run `cargo audit` in CI. A vulnerable dependency is a vulnerability.

## 9. Rust-Specific Anti-Patterns

### 9.1 `unwrap()` Everywhere

Covered in 2.1.

### 9.2 `panic!` for Control Flow

Covered in 2.2.

### 9.3 Excessive `clone()`

Covered in 3.3.

### 9.4 `Rc<RefCell<T>>` Everywhere

Covered in 3.6.

### 9.5 Holding a Lock Across `.await`

Covered in 5.3.

### 9.6 Blocking in Async

Covered in 5.5.

### 9.7 Unbounded Channels

Covered in 5.6.

### 9.8 `unsafe` Without a Safety Comment

Covered in 4.1.

### 9.9 `unsafe impl Send` Without Proof

Covered in 5.7.

### 9.10 `String` in Function Signatures

Covered in 3.2.

### 9.11 Deeply Nested `match`

A `match` inside a `match` inside a `match` is unreadable. Extract
functions or use combinators.

### 9.12 `if let` Chains

Before Rust 2024, `if let` chains are not stable. Use `match` with
`|` patterns.

### 9.13 `.into()` Everywhere

Every `.into()` is a type inference opportunity for the compiler and
a readability cost for the reader. Prefer explicit conversions when
the target type is not obvious.

### 9.14 `impl Trait` in Return With Mixed Types

`fn f() -> impl Trait` requires all return paths to be the same type.
Use `Box<dyn Trait>` when they differ.

### 9.15 Ignoring `#[must_use]`

A function with `#[must_use]` returns a value that matters. Ignoring
it is a bug.

BAD: `vec.len();` (the result is unused).
GOOD: `let _ = vec.len();` (if genuinely ignored) or use the value.

### 9.16 `std::mem::forget` Without a Reason

`mem::forget` leaks memory deliberately. Use it only for FFI or
destructor-avoidance patterns with a documented reason.

### 9.17 Ignoring Clippy

Clippy warnings are not noise. A project with `#![allow(clippy::all)]`
is a project that has given up.

### 9.18 Ignoring the Borrow Checker

BAD: Adding `clone()` or `Rc<RefCell>` to make the compiler happy.
GOOD: Understanding what the compiler wants and restructuring.

The borrow checker is usually right. Fighting it is a sign of a
design problem.

### 9.19 Manual `Drop` Without a Reason

Explicit `Drop` implementations are for resource cleanup. For memory
management, the compiler handles it.

### 9.20 String Formatting in Hot Paths

`format!` allocates. In hot loops, use `write!` to a reused buffer.

### 9.21 `Vec::remove(0)`

`Vec::remove(0)` is O(n). For a queue, use `VecDeque`.

### 9.22 Manual Indexing in Loops

BAD:
```rust
for i in 0..vec.len() {
    process(vec[i]);
}
```

GOOD:
```rust
for item in &vec {
    process(item);
}
```

The iterator version is faster (bounds check eliminated) and safer.

### 9.23 `HashSet`/`HashMap` With Non-Cryptographic Hash

For untrusted input, `std::collections::HashMap` uses SipHash (safe).
Do not replace with `FxHashMap` or `AHash` for untrusted keys
without understanding hash-flooding.

### 9.24 `tokio::spawn` Without Handling the JoinHandle

A spawned task that panics disappears silently. Either await the
handle or log the outcome.

### 9.25 No `#[cfg(test)]` Module

Every module has unit tests in a `#[cfg(test)] mod tests`. Without
them, correctness is assumed.

## 10. Response to Violation

If a previous response violated a rule here:

```
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

No justification. No apology paragraph. Fix and move on.
