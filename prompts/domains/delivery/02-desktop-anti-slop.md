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

Layered under `_universal/00-master-anti-slop.md`. Universal rules are not
repeated. Framework-specific Electron or Tauri rules remain separate.

## 1. Stack Assumptions

**1.1 Confirm the desktop matrix.** Identify supported operating systems,
architectures, update channels, signing requirements, and packaging mode.

**1.2 Separate trust zones.** Main process, preload, renderer, native modules,
and local files have different privileges and data exposure.

**1.3 Use the existing shell.** Reuse the repository's window, menu, tray,
notification, protocol, and update abstractions.

## 2. Domain Contracts

**2.1 Main owns privileged operations.** Renderer requests capability through
a narrow, validated IPC contract; it does not access Node or OS secrets by
default.

**2.2 Renderer data is untrusted.** Validate IPC input, navigation targets,
deep links, file paths, and external content.

**2.3 Updates are staged and reversible.** Verify signatures and metadata,
use the platform updater, and retain a recovery path.

**2.4 Local persistence is explicit.** Classify data, protect it with the
platform store, and handle migration and deletion.

## 3. Domain-Specific Rules

**3.1 Minimize preload API.** Expose named operations with serializable,
versioned messages; do not bridge the entire process object.

**3.2 Validate every IPC request.** Check sender, channel, schema, size,
authorization, and operation-specific resource bounds.

**3.3 Disable unnecessary navigation.** Block unexpected navigation, new
windows, and external protocol launches unless explicitly allowlisted.

**3.4 Apply CSP.** Keep renderer content security policy strict; do not use
remote code or unsafe evaluation to make a feature work.

**3.5 Design menus declaratively.** Match platform accelerator and shortcut
behavior; keep actions idempotent and route them through the same owner.

**3.6 Handle lifecycle events.** Save durable state before close, release
resources on suspend, and resume from explicit persisted state.

**3.7 Make updates atomic.** Do not replace a running binary while it can
corrupt state; stage, verify, and restart at a defined point.

**3.8 Recover from crashes.** Keep a last-known-good state and avoid writing
partial application data during shutdown.

**3.9 Test packaged application.** Development mode does not prove signing,
paths, auto-update, menus, permissions, or OS integration.

**3.22 Version the IPC contract.** Include a protocol version and reject incompatible messages before invoking a handler.

**3.23 Bound local files.** Validate path, owner, extension, size, and destination before opening or writing a user-selected file.

**3.24 Constrain navigation.** External links, deep links, new windows, and protocol launches follow explicit allowlists and authentication checks.

**3.25 Preserve update trust.** Verify the exact signed artifact, stage it atomically, and keep the previous version recoverable.

**3.26 Test package lifecycle.** Verify first launch, supported upgrade, interrupted installation, crash restart, signing, and platform menus.

**3.30 Isolate privileged work.** Main owns native operations and renderer receives only validated IPC operations.

**3.31 Protect navigation and files.** Allowlists, path checks, CSP, and update verification are enforced at their boundaries.

**3.32 Test package recovery.** Verify clean install, upgrade, interrupted update, crash restart, signing, and platform integration.

**3.33 Keep package evidence safe.** Record signed artifact, update result, crash state, and recovery target without secrets.

## 4. Domain-Specific Anti-Patterns

### 4.1 Full Node Bridge to Renderer

BAD:
```typescript
contextBridge.exposeInMainWorld("desktop", { ipcRenderer });
```

GOOD:
```typescript
contextBridge.exposeInMainWorld("desktop", {
  openDocument: (id: string) => ipcRenderer.invoke("open-document", id)
});
```

The renderer receives a narrow contract, not arbitrary IPC.

### 4.2 Unvalidated External Navigation

BAD:
```typescript
win.webContents.on("will-navigate", () => {});
```

GOOD:
```typescript
win.webContents.on("will-navigate", (event, url) => {
  if (!allowedNavigation(url)) event.preventDefault();
});
```

External destinations do not silently become application pages.

### 4.3 Update Overwrite Without Verification

BAD:
```typescript
fs.copyFileSync(downloadPath, appBinaryPath);
```

GOOD:
```typescript
verifySignatureAndDigest(downloadPath);
installWithPlatformUpdater(downloadPath);
```

The application installs only a verified staged artifact.

**3.10 Version IPC contracts.** Include a protocol version and reject incompatible messages with a safe error rather than guessing fields.

**3.11 Bound file operations.** Validate paths, ownership, size, and extension before opening user-selected files or writing downloads.

**3.12 Handle single-instance behavior.** Define what a second launch does, which window is focused, and how its arguments are validated.

**3.13 Protect window state.** Persist only user-approved preferences and recover from corrupt state without blocking startup.

**3.14 Observe lifecycle failures.** Log safe context for renderer crash, update failure, and protocol disconnect while preserving user data.

**3.15 Test platform integration.** Verify keyboard shortcuts, tray or menu visibility, signing, installation paths, and update restart on supported systems.

**3.16 Keep renderer updates serializable.** IPC payloads use stable schemas and do not send native handles, functions, or unbounded buffers.

**3.17 Separate user data paths.** Use the OS-approved application data location and do not assume the executable directory is writable.

**3.18 Handle display and locale changes.** Recompute layout, shortcuts, and menus without losing unsaved state.

**3.19 Constrain deep links.** Validate scheme, host, route, parameters, and authentication before dispatching an external launch.

**3.20 Review code signing inputs.** Sign only the exact packaged artifact and preserve the updater's trust relationship.

**3.21 Test crash recovery.** Verify restart after renderer failure, interrupted save, blocked update, and unavailable network.

**3.22 Make protocol errors actionable.** Return a stable error category and retry policy without exposing native paths or credentials.

**3.23 Keep updates observable.** Expose update availability, verification failure, installation result, and restart state to the product owner.

**3.24 Test clean and upgrade installs.** Verify first launch, upgrade from the supported prior version, and recovery from an interrupted installation.

## 5. Response to Violation

If a prior response violated this layer, name the IPC, renderer, update,
menu, lifecycle, or packaging risk and show the corrected boundary. Do not
claim a signed installer or update was verified without evidence.
