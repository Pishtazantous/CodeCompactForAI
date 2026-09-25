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

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
security anti-patterns, output format) are NOT repeated here.

This file covers rules specific to PHP: type declarations, PSR
compliance, global state, superglobals, and the patterns that produce
security vulnerabilities. Framework rules (Laravel, Symfony) live in
`domains/framework/`.

## 1. Stack Assumptions

This layer assumes:

- PHP 8.1 or later.
- Composer for dependencies.
- PSR-12 coding standard.

## 2. Type System

### 2.1 `declare(strict_types=1)` at the Top

Every PHP file starts with:

```php
<?php

declare(strict_types=1);

namespace App\...;
```

Without it, PHP coerces types silently.

### 2.2 Type Declarations Everywhere

Every function has parameter and return types:

BAD:
```php
function add($a, $b) {
    return $a + $b;
}
```

GOOD:
```php
function add(int $a, int $b): int {
    return $a + $b;
}
```

### 2.3 No `mixed` Without a Reason

`mixed` disables type checking. Prefer a union type or a specific
type.

### 2.4 Nullable With `?`

A type that may be `null` uses `?`:

```php
function find(string $id): ?User { ... }
```

### 2.5 Union Types Over Docblocks

PHP 8.0+ supports union types natively:

BAD:
```php
/** @param int|string $id */
function find($id) { ... }
```

GOOD:
```php
function find(int|string $id): ?User { ... }
```

### 2.6 Enums Over Constants

BAD:
```php
class Status {
    const ACTIVE = 'active';
    const INACTIVE = 'inactive';
}
```

GOOD:
```php
enum Status: string {
    case Active = 'active';
    case Inactive = 'inactive';
}
```

## 3. PSR Compliance

### 3.1 PSR-12 Formatting

- 4 spaces indentation (no tabs).
- Opening brace on the same line for methods, next line for classes.
- One class per file.
- `use` statements alphabetized.

### 3.2 PSR-4 Autoloading

Namespace matches directory structure. `App\Services\UserService`
lives in `src/Services/UserService.php`.

### 3.3 PSR-3 Logging

Loggers implement `Psr\Log\LoggerInterface`. Never `error_log` or
`echo` for logs.

### 3.4 PSR-7/PSR-15 for HTTP

Modern frameworks use PSR-7 (requests/responses) and PSR-15
(middleware). Follow the framework's convention.

## 4. Superglobals

### 4.1 Never Use `$_GET`, `$_POST` Directly

BAD: `$id = $_GET['id'];`.
GOOD: Use the framework's request object:
```php
$id = $request->query('id');
```

In vanilla PHP, use `filter_input()`:
```php
$id = filter_input(INPUT_GET, 'id', FILTER_VALIDATE_INT);
```

### 4.2 Never Trust `$_SERVER`

`$_SERVER['HTTP_HOST']`, `$_SERVER['REMOTE_ADDR']`, and
`$_SERVER['HTTP_X_FORWARDED_FOR']` are attacker-controlled unless
validated.

### 4.3 `$_SESSION` Requires Session Hardening

- `session_start()` with `session.cookie_httponly=1` and
  `session.cookie_secure=1`.
- Regenerate the session ID on login.
- Never store sensitive data in `$_SESSION` unencrypted.

### 4.4 No `$_REQUEST`

`$_REQUEST` merges GET, POST, and COOKIE. Never use it. It hides
the request method and mixes trust levels.

### 4.5 No `extract()`

`extract($_POST)` creates variables from user input. Never.

## 5. Security

### 5.1 Prepared Statements

BAD:
```php
$result = $pdo->query("SELECT * FROM users WHERE id = $id");
```

GOOD:
```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = ?");
$stmt->execute([$id]);
```

Never concatenate SQL. Never.

### 5.2 Escape Output

BAD: `echo $_GET['name'];` (XSS).
GOOD: `echo htmlspecialchars($name, ENT_QUOTES, 'UTF-8');`.

### 5.3 `password_hash` and `password_verify`

BAD: `md5($password)` or `sha1($password)`.
GOOD:
```php
$hash = password_hash($password, PASSWORD_ARGON2ID);
// or PASSWORD_DEFAULT for bcrypt
```

Verify with `password_verify($input, $hash)`.

### 5.4 `random_bytes` for Randomness

BAD: `rand()` or `mt_rand()` for tokens.
GOOD: `bin2hex(random_bytes(32))`.

### 5.5 `hash_equals` for Token Comparison

BAD: `if ($provided === $stored)`.
GOOD: `if (hash_equals($stored, $provided))`.

Prevents timing attacks.

### 5.6 `unserialize` Never on User Input

`unserialize()` on untrusted data allows object injection. Use
`json_decode` instead.

### 5.7 No `eval`, `assert` With Strings, `create_function`

These execute arbitrary code. Never.

### 5.8 File Uploads

- Validate MIME type (not just extension).
- Store outside the web root.
- Rename to a UUID.
- Never `move_uploaded_file` into an executable directory.

## 6. Error Handling

### 6.1 Throw Exceptions

BAD: `return false;` or `return null;` on failure.
GOOD: `throw new UserNotFoundException($id);`.

### 6.2 Custom Exception Hierarchy

```php
class AppException extends \Exception {}
class UserNotFoundException extends AppException {}
```

### 6.3 Catch Specific Exceptions

BAD: `catch (\Exception $e) { }`.
GOOD: `catch (UserNotFoundException $e) { }`.

### 6.4 Never Swallow

BAD: `try { ... } catch (\Exception $e) {}`.
GOOD: Log and rethrow, or convert and rethrow.

### 6.5 No `@` Error Suppression

The `@` operator suppresses warnings. It hides bugs and slows
execution. Never use it.

### 6.6 `finally` for Cleanup

Use `try`/`finally` or the framework's cleanup mechanisms.

## 7. Classes and Objects

### 7.1 Constructor Property Promotion

PHP 8.0+:

BAD:
```php
class UserService {
    private UserRepository $repo;
    public function __construct(UserRepository $repo) {
        $this->repo = $repo;
    }
}
```

GOOD:
```php
class UserService {
    public function __construct(
        private readonly UserRepository $repo,
    ) {}
}
```

### 7.2 `readonly` for Immutable Properties

PHP 8.1+: mark properties `readonly` when they do not change.

### 7.3 No Public Properties

BAD: `public string $name;`.
GOOD: `private string $name;` with getter, or `public readonly`.

### 7.4 `final` by Default for Non-Extensible Classes

Mark classes `final` unless extension is intended.

### 7.5 No Static Methods for Business Logic

A static method hides dependencies and complicates testing. Use an
injected instance.

Exception: pure utility functions.

## 8. Composer and Dependencies

### 8.1 `composer.lock` Committed

The lock file is committed. `composer install` (not `update`) in CI
and production.

### 8.2 Version Constraints

BAD: `"vendor/package": "*"`.
GOOD: `"vendor/package": "^2.0"`.

### 8.3 No Dev Dependencies in Production

`composer install --no-dev` in production.

### 8.4 No Abandoned Packages

Check `composer outdated` and the package's repository.

## 9. PHP-Specific Anti-Patterns

### 9.1 No `declare(strict_types=1)`

Covered in 2.1.

### 9.2 SQL Concatenation

Covered in 5.1.

### 9.3 `md5`/`sha1` for Passwords

Covered in 5.3.

### 9.4 `$_REQUEST`

Covered in 4.4.

### 9.5 `extract()`

Covered in 4.5.

### 9.6 `eval` Family

Covered in 5.7.

### 9.7 `unserialize` on User Input

Covered in 5.6.

### 9.8 `@` Error Suppression

Covered in 6.5.

### 9.9 No Type Declarations

Covered in 2.2.

### 9.10 `array()` Over `[]`

BAD: `$items = array(1, 2, 3);`.
GOOD: `$items = [1, 2, 3];`.

### 9.11 Mixing HTML and PHP

BAD: A PHP file with HTML and complex logic.
GOOD: A template engine (Twig, Blade) or a separate view layer.

### 9.12 String Concatenation With `.` in Loops

BAD: `$s .= $x;` in a loop over thousands of items.
GOOD: `implode()` or `sprintf`.

### 9.13 `empty()` for Type Checking

BAD: `if (empty($value))` (treats `0` and `"0"` as empty).
GOOD: `if ($value === null || $value === '')`.

### 9.14 `isset()` for Null Check

`isset($var)` is true if `$var` is set and not `null`. For a null
check, `$var !== null` is clearer when the variable may not exist.

### 9.15 `array_push` Over `[]=`

BAD: `array_push($items, $x);`.
GOOD: `$items[] = $x;`.

### 9.16 Deeply Nested Arrays

An array with five levels of nesting is unreadable. Use an object or
a typed collection.

### 9.17 `global` Keyword

BAD: `global $db;` inside a function.
GOOD: Pass dependencies as parameters or use a container.

### 9.18 Static State

BAD: A static property used as a cache or a singleton.
GOOD: An injected instance with a defined lifecycle.

### 9.19 `include`/`require` for Logic

File inclusion is for templates, not for control flow. Use autoloading.

### 9.20 `elseif` Without Braces

Always use braces, even for single statements.

### 9.21 Variable Variables

BAD: `$$name = 'value';`.
GOOD: An associative array.

### 9.22 `list()` Over `[]` Destructuring

BAD: `list($a, $b) = $pair;`.
GOOD: `[$a, $b] = $pair;`.

### 9.23 Null Coalescing Misuse

`$a ?? $b` is not a default for empty strings. `""` is not `null`.

### 9.24 `?->` Without Need

The nullsafe operator is for cases where the receiver may be `null`.
Do not use it everywhere as a substitute for validation.

### 9.25 Returning `false` on Error

Covered in 6.1.

## 10. Response to Violation

If a previous response violated a rule here:

```
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

No justification. No apology paragraph. Fix and move on.
