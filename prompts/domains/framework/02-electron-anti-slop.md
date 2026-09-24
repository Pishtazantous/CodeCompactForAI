---
id: 02-electron-anti-slop
title: "Electron Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-backend-anti-slop, 02-desktop-anti-slop]
category: domain
domain_type: framework
version: 1
---

# Electron Anti-Slop Layer

Layered under the master, architecture, backend, and desktop delivery layers.
This file covers the main and renderer split, IPC, desktop security, windows,
and updates.

## 1. Stack Assumptions

1. Use the Electron version and package manager declared by the project.
2. Confirm the renderer framework and build output before changing paths.
3. Treat main, preload, renderer, and native dependencies as separate layers.
4. Use the existing configuration and packaging tool.
5. Confirm target operating systems and minimum versions.
6. Keep production and development browser settings distinct.
7. Read the existing preload and window creation code first.
8. Do not add a new IPC library when Electron IPC is sufficient.
9. Treat update behavior as a product contract, not an ad hoc download.
10. Verify behavior in a packaged build when desktop behavior matters.

## 2. Project Structure

11. Keep main-process entry code small and free of UI layout concerns.
12. Keep window and lifecycle orchestration in a dedicated main module.
13. Keep preload code limited to a narrow, typed capability bridge.
14. Keep renderer code unaware of Node and main-process module paths.
15. Put storage and backend adapters behind application services.
16. Keep update and packaging configuration separate from feature code.
17. Follow the existing feature or layer organization.
18. Do not import renderer modules into main or preload.
19. Do not import Node-only modules into a renderer bundle.
20. Keep shared values serializable across the process boundary.

## 3. Main and Renderer Split

21. Create windows through one reviewed window factory.
22. Configure preload, context isolation, sandbox, and node integration deliberately.
23. Treat renderer input as untrusted even when it comes from local files.
24. Keep navigation and new-window policy in main.
25. Restrict navigation to an explicit allowlist.
26. Reject unexpected protocols and external file targets.
27. Keep privileged filesystem and process work out of the renderer.
28. Do not use `remote` in new code.
29. Keep renderer state separate from main-owned application state.
30. Make window close and re-open behavior idempotent.

## 4. IPC Discipline

31. Expose only named operations through preload.
32. Use a typed request and response contract for every channel.
33. Validate arguments in main before using them.
34. Return structured success and error results.
35. Keep channel names centralized and stable across releases.
36. Do not expose a generic `invoke(command, args)` bridge.
37. Keep event subscriptions owned and removable by the caller.
38. Include an operation identifier for cancellable or long-running work.
39. Do not send secrets or unrestricted filesystem objects to the renderer.
40. Handle sender validation when multiple windows can invoke a channel.
41. Keep IPC handlers free of business rules and database details.
42. Use the application service layer for persistence and external calls.
43. Add timeout and cancellation behavior for external operations.
44. Log IPC failures without logging sensitive payloads.

## 5. Security and Updates

45. Disable or constrain remote content in the main process.
46. Use safe navigation and permission request handlers.
47. Never disable context isolation to make a preload bridge work.
48. Never enable node integration for a renderer that displays untrusted data.
49. Do not use shell execution for application commands.
50. Validate URLs before opening them externally.
51. Keep update manifests and release channels project-controlled.
52. Verify update signatures and minimum supported versions.
53. Make update failure recoverable without blocking the current app.
54. Do not auto-install an update while unsaved work would be lost.
55. Keep release artifacts free of development endpoints and debug flags.
56. Test update and relaunch behavior with representative data.

## 6. Domain-Specific Anti-Patterns

### 6.1 Renderer gets Node access

BAD:
```javascript
new BrowserWindow({ webPreferences: { nodeIntegration: true } });
```

GOOD:
```javascript
new BrowserWindow({
  webPreferences: { preload, contextIsolation: true, sandbox: true },
});
```

### 6.2 Generic IPC dispatcher

BAD:
```javascript
contextBridge.exposeInMainWorld("api", {
  invoke: (channel, payload) => ipcRenderer.invoke(channel, payload),
});
```

GOOD:
```javascript
contextBridge.exposeInMainWorld("api", {
  saveDocument: (request) => ipcRenderer.invoke("document:save", request),
});
```

### 6.3 Unsafe window navigation

BAD:
```javascript
win.webContents.on("will-navigate", (_event, url) => {});
```

GOOD:
```javascript
win.webContents.on("will-navigate", (event, url) => {
  if (!allowedOrigins.has(new URL(url).origin)) event.preventDefault();
});
```

### 6.4 Update without recovery

BAD:
```javascript
await downloadUpdate();
app.quit();
app.relaunch();
```

GOOD:
```javascript
const update = await verifyAndStageUpdate();
await applyUpdateWithRecovery(update);
```

## 7. Response to Violation

57. Stop and identify whether the problem is main, preload, or renderer.
58. Fetch the current window factory, preload bridge, and service boundary.
59. Move the operation to the smallest privileged boundary.
60. Remove unnecessary Node access and generic command dispatch.
61. Add validation for arguments, navigation, and external targets.
62. Test renderer failure, denied permission, and update failure paths.
63. Verify packaging settings in a release artifact.
64. Report platform-specific behavior that cannot be tested locally.
65. State changed files, unchanged files, and remaining risks.
66. Do not silently weaken a security control for a build issue.
67. Do not claim signed update behavior without inspecting the configuration.
68. Keep the diff limited to the requested desktop capability.
69. Run the repository's lint, typecheck, and relevant tests.
70. Leave no incomplete code or unspecified integration points.
71. Record the exact commands that were run and their result.
73. Keep a small inventory of privileged windows and their origins.
74. Reject unexpected origins before dispatching IPC.
75. Test menu, shortcut, and protocol handlers with hostile input.
76. Keep deep links and file-open events outside renderer components.
77. Validate file-open paths against the configured workspace policy.
78. Make application state restore explicit after a crash or forced quit.
79. Test window recreation without duplicate listeners or jobs.
80. Keep long-running work observable through progress and cancellation.
81. Do not hold a renderer reference in main-process global state.
82. Release resources when a window is closed or replaced.
83. Keep package metadata and runtime permissions in sync.
84. Test both installed and portable artifacts when supported.
85. Report platform signing or packaging failures as blockers.
86. Do not disable sandboxing to work around a preload mistake.
87. Keep debug tooling absent from production entry points.
88. Use a single source for remote endpoint and update policy.
89. Review every new channel against least privilege.
90. Preserve user data across update and downgrade boundaries.