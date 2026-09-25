---
id: 02-testing-anti-slop
title: "Testing Anti-Slop Layer"
lang: en
depends_on: ["_universal/00-style-guide.md", "_universal/00-master-anti-slop.md"]
category: domain
domain_type: concern
version: 2
---

# Testing Anti-Slop Layer

This file defines behavioral contracts specific to the testing concern. It sits in the concern layer, below the universal anti-slop rules and alongside other cross-cutting concerns. It covers verification baseline, test portfolio shape, test value, fixture integrity, flakiness elimination, and execution reliability. It does not cover domain-specific testing rules (database query testing, API contract testing, UI component testing), framework-specific test runners (Jest, pytest, Go testing), language-specific test idioms (see language files), or universal claim verification rules (see `00-master-anti-slop.md` MAS-007).

Testing is evidence that a risky behavior remains reliable as the code changes. It is not a substitute for inspecting the implementation.

## When This File Applies

This file MUST be sent when at least one of the following objective criteria is met:

- A change introduces or modifies a test, a fixture, or a test seam.
- A change modifies a build pipeline test stage.
- A change modifies behavior whose regression would affect users or operations.
- A change introduces a new executable behavior that is not yet protected by a test.

This file does NOT apply to: documentation-only edits with no executable behavior, configuration-only changes with no behavioral impact, or pure formatting changes.

A repository without a test command is not exempt: the baseline begins with discovering the existing verification path before proposing a framework.

## Scope

This file applies to all test levels (unit, integration, end-to-end) across all languages and frameworks. The principles are language-agnostic and framework-agnostic. The examples use Python and JavaScript syntax where illustrative. Framework-specific test runner configuration (Jest, pytest, Go testing, JUnit) lives in framework files. Domain-specific testing rules (database migration testing, API contract testing) live in delivery files.

## Concern Budgets

Testing concern operates within these measurable thresholds:

| Concern | Threshold | Verification Method | Rule |
|---|---|---|---|
| Developer Feedback Loop | Bounded by repository's agreed budget | CI stage timing | TEST-008 |
| Uncovered Critical Paths | Reviewed when coverage falls below baseline | Coverage report review | TEST-011 |
| Flake Reproduction | 100% reproducible before fix | Repeated runs in CI | TEST-021 |
| Test Failure Diagnosis | Identifies violated contract | Test failure message review | TEST-014 |
| Slow Test Groups | Named and timed in reports | CI report analysis | TEST-010 |

## Rule Severity

Severity follows `_universal/00-style-guide.md`. Violations in this file result in unreliable verification, false confidence, or wasted development time.

## Contracts

A testing concern commits to five contracts. The table below maps each contract to the rules that enforce it.

| Contract | Description | Enforced By |
|---|---|---|
| Verification Baseline | Changed behavior is identified, tested, and reported without inventing execution. | TEST-001 to TEST-005 |
| Test Portfolio Balance | Test pyramid matches risk, is measurable, and tuned. | TEST-006 to TEST-010 |
| Test Value | Tests protect contracts, not just execute lines. | TEST-011 to TEST-015 |
| Fixture Integrity | Fixtures are isolated, stable, and cleaned up. | TEST-016 to TEST-020 |
| Execution Reliability | Tests are repeatable, non-flaky, and properly isolated. | TEST-021 to TEST-028 |

## Verification Baseline

### TEST-001 — Behavior Identification

**MUST**

Before any test-related change, the changed behavior and its observable contract MUST be identified. The contract is what the user or downstream system depends on.

### TEST-002 — Narrowest Verification First

**MUST**

The narrowest relevant existing verification command MUST be run first. Running the entire test suite before identifying the affected scope is prohibited.

### TEST-003 — Regression Test Addition

**MUST**

When the changed behavior is not already protected by an existing test, a regression test MUST be added or updated. A behavior change without a protecting test is a risk.

### TEST-004 — Test Group Execution

**MUST**

The affected test group and the repository quality gates MUST be run after the change. Partial verification is not sufficient.

### TEST-005 — Execution Report Integrity

**MUST NOT**

Test commands and outcomes MUST be reported accurately. Inventing execution results is prohibited.

See MAS-007 in `_universal/00-master-anti-slop.md`.

## Test Portfolio Shape

### TEST-006 — Risk-Based Pyramid

**MUST**

The test pyramid MUST match the risk profile:

1. Most tests MUST be fast and deterministic near the domain boundary.
2. Integration tests MUST be used for real serialization, persistence, transactions, and component contracts that mocks would distort.
3. A small number of end-to-end tests MUST cover critical user journeys.

A pyramid is a cost model, not a quota. A tiny pure function does not need three layers. A payment transition may deserve explicit coverage at every relevant boundary.

### TEST-007 — Portfolio Diversity

**MUST NOT**

One test shape MUST NOT be copied to every project. A library, a data pipeline, and a browser product have different expensive boundaries. The portfolio MUST be shaped by the project's actual risk and cost profile.

### TEST-008 — Feedback Loop Budget

**MUST**

The default developer feedback loop MUST be bounded by the repository's agreed budget. A feedback loop that exceeds the budget discourages testing.

### TEST-009 — Slow Test Stage Management

**MUST**

Slow coverage MUST be moved to a later stage only if the stage still runs somewhere before release. Tests removed from all stages are deleted tests.

### TEST-010 — Layer Measurement

**MUST**

The count, runtime, and failure rate of each test layer MUST be recorded. Slow groups MUST be reported with names and timings so the shape can be tuned. Tests MUST NOT be labeled integration or end-to-end based on file location alone.

## Test Value

### TEST-011 — Coverage as Inventory

**MUST NOT**

Coverage MUST NOT be used as the sole success gate. Coverage MUST be used to find untested branches. A protected assertion for the changed behavior MUST be required. Tests that execute a line but assert nothing meaningful MUST be rejected. Uncovered critical paths MUST be reviewed when coverage falls below baseline. Generated code MUST only be excluded with a narrow, documented rule.

### TEST-012 — Contract-Based Naming

**MUST**

Tests MUST be named after the rule, risk, or scenario they protect. Generic names like `test_1` or `test_function` are prohibited.

### TEST-013 — Output Assertion

**MUST**

Tests MUST assert public outputs, state transitions, emitted messages, and durable side effects. Assertions on private calls MUST NOT be preferred over realistic boundary objects.

### TEST-014 — Negative Case Requirement

**MUST**

Every destructive or privileged path MUST include one negative case. The failure message MUST identify the violated contract.

### TEST-015 — Duplication Discipline

**SHOULD**

Setup SHOULD be extracted only when it hides non-obvious setup or removes meaningful duplication. Scenario-specific assertions SHOULD remain visible in the scenario. Generic DSLs that make test intent harder to read SHOULD NOT be built. Mutable fixtures MUST NOT be shared across unrelated tests. Focused duplication MAY be allowed when it makes the protected rule clearer.

## Fixtures and Test Data

### TEST-016 — Minimal Fixture

**MUST**

The smallest fixture that satisfies the behavior under test MUST be built. Over-sized fixtures obscure the test's intent.

### TEST-017 — Fixture Ownership

**MUST**

Fixture ownership MUST be declared: inline, function, class, module, or suite scope. Ownership ambiguity causes cross-test contamination.

### TEST-018 — Global State Restoration

**MUST**

Global configuration, clocks, environment variables, and module state MUST be restored after every test. Setup MUST be idempotent or recreated per test. Builders SHOULD be used when many valid objects share required fields.

### TEST-019 — Deterministic Test Data

**MUST**

Fixed dates, identifiers, and amounts MUST be used where a stable result is expected. Randomness MUST be controlled through an injected seed or deterministic fake. Time zones and locales MUST be explicit in locale-sensitive tests. Fixtures copied from production MUST include required fields. Binary and large fixtures SHOULD be outside source when practical, with deterministic retrieval or generation.

### TEST-020 — Test Isolation

**MUST**

Network access MUST be disabled by default for unit tests. External services MUST be replaced with fakes at a stable interface boundary. Real databases or queues MUST be used when the behavior being tested is the integration itself. Created records and files MUST be cleaned even when an assertion fails. Failures MUST NOT be hidden by retrying or resetting state silently.

## Flakiness and Isolation

### TEST-021 — Flake Classification

**MUST**

Every flake MUST be reproduced before changing the test. The cause MUST be labeled as timing, shared state, ordering, dependency, randomness, environment, or test design. The source of nondeterminism MUST be fixed, not the visible symptom. Quarantine MUST only occur with an owner, a reason, and a removal condition. Repeat failures MUST be tracked in continuous integration.

### TEST-022 — Flake Source Fix

**MUST NOT**

Fixing the visible symptom of a flake without addressing the source is prohibited. Adding retries or increasing timeouts without diagnosis is a cover-up, not a fix.

### TEST-023 — Quarantine Discipline

**MUST**

Quarantined tests MUST have an owner, a documented reason, and a removal condition. A quarantined test without these is a deleted test in disguise.

### TEST-024 — Repeatable Execution

**MUST NOT**

Tests MUST NOT depend on test order unless the contract explicitly requires it. Real sleeps MUST be avoided; synchronization MUST occur on observable state. Timeouts MUST be bounded with failure diagnostics. Port collisions, shared database names, and fixed temporary paths MUST be avoided. The suspected group MUST be run repeatedly in randomized order when fixing isolation.

### TEST-025 — No Real Sleeps

**MUST NOT**

`time.sleep()`, `setTimeout()`, or equivalent real-time waits MUST NOT be used for synchronization in tests. Tests MUST synchronize on observable state with bounded waits.

Example (illustrative, Python):

BAD:
```python
def test_worker_queues_event():
    worker.start()
    time.sleep(2)
    assert queue.size() == 1
```

GOOD:
```python
def test_worker_queues_event():
    worker.start()
    assert queue.wait_for_size(1, timeout=1)
```

### TEST-026 — Bounded Timeouts

**MUST**

All waits in tests MUST have bounded timeouts. An unbounded wait can hang the test suite indefinitely. Timeout failures MUST include diagnostics identifying what was waited for.

### TEST-027 — Concurrency Test Control

**MUST**

When behavior depends on interleaving, scheduling MUST be controlled. Barriers, channels, or fake clocks MUST be used instead of timing assumptions. Eventual state assertions with bounded polling MUST only be used when the contract is asynchronous. Races MUST be reproduced in repeated runs with a controlled stress factor.

### TEST-028 — Race Test Evidence

**MUST NOT**

A race test MUST NOT be claimed reliable without repeated execution evidence. A single passing run of a concurrency test is not proof of correctness.

## AI-Specific Testing Discipline

### TEST-060 — Test Execution Fabrication Prohibition

**MUST NOT**

The assistant MUST NOT claim to have run tests, report test results, or describe test output without actual execution. Fabricated test results are indistinguishable from real ones and destroy trust in the verification process.

See MAS-007 in `_universal/00-master-anti-slop.md`.

### TEST-061 — Existing Test Discovery

**MUST**

Before writing a new test, the assistant MUST search the repository for existing tests covering the same behavior or contract. Adding parallel tests for the same contract creates maintenance burden and divergent expectations.

See MAS-035 in `_universal/00-master-anti-slop.md`.

### TEST-062 — Test Framework Restraint

**SHOULD**

The assistant SHOULD NOT introduce a new test framework, mocking library, or assertion library unless the project lacks one entirely or the existing tooling cannot express the required test. Adding parallel testing infrastructure fragments the test suite.

See MAS-038 in `_universal/00-master-anti-slop.md`.

## Anti-Patterns

### TEST-040 — Coverage Theater

**MUST NOT**

Tests that execute code without protecting a business outcome are prohibited. An assertion like `assert result is not None` executes a line but verifies nothing meaningful.

Example (illustrative, Python):

BAD:
```python
def test_discount_service():
    assert calculate_discount(order) is not None
```

GOOD:
```python
def test_discount_service_applies_contracted_rate():
    order = make_order(subtotal=10_000, discount_rate="10%")
    result = calculate_discount(order)
    assert result.amount == 1_000
    assert order.currency == "EUR"
```

### TEST-041 — Shared Mutable Fixture

**MUST NOT**

Mutable fixtures shared across tests MUST NOT be used. A shared mutable object leaks state across test order and produces order-dependent failures.

Example (illustrative, JavaScript):

BAD:
```javascript
let account;
beforeAll(() => {
  account = createAccount({ balance: 100 });
});
test("deposit adds money", () => {
  account.balance += 50;
});
```

GOOD:
```javascript
test("withdrawal starts from a known balance", () => {
  const account = createAccount({ balance: 100 });
  expect(withdraw(account, 20).balance).toBe(80);
});
```

### TEST-042 — Sleep-Based Synchronization

**MUST NOT**

Fixed sleeps for test synchronization MUST NOT be used. They hide scheduling and dependency latency. Tests MUST synchronize on observable work with a bounded wait.

### TEST-043 — Monolithic E2E Tests

**MUST NOT**

A single end-to-end test that seeds all systems, navigates, types, clicks, and asserts MUST NOT be the primary protection for a business rule. The rule MUST be tested directly; the journey remains for integration wiring.

Example (illustrative, JavaScript):

BAD:
```javascript
test("complete checkout", async () => {
  await seedAllSystems();
  await browser.goto("/");
  await browser.type("input", "value");
  await browser.click("button");
  await expect(page.locator(".result")).toHaveText("complete");
});
```

GOOD:
```javascript
test("checkout applies the active discount", () => {
  const checkout = createCheckout({
    subtotal: 10_000,
    discount: discount("10%"),
  });
  expect(checkout.total()).toBe(9_000);
});
```

### TEST-044 — Fake Reimplementation

**MUST NOT**

Hand-built fakes that repeat production mapping logic MUST NOT be used. The fixture MUST preserve the response contract without duplicating production logic.

Example (illustrative, Python):

BAD:
```python
def fake_user_response(user):
    return {"id": user["id"], "name": user["name"].title()}
```

GOOD:
```python
USER_RESPONSE = {
    "id": "usr_42",
    "name": "Ada Lovelace",
    "permissions": ["invoices:read"],
}
```

## Response to Violation

When a rule in this file is violated, report:

Violation: TEST-{NNN}
Reason: {one-line reason}
Correction: {smallest fix}

State only the violated rule, the correction, and any verification still required. Do not defend the suite or add unrelated test work.

For multiple violations, report each rule ID separately.

Do not replace a technical correction with a generic explanation.