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

Layered under `_universal/00-master-anti-slop.md`. Universal rules are not
repeated. Engine and language behavior belongs to related layers.

## 1. Stack Assumptions

**1.1 Define the target frame.** Record platform, refresh-rate target,
resolution, simulation rate, input latency, and memory budget.

**1.2 Follow the engine loop.** Respect the project's fixed-step, variable-
step, render, input, audio, and pause architecture.

**1.3 Keep gameplay and presentation separate.** Simulation state is not
derived from animation or UI state.

## 2. Domain Contracts

**2.1 Frame time is a budget.** Simulation, input, physics, animation, audio,
and rendering have explicit allocations and measurable overrun behavior.

**2.2 Game state is authoritative.** Events that affect simulation are applied
through a defined order and owner, not from presentation callbacks.

**2.3 Assets are controlled.** Memory, formats, load points, and release
licenses are reviewed before use.

**2.4 Determinism is scoped.** Randomness, fixed-point arithmetic, iteration
order, and time sources are deterministic where replay or lockstep requires.

## 3. Domain-Specific Rules

**3.1 Profile the real target.** Use representative scenes and device
profiles; desktop editor timing is not console or mobile evidence.

**3.2 Use ECS ownership deliberately.** Give each component and system one
owner; avoid hidden cross-entity mutation and allocation during updates.

**3.3 Bound collections.** Pool or reuse objects only when ownership and reset
are explicit. Never let a level create unbounded entities.

**3.4 Load assets by need.** Define budgets, streaming thresholds, fallback
assets, and failure states for missing or corrupt files.

**3.5 Validate saves.** Version schemas, validate checksums and fields, and
recover or reject corrupt data without invoking arbitrary code.

**3.6 Make inputs repeatable.** Rebind safely, distinguish device loss, and
avoid polling more frequently than the engine supports.

**3.7 Separate simulation clocks.** Apply pause, slow motion, rollback, and
network prediction through explicit timing rules.

**3.8 Test determinism where promised.** Replay fixed input, seed, and platform
configuration when deterministic behavior is a product contract.

**3.9 Prevent frame spikes.** Avoid synchronous disk, network, allocation,
or shader compilation in the frame path; stage work before play.

**3.10 Measure player experience.** Track frame time percentiles, hitch time,
memory, load time, input latency, and crash frequency by platform.

**3.22 Separate simulation and render state.** Animation, camera, effects, and UI never overwrite authoritative gameplay state.

**3.23 Control asset loading.** Define memory, streaming, corruption, and missing-content fallbacks within the target budget.

**3.24 Keep saves recoverable.** Version authoritative state, validate checksums, and recover from interrupted or corrupt writes.

**3.25 Preserve input semantics.** Device loss, rebinding, focus changes, and reconnects do not duplicate or silently discard actions.

**3.26 Measure target behavior.** Test release builds on representative hardware with frame, memory, load, input, and crash budgets.

## 4. Domain-Specific Anti-Patterns

### 4.1 Allocation During Every Frame

BAD:
```cpp
void update() {
    auto bullet = std::make_unique<Bullet>();
    spawn(std::move(bullet));
}
```

GOOD:
```cpp
void update() {
    Bullet& bullet = pool.acquire();
    bullet.reset();
    spawn(bullet);
}
```

The frame path uses bounded owned storage.

### 4.2 Randomness From Wall Clock

BAD:
```cpp
spawnX = std::rand() % 100;
```

GOOD:
```cpp
spawnX = randomStream.next() % 100;
```

Replay can reproduce the sequence.

### 4.3 Missing Asset Crash

BAD:
```cpp
if (!texture) {
    abort();
}
```

GOOD:
```cpp
if (!texture) {
    texture = fallbackTexture();
    scheduleAssetRecovery();
}
```

A missing asset has a bounded, observable fallback.

**3.11 Budget loading and streaming.** Measure worst-case memory, transfer time, and hitches rather than assuming assets arrive before play.

**3.12 Keep gameplay state serializable.** Save only authoritative state and version every format; presentation caches may be rebuilt.

**3.13 Respect platform lifecycle.** Pause, suspend, focus loss, controller disconnect, and display refresh must not corrupt simulation state.

**3.14 Make replay contracts explicit.** Record seed, input stream, build identity, and compatibility rules when replay is a supported feature.

**3.15 Test performance regressions.** Keep representative scenes, device profiles, and frame-time thresholds in the project's test or profiling workflow.

**3.16 Separate simulation from render state.** UI animation, camera smoothing, and visual effects cannot become authoritative gameplay state.

**3.17 Handle content failure.** Missing localization, shaders, audio, or input definitions use a tested fallback and report the failure.

**3.18 Keep asset references stable.** Asset IDs, bundle membership, and ownership follow the project's content pipeline and release process.

**3.19 Profile the critical path.** Identify the systems that exceed the frame budget and optimize against a measured scenario, not intuition.

**3.20 Test remapping and reconnect.** Input changes preserve gameplay state and do not duplicate actions when devices return.

**3.21 Verify release builds.** Stripped, compressed, and optimized builds retain required behavior, assets, diagnostics, and platform permissions.

**3.22 Keep content deterministic.** Asset identifiers, bundle order, and initialization must not change simulation results unexpectedly.

**3.23 Handle input loss.** Disconnected devices, focus changes, and unavailable controllers lead to a documented pause or neutral state.

**3.24 Preserve user progress.** Save frequency, atomicity, and recovery are defined for each supported save type.

## 5. Response to Violation

If a prior response violated this layer, name the frame, ECS, asset, timing,
or determinism issue and show the corrected design. Do not claim a target
frame rate without a measured build.
