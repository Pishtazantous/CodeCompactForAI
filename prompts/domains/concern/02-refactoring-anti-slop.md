---
id: 02-refactoring-anti-slop
title: "Refactoring Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: concern
version: 1
---

# Refactoring Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules,
minimal-diff guidance, and the general prohibition on mixing refactors
with behavior changes are not repeated here. This layer governs changes
whose purpose is to improve structure while preserving behavior.

## 1. Applicability

Send this layer when the requested outcome is one of these:

- improve readability, cohesion, or naming;
- remove duplication, dead structure, or accidental complexity;
- change an internal boundary without changing the external contract;
- prepare code for a later change;
- replace an implementation behind a stable interface.

Do not send it for a feature whose intended behavior is new. Implement
the feature with the existing design. Suggest refactoring separately if
the current design blocks the feature.

A refactor is valid only when the intended outcome and behavior boundary
are named. "Make it cleaner" is not a sufficient contract.

## 2. Refactoring Contract

### 2.1 Define Preserved Behavior

1. List observable inputs, outputs, side effects, errors, and timing
   guarantees that callers may rely on.
2. Distinguish public contracts from incidental implementation details.
3. Record the verification command that currently exercises the area.
4. Add characterization coverage when important behavior is unverified.
5. Do not promise compatibility for undocumented accident unless the
   repository treats it as a supported contract.

### 2.2 Define the Improvement

1. Name the concrete smell: duplicated rule, unclear boundary, deep
   branch, excess coupling, poor name, or misplaced responsibility.
2. State the expected reduction in cognitive or change cost.
3. Keep unrelated cleanup out of the scope.
4. If the result requires new abstraction, show real current usages.
5. If no measurable or reviewable improvement results, do not refactor.

## 3. Characterization Tests

### 3.1 Capture Behavior Before Moving It

1. Test through the same boundary production callers use when possible.
2. Cover normal behavior, boundary inputs, and important failures.
3. Freeze only the contract that should remain stable.
4. Avoid asserting private sequence, names, or implementation structure.
5. Run characterization tests before moving code and again afterward.

A characterization test may document undesirable behavior. It becomes
a change test only after the user authorizes a behavior change.

### 3.2 Handle Legacy Code

1. Add a narrow test at the nearest stable boundary.
2. Use a seam to isolate time, network, storage, or nondeterminism.
3. Do not redesign the whole module merely to make the first test easy.
4. Use a snapshot only when the reviewed output is part of the contract.
5. Decode unclear recorded output into explicit assertions when feasible.

## 4. Small Steps

### 4.1 Change One Structural Axis at a Time

1. Separate moves, renames, extraction, and logic simplification.
2. Run the focused verification after each meaningful step.
3. Keep intermediate states buildable when practical.
4. Avoid large rename-and-restructure changes across unrelated modules.
5. Stop immediately when behavior changes without approval.

### 4.2 Review the Diff

1. Check that deletion is as intentional as addition.
2. Reject hidden behavior changes in condition reordering or defaulting.
3. Check error types, return shapes, null handling, and ordering.
4. Check public exports and dependency direction.
5. Use reversible commits when the repository workflow permits.

## 5. Strangler and Boundary Migration

### 5.1 Use Strangler for Live Migration

1. Define the stable interface that both implementations satisfy.
2. Route one bounded use case to the replacement.
3. Compare outputs and side effects with the existing implementation.
4. Increase traffic or scope only after evidence supports it.
5. Remove the old path after usage reaches zero and data is reconciled.

### 5.2 Make Seams Deliberate

1. Introduce an adapter at the external or volatile boundary.
2. Keep domain decisions independent from the transport mechanism.
3. Do not create an interface for a trivial concrete helper.
4. Do not route production through a test-only abstraction.
5. Ensure rollback does not require unsafe mixed writes or dual execution.

### 5.3 Strangler Rules

1. Do not call a rewrite a Strangler migration.
2. Do not migrate all callers before proving one route.
3. Do not keep two sources of truth indefinitely.
4. Do not hide partial migration behind a feature flag without an owner
   and removal date.
5. Reconcile writes and verify consistency before deleting the old path.

## 6. Behavior Preservation

### 6.1 Preserve More Than Return Values

1. Preserve exception or failure modes required by callers.
2. Preserve ordering when consumers depend on it.
3. Preserve side-effect timing unless timing is explicitly changing.
4. Preserve mutation, ownership, and visibility of shared objects.
5. Preserve caching, idempotency, and transaction boundaries.

### 6.2 Treat Observability as Behavior

1. Keep stable log events and fields required by operations.
2. Keep metric names and labels used by dashboards or alerts.
3. Keep trace context across replaced boundaries.
4. Do not change configuration precedence silently.
5. Update consumers before renaming an operational contract.

## 7. Domain-Specific Rules

### 7.1 Refactoring Rules

1. Write the preserved-behavior contract before editing.
2. Use characterization tests at the most stable available boundary.
3. Change structure in small, independently verifiable steps.
4. Use Strangler migration only for incremental replacement.
5. Revert an unexplained behavior change instead of expanding scope.
6. Keep cleanup separate from intentional behavior change.

## Domain-Specific Anti-Patterns

### 8.1 Rewrite With a Compatibility Excuse

BAD:
```typescript
export function parseSettings(input: string): Settings {
  return JSON.parse(input, (key, value) => {
    if (key === "retries") return Number(value);
    return value;
  });
}
```
The parser rewrite changes accepted inputs and internal structure together.
GOOD:
```typescript
export function parseSettings(input: string): Settings {
  const raw = JSON.parse(input) as RawSettings;
  return mapSettings(raw);
}
```
The parser behavior stays stable while its responsibility is extracted.

### 8.2 Extraction Without Characterization

BAD:
```javascript
const totalBefore = 100;
const discount = calculateDiscount(totalBefore, customer);
export { discount };
```
Moving code without a characterization test leaves behavior unguarded.
GOOD:
```javascript
test.each([
  [100, "standard", 100],
  [100, "member", 90],
])("preserves discount for %s", (total, tier, expected) => {
  expect(calculateDiscount(total, tier)).toBe(expected);
});
```
Characterization coverage protects the public discount boundary before the move.

### 8.3 Big-Bang Cleanup

BAD:
```typescript
renameClass(sourceDir, "Service", "UseCase");
moveFiles(sourceDir, targetDir);
rewriteImports(sourceDir, targetDir);
rewriteExports(targetDir);
```

GOOD:
```typescript
const compatibilityExport = renameClass(
  "src/orders/OrderService.ts",
  "OrderService",
  "CreateOrder",
);
verifyFocusedTests();
export { compatibilityExport };
```

The batch cleanup makes failures hard to localize and review. The focused rename keeps a compatibility export and a verification checkpoint.

### 8.4 Strangler With Two Sources of Truth

BAD:
```python
legacy.save(order)
new_adapter.save(order)
```
Two writers create conflicting sources of truth during migration.
GOOD:
```python
writer = new_writer if order.use_new_path else legacy_writer
  writer.save(order)
```
One authoritative write path keeps the migration reversible.

## 9. Response to Violation

If a previous response violated this layer:

```text
In the previous response, [specific refactoring rule] was violated. Correction:
[behavior-preserving corrected step]
```

Name the unpreserved behavior when known. Do not justify the mixed
change, and do not begin an additional refactor while correcting it.
