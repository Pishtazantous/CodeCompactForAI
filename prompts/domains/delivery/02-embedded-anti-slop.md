---
id: 02-embedded-anti-slop
title: "Embedded Anti-Slop Layer"
lang: en
depends_on: ["_universal/00-style-guide.md", "_universal/00-master-anti-slop.md"]
category: domain
domain_type: delivery
version: 3
---

# Embedded Anti-Slop Layer

This file defines behavioral contracts specific to embedded systems. It sits in the delivery layer, below the universal anti-slop rules and above language-specific patterns. It covers memory discipline, real-time constraints, interrupt handling, concurrency, power management, communication protocols, firmware updates, and on-target debugging. It does not cover language rules (see language files, especially C, C++, and Rust), framework rules, or security and performance concerns in detail (see concern files).

An embedded system runs on hardware the user cannot inspect, cannot reboot at will, and often cannot update. A bug is not a stack trace; it is a device that stops working in the field.

## Scope

This file applies to bare-metal firmware (C, C++, Rust, assembly), RTOS-based systems (FreeRTOS, Zephyr, RT-Thread, ThreadX), embedded Linux (Yocto, Buildroot), microcontrollers (ARM Cortex-M, ESP32, AVR, RISC-V, PIC), and SoC platforms (Raspberry Pi, Jetson, custom boards). The examples use C and C++ syntax where illustrative. Hardware-specific register names and HAL APIs are placeholders; the project's actual APIs MUST be substituted.

## Rule Severity

Severity follows `_universal/00-style-guide.md`.

## Contracts

An embedded system commits to seven contracts. The table below maps each contract to the rules that enforce it.

| Contract | Description | Enforced By |
|---|---|---|
| Bounded Memory | Firmware fits in RAM and flash with margin. No unbounded allocation. | EMB-001 to EMB-006 |
| Deterministic Timing | Tasks and ISRs complete within budget. WCET is known and respected. | EMB-007 to EMB-011 |
| Safe Concurrency | Shared state between ISRs and tasks is synchronized. No race conditions. | EMB-018 to EMB-023 |
| Power Discipline | Device sleeps when idle, wakes on defined events, and preserves battery. | EMB-024 to EMB-029 |
| Communication Robustness | Links have framing, checksums, timeouts, and resynchronization. | EMB-030 to EMB-035 |
| Recoverable Updates | Firmware updates are atomic, signed, and reversible. | EMB-036 to EMB-040 |
| Field Diagnosability | Device reports state, reset reason, and fault history without physical access. | EMB-045 to EMB-047 |

## Memory Discipline

### EMB-001 — No Dynamic Allocation After Initialization

**MUST NOT**

After the initialization phase, dynamic allocation (`malloc`, `new`, `Box::new`) MUST NOT be used. Heap fragmentation and allocation failure cause silent crashes in the field. If dynamic allocation is strictly unavoidable, a fixed-size pool allocator with a hard cap and a documented failure path MUST be used.

Example (illustrative, C):

BAD:
```c
void handle_event(void) {
    char *buffer = malloc(256); // may return NULL in the field
    // ...
    free(buffer);
}
```

GOOD:
```c
static char buffer[256]; // fixed at compile time
void handle_event(void) { /* use buffer */ }
```

### EMB-002 — Static Allocation for Long-Lived Objects

**MUST**

Buffers, queues, and state machines MUST be statically allocated at compile time or during a bounded initialization phase.

### EMB-003 — Stack Size Budgeting

**MUST**

Every task or thread MUST have a defined stack size. Stack overflow is silent and corrupts adjacent memory. The stack size MUST be based on a measured high-water mark with a margin of at least 30%.

### EMB-004 — Recursion Bound Prohibition

**MUST NOT**

Deep recursion on a small stack overflows. Recursion MUST NOT be used without a mathematically proven maximum depth bound. Iteration MUST be preferred.

### EMB-005 — Memory Measurement

**MUST**

Memory usage MUST be determined via `sizeof`, linker maps, and runtime watermark tracking. Guesswork produces field failures.

### EMB-006 — Linker Script as Design

**MUST**

The memory layout (flash, RAM, stack, heap, reserved regions) MUST be documented in the linker script. A change to the linker script is a change to the system, not a build detail.

## Real-Time Constraints

### EMB-007 — Hard Deadlines

**MUST**

A missed deadline is a failure, not a slowdown. The deadline for every task MUST be identified and proven to be met.

### EMB-008 — Worst-Case Execution Time (WCET)

**MUST**

The worst-case execution time MUST be analyzed, not the average. A function that usually takes 10 microseconds may take 100 under a cache miss or an interrupt storm.

### EMB-009 — Priority Inversion Prevention

**MUST**

Priority inversion MUST be prevented. A low-priority task holding a lock MUST NOT block a high-priority task. Priority inheritance mutexes or lock-free designs MUST be used.

### EMB-010 — Interrupt Latency Bounding

**MUST**

The time between an interrupt firing and its handler running MUST be bounded. Long critical sections in other code delay it. The maximum disabled-interrupt window MUST be measured and capped.

### EMB-011 — Timing Determinism

**MUST**

A real-time system MUST produce the same timing behavior on every run. Non-deterministic caches, DMA contention, or bus arbitration that violate this MUST be mitigated.

## Interrupt Handling

### EMB-012 — Short Interrupt Handlers

**MUST**

An Interrupt Service Routine (ISR) MUST only capture data, signal a task, and return. Complex processing MUST happen in a task context.

Example (illustrative, C):

BAD:
```c
void ADC_IRQHandler(void) {
    uint16_t sample = ADC_Read();
    float voltage = sample * 3.3f / 4096.0f; // float math in ISR
    log_to_flash(voltage);                    // flash write in ISR
}
```

GOOD:
```c
volatile uint16_t g_adc_sample;
void ADC_IRQHandler(void) {
    g_adc_sample = ADC_Read();
    BaseType_t woken = pdFALSE;
    vTaskNotifyGiveFromISR(adc_task, &woken);
    portYIELD_FROM_ISR(woken);
}
```

### EMB-013 — No Blocking in ISRs

**MUST NOT**

Blocking operations (`malloc`, `printf`, mutex acquisition, waiting, `delay_ms`) MUST NOT be used in ISRs. They may deadlock or take unbounded time.

### EMB-014 — `volatile` and Atomics for Shared Data

**MUST**

A variable shared between an ISR and a task MUST be declared `volatile` (in C/C++) or as an atomic type (in Rust/C11).

### EMB-015 — Minimal Critical Sections

**MUST**

Interrupts MUST be disabled only for the shortest possible window. Atomic operations or lock-free queues MUST be preferred. The maximum disabled window MUST be measured and documented.

### EMB-016 — Intentional Interrupt Priority

**MUST**

Interrupt priority assignment MUST be intentional. A priority that conflicts with the RTOS's requirements (e.g., `configMAX_SYSCALL_INTERRUPT_PRIORITY` in FreeRTOS) causes crashes.

### EMB-017 — Interrupt Source Clearing

**MUST**

An ISR MUST clear the interrupt flag. An ISR that does not clear the flag re-enters immediately, locking the device in an interrupt storm.

## Concurrency

### EMB-018 — Single Writer Principle

**MUST**

Shared data MUST have one writer. Multiple writers require explicit synchronization.

### EMB-019 — Lock-Free ISR-to-Task Queues

**MUST**

A single-producer single-consumer ring buffer MUST be used for ISR-to-task communication. A mutex MUST NEVER be used in an ISR.

### EMB-020 — Hardware Watchdog

**MUST**

A hardware watchdog MUST reset the system when a task hangs. The watchdog MUST be fed by the healthy path (e.g., a "supervisor" task checking subsystem heartbeats), not by a high-priority task that runs regardless of application health.

### EMB-021 — No Busy-Wait in Tasks

**MUST NOT**

Busy-waiting consumes CPU and power. The RTOS's sleep or event mechanisms MUST be used instead of spinning.

### EMB-022 — Atomic Multi-Byte Access

**MUST**

A multi-byte variable modified by both an ISR and a task on an architecture that does not guarantee atomic access (e.g., 32-bit variable on an 8-bit MCU) MUST use atomic operations, `ATOMIC_BLOCK`, or brief interrupt disabling.

### EMB-023 — Shared State Avoidance

**SHOULD**

A design where each task owns its data and communicates via queues SHOULD be preferred over sharing state with locks.

## Power Management

### EMB-024 — Sleep When Idle

**MUST**

Between events, the CPU MUST sleep. The idle task MUST enter the lowest power mode consistent with wake-up latency requirements.

### EMB-025 — Explicit Wake-Up Sources

**MUST**

Every wake-up source (timer, GPIO, radio) MUST be explicitly enumerated. An unexpected wake-up wastes power and indicates a bug.

### EMB-026 — Radio Duty Cycle Minimization

**MUST**

For battery-powered radios, transmit time MUST be minimized. Data MUST be batched where possible.

### EMB-027 — Power Measurement

**MUST**

Power consumption MUST be measured with a meter or the platform's power profiler. Estimated power consumption is a guess.

### EMB-028 — Unused Peripheral Disabling

**MUST**

Every peripheral the application does not use MUST be disabled (clock gated and powered down). A peripheral left in its default state consumes power.

### EMB-029 — Brown-Out Handling

**MUST**

Brown-out detection MUST be enabled. A low-voltage condition corrupts memory; the system MUST handle it via safe reset or safe state restoration.

## Communication

### EMB-030 — Protocol Framing and Checksums

**MUST**

Every communication protocol MUST have a framing scheme (length prefix, delimiter, fixed size), a checksum (CRC, not parity alone), a timeout for incomplete frames, and a resynchronization path after error.

### EMB-031 — Explicit Byte-Order Conversion

**MUST**

Endianness varies between MCUs. Byte order MUST be converted explicitly before transmission and after reception.

### EMB-032 — High-Throughput I/O

**MUST**

Polling a UART at high baud rates wastes cycles. Interrupt-driven or DMA-based I/O MUST be used for high-throughput communication.

### EMB-033 — Flow Control

**MUST**

Hardware or software flow control MUST be used to prevent a fast sender from overwhelming a slow receiver.

### EMB-034 — Expected Error Handling

**MUST**

Communication errors MUST be expected, logged, and retried with bounds. An unbounded `while (true) { retry; }` in a task starves other tasks and MUST NOT be used.

### EMB-035 — Bounded Receive Buffers

**MUST**

Every receive buffer MUST have a maximum size. A sender that exceeds it MUST trigger a defined policy: drop oldest, drop newest, or disconnect.

## Firmware Updates

### EMB-036 — Signed Firmware

**MUST**

Every firmware image MUST be cryptographically signed. The bootloader MUST verify the signature before applying. An unsigned update path is a critical vulnerability.

### EMB-037 — Atomic Updates

**MUST**

A power loss during an update MUST NOT brick the device. A/B partitions or a recoverable bootloader MUST be used.

### EMB-038 — Rollback Capability

**MUST**

A bad update MUST be revertible. The previous image MUST be kept until the new one has proven itself via a health check or a timeout.

### EMB-039 — Version Compatibility

**MUST**

The new firmware MUST work with the existing configuration and data. Migration MUST be explicit.

### EMB-040 — Update Authorization

**MUST**

An update MUST be authorized by the device owner or a trusted server. An unauthenticated update path allows malicious firmware.

## Testing and Debugging

### EMB-041 — On-Target Testing

**MUST**

Tests MUST run on the target hardware. Timing, interrupts, and peripherals behave differently on hardware than on a simulator.

### EMB-042 — Hardware-in-the-Loop (HIL)

**SHOULD**

For safety-critical or complex systems, HIL testing SHOULD be used to exercise the real hardware in simulated environments.

### EMB-043 — No `printf` in Production

**MUST NOT**

`printf` blocks, uses the heap, and is slow. A lightweight logging mechanism with a non-blocking ring buffer MUST be used in production.

### EMB-044 — Watchpoints and Trace

**SHOULD**

The platform's debugger and trace facilities (SWO, ETM, SWD, JTAG) SHOULD be used. `printf` debugging MUST be a last resort.

### EMB-045 — Fault Handler State Capture

**MUST**

A HardFault (or platform equivalent) handler MUST capture the faulting instruction address, register state, stack trace, and reset reason to non-volatile memory before resetting.

### EMB-046 — Reset Reason Tracking

**MUST**

The device MUST record why it reset (power-on, watchdog, brown-out, software). Without it, an unexpected reset is a mystery.

### EMB-047 — Persistent Logs

**MUST**

Crash logs MUST be stored in non-volatile memory (flash, FRAM, backup SRAM). A log that dies with the reset is useless.

## AI-Specific Embedded Discipline

### EMB-060 — HAL and Register API Verification

**MUST**

Before writing hardware abstraction layer (HAL) calls or direct register manipulations, the assistant MUST verify the register names, bitmasks, and HAL function signatures against the specific MCU's datasheet and reference manual. Invented register names or incorrect bit shifts cause silent hardware misbehavior or permanent damage.

See MAS-036 in `_universal/00-master-anti-slop.md`.

### EMB-061 — RTOS API Verification

**MUST**

Before using an RTOS API, the assistant MUST verify the function signature, required macro definitions, and ISR-safe variants (e.g., `xQueueSendFromISR` instead of `xQueueSend`). Using task-level APIs inside an ISR causes immediate system crashes.

See MAS-036 in `_universal/00-master-anti-slop.md`.

### EMB-062 — Existing Peripheral Driver Discovery

**MUST**

Before writing a new peripheral driver or communication protocol handler, the assistant MUST search the project or the RTOS's native subsystem for an existing driver. Inventing parallel I2C or SPI drivers creates resource contention and timing violations.

See MAS-035 in `_universal/00-master-anti-slop.md`.

## Anti-Patterns

### EMB-048 — Busy-Wait Delays

**MUST NOT**

Busy-wait loops (e.g., `for (i = 0; i < 1000000; i++) {}`) block the CPU and waste power. A hardware timer or the RTOS's sleep function MUST be used.

### EMB-049 — Unbounded Loops in Tasks

**MUST NOT**

A task that loops on an error without yielding starves other tasks. Retries MUST be bounded and include a delay (e.g., `vTaskDelay`).

### EMB-050 — Global Mutable State

**MUST NOT**

Shared globals without `volatile` or atomics produce non-deterministic race conditions and MUST NOT be used.

### EMB-051 — Missing Errata Workarounds

**MUST**

Silicon errata MUST be read for every peripheral used. Ignoring documented errata causes intermittent failures.

### EMB-052 — Interrupt Storm Prevention

**MUST**

An interrupt that fires continuously due to a stuck condition starves the CPU. The source MUST be debounced and cleared.

### EMB-053 — Timing Measurement Requirement

**MUST NOT**

Timing assumptions without measurement (e.g., "This loop takes 1 microsecond") are prohibited. Timing MUST be measured with a logic analyzer or oscilloscope, as compiler optimization and cache state change execution time.

### EMB-054 — Floating Point in ISRs

**MUST NOT**

FPU context save/restore in an ISR is slow and error-prone. Fixed-point math MUST be used, or the computation MUST be deferred to a task.

### EMB-055 — Flash Erase Before Write

**MUST NOT**

Flash MUST be erased before writing. Writing without erasing corrupts data silently.

### EMB-056 — Power-On Self-Test (POST)

**MUST**

A device that boots with corrupted RAM behaves unpredictably. A POST MUST be executed to catch hardware faults early.

### EMB-057 — Clock Configuration Verification

**MUST**

The MCU clock tree MUST be verified against a known reference. A misconfigured clock tree causes timing to be off by significant margins.

### EMB-058 — Explicit Peripheral Initialization

**MUST**

Every peripheral MUST be initialized explicitly. A GPIO pin MUST NOT be left floating; it MUST be configured as input with pull, output with a defined level, or analog, based on the schematic.

### EMB-059 — DMA Cache Coherency

**MUST**

DMA transfers bypass the CPU cache. Buffers shared with DMA MUST have cache maintenance applied (invalidate before read, clean before write).

### EMB-063 — Production Debug Interface

**MUST NOT**

The debug interface (JTAG/SWD) MUST NOT be left enabled in production. It exposes memory and execution. It MUST be disabled or locked.

### EMB-064 — Operating Range Testing

**MUST**

Code MUST be tested across the specified operating temperature and voltage range. Code that works at 25°C may fail at -40°C or 85°C.

### EMB-065 — Struct Atomicity

**MUST NOT**

`volatile` prevents compiler caching but does not make a multi-field struct atomic. A struct updated by an ISR and read by a task MUST use a lock or a double-buffer pattern.

### EMB-066 — Watchdog Reset Handling

**MUST**

A device that resets repeatedly because the watchdog was not fed during a long operation MUST be restructured. The watchdog MUST be fed from the appropriate task.

### EMB-067 — Firmware Version Reporting

**MUST**

The device MUST report its firmware version. Field debugging cannot identify the running build without it.

### EMB-068 — Configuration CRC

**MUST**

Configuration stored in flash MUST have a CRC. A corrupted configuration MUST NOT load silently.

### EMB-069 — Protected Flash Writes

**MUST**

Flash writes during a power loss can corrupt the sector. Data MUST be written to a backup sector first, then swapped.

### EMB-070 — Safe Mode

**MUST**

A device that boots into a broken state MUST have a safe mode (minimal configuration, waiting for update) to allow recovery.

### EMB-071 — Brown-Out Reset Cause

**MUST NOT**

A brown-out reset MUST NOT be treated as a normal power-on. The device boots with potentially corrupted configuration and MUST handle it explicitly.

### EMB-072 — Factory Reset Path

**MUST**

A device MUST have a factory reset path. A device without one is unrecoverable if configuration becomes corrupt.

### EMB-073 — Production Hardware Testing

**MUST NOT**

Testing only on the development board is prohibited. The production device has different RAM, power supply, and debug constraints.

### EMB-074 — First Silicon Errata

**MUST**

Early silicon revisions have more errata. Both the early and final revision errata sheets MUST be read.

### EMB-075 — Field Firmware Version Negotiation

**MUST**

The device MUST negotiate compatibility before accepting an update. Accepting any firmware the server sends risks applying an incompatible version and bricking the device.

## Response to Violation

When a rule in this file is violated, report:

Violation: EMB-{NNN}
Reason: {one-line reason}
Correction: {smallest fix}

For multiple violations, report each rule ID separately.

Do not replace a technical correction with a generic explanation.