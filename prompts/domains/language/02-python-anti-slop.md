---
id: 02-python-anti-slop
title: "Python Anti-Slop Layer"
lang: en
depends_on: ["_universal/00-style-guide.md", "_universal/00-master-anti-slop.md", "domains/framework/02-architecture-anti-slop.md"]
category: domain
domain_type: language
version: 2
---

# Python Anti-Slop Layer

This file defines behavioral contracts specific to the Python language. It sits in the language layer, below the universal and architectural rules, and above framework-specific rules. It covers language semantics, mutability, type hints, async, packaging, and the common dynamic patterns that produce silent bugs. It does not cover framework rules (Django, FastAPI, Flask — see `domains/framework/`), delivery rules (see `domains/delivery/`), or universal security and fabrication rules (see `_universal/00-master-anti-slop.md`).

Python's value is its readability and dynamic flexibility; its danger is its implicit mutability, runtime type erasure, and historical quirks. Every rule below either prevents a class of silent bug or documents a modern idiom that replaces a legacy trap.

## Scope

This file applies to Python codebases targeting Python 3.10 or later, utilizing modern dependency management (`pyproject.toml` with `uv`, `poetry`, `hatch`, or `pdm`), and employing type hints.

### Version Applicability

- **Minimum version**: Python 3.10.
- **Features requiring specific versions**:
  - `match` statements: Python 3.10+.
  - `X | Y` union syntax in annotations: Python 3.10+.
  - `Self` type hint: Python 3.11+ (or `typing_extensions`).
  - `asyncio.TaskGroup`: Python 3.11+.
  - `type` statement: Python 3.12+.
- If the project targets 3.8 or 3.9, the version-specific syntax above is unavailable, but the remaining rules still apply.
- If the project does not use type hints, the type-hint sections can be skipped, but runtime validation rules still apply.

## Rule Severity

Severity follows `_universal/00-style-guide.md`.

## Contracts

A Python codebase commits to five contracts. The table below maps each contract to the rules that enforce it.

| Contract | Description | Enforced By |
|---|---|---|
| Type and Annotation Integrity | Type hints are modern, justified, and backed by runtime validation at boundaries. | PY-005 to PY-010 |
| Mutability and State Safety | Default arguments, shared references, and global state are strictly controlled. | PY-011 to PY-015, PY-063 |
| Control Flow and Exception Discipline | Exceptions are specific, chained, and never used for standard control flow. | PY-023 to PY-032 |
| Async and Concurrency Correctness | Event loops are not blocked, and thread/GIL boundaries are respected. | PY-033 to PY-038 |
| Packaging and Module Hygiene | Imports are clean, side-effect-free, and dependencies are managed via `pyproject.toml`. | PY-050 to PY-056 |

## Style and Tooling

### PY-001 — Formatter Adherence

**MUST**

The project's formatter (`black`, `ruff format`, or equivalent) MUST be followed. Code MUST NOT be hand-aligned, and a different line-length convention MUST NOT be introduced. Consistent formatting prevents review friction and merge conflicts.

### PY-002 — Linter Adherence

**MUST**

The project's linter configuration (`ruff`, `flake8`, `pylint`, `mypy`, `pyright`) MUST be matched. `# noqa` or `# type: ignore` MUST NOT be added without a reason comment. Suppressing linters hides real issues.

### PY-003 — Import Discipline

**MUST**

Standard library imports MUST come first, then third-party, then local. Wildcard imports (`from x import *`) MUST NOT be used, as they pollute the namespace and hide dependencies. Absolute imports SHOULD be preferred; relative imports SHOULD only be used when the project's pattern dictates. Imports inside functions MUST NOT be used unless solving a documented circular-import or startup-time problem.

### PY-004 — Naming Conventions

**MUST**

Python naming conventions MUST be followed: `snake_case` for functions, variables, and modules; `PascalCase` for classes; `UPPER_SNAKE_CASE` for module-level constants; leading underscore (`_name`) for internal helpers; and dunder (`__name__`) only for Python-defined protocols. `camelCase` MUST NOT be used in Python. Mixing conventions creates cognitive overhead.

## Types and Annotations

### PY-005 — Public Function Annotations

**MUST**

Every public function MUST have annotations on parameters and return types. Private functions (`_name`) may omit them if obvious, but consistency is preferred. Annotations serve as executable documentation and enable static analysis.

### PY-006 — Modern Annotation Syntax

**MUST**

Modern syntax MUST be used: `list[int]`, `dict[str, int]`, `tuple[int, ...]` instead of `typing.List`/`Dict`/`Tuple` (deprecated since 3.9); `X | Y` instead of `Union[X, Y]`; `X | None` instead of `Optional[X]`; and `Callable` from `collections.abc`. Modern syntax is clearer and natively supported by the interpreter.

### PY-007 — Type-Ignore Justification

**MUST**

Every `# type: ignore` MUST include the specific error code (e.g., `# type: ignore[arg-type]`) and a short reason. If the reason cannot be explained in one line, the annotation or code is wrong. Unjustified ignores hide real type errors.

### PY-008 — Runtime Validation at Boundaries

**MUST**

Type hints are not enforced at runtime. At API, config, and message boundaries, data MUST be validated with a runtime library (`pydantic`, `attrs` with validators, `marshmallow`, `cattrs`). Trusting type hints to protect against invalid external input leads to runtime crashes.

### PY-009 — `Any` Prohibition

**MUST NOT**

`Any` disables type checking for the value and everything it touches. `object`, a `Protocol`, or a generic MUST be preferred when the value can be anything but must be narrowed. `Any` is only permitted as a last resort for broken third-party stubs.

### PY-010 — Protocol Over ABC

**SHOULD**

For structural typing (duck typing), `typing.Protocol` SHOULD be used. Abstract Base Classes (ABCs) SHOULD be reserved for nominal inheritance hierarchies, not for "any class that has this method". Protocols align better with Python's dynamic nature.

## Mutability and State

### PY-011 — Mutable Default Arguments

**MUST NOT**

Mutable default arguments (e.g., `target=[]`) MUST NOT be used. The default persists across calls, causing shared state bugs. `None` MUST be used as the default, and the mutable object instantiated inside the function body.

Example (illustrative, Python):

BAD:
```python
def append_to(item, target=[]):
    target.append(item)
    return target
```

GOOD:
```python
def append_to(item, target=None):
    if target is None:
        target = []
    target.append(item)
    return target
```

### PY-012 — Dataclass Defaults

**MUST**

When using `@dataclass` with a mutable default (list, dict, set), `field(default_factory=list)` MUST be used. Bare mutable defaults are rejected by Python, but using `field` proactively prevents confusing errors and clarifies intent.

### PY-013 — Argument Mutation

**MUST NOT**

Functions MUST NOT modify collections passed as arguments unless the function's name explicitly indicates mutation (e.g., `append_`, `update_`). A new value MUST be returned instead. Silent mutation surprises callers and breaks memoization.

### PY-014 — Reference Sharing

**MUST**

Assigning a collection to another variable does not copy it. When an independent copy is needed, `copy.copy`, `copy.deepcopy`, or explicit construction (e.g., `list(items)`) MUST be used. Assuming assignment creates a copy leads to unintended side effects.

### PY-015 — Immutable Data Structures

**SHOULD**

When a value must not change, a `tuple` or `frozenset` SHOULD be used. This communicates intent and prevents accidental mutation.

## Equality and Identity

### PY-016 — `is` vs `==`

**MUST**

`is` compares identity (memory address); `==` compares value (calls `__eq__`). `is` MUST only be used for `None`, `True`, `False`, and guaranteed singletons. For everything else, `==` MUST be used. Using `is` for value comparison is unreliable due to Python's object interning quirks.

### PY-017 — `is None` Discipline

**MUST**

`x is None` and `x is not None` MUST be used instead of `x == None`. `==` can be overridden by custom classes, whereas `is` cannot.

### PY-018 — Collection Truthiness

**SHOULD**

Empty collections are falsy. `if items:` SHOULD be used instead of `if len(items) > 0:`. However, when values that can be falsy yet meaningful (e.g., `0`, `""`, `False`, `Decimal("0")`) are possible, explicit comparison MUST be used to avoid logic bugs.

## Functions and Control Flow

### PY-019 — Keyword-Only Booleans

**SHOULD**

Boolean parameters SHOULD be keyword-only (e.g., `def create_user(name, *, is_admin=False):`). This prevents callers from passing ambiguous positional booleans like `create_user("Alice", True)`.

### PY-020 — Early Return

**SHOULD**

Deeply nested conditionals SHOULD be avoided. The failure case SHOULD be returned early to flatten the control flow and improve readability.

### PY-021 — `*args` and `**kwargs` Discipline

**MUST NOT**

`*args` and `**kwargs` MUST NOT be used without a documented reason. They hide the signature from tooling and callers. They SHOULD only be used when forwarding to a wrapped function or implementing a decorator.

### PY-022 — Function Length

**SHOULD**

A function over 50 lines is usually doing more than one thing. Functions SHOULD be split when each part has an independent responsibility.

## Exceptions and Context Managers

### PY-023 — Specific Exception Catching

**MUST**

Specific exceptions (e.g., `ValueError`, `KeyError`) MUST be caught. Catching the broad `Exception` class swallows programming errors and makes debugging impossible.

### PY-024 — Bare `except:` Prohibition

**MUST NOT**

Bare `except:` MUST NOT be used. It catches `SystemExit` and `KeyboardInterrupt`, preventing the application from being terminated gracefully. It MUST only be used in top-level application code with an immediate re-raise.

### PY-025 — Empty Catch and Rethrow

**MUST NOT**

A `try...except` block that catches an exception and immediately re-raises it without modification adds nothing and MUST NOT exist.

### PY-026 — Exception Chaining

**MUST**

When wrapping an exception, `raise NewError(...) from original_error` MUST be used. Failing to use `from` loses the original traceback, making root-cause analysis difficult.

### PY-027 — Custom Exception Hierarchies

**SHOULD**

Project exceptions SHOULD inherit from a base class (e.g., `AppError`). This allows callers to catch the base for all application errors, or a specific subclass for fine-grained handling.

### PY-028 — Exceptions for Control Flow

**MUST NOT**

Exceptions MUST NOT be used for expected branches (e.g., using `KeyError` to check dictionary membership). Methods like `.get()` MUST be used. Exceptions are for exceptional cases.

### PY-029 — Resource Cleanup

**MUST**

Garbage collection MUST NOT be relied upon for resource cleanup. Context managers (`with open(...) as f:`) or `try/finally` blocks MUST be used to ensure resources are released.

### PY-030 — `with` Over Manual `try/finally`

**MUST**

The `with` statement MUST be preferred over manual `try/finally` blocks for context management. It is less error-prone and more readable.

### PY-031 — Multiple Resources

**SHOULD**

Multiple resources SHOULD be managed in a single `with` statement (e.g., `with open(src) as fin, open(dst, "w") as fout:`) rather than nested `with` blocks, when supported.

### PY-032 — Custom Context Managers

**SHOULD**

`@contextlib.contextmanager` SHOULD be used for generator-based context managers. A class-based approach SHOULD only be used when the state is complex or the manager is reused heavily.

## Async and Concurrency

### PY-033 — `async def` Justification

**MUST NOT**

A function that never `await`s anything MUST NOT be declared `async def`. It adds overhead and forces callers to await it unnecessarily.

### PY-034 — Parallel Async Execution

**SHOULD**

When order does not matter and parallel execution is safe, `asyncio.gather` or `asyncio.TaskGroup` (3.11+) SHOULD be used instead of awaiting sequentially in a `for` loop.

### PY-035 — Blocking Calls in Async

**MUST NOT**

Blocking calls (synchronous file I/O, `requests`, `time.sleep`) MUST NOT be used in async code, as they block the entire event loop. Async libraries (`aiofiles`, `httpx`, `asyncio.sleep`) or `asyncio.to_thread` MUST be used.

### PY-036 — Cancellation Handling

**MUST**

Async tasks MUST handle `asyncio.CancelledError` correctly. It MUST NOT be swallowed. Resources MUST be cleaned up and the error re-raised.

### PY-037 — GIL and CPU Parallelism

**MUST**

Threads do not provide CPU parallelism in CPython due to the Global Interpreter Lock (GIL). For CPU-bound work, `multiprocessing` or `concurrent.futures.ProcessPoolExecutor` MUST be used.

### PY-038 — Thread State Synchronization

**MUST**

Mutable state (lists, dicts, counters) shared across threads MUST be protected with explicit synchronization (`threading.Lock`, `queue.Queue`). Unsynchronized shared state causes race conditions.

## Data Structures and Iteration

### PY-039 — `@dataclass` Over Manual `__init__`

**SHOULD**

For simple value objects, `@dataclass` SHOULD be used instead of manual `__init__`, `__repr__`, and `__eq__` methods. It reduces boilerplate and prevents implementation bugs.

### PY-040 — Frozen Dataclasses

**SHOULD**

`@dataclass(frozen=True)` SHOULD be used for value objects to prevent attribute mutation and enforce immutability.

### PY-041 — `NamedTuple` for Tuple-Like

**SHOULD**

When a value must behave exactly like a tuple (unpacking, indexing, hashability), `NamedTuple` SHOULD be used. Otherwise, a dataclass is preferred.

### PY-042 — `dict` vs Dataclass

**MUST NOT**

A `dict` MUST NOT be used to represent structured data with known keys (e.g., returning `{"name": ..., "email": ...}`). A dataclass or `TypedDict` MUST be used to provide explicit shape and tooling support.

### PY-043 — Comprehensions Over `map`/`filter`

**SHOULD**

List comprehensions SHOULD be preferred over `map` and `filter` with `lambda` functions for readability and Pythonic style.

### PY-044 — Comprehension Side Effects

**MUST NOT**

Comprehensions MUST NOT be used for side effects (e.g., `[print(x) for x in items]`). A comprehension builds a collection; if the collection is discarded, a standard `for` loop MUST be used.

### PY-045 — `enumerate` and `zip`

**SHOULD**

`enumerate` SHOULD be used instead of `range(len(...))` for indexed iteration. `zip` SHOULD be used for parallel iteration over multiple sequences.

### PY-046 — `dict.items()`

**SHOULD**

`dict.items()` SHOULD be used for key-value iteration instead of looking up values via `my_dict[key]` inside a loop over keys.

### PY-047 — Generators for Large Data

**SHOULD**

For large or streaming data, generator expressions (e.g., `(x * x for x in range(1_000_000))`) SHOULD be used instead of list comprehensions to avoid materializing the entire collection in memory.

## Modules and Packaging

### PY-048 — `__main__` Guard

**MUST**

Every script that is also importable MUST have the `if __name__ == "__main__":` guard. Code inside it runs only when the file is executed directly, preventing unintended execution on import.

### PY-049 — Import-Time Side Effects

**MUST NOT**

Importing a module MUST NOT perform I/O, network calls, or mutate global state. Import-time side effects make testing and tooling unpredictable.

### PY-050 — `__init__.py` Discipline

**MUST NOT**

`__init__.py` MUST NOT be used as a barrel that re-exports everything. This creates import cycles, slows startup, and breaks tree-shaking.

### PY-051 — `sys.path` Manipulation

**MUST NOT**

`sys.path.append` MUST NOT be used in library or application code. Proper packaging (`pyproject.toml`) or relative imports MUST be used instead.

### PY-052 — `pyproject.toml` Exclusivity

**MUST**

If the project uses `pyproject.toml`, `setup.py` and `setup.cfg` MUST NOT be added. If it uses `uv` or `poetry`, `requirements.txt` MUST NOT be added. Mixing packaging systems causes dependency resolution conflicts.

### PY-053 — Version Pinning Consistency

**MUST**

The project's convention for version pinning MUST be matched. If the project pins exact versions, ranges MUST NOT be added, and vice versa.

### PY-054 — Dependency Addition

**MUST NOT**

A new dependency MUST NOT be added without explicit permission. The Python ecosystem has many overlapping libraries (e.g., `requests` vs `httpx`, `attrs` vs `pydantic`). Adding one when another is present is a maintenance cost.

See MAS-014 in `_universal/00-master-anti-slop.md`.

## Traps from Other Languages

### PY-071 — Java/C++ Class Overuse

**SHOULD NOT**

Python favors modules, functions, and dictionaries. Reaching for a class with static methods or deep inheritance hierarchies (as in Java/C++) SHOULD NOT be done when a module of functions or a dataclass is clearer.

### PY-072 — JS/TS Implicit Undefined

**MUST NOT**

JavaScript relies on `undefined` for missing properties. In Python, accessing a missing key raises `KeyError`, and missing attributes raise `AttributeError`. Code MUST NOT assume missing values silently evaluate to `None` or falsy; `.get()` or `hasattr` MUST be used explicitly.

### PY-073 — Go Error Return Tuples

**SHOULD NOT**

Go returns `(result, error)`. Python uses exceptions. Inventing a `(result, error)` tuple convention SHOULD NOT be done unless the project already uses it. Python functions SHOULD raise exceptions on failure.

### PY-074 — Rust Compile-Time Mutability

**MUST**

Rust enforces mutability at compile time (`mut`). Python does not. Developers coming from Rust MUST remember that Python variables are just labels, and passing a list to a function allows the function to mutate the caller's data unless explicitly protected (see PY-013).

## AI-Specific Python Discipline

### PY-080 — Python API Verification

**MUST**

Before using a standard library function or third-party API, the assistant MUST verify its signature and behavior in the target Python version. Python APIs change frequently between minor versions (e.g., `datetime.utcnow()` deprecation, `asyncio` loop policies). Invented APIs produce `AttributeError` at runtime.

See MAS-036 in `_universal/00-master-anti-slop.md`.

### PY-081 — Existing Utility Discovery

**MUST**

Before writing a new utility function or importing a new third-party library for a common task (e.g., date parsing, HTTP requests, data validation), the assistant MUST search the project's existing dependencies and `stdlib`. Inventing parallel utilities fragments the codebase.

See MAS-035 in `_universal/00-master-anti-slop.md`.

### PY-082 — Metaprogramming Restraint

**SHOULD**

The assistant SHOULD NOT introduce advanced metaprogramming (metaclasses, `__new__`, descriptor protocols, runtime code generation) unless the project already uses them and the task strictly requires them. These patterns defeat static analysis and are a common source of AI-generated bugs.

See MAS-038 in `_universal/00-master-anti-slop.md`.

## Anti-Patterns

### PY-055 — String Formatting Consistency

**MUST**

f-strings MUST be used for string formatting in Python 3.6+. `str.format` SHOULD only be used when f-strings are not possible (e.g., deferred logging). `%` formatting MUST NOT be used in new code. String concatenation MUST NOT be used for more than two parts.

### PY-056 — Chained Comparison Clarity

**SHOULD**

`a < b < c` is valid Python, but it is not always what readers expect. It SHOULD only be used when the meaning is genuinely a mathematical range check.

### PY-057 — `eval` and `exec` Prohibition

**MUST NOT**

`eval` and `exec` MUST NOT be used on untrusted input, and SHOULD NOT be used on any input. They exist for narrow metaprogramming cases that are almost never justified and introduce critical security vulnerabilities.

### PY-058 — `assert` for Runtime Validation

**MUST NOT**

`assert` is removed when Python runs with the `-O` (optimize) flag. It MUST NOT be used for validation that must run in production. Explicit `if ... raise` MUST be used.

Example (illustrative, Python):

BAD:
```python
def withdraw(amount):
    assert amount > 0
```

GOOD:
```python
def withdraw(amount):
    if amount <= 0:
        raise ValueError("amount must be positive")
```

### PY-059 — Timezone-Aware Datetimes

**MUST NOT**

`datetime.utcnow()` returns a naive datetime with no timezone information and is deprecated. `datetime.now(timezone.utc)` MUST be used for timezone-aware values.

### PY-060 — `print` for Logging

**MUST NOT**

`print` MUST NOT be used for application logging. It bypasses the logging configuration and cannot be filtered, formatted, or redirected. A configured `logger` MUST be used.

### PY-061 — Global Mutable State

**MUST NOT**

Module-level mutable state (e.g., `cache = {}`) MUST NOT be shared across callers. It breaks testing and creates hidden coupling. Dependencies MUST be passed explicitly.

### PY-062 — `pathlib` Over `os.path`

**SHOULD**

`pathlib.Path` SHOULD be used for path manipulation instead of `os.path`. It is cross-platform, object-oriented, and less error-prone.

### PY-063 — `timedelta` for Datetime Arithmetic

**MUST NOT**

Integers MUST NOT be added directly to a `datetime`. `timedelta` MUST be used for all datetime arithmetic to prevent unit confusion and errors.

### PY-064 — `deque` for FIFO Queues

**MUST NOT**

`list.pop(0)` is O(n) and MUST NOT be used for FIFO queues. `collections.deque` MUST be used, as it provides O(1) appends and pops from both ends.

### PY-065 — Bounded Caches

**MUST NOT**

An unbounded `dict` used as a cache grows forever and causes memory leaks. `functools.lru_cache` with a `maxsize`, or `functools.cache` (only when the argument set is strictly bounded and small), MUST be used.

### PY-066 — `isinstance` Chain Prohibition

**SHOULD NOT**

Long `if/elif` chains of `isinstance` checks defeat polymorphism. A common base class with a method, or `functools.singledispatch`, SHOULD be used instead.

### PY-067 — Comprehension Complexity Limit

**MUST NOT**

Comprehensions with more than two `for` clauses or complex nested `if` conditions are unreadable and MUST NOT be used. A generator function or a standard loop MUST be extracted.

### PY-068 — Dict Iteration Order Assumptions

**MUST NOT**

While Python 3.7+ preserves insertion order in `dict`, business logic MUST NOT rely on this implicitly. If order matters for correctness, `OrderedDict` or explicit sorting MUST be used to make the intent clear.

### PY-069 — Silent `except: pass`

**MUST NOT**

Catching an exception and silently passing (`except Exception: pass`) is prohibited. It hides bugs and makes debugging impossible. Errors MUST be logged, re-raised, or explicitly handled.

## Response to Violation

When a rule in this file is violated, report:

Violation: PY-{NNN}
Reason: {one-line reason}
Correction: {smallest fix}

For multiple violations, report each rule ID separately.

Do not replace a technical correction with a generic explanation.