---
id: 02-game-anti-slop
title: "Game Anti-Slop Layer"
lang: en
depends_on: ["_universal/00-style-guide.md", "_universal/00-master-anti-slop.md"]
category: domain
domain_type: delivery
version: 2
---

# Game Anti-Slop Layer

This file defines behavioral contracts specific to game development. It sits in the delivery layer, below the universal anti-slop rules and above engine-specific or language-specific patterns. It covers frame budgets, entity systems, asset pipelines, determinism, netcode, and the patterns that produce stutters, desyncs, or unshippable builds. It does not cover language-specific rules (see language files) or engine-specific rules for Unity, Unreal, or Godot (see framework files when present).

A game is a real-time simulation bound by strict hardware limits. A bug is not just a crash; it is a dropped frame, a desync, or an unshippable build.

## Scope

This file applies to native engines (Unreal, custom C++ engines), managed engines (Unity, Godot), web games (Three.js, Babylon.js, WebGL), 2D and 3D games, single-player and multiplayer architectures, and PC, console, mobile, and web targets. The principles are engine-agnostic. The examples use C# and C++ syntax where illustrative.

## Rule Severity

Severity follows `_universal/00-style-guide.md`.

## Contracts

A game system commits to five contracts. The table below maps each contract to the rules that enforce it.

| Contract | Description | Enforced By |
|---|---|---|
| Frame Budget Discipline | Every subsystem operates within a measured time budget to maintain target FPS. | GAME-001 to GAME-004 |
| Architecture & Memory | Entity systems use composition, data-oriented design, and stable IDs to maximize cache coherence. | GAME-005 to GAME-009, GAME-039 |
| Determinism & Loop | Simulation runs on a fixed timestep, interpolates for rendering, and produces identical outputs for identical inputs. | GAME-010 to GAME-018 |
| Network Integrity | The server is authoritative, clients predict and reconcile, and bandwidth is bounded. | GAME-019 to GAME-027, GAME-049 |
| Pipeline & Asset Flow | Assets are built, compressed, streamed, and versioned without blocking the main thread. | GAME-028 to GAME-036, GAME-054, GAME-055 |

## Frame Budget

### GAME-001 — Frame Budget Adherence

**MUST**

Every frame MUST have a strict time budget. 60 FPS requires a 16.67 ms budget; 30 FPS requires 33.33 ms. Exceeding the budget drops a frame and degrades the user experience.

### GAME-002 — Subsystem Budget Measurement

**MUST**

Every subsystem (simulation, rendering, audio, I/O) MUST have a defined and measured time budget. A typical split might be ~50% simulation, ~30% rendering, ~5% audio, and ~15% other, but the exact split MUST be profiled and enforced per project.

### GAME-003 — Profiler-Driven Optimization

**MUST**

Optimization MUST be driven by profiler data, not assumptions. A frame drop is either one slow system or a thousand small costs; the profiler MUST dictate the target.

### GAME-004 — Asynchronous Asset Loading

**MUST NOT**

Synchronous loading of textures, models, or audio clips during gameplay MUST NOT occur, as it causes frame stutters. Assets MUST be loaded asynchronously or during designated loading screens.

## Entity and Component Systems

### GAME-005 — Composition Over Inheritance

**MUST**

Entity architecture MUST prefer composition over deep inheritance hierarchies. A `Player` inheriting from `Character` inheriting from `GameObject` is rigid. Composition (a `Player` entity possessing `Movement`, `Health`, and `Renderer` components) MUST be used for flexibility.

### GAME-006 — Data-Oriented Design

**SHOULD**

For systems processing hundreds or thousands of entities, data-oriented design (structure-of-arrays layout) SHOULD be used instead of array-of-objects to maximize CPU cache coherence in hot paths.

### GAME-007 — Component Data Purity

**MUST**

Components MUST hold data, not behavior. Systems MUST process components. This separation enables caching, networking serialization, and efficient memory layout.

### GAME-008 — Stable Entity IDs

**MUST**

Entity IDs MUST be stable identifiers, not memory pointers. They MUST survive save/load cycles, network transfers, and frame boundaries.

### GAME-009 — Deterministic System Order

**MUST**

The order in which systems run affects the simulation and MUST be defined explicitly. Relying on dictionary iteration order or implicit engine ordering is prohibited.

## Game Loop

### GAME-010 — Fixed Timestep Simulation

**MUST**

Physics and gameplay logic MUST run at a fixed timestep (e.g., 60 Hz, 30 Hz). Variable timesteps for physics destroy reproducibility and cause simulation divergence across different hardware.

### GAME-011 — Render Interpolation

**MUST**

The renderer MUST display an interpolated state between the last two simulation ticks. Without interpolation, the game looks jittery at high refresh rates or when the simulation rate differs from the display rate.

### GAME-012 — Delta Time Clamping

**MUST**

Delta time MUST be clamped to a maximum value (e.g., 100 ms). A long pause (loading, breakpoint, alt-tab) produces a huge delta that causes physics explosions and tunneling if unclamped.

### GAME-013 — Game Loop I/O Prohibition

**MUST NOT**

Disk reads, network calls, and file writes MUST NOT occur on the main game loop thread. I/O MUST be offloaded to worker threads or handled asynchronously.

## Determinism

### GAME-014 — Simulation Determinism

**MUST**

Given the same inputs and the same initial state, the simulation MUST produce the exact same output every time. This is mandatory for lockstep multiplayer and replay systems.

### GAME-015 — Cross-Platform Math Determinism

**MUST**

Standard floating-point math (`sin`, `cos`, `pow`, fused multiply-add) differs between CPUs, compilers, and optimization levels. For lockstep multiplayer, fixed-point math or a strictly deterministic math library MUST be used.

### GAME-016 — Deterministic Iteration Order

**MUST NOT**

Iteration over hash maps, sets, or unordered collections MUST NOT be used in simulation code, as it produces non-deterministic order. Sorted or indexed collections MUST be used.

### GAME-017 — Seeded RNG

**MUST**

The game's Random Number Generator MUST be seeded. Every player in a lockstep session MUST use the same seed to ensure replays and multiplayer simulations are reproducible.

### GAME-018 — Wall Clock Prohibition

**MUST NOT**

Wall clock time (e.g., `System.currentTimeMillis()`, `time.time()`) MUST NOT be used in simulation code. The simulation tick counter MUST be used to preserve determinism.

## Networking

### GAME-019 — Explicit Network Topology

**MUST**

The network topology (Client-Server or Peer-to-Peer) MUST be chosen deliberately. Hybrid approaches (listen servers, host migration) add massive complexity and MUST be explicitly justified.

### GAME-020 — Server Authority

**MUST**

In a client-server model, the server MUST own the truth. Clients predict locally and reconcile. A client MUST NEVER determine the outcome of a competitive action.

### GAME-021 — Client-Side Prediction

**MUST**

The client MUST apply input actions immediately for responsiveness, then reconcile state when the server's authoritative update arrives.

### GAME-022 — Lag Compensation

**SHOULD**

For competitive shooters or action games, the server SHOULD rewind the world to the shooter's view when validating a hit. Without lag compensation, high-latency players will consistently miss.

### GAME-023 — Bandwidth Budgeting

**MUST**

Every network message MUST have a measured size. The bandwidth per player per second MUST be bounded, optimized, and strictly monitored.

### GAME-024 — Snapshot Interpolation

**MUST**

The client MUST buffer server snapshots and interpolate between them to render smooth motion for remote entities.

### GAME-025 — Client Input Validation

**MUST NOT**

Client input MUST NEVER be trusted. The server MUST validate movement speed, fire rate, resource spending, and action cooldowns to prevent cheating.

### GAME-026 — Graceful Disconnection

**MUST**

A disconnected player MUST be handled gracefully. Their entity MUST be frozen, removed, or taken over by AI depending on the game's design, rather than causing a crash or null-reference error.

### GAME-027 — Cheat Prevention Baseline

**MUST**

Competitive games MUST implement server-side validation for every action and MUST NOT trust client-side state for resources, positions, or scores.

## Asset Pipeline

### GAME-028 — Runtime Asset Format

**MUST**

Raw assets (PSD, Maya, WAV) MUST be processed into optimized runtime formats by a build step. The runtime MUST NOT read source formats.

### GAME-029 — Platform-Specific Compression

**MUST**

Assets MUST use platform-specific compression (e.g., BC, ASTC, ETC2 for textures; Vorbis/Opus for long audio). Using uncompressed or wrong formats (e.g., PNG for 3D textures) wastes memory and bandwidth.

### GAME-030 — Level of Detail (LOD)

**MUST**

Distant objects MUST use lower-detail meshes (LODs). Rendering high-poly meshes for pixels the player cannot see wastes GPU time.

### GAME-031 — World Streaming

**SHOULD**

Large worlds SHOULD stream assets by region asynchronously. The player MUST NOT be forced into a loading screen when crossing a boundary.

### GAME-032 — Asset Versioning

**MUST**

Assets MUST be versioned alongside the code. A mismatch between code and asset versions causes missing or broken content at runtime.

## Audio

### GAME-033 — Async Audio Loading

**MUST NOT**

Audio clips MUST NOT be loaded synchronously during gameplay. They MUST be preloaded or streamed asynchronously to prevent audio stutters.

### GAME-034 — Concurrent Voice Limit

**MUST**

The number of concurrent audio voices MUST be capped. A hundred simultaneous sounds overwhelm the mixer and the CPU.

### GAME-035 — 3D Audio Positioning

**MUST**

Sounds in a 3D game MUST be spatially positioned. Playing stereo-only sounds in a 3D world breaks immersion and spatial awareness.

### GAME-036 — Audio Ducking

**MUST**

Music and ambient audio MUST duck (quiet down) under dialogue or critical sound effects. Without ducking, critical audio becomes inaudible.

## AI-Specific Game Discipline

### GAME-060 — Engine API Verification

**MUST**

Before using an engine-specific API (e.g., Unity `GetComponent`, Unreal `UObject` macros, Godot `Node` methods), the assistant MUST verify the method signature and lifecycle rules for the target engine version. Invented APIs or misuse of engine lifecycles cause silent failures or editor crashes.

See MAS-036 in `_universal/00-master-anti-slop.md`.

### GAME-061 — Existing Component Discovery

**MUST**

Before creating a new gameplay component, manager, or shader, the assistant MUST search the project for an existing equivalent. Inventing parallel movement controllers or UI managers fragments gameplay logic and creates state desyncs.

See MAS-035 in `_universal/00-master-anti-slop.md`.

### GAME-062 — Architecture Restraint

**SHOULD**

The assistant SHOULD NOT introduce complex software design patterns (e.g., heavy dependency injection, deep OOP hierarchies, reactive streams) into hot game loops unless the engine explicitly requires them. Game architecture MUST prioritize cache locality and frame budget over enterprise abstraction.

See MAS-038 in `_universal/00-master-anti-slop.md`.

## Anti-Patterns

### GAME-037 — God Object Prohibition

**MUST NOT**

A `GameManager` that owns everything is prohibited. Every new feature MUST NOT add another field and method to a single monolithic class. Responsibilities MUST be split.

### GAME-038 — Hot Path String Lookup Prohibition

**MUST NOT**

String-based lookups (e.g., `GetComponent("Health")`, `Find("Player")`) MUST NOT be used in hot paths (per-frame updates). Cached component references or integer IDs MUST be used.

### GAME-039 — Per-Frame Allocation Prohibition

**MUST NOT**

Allocating memory (`new` in C#/Java/JS, `malloc` in C++) per frame produces Garbage Collection pauses or heap fragmentation. Objects MUST be reused from an object pool.

### GAME-040 — Per-Frame Scene Query Prohibition

**MUST NOT**

Querying the entire scene tree every frame (e.g., `FindObjectsOfType<Enemy>()` in `Update`) is prohibited. A maintained list updated on spawn/despawn events MUST be used.

### GAME-041 — Float Equality Prohibition

**MUST NOT**

Exact float equality checks (e.g., `if (position.x == target.x)`) MUST NOT be used due to precision issues. Epsilon comparisons (e.g., `Math.Abs(a - b) < epsilon`) MUST be used.

### GAME-042 — Target Hardware Testing

**MUST**

Testing MUST NOT occur only on the high-end development machine. The game MUST be profiled and tested on the minimum target hardware to catch frame drops and memory limits.

### GAME-043 — Gameplay Magic Number Prohibition

**MUST NOT**

Magic numbers in gameplay logic (e.g., `if (health < 23)`) MUST NOT be used. Named constants or data-driven configuration (e.g., `LOW_HEALTH_THRESHOLD`) MUST be used.

### GAME-044 — Save Format Compatibility

**MUST**

Save file formats MUST maintain backward compatibility or include explicit migration logic. A new version MUST NOT render existing player saves unreadable.

### GAME-045 — Hardcoded Path Prohibition

**MUST NOT**

Hardcoded absolute paths (e.g., `C:\Users\dev\assets\...`) MUST NOT be used. Resource paths MUST be resolved dynamically via the engine's virtual file system.

### GAME-046 — Multi-Threading Utilization

**SHOULD**

Modern CPUs have many cores. Physics, animation, pathfinding, and rendering SHOULD be parallelized. Single-threaded architectures leave performance unused.

### GAME-047 — String Externalization

**MUST NOT**

Hardcoding UI and dialogue strings in code is prohibited. Strings MUST be externalized for localization from the start; adding localization at the end costs exponentially more.

### GAME-048 — Accessibility Baseline

**MUST**

Games MUST include a baseline of accessibility: subtitles, remappable controls, and colorblind modes. Excluding these fails platform requirements (e.g., CVAA) and excludes players.

See MAS-039 in `_universal/00-master-anti-slop.md`.

### GAME-049 — Network Reconnection

**MUST**

Multiplayer games MUST provide a reconnection mechanism with state restoration. A minor network blip MUST NOT disconnect the player permanently.

### GAME-050 — Matchmaking Consideration

**SHOULD**

Multiplayer games SHOULD implement skill-based or rule-based matchmaking. Randomly matching players of vastly different skill levels degrades the experience.

### GAME-051 — Telemetry and Analytics

**MUST**

Games MUST include telemetry for crashes, frame rate drops, and player progression bottlenecks. Fixing live issues without analytics is guesswork.

### GAME-052 — Editor and Runtime Separation

**MUST**

Runtime code and editor-only code MUST be strictly separated. Code that works in the editor but relies on editor-only assemblies or states MUST NOT be included in the production build.

### GAME-053 — Reproducible Builds

**MUST**

The build process MUST be a one-command, reproducible operation. Manual build steps lead to unshippable or inconsistent releases.

### GAME-054 — Asset Pipeline CI

**MUST**

The CI pipeline MUST validate the asset pipeline. An asset change that breaks the game MUST be caught in CI, not at runtime on a player's machine.

### GAME-055 — Shader Precompilation

**MUST**

Shaders MUST be precompiled or cached. Compiling a shader on first use during gameplay causes a massive, visible frame stutter.

## Response to Violation

When a rule in this file is violated, report:

Violation: GAME-{NNN}
Reason: {one-line reason}
Correction: {smallest fix}

For multiple violations, report each rule ID separately.

Do not replace a technical correction with a generic explanation.