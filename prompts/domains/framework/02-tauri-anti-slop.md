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
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "main-capability",
  "description": "Read application data files for the main window",
  "windows": ["main"],
  "permissions": [
    "core:default",
    {
      "identifier": "fs:allow-read-text-file",
      "allow": [{ "path": "$APPDATA/data/**" }]
    }
  ]
}
```
This capability grants one concrete filesystem permission to one window and
scopes it to the application's data directory. Do not add a shell permission
unless a reviewed command needs a narrowly scoped operation.

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

- Correction — `Command boundary / open_document`: replace arbitrary shell execution with structured arguments, validation, and delegation to the existing service.
- Verify — `Command boundary / open_document`: run `cargo test <command-test>`; expected result is PASS for valid, invalid, denied, and cancelled inputs.
- Correction — `Permission scope / capability configuration`: grant only the filesystem or shell capability required by this command and preserve the invoke boundary.
- Verify — `Permission scope / capability configuration`: inspect the packaged artifact; expected result is the focused permission set with no wildcard capability.
- Correction — `Shared state / AppState`: keep the repository behind the explicit state owner and keep locks short rather than across awaits.
- Verify — `Shared state / AppState`: run `cargo clippy --all-targets -- -D warnings`; expected result is no lock, serialization, or async diagnostics.
- Scope — limit the patch to the cited rule, file, or symbol; record changed and unchanged paths and any untested target OS or packaged build.
