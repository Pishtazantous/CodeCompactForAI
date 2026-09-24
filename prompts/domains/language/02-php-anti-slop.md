---
id: 02-php-anti-slop
title: "PHP Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: language
version: 1
---
# PHP Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. This layer covers PHP
runtime boundaries, type safety, sessions, and Composer practices. Framework
rules remain in the corresponding framework layer.

## 1. Scope and Assumptions
1. Read `composer.json`, the runtime version, extension requirements, and the
   project entry point before selecting functions or syntax.
2. Match the project's PSR standard, autoloader, error policy, and test setup.
3. Keep public function signatures and serialized data compatible unless the
   task explicitly authorizes a migration.

## 2. Global State
4. Do not use `global` for business state. Pass dependencies and values through
   parameters, constructors, or a narrowly scoped service.
5. Avoid superglobals outside the request boundary. Copy, validate, and type
   request data before passing it inward.
6. Do not use a function to secretly read configuration from global state.
   Configuration should be an explicit dependency.

## 3. Sessions and Request State
7. Treat session data as untrusted, persistent, and schema-less. Validate and
   normalize it on every use.
8. Regenerate the session identifier after authentication or privilege change.
9. Do not store secrets or unnecessary personal data in the session. Set the
   project's secure cookie and same-site attributes at the application edge.
10. Do not use a global request singleton to pass data between unrelated
    services.

## 4. Type Safety and Juggling
11. Enable or honor `declare(strict_types=1)` in files that define typed
    contracts. Never loosen scalar types to make a call succeed.
12. Do not rely on PHP's loose comparisons for user data. Use strict comparison
    when identity, numeric strings, or booleans matter.
13. Validate arrays with required keys and types before accessing nested data.
    Do not pass unchecked `$_GET` values to a domain function.
14. Use `enum`, value objects, or DTOs when a constrained value crosses layers.
    Do not represent every domain object as an untyped associative array.

## 5. Errors and Exceptions
15. Throw specific exceptions for domain and infrastructure failures. Do not
    return `false` for every failure and force callers to guess the cause.
16. Do not catch `Throwable` to continue after unknown errors. Rescue a named
    exception when recovery is possible, then log or rethrow with context.
17. Keep display errors disabled in deployed environments. Return safe user
    messages and preserve details in controlled logs.

## 6. Composer and Dependencies
18. Use Composer's autoloader and PSR-4 mapping. Do not hand-require files
    from arbitrary paths.
19. Do not add a package without permission. Prefer an existing package or
    platform capability and record why it is insufficient.
20. Pin compatible dependency constraints according to the repository policy;
    never commit secrets in `auth.json` or environment files.
21. Run the repository's Composer validation and tests after dependency or
    autoload changes.

## 7. Functions and Data Contracts
22. Use strict parameter and return types on new public functions. Add
    `mixed` only when the value truly is heterogeneous, then validate it.
23. Prefer named arguments for optional behavior. Avoid functions with many
    positional booleans that make call sites unreadable.
24. Keep side effects at the edge. Pure transformations should be easy to test
    and should not echo output or mutate superglobals.
25. Escape output at the rendering boundary according to its context; do not
    escape once and assume every consumer is safe.

## 8. Framework-Neutral Rules
26. Keep routing, authentication, validation, persistence, and rendering
    concerns separate. Do not put all of them in one procedural endpoint file.
27. Use transactions only around the required database work. Do not assume a
    rollback can undo a remote HTTP call.
28. Avoid static service containers. They make tests and ownership ambiguous.
29. Use dependency injection where the existing architecture supports it.

34. Review every array access for a missing-key failure and make the response
    explicit rather than allowing an undefined-index notice.
35. Inspect session writes and privilege changes for ordering and isolation.
36. Verify that Composer changes preserve autoload and platform constraints.
37. Check rendered values with the encoder required by their exact context.
39. Validate session identifiers after authentication and privilege changes.
40. Check Composer lock changes separately from application behavior.
41. Exercise malformed nested input and strict comparison boundaries.
42. Run the repository's exact configured verification commands.
43. Inspect responses for accidental diagnostic disclosure.

44. Review every nested array access for a defined failure path.
45. Check session writes occur before response output.
46. Inspect Composer lock changes separately.
47. Verify logs exclude secrets and personal data.
48. Run the repository's configured verification commands.
49. Exercise session expiry and privilege changes.
50. Confirm strict comparison at authorization boundaries.
51. Check context-specific output encoding.
52. Review transaction duration around remote calls.
53. Confirm dependencies own no hidden global state.
54. Record exact formatter, analysis, and test output.

## Domain-Specific Anti-Patterns

### 9.1 Hidden Global Dependencies
BAD:
```php
function sendInvoice(): void {
    global $mailer;
    $mailer->send(readUserId());
}
```
GOOD:
```php
function sendInvoice(Mailer $mailer, UserId $userId): void {
    $mailer->send($userId);
}
```

### 9.2 Type Juggling
BAD:
```php
if ($user['role'] == 0) { grantAdmin($user); }
```
GOOD:
```php
if ($user->role === UserRole::Member) { grantMemberAccess($user); }
```

### 9.3 Unchecked Request Nesting
BAD:
```php
$name = $_POST['user']['profile']['name'];
echo $name;
```
GOOD:
```php
$name = $request->input('user.profile.name');
if (!is_string($name)) { return Problem::badRequest(); }
echo htmlspecialchars($name, ENT_QUOTES, 'UTF-8');
```

## 10. Verification Checklist
30. A `while` loop that repeatedly queries a growing result set needs an index,
    pagination, or a bounded query plan.
31. `extract`, `compact`, and variable variables are security and maintenance
    risks unless strictly local and reviewed.
32. Test malformed input, missing keys, session expiry, type boundaries, and
    failure paths in addition to the happy path.
33. Run the configured formatter, static analysis, and tests; report exact
    commands and results.

## 11. Response to Violation
State the file and function, cite the numbered rule, and describe the concrete
security, type, or runtime failure. Make the smallest correction without
changing unrelated behavior. Refer to the master layer instead of repeating
it. If a Composer, session, or public signature change needs a migration,
call out that impact before editing.
Report the exact checks that were run.
