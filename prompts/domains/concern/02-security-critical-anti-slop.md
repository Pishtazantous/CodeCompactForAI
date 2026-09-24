---
id: 02-security-critical-anti-slop
title: "Security-Critical Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: concern
version: 1
---

# Security-Critical Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
security anti-patterns from section 2.4, output format) are NOT
repeated here.

This file is sent for projects where security is a first-class
requirement, not an afterthought: authentication services, payment
systems, financial products, health records, multi-tenant platforms,
and anything that handles PII, credentials, or money. It covers the
discipline of writing code that resists attack.

For most projects, the security section of `00-master-anti-slop.md`
is sufficient. This file is for the subset of projects where a single
mistake can compromise users.

## 1. When This File Applies

Send this file when the project is:

- An authentication or identity service.
- A payment gateway or a wallet.
- A system storing PII, PHI, or financial records.
- A multi-tenant platform where tenants must not see each other's
  data.
- A service exposing an API to untrusted clients.
- A cryptographic tool or a key-management system.

If the project is a static marketing site or an internal tool with
no sensitive data, this file is not necessary.

## 2. Threat Modeling Discipline

### 2.1 Identify the Assets

Before writing code, name what must be protected:

- Credentials (passwords, tokens, API keys)
- Personal data (name, email, address, phone)
- Financial data (card numbers, bank accounts, transactions)
- Health data
- Proprietary business data
- Audit logs

If the asset list is empty, this file does not apply.

### 2.2 Identify the Adversaries

Name who might attack:

- Anonymous internet users
- Authenticated users escalating privilege
- A compromised dependency
- An insider
- A nation-state (rarely; document if relevant)

The adversary determines the countermeasures. Defending against a
script kiddie is not the same as defending against a targeted
attacker.

### 2.3 Identify the Attack Surfaces

List every place untrusted input enters the system:

- HTTP requests (body, query, headers, cookies)
- WebSocket messages
- File uploads
- Webhooks from third parties
- Queue messages
- Environment variables set by operators
- Data read from a database that was written by an earlier
  compromised request

### 2.4 Assume the Network Is Hostile

Every byte from the network is attacker-controlled until validated.
Every response from a third-party service may be compromised. Every
certificate may be revoked. Every DNS answer may be spoofed.

### 2.5 Assume the Client Is Compromised

The browser, the mobile app, the CLI, the desktop client: all are
attacker-controlled. Never trust a client-provided:

- User ID
- Role
- Permission flag
- Price
- Discount
- Timestamp
- Amount

The server decides these from authoritative sources.

## 3. Authentication

### 3.1 Never Roll Your Own Crypto

Use the platform's or the language's standard library for:

- Password hashing (bcrypt, argon2, scrypt)
- Random number generation (`secrets` in Python, `crypto.randomBytes`
  in Node.js, `crypto/rand` in Go)
- Symmetric encryption (AES-GCM, ChaCha20-Poly1305)
- Key derivation (HKDF, PBKDF2)
- Signature verification (Ed25519, ECDSA P-256)

Never invent a cipher, a hash, or a protocol.

### 3.2 Password Hashing Parameters

- Argon2id with current OWASP-recommended parameters, or
- bcrypt with cost >= 12, or
- scrypt with appropriate memory/time cost.

Never MD5, SHA-1, SHA-256 alone, or any fast hash for passwords.

### 3.3 Constant-Time Comparison for Secrets

BAD: `if (providedToken === storedToken)`
GOOD: `crypto.timingSafeEqual(providedToken, storedToken)`

Length leaks are also side channels. Compare padded values or use
the language's constant-time primitive.

### 3.4 Rate Limit Authentication

Every login, password reset, OTP verification, and API key validation
has a rate limit. Per-account, per-IP, and per-device where relevant.

### 3.5 Account Lockout With Care

Permanent lockout enables a denial-of-service attack by an adversary
who knows a victim's email. Use exponential backoff or a temporary
lockout with a clear unlock path.

### 3.6 Multi-Factor Authentication

When the project supports MFA:

- TOTP secrets are stored encrypted at rest.
- Recovery codes are single-use and stored hashed.
- MFA cannot be bypassed by password reset without a second factor.
- MFA setup requires re-authentication with the current password.

### 3.7 Session Tokens

- Generated from a cryptographically secure random source.
- At least 128 bits of entropy.
- Stored hashed on the server if they are session identifiers.
- Rotated on login and privilege change.
- Invalidated on logout, password change, and account suspension.

### 3.8 JWT

- Signed with a strong algorithm (RS256, ES256, EdDSA). Never `none`.
- `alg` header is validated against an allowlist. Never trust the
  token's own `alg`.
- Short expiry (minutes, not days). Refresh tokens are separate.
- `aud`, `iss`, `exp`, `nbf` are validated on every request.
- Revocation is handled (a deny list or short expiry with rotation).

### 3.9 OAuth / OIDC

- `state` parameter is used and validated (CSRF protection).
- `nonce` is used for OIDC and validated.
- `redirect_uri` is validated against an exact-match allowlist.
- PKCE is used for public clients.
- Tokens are never sent to the frontend channel; the backend holds
  them.

### 3.10 API Keys

- Never logged, never in URLs, never in error messages.
- Stored hashed on the server.
- Scoped to a specific tenant or permission set.
- Rotatable without downtime.
- Revocable immediately.

## 4. Authorization

### 4.1 Server-Side Only

Authorization is decided on the server. The frontend may hide a
button; the server decides whether the action is allowed.

BAD: The UI hides "Delete" for non-admins, and the delete endpoint
trusts any authenticated caller.
GOOD: The delete endpoint checks the caller's role before acting.

### 4.2 Deny by Default

Every endpoint, every resource, every field starts inaccessible.
Permissions are added explicitly.

BAD: A new endpoint inherits the middleware of its router without
an explicit check.
GOOD: A new endpoint explicitly declares its required permission.

### 4.3 Object-Level Authorization

Checking "is the user authenticated" is not enough. The server must
check "does this user own this resource".

BAD:
```typescript
app.get("/orders/:id", auth, async (req, res) => {
  const order = await db.orders.findById(req.params.id);
  res.json(order); // any user can read any order
});
GOOD:

typescript
app.get("/orders/:id", auth, async (req, res) => {
  const order = await db.orders.findOne({
    id: req.params.id,
    userId: req.user.id,
  });
  if (!order) return res.status(404).json({ error: "not found" });
  res.json(order);
});```
Return 404, not 403, when the resource exists but belongs to another
user. Returning 403 leaks existence.

4.4 Function-Level Authorization
Beyond ownership, check that the caller's role permits the operation.
A regular user calling an admin endpoint is rejected even if the
endpoint is behind auth.

4.5 Never Trust a Role From the Client
The role is read from the session or from a database lookup, never
from a header, a query param, or a body field.

4.6 Privilege Escalation Paths
Audit for:

A user updating their own role via a profile update endpoint.

A user assigning themselves to an admin group.

A user changing their tenant ID.

A user editing a record they are not the owner of.

Every field the user can write must be allowlisted. Never bind the
request body directly to the model.

5. Input Validation and Output Encoding
5.1 Validate at the Boundary
Every external input is validated before use, using the project's
schema library. The schema is the contract.

5.2 Validate on Type, Length, Format, Range
Type: string, number, boolean, object.

Length: max chars for strings, max items for arrays.

Format: email regex, URL scheme allowlist, UUID shape.

Range: numeric min/max, date bounds.

5.3 Never Blacklist, Always Allowlist
A blacklist of known-bad patterns is always incomplete. An allowlist
of known-good patterns is enforceable.

5.4 Output Encoding Depends on Context
HTML context: HTML-encode <, >, &, ", '.

Attribute context: quote attributes, encode quotes.

URL context: percent-encode.

JavaScript context: JSON-encode and escape </script>.

CSS context: avoid dynamic CSS entirely if possible.

SQL: parameterized queries, never string concatenation.

5.5 Never Concatenate Untrusted Input Into:
SQL queries

Shell commands

HTML strings

LDAP queries

XPath queries

Log format strings (log injection)

Template engines evaluated at runtime

eval, Function, exec

Filesystem paths

5.6 File Uploads
Validate the content type, not just the extension.

Limit size, count, and total.

Store outside the web root, or in object storage.

Rename to a safe identifier (UUID) before storing.

Never execute, never include, never serve with the user's original
name if that name contains path separators.

Scan for malware if the project handles untrusted files.

5.7 Never eval, Function(), exec, pickle.loads, yaml.load
JavaScript: no eval, no new Function(userInput).

Python: no eval, no exec, no pickle on untrusted data.

Ruby: no eval.

PHP: no eval, no assert with strings.

Java: no ScriptEngine with untrusted scripts.

YAML: always safe_load (Python), safeLoad (Ruby), never the
default loader.

6. Data Protection
6.1 Secrets Never in Source
Covered in universal section 2.4. Repeating with specifics:

.env files are gitignored.

CI secrets come from the CI's secret store.

Production secrets come from a secret manager (Vault, AWS Secrets
Manager, GCP Secret Manager).

No secret in a Docker image layer.

No secret in a build artifact.

6.2 Encryption at Rest
PII, credentials, and financial data are encrypted at the column
level or the file level, in addition to the database's own
encryption.

Encryption keys are managed separately from the encrypted data.
Rotating keys must be possible without re-encrypting everything
blindly.

6.3 Encryption in Transit
TLS 1.2 or 1.3 everywhere. No plaintext HTTP for anything that
carries a token, a password, or personal data.

HSTS is enabled. Redirects from HTTP to HTTPS are permanent.

6.4 Never Log Secrets
Covered in universal section 2.4. Repeating with specifics:

Tokens, session IDs, API keys: never.

Passwords: never, not even hashed.

Credit card numbers: never, not even the last four (unless the
project's policy allows the last four).

Full request bodies: never when they may contain the above.

PII: only when necessary, and with the project's logging policy.

6.5 PII Minimization
Collect only what the business needs. Store only what is used. Delete
when no longer needed. Provide users a path to export and delete
their data.

6.6 Data Retention
Define retention for every category of data. Logs, sessions,
audit trails, user-generated content. Never keep indefinitely without
a reason.

6.7 Backups Are Encrypted
A backup of an unencrypted database is an unencrypted database in a
different folder. Encrypt backups with a key that is not stored in
the same location.

7. Session and Cookie Security
7.1 Session Cookies
HttpOnly: always for session tokens. Prevents JavaScript access.

Secure: always. No exceptions in production.

SameSite=Lax or SameSite=Strict: for session cookies. None
only when cross-site is genuinely needed, and then with Secure.

Path: as narrow as practical.

Domain: avoid unless necessary.

7.2 CSRF Protection
For cookie-based sessions, CSRF protection is mandatory:

Synchronizer token, or

Double-submit cookie with a signed token, or

SameSite=Strict plus an origin check.

For API-only services using Authorization header tokens, CSRF is
not applicable.

7.3 Session Fixation
Regenerate the session ID on login and on privilege change. Never
accept a session ID from the URL.

7.4 Logout
Logout invalidates the session on the server, not just on the client.
Clearing the cookie is not enough.

7.5 Idle and Absolute Timeouts
Sessions expire after inactivity and after an absolute duration.
Both are configurable and enforced server-side.

8. Cryptography
8.1 Use High-Level Libraries
Use libsodium or the platform's crypto module.

Use the library's high-level API (secretbox, sealed box) rather
than its low-level primitives when possible.

8.2 Never Reuse a Nonce
For AES-GCM and ChaCha20-Poly1305, a nonce reused with the same key
is catastrophic. The library's high-level API manages nonces. Do not
manage them manually without a documented plan.

8.3 Random, Not Pseudorandom
Secrets: crypto.randomBytes, secrets.token_bytes, crypto/rand.

Not: Math.random, random.random, rand.Intn (without seeding
from a secure source).

8.4 Key Management
Keys are generated from a CSPRNG.

Keys are stored in a KMS or a secret manager.

Keys are rotated on a schedule.

Key material is never logged, never printed, never in a stack
trace.

8.5 Signature Verification
Verify signatures before trusting the payload.

Verify the algorithm matches the expected algorithm. Never accept
the payload's own claim about which algorithm was used.

Reject unsigned payloads when the protocol requires signing.

8.6 Deprecated Algorithms
Never use:

MD5, SHA-1 for anything security-relevant.

DES, 3DES, RC4.

RSA with keys under 2048 bits.

ECB mode.

Static IVs.

9. Dependencies and Supply Chain
9.1 Every Dependency Is a Risk
Before adding a package:

Check its maintenance status (last release, open issues).

Check its download count and reputation.

Check its transitive dependencies.

Check its license.

9.2 Lockfiles Are Committed
package-lock.json, yarn.lock, poetry.lock, Cargo.lock,
go.sum are committed. Never ignored.

9.3 Dependency Updates
Security patches are applied promptly.

Updates are reviewed before merge (not auto-merged blindly).

The project runs a vulnerability scanner (npm audit,
pip-audit, govulncheck, Dependabot).

9.4 Typosquatting
Verify the package name character-by-character before installing.
cross-env and crossenv are different packages.

9.5 Postinstall Scripts
A dependency's postinstall script runs arbitrary code at install
time. If the project disables them (--ignore-scripts), respect
that. Do not re-enable without a reason.

10. Error Messages and Information Disclosure
10.1 Neutral Authentication Errors
BAD: "No account with that email" (reveals existence).
GOOD: "Invalid email or password" (neutral).

The same neutral message for wrong password and unknown user.

10.2 No Stack Traces to the Client
Covered in 02-backend-anti-slop.md section 4. Repeating because it
is the most common leak.

10.3 No Internal Identifiers in Errors
Database IDs, internal service names, file paths, hostnames: none
in client-visible errors.

10.4 No Debug Endpoints in Production
/debug, /metrics (unless protected), /actuator (unless
protected), /__webpack_hmr. All removed or gated behind
authentication.

10.5 No Source Maps in Production
Unless the project explicitly serves them behind authentication for
error tracking. Public source maps reveal the entire codebase.

10.6 No Version Numbers in Headers
Server: nginx/1.18.0 tells the attacker which CVEs to try. Set a
generic value or omit.

11. Logging and Monitoring
11.1 Log Security Events
Login success and failure

Password change

Permission change

Access to sensitive resources

Admin actions

Rate limit hits

CSRF, CORS, CSP violations

11.2 Logs Are Tamper-Resistant
Security logs go to a system that the application cannot modify:
a separate service, append-only storage, or a SIEM.

11.3 Alert on Anomalies
Spike in login failures

Login from a new country

Access to many resources by one account

Failed authorization attempts

11.4 Never Log the Sensitive Payload
Covered in 6.4. Repeating: the log is often less protected than the
database.

12. Security-Critical Anti-Patterns
12.1 Trusting the Client
Covered in 2.5. The single most common vulnerability.

12.2 The Check That Only the Frontend Does
The backend has no authorization check. The frontend hides the
button. Any attacker with a proxy bypasses the UI.

12.3 Disabling Security "Temporarily"
BAD: app.use(cors({ origin: "*" })) in a commit that says
"temporary".
GOOD: The correct origin allowlist, always.

12.4 http:// in Production
Even for internal services. Credentials, tokens, and PII travel in
plaintext.

12.5 Storing Secrets in Git
Even in a private repository, even in a branch that will be deleted.
The secret must be rotated the moment it enters Git history.

12.6 Rolling Your Own JWT Validation
Verifying the signature is not enough. The alg, exp, nbf,
aud, iss must all be checked. Use the library's full validation,
not a hand-written jwt.verify(token, secret).

12.7 Ignoring SameSite
A cookie without SameSite is sent with every cross-site request.
The default in modern browsers is Lax, but relying on the default
in code that must work everywhere is a mistake.

12.8 CORS Misconfiguration
BAD: Access-Control-Allow-Origin: * with
Access-Control-Allow-Credentials: true. This combination is
rejected by browsers, but a misconfigured proxy may still serve it.

BAD: Reflecting the Origin header without validating it against
an allowlist.

12.9 Mass Assignment
BAD:

typescript
const user = await User.create(req.body);
The client can set role, isAdmin, balance, or any other field.

GOOD: Extract the allowed fields explicitly, or use a schema that
whitelists them.

12.10 IDOR (Insecure Direct Object Reference)
Covered in 4.3. Repeating because it is the most common API
vulnerability.

12.11 Sequential IDs as the Only Protections
Using an auto-increment ID does not protect an endpoint. The check
is authorization, not obscurity. UUIDs reduce enumeration but do
not replace the check.

12.12 Password Reset Token Reuse
A reset token is single-use. After use, it is invalidated. The
password change endpoint does not accept the same token twice.

12.13 Time-Based Comparison
Covered in 3.3. Repeating: === on tokens leaks timing.

12.14 JSON.parse on Untrusted Deeply Nested Data
A JSON payload with 10,000 levels of nesting causes a stack
overflow in some parsers. Limit depth.

12.15 SSRF (Server-Side Request Forgery)
BAD: An endpoint that fetches a URL provided by the user.
The attacker requests http://169.254.169.254/... (cloud metadata)
or an internal service.

GOOD: Validate the URL against an allowlist of hosts. Resolve DNS
and check the IP against a denylist of private ranges. Do not follow
redirects blindly.

12.16 XXE (XML External Entity)
XML parsers that resolve external entities allow reading local
files or making network requests. Disable external entity
resolution in every XML parser.

12.17 Open Redirect
BAD: /login?next=https://evil.com redirects after login.
GOOD: The next parameter is validated to be a relative path
within the site, or an allowlisted host.

12.18 Prototype Pollution (JavaScript)
BAD:

typescript
function merge(target, source) {
  for (const key in source) target[key] = source[key];
}
If source is { "__proto__": { "isAdmin": true } }, every object
inherits isAdmin.

GOOD: Use Object.create(null) for dictionaries, or a merge
function that blocks __proto__, constructor, and prototype.

12.19 Object.assign({}, userInput)
Same issue as 12.18 in a different form.

12.20 Regex Denial of Service (ReDoS)
A regex with nested quantifiers on untrusted input can run for
minutes. Test regexes against adversarial input, or use a
linear-time engine.

12.21 Deserialization of Untrusted Data
Java: ObjectInputStream. Python: pickle. Ruby: Marshal.load.
PHP: unserialize. All allow code execution. Never on untrusted
input.

12.22 Environment Variable Injection
If the app reads env vars from a file it does not own, or from
user-controlled input, an attacker can override configuration.

12.23 Timing Attacks on Password Reset
A reset endpoint that responds differently for known and unknown
emails leaks account existence. Respond identically and take the
same time.

12.24 Cache Poisoning
A response cache that keys on the URL but ignores the Host,
Authorization, or Cookie header. An attacker's response is
served to another user.

13. Security Review Discipline
13.1 Threat Model Every New Endpoint
For every new endpoint, answer:

Who can call it?

What does it expose?

What does it allow the caller to change?

What is the worst-case abuse?

13.2 Review Diffs for Secrets
Before committing, review the diff for anything that looks like a
secret. An accidental commit is faster to prevent than to remediate.

13.3 Never Merge a Security Fix Without Tests
A security fix without a regression test will regress. Write the
test that fails before the fix and passes after.

13.4 Report, Do Not Silently Fix
If you find a security issue while working on an unrelated task,
report it to the user with a clear description. Do not fix it
silently; the fix may need coordination (rotation, notification,
audit).

13.5 Document Assumptions
Security relies on assumptions about the deployment, the network,
and the operators. State them. When the assumptions change, the
security changes.

14. Response to Violation
If a previous response violated a rule here:

text
In the previous response, [specific rule] was violated. Correction:
[corrected code]
No justification. No apology paragraph. Fix and move on.

If the violation is in already-deployed code, the correction is
accompanied by a note: "This issue may require secret rotation,
session invalidation, or user notification. Coordinate with the
user before deploying."

text

---