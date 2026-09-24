---
id: 02-browser-extension-anti-slop
title: "Browser Extension Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: delivery
version: 1
---
# Browser Extension Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules are not
repeated. Browser and framework behavior belongs to related layers.

## 1. Stack Assumptions

**1.1 Target Manifest V3.** Confirm the manifest version, minimum browser,
service-worker lifecycle, and packaging channel before implementation.

**1.2 Map extension surfaces.** Identify background, content script, popup,
options, side panel, storage, alarms, and externally connectable origins.

**1.3 Use declared capabilities.** Request only permissions and host
permissions required by reviewed behavior.

## 2. Domain Contracts

**2.1 Contexts are isolated.** Background, content, and extension pages use
messaging contracts instead of importing privileged browser APIs everywhere.

**2.2 Content scripts are defensive.** They validate page data, avoid unsafe
HTML insertion, and do not expose extension secrets to the page.

**2.3 Messaging is typed and bounded.** Validate sender, origin, message
kind, payload shape, and size before acting.

**2.4 State is durable and minimal.** Use extension storage according to
sensitivity and size; do not store unnecessary browsing history.

## 3. Domain-Specific Rules

**3.1 Handle service-worker restart.** Persist state needed to resume work;
do not rely on a persistent global process.

**3.2 Use alarms and events instead of timers.** Long intervals and wakeups
use the extension lifecycle mechanism appropriate to the feature.

**3.3 Minimize host permissions.** Prefer active-tab or narrow origins over
`<all_urls>` when the product requirement allows it.

**3.4 Escape all page insertion.** Treat DOM text and URLs as untrusted; use
safe text assignment, URL validation, and existing sanitizer policy.

**3.5 Restrict messaging.** Reject unknown runtime senders, origin mismatches,
and oversized or unknown message types.

**3.6 Make scripts idempotent.** Re-injection or navigation may run a content
script again; guard initialization and remove listeners.

**3.7 Observe CSP and web-accessible resources.** Do not weaken page or
extension CSP, inject remote code, or expose broad script resources.

**3.8 Respect privacy boundaries.** Avoid collecting unrelated URLs, tokens,
or page content; provide deletion and retention behavior.

**3.9 Test update and disable paths.** Verify upgrade, browser restart,
extension reload, revoked host access, and uninstall cleanup.

**3.10 Review permissions at release.** Match manifest permissions to current
features and remove unused capability.

**3.25 Keep initialization idempotent.** A content script checks its marker before registering listeners or changing the page.

**3.26 Bound page data.** Message size, nesting, text length, and URL length are checked before parsing or forwarding page content.

**3.27 Version stored state.** Storage migrations preserve required records, reject malformed values, and do not silently discard settings.

**3.28 Handle permission revocation.** A revoked host permission produces a disabled state without repeated prompts or failed background work.

**3.29 Verify release policy.** Test the packaged manifest, production CSP, storage area, icons, and minimum supported browser behavior.

**3.30 Keep initialization idempotent.** Re-injection and navigation do not duplicate listeners or page mutations.

**3.31 Bound page data.** Validate sender, origin, message kind, payload, URL, and size before acting.

**3.32 Verify packaged policy.** Test the production manifest, CSP, storage, permissions, and oldest supported browser.

## 4. Domain-Specific Anti-Patterns

### 4.1 Unvalidated Runtime Message

BAD:
```javascript
chrome.runtime.onMessage.addListener((message) => {
  fetch(message.url);
});
```

GOOD:
```javascript
chrome.runtime.onMessage.addListener((message, sender) => {
  if (sender.id !== chrome.runtime.id || !allowlisted(message.kind)) return;
  handle(message.payload);
});
```

The receiver authenticates and validates the contract.

### 4.2 Secret in Content Script

BAD:
```javascript
const token = await chrome.storage.local.get("apiKey");
document.body.dataset.token = token.apiKey;
```

GOOD:
```javascript
const response = await chrome.runtime.sendMessage({ kind: "lookup" });
render(response);
```

The page never receives the credential.

### 4.3 Broad Host Permission

BAD:
```json
{ "host_permissions": ["<all_urls>"] }
```

GOOD:
```json
{ "host_permissions": ["app.example.com/*"] }
```

Access is limited to the feature's domain.

**3.11 Make navigation idempotent.** A content script can run again after a route change; initialization guards must not duplicate listeners or mutations.

**3.12 Bound storage.** Respect extension quota and storage-area rules, and handle quota failure without discarding required state silently.

**3.13 Review external resources.** Every web-accessible resource has a documented purpose and does not expose secrets or unrestricted executable code.

**3.14 Handle API absence.** Feature-detect optional browser APIs and provide a safe disabled state for unsupported browsers.

**3.15 Test hostile pages.** Include hostile DOM, unexpected message shapes, rapid navigation, extension disablement, and permission changes.

**3.16 Separate content-script data.** Page text remains untrusted and is passed to the extension only through a bounded, typed contract.

**3.17 Review injected styles.** Scope selectors and properties to the feature; do not modify unrelated page layout or user settings.

**3.18 Handle storage races.** Serialize updates or use a documented merge policy so concurrent contexts do not lose required state.

**3.19 Make permissions observable.** Surface why a permission is needed and what feature stops working when access is denied.

**3.20 Version data migrations.** Storage keys include a schema version and can recover or reject old values without crashing startup.

**3.21 Verify packaged policy.** Run the extension with production CSP, manifest, icons, permissions, and release metadata.

**3.22 Handle extension updates.** Preserve required storage and pending work across update, and cancel work that can no longer complete safely.

**3.23 Minimize page disturbance.** A content script changes only the DOM owned by the feature and removes its listeners and nodes on teardown.

**3.24 Check browser support.** Feature availability and permission outcomes are tested on the oldest supported browser target.

## 5. Response to Violation

If a prior response violated this layer, identify the manifest, permission,
lifecycle, messaging, CSP, or isolation issue and show the corrected contract.
Do not claim browser behavior without a manifest-compatible test.
