---
id: 02-browser-extension-anti-slop
title: "Browser Extension Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: delivery
version: 2
---

# Browser Extension Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
generic security, dependency addition, output format) are NOT
repeated here.

This file covers rules specific to browser extensions: manifest
discipline, permissions, service worker lifecycle, content scripts,
message passing, storage, UI surfaces, and store compliance. It does
NOT cover web page logic (see `02-frontend-anti-slop.md`), framework
rules (see the framework files), language rules (see the language
files), or security and accessibility concerns in detail (see the
concern files).

An extension runs inside the user's browser, on every page the user
visits, with elevated privileges. The browser trusts the extension.
The extension must be written to deserve that trust.

## 1. Stack Assumptions

This file applies to:

- Chrome and Edge extensions (Manifest V3).
- Firefox extensions (Manifest V2, migrating to V3).
- Safari extensions (Safari Web Extensions, based on WebKit).
- Cross-browser extensions using a polyfill (`webextension-polyfill`).

The examples use the Chrome extension API names. Firefox and Safari
names differ slightly. The principles are identical. When the
browser is not specified, assume Manifest V3 for Chromium.

## 2. Delivery Contracts

A browser extension commits to six contracts. Every section below
enforces one or more of these.

### 2.1 Permission Minimalism

The extension requests only the permissions it uses. Every
permission is a trust cost and a review hurdle.

### 2.2 Isolation

The extension does not corrupt the host page. Its DOM changes are
namespaced and removable. Its scripts run in isolated worlds. Its
styles are scoped.

### 2.3 Stateless Service Worker

The service worker may be terminated at any time. Every behavior
survives termination and resumption.

### 2.4 Store Compliance

The extension follows the Chrome Web Store, Edge Add-ons, and
Mozilla Add-ons policies. Non-compliance means removal.

### 2.5 Data Minimalism

The extension collects only what it needs. It does not exfiltrate
data. It discloses what it collects.

### 2.6 User Control

The user can disable the extension, revoke permissions, and uninstall
without leaving artifacts. The extension does not fight the user.

## 3. Manifest Discipline

### 3.1 Minimal Permissions

Every permission is a review hurdle and a security risk. Request
only what the extension uses.

BAD:
```json
"permissions": ["tabs", "storage", "webRequest", "<all_urls>"]
```

For an extension that reads the current tab's URL, the above is
over-permissioned.

GOOD:
```json
"permissions": ["activeTab", "storage"]
```

### 3.2 Optional Permissions

For features the user may not need immediately, use
`optional_permissions` and request at runtime. This reduces the
initial trust prompt and improves install conversion.

### 3.3 Specific Host Permissions

BAD:
```json
"host_permissions": ["<all_urls>"]
```

GOOD:
```json
"host_permissions": ["https://example.com/*"]
```

`<all_urls>` triggers additional review and alarms users. Use a
specific origin when possible.

### 3.4 `activeTab` Over Broad Host Permissions

`activeTab` grants temporary access to the current tab when the user
invokes the extension. It is preferred over host permissions for
extensions that act on the active page.

### 3.5 No Remote Code

Manifest V3 forbids loading code from a remote server. Every script
is bundled. No `eval`, no `new Function`, no remote `<script src>`.
The extension's CSP enforces this.

### 3.6 Tight CSP

The extension's Content Security Policy does not include
`unsafe-eval` or `unsafe-inline`. If a library requires them, find
another library.

### 3.7 Manifest `version` Bumps

Every publish increments the manifest version. A same-version upload
is rejected. Use semantic versioning: `1.0.0`, `1.0.1`, `1.1.0`.

### 3.8 `minimum_chrome_version`

If the extension uses an API introduced in a recent Chrome version,
state the minimum. Older browsers reject the install cleanly
instead of failing at runtime.

## 4. Service Worker (Background)

### 4.1 No Persistent State in Memory

A Manifest V3 service worker terminates after 30 seconds of
inactivity. State in module-level variables is lost.

BAD:
```javascript
let currentUser = null;
```

GOOD:
```javascript
await chrome.storage.session.set({ currentUser });
```

### 4.2 Use `chrome.storage` for Persistence

- `storage.session`: in-memory, cleared on browser restart.
- `storage.local`: persists until uninstalled.
- `storage.sync`: syncs across devices, quota-limited.

Choose the right one. `storage.session` for transient state,
`storage.local` for durable state.

### 4.3 Event Listeners Registered Synchronously

Event listeners (message, alarm, action, tabs, webNavigation) are
registered at the top level of the service worker, not inside an
async function or a callback. Otherwise the listener is registered
after the event fires.

BAD:
```javascript
chrome.storage.local.get(["enabled"]).then(({ enabled }) => {
  if (enabled) {
    chrome.runtime.onMessage.addListener(handleMessage);
  }
});
```

GOOD:
```javascript
chrome.runtime.onMessage.addListener(handleMessage);
```

The handler itself reads state from `chrome.storage` when needed.

### 4.4 `chrome.alarms` Over `setInterval`

`setInterval` does not survive service worker termination. Use
`chrome.alarms` for periodic work.

BAD:
```javascript
setInterval(checkForUpdates, 60_000);
```

GOOD:
```javascript
chrome.alarms.create("check-updates", { periodInMinutes: 1 });
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === "check-updates") checkForUpdates();
});
```

### 4.5 No Long-Running Tasks

A task over 30 seconds may be killed. Break into chunks, use an
offscreen document, or offload to a native host.

### 4.6 No DOM Access in the Service Worker

The service worker has no DOM. `document` is undefined. Use an
offscreen document for DOM-requiring APIs (parsing, canvas,
audio).

### 4.7 Persist Work in Progress

If the service worker may be terminated mid-operation, persist the
work and resume on the next event.

## 5. Content Scripts

### 5.1 Isolated World by Default

Content scripts run in an isolated world. They have access to the
DOM but not to the page's JavaScript variables. `window.myApp` is
not accessible.

### 5.2 Message Passing to the Service Worker

Content scripts communicate with the service worker via
`chrome.runtime.sendMessage`. The service worker responds
asynchronously.

### 5.3 No `eval` in Content Scripts

Same rule as the service worker. The extension's CSP forbids it.

### 5.4 Scoped DOM Changes

Every DOM change is namespaced with a class prefix or a custom
attribute. Without it, the extension's elements conflict with the
page's.

BAD:
```html
<div class="toolbar">...</div>
```

GOOD:
```html
<div class="myext-toolbar" data-myext="true">...</div>
```

### 5.5 `MutationObserver` With Filtering

`MutationObserver` on a busy page fires constantly. Filter the
observations to the subtree that matters.

BAD:
```javascript
observer.observe(document.body, { childList: true, subtree: true });
```

GOOD:
```javascript
observer.observe(document.querySelector("#app"), {
  childList: true,
  subtree: false,
});
```

### 5.6 Cleanup on Unload

DOM elements added by the content script are removed when the
extension is disabled or the page unloads.

### 5.7 No Global Styles

A content script does not inject global CSS. Styles are scoped to
the extension's elements, or injected into a shadow DOM.

BAD:
```css
button { background: red; }
```

GOOD:
```css
.myext-toolbar button { background: red; }
```

### 5.8 Handle Pages Without the Expected DOM

A content script runs on any matching URL. If the page does not
have the expected structure, the script exits cleanly.

## 6. Message Passing

### 6.1 Typed Messages

Every message has a `type` field. Handlers switch on the type.
Unknown types are ignored, not silently processed.

```javascript
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  switch (msg.type) {
    case "GET_USER": return handleGetUser(sendResponse);
    case "SET_USER": return handleSetUser(msg, sendResponse);
    default: return false;
  }
});
```

### 6.2 Async Responses

An async handler returns `true` from the listener and calls
`sendResponse` later.

BAD:
```javascript
chrome.runtime.onMessage.addListener(async (msg, sender, sendResponse) => {
  const result = await handle(msg);
  sendResponse(result); // channel already closed
});
```

GOOD:
```javascript
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  (async () => {
    const result = await handle(msg);
    sendResponse(result);
  })();
  return true;
});
```

### 6.3 Never Trust the Sender

A content script can claim to be from any URL. Validate
`sender.origin` or `sender.tab.url` when the response is sensitive.

### 6.4 No Sensitive Data in Messages

Messages between content scripts and the service worker may be
observed. Do not pass tokens or PII unnecessarily.

### 6.5 Message Versioning

The message protocol is versioned. A content script injected by an
old version talks to a new service worker during an update.
Include a protocol version in messages and handle mismatches.

### 6.6 No Direct DOM Access From Messages

The service worker does not manipulate the DOM. The content script
does. Messages carry data, not selectors or HTML strings.

### 6.7 Idempotent Handlers

A message handler that runs twice does not cause harm. This matters
during reconnections and duplicated events.

## 7. Storage

### 7.1 Quotas

`chrome.storage.local` has a 10 MB quota by default (unlimited with
the `unlimitedStorage` permission). `chrome.storage.sync` has 100 KB
total, 8 KB per item. Design within these limits.

### 7.2 No Secrets in `storage.sync`

`storage.sync` synchronizes to the user's Google account. Do not
put tokens there.

### 7.3 Schema Versioning

When the stored data shape changes, migrate. Otherwise existing
users' data is misread.

BAD:
```javascript
const { settings } = await chrome.storage.local.get("settings");
// assumes the new shape; old data breaks
```

GOOD:
```javascript
const { settings, schemaVersion = 1 } = await chrome.storage.local.get([
  "settings",
  "schemaVersion",
]);
const migrated = migrateSettings(settings, schemaVersion);
```

### 7.4 Encrypt Sensitive Data

If the extension stores tokens, encrypt them before writing. The
`storage.local` area is readable by anything with filesystem access
to the user's profile.

### 7.5 Batch Reads and Writes

`chrome.storage.local.get` and `.set` are async. Batch operations
to reduce round trips.

BAD:
```javascript
const a = await chrome.storage.local.get("a");
const b = await chrome.storage.local.get("b");
const c = await chrome.storage.local.get("c");
```

GOOD:
```javascript
const { a, b, c } = await chrome.storage.local.get(["a", "b", "c"]);
```

### 7.6 Clean Up on Uninstall

The `runtime.onInstalled` event with `details.reason === "uninstall"`
allows cleanup. Use it for remote config, server-side sessions, or
user-specific state that should not persist.

## 8. UI Surfaces

### 8.1 Popup Is Transient

A popup closes when the user clicks outside it. Do not put workflows
that require multiple clicks in the popup unless the state is
persisted.

### 8.2 Options Page for Complex Settings

Options live in `options.html`, not in the popup. Popups are for
quick actions, not configuration.

### 8.3 Action Badge

The badge is 4 characters maximum. Use it sparingly. A badge that
is always visible is noise.

### 8.4 Context Menus

Register context menu items in the service worker. Validate the
`info` argument before acting.

### 8.5 Side Panel and DevTools

Chrome's Side Panel and DevTools panels are for extended UI. Use
them when the popup is too small.

### 8.6 No Full-Page Overlays

An overlay that covers the whole page disrupts the user. Use a
small floating widget, a popup, or a side panel.

## 9. Publishing and Store Compliance

### 9.1 Store Listing Content

- Clear description.
- Screenshots showing actual functionality.
- Privacy policy if the extension handles user data.
- Justification for every permission in the developer dashboard.

### 9.2 Single Purpose

Chrome Web Store requires a single, narrow purpose. An extension
that does five things is rejected or split.

### 9.3 No Deceptive Behavior

No hidden tracking, no ad injection, no changing the user's search
engine without consent. Deceptive behavior is an immediate removal.

### 9.4 Data Collection Disclosure

Both Chrome and Firefox require a privacy disclosure listing the
data collected and its use. Match the disclosure to the actual
behavior.

### 9.5 Update Cadence

Frequent updates are fine, but each update is reviewed. A breaking
change requires a version bump and a release note.

### 9.6 No Remotely Hosted Code

Manifest V3 forbids loading code from a remote server. Every script
is bundled. Configuration and rules can be remote; code cannot.

### 9.7 Reviewable Source

If the extension is minified, provide the source map or a link to
the source. Reviewers reject opaque extensions.

## 10. Security

### 10.1 Cross-Origin Requests Through the Service Worker

Content scripts cannot make cross-origin requests. The service
worker does, using `fetch`. Validate the URLs before fetching.

### 10.2 `chrome.scripting` Injection With Validation

BAD:
```javascript
chrome.scripting.executeScript({
  target: { tabId },
  files: [userProvidedPath],
});
```

GOOD: A static list of script files. Never a user-provided path.

### 10.3 Content Security Policy

The extension's CSP is set in the manifest. Do not weaken it.
`unsafe-eval` and `unsafe-inline` are rejected by the store.

### 10.4 No Token in URL

Tokens in query strings are logged by proxies and leaked via
referrers. Use headers or `chrome.storage`.

### 10.5 Validate Incoming Messages

A message handler validates every field of the message. A malformed
message does not crash the handler.

### 10.6 No Privilege Escalation via DOM

A content script that reads from the page's DOM trusts page
content. Sanitize before using values from the DOM.

## 11. Performance

### 11.1 No Blocking Page Load

A content script at `document_start` runs before the page's DOM is
ready. Do not perform heavy work there. Defer to `DOMContentLoaded`
or later.

### 11.2 Lazy Injection

Inject content scripts only on pages where they are needed. Use
`matches` in the manifest and dynamic injection for opt-in features.

### 11.3 Bundle Size

The extension's bundle is downloaded once per install and stored on
disk. Keep it small. Unused dependencies inflate the package.

### 11.4 No Infinite `MutationObserver`

An observer that triggers DOM changes that trigger the observer
loops forever. Break the cycle by filtering or debouncing.

### 11.5 Debounce Storage Writes

Every `chrome.storage.local.set` is async and has a cost. Debounce
high-frequency writes.

## 12. Anti-Patterns

### 12.1 Broad Permissions

Covered in 3.1 and 3.3. Over-permissioning is the most common
review rejection cause.

### 12.2 Remote Code

Any script loaded from a URL fails review and violates the store
policy.

### 12.3 Persistent Service Worker State

Module-level variables are lost when the service worker terminates.

### 12.4 `setInterval` in the Service Worker

Does not survive termination. Use `chrome.alarms`.

### 12.5 Listener Registered Inside an Async Function

The listener misses events that occur before it registers. Register
listeners synchronously at the top level.

### 12.6 DOM Pollution

Global styles or un-namespaced elements conflict with the host page.
Scope everything.

### 12.7 `MutationObserver` on the Whole Document

Fires on every DOM change. Filter to the subtree that matters.

### 12.8 Unhandled Messages

A message handler that does not switch on `type` and does not
return `false` leaves the response channel open. The caller times
out.

### 12.9 Sync `storage.sync` for Secrets

Tokens in `storage.sync` are synchronized to the user's account.
Use `storage.local` with encryption.

### 12.10 `innerHTML` From User Input

BAD: `popup.innerHTML = userProvidedText`.

GOOD: `popup.textContent = userProvidedText`.

The extension's origin has elevated privileges. XSS here is worse
than on a normal page.

### 12.11 No CSP

A manifest without a CSP (in Manifest V2) or with an `unsafe-eval`
CSP is rejected.

### 12.12 Injecting Into Every Page

A content script that runs on `<all_urls>` for a feature that only
matters on three sites wastes resources and increases the attack
surface.

### 12.13 Unhandled Errors in Content Scripts

An error in a content script may break the page. Wrap in
try/catch and report to the service worker.

### 12.14 No Update Migration

A schema change without migration breaks existing users' data.

### 12.15 Synchronous Storage Reads in Hot Paths

`chrome.storage.local.get` is async. Calling it on every keystroke
in a content script is slow. Cache in memory.

### 12.16 Message Protocol Without Version

The message format changes between extension versions. Content
scripts injected by an old version miscommunicate with a new
service worker during an update.

### 12.17 Blocking the Main Thread on the Page

A content script that runs a heavy loop blocks the page's rendering.
Yield or offload to the service worker.

### 12.18 No Uninstall Cleanup

State stored in `storage.local` remains after uninstall in some
browsers. Provide a cleanup path via `runtime.setUninstallURL`.

### 12.19 Badge Updates on Every Event

A badge update on every message causes flicker and CPU churn.
Debounce.

### 12.20 No Error Reporting

A silent failure in the service worker means a broken extension
with no diagnostic. Log to `storage.local` or a remote service with
consent.

### 12.21 Trusting `sender.url` Blindly

A content script can claim any URL. Validate `sender.origin` against
the extension's allowlist.

### 12.22 `tabs` Permission for `activeTab` Use Case

BAD: Requesting `tabs` when the extension only needs the active
tab.

GOOD: `activeTab` with a user gesture.

### 12.23 `webRequest` in Manifest V3

`webRequest` blocking is replaced by `declarativeNetRequest`. Using
the old API is rejected.

### 12.24 Inline Scripts in Extension Pages

Inline `<script>` blocks are rejected by the CSP. Use external
script files.

### 12.25 localStorage in Extension Pages

`localStorage` in an extension page is not synchronized with
`chrome.storage` and is not accessible from the service worker.
Use `chrome.storage` consistently.

### 12.26 `window.open` Without Validation

BAD: `window.open(userProvidedUrl)`.

GOOD: Validate against an allowlist of domains.

### 12.27 Mixed Content in Extension Pages

An extension page that loads `http://` resources is blocked by
default. Use `https://` or bundle the resource.

### 12.28 No `incognito` Strategy

An extension that behaves differently in incognito without
documentation confuses users. Declare `incognito` mode in the
manifest and document the behavior.

### 12.29 File Downloads Without a Reason

`chrome.downloads` requires a permission and is a review trigger.
Use it only when the extension genuinely downloads files, not as a
convenience.

### 12.30 No Content Script Cleanup

A content script that adds listeners or observers without removing
them leaks memory. Remove listeners on `unload`.

## 13. Response to Violation

If a previous response violated a rule here:

```
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

No justification. No apology paragraph. Fix and move on.
