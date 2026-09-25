---
id: 02-desktop-anti-slop
title: "Desktop App Anti-Slop Layer"
lang: en
depends_on: ["_universal/00-style-guide.md", "_universal/00-master-anti-slop.md"]
category: domain
domain_type: delivery
version: 2
---

# Desktop App Anti-Slop Layer

This file defines behavioral contracts specific to desktop applications. It sits in the delivery layer, below the universal anti-slop rules and above framework-specific patterns. It covers process architecture, security, file system access, native integration, state persistence, updates, and performance for Electron, Tauri, and native toolkits (Qt, GTK, WinUI, SwiftUI/AppKit). Framework-specific rules for Electron and Tauri live in `domains/framework/`. This file covers the platform-agnostic discipline. It does not cover general frontend rules (see `02-frontend-anti-slop.md`) or mobile-specific rules (see `02-mobile-anti-slop.md`).

A desktop app runs with elevated OS privileges and direct file system access. A security flaw is not just a data leak; it is remote code execution on the user's machine.

## Scope

This file applies to Electron (Chromium + Node.js), Tauri (Rust + system webview), Qt (C++ / Python), GTK (C / Python / Rust), WinUI / WPF (.NET), AppKit / SwiftUI (macOS), and cross-platform frameworks (Flutter desktop, .NET MAUI). The principles are framework-agnostic. The examples use JavaScript/Electron syntax where illustrative.

## Rule Severity

Severity follows `_universal/00-style-guide.md`.

## Contracts

A desktop application commits to six contracts. The table below maps each contract to the rules that enforce it.

| Contract | Description | Enforced By |
|---|---|---|
| Process Isolation | UI and Main processes are strictly separated; IPC is minimal and validated. | DSK-001 to DSK-003 |
| Security Baseline | Context isolation, CSP, and signed updates prevent RCE and compromise. | DSK-004 to DSK-010, DSK-031, DSK-043 |
| File System Safety | Paths are validated, sandboxed, symlink-safe, and streamed. | DSK-011 to DSK-014, DSK-042 |
| Native Convention | Menus, shortcuts, dialogs, and notifications follow OS guidelines. | DSK-015 to DSK-019, DSK-034, DSK-037, DSK-041 |
| State and Persistence | Data is stored in OS-specific directories, migrated safely, and secrets are encrypted. | DSK-020 to DSK-022 |
| Update Discipline | Updates are signed, consensual, rollback-capable, and documented. | DSK-023 to DSK-026, DSK-039 |

## Process Architecture

### DSK-001 — Process Separation

**MUST**

Desktop apps MUST separate the UI process (renderer, webview) from the Main process (native core). The UI process handles user input and displays content. The Main process handles file system, OS integration, networking, and privileged operations. The UI process MUST NOT have direct access to the OS.

### DSK-002 — UI Process Trust Prohibition

**MUST NOT**

The UI process MUST NOT be trusted. It may be compromised by a cross-site scripting bug in a loaded page. The Main process MUST validate every IPC request as if it came from an untrusted remote client.

### DSK-003 — Minimal IPC Surface

**MUST**

Every IPC channel MUST expose the smallest possible functionality. Generic execution channels are prohibited.

Example (illustrative):

- No `runCommand(cmd)` with arbitrary strings.
- No `readFile(path)` without a path allowlist.
- No `openUrl(url)` without a scheme and host allowlist.

## Security

### DSK-004 — Context Isolation

**MUST**

Context isolation (e.g., `contextIsolation: true` in Electron) MUST be enabled. It MUST NEVER be disabled.

### DSK-005 — Node Integration Prohibition

**MUST NOT**

Direct Node.js API access in the renderer process (e.g., `nodeIntegration: true`) MUST NOT be enabled. A single XSS vulnerability with Node integration enabled results in Remote Code Execution (RCE).

### DSK-006 — Preload Script Discipline

**MUST**

A minimal API MUST be exposed via a context bridge (e.g., `contextBridge.exposeInMainWorld`). The raw IPC module (e.g., `ipcRenderer`) MUST NEVER be exposed directly to the renderer.

Example (illustrative, JavaScript):
```javascript
contextBridge.exposeInMainWorld("api", {
  saveFile: (content) => ipcRenderer.invoke("save-file", content),
});
```

### DSK-007 — Remote Module Prohibition

**MUST NOT**

Deprecated and dangerous IPC modules that allow the renderer to call main-process modules directly (e.g., Electron's `remote` module) MUST NOT be used.

### DSK-008 — Strict Content Security Policy

**MUST**

A strict Content Security Policy (CSP) MUST be applied to every HTML file. `unsafe-eval` and remote scripts MUST NOT be allowed.

### DSK-009 — Navigation and Window Open Restrictions

**MUST**

Navigation to untrusted origins MUST be blocked. `window.open` MUST be intercepted and restricted to approved external handlers or denied.

Example (illustrative, JavaScript):
```javascript
webContents.on("will-navigate", (event, url) => {
  if (!isAllowed(url)) event.preventDefault();
});
webContents.setWindowOpenHandler(({ url }) => {
  shell.openExternal(url);
  return { action: "deny" };
});
```

### DSK-010 — Signed Updates

**MUST**

Auto-updates MUST be cryptographically signed by the publisher. The app MUST verify the signature before applying the update.

## File System

### DSK-011 — Path Validation

**MUST**

Every file path received from the UI or external sources MUST be validated: normalized, resolved to an absolute path, and checked to ensure it resides inside an explicitly allowed sandbox directory.

### DSK-012 — Write Location Restriction

**MUST NOT**

The app MUST NOT write to arbitrary locations or the installation directory. Writes MUST be restricted to the OS-specific user data directory, the temporary directory, or locations explicitly chosen by the user via a native file dialog.

### DSK-013 — Symlink Resolution and Validation

**MUST**

Symlinks can escape a sandbox. Every path MUST have symlinks resolved before the sandbox boundary check is applied.

### DSK-014 — Large File Streaming

**MUST NOT**

Large files (e.g., > 100 MB) MUST NOT be read entirely into memory. They MUST be processed via streams to prevent application crashes.

## Native Integration

### DSK-015 — Platform Menu Conventions

**MUST**

Menus MUST match the platform's conventions (e.g., App/Edit/Window menus on macOS; File/Edit/View/Help on Windows/Linux). Inventing custom menu paradigms is prohibited.

### DSK-016 — Standard Keyboard Shortcuts

**MUST**

Standard OS keyboard shortcuts (Copy, Cut, Paste, Undo, Redo) MUST be respected using the platform's modifier key (Cmd on macOS, Ctrl elsewhere). OS-level shortcuts (Cmd+Tab, Alt+Tab) MUST NOT be overridden.

### DSK-017 — File Association Handling

**MUST**

If the app registers as a handler for specific file types, it MUST handle the OS "open with" event correctly. The file path MUST be received from the OS event, not parsed from user input.

### DSK-018 — System Tray Discipline

**SHOULD NOT**

System tray icons SHOULD NOT be used unless they provide persistent, actionable value. A tray icon that adds no value is noise.

### DSK-019 — Native Notification Usage

**MUST**

The OS notification system MUST be used instead of custom in-app popups. The user's Do Not Disturb settings MUST be respected.

## State and Persistence

### DSK-020 — OS-Specific User Data Directory

**MUST**

Persistent application data MUST be stored in the OS-specific user data directory (e.g., `~/Library/Application Support/<AppName>` on macOS, `%APPDATA%/<AppName>` on Windows, `~/.config/<AppName>` on Linux). Data MUST NOT be stored in the app's installation directory.

### DSK-021 — Schema Migration

**MUST**

Data persisted by previous versions of the app MUST be readable by the current version. Explicit migration logic MUST be provided for schema changes.

### DSK-022 — Encrypted Secret Storage

**MUST NOT**

Tokens, passwords, and secrets MUST NOT be stored in plain text files (e.g., JSON) in the user data directory. The OS-native keychain (macOS Keychain, Windows Credential Manager, Linux libsecret/gnome-keyring) MUST be used.

## Updates

### DSK-023 — Platform Auto-Update Mechanism

**MUST**

The platform's or framework's standard auto-update mechanism (e.g., Squirrel, AppImage update, MSIX) MUST be used. The user MUST be notified and allowed to defer the update.

### DSK-024 — Update Consent

**MUST NOT**

Forced, silent updates are hostile. A "remind me later" or deferral path MUST be provided.

### DSK-025 — Update Rollback Capability

**MUST**

A failed or buggy update MUST be revertible. The previous version MUST be retained or recoverable until the new version is verified stable.

### DSK-026 — Update Channel Support

**SHOULD**

Beta and stable channels SHOULD be supported to allow users to opt into instability for early access.

## Performance

### DSK-027 — Cold Start Budget

**SHOULD**

Cold start time SHOULD be under 3 seconds for a simple app and under 5 seconds for a complex one. Startup MUST be profiled and optimized.

### DSK-028 — Bundle Size Awareness

**MUST**

The trade-off between framework bundle size (e.g., Electron bundling Chromium vs. Tauri using the system webview) MUST be evaluated against the application's requirements.

### DSK-029 — Memory Growth Monitoring

**MUST**

Memory usage MUST be monitored and capped. Desktop users are highly sensitive to continuous memory growth (leaks).

### DSK-030 — Background Work Offloading

**MUST NOT**

Heavy computational tasks MUST NOT run on the UI thread or the Main process's event loop. They MUST be offloaded to worker threads or background processes to prevent UI freezing.

## AI-Specific Desktop Discipline

### DSK-060 — Desktop Framework API Verification

**MUST**

Before using a desktop framework API (e.g., Electron `BrowserWindow` options, Tauri `invoke` commands, Qt signals), the assistant MUST verify the API signature and security defaults for the installed version. Invented APIs or deprecated security flags (e.g., `nodeIntegration`) cause silent security degradations or runtime crashes.

See MAS-036 in `_universal/00-master-anti-slop.md`.

### DSK-061 — Existing IPC Channel Discovery

**MUST**

Before creating a new IPC channel or native bridge method, the assistant MUST search the project's Main process code for an existing equivalent. Inventing parallel IPC channels fragments the security boundary and increases the attack surface.

See MAS-035 in `_universal/00-master-anti-slop.md`.

### DSK-062 — Platform Abstraction Restraint

**SHOULD**

The assistant SHOULD NOT introduce complex cross-platform abstraction layers for OS-specific features (e.g., custom menu frameworks, custom window managers) unless the project already uses them and native APIs are proven insufficient.

See MAS-038 in `_universal/00-master-anti-slop.md`.

## Anti-Patterns

### DSK-031 — Remote Content Loading

**MUST NOT**

Loading remote, untrusted web content (e.g., `https://example.com`) directly inside the desktop app's main window is prohibited. It gives that remote origin full access to the preload API. Only content the app controls and bundles MUST be loaded.

### DSK-032 — Platform-Specific Code Guards

**MUST NOT**

Platform-specific code (e.g., `if (process.platform === "darwin")`) MUST NOT be scattered throughout the codebase. It MUST be encapsulated in an abstraction layer with platform-specific implementations.

### DSK-033 — Cross-Platform Custom Titlebars

**MUST**

Custom titlebars MUST be tested and supported on every target platform. A custom titlebar that works on macOS but breaks window management on Windows or Linux is prohibited.

### DSK-034 — Missing macOS App Menu

**MUST NOT**

A macOS application MUST NOT omit the standard App menu. Without it, the user cannot access standard Quit, Hide, or About actions normally.

### DSK-035 — Orphaned Badge Counts

**MUST NOT**

Displaying a badge count on the dock/taskbar without a corresponding OS notification or clear in-app indicator is confusing and MUST NOT be used.

### DSK-036 — Main Process Blocking

**MUST NOT**

Synchronous I/O or heavy computation in the Main process event loop freezes every window and OS integration hook. It is strictly prohibited.

### DSK-037 — Cross-Platform Quit Behavior

**MUST**

The app MUST handle the "close all windows" event according to platform conventions: quitting the app on Windows/Linux, but keeping the app running in the dock on macOS (unless explicitly quit).

### DSK-038 — Single Instance Lock

**MUST**

The platform's single-instance lock mechanism MUST be used. Multiple concurrent instances of the same desktop app competing for file locks and local databases cause data corruption.

### DSK-039 — Update Release Notes

**MUST**

Auto-updates MUST be accompanied by release notes or a changelog. Presenting an update to the user with no information about what changed is hostile.

### DSK-040 — Silent Crash Prohibition

**MUST NOT**

The app MUST NOT crash silently. A crash reporter or a persistent error log MUST be implemented so the user and developer know why the window closed.

### DSK-041 — Native Dialog Fatigue

**SHOULD NOT**

Using native OS dialogs for every minor confirmation or save action fatigues the user. Custom in-app UI SHOULD be used for frequent, low-risk interactions, reserving native dialogs for critical OS-level file or permission requests.

### DSK-042 — Cross-Platform Path Assumptions

**MUST NOT**

Hardcoded path separators or OS-specific path structures (e.g., `C:\Users\...`) MUST NOT be used. The platform's path manipulation APIs (e.g., Node `path.join`, Rust `PathBuf`) MUST be used.

### DSK-043 — Production Code Signing

**MUST**

Production builds MUST be code-signed. Unsigned applications trigger OS-level security warnings (Windows SmartScreen, macOS Gatekeeper) and are often blocked from execution.

## Response to Violation

When a rule in this file is violated, report:

Violation: DSK-{NNN}
Reason: {one-line reason}
Correction: {smallest fix}

For multiple violations, report each rule ID separately.

Do not replace a technical correction with a generic explanation.