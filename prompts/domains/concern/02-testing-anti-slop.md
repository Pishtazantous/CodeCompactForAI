---
id: 02-testing-anti-slop
title: "Testing Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: concern
version: 1
---
# Testing Anti-Slop Layer
Layered under `_universal/00-master-anti-slop.md`. Universal rules and
claims about correctness are not repeated here. This layer defines the
testing concern: evidence that a risky behavior remains reliable as the
code changes.
## 1. Testing Concern Baseline
Send this layer when a change introduces or modifies a test, a fixture,
a test seam, a build pipeline test stage, or behavior whose regression
would affect users or operations.
Do not send it for a documentation-only edit with no executable
behavior. A repository without a test command is not exempt: the
baseline then begins with discovering the existing verification path
before proposing a framework.
The baseline for every change is:
1. Identify the changed behavior and its observable contract.
2. Run the narrowest relevant existing verification command.
3. Add or update a regression test when the changed behavior is not
   already protected.
4. Run the affected test group and the repository quality gates.
5. Report commands and outcomes without inventing execution.
Testing is not a substitute for inspecting the implementation, and
this layer does not repeat the universal requirement to verify claims.
## 2. Test Portfolio Shape
### 2.1 Match the Pyramid to Risk
1. Keep most tests fast and deterministic near the domain boundary.
2. Use integration tests for real serialization, persistence,
   transactions, and component contracts that mocks would distort.
3. Use a small number of end-to-end tests for critical user journeys.
4. Do not copy one shape to every project. A library, a data pipeline,
   and a browser product have different expensive boundaries.
5. Measure the suite's slowest and least reliable groups before adding
   more end-to-end coverage.
A pyramid is a cost model, not a quota. A tiny pure function does not
need three layers. A payment transition may deserve explicit coverage
at every relevant boundary.
### 2.2 Make the Pyramid Measurable
1. Record the count, runtime, and failure rate of each test layer.
2. Keep the default developer feedback loop bounded by the repository's
   agreed budget.
3. Move slow coverage to a later stage only if the stage still runs
   somewhere before release.
4. Do not label a test integration or end-to-end based on file location.
5. Report slow groups with names and timings so the shape can be tuned.
## 3. Test Value
### 3.1 Coverage Is an Inventory, Not Proof
1. Use coverage to find untested branches, not as the sole success gate.
2. Require a protected assertion for the changed behavior.
3. Reject tests that execute a line but assert nothing meaningful.
4. Review uncovered critical paths when coverage falls below baseline.
5. Exclude generated code only with a narrow, documented rule.
### 3.2 Test the Contract
1. Name tests after the rule, risk, or scenario they protect.
2. Assert public outputs, state transitions, emitted messages, and
   durable side effects.
3. Prefer realistic boundary objects over assertions on private calls.
4. Include one negative case for every destructive or privileged path.
5. Make the failure message identify the violated contract.
### 3.3 Avoid Duplication
1. Extract setup only when it hides non-obvious setup or removes
   meaningful duplication.
2. Keep scenario-specific assertions visible in the scenario.
3. Do not build a generic DSL that makes test intent harder to read.
4. Do not share mutable fixtures across unrelated tests.
5. Allow focused duplication when it makes the protected rule clearer.
## 4. Fixtures and Test Data
### 4.1 Explicit Lifecycle
1. Build the smallest fixture that satisfies the behavior under test.
2. Declare ownership: inline, function, class, module, or suite scope.
3. Restore global configuration, clocks, environment variables, and
   module state after every test.
4. Make setup idempotent or recreate it per test.
5. Prefer builders when many valid objects share required fields.
### 4.2 Stable and Meaningful Data
1. Use fixed dates, identifiers, and amounts where a stable result is
   expected.
2. Control randomness through an injected seed or deterministic fake.
3. Use time zones and locales explicitly in locale-sensitive tests.
4. Avoid fixtures copied from production without the required fields.
5. Keep binary and large fixtures outside source when practical, with
   deterministic retrieval or generation.
### 4.3 Isolation Without Theater
1. Disable network access by default for unit tests.
2. Replace external services with fakes at a stable interface boundary.
3. Use real databases or queues when the behavior being tested is the
   integration itself.
4. Clean created records and files even when an assertion fails.
5. Do not hide failures by retrying or resetting state silently.
## 5. Flakiness and Isolation
### 5.1 Classify Every Flake
1. Reproduce the failure before changing the test.
2. Label the cause as timing, shared state, ordering, dependency,
   randomness, environment, or test design.
3. Fix the source of nondeterminism, not the visible symptom.
4. Quarantine only with an owner, a reason, and a removal condition.
5. Track repeat failures in continuous integration.
### 5.2 Make Execution Repeatable
1. Do not depend on test order unless the contract explicitly requires it.
2. Avoid real sleeps; synchronize on observable state.
3. Use bounded timeouts with failure diagnostics.
4. Avoid port collisions, shared database names, and fixed temporary paths.
5. Run the suspected group repeatedly in randomized order when fixing
   isolation.
### 5.3 Concurrency Tests
1. Control scheduling when the behavior depends on interleaving.
2. Use barriers, channels, or fake clocks instead of timing assumptions.
3. Assert eventual state with bounded polling only when the contract is
   asynchronous.
4. Reproduce races in repeated runs with a controlled stress factor.
5. Do not call a race test reliable without repeated execution evidence.
## 6. Domain-Specific Rules
### 6.1 Testing Rules
1. Select the test level from risk, speed, and boundary realism.
2. Write a regression case before or with a behavior fix.
3. Use fixtures with explicit ownership and cleanup.
4. Eliminate order dependence and uncontrolled time.
5. Evaluate coverage as a map, then assess the value of assertions.
6. Keep slow critical journeys small and visible.
### 6.2 Refactoring Rules
1. Refactoring rules are separate from this testing layer.
2. When tests are part of a refactor, preserve the observable contract.
3. Do not delete a test solely because its implementation references a
   private structure unless an equivalent public-contract test replaces it.
## Domain-Specific Anti-Patterns
### 7.1 Coverage Theater
BAD:
```python
def test_discount_service():
    assert calculate_discount(order) is not None
```
The assertion executes code without protecting a business outcome.
GOOD:
```python
def test_discount_service_applies_contracted_rate():
    order = make_order(subtotal=10_000, discount_rate="10%")
    result = calculate_discount(order)
    assert result.amount == 1_000
    assert order.currency == "EUR"
```
The assertion protects the exact business outcome and boundary cases.
### 7.2 Shared Mutable Fixture
BAD:
```javascript
let account;
beforeAll(() => {
  account = createAccount({ balance: 100 });
});
test("deposit adds money", () => {
  account.balance += 50;
});
test("withdrawal starts from a known balance", () => {
  expect(withdraw(account, 20).balance).toBe(80);
});
```
A shared mutable object leaks state across test order.
GOOD:
```javascript
test("withdrawal starts from a known balance", () => {
  const account = createAccount({ balance: 100 });
  expect(withdraw(account, 20).balance).toBe(80);
});
```
The fixture is isolated and its lifecycle is explicit.
### 7.3 Sleeping and Retrying
BAD:
```python
def test_worker_queues_event():
    worker.start()
    time.sleep(2)
    assert queue.size() == 1
```
A fixed sleep hides scheduling and dependency latency.
GOOD:
```python
def test_worker_queues_event():
    worker.start()
    assert queue.wait_for_size(1, timeout=1)
```
The test synchronizes on observable work with a bounded wait.
### 7.4 One Giant End-to-End Pyramid
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
The journey does not isolate the business rule from wiring.
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
The rule is tested directly; the journey remains for integration wiring.
### 7.5 A Fake That Reimplements Production
BAD:
```python
def fake_user_response(user):
    return {"id": user["id"], "name": user["name"].title()}
```
The hand-built response repeats production mapping logic.
GOOD:
```python
USER_RESPONSE = {
    "id": "usr_42",
    "name": "Ada Lovelace",
    "permissions": ["invoices:read"],
}
```
The fixture preserves the response contract without duplicating production mapping.
## 8. Response to Violation
If a previous response violated this layer:
```text
In the previous response, [specific testing rule] was violated. Correction:
[corrected test or verification]
```
State only the violated rule, the correction, and any verification still
required. Do not defend the suite or add unrelated test work.
