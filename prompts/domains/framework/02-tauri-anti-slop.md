---
id: 02-tauri-anti-slop
title: "Tauri Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-backend-anti-slop, 02-desktop-anti-slop]
category: domain
domain_type: framework
version: 1
---

# Tauri Anti-Slop Layer

Layered under the master, architecture, backend, and desktop delivery layers.
This file covers commands, permissions, and the frontend-to-Rust boundary in
Tauri applications.

## 1. Stack Assumptions

1. Use the Tauri version and Rust toolchain declared by the project.
2. Confirm whether the frontend uses TypeScript, JavaScript, or another binding.
3. Read the existing capability and permission configuration first.
4. Keep Rust domain code independent from frontend framework types.
5. Use the existing command and state organization.
6. Confirm target operating systems and packaging configuration.
7. Do not add a command wrapper when the existing binding is sufficient.
8. Treat generated bindings as build artifacts, not as source contracts.
9. Test the packaged desktop behavior for filesystem and process operations.
10. Keep configuration values in the project's existing config system.

## 2. Project Structure

11. Keep frontend screens and components outside the Rust crate.
12. Keep commands in an explicit application or interface module.
13. Keep domain rules independent of Tauri command types.
14. Keep infrastructure adapters separate from command handlers.
15. Keep permissions and capabilities in the existing Tauri configuration.
16. Follow the existing feature or layer structure.
17. Do not create a frontend utility that duplicates a Rust service.
18. Keep shared state ownership explicit and scoped.
19. Do not expose a command module as a public frontend API wholesale.
20. Use the crate's existing public module boundary.

## 3. Command Discipline

21. A command is a narrow use-case boundary, not a generic RPC endpoint.
22. Use explicit command names and typed arguments.
23. Return a serializable, stable result type.
24. Validate all arguments before filesystem, process, or network work.
25. Keep command handlers short and delegate business logic.
26. Use `Result` for expected operational failures.
27. Keep internal error details out of user-facing command results.
28. Do not accept a shell string where structured arguments are sufficient.
29. Never execute an arbitrary command supplied by the frontend.
30. Make long-running commands cancellable and bounded.
31. Include context in errors and logs without sensitive payloads.
32. Test each command with valid, invalid, denied, and cancelled inputs.
33. Keep command return types free of database or framework internals.
34. Do not duplicate command logic in frontend wrappers.
35. Document command authorization assumptions at the handler boundary.

## 4. Permissions Model

36. Grant the minimum capability required by each window or feature.
37. Keep permissions in the project configuration, not in frontend code.
38. Do not add a broad permission to avoid a focused policy decision.
39. Review every new filesystem, shell, network, or asset permission.
40. Keep user data and application data in separate scopes.
41. Use path validation and canonical containment checks where applicable.
42. Treat a denied permission as an expected product state.
43. Show an actionable message without retrying indefinitely.
44. Never bypass Tauri permissions by invoking an internal command directly.
45. Keep production and development capabilities distinct.
46. Verify packaged application behavior under the release policy.
47. Remove permissions for removed features.
48. Keep permission changes synchronized with user-facing explanations.

## 5. Shared State and Events

49. Keep mutable shared state behind an explicit owner.
50. Do not put request-specific values in global Tauri state.
51. Use locks or concurrency primitives according to the state type.
52. Keep state cloning and serialization intentional.
53. Emit events only for data that multiple consumers need.
54. Give events stable names and versioned payloads.
55. Remove event listeners on the frontend owner that created them.
56. Do not use events as an unbounded command result channel.
57. Keep state changes observable through structured logs or metrics.
58. Avoid deadlocks by keeping lock scopes short.
59. Make shutdown safe when commands are still completing.
60. Report partial state changes through the application's error contract.

## 6. Domain-Specific Anti-Patterns

### 6.1 Command as arbitrary shell

BAD:
```rust
#[tauri::command]
fn run(command: String) {
    std::process::Command::new("sh").arg("-c").arg(command).spawn().unwrap();
}
```

GOOD:
```rust
#[tauri::command]
fn open_document(path: String) -> Result<Document, AppError> {
    document_service.open(validated_path(path))
}
```

### 6.2 Capability inflation

BAD:
```json
{"permissions": ["fs:all", "shell:all", "http:all"]}
```

GOOD:
```json
{"permissions": ["fs:read-app-data", "shell:open"]}
```

### 6.3 Global mutable state

BAD:
```rust
static CURRENT_USER: Mutex<Option<User>> = Mutex::new(None);
```

GOOD:
```rust
fn save_user(state: State<AppState>, user: User) -> Result<(), AppError> {
    state.repository.save(&user)
}
```

### 6.4 Event as firehose

BAD:
```rust
window.emit("progress", snapshot)?;
```

GOOD:
```rust
window.emit("operation:completed", CompletionPayload::new(id))?;
```

## 7. Response to Violation

61. Identify whether the defect is a command, permission, state, or frontend
    contract problem before changing code.
62. Fetch the relevant command, capability, state, and caller files.
63. Narrow the command surface and move logic to its owning layer.
64. Add argument validation and stable error results.
65. Verify the permission scope in development and packaged builds.
66. Test concurrent state access and shutdown behavior where relevant.
67. Report a denied capability as a product decision, not a crash.
68. State changed files, unchanged files, and untested platform paths.
69. Do not weaken permissions or bypass the invoke boundary.
70. Run lint, typecheck, Rust checks, and relevant tests.
71. Record commands and results without claiming unexecuted verification.
72. Leave no incomplete command or unspecified permission behavior.

73. Keep a command inventory with its required capability.
74. Reject unknown frontend origins for privileged operations.
75. Test denied, restricted, and unavailable capability states.
76. Make shutdown wait for owned resources and active commands.
77. Keep event payloads free of account secrets and raw records.
78. Test concurrent state access without holding locks across awaits.
79. Report cancellation separately from command failure.
80. Keep filesystem paths canonical and workspace-scoped where possible.
81. Do not infer permission from a frontend feature flag.
82. Keep production and development configuration distinct.
83. Verify generated bindings match the Rust command signatures.
84. Test packaging on each supported desktop target.
85. Keep update and migration behavior outside feature handlers.
86. Remove commands and capabilities when their feature is removed.
87. Log command failure with request context and safe identifiers.
88. Do not expose database records directly through command results.
89. Review every new event consumer and unsubscribe path.
90. Report unsupported platform behavior as a compatibility limitation.