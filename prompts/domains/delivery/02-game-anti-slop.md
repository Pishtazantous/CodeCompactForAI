---
id: 02-game-anti-slop
title: "Game Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: delivery
version: 1
---

# Game Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
security anti-patterns, output format) are NOT repeated here.

This file covers rules specific to game development: frame budget,
entity systems, asset pipelines, determinism, netcode, and the
patterns that produce stutters, desyncs, or unshippable builds.
Language-specific rules live in `domains/language/`. Engine-specific
rules (Unity, Unreal, Godot) live in `domains/framework/` when
present.

## 1. Stack Assumptions

This layer applies to:

- Native engines (Unreal, custom C++ engines).
- Managed engines (Unity, Godot).
- Web games (Three.js, Babylon.js, WebGL).
- 2D and 3D games, single-player and multiplayer.
- PC, console, mobile, and web targets.

## 2. Frame Budget

### 2.1 16.67 ms for 60 FPS

Every frame has a budget. 60 FPS means 16.67 ms per frame. 30 FPS
means 33.33 ms. Exceeding the budget drops a frame.

### 2.2 Budget Breakdown

- Simulation (physics, AI, gameplay logic): ~50%.
- Rendering: ~30%.
- Audio: ~5%.
- Everything else: ~15%.

The exact split depends on the game. The rule is: every subsystem
has a budget, and it is measured.

### 2.3 Profile Before Optimizing

A 10 FPS drop is either one slow system or a thousand small costs.
The profiler tells which.

### 2.4 No Synchronous Asset Loads During Gameplay

Loading a texture, model, or audio clip mid-frame causes a stutter.
Assets are loaded asynchronously or during a loading screen.

## 3. Entity and Component Systems

### 3.1 Prefer Composition Over Inheritance

A `Player` inheriting from `Character` inheriting from `GameObject`
is rigid. Composition (a `Player` has a `Movement`, a `Health`, a
`Renderer`) is flexible.

### 3.2 Data-Oriented When Performance Requires

For hundreds or thousands of entities, structure-of-arrays layout
is faster than array-of-objects. Use it in hot systems.

### 3.3 Component Purity

A component holds data, not behavior. Systems process components.
This separation enables caching, networking, and serialization.

### 3.4 Entity IDs Are Stable

An entity ID is not a pointer. It survives save/load, network
transfers, and frame boundaries.

### 3.5 System Order Is Deterministic

The order in which systems run affects the simulation. Define it
explicitly. Do not rely on dictionary iteration order.

## 4. Game Loop

### 4.1 Fixed Timestep for Simulation

Physics and gameplay logic run at a fixed rate (60 Hz, 30 Hz). The
renderer interpolates between states.

BAD: Variable timestep for physics. Reproducibility is lost, and
physics behaves differently on different hardware.

### 4.2 Interpolation for Rendering

The renderer displays an interpolated state between the last two
simulation ticks. Without this, the game looks jittery at high
refresh rates.

### 4.3 Clamp Delta Time

A long pause (loading, breakpoint, alt-tab) produces a huge delta.
Clamp it to a maximum (e.g. 100 ms) to prevent physics explosions.

### 4.4 No I/O in the Game Loop

Disk reads, network calls, and file writes are offloaded to worker
threads.

## 5. Determinism

### 5.1 Same Input, Same Output

Given the same inputs and the same initial state, the simulation
produces the same output every time.

### 5.2 No Floating-Point Non-Determinism Across Platforms

`sin`, `cos`, `pow`, and fused multiply-add differ between CPUs,
compilers, and optimization levels. For lockstep multiplayer, use
fixed-point math or a deterministic math library.

### 5.3 Iteration Order

Any iteration over a hash map, a set, or an unordered collection
produces non-deterministic order. Use sorted or indexed collections
in simulation code.

### 5.4 Random Seed

The game's RNG is seeded. Every player in a lockstep session uses
the same seed. Replays are reproducible.

### 5.5 No Wall Clock in Simulation

`System.currentTimeMillis()` or `time.time()` in simulation code
breaks determinism. Use the simulation tick counter.

## 6. Networking

### 6.1 Client-Server or Peer-to-Peer

Pick one. Hybrid approaches (listen servers, host migration) add
complexity. Choose deliberately.

### 6.2 Authoritative Server

The server owns the truth. Clients predict locally and reconcile.
A client never determines the outcome of a competitive action.

### 6.3 Client-Side Prediction

The client applies the action immediately, then reconciles when the
server's authoritative state arrives.

### 6.4 Lag Compensation

The server rewinds the world to the shooter's view when validating a
hit. Without it, high-latency players miss.

### 6.5 Bandwidth Budget

Every message has a size. The bandwidth per player per second is
bounded. Measure and optimize.

### 6.6 Snapshot Interpolation

The client buffers server snapshots and interpolates between them
for smooth motion.

### 6.7 No Trust in Client Input

A client can send any input. Validate on the server: movement speed,
fire rate, resource spending.

### 6.8 Disconnection Handling

A disconnected player is handled gracefully: their entity is frozen,
removed, or taken over by AI depending on the game.

### 6.9 Cheat Prevention

- Server-side validation of every action.
- No client-side trust for resources, positions, or scores.
- Anti-cheat for competitive games.

## 7. Asset Pipeline

### 7.1 Assets Are Built, Not Imported

Raw assets (PSD, Maya, WAV) are processed into runtime formats by a
build step. Runtime does not read the source formats.

### 7.2 Compression and Format

- Textures: platform-specific (BC, ASTC, ETC2). Not PNG in a 3D
  game.
- Audio: compressed (Vorbis, Opus) for long clips; uncompressed for
  short, frequent clips.
- Meshes: optimized index order, LODs, no unused data.

### 7.3 LOD

Distant objects use lower-detail meshes. Without LOD, distant objects
consume GPU time for pixels the player cannot see.

### 7.4 Streaming

Large worlds stream assets by region. The player is not in a loading
screen when crossing a boundary.

### 7.5 Asset Versioning

Assets are versioned with the code. A mismatch causes missing or
wrong assets at runtime.

## 8. Audio

### 8.1 No Blocking Audio Loads

Audio is loaded asynchronously or preloaded. A synchronous load
stutters.

### 8.2 Voice Limit

A hundred simultaneous sounds overwhelm the mixer and the CPU. Cap
the number of concurrent voices.

### 8.3 3D Positioning

Sounds in a 3D game are positioned. A stereo-only sound in a 3D
world breaks immersion.

### 8.4 Audio Ducking

Music quiets under dialogue. Without it, the dialogue is inaudible.

## 9. Game-Specific Anti-Patterns

### 9.1 Variable Timestep Physics

Covered in 4.1.

### 9.2 Unclamped Delta Time

Covered in 4.3.

### 9.3 Synchronous Loading During Gameplay

Covered in 2.4.

### 9.4 Deep Inheritance Hierarchies

Covered in 3.1.

### 9.5 God Object

A `GameManager` that owns everything. Every new feature adds another
field and another method. Split by responsibility.

### 9.6 String-Based Lookups in Hot Paths

BAD: `GetComponent("Health")` per frame.
GOOD: A cached component reference, or an integer ID.

### 9.7 Allocations Per Frame

`new` (C#, Java, JavaScript) or `malloc` (C++) per frame produces GC
pauses or fragmentation. Reuse objects from a pool.

### 9.8 Querying the Scene Tree Every Frame

BAD: `FindObjectsOfType<Enemy>()` in `Update`.
GOOD: A maintained list updated when enemies spawn or die.

### 9.9 Float Equality

BAD: `if (position.x == target.x)`.
GOOD: `if (Math.Abs(position.x - target.x) < epsilon)`.

### 9.10 No Fixed Update for Physics

Physics runs in the physics update, not the render update. Otherwise
behavior depends on frame rate.

### 9.11 Ignoring Frame Rate on Different Hardware

Testing only on a development machine at 120 FPS. The game stutters
on target hardware.

### 9.12 Magic Numbers in Gameplay

BAD: `if (player.health < 23) { ... }`.
GOOD: `if (player.health < LOW_HEALTH_THRESHOLD) { ... }`.

### 9.13 No Save/Load Compatibility

A new version changes the save format. Existing saves are unreadable.

### 9.14 Hardcoded Paths

BAD: `C:\Users\dev\assets\...` in code.
GOOD: A resource path resolved at runtime.

### 9.15 Single-Threaded Everything

Modern CPUs have many cores. Physics, animation, and rendering can
be parallelized. Single-threaded games leave performance unused.

### 9.16 No Localization

Strings hardcoded in code. Localization added at the end costs ten
times more.

### 9.17 No Accessibility

No subtitles, no remappable controls, no colorblind mode. Excludes
players and fails platform requirements.

### 9.18 Trusting Client State in Multiplayer

Covered in 6.7.

### 9.19 No Reconnect

A network blip disconnects the player permanently. Provide reconnect
with state restoration.

### 9.20 No Matchmaking Considerations

Random matchmaking with players of vastly different skill. Skill-based
matchmaking is expected.

### 9.21 No Analytics

No telemetry on crashes, frame rate, or player progression. Fixing
issues is guesswork.

### 9.22 Ignoring the Editor

Runtime code and editor code are tangled. The game works in the
editor but breaks in a build.

### 9.23 No Build Reproducibility

The build script is a series of manual steps. A reproducible build
is a one-command operation.

### 9.24 No Content Pipeline Tests

An asset change breaks the game in a way that is only caught at
runtime. CI validates assets.

### 9.25 Shader Compilation Stutters

A shader compiled on first use causes a stutter. Precompile or use a
shader cache.

## 10. Response to Violation

If a previous response violated a rule here:

```
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

No justification. No apology paragraph. Fix and move on.
