---
id: 02-security-critical-anti-slop
title: "Security-Critical Anti-Slop Layer"
lang: en
depends_on: ["_universal/00-style-guide.md", "_universal/00-master-anti-slop.md"]
category: domain
domain_type: concern
version: 3
---

# Security-Critical Anti-Slop Layer

This file defines behavioral contracts specific to security-critical systems. It sits in the concern layer, below the universal anti-slop rules and alongside other cross-cutting concerns. It covers threat modeling, authentication, authorization, cryptography, input validation, data protection, session management, supply chain security, and security review discipline. It does not cover generic security basics already defined in `00-master-anti-slop.md` (section MAS-009), domain-specific security rules (see delivery files), language-specific security features (see language files), or framework-specific security configuration (see framework files).

For most projects, the security baseline in `00-master-anti-slop.md` is sufficient. This file applies to the subset of projects where a single mistake can compromise users, funds, or regulated data.

## When This File Applies

This file MUST be sent when at least one of the following objective criteria is met:

- The system implements authentication or identity (OAuth provider, SSO, auth service).
- The system processes payments, wallets, or financial transactions.
- The system stores PII, PHI, or financial records subject to regulation (GDPR, HIPAA, PCI-DSS).
- The system is multi-tenant with strict tenant isolation requirements.
- The system exposes APIs to untrusted third-party clients.
- The system implements cryptographic operations or key management.
- The system operates in a hostile environment (public internet, untrusted client devices).

This file does NOT apply to: static marketing sites, internal tools with no sensitive data, public read-only APIs with no authentication, or prototype projects with no production intent.

## Scope

This file applies to security-critical systems built in any language or framework. The examples use JavaScript/TypeScript, Python, and Go syntax where illustrative. Language-specific security features (type-safe parsing, memory safety) live in language files. Framework-specific security middleware (Express helmet, Django CSRF, Spring Security) lives in framework files.

The concern is cross-cutting: rules in this file apply to backend services, frontend applications, mobile apps, CLI tools, libraries, and infrastructure equally, wherever the applicability criteria above are met.

## Concern Budgets

Security-critical systems MUST operate within these measurable thresholds:

| Concern | Threshold | Verification Method | Rule |
|---|---|---|---|
| Session Token Entropy | >= 128 bits | CSPRNG source audit, bit-length test | SEC-012 |
| Password Hash Cost | bcrypt >= 12, Argon2id per OWASP | Config review, benchmark test | SEC-007 |
| JWT Access Token Expiry | <= 15 minutes | Token inspection, test suite | SEC-013 |
| Auth Rate Limit | <= 5 attempts/min/account | Load test, log analysis | SEC-009 |
| TLS Version | >= 1.2 (1.3 preferred) | SSL Labs scan, `testssl.sh` | SEC-030 |
| RSA Key Size | >= 2048 bits | Certificate inspection | SEC-045 |
| Password Reset Token | Single-use, <= 15 min expiry | Functional test, code review | SEC-070 |
| Max JSON Nesting Depth | <= 64 levels | Fuzz test with deeply nested JSON | SEC-071 |
| Dependency Audit | Weekly scan, 0 high/critical CVEs | CI pipeline (`npm audit`, `pip-audit`) | SEC-048 |

## Rule Severity

Severity follows `_universal/00-style-guide.md`. Violations in this file are typically critical due to the security nature of the concern.

## Contracts

A security-critical system commits to eight contracts. The table below maps each contract to the rules that enforce it.

| Contract | Description | Enforced By |
|---|---|---|
| Threat Awareness | Assets, adversaries, and attack surfaces are identified before code. | SEC-001 to SEC-005 |
| Authentication Integrity | Credentials hashed, sessions secure, MFA properly implemented. | SEC-006 to SEC-014 |
| Authorization Correctness | Server-side, deny-by-default, object-level, function-level checks. | SEC-015 to SEC-020 |
| Input/Output Safety | All input validated, all output encoded, no injection vectors. | SEC-021 to SEC-027 |
| Data Protection | Secrets managed, data encrypted, PII minimized, backups secured. | SEC-028 to SEC-034 |
| Session Security | Cookies hardened, CSRF protected, sessions bounded and invalidated. | SEC-035 to SEC-039 |
| Cryptographic Correctness | Standard libraries, unique nonces, managed keys, no deprecated algorithms. | SEC-040 to SEC-045 |
| Operational Security | Dependencies audited, errors neutral, logs tamper-resistant, reviews mandatory. | SEC-046 to SEC-061 |

## Threat Modeling Discipline

### SEC-001 — Asset Identification

**MUST**

Before writing code, the assets that must be protected MUST be explicitly named: credentials, personal data, financial data, health data, proprietary business data, and audit logs. If the asset list is empty, this file does not apply.

### SEC-002 — Adversary Identification

**MUST**

Potential adversaries MUST be identified: anonymous internet users, authenticated users escalating privilege, compromised dependencies, insiders, and (when relevant) nation-states. The adversary determines the countermeasures.

### SEC-003 — Attack Surface Enumeration

**MUST**

Every place untrusted input enters the system MUST be listed: HTTP requests (body, query, headers, cookies), WebSocket messages, file uploads, webhooks, queue messages, operator-set environment variables, and data read from a database written by earlier requests.

### SEC-004 — Hostile Network Assumption

**MUST**

Every byte from the network MUST be treated as attacker-controlled until validated. Every third-party response, certificate, and DNS answer MUST be assumed potentially compromised.

### SEC-005 — Compromised Client Assumption

**MUST NOT**

The client (browser, mobile app, CLI, desktop) MUST NOT be trusted. Client-provided User ID, Role, Permission flag, Price, Discount, Timestamp, and Amount MUST NOT be used for authorization or business logic. The server MUST decide these from authoritative sources.

## Authentication

### SEC-006 — No Custom Cryptography

**MUST NOT**

Custom ciphers, hashes, or protocols MUST NOT be invented. The platform's or language's standard library MUST be used for password hashing, random number generation, symmetric encryption, key derivation, and signature verification.

Invented cryptography fails in ways that are invisible until exploited.

### SEC-007 — Password Hashing Parameters

**MUST**

Password hashing MUST use Argon2id with current OWASP-recommended parameters, bcrypt with cost >= 12, or scrypt with appropriate memory/time cost. MD5, SHA-1, SHA-256 alone, or any fast hash MUST NOT be used for passwords.

Fast hashes allow offline brute-force at billions of guesses per second.

### SEC-008 — Constant-Time Secret Comparison

**MUST**

Secret comparisons MUST use constant-time primitives (e.g., `crypto.timingSafeEqual`). Length leaks are also side channels; padded values or language primitives MUST be used.

Example (illustrative, JavaScript):

BAD:
```javascript
if (providedToken === storedToken) { /* ... */ }
```

GOOD:
```javascript
crypto.timingSafeEqual(providedToken, storedToken);
```

### SEC-009 — Authentication Rate Limiting

**MUST**

Every login, password reset, OTP verification, and API key validation MUST have rate limits: per-account, per-IP, and per-device where relevant.

### SEC-010 — Careful Account Lockout

**SHOULD**

Permanent lockout enables DoS by adversaries who know a victim's email. Exponential backoff or temporary lockout with a clear unlock path SHOULD be used instead.

### SEC-011 — MFA Implementation

**MUST**

When MFA is supported:

- TOTP secrets MUST be encrypted at rest.
- Recovery codes MUST be single-use and stored hashed.
- MFA MUST NOT be bypassable by password reset without a second factor.
- MFA setup MUST require re-authentication with the current password.

### SEC-012 — Session Token Entropy

**MUST**

Session tokens MUST be generated from a cryptographically secure random source with at least 128 bits of entropy. They MUST be stored hashed on the server, rotated on login and privilege change, and invalidated on logout, password change, and account suspension.

### SEC-013 — JWT Discipline

**MUST**

JWTs MUST be signed with a strong algorithm (RS256, ES256, EdDSA). The `none` algorithm MUST NOT be accepted. The `alg` header MUST be validated against an allowlist. Access token expiry MUST be short (minutes). `aud`, `iss`, `exp`, `nbf` MUST be validated on every request. Revocation MUST be handled via a deny list or short expiry with rotation.

### SEC-014 — OAuth and OIDC Correctness

**MUST**

OAuth/OIDC implementations MUST:

- Use and validate `state` (CSRF protection).
- Use and validate `nonce` (OIDC).
- Validate `redirect_uri` against an exact-match allowlist.
- Use PKCE for public clients.
- Keep tokens on the backend, never sending them to the frontend channel.

## Authorization

### SEC-015 — Server-Side Authorization

**MUST**

Authorization MUST be decided on the server. The frontend may hide a button, but the server MUST decide whether the action is allowed.

### SEC-016 — Deny by Default

**MUST**

Every endpoint, resource, and field MUST start inaccessible. Permissions MUST be added explicitly. New endpoints MUST NOT inherit middleware without an explicit authorization check.

### SEC-017 — Object-Level Authorization

**MUST**

The server MUST check "does this user own this resource", not just "is the user authenticated". A 404 MUST be returned (not 403) when the resource exists but belongs to another user, to prevent existence leakage.

Example (illustrative, TypeScript):

BAD:
```typescript
app.get("/orders/:id", auth, async (req, res) => {
  const order = await db.orders.findById(req.params.id);
  res.json(order); // any authenticated user reads any order
});
```

GOOD:
```typescript
app.get("/orders/:id", auth, async (req, res) => {
  const order = await db.orders.findOne({
    id: req.params.id,
    userId: req.user.id,
  });
  if (!order) return res.status(404).json({ error: "not found" });
  res.json(order);
});
```

### SEC-018 — Function-Level Authorization

**MUST**

Beyond ownership, the caller's role MUST permit the operation. A regular user calling an admin endpoint MUST be rejected even if the endpoint is behind authentication.

### SEC-019 — No Client-Provided Roles

**MUST NOT**

Roles MUST be read from the session or a database lookup. They MUST NEVER come from a header, query param, or body field.

### SEC-020 — Privilege Escalation Audit

**MUST**

Every field the user can write MUST be allowlisted. Request bodies MUST NEVER be bound directly to models. Audit for: users updating their own role, assigning themselves to admin groups, changing their tenant ID, or editing records they do not own.

## Input Validation and Output Encoding

### SEC-021 — Boundary Validation

**MUST**

Every external input MUST be validated before use using the project's schema library. The schema is the contract.

### SEC-022 — Comprehensive Validation

**MUST**

Validation MUST cover type, length (max chars, max items), format (regex, scheme allowlist, UUID shape), and range (min/max, date bounds).

### SEC-023 — Allowlist Over Blacklist

**MUST**

Allowlists of known-good patterns MUST be used. Blacklists of known-bad patterns are always incomplete and MUST NOT be relied upon.

### SEC-024 — Context-Aware Output Encoding

**MUST**

Output MUST be encoded for its context:

- HTML context: HTML-encode `<`, `>`, `&`, `"`, `'`.
- Attribute context: quote attributes, encode quotes.
- URL context: percent-encode.
- JavaScript context: JSON-encode and escape `</script>`.
- CSS context: avoid dynamic CSS entirely if possible.
- SQL: parameterized queries, never string concatenation.

### SEC-025 — No Untrusted Input Concatenation

**MUST NOT**

Untrusted input MUST NEVER be concatenated into: SQL queries, shell commands, HTML strings, LDAP queries, XPath queries, log format strings, template engines evaluated at runtime, `eval`/`Function`/`exec`, or filesystem paths.

### SEC-026 — File Upload Safety

**MUST**

File uploads MUST validate content type (not just extension), limit size/count/total, store outside the web root or in object storage, rename to a safe identifier (UUID), and never execute or serve with the user's original name containing path separators. Untrusted files MUST be scanned for malware.

### SEC-027 — No Unsafe Deserialization

**MUST NOT**

The following MUST NOT be used on untrusted input: `eval`, `Function()`, `exec`, `pickle.loads`, `yaml.load` (use `safe_load`), `Marshal.load`, `unserialize`, `ObjectInputStream`, or `ScriptEngine` with untrusted scripts.

## Data Protection

### SEC-028 — Source and Git Secret Prohibition

**MUST NOT**

Secrets MUST NEVER appear in source code, committed `.env` files, Docker image layers, build artifacts, or Git history (even in private repositories or branches that will be deleted). A secret that enters Git history MUST be rotated immediately.

Secrets MUST come from CI secret stores and production secret managers (Vault, AWS Secrets Manager, GCP Secret Manager).

Hardcoded secrets in generated code are also prohibited per MAS-009 in `_universal/00-master-anti-slop.md`.

### SEC-029 — Encryption at Rest

**MUST**

PII, credentials, and financial data MUST be encrypted at the column or file level, in addition to database-level encryption. Keys MUST be managed separately from encrypted data and rotatable without blind re-encryption.

### SEC-030 — Encryption in Transit

**MUST**

TLS 1.2 or 1.3 MUST be used everywhere. Plaintext HTTP MUST NOT carry tokens, passwords, or personal data. HSTS MUST be enabled. HTTP-to-HTTPS redirects MUST be permanent.

### SEC-031 — No Secret Logging

**MUST NOT**

Tokens, session IDs, API keys, passwords (even hashed), credit card numbers (beyond allowed last four), and full request bodies containing these MUST NEVER be logged. PII MUST only be logged per project policy.

### SEC-032 — PII Minimization

**MUST**

Only business-necessary PII MUST be collected. Only used PII MUST be stored. PII MUST be deleted when no longer needed. Users MUST have a path to export and delete their data.

### SEC-033 — Data Retention Policy

**MUST**

Retention MUST be defined for every data category: logs, sessions, audit trails, user-generated content. Indefinite retention without a documented reason is prohibited.

### SEC-034 — Encrypted Backups

**MUST**

Backups MUST be encrypted with a key not stored in the same location as the backup. An unencrypted backup is an unencrypted database in a different folder.

## Session and Cookie Security

### SEC-035 — Session Cookie Hardening

**MUST**

Session cookies MUST have: `HttpOnly` (always), `Secure` (always in production), `SameSite=Lax` or `Strict` (None only when cross-site is genuinely needed, with Secure), narrow `Path`, and avoided `Domain` unless necessary.

### SEC-036 — CSRF Protection

**MUST**

For cookie-based sessions, CSRF protection is mandatory: synchronizer token, double-submit cookie with a signed token, or `SameSite=Strict` plus an origin check. For API-only services using Authorization header tokens, CSRF does not apply.

### SEC-037 — Session Fixation Prevention

**MUST**

The session ID MUST be regenerated on login and privilege change. Session IDs from URLs MUST NOT be accepted.

### SEC-038 — Server-Side Logout

**MUST**

Logout MUST invalidate the session on the server, not just on the client. Clearing the cookie is insufficient.

### SEC-039 — Session Timeouts

**MUST**

Sessions MUST expire after inactivity and after an absolute duration. Both MUST be configurable and enforced server-side.

## Cryptography

### SEC-040 — High-Level Crypto Libraries

**SHOULD**

High-level libraries (libsodium, platform crypto modules) SHOULD be used. High-level APIs (secretbox, sealed box) SHOULD be preferred over low-level primitives to avoid nonce and padding mistakes.

### SEC-041 — Nonce Uniqueness

**MUST NOT**

A nonce MUST NOT be reused with the same key for AES-GCM or ChaCha20-Poly1305. Nonce reuse with the same key is catastrophic and allows full plaintext recovery. The library's high-level API manages nonces; manual management MUST NOT be done without a documented plan.

### SEC-042 — Cryptographic Randomness

**MUST**

Secrets MUST use cryptographic random sources (`crypto.randomBytes`, `secrets.token_bytes`, `crypto/rand`). Non-cryptographic sources (`Math.random`, `random.random`, unseeded `rand.Intn`) MUST NOT be used.

### SEC-043 — Key Management

**MUST**

Keys MUST be generated from a CSPRNG, stored in a KMS or secret manager, rotated on a schedule, and NEVER logged, printed, or included in stack traces.

### SEC-044 — Signature Verification

**MUST**

Signatures MUST be verified before trusting the payload. The algorithm MUST be verified against an expected allowlist; the payload's own claim MUST NOT be trusted. Unsigned payloads MUST be rejected when the protocol requires signing.

### SEC-045 — Deprecated Algorithm Prohibition

**MUST NOT**

The following MUST NOT be used for security-relevant purposes: MD5, SHA-1, DES, 3DES, RC4, RSA with keys under 2048 bits, ECB mode, and static IVs.

## Dependencies and Supply Chain

### SEC-046 — Dependency Risk Assessment

**MUST**

Before adding a package, its maintenance status, download count, reputation, transitive dependencies, and license MUST be checked.

### SEC-047 — Committed Lockfiles

**MUST**

Lockfiles (`package-lock.json`, `yarn.lock`, `poetry.lock`, `Cargo.lock`, `go.sum`) MUST be committed. They MUST NOT be ignored.

### SEC-048 — Dependency Update Discipline

**MUST**

Security patches MUST be applied promptly. Updates MUST be reviewed before merge (not auto-merged blindly). A vulnerability scanner (`npm audit`, `pip-audit`, `govulncheck`, Dependabot) MUST be run regularly.

### SEC-049 — Typosquatting Prevention

**MUST**

The package name MUST be verified character-by-character before installing. `cross-env` and `crossenv` are different packages.

### SEC-050 — Postinstall Script Discipline

**MUST**

If the project disables postinstall scripts (`--ignore-scripts`), they MUST NOT be re-enabled without a documented reason. Postinstall scripts run arbitrary code at install time.

## Error Messages and Information Disclosure

### SEC-051 — Neutral Authentication Errors

**MUST**

Authentication errors MUST be neutral. The same message MUST be used for wrong password and unknown user to prevent account enumeration.

Example (illustrative):

BAD: "No account with that email" (reveals existence).
GOOD: "Invalid email or password" (neutral).

### SEC-052 — Information Disclosure Prevention

**MUST NOT**

The following MUST NOT be exposed to clients:

- Stack traces (the most common information leak).
- Database IDs, internal service names, file paths, hostnames in error messages.
- Debug endpoints (`/debug`, unprotected `/metrics`, `/actuator`, `/__webpack_hmr`).
- Public source maps (unless gated behind authentication for error tracking).
- Server version headers (e.g., `Server: nginx/1.18.0`).

A generic error response with an internal reference ID for log correlation MUST be used instead.

### SEC-053 — Timing Attack on Authentication Endpoints

**MUST**

Authentication and password reset endpoints MUST respond identically and take the same time for known and unknown accounts to prevent enumeration via timing.

## Logging and Monitoring

### SEC-054 — Security Event Logging

**MUST**

Security events MUST be logged: login success/failure, password change, permission change, access to sensitive resources, admin actions, rate limit hits, and CSRF/CORS/CSP violations.

### SEC-055 — Tamper-Resistant Logs

**MUST**

Security logs MUST go to a system the application cannot modify: a separate service, append-only storage, or a SIEM.

### SEC-056 — Anomaly Alerting

**MUST**

Alerts MUST fire on anomalies: spike in login failures, login from a new country, access to many resources by one account, and failed authorization attempts.

## Security Review Discipline

### SEC-057 — Threat Model Every Endpoint

**MUST**

For every new endpoint, the following MUST be answered: Who can call it? What does it expose? What does it allow the caller to change? What is the worst-case abuse?

### SEC-058 — Diff Secret Review

**MUST**

Before committing, the diff MUST be reviewed for anything that looks like a secret. Prevention is faster than remediation.

### SEC-059 — Security Fix Tests

**MUST NOT**

A security fix MUST NOT be merged without a regression test. The test MUST fail before the fix and pass after.

### SEC-060 — Report, Do Not Silently Fix

**MUST**

If a security issue is found while working on an unrelated task, it MUST be reported to the user with a clear description. It MUST NOT be fixed silently; the fix may require coordination (rotation, notification, audit).

### SEC-061 — Documented Security Assumptions

**MUST**

Security assumptions about deployment, network, and operators MUST be documented. When assumptions change, the security posture changes and MUST be re-evaluated.

## AI-Specific Security Discipline

### SEC-062 — Cryptographic Primitive Verification

**MUST**

Before using a cryptographic function (hashing, encryption, signing), the assistant MUST verify the algorithm is not deprecated, the library is reputable, and the parameters meet current OWASP/NIST recommendations. Invented crypto or weak parameters produce silent vulnerabilities that are catastrophic when exploited.

See MAS-036 in `_universal/00-master-anti-slop.md`.

### SEC-063 — Security Library Verification

**MUST**

Before using a security library (JWT validator, OAuth client, sanitizer), the assistant MUST verify it is the recommended library for the ecosystem and that the method being called handles all required security checks (e.g., JWT `alg` validation, not just signature verification). Partial validation is a common AI-generated vulnerability.

See MAS-036 in `_universal/00-master-anti-slop.md`.

### SEC-064 — Generated Code Secret Prohibition

**MUST NOT**

The assistant MUST NEVER generate code with hardcoded secrets, API keys, passwords, or tokens, even as placeholders or "temporary" values. AI-generated code is frequently committed without review; hardcoded secrets become permanent leaks.

This specializes MAS-009 in `_universal/00-master-anti-slop.md` for the AI code generation context.

## Anti-Patterns

### SEC-065 — Frontend-Only Authorization Check

**MUST NOT**

Authorization checks MUST NOT exist only on the frontend. The backend MUST enforce authorization. An attacker with a proxy bypasses the UI entirely.

### SEC-066 — Temporary Security Disabling

**MUST NOT**

Security controls (CORS, CSP, authentication, TLS verification) MUST NOT be disabled "temporarily" in commits. The correct configuration MUST always be in place.

Example (illustrative):

BAD: `app.use(cors({ origin: "*" }))` in a commit labeled "temporary".

### SEC-067 — Plaintext HTTP in Production

**MUST NOT**

`http://` MUST NOT be used in production, even for internal services. Credentials, tokens, and PII travel in plaintext.

### SEC-068 — Custom JWT Validation

**MUST NOT**

Hand-written JWT validation (e.g., signature check without full claim validation) is prohibited. The library's full validation MUST be used: `alg`, `exp`, `nbf`, `aud`, `iss`.

### SEC-069 — CORS Misconfiguration

**MUST NOT**

`Access-Control-Allow-Origin: *` with `Access-Control-Allow-Credentials: true` MUST NOT be used. Reflecting the `Origin` header without validating against an allowlist is prohibited.

### SEC-070 — Password Reset Token Reuse

**MUST NOT**

A reset token MUST be single-use. After use, it MUST be invalidated. The password change endpoint MUST NOT accept the same token twice.

### SEC-071 — Deeply Nested JSON Parsing

**MUST**

JSON parsers MUST limit nesting depth. A JSON payload with thousands of levels of nesting causes a stack overflow in some parsers.

### SEC-072 — SSRF Prevention

**MUST NOT**

Endpoints that fetch user-provided URLs MUST validate against a host allowlist, resolve DNS and check the IP against a denylist of private ranges (e.g., `169.254.169.254` for cloud metadata), and not follow redirects blindly.

### SEC-073 — XXE Prevention

**MUST**

External entity resolution MUST be disabled in every XML parser to prevent reading local files or making network requests.

### SEC-074 — Open Redirect Prevention

**MUST NOT**

Redirect parameters (e.g., `?next=...`) MUST be validated to be a relative path within the site or an allowlisted host. Open redirects enable phishing.

### SEC-075 — Prototype Pollution Prevention

**MUST NOT**

Object merging MUST block `__proto__`, `constructor`, and `prototype` keys. `Object.create(null)` MUST be used for dictionaries, or a safe merge function that rejects dangerous keys.

Example (illustrative, JavaScript):

BAD:
```javascript
function merge(target, source) {
  for (const key in source) target[key] = source[key];
}
// source = { "__proto__": { "isAdmin": true } } pollutes every object
```

GOOD:
```javascript
function merge(target, source) {
  for (const key of Object.keys(source)) {
    if (key === "__proto__" || key === "constructor") continue;
    target[key] = source[key];
  }
}
```

### SEC-076 — ReDoS Prevention

**MUST**

Regular expressions with nested quantifiers on untrusted input MUST be tested against adversarial input, or a linear-time engine MUST be used to prevent Regex Denial of Service.

### SEC-077 — Environment Variable Injection Prevention

**MUST NOT**

Environment variables MUST NOT be read from files the app does not own or from user-controlled input. An attacker could override configuration.

### SEC-078 — Cache Poisoning Prevention

**MUST**

Response caches MUST key on `Host`, `Authorization`, and `Cookie` headers in addition to the URL. Otherwise an attacker's response is served to another user.

### SEC-079 — Mass Assignment

**MUST NOT**

Request bodies MUST NOT be bound directly to models (e.g., `User.create(req.body)`). The client could set `role`, `isAdmin`, `balance`, or any other field. Fields MUST be explicitly allowlisted.

Example (illustrative, TypeScript):

BAD:
```typescript
const user = await User.create(req.body);
```

GOOD:
```typescript
const { name, email } = req.body;
const user = await User.create({ name, email });
```

### SEC-080 — Sequential ID Trust

**MUST NOT**

Auto-increment IDs do not protect an endpoint. Authorization checks are required, not obscurity. UUIDs reduce enumeration but do not replace the authorization check.

### SEC-081 — SameSite Ignorance

**MUST NOT**

A cookie without an explicit `SameSite` attribute relies on browser defaults that differ across versions. `SameSite` MUST be explicitly set on every session cookie.

### SEC-082 — Deserialization of Untrusted Data

**MUST NOT**

Deserialization of untrusted data via `ObjectInputStream` (Java), `pickle` (Python), `Marshal.load` (Ruby), or `unserialize` (PHP) allows code execution and MUST NOT be used on untrusted input.

### SEC-083 — Unvalidated `window.open` or URL Launch

**MUST NOT**

`window.open(userProvidedUrl)` or equivalent URL-launching APIs MUST NOT be called with unvalidated input. URLs MUST be validated against an allowlist of schemes and domains.

### SEC-084 — Mixed Content in Authenticated Pages

**MUST NOT**

Authenticated pages MUST NOT load `http://` resources. Mixed content is blocked by modern browsers and exposes the user to MITM attacks.

## Response to Violation

When a rule in this file is violated, report:

Violation: SEC-{NNN}
Reason: {one-line reason}
Correction: {smallest fix}

If the violation is in already-deployed code, the correction MUST be accompanied by:

> "This issue may require secret rotation, session invalidation, or user notification. Coordinate with the user before deploying."

For multiple violations, report each rule ID separately.

Do not replace a technical correction with a generic explanation.