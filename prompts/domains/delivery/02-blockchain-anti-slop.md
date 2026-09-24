---
id: 02-blockchain-anti-slop
title: "Blockchain Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: delivery
version: 1
---
# Blockchain Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules are not
repeated. Contract security details require the project's security review.

## 1. Stack Assumptions

**1.1 Identify the chain and VM.** Confirm network, compiler version, contract
framework, account model, fee market, and finality assumptions.

**1.2 Map upgrade authority.** Name who can upgrade, pause, mint, change
roles, and migrate storage; document emergency powers.

**1.3 Follow existing conventions.** Reuse interfaces, errors, events,
libraries, deployment scripts, and test fixtures already in the repository.

## 2. Domain Contracts

**2.1 State transitions are explicit.** Define preconditions, postconditions,
authorization, and invariants for every public or external function.

**2.2 External calls are hazards.** Use the framework's pull-payment or
checks-effects-interactions pattern when a call can reenter.

**2.3 Gas is part of correctness.** Bound loops, storage writes, calldata,
and external calls; avoid unbounded user-controlled iteration.

**2.4 Events are interfaces.** Emit stable, indexed, non-secret events for
consumers and define their ordering and versioning.

**2.5 Upgrades preserve state.** Use a reviewed storage layout, initializer,
reentrancy policy, and migration test before replacing code.

## 3. Domain-Specific Rules

**3.1 Check arithmetic and units.** Use safe math, explicit rounding, and
domain-specific units; do not rely on unchecked multiplication.

**3.2 Reentrancy checks cover cross-function paths.** Guard shared state,
follow lock ordering, and test callbacks into every reachable external call.

**3.3 Minimize privileged roles.** Separate admin, pauser, upgrader, and
operator duties; document multisig and timelock requirements.

**3.4 Guard emergency controls.** Pausing must be observable, bounded, and
paired with a tested recovery path; never leave an indefinite silent pause.

**3.5 Validate zero-address and token behavior.** Handle zero amounts,
unsupported tokens, fee-on-transfer tokens, and failed transfers explicitly.

**3.6 Avoid oracle trust by accident.** Bound freshness, source, decimals,
and failure mode for every external price or asset reference.

**3.7 Test upgrade invariants.** Compare storage, roles, events, and user
balances across upgrade fixtures and rollback targets.

**3.8 Measure gas before release.** Record deployment and critical-path gas
under supported compiler and optimizer settings.

**3.9 Protect keys operationally.** Use the existing signer boundary; never
embed private keys, mnemonics, or unverified admin URLs.

**3.10 Simulate hostile ordering.** Fuzz callbacks, concurrent users,
partial reverts, fee spikes, and failed external calls.

**3.22 Define upgrade compatibility.** Storage layout, initialization, roles, events, and rollback are tested before implementation replacement.

**3.23 Bound administrative actions.** Upgrade, pause, mint, rescue, and migration paths have narrow roles, limits, and event evidence.

**3.24 Handle economic failure.** Token behavior, fees, decimals, liquidity, oracle freshness, and chain reorganization are explicit.

**3.25 Test cross-function reentrancy.** Every external callback, batch, callback, and administrative path reaches the same guards.

**3.26 Measure release settings.** Build and test with the declared compiler, optimizer, metadata, VM version, and gas profile.

## 4. Domain-Specific Anti-Patterns

### 4.1 State Change Before External Call

BAD:
```solidity
function withdraw() external {
    balance[msg.sender] = 0;
    token.transfer(msg.sender, balanceOf(msg.sender));
}
```

GOOD:
```solidity
function withdraw() external nonReentrant {
    uint256 amount = balance[msg.sender];
    balance[msg.sender] = 0;
    token.transfer(msg.sender, amount);
}
```

The external callback cannot reenter the guarded balance path.

### 4.2 Unbounded Loop

BAD:
```solidity
for (uint256 i = 0; i < users.length; i++) {
    distribute(users[i]);
}
```

GOOD:
```solidity
uint256 processed = distributeBatch(users, MAX_BATCH);
emit Progress(processed);
```

A bounded batch has a continuation path.

### 4.3 Upgrade Without Layout Review

BAD:
```solidity
function migrateStorage(address newImplementation) external onlyRole(UPGRADER) {
    require(storageLayoutCompatible(), "layout");
    _authorizeUpgrade(newImplementation);
}
```

GOOD:
```solidity
function migrateStorage(address newImplementation) external onlyRole(UPGRADER) {
    require(storageLayoutCompatible(), "layout");
    _initializeNewState();
    _authorizeUpgrade(newImplementation);
}
```

State compatibility is a release gate, not an afterthought.

**3.11 Emit events after state commits.** Consumers must not interpret an event as durable state before the corresponding state transition succeeds.

**3.12 Bound batch operations.** Set maximum batch size and continuation semantics so a user cannot force an unrecoverable gas failure.

**3.13 Check upgrade authorization.** Every privileged migration and role change verifies the current authority and emits an auditable event.

**3.14 Test against compiler settings.** Build and test with the declared optimizer, metadata hash, and VM version before deployment.

**3.15 Review economic assumptions.** Document price, fee, liquidity, and reward assumptions that can make safe code economically unsafe.

**3.16 Separate roles from code paths.** Role checks occur at every privileged entry point, including batch, callback, and administrative functions.

**3.17 Make event schemas stable.** Event names, field types, indexing, and nullability have compatibility rules for downstream consumers.

**3.18 Handle chain reorgs.** Finality assumptions and confirmation depth are explicit for bridges, staking, oracles, and irreversible actions.

**3.19 Bound rescue and migration paths.** Recovery code has a limited scope, explicit authorization, and a tested pre-upgrade plan.

**3.20 Review decimals and tokens.** Reject unsupported token behavior and verify actual received amounts before updating accounting state.

**3.21 Exercise adversarial tests.** Include reentrant callbacks, malicious receivers, fee spikes, block limits, and failed upgrade initialization.

## 5. Response to Violation

If a prior response violated this layer, name the invariant, reentrancy, gas,
role, or upgrade risk and show the corrected contract behavior. Do not claim
an audit, deployment, or on-chain verification without evidence.
