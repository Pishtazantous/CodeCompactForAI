---
id: 02-browser-extension-anti-slop
title: "Browser Extension Anti-Slop Layer"
lang: en
depends_on: ["_universal/00-style-guide.md", "_universal/00-master-anti-slop.md"]
category: domain
domain_type: delivery
version: 3
---

# Browser Extension Anti-Slop Layer

This file defines behavioral contracts specific to browser extensions. It sits in the delivery layer, below the universal anti-slop rules and above framework-specific web patterns. It covers manifest discipline, permissions, service worker lifecycle, content scripts, message passing, storage, UI surfaces, and store compliance. It does not cover general web page logic (see `02-frontend-anti-slop.md`), framework rules (see framework files), language rules (see language files), or detailed security and accessibility concerns (see concern files).

An extension runs inside the user's browser, on every page the user visits, with elevated privileges. The browser trusts the extension. The extension MUST be written to deserve that trust.

## Scope

This file applies to Chrome and Edge extensions (Manifest V3), Firefox extensions (Manifest V2/V3), Safari Web Extensions, and cross-browser extensions using polyfills (e.g., `webextension-polyfill`). The examples use Chrome Extension API names where illustrative. Firefox and Safari APIs differ slightly, but the principles are identical. When the browser is not specified, Manifest V3 for Chromium is assumed.

## Rule Severity

Severity follows `_universal/00-style-guide.md`.

## Contracts

A browser extension commits to six contracts. The table below maps each contract to the rules that enforce it.

| Contract | Description | Enforced By |
|---|---|---|
| Permission Minimalism | Requests only the permissions it uses. Every permission is a trust cost. | EXT-001 to EXT-004, EXT-055 |
| Isolation | Does not corrupt the host page. DOM changes are namespaced, scripts isolated, styles scoped. | EXT-016, EXT-019, EXT-022, EXT-053 |
| Stateless Service Worker | Survives termination and resumption. No persistent state in memory. | EXT-009 to EXT-015 |
| Store Compliance | Follows Chrome Web Store, Edge Add-ons, and Mozilla Add-ons policies. | EXT-005 to EXT-008, EXT-043 to EXT-048, EXT-067 |
| Data Minimalism | Collects only what it needs. Does not exfiltrate data. Discloses collection. | EXT-027, EXT-032, EXT-034, EXT-046 |
| User Control | User can disable, revoke, and uninstall without artifacts. Does not fight the user. | EXT-036, EXT-042, EXT-072 |

## Manifest Discipline

### EXT-001 — Minimal Permissions

**MUST**

Every permission is a review hurdle and a security risk. The extension MUST request only what it explicitly uses.

Example (illustrative, Chrome Extension API):

BAD:
```json
"permissions": ["tabs", "storage", "webRequest", "<all_urls>"]
```

GOOD:
```json
"permissions": ["activeTab", "storage"]
```

### EXT-002 — Optional Permissions

**SHOULD**

For features the user may not need immediately, `optional_permissions` SHOULD be used and requested at runtime. This reduces the initial trust prompt and improves install conversion.

### EXT-003 — Specific Host Permissions

**MUST**

Broad host permissions MUST NOT be used when specific origins suffice. `<all_urls>` triggers additional review and alarms users.

Example (illustrative):

BAD: `"host_permissions": ["<all_urls>"]`
GOOD: `"host_permissions": ["https://example.com/*"]`

### EXT-004 — `activeTab` Preference

**SHOULD**

`activeTab` grants temporary access to the current tab when the user invokes the extension. It SHOULD be preferred over broad host permissions for extensions that act on the active page via a user gesture.

### EXT-005 — Remote Code Prohibition

**MUST NOT**

Manifest V3 forbids loading code from a remote server. Every script MUST be bundled. `eval`, `new Function`, and remote `<script src>` MUST NOT be used. The extension's CSP enforces this.

### EXT-006 — Tight CSP

**MUST NOT**

The extension's Content Security Policy MUST NOT include `unsafe-eval` or `unsafe-inline`. If a library requires them, a different library MUST be found.

### EXT-007 — Manifest Version Bumps

**MUST**

Every publish MUST increment the manifest version. A same-version upload is rejected. Semantic versioning (e.g., `1.0.0`, `1.0.1`, `1.1.0`) MUST be used.

### EXT-008 — Minimum Browser Version

**MUST**

If the extension uses an API introduced in a recent browser version, `minimum_chrome_version` (or equivalent) MUST be stated. Older browsers will reject the install cleanly instead of failing at runtime.

## Service Worker (Background)

### EXT-009 — No Persistent Memory State

**MUST NOT**

A Manifest V3 service worker terminates after ~30 seconds of inactivity. State in module-level variables is lost and MUST NOT be relied upon.

Example (illustrative):

BAD: `let currentUser = null;`
GOOD: `await chrome.storage.session.set({ currentUser });`

### EXT-010 — Chrome Storage Usage

**MUST**

`chrome.storage` MUST be used for persistence. `storage.session` MUST be used for transient state (cleared on restart), and `storage.local` MUST be used for durable state.

### EXT-011 — Synchronous Event Listener Registration

**MUST**

Event listeners (message, alarm, action, tabs, webNavigation) MUST be registered synchronously at the top level of the service worker. Registering them inside an async function or callback causes them to miss events that fire before registration.

### EXT-012 — `chrome.alarms` Over `setInterval`

**MUST**

`setInterval` does not survive service worker termination and MUST NOT be used. `chrome.alarms` MUST be used for periodic work.

### EXT-013 — Long-Running Task Prohibition

**MUST NOT**

A task over 30 seconds may be killed by the browser. Long tasks MUST be broken into chunks, offloaded to an offscreen document, or delegated to a native host.

### EXT-014 — No DOM Access in Service Worker

**MUST NOT**

The service worker has no DOM (`document` is undefined). DOM-requiring APIs (parsing, canvas, audio) MUST use an offscreen document.

### EXT-015 — Work in Progress Persistence

**MUST**

If the service worker may be terminated mid-operation, the work MUST be persisted and resumed on the next event.

## Content Scripts

### EXT-016 — Isolated World Assumption

**MUST**

Content scripts run in an isolated world. They have access to the DOM but not to the page's JavaScript variables (e.g., `window.myApp`). Code MUST NOT assume access to the page's JS context.

### EXT-017 — Service Worker Message Passing

**MUST**

Content scripts MUST communicate with the service worker via `chrome.runtime.sendMessage`. The service worker responds asynchronously.

### EXT-018 — No `eval` in Content Scripts

**MUST NOT**

The extension's CSP forbids `eval` in content scripts. It MUST NOT be used.

### EXT-019 — Scoped DOM Changes

**MUST**

Every DOM change MUST be namespaced with a class prefix or a custom attribute to prevent conflicts with the host page's elements.

Example (illustrative):

BAD: `<div class="toolbar">...</div>`
GOOD: `<div class="myext-toolbar" data-myext="true">...</div>`

### EXT-020 — Filtered MutationObserver

**MUST**

`MutationObserver` on a busy page fires constantly. Observations MUST be filtered to the specific subtree that matters. Observing the entire `document.body` with `subtree: true` is prohibited unless strictly necessary.

### EXT-021 — Cleanup on Unload

**MUST**

DOM elements and event listeners added by the content script MUST be removed when the extension is disabled or the page unloads.

### EXT-022 — No Global Styles

**MUST NOT**

A content script MUST NOT inject global CSS (e.g., `button { background: red; }`). Styles MUST be scoped to the extension's elements or injected into a shadow DOM.

### EXT-023 — Graceful DOM Absence

**MUST**

A content script runs on any matching URL. If the page does not have the expected DOM structure, the script MUST exit cleanly without throwing errors.

## Message Passing

### EXT-024 — Typed Messages

**MUST**

Every message MUST have a `type` field. Handlers MUST switch on the type. Unknown types MUST be ignored, not silently processed.

### EXT-025 — Async Response Handling

**MUST**

An async handler MUST return `true` from the listener synchronously and call `sendResponse` later. Failing to return `true` closes the channel before the async work completes.

### EXT-026 — Sender Trust Prohibition

**MUST NOT**

A content script can claim to be from any URL. `sender.origin` or `sender.tab.url` MUST be validated when the response is sensitive. Blindly trusting the sender is prohibited.

### EXT-027 — No Sensitive Data in Messages

**MUST NOT**

Messages between content scripts and the service worker may be observed. Tokens or PII MUST NOT be passed unnecessarily.

### EXT-028 — Message Protocol Versioning

**MUST**

The message protocol MUST be versioned. A content script injected by an old version may talk to a new service worker during an update. A protocol version MUST be included and mismatches handled.

### EXT-029 — No Direct DOM Access From Messages

**MUST NOT**

The service worker does not manipulate the DOM. Messages MUST carry data, not selectors or HTML strings for the service worker to process.

### EXT-030 — Idempotent Handlers

**MUST**

Message handlers MUST be idempotent. A handler that runs twice (due to reconnections or duplicated events) MUST NOT cause harm.

## Storage

### EXT-031 — Quota Awareness

**MUST**

Storage quotas (`storage.local` default 10 MB, `storage.sync` 100 KB total / 8 KB per item) MUST be respected. Data structures MUST be designed within these limits.

### EXT-032 — No Secrets in `storage.sync`

**MUST NOT**

`storage.sync` synchronizes to the user's cloud account. Tokens and secrets MUST NOT be stored there.

### EXT-033 — Schema Versioning and Migration

**MUST**

When the stored data shape changes, a migration MUST be applied. Reading new shapes directly from old data breaks existing users.

### EXT-034 — Sensitive Data Encryption

**MUST**

If the extension stores tokens locally, they MUST be encrypted before writing to `storage.local`, as it is readable by anything with filesystem access to the user's profile.

### EXT-035 — Batched Storage Operations

**SHOULD**

`chrome.storage.local.get` and `.set` are async. Operations SHOULD be batched to reduce round trips.

### EXT-036 — Uninstall Cleanup

**MUST**

The `runtime.onInstalled` event (or `runtime.setUninstallURL`) MUST be used to clean up remote config, server-side sessions, or user-specific state that should not persist after uninstall.

## UI Surfaces

### EXT-037 — Transient Popup

**MUST**

A popup closes when the user clicks outside it. Workflows requiring multiple clicks MUST NOT be placed in the popup unless the state is strictly persisted.

### EXT-038 — Options Page for Complex Settings

**MUST**

Complex configuration MUST live in `options.html`, not in the popup. Popups are for quick actions.

### EXT-039 — Action Badge Discipline

**MUST**

The badge is 4 characters maximum. It MUST be used sparingly. A badge that is always visible without updating is noise.

### EXT-040 — Context Menu Validation

**MUST**

Context menu items MUST be registered in the service worker. The `info` argument MUST be validated before acting.

### EXT-041 — Extended UI Surfaces

**SHOULD**

Chrome's Side Panel and DevTools panels SHOULD be used when the popup is too small for the required UI.

### EXT-042 — No Full-Page Overlays

**MUST NOT**

An overlay that covers the whole page disrupts the user and MUST NOT be used. A small floating widget, a popup, or a side panel MUST be used instead.

## Publishing and Store Compliance

### EXT-043 — Store Listing Accuracy

**MUST**

The store listing MUST have a clear description, screenshots showing actual functionality, a privacy policy if handling user data, and justification for every permission in the developer dashboard.

### EXT-044 — Single Purpose

**MUST**

Chrome Web Store requires a single, narrow purpose. An extension that does multiple unrelated things will be rejected or MUST be split.

### EXT-045 — Deceptive Behavior Prohibition

**MUST NOT**

Hidden tracking, ad injection, or changing the user's search engine without explicit consent are immediate removal offenses and MUST NOT be used.

### EXT-046 — Data Collection Disclosure

**MUST**

Privacy disclosures listing collected data and its use MUST match the actual behavior of the extension.

### EXT-047 — Update Cadence and Notes

**MUST**

Breaking changes MUST include a version bump and a release note.

### EXT-048 — Reviewable Source

**MUST**

If the extension is minified, the source map or a link to the source MUST be provided. Reviewers reject opaque extensions.

## Security

### EXT-049 — Cross-Origin Request Routing

**MUST**

Content scripts cannot make cross-origin requests. The service worker MUST make them using `fetch`. URLs MUST be validated before fetching.

### EXT-050 — `chrome.scripting` Injection Validation

**MUST NOT**

User-provided paths MUST NOT be passed to `chrome.scripting.executeScript`. A static list of script files MUST be used.

### EXT-051 — No Token in URL

**MUST NOT**

Tokens in query strings are logged by proxies and leaked via referrers. They MUST be passed via headers or `chrome.storage`.

### EXT-052 — Incoming Message Validation

**MUST**

A message handler MUST validate every field of the message. A malformed message MUST NOT crash the handler.

### EXT-053 — DOM Privilege Escalation Prevention

**MUST**

A content script that reads from the page's DOM trusts page content. Values from the DOM MUST be sanitized before use to prevent XSS or privilege escalation.

## Performance

### EXT-054 — No Blocking Page Load

**MUST NOT**

A content script at `document_start` runs before the page's DOM is ready. Heavy work MUST NOT be performed there. It MUST be deferred to `DOMContentLoaded` or later.

### EXT-055 — Lazy Injection

**MUST**

Content scripts MUST only be injected on pages where they are needed. `matches` in the manifest and dynamic injection for opt-in features MUST be used. Injecting into `<all_urls>` for a niche feature is prohibited.

### EXT-056 — Bundle Size Discipline

**MUST**

The extension's bundle is downloaded once per install and stored on disk. Unused dependencies MUST be removed to keep it small.

### EXT-057 — Infinite MutationObserver Prohibition

**MUST NOT**

An observer that triggers DOM changes that trigger the observer loops forever. The cycle MUST be broken by filtering or debouncing.

### EXT-058 — Debounced Storage Writes

**MUST**

Every `chrome.storage.local.set` is async and has a cost. High-frequency writes MUST be debounced.

## AI-Specific Browser Extension Discipline

### EXT-080 — Extension API Verification

**MUST**

Before using a browser extension API (e.g., `chrome.declarativeNetRequest`, `chrome.sidePanel`), the assistant MUST verify the API exists in the target Manifest version (V2 vs V3) and browser. Invented APIs or V2 APIs used in V3 cause immediate review rejection or runtime crashes.

See MAS-036 in `_universal/00-master-anti-slop.md`.

### EXT-081 — Existing Handler Discovery

**MUST**

Before creating a new content script, message listener, or background task, the assistant MUST search the project for an existing equivalent. Inventing parallel message channels or duplicate content scripts creates state desyncs and memory leaks.

See MAS-035 in `_universal/00-master-anti-slop.md`.

### EXT-082 — Permission Restraint

**SHOULD**

The assistant SHOULD NOT suggest broad permissions (e.g., `<all_urls>`, `webRequest`) when a narrower alternative (e.g., `activeTab`, `declarativeNetRequest`) exists. Over-permissioning is the primary cause of store review rejection.

See MAS-038 in `_universal/00-master-anti-slop.md`.

## Anti-Patterns

### EXT-059 — Unhandled Message Channels

**MUST NOT**

A message handler that does not switch on `type` and does not return `false` leaves the response channel open. The caller times out. Unhandled messages MUST return `false`.

### EXT-060 — `innerHTML` XSS Prohibition

**MUST NOT**

Assigning user input or DOM-scraped text to `innerHTML` in extension pages (popup, options) is prohibited. The extension's origin has elevated privileges; XSS here is critical. `textContent` or strict sanitization MUST be used.

### EXT-061 — Unhandled Content Script Errors

**MUST**

An error in a content script may break the host page. Content scripts MUST wrap execution in try/catch and report errors to the service worker.

### EXT-062 — Synchronous Storage Reads in Hot Paths

**MUST NOT**

`chrome.storage.local.get` is async. Calling it on every keystroke or mouse move in a content script is slow. Data MUST be cached in memory.

### EXT-063 — Main Thread Blocking

**MUST NOT**

A content script that runs a heavy synchronous loop blocks the host page's rendering. Work MUST yield to the event loop or be offloaded to the service worker.

### EXT-064 — Badge Update Flicker

**MUST NOT**

Updating the action badge on every single message or event causes flicker and CPU churn. Badge updates MUST be debounced.

### EXT-065 — Silent Service Worker Failures

**MUST NOT**

A silent failure in the service worker means a broken extension with no diagnostic. Errors MUST be logged to `storage.local` or a remote service (with user consent).

### EXT-066 — `webRequest` Blocking in V3

**MUST NOT**

`webRequest` blocking is replaced by `declarativeNetRequest` in Manifest V3. Using the old blocking API is rejected by the store.

### EXT-067 — Inline Scripts in Extension Pages

**MUST NOT**

Inline `<script>` blocks in extension pages (popup, options) are rejected by the default CSP. External script files MUST be used.

### EXT-068 — `localStorage` in Extension Pages

**MUST NOT**

`localStorage` in an extension page is not synchronized with `chrome.storage` and is not accessible from the service worker. `chrome.storage` MUST be used consistently.

### EXT-069 — Unvalidated `window.open`

**MUST NOT**

`window.open(userProvidedUrl)` is prohibited. URLs MUST be validated against an allowlist of domains.

### EXT-070 — Mixed Content Prohibition

**MUST NOT**

An extension page loading `http://` resources is blocked by default. `https://` or bundled resources MUST be used.

### EXT-071 — Incognito Strategy Declaration

**MUST**

An extension that behaves differently in incognito without documentation confuses users. `incognito` mode MUST be declared in the manifest and the behavior documented.

### EXT-072 — File Download Justification

**MUST**

`chrome.downloads` requires a permission and is a review trigger. It MUST only be used when the extension genuinely downloads files, not as a convenience.

## Response to Violation

When a rule in this file is violated, report:

Violation: EXT-{NNN}
Reason: {one-line reason}
Correction: {smallest fix}

For multiple violations, report each rule ID separately.

Do not replace a technical correction with a generic explanation.