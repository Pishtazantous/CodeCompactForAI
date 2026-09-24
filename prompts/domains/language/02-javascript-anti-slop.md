---
id: 02-javascript-anti-slop
title: "JavaScript Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: language
version: 1
---

# JavaScript Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
security anti-patterns, output format) are NOT repeated here.

This file covers rules specific to JavaScript: language semantics,
equality, coercions, scope, async, modules, and the common dynamic
patterns that produce silent bugs. Framework rules (React, Vue, Node
runtime) live in `domains/framework/`. Rules for TypeScript live in
`02-typescript-anti-slop.md` and take precedence when both apply.

## 1. Stack Assumptions

This layer assumes:

- Modern ECMAScript (ES2020 or later), as configured by the project's
  `package.json`, `tsconfig.json`, or bundler.
- Modules (ESM `import` / `export`) unless the project explicitly uses
  CommonJS.
- Async/await is available and preferred over raw Promises for control
  flow.
- The runtime may be Node.js, a browser, Deno, Bun, or a worker. Rules
  that depend on the host environment are noted.

## 2. Strict Mode and Modern Syntax

### 2.1 Strict Mode Is On

ES modules are always strict. CommonJS files must have `"use strict"`
at the top, or the project's pattern must enforce it. Never rely on
sloppy mode behavior.

### 2.2 `var` Is Forbidden

Use `const` by default. Use `let` only when the binding is reassigned.
Never use `var`: it is function-scoped, hoisted in confusing ways, and
has no place in modern code.

BAD:
javascript
var count = 0;
for (var i = 0; i < 10; i++) { /* ... */ }
GOOD:

javascript
let count = 0;
for (let i = 0; i < 10; i++) { /* ... */ }
2.3 const by Default
A binding that is never reassigned is const. The presence of let
should be a signal that reassignment happens in this scope.

const does not make objects immutable; it prevents rebinding. Do not
confuse the two.

2.4 Arrow Functions
Use arrow functions when the lexical this is intended. Use function
declarations for named top-level functions, especially when hoisting is
desired or when the function is used as a constructor.

Do not use arrow functions for methods on objects that need this.

3. Equality
3.1 === and !== Only
== and != perform type coercion with rules that are widely
misunderstood. Use === and !== everywhere.

The only accepted exception is value == null, which is true for both
null and undefined. Even this is a project-specific convention;
match what the project uses.

BAD:

javascript
if (x == 0) { /* true for "", [], "0" */ }
GOOD:

javascript
if (x === 0) { /* true only for the number 0 */ }
3.2 Object.is for Edge Cases
For NaN and -0 distinctions, use Object.is:

javascript
Object.is(NaN, NaN); // true
Object.is(-0, 0);    // false
3.3 Comparing Objects by Reference
Two object literals with the same content are not equal. Never use ===
to compare objects. Use a deep-equal utility from the project (or
compare fields explicitly).

4. Coercion and Truthiness
4.1 Explicit Coercion
Never rely on implicit coercion in a branch or a comparison.

BAD:

javascript
if (userInput) { /* true for "0", false for "" */ }
GOOD:

javascript
if (userInput.length > 0) { /* explicit */ }
4.2 Boolean(x) vs !!x
Both are explicit. Pick one and be consistent. !!x is shorter and
conventional; Boolean(x) is clearer.

4.3 Numeric Conversion
Number(x) and parseInt(x, 10) do different things. Number("") is
0. parseInt("") is NaN. Match the intent.

Always pass the radix to parseInt. Without it, leading-zero strings
may be parsed as octal in older engines, and linters flag it anyway.

4.4 + Overloads
+ concatenates strings and adds numbers. When both operands are not
the same type, the result is a string. Convert explicitly before
addition:

BAD:

javascript
const total = "5" + 3; // "53"
GOOD:

javascript
const total = Number("5") + 3; // 8
4.5 Template Literals
Use template literals for interpolation, not string concatenation:

BAD:

javascript
const url = "/users/" + id + "/posts";
GOOD:

javascript
const url = `/users/${id}/posts`;
4.6 null vs undefined
Pick one for "no value" and be consistent. In most modern projects, use
undefined for "missing" and reserve null for "explicitly empty"
(especially when it comes from a JSON payload).

Never mix them within a single API or type.

5. Scope and Hoisting
5.1 Block Scope
let and const are block-scoped. Do not declare a variable outside
the block where it is used.

5.2 Function Hoisting
Function declarations hoist. Function expressions and arrow functions
do not. Rely on this intentionally, never accidentally.

5.3 Temporal Dead Zone
Accessing a let or const before its declaration throws. This is a
feature: it catches bugs. Do not work around it by moving declarations
to the top of a file "just in case".

5.4 No Implicit Globals
Assigning to an undeclared variable creates a global. In strict mode
this throws, which is good. Never rely on the sloppy mode behavior.

BAD:

javascript
function setup() {
  config = {}; // creates global `config`
}
GOOD:

javascript
function setup() {
  const config = {};
  return config;
}
6. Objects and Arrays
6.1 Destructuring Over Property Access
When reading multiple properties from the same object:

BAD:

javascript
const name = user.name;
const email = user.email;
const role = user.role;
GOOD:

javascript
const { name, email, role } = user;
6.2 Default Values in Destructuring
Use defaults for optional fields:

javascript
const { limit = 20, offset = 0 } = options;
Do not then write limit = limit || 20 inside the body.

6.3 Rest and Spread
Use rest (...rest) for grouping remaining properties. Use spread
(...obj) for merging. Do not mutate inputs:

BAD:

javascript
function update(target, source) {
  Object.assign(target, source); // mutates target
  return target;
}
GOOD:

javascript
function update(target, source) {
  return { ...target, ...source };
}
6.4 Object.freeze for Constants
For module-level lookup tables that must not be mutated, use
Object.freeze or as const (TypeScript):

javascript
const STATUSES = Object.freeze({
  ACTIVE: "active",
  INACTIVE: "inactive",
});
Freezing is shallow. Nested objects remain mutable unless frozen
recursively.

6.5 Array Methods Over Loops
Prefer map, filter, reduce, find, some, every, flatMap
over manual for loops for transformations. Use for...of when the
loop has side effects or early exit.

Do not use .forEach for transformations; it discards the return
value and forces mutation.

BAD:

javascript
const names = [];
users.forEach(u => names.push(u.name));
GOOD:

javascript
const names = users.map(u => u.name);
6.6 Never Mutate Function Arguments
A function that mutates its arguments surprises callers and breaks
memoization. Return a new value instead.

Exception: the function's name explicitly says it mutates
(sortInPlace, pushItem), or the project's pattern is mutation-based
(rare, and usually a mistake).

6.7 Array.prototype.sort Mutates
sort sorts in place and returns the same array. If the input must not
change, copy first:

javascript
const sorted = [...items].sort((a, b) => a.rank - b.rank);
6.8 includes vs indexOf
Use includes for existence checks. indexOf is only for finding an
index.

BAD: if (arr.indexOf(x) !== -1)
GOOD: if (arr.includes(x))

6.9 Set for Uniqueness
For removing duplicates or fast lookups, use Set, not an array scan.

BAD:

javascript
if (items.filter(i => i === x).length > 0) { /* ... */ }
GOOD:

javascript
const seen = new Set(items);
if (seen.has(x)) { /* ... */ }
7. Functions
7.1 Default Parameters
Use default parameters, not || inside the body:

BAD:

javascript
function greet(name) {
  name = name || "world";
}
GOOD:

javascript
function greet(name = "world") { /* ... */ }
|| treats 0, "", and false as missing. Default parameters do
not.

7.2 Named Parameters via Object Destructuring
For functions with more than three parameters, use an options object:

BAD:

javascript
function createUser(name, email, role, active, sendEmail) { /* ... */ }
GOOD:

javascript
function createUser({ name, email, role, active = true, sendEmail = false }) { /* ... */ }
7.3 Return Early
Do not nest conditionals. Return early for the failure case:

BAD:

javascript
function process(user) {
  if (user) {
    if (user.active) {
      return doWork(user);
    }
  }
  return null;
}
GOOD:

javascript
function process(user) {
  if (!user) return null;
  if (!user.active) return null;
  return doWork(user);
}
7.4 Side Effects Belong in Named Functions
A function named getUser should not send an email. Keep read functions
pure, name side effects explicitly (saveUser, sendWelcomeEmail).

8. Async and Promises
8.1 Async/Await Over .then Chains
Use async / await for readable control flow. Use .then only for
short chains or when mixing with non-async APIs.

BAD:

javascript
fetchUser(id)
  .then(user => fetchPosts(user.id))
  .then(posts => render(posts))
  .catch(handleError);
GOOD:

javascript
try {
  const user = await fetchUser(id);
  const posts = await fetchPosts(user.id);
  render(posts);
} catch (error) {
  handleError(error);
}
8.2 Never await in forEach
forEach does not await the callback. The loop returns immediately.

BAD:

javascript
items.forEach(async (item) => {
  await process(item); // not awaited
});
GOOD:

javascript
for (const item of items) {
  await process(item);
}
If order does not matter and parallel execution is desired:

javascript
await Promise.all(items.map(item => process(item)));
8.3 Promise.all vs Promise.allSettled
Promise.all rejects on the first rejection. Use when all results
are required.

Promise.allSettled returns all outcomes. Use when partial success
is acceptable.

Do not use Promise.all for fire-and-forget operations. Unhandled
rejections cause process crashes or silent failures.

8.4 Never Mix Callbacks and Promises
A function either returns a Promise or takes a callback. Not both.
Never wrap a callback API in a Promise and also call the callback.

8.5 Timeouts on External Calls
Every network, database, or external call has a timeout. A promise that
never resolves hangs the request forever.

javascript
const controller = new AbortController();
setTimeout(() => controller.abort(), 5000);
await fetch(url, { signal: controller.signal });
8.6 Unhandled Rejections
Every promise chain has a .catch, or it is inside a try / catch,
or it is returned from an async function whose caller handles it.
Never let a promise reject without a handler.

9. Error Handling
9.1 Always Throw Error or Subclasses
BAD:

javascript
throw "something went wrong";
GOOD:

javascript
throw new Error("something went wrong");
String throws lose the stack trace and the .message property's
conventions.

9.2 Do Not Swallow Errors
BAD:

javascript
try { doWork(); } catch (e) { /* nothing */ }
GOOD:

javascript
try {
  doWork();
} catch (error) {
  logger.error("doWork failed", error);
  throw error;
}
If the error is intentionally ignored, add a comment explaining why.

9.3 Do Not catch and Rethrow Without Change
BAD:

javascript
try { doWork(); } catch (e) { throw e; }
GOOD:

javascript
doWork();
The try / catch adds nothing. Remove it.

9.4 Re-throw With Context
When wrapping an error:

javascript
try {
  await saveUser(user);
} catch (error) {
  throw new Error(`failed to save user ${user.id}`, { cause: error });
}
Use the cause option. Do not concatenate messages and lose the
original error object.

9.5 Do Not Use error.message for Logic
Messages are for humans. Match on error types or codes:

BAD:

javascript
catch (error) {
  if (error.message.includes("not found")) { /* ... */ }
}
GOOD:

javascript
catch (error) {
  if (error instanceof NotFoundError) { /* ... */ }
}
10. Modules
10.1 ESM Over CommonJS
Use import / export. Only use require when the project is
explicitly CommonJS and cannot migrate.

10.2 Named Exports Over Default Exports
Named exports make refactoring tools work, avoid naming mismatches at
import sites, and produce clearer stack traces.

BAD:

javascript
export default function createUser() { /* ... */ }
GOOD:

javascript
export function createUser() { /* ... */ }
Default exports are acceptable when the module is truly a single
concept and the project uses this consistently.

10.3 No Barrel Files
An index.js that re-exports everything from a folder:

Breaks tree-shaking.

Creates circular import risk.

Makes stack traces harder to read.

Import directly from the specific file.

10.4 No Side Effects in Module Top-Level
A module's top-level code runs on import. Do not put I/O, network
calls, or global mutations there. Do work in named functions.

Exception: explicitly documented initialization modules with a single
init() that is called by the application entry point.

10.5 Dynamic Import for Lazy Loading
Use await import("...") for code that is not needed at startup.
Static imports always load.

11. DOM and Browser (When Applicable)
11.1 querySelector Over getElementById
Modern querySelector / querySelectorAll handle all selectors
uniformly. Prefer them unless the project has a reason not to.

11.2 No innerHTML With Untrusted Data
BAD:

javascript
element.innerHTML = userInput;
GOOD:

javascript
element.textContent = userInput;
Or sanitize explicitly with the project's sanitizer library.

11.3 Event Delegation
Attach listeners to a parent element when the children are dynamic.
Do not attach a listener per row of a list.

11.4 addEventListener Requires Removal
Every listener added to a long-lived element is removed when no longer
needed, or the element is discarded. Otherwise, listeners leak.

11.5 localStorage Is Synchronous and Limited
localStorage blocks the main thread and has a small quota. Never
store large objects. Never store sensitive data (tokens, PII).

12. Node.js (When Applicable)
12.1 Never Use __dirname in ESM
Use import.meta.url and fileURLToPath:

javascript
import { fileURLToPath } from "node:url";
import { dirname } from "node:path";
const __dirname = dirname(fileURLToPath(import.meta.url));
12.2 Use node: Prefix for Core Modules
BAD: import fs from "fs";
GOOD: import fs from "node:fs";

The node: prefix distinguishes core modules from npm packages with
the same name.

12.3 Prefer fs/promises Over Callbacks
BAD: fs.readFile(path, (err, data) => {})
GOOD: await fs.readFile(path)

12.4 Never process.exit() in Library Code
Only the application entry point calls process.exit(). Libraries
throw, let the caller decide.

12.5 Streams for Large Data
Reading a 2 GB file with readFile will crash. Use streams.

13. JavaScript-Specific Anti-Patterns
13.1 == Somewhere in the Codebase
Even one instance invites more. Enforce === with a linter.

13.2 Mutation of Shared State
BAD: A module-level let cache = {} that every function mutates.
GOOD: A dedicated cache module with a clear API, or no cache at all.

13.3 Implicit Globals From Typos
BAD: userNmae = "x" (typo creates global).
GOOD: Strict mode throws. Keep it on.

13.4 arguments Object
BAD: function f() { return arguments[0]; }
GOOD: function f(...args) { return args[0]; }

arguments is not an array, does not work with arrow functions, and
defeats rest-parameter tooling.

13.5 this in Callbacks
BAD:

javascript
obj.on("event", function() { this.handle(); });
GOOD:

javascript
obj.on("event", () => this.handle());
Or bind explicitly if function is required.

13.6 new With Factory Functions
If a function returns an object, do not call it with new. The new
operator adds this binding rules that are easy to get wrong.

13.7 Chained || for Default Values
BAD: const name = input || "default";
This treats 0, "", and false as missing.

GOOD: const name = input ?? "default";

13.8 ?? and || Precedence
a ?? b || c is a syntax error without parentheses. Even with
parentheses, mixing them is confusing. Write it explicitly:

javascript
const value = (a ?? b) || c;
13.9 Optional Chaining Over Guard Chains
BAD:

javascript
const name = user && user.profile && user.profile.name;
GOOD:

javascript
const name = user?.profile?.name;
13.10 Non-Null Assertions in Plain JS
Plain JavaScript has no !. Do not import the TypeScript habit of
assuming a value is non-null without checking.

13.11 Floating Promises
A promise that is created and not awaited or chained is a floating
promise. Linters flag it. Every promise must be:

awaited, or

.catched, or

explicitly returned to a caller, or

intentionally ignored with a comment.

13.12 Callbacks Without Error Parameters
Node-style callbacks take (err, result). Do not call a callback with
a single argument when the convention is two. It silently misaligns
consumers.

13.13 Magic Numbers and Strings
BAD: if (status === 3)
GOOD: if (status === STATUS.ACTIVE)

Named constants improve readability and refactoring.

13.14 Deeply Nested Ternaries
BAD:

javascript
const label = a ? "A" : b ? "B" : c ? "C" : "D";
GOOD: A switch, a lookup table, or an if / else chain.

13.15 JSON.parse(JSON.stringify(x)) for Deep Clone
This loses Date, Map, Set, undefined, functions, and circular
references. Use structuredClone when available, or a proper deep-clone
library.

13.16 NaN Comparison
NaN === NaN is false. Use Number.isNaN(x), not x === NaN.

13.17 typeof null === "object"
This is a historical bug. Never branch on typeof x === "object" to
detect objects; use x !== null && typeof x === "object".

14. Response to Violation
If a previous response violated a rule here:

text
In the previous response, [specific rule] was violated. Correction:
[corrected code]
No justification. No apology paragraph. Fix and move on.

text

---