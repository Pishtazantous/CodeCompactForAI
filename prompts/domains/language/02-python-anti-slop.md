---
id: 02-python-anti-slop
title: "Python Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: language
version: 1
---

# Python Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
security anti-patterns, output format) are NOT repeated here.

This file covers rules specific to Python: language semantics, mutability,
type hints, async, packaging, and the common dynamic patterns that produce
silent bugs. Framework rules (Django, FastAPI, Flask) live in
`domains/framework/`. This file applies to Python 3.10 or later unless
the project's configuration says otherwise.

## 1. Stack Assumptions

This layer assumes:

- Python 3.10 or later. If the project targets 3.8 or 3.9, some syntax
  (notably `match`, `X | Y` in annotations, `Self`) is unavailable.
- Type hints are used in the project. If not, this file still applies
  but the type-hint sections can be skipped.
- The project uses a modern dependency manager (`pyproject.toml` with
  `uv`, `poetry`, `hatch`, or `pdm`). If it still uses `requirements.txt`,
  match the project.

## 2. Style and Tooling

### 2.1 Follow the Project's Formatter

Match the project's formatter (`black`, `ruff format`, or equivalent).
Do not hand-align code, do not fight the formatter, and do not introduce
a different line-length convention.

### 2.2 Follow the Project's Linter

Match the project's linter configuration (`ruff`, `flake8`, `pylint`,
`mypy`, `pyright`). Do not add `# noqa` or `# type: ignore` without a
reason comment.

### 2.3 Imports

- Standard library imports first, then third-party, then local. The
  formatter usually handles this; follow it.
- Never use wildcard imports (`from x import *`). They pollute the
  namespace and hide what is used.
- Prefer absolute imports. Use relative imports only when the project's
  pattern does.
- Never import inside a function unless it solves a real circular-import
  or startup-time problem. Document the reason when you do.

### 2.4 Naming

- `snake_case` for functions, variables, and modules.
- `PascalCase` for classes.
- `UPPER_SNAKE_CASE` for module-level constants.
- Leading underscore (`_name`) for internal helpers.
- Dunder (`__name__`) only for Python-defined protocols.

Do not mix conventions. Do not use `camelCase` in Python.

## 3. Types and Annotations

### 3.1 Annotate Public Functions

Every public function has annotations on parameters and return type.
Private functions (`_name`) may omit if obvious, but consistency is
preferred.

### 3.2 Modern Annotation Syntax

- Use `list[int]`, `dict[str, int]`, `tuple[int, ...]` instead of
  `List`, `Dict`, `Tuple` from `typing` (deprecated since 3.9).
- Use `X | Y` instead of `Union[X, Y]` (since 3.10).
- Use `X | None` instead of `Optional[X]`.
- Use `Callable[[int], str]` from `collections.abc`, not `typing`.

### 3.3 No Type-Ignore Without a Reason

`# type: ignore` suppresses a real error. Always add the specific code
(`# type: ignore[arg-type]`) and a short reason. If you cannot explain
the reason in one line, the annotation is wrong.

### 3.4 Runtime vs Static Types

Type hints are not enforced at runtime. At API, config, and message
boundaries, validate with a runtime library (`pydantic`, `attrs` with
validators, `marshmallow`, `cattrs`). Do not trust the type hint to
protect you.

### 3.5 `Any` Is a Last Resort

`Any` disables type checking for the value. Prefer `object` when the
value can be anything but must be narrowed, or a protocol, or a generic.

### 3.6 Protocol Over ABC

For structural typing, use `typing.Protocol`. Abstract base classes are
for inheritance hierarchies, not for "any class that has this method".

## 4. Mutability

### 4.1 Never Use Mutable Default Arguments

BAD:
python
def append_to(item, target=[]):
    target.append(item)
    return target
Every call shares the same list. The default persists across calls.

GOOD:

python
def append_to(item, target=None):
    if target is None:
        target = []
    target.append(item)
    return target
Or use an immutable default (target: tuple = ()) and return a new
collection.

4.2 Dataclass Defaults
@dataclass with a mutable default (list, dict, set) requires
field(default_factory=list). Python will reject the bare mutable
default, but the error message is confusing, so use field proactively
for any non-trivial type.

4.3 Do Not Mutate Function Arguments
Unless the function's name says it mutates (append_, update_), do
not modify collections passed in. Return a new value instead.

BAD:

python
def normalize(items):
    items.sort()
    return items
GOOD:

python
def normalize(items):
    return sorted(items)
4.4 dict, list, set Are Mutable and Shared by Reference
Assigning a collection to another variable does not copy it. Use
copy.copy for a shallow copy, copy.deepcopy for a deep copy, or
construct a new collection explicitly.

BAD:

python
new_items = items  # same list
new_items.append(x)  # mutates items too
GOOD:

python
new_items = list(items)
4.5 Tuples and frozenset for Immutable Data
When a value must not change, use a tuple or frozenset. This
communicates intent and prevents accidental mutation.

5. Equality and Identity
5.1 is vs ==
is compares identity (same object in memory).

== compares value (calls __eq__).

Use is only for None, True, False, and singletons (rare). For
everything else, use ==.

BAD:

python
if value is 5:  # identity check on an int, unreliable
GOOD:

python
if value == 5:
5.2 is None and is not None
This is the one place is is preferred. x is None cannot be
overridden; x == None can, and some libraries do.

5.3 Truthiness of Collections
BAD:

python
if len(items) > 0:
GOOD:

python
if items:
But be careful with values that can be falsy yet meaningful (0, "",
False, Decimal("0")). Explicit comparison is clearer when those are
possible.

6. Functions
6.1 Keyword-Only Arguments for Booleans
BAD:

python
def create_user(name, is_admin):
    ...
create_user("Alice", True)  # what does True mean?
GOOD:

python
def create_user(name, *, is_admin=False):
    ...
create_user("Alice", is_admin=True)
6.2 Return Early
Avoid deeply nested conditionals. Return the failure case first.

6.3 Do Not Use *args and **kwargs Without a Reason
They hide the signature from tooling and from the caller. Use them only
when forwarding to a wrapped function or implementing a decorator.

6.4 Function Length
A function over 50 lines is usually doing more than one thing. Split
only when each part has an independent responsibility.

7. Exceptions
7.1 Catch Specific Exceptions
BAD:

python
try:
    do_work()
except Exception:
    pass
This swallows KeyboardInterrupt (which is not an Exception but a
BaseException in most contexts, so it slips through) and every
programming error.

GOOD:

python
try:
    do_work()
except ValueError as error:
    logger.warning("invalid input: %s", error)
    raise
7.2 Never Bare except:
Bare except: catches SystemExit and KeyboardInterrupt. Only use it
in top-level application code with a re-raise.

7.3 Do Not Catch and Rethrow Unchanged
BAD:

python
try:
    do_work()
except ValueError:
    raise
The try / except adds nothing. Remove it.

7.4 Use raise X from Y to Chain
BAD:

python
try:
    load_config()
except OSError as error:
    raise ConfigError("cannot load config")
This loses the original traceback. Use from:

GOOD:

python
try:
    load_config()
except OSError as error:
    raise ConfigError("cannot load config") from error
7.5 Custom Exception Hierarchies
Project exceptions inherit from a base class:

python
class AppError(Exception): ...
class NotFoundError(AppError): ...
class ValidationError(AppError): ...
Callers can catch the base for all application errors, or a specific
subclass for fine-grained handling.

7.6 Do Not Use Exceptions for Control Flow
BAD:

python
try:
    value = my_dict[key]
except KeyError:
    value = default
GOOD:

python
value = my_dict.get(key, default)
Use exceptions for exceptional cases, not for expected branches.

7.7 Cleanup With with or try/finally
Never rely on garbage collection for resource cleanup. Use context
managers (with open(...) as f) or try/finally.

8. Context Managers
8.1 Prefer with Over Manual try/finally
BAD:

python
f = open(path)
try:
    data = f.read()
finally:
    f.close()
GOOD:

python
with open(path) as f:
    data = f.read()
8.2 Multiple Resources in One with
python
with open(src) as fin, open(dst, "w") as fout:
    fout.write(fin.read())
8.3 Custom Context Managers
Use @contextlib.contextmanager for generator-based context managers.
Use a class only when the state is complex or the manager is reused
heavily.

9. Async and Concurrency
9.1 async def Only When You Actually Await
A function that never awaits anything does not need to be async. It
adds overhead and forces callers to await it for no reason.

BAD:

python
async def get_name(user):
    return user.name
GOOD:

python
def get_name(user):
    return user.name
9.2 Do Not await in a Loop When Parallel Is Safe
BAD:

python
for url in urls:
    result = await fetch(url)
This is sequential. If order does not matter:

GOOD:

python
results = await asyncio.gather(*(fetch(url) for url in urls))
Use asyncio.gather when all results are needed.
Use asyncio.TaskGroup (3.11+) for structured concurrency with error
handling.

9.3 Never Call Blocking Functions in Async Code
Blocking calls (file I/O, requests, time.sleep`) block the entire
event loop. Use:

An async library (aiofiles, httpx, asyncio.sleep).

asyncio.to_thread for unavoidable blocking calls.

9.4 Cancellation
Async tasks must handle asyncio.CancelledError correctly. Do not
swallow it. Clean up resources and re-raise.

9.5 Threads and GIL
Threads do not give CPU parallelism in CPython (they give I/O
concurrency). For CPU-bound work, use multiprocessing or
concurrent.futures.ProcessPoolExecutor.

9.6 Never Share Mutable State Across Threads Without a Lock
Lists, dicts, and counters modified from multiple threads need explicit
synchronization (threading.Lock, queue.Queue).

10. Data Classes and Types
10.1 @dataclass Over Manual __init__
For simple value objects:

BAD:

python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __repr__(self):
        return f"Point({self.x}, {self.y})"
    def __eq__(self, other):
        return isinstance(other, Point) and self.x == other.x and self.y == other.y
GOOD:

python
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: float
    y: float
10.2 Frozen Dataclasses for Immutability
@dataclass(frozen=True) prevents attribute mutation. Use it for value
objects.

10.3 NamedTuple for Tuple-Like
When the value must behave like a tuple (unpacking, indexing),
NamedTuple is correct. Otherwise, use a dataclass.

10.4 pydantic for Validation
At input boundaries (API payloads, config files), use pydantic
(if the project uses it) to parse and validate. The type hints alone do
not validate.

10.5 Do Not Use dict Where a Dataclass Fits
BAD: Returning {"name": ..., "email": ...} and documenting the keys in
a comment.

GOOD: Returning a dataclass or a TypedDict with explicit keys.

11. Iteration and Comprehensions
11.1 List Comprehensions Over map/filter
BAD:

python
result = list(map(lambda x: x * 2, items))
GOOD:

python
result = [x * 2 for x in items]
11.2 Do Not Use Comprehensions for Side Effects
BAD:

python
[print(x) for x in items]
GOOD:

python
for x in items:
    print(x)
A comprehension builds a list. If the list is discarded, the loop was
wrong.

11.3 enumerate Over range(len(...))
BAD:

python
for i in range(len(items)):
    print(i, items[i])
GOOD:

python
for i, item in enumerate(items):
    print(i, item)
11.4 zip for Parallel Iteration
BAD:

python
for i in range(len(a)):
    print(a[i], b[i])
GOOD:

python
for x, y in zip(a, b):
    print(x, y)
11.5 dict.items for Key-Value Iteration
BAD:

python
for key in my_dict:
    value = my_dict[key]
GOOD:

python
for key, value in my_dict.items():
    ...
11.6 Generators for Large Data
A list comprehension materializes the entire list. For large or
streaming data, use a generator expression:

python
sum(x * x for x in range(1_000_000))
12. Modules and Packages
12.1 if __name__ == "__main__":
Every script that is also importable has this guard. Code inside it runs
only when the file is executed directly.

12.2 No Side Effects at Import Time
Importing a module must not perform I/O, network calls, or mutate
global state. Import-time side effects make testing and tooling
unpredictable.

12.3 __init__.py Should Be Empty or Minimal
Do not use __init__.py as a barrel that re-exports everything. It
creates import cycles and slows startup.

12.4 Avoid sys.path Manipulation
Never sys.path.append in library code. Use proper packaging
(pyproject.toml) or relative imports.

13. Packaging and Dependencies
13.1 pyproject.toml Only
Do not add setup.py or setup.cfg if the project uses
pyproject.toml. Do not add a requirements.txt if the project uses
uv or poetry.

13.2 Pin vs Range
Match the project's convention for version pinning. If the project pins
exact versions, do not add a range. If it uses ranges, do not add
exact pins.

13.3 Never Add a Dependency Without Permission
Universal rule 3.5 applies with extra weight in Python: the ecosystem
has many overlapping libraries (requests vs httpx vs aiohttp,
attrs vs dataclasses vs pydantic). Adding one when another is
already present is a maintenance cost.

14. Python-Specific Anti-Patterns
14.1 Mutable Default Arguments
Covered in 4.1. This is the single most common Python bug.

14.2 Bare except:
Covered in 7.2.

14.3 from module import *
Covered in 2.3.

14.4 String Formatting Inconsistency
Pick one style for the project:

f-strings (preferred for 3.6+).

str.format (only when f-strings are not possible).

Never % formatting in new code. Never concatenation for anything more
than two parts.

14.5 Chained Comparison Confusion
a < b < c is valid Python and means a < b and b < c. It is not
always what readers expect. Use it only when the meaning is genuinely
that.

14.6 range and len for Iteration
Covered in 11.3.

14.7 Manual Resource Cleanup
Covered in 8.1.

14.8 eval and exec
Never use them on untrusted input. Never use them on any input. They
exist for very narrow metaprogramming cases that are almost never
justified.

14.9 assert for Runtime Validation
assert is removed when Python runs with -O. Never use it for
validation that must run in production. Use explicit if ... raise.

BAD:

python
def withdraw(amount):
    assert amount > 0
    ...
GOOD:

python
def withdraw(amount):
    if amount <= 0:
        raise ValueError("amount must be positive")
    ...
14.10 datetime.utcnow() Without Timezone
datetime.utcnow() returns a naive datetime with no timezone
information. Use datetime.now(timezone.utc) for timezone-aware
values.

BAD:

python
from datetime import datetime
now = datetime.utcnow()
GOOD:

python
from datetime import datetime, timezone
now = datetime.now(timezone.utc)
14.11 print for Logging
BAD: print(f"user logged in: {user.id}")
GOOD: logger.info("user logged in", extra={"user_id": user.id})

print bypasses the logging configuration and cannot be filtered or
redirected.

14.12 Global State
Module-level mutable state is shared across all callers. It breaks
testing and creates hidden coupling. Prefer passing dependencies
explicitly.

14.13 os.path in New Code
Use pathlib.Path for path manipulation. It is cross-platform and
object-oriented.

BAD:

python
import os
full = os.path.join(base, "sub", "file.txt")
GOOD:

python
from pathlib import Path
full = Path(base) / "sub" / "file.txt"
14.14 datetime Arithmetic Without timedelta
Do not add seconds as integers to a datetime. Use timedelta.

14.15 list as a Queue
list.pop(0) is O(n). Use collections.deque for FIFO.

14.16 Manual Cache Without Bounds
An unbounded dict used as a cache grows forever. Use
functools.lru_cache with a maxsize, or functools.cache only when
the argument set is bounded and small.

14.17 isinstance Chains
BAD:

python
if isinstance(x, A):
    ...
elif isinstance(x, B):
    ...
elif isinstance(x, C):
    ...
This defeats polymorphism. Use a common base with a method, or
functools.singledispatch.

14.18 Deeply Nested Comprehensions
A comprehension with two for clauses and two if clauses is
unreadable. Extract a generator function or a loop.

14.19 Silent except: pass
Covered in 7.1 and 7.2. This is the second most common Python bug.

14.20 dict Iteration Order Assumptions Across Versions
Since Python 3.7, dict preserves insertion order. Do not rely on
this for business logic; if order matters, use OrderedDict or sort
explicitly.

15. Response to Violation
If a previous response violated a rule here:

text
In the previous response, [specific rule] was violated. Correction:
[corrected code]
No justification. No apology paragraph. Fix and move on.

text

---
