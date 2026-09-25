---
id: 02-desktop-anti-slop
title: "Desktop App Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: delivery
version: 1
---

# Desktop App Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
security anti-patterns, output format) are NOT repeated here.

This file covers rules specific to desktop applications: Electron,
Tauri, and native toolkits (Qt, GTK, WinUI, SwiftUI/AppKit). Framework-
specific rules for Electron and Tauri live in
`domains/framework/`. This file covers the platform-agnostic
discipline.

## 1. Stack Assumptions

This layer applies to:

- Electron (Chromium + Node.js)
- Tauri (Rust + system webview)
- Qt (C++ / Python)
- GTK (C / Python / Rust)
- WinUI / WPF (.NET)
- AppKit / SwiftUI (macOS)
- Cross-platform (Flutter desktop, .NET MAUI)

## 2. Process Architecture

### 2.1 Separation of Concerns

Desktop apps separate:

- **UI process** (renderer, webview): displays content, handles user
  input.
- **Main process** (or native core): file system, OS integration,
  networking, privileged operations.

The UI process has no direct access to the OS. It requests via IPC.

### 2.2 Never Trust the UI Process

The UI process may be compromised by a cross-site scripting bug in a
loaded page. The main process validates every IPC request.

### 2.3 Minimal IPC Surface

Every IPC channel exposes the smallest possible functionality:

- No `runCommand(cmd)` with arbitrary strings.
- No `readFile(path)` without a path allowlist.
- No `openUrl(url)` without a scheme and host allowlist.

## 3. Security

### 3.1 Context Isolation

Electron: `contextIsolation: true` is the default in modern versions.
Never disable it.

### 3.2 Node Integration Off in Renderer

Electron: `nodeIntegration: false`. The renderer does not have access
to Node.js APIs directly.

### 3.3 Preload Script With `contextBridge`

Expose a minimal API via `contextBridge.exposeInMainWorld`:

```javascript
contextBridge.exposeInMainWorld("api", {
  saveFile: (content) => ipcRenderer.invoke("save-file", content),
});
```

Never expose `ipcRenderer` directly.

### 3.4 No `remote` Module

Electron's `remote` module allows the renderer to call main-process
modules directly. It is deprecated and dangerous. Do not use it.

### 3.5 Content Security Policy

A strict CSP in every HTML file. No `unsafe-eval`. No remote scripts.

### 3.6 Navigation and `window.open` Restrictions

Block navigation to untrusted origins:

```javascript
webContents.on("will-navigate", (event, url) => {
  if (!isAllowed(url)) event.preventDefault();
});

webContents.setWindowOpenHandler(({ url }) => {
  shell.openExternal(url);
  return { action: "deny" };
});
```

### 3.7 Updates Are Signed

Auto-updates are signed by the publisher. The app verifies the
signature before applying.

## 4. File System

### 4.1 Path Validation

Every path from the UI is validated:

- Normalize the path.
- Resolve to an absolute path.
- Check it is inside an allowed directory.

BAD: `fs.readFile(userProvidedPath)` in the main process.
GOOD: Validate the path against a sandbox root.

### 4.2 No Arbitrary Write Locations

The app writes to:

- User data directory (OS-specific).
- Temporary directory.
- Locations the user explicitly chooses via a file dialog.

Never write to the installation directory.

### 4.3 Symlink Handling

Symlinks can escape a sandbox. Resolve them and re-check.

### 4.4 Large Files

Reading a 2 GB file into memory crashes the app. Stream.

## 5. Native Integration

### 5.1 Menus

- macOS: app menu, Edit menu, Window menu.
- Windows/Linux: File, Edit, View, Help.

Match the platform's conventions. Do not invent menus.

### 5.2 Keyboard Shortcuts

- Copy, Cut, Paste, Undo, Redo: platform defaults.
- Cmd on macOS, Ctrl elsewhere.
- Never override OS shortcuts (Cmd+Tab, Alt+Tab).

### 5.3 File Associations

If the app opens files of a specific type, it registers as a handler
and handles the "open with" event. The path comes from the OS, not
from user input.

### 5.4 System Tray

Use sparingly. A tray icon that adds no value is noise.

### 5.5 Notifications

Use the OS notification system, not a custom popup. Respect the
user's Do Not Disturb settings.

## 6. State and Persistence

### 6.1 User Data Directory

Persist to the OS-specific user data directory:

- macOS: `~/Library/Application Support/<AppName>`
- Windows: `%APPDATA%/<AppName>`
- Linux: `~/.config/<AppName>` or `~/.local/share/<AppName>`

Never to the app's installation directory.

### 6.2 Schema Migration

Data persisted by v1 must be readable by v2. Provide migrations.

### 6.3 Encrypted Storage for Secrets

OS keychains:

- macOS: Keychain
- Windows: Credential Manager
- Linux: libsecret / gnome-keyring

Never store tokens in plain JSON in the user data directory.

## 7. Updates

### 7.1 Auto-Update

Use the platform's mechanism (Squirrel on macOS/Windows, AppImage
update, MSIX). The user is notified and can defer.

### 7.2 Never Update Without Consent

Forced updates are hostile. Offer a "remind me later" path.

### 7.3 Rollback

A bad update must be revertible. Keep the previous version.

### 7.4 Channel Support

Beta and stable channels. Beta users accept instability.

## 8. Performance

### 8.1 Cold Start Time

Under 3 seconds for a simple app. Under 5 for a complex one. Profile
startup.

### 8.2 Bundle Size

Electron apps bundle Chromium (100+ MB). Tauri uses the system
webview (much smaller). Weigh the trade-off.

### 8.3 Memory

Desktop users notice memory growth. Monitor and cap.

### 8.4 Background Work

Offload heavy tasks to worker threads or the main process, not the
UI thread.

## 9. Desktop-Specific Anti-Patterns

### 9.1 `nodeIntegration: true` in Renderer

Covered in 3.2. A single XSS in the app is RCE.

### 9.2 `contextIsolation: false`

Covered in 3.1.

### 9.3 Arbitrary IPC

Covered in 2.3.

### 9.4 Remote Content Loaded in the App

Loading `https://example.com` inside the app gives that page full
access to the preload API. Only load content the app controls.

### 9.5 No CSP

Covered in 3.5.

### 9.6 Storing Secrets in JSON

Covered in 6.3.

### 9.7 No Update Signature

Covered in 3.7. A compromised update server owns every user's machine.

### 9.8 Platform-Specific Code Without Guards

BAD: `if (process.platform === "darwin")` scattered everywhere.
GOOD: An abstraction with platform-specific implementations.

### 9.9 Custom Titlebar Without Platform Support

A custom titlebar that works on macOS and breaks on Windows. Test on
each platform.

### 9.10 Missing Menus on macOS

A macOS app with no app menu cannot be quit normally. Provide the
standard menus.

### 9.11 No Keyboard Shortcuts

Users expect Cmd+C to copy. Without it, the app feels broken.

### 9.12 Badge Count Without a Notification Center

A badge without a corresponding OS notification is confusing.

### 9.13 Blocking the Main Process

A synchronous operation in the main process freezes every window.

### 9.14 App Doesn't Quit

Closing all windows does not quit on macOS (expected) but does on
Windows/Linux. Handle both.

### 9.15 No Single Instance Lock

Multiple instances of the app compete for files and locks. Use the
platform's single-instance mechanism.

### 9.16 Auto-Update Without Release Notes

The user sees an update with no information. Provide a changelog.

### 9.17 Silent Crash

A crash without a log or a crash reporter. Users see a closed window
and no explanation.

### 9.18 Native Dialogs for Everything

Every save, every confirm is a native dialog. Too many dialogs fatigue
the user.

### 9.19 Cross-Platform Assumptions

A path like `C:\Users\...` hardcoded. Use the platform's path APIs.

### 9.20 No Code Signing

An unsigned app triggers SmartScreen and Gatekeeper warnings. Sign
for production.

## 10. Response to Violation

If a previous response violated a rule here:

```
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

No justification. No apology paragraph. Fix and move on.
