---
id: 02-embedded-anti-slop
title: "Embedded Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: delivery
version: 1
---
# Embedded Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules are not
repeated. Hardware-specific toolchain rules belong to the project.

## 1. Stack Assumptions

**1.1 Define the target.** Identify MCU or SoC, core, compiler, memory map,
clock, peripherals, power mode, and update mechanism.

**1.2 Use the existing HAL.** Reuse the repository's drivers, RTOS primitives,
logging, and build system before adding a hardware abstraction.

**1.3 State timing budgets.** Define deadlines for control loops, interrupts,
communication, and logging on the slowest supported target.

## 2. Domain Contracts

**2.1 Memory is finite.** Every allocation, stack, buffer, queue, and DMA
transfer has a bounded worst case.

**2.2 Interrupts stay short.** Long work belongs in tasks or main loops;
shared state is protected and deterministic.

**2.3 Watchdogs recover safely.** A reset must preserve a diagnosable state
and avoid repeating a hazardous action without a guard.

**2.4 Firmware is versioned.** Hardware compatibility, boot image, config,
and migration rules are explicit.

## 3. Domain-Specific Rules

**3.1 Analyze worst-case memory.** Track heap high-water mark, stack
headroom, fragmentation risk, and buffer lifetime; never assume free heap.

**3.2 Mark ISR constraints.** Avoid blocking, unbounded loops, allocation,
logging with locks, and calls into non-reentrant code from interrupts.

**3.3 Protect shared state.** Use the project's mutex, queue, atomic, or
critical-section pattern with a documented lock order.

**3.4 Bound queues and retries.** A peripheral or network failure must not
grow memory or block the control loop.

**3.5 Debounce real hardware.** Poll and edge transitions have stable timing;
software filtering must not erase legitimate pulses.

**3.6 Handle brownout and reset.** Persist only validated, bounded state and
run a self-test before normal control resumes.

**3.7 Measure current and timing.** Instrument representative worst cases
and verify with target hardware, not only simulation.

**3.8 Make firmware updates recoverable.** Use the bootloader contract,
signature or integrity policy, dual-bank or rollback strategy, and power-loss
behavior required by the product.

**3.9 Keep configuration validated.** Reject unsupported clock, voltage,
calibration, and feature combinations at startup.

**3.10 Test fault injection.** Cover sensor stuck values, bus timeout,
overflow, watchdog reset, brownout, flash exhaustion, and thermal limits.

**3.22 Reserve worst-case resources.** Include interrupt nesting, callback depth, driver buffers, and recovery paths in memory budgets.

**3.23 Make timing measurable.** Define clock source, units, deadline, tolerance, and timeout behavior for each real-time path.

**3.24 Validate hardware inputs.** Reject unsupported clocks, voltages, calibration, sensor ranges, and peripheral combinations at startup.

**3.25 Keep reset recovery safe.** A reset records a reason, enters a safe state, and cannot repeat hazardous output without a guard.

**3.26 Test production behavior.** Validate sustained load, brownout, thermal limits, flash endurance, power loss, and firmware update interruption.

**3.30 Bound firmware resources.** Stack, heap, queues, interrupts, and DMA have measured worst-case limits.

**3.31 Protect safety state.** Calibration, watchdog, emergency stop, and recovery states are validated and persistent.

**3.32 Verify target hardware.** Timing, power, thermal, brownout, endurance, and update interruption are measured on target.

## 4. Domain-Specific Anti-Patterns

### 4.1 Unbounded Blocking Loop

BAD:
```c
while (!sensor_ready()) {
    process_all_work();
}
```

GOOD:
```c
if (wait_sensor_ready(SENSOR_TIMEOUT_MS) != SENSOR_OK) {
    enter_degraded_mode();
}
```

The loop has a deadline and a safe state.

### 4.2 Dynamic Allocation in Interrupt Context

BAD:
```c
void ADC_IRQHandler(void) {
    sample = malloc(sizeof(sample_t));
}
```

GOOD:
```c
void ADC_IRQHandler(void) {
    sample = ring_push_from_isr(&samples, value);
}
```

The interrupt path uses bounded, non-blocking storage.

### 4.3 Watchdog Reset Loop

BAD:
```c
watchdog_enable(100);
motor_start();
```

GOOD:
```c
if (!safe_calibration_persisted()) {
    watchdog_disable();
    enter_maintenance_mode();
}
```

A reset cannot repeatedly energize unsafe hardware.

**3.11 Reserve stack headroom.** Track the deepest measured call chain, interrupt nesting, and exception paths; do not size stacks from idle usage.

**3.12 Make timing explicit.** Define clock source, wraparound handling, deadline units, and tolerance for control and communication timing.

**3.13 Validate calibration.** Reject unsafe or expired calibration values and preserve the last known safe configuration when validation fails.

**3.14 Bound flash wear.** Batch writes, honor erase limits, and place persistent updates only where the device contract permits them.

**3.15 Verify production hardware.** Run timing, current, brownout, temperature, and recovery tests on representative boards and peripherals.

**3.16 Make recovery observable.** Record reset reason, firmware version, boot outcome, and safe diagnostic counters within the memory budget.

**3.17 Keep configuration atomic.** A configuration update either activates completely or leaves the previous valid configuration active.

**3.18 Separate safety from convenience.** Emergency stop, watchdog, and power controls cannot be disabled by an unprivileged command.

**3.19 Bound peripheral access.** Timeouts and error states prevent one unavailable peripheral from blocking unrelated control paths.

**3.20 Verify units and scaling.** Convert sensor counts, clocks, temperatures, and pressures at a documented boundary with checked arithmetic.

**3.21 Test sustained operation.** Exercise thermal limits, memory retention, power cycles, and update interruption over the intended lifetime.

## 5. Response to Violation

If a prior response violated this layer, name the memory, ISR, timing,
watchdog, or update risk and show the corrected bounded design. Do not claim
hardware timing or reset recovery without target validation.
