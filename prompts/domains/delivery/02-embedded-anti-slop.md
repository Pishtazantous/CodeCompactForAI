---
id: 02-embedded-anti-slop
title: "Embedded Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: delivery
version: 2
---

# Embedded Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
generic security, dependency addition, output format) are NOT
repeated here.

This file covers rules specific to embedded systems: memory
discipline, real-time constraints, interrupt handling, concurrency,
power management, communication protocols, firmware updates, and
on-target debugging. It does NOT cover language rules (see the
language files, especially C and C++), framework rules, or security
and performance concerns in detail (see the concern files).

An embedded system runs on hardware the user cannot inspect, cannot
reboot at will, and often cannot update. A bug is not a stack trace;
it is a device that stops working in the field. The rules below
reflect that constraint.

## 1. Stack Assumptions

This file applies to:

- Bare-metal firmware (C, C++, Rust, assembly).
- RTOS-based systems (FreeRTOS, Zephyr, RT-Thread, ThreadX).
- Embedded Linux (Yocto, Buildroot).
- Microcontrollers (ARM Cortex-M, ESP32, AVR, RISC-V, PIC).
- SoC platforms (Raspberry Pi, Jetson, custom boards).

The examples use C and C++. The principles are language-agnostic.
Language-specific rules (undefined behavior in C++, unsafe in Rust)
live in the language files. Hardware-specific register names and
HAL APIs are placeholders; substitute the project's actual APIs.

## 2. Delivery Contracts

An embedded system commits to seven contracts. Every section below
enforces one or more of these.

### 2.1 Bounded Memory

The firmware fits in the device's RAM and flash with margin. No
allocation grows without bound. No stack overflow is possible.

### 2.2 Deterministic Timing

Every task and interrupt handler completes within its budget. The
worst-case execution time (WCET) is known and respected.

### 2.3 Safe Concurrency

Shared state between interrupts and tasks is synchronized with
atomics, critical sections, or lock-free structures. No race
conditions.

### 2.4 Power Discipline

The device sleeps when idle, wakes on defined events, and does not
drain the battery unnecessarily.

### 2.5 Communication Robustness

Every serial, I2C, SPI, CAN, or radio link has framing, checksums,
timeouts, and resynchronization. A noisy bus does not crash the
device.

### 2.6 Recoverable Updates

Firmware updates are atomic, signed, and reversible. A power loss
during an update does not brick the device.

### 2.7 Field Diagnosability

A device in the field can report its state, its reset reason, and
its fault history. Debugging a failure does not require physical
access.

## 3. Memory Discipline

### 3.1 No Dynamic Allocation After Initialization

After the initialization phase, no `malloc`, `new`, `Box::new`, or
equivalent. Heap fragmentation and allocation failure cause silent
crashes in the field.

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

void handle_event(void) {
    // use buffer
}
```

If dynamic allocation is unavoidable, use a fixed-size pool
allocator with a hard cap and a documented failure path.

### 3.2 Static Allocation for Long-Lived Objects

Buffers, queues, and state machines are statically allocated at
compile time or during a bounded initialization phase.

### 3.3 Stack Size Is a Budget

Every task or thread has a defined stack size. Overflow is silent
and corrupts adjacent memory.

BAD: A task with 1 KB stack and 10 levels of recursion.

GOOD: A task with a measured high-water mark and a margin of at
least 30%.

### 3.4 No Recursion Without a Proven Bound

Deep recursion on a small stack overflows. Prefer iteration, or
prove the maximum depth is safe.

BAD:
```c
int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1); // stack grows with n
}
```

GOOD:
```c
int factorial(int n) {
    int result = 1;
    for (int i = 2; i <= n; i++) result *= i;
    return result;
}
```

### 3.5 Measure, Do Not Guess

`sizeof`, linker maps, and runtime watermark tracking determine
memory usage. Guesswork produces field failures.

### 3.6 Linker Scripts Are Part of the Design

The memory layout (flash, RAM, stack, heap, reserved regions) is
documented. A change to the linker script is a change to the
system, not a build detail.

## 4. Real-Time Constraints

### 4.1 Deadlines Are Hard

A missed deadline is a failure, not a slowdown. Identify the
deadline for every task and prove it is met.

### 4.2 Worst-Case Execution Time

Analyze the worst case, not the average. A function that usually
takes 10 microseconds may take 100 under a cache miss or an
interrupt storm.

### 4.3 Priority Inversion

A low-priority task holding a lock blocks a high-priority task.
Use priority inheritance mutexes or lock-free designs.

BAD: A high-priority task waits on a mutex held by a low-priority
task that is preempted by a medium-priority task.

GOOD: Use the RTOS's priority-inheriting mutex, or restructure so
the high-priority task does not depend on the lock.

### 4.4 Interrupt Latency

The time between an interrupt firing and its handler running is
bounded. Long critical sections in other code delay it. Measure
and cap the maximum disabled-interrupt window.

### 4.5 Determinism

A real-time system produces the same timing behavior on every run.
Non-deterministic caches, DMA contention, or bus arbitration
violate this.

## 5. Interrupt Handling

### 5.1 Interrupt Handlers Are Short

An ISR captures data, signals a task, and returns. Complex
processing happens in a task.

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

### 5.2 No Blocking in ISRs

No `malloc`, no `printf`, no mutex acquisition, no waiting. These
may deadlock or take unbounded time.

### 5.3 `volatile` for Shared Data

A variable shared between an ISR and a task is `volatile` (in C)
or an atomic (in Rust).

BAD:
```c
int g_flag = 0; // compiler may cache the read in a register

while (!g_flag) { /* spin */ }
```

GOOD:
```c
volatile int g_flag = 0;

while (!g_flag) { /* spin */ }
```

### 5.4 Critical Sections Are Minimal

Disable interrupts only for the shortest possible window. Prefer
atomic operations or lock-free queues. Measure the maximum disabled
window and document it.

### 5.5 Interrupt Priority Assignment

Higher-priority interrupts preempt lower-priority ones. The
priority assignment is intentional, not accidental. A priority
that conflicts with the RTOS's requirements (for example,
`configMAX_SYSCALL_INTERRUPT_PRIORITY` in FreeRTOS) causes crashes.

### 5.6 Clear the Interrupt Source

An ISR that does not clear the flag re-enters immediately. The
device locks in an interrupt storm.

## 6. Concurrency

### 6.1 One Writer Per Shared Variable

Shared data has one writer. Multiple writers require explicit
synchronization.

### 6.2 Lock-Free Queues for ISR-to-Task

A single-producer single-consumer ring buffer is the standard
pattern. Never a mutex in an ISR.

### 6.3 Watchdog

A hardware watchdog resets the system when a task hangs. The
watchdog is fed by the healthy path, not by the hung path.

BAD: Feeding the watchdog from a high-priority task that runs
regardless of whether the application logic is healthy.

GOOD: Feeding the watchdog from a "supervisor" task that checks
each subsystem's heartbeat.

### 6.4 No Busy-Wait in Tasks

A busy-wait consumes CPU and power. Use the RTOS's sleep or event
mechanisms.

BAD:
```c
while (!flag) { /* spin, burning power */ }
```

GOOD:
```c
ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
```

### 6.5 Atomic Access for Multi-Byte Variables

A 32-bit variable modified by both an ISR and a task on an 8-bit
MCU requires atomic access. Use `ATOMIC_BLOCK`, disable interrupts
briefly, or use atomics.

### 6.6 Avoid Shared State When Possible

A design where each task owns its data and communicates via queues
is simpler than one that shares state with locks.

## 7. Power Management

### 7.1 Sleep When Idle

Between events, the CPU sleeps. The idle task enters the lowest
power mode consistent with wake-up latency requirements.

### 7.2 Wake-Up Sources Are Explicit

Every wake-up source is enumerated (timer, GPIO, radio). An
unexpected wake-up wastes power and indicates a bug.

### 7.3 Radio Duty Cycle

For battery-powered radios, minimize transmit time. Batch data
where possible.

### 7.4 Measure Power

Estimated power consumption is a guess. Measure it with a meter or
the platform's power profiler. A firmware change that doubles
consumption is invisible without measurement.

### 7.5 Disable Unused Peripherals

A peripheral left in its default state consumes power. Disable
every peripheral the application does not use.

BAD: Leaving the ADC running when only the GPIO is needed.

GOOD: Disabling the ADC clock and powering it down until needed.

### 7.6 Handle Brown-Out

A low-voltage condition corrupts memory. Enable brown-out detection
and handle it (safe reset, safe state restoration).

## 8. Communication

### 8.1 Framing and Checksums

Every protocol has:

- A framing scheme (length prefix, delimiter, fixed size).
- A checksum (CRC, not parity alone).
- A timeout for incomplete frames.
- A resynchronization path after error.

BAD:
```c
while (UART_Available()) {
    process_byte(UART_Read()); // no framing, no checksum
}
```

GOOD:
```c
typedef struct {
    uint8_t  start;
    uint16_t length;
    uint8_t  payload[MAX_PAYLOAD];
    uint16_t crc;
} Frame;
// Parse with state machine, validate CRC, drop on timeout.
```

### 8.2 No Byte-Order Assumptions

Endianness varies between MCUs. Convert explicitly.

### 8.3 Interrupt or DMA for High-Throughput

Polling a UART at high baud rates wastes cycles. Use
interrupt-driven or DMA-based I/O.

### 8.4 Flow Control

A fast sender overwhelms a slow receiver. Use hardware or software
flow control.

### 8.5 Error Handling Is Expected

A communication error is expected. Log it, retry, and continue.
Never `while (true) { retry; }` in a task, which starves other
tasks.

### 8.6 Bounded Buffers

Every buffer has a maximum size. A sender that exceeds it triggers
a policy: drop oldest, drop newest, or disconnect.

## 9. Firmware Updates

### 9.1 Signed Firmware

Every firmware image is signed. The bootloader verifies the
signature before applying. An unsigned update path is a
vulnerability.

### 9.2 Atomic Update

A power loss during an update must not brick the device. Use A/B
partitions or a bootloader that can recover.

### 9.3 Rollback

A bad update must be revertible. Keep the previous image until the
new one has proven itself (via a health check or a timeout).

### 9.4 Version Compatibility

The new firmware works with the existing configuration and data.
Migration is explicit.

### 9.5 Update Authorization

An update is authorized by the device owner or a trusted server.
An unauthenticated update path allows malicious firmware.

## 10. Testing and Debugging

### 10.1 On-Target Testing

A test that runs only on a simulator is partial. Timing,
interrupts, and peripherals behave differently on hardware.

### 10.2 Hardware-in-the-Loop

For safety-critical or complex systems, HIL testing exercises the
real hardware.

### 10.3 No `printf` in Production

`printf` blocks, uses the heap, and is slow. Use a lightweight
logging mechanism with a ring buffer.

BAD:
```c
printf("sensor: %d\n", value); // blocking, heap-allocating
```

GOOD:
```c
log_push(LOG_SENSOR, value); // ring buffer, non-blocking
```

### 10.4 Watchpoints and Trace

Use the platform's debugger and trace facilities (SWO, ETM, SWD,
JTAG). `printf` debugging is a last resort.

### 10.5 Fault Handlers Capture State

A HardFault (or the platform's equivalent) captures:

- The faulting instruction address.
- The register state.
- A stack trace.
- The reset reason.

Without this, a field crash is undebuggable.

BAD:
```c
void HardFault_Handler(void) {
    while (1); // silent hang
}
```

GOOD:
```c
void HardFault_Handler(void) {
    save_fault_context();   // to non-volatile memory
    log_fault();
    NVIC_SystemReset();
}
```

### 10.6 Reset Reason Tracking

The device records why it reset (power-on, watchdog, brown-out,
software). Without it, an unexpected reset is a mystery.

### 10.7 Persistent Logs

Crash logs are stored in non-volatile memory (flash, FRAM, backup
SRAM). A log that dies with the reset is useless.

## 11. Anti-Patterns

### 11.1 `malloc` After Init

Covered in 3.1.

### 11.2 `printf` in an ISR

Covered in 5.2.

### 11.3 Missing `volatile`

Covered in 5.3.

### 11.4 Deep Recursion

Covered in 3.4.

### 11.5 Busy-Wait Delays

BAD: `for (i = 0; i < 1000000; i++) {}`.

GOOD: A hardware timer or the RTOS's sleep function.

A busy-wait blocks the CPU and wastes power.

### 11.6 Stack Overflow

Covered in 3.3.

### 11.7 Unbounded Loops in Tasks

A task that loops on an error without yielding starves other tasks.

BAD:
```c
while (spi_write(data) != OK) {
    // retry forever
}
```

GOOD:
```c
int retries = 0;
while (spi_write(data) != OK && retries < 3) {
    vTaskDelay(pdMS_TO_TICKS(10));
    retries++;
}
if (retries >= 3) handle_spi_failure();
```

### 11.8 Global Mutable State

Shared globals without `volatile` or atomics. Races produce
non-deterministic bugs.

### 11.9 No Watchdog

Covered in 6.3.

### 11.10 Missing Errata Workarounds

Silicon errata are documented. Ignoring them causes intermittent
failures. Read the errata sheet for every peripheral used.

### 11.11 No Reset Reason Tracking

Covered in 10.6.

### 11.12 Interrupt Storm

An interrupt fires continuously due to a stuck condition. The CPU
starves. Debounce and clear the source.

### 11.13 Timing Assumptions Without Measurement

BAD: "This loop takes 1 microsecond."

GOOD: Measured with a logic analyzer or an oscilloscope. Compiler
optimization and cache state change the timing.

### 11.14 No Brown-Out Detection

Covered in 7.6.

### 11.15 Floating Point in ISRs

FPU context save/restore in an ISR is slow and error-prone. Use
fixed-point or defer the computation.

### 11.16 Non-Atomic Multi-Byte Access

Covered in 6.5.

### 11.17 Overwriting Flash Without Erase

Flash must be erased before writing. Writing without erasing
corrupts data silently.

### 11.18 No Power-On Self-Test

A device that boots with corrupted RAM behaves unpredictably. A
POST catches this early.

### 11.19 Firmware Update Without Fallback

Covered in 9.2 and 9.3.

### 11.20 No Clock Configuration Verification

The MCU runs at the wrong frequency because the clock tree is
misconfigured. Timing is off by 10%. Verify the clock against a
known reference.

### 11.21 Uninitialized Peripherals

A peripheral is left in a default state that consumes power or
drives an output. Initialize every peripheral explicitly.

BAD: A GPIO pin left floating with no pull-up or pull-down.

GOOD: Configure every pin as input with pull, output with a defined
level, or analog, based on the schematic.

### 11.22 DMA Without Cache Coherency

DMA transfers bypass the CPU cache. Buffers shared with DMA
require cache maintenance (invalidate before read, clean before
write).

### 11.23 No Production Debug Interface

The debug interface is left enabled in production. It exposes
memory and execution. Disable it or lock it.

### 11.24 Ignoring Temperature and Voltage

Code that works at 25°C fails at -40°C or 85°C. Test across the
operating range.

### 11.25 `volatile` on Structs Without Atomicity

`volatile` prevents compiler caching but does not make a
multi-field struct atomic. A struct updated by an ISR and read by a
task requires a lock or a double-buffer pattern.

### 11.26 Reading a Multi-Byte Value Non-Atomically

BAD:
```c
uint32_t now = g_tick_count; // may read a torn value if ISR updates
```

GOOD:
```c
uint32_t now;
do {
    uint32_t before = g_tick_count;
    now = before;
} while (now != g_tick_count); // or disable interrupts briefly
```

### 11.27 ISR Priority Set Below RTOS Threshold

A priority at or below the RTOS's `configMAX_SYSCALL_INTERRUPT_PRIORITY`
may call RTOS APIs. Above that threshold, calling `xQueueSendFromISR`
crashes.

### 11.28 `Delay` in an ISR

`delay_ms`, `sleep`, or any blocking call in an ISR halts the
system.

### 11.29 Not Handling Watchdog Reset

A device that resets repeatedly because the watchdog was not fed
during a long operation. Feed the watchdog from the appropriate
task, or restructure the operation.

### 11.30 Unbounded Buffers in the Receive Path

A UART receive buffer without a maximum size overflows when the
sender is faster than the consumer.

### 11.31 No Version in Firmware

The device does not report its firmware version. Field debugging
cannot tell which build is running.

### 11.32 Missing CRC on Configuration

Configuration stored in flash without a CRC. A corrupted
configuration loads silently and misconfigures the device.

### 11.33 Unprotected Flash Writes

Flash writes during a power loss can corrupt the sector. Write to a
backup sector first, then swap.

### 11.34 No Safe Mode

A device that boots into a broken state with no recovery path. A
safe mode (minimal configuration, waiting for update) allows
recovery.

### 11.35 Ignoring Brown-Out Reset Cause

A brown-out reset is treated as a power-on. The device boots with
potentially corrupted configuration.

### 11.36 No Factory Reset Path

A device without a factory reset is unrecoverable if configuration
becomes corrupt.

### 11.37 Testing Only on the Dev Board

The dev board has more RAM, a stable power supply, and a debugger.
The production device has none of these.

### 11.38 Ignoring Errata on the First Silicon Revision

Early silicon revisions have more errata. Production uses the final
revision, which may still have errata. Read both sheets.

### 11.39 No Field Firmware Version Negotiation

The device accepts any firmware the server sends. An incompatible
version is applied and bricks the device. Negotiate compatibility
before accepting an update.

### 11.40 Power Loss During Flash Write

Covered in 11.33.

## 12. Response to Violation

If a previous response violated a rule here:

```
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

No justification. No apology paragraph. Fix and move on.
