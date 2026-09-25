---
id: 02-blockchain-anti-slop
title: "Blockchain Anti-Slop Layer"
lang: en
depends_on: ["_universal/00-style-guide.md", "_universal/00-master-anti-slop.md"]
category: domain
domain_type: delivery
version: 3
---

# Blockchain Anti-Slop Layer

This file defines behavioral contracts specific to blockchain systems and smart contracts. It sits in the delivery layer, below the universal anti-slop rules and above language-specific patterns. It covers smart contract security, gas discipline, upgradeability, oracle use, testing methodology, and deployment. It does not cover generic web security (see `02-security-critical-anti-slop.md`), language rules for Solidity or Rust (see language files), or frontend rules for dApps (see `02-frontend-anti-slop.md`).

A deployed smart contract is immutable. A bug is permanent and, if exploitable, is exploited within hours. The adversary is anonymous, funded, and automated.

## Scope

This file applies to EVM chains (Ethereum, Polygon, Arbitrum, Optimism, Base, BNB Chain, Avalanche C-Chain), Solana (Rust, Anchor), Move-based chains (Aptos, Sui), Cosmos SDK chains, and Bitcoin script (limited scope). The examples use Solidity and Rust syntax where illustrative. Solidity-specific rules (storage layout, `delegatecall` semantics) are covered here because they are part of the protocol, not just the language.

## Rule Severity

Severity follows `_universal/00-style-guide.md`.

## Contracts

A blockchain system commits to eight contracts. The table below maps each contract to the rules that enforce it.

| Contract | Description | Enforced By |
|---|---|---|
| Immutability Discipline | Bytecode cannot be changed unless explicitly designed for upgradeability. | BC-040 to BC-046 |
| Value Preservation | Funds are not lost, drained, or locked. External calls have defined failure modes. | BC-009, BC-065, BC-075 |
| Access Control | State-changing functions have explicit checks. Default is deny. | BC-016 to BC-021 |
| Gas Predictability | Users can predict gas costs. Unbounded loops are prohibited. | BC-022 to BC-027, BC-046 |
| Oracle Integrity | Data comes from manipulation-resistant sources. No single-source oracle. | BC-030 to BC-034 |
| Reentrancy Safety | External calls are analyzed for reentrancy and explicitly guarded. | BC-009 to BC-015 |
| MEV & Flash Loan Safety | Slippage, front-running, and infinite capital adversaries are mitigated. | BC-035 to BC-039 |
| Public Auditability | Source is verified, owner authority is visible, and events are emitted. | BC-056, BC-061, BC-072 |

## Reentrancy

### BC-009 — Checks-Effects-Interactions

**MUST**

State MUST be updated before any external call. An attacker's fallback function can call back into the contract before state is zeroed, draining funds.

Example (illustrative, Solidity):

BAD:
```solidity
function withdraw() external {
    uint256 amount = balances[msg.sender];
    (bool ok, ) = msg.sender.call{value: amount}("");
    require(ok);
    balances[msg.sender] = 0;  // state updated after external call
}
```

GOOD:
```solidity
function withdraw() external nonReentrant {
    uint256 amount = balances[msg.sender];
    balances[msg.sender] = 0;  // state updated first
    (bool ok, ) = msg.sender.call{value: amount}("");
    require(ok);
}
```

### BC-010 — nonReentrant Defense in Depth

**MUST**

Even with Checks-Effects-Interactions, a `nonReentrant` guard MUST be added to functions that make external calls. The modifier protects against future modifications that break the pattern.

### BC-011 — Cross-Function Reentrancy

**MUST**

Reentrancy guards MUST apply to every function that shares state with an external-calling function. An attacker can call a different function during the callback, not just the same one.

### BC-012 — Read-Only Reentrancy

**MUST**

State MUST be updated before external calls to prevent read-only reentrancy. A view function called during an external callback returning inconsistent state has drained lending protocols and DEXs.

### BC-013 — `call` Over `transfer` and `send`

**MUST NOT**

`transfer` and `send` forward a fixed 2,300 gas. A recipient with a fallback consuming more than that reverts the transfer. `call` with a reentrancy guard MUST be used instead.

### BC-014 — Token Standard Callback Awareness

**MUST**

Some token standards (ERC-777, ERC-1155) invoke callbacks on transfer. A contract that assumes ERC-20 semantics is reentrant through these tokens. The token's standard MUST be checked before integrating.

### BC-015 — Minimal Fallback Functions

**MUST**

A contract's `receive` or `fallback` function that modifies state is a reentrancy entry point. They MUST be kept minimal and strictly guarded.

## Access Control

### BC-016 — `msg.sender` Over `tx.origin`

**MUST NOT**

`tx.origin` MUST NOT be used for authentication. An attacker can trick the owner into calling a malicious contract that calls back into the victim contract. `msg.sender` MUST be used.

Example (illustrative, Solidity):

BAD: `require(tx.origin == owner, "not owner");`
GOOD: `require(msg.sender == owner, "not owner");`

### BC-017 — Explicit Modifiers

**MUST**

Every restricted function MUST have an explicit modifier. Implicit trust is prohibited.

### BC-018 — Role-Based Access Control

**SHOULD**

For contracts with multiple roles, a standard Role-Based Access Control library (e.g., OpenZeppelin's `AccessControl`) SHOULD be used. Roles MUST be granted and revoked, not hardcoded.

### BC-019 — Multisig Ownership

**MUST**

A contract's owner MUST be a multisig (e.g., Safe, Gnosis). A single EOA is a single point of failure and compromise. At least three keys SHOULD be in hardware wallets, geographically distributed.

### BC-020 — Renounce Ownership Discipline

**MUST**

Renouncing ownership removes the ability to fix bugs. It MUST only be done when the contract is intended to be immutable and the logic is fully audited.

### BC-021 — Hidden Owner Prohibition

**MUST NOT**

A contract with a backdoored admin function (mint without limit, pause, self-destruct) is an exit scam. Hidden owners MUST NOT exist. Users MUST be able to see the risk without reading the code.

## Gas and Storage

### BC-022 — Storage Minimization

**MUST**

Writing a new storage slot costs 20,000 gas; reading costs 2,100. Storage writes MUST be minimized.

### BC-023 — Struct Field Packing

**SHOULD**

Solidity packs fields into 32-byte slots. Struct fields SHOULD be ordered to maximize packing and minimize wasted bytes.

### BC-024 — `calldata` Over `memory`

**MUST**

For external function parameters, `calldata` MUST be used instead of `memory` to avoid unnecessary copying.

### BC-025 — `immutable` and `constant` Usage

**MUST**

Values that do not change MUST be declared as `immutable` (set in constructor) or `constant` (compile-time). They are not stored in storage slots.

### BC-026 — Custom Errors

**SHOULD**

Custom errors (e.g., `error InsufficientBalance(...)`) SHOULD be used instead of string literals in `require` statements. They are cheaper and more informative.

### BC-027 — Unbounded Loops Prohibition

**MUST NOT**

Unbounded loops over growing arrays MUST NOT be used. A loop that eventually exceeds the block gas limit bricks the function. Pagination or a pull-based pattern MUST be used.

### BC-028 — `unchecked` Arithmetic Discipline

**MUST**

`unchecked { ++i; }` saves gas when overflow is impossible, but MUST only be used when mathematically proven. In Solidity 0.8+, arithmetic is checked by default.

### BC-029 — Storage Layout Documentation

**MUST**

For upgradeable contracts, the storage layout MUST be documented and tested. Reordering breaks all existing data.

## Oracles

### BC-030 — Single-Source Price Prohibition

**MUST NOT**

A single-source price oracle (e.g., a single DEX pool reserve) MUST NOT be used. A flash loan can move the reserve and the price in one transaction. A decentralized oracle (e.g., Chainlink) or a TWAP with a reasonable window MUST be used.

### BC-031 — TWAP Window Length

**MUST**

A TWAP (Time-Weighted Average Price) MUST use a window long enough that an attacker cannot sustain manipulation.

### BC-032 — Stale Price Checks

**MUST**

The timestamp of the oracle response MUST be checked. A price older than the configured maximum staleness MUST be rejected.

Example (illustrative, Solidity):
```solidity
(uint80 roundId, int256 price, , uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();
require(updatedAt > block.timestamp - MAX_STALENESS, "stale price");
require(answeredInRound >= roundId, "stale round");
require(price > 0, "invalid price");
```

### BC-033 — Decimal Normalization

**MUST**

Different oracles use different decimals (e.g., 8, 18). Decimals MUST be normalized before arithmetic.

### BC-034 — Circuit Breakers

**SHOULD**

If the oracle reports a price beyond a configurable deviation from the last price, the contract SHOULD pause. A sudden 90% move is either a real event or an attack; pausing saves funds.

## Flash Loans and MEV

### BC-035 — Infinite Capital Adversary Assumption

**MUST**

The adversary MUST be assumed to have infinite capital via flash loans. Any protocol that depends on an instantaneous balance or reserve without a time-weighted check is vulnerable.

### BC-036 — Slippage Protection

**MUST**

Every swap MUST have a `minAmountOut` or `maxAmountIn`. A swap without slippage protection will be sandwiched.

Example (illustrative, Solidity):

BAD: `router.swapExactTokensForTokens(amountIn, 0, path, to, deadline);`
GOOD: `router.swapExactTokensForTokens(amountIn, minAmountOut, path, to, deadline);`

### BC-037 — Commit-Reveal for Sensitive Ops

**MUST**

An auction or game that reveals bids on-chain is front-runnable. Commit-reveal with a delay MUST be used for sensitive operations.

### BC-038 — Private Mempool Usage

**SHOULD**

For critical operations, transactions SHOULD be submitted through a private mempool (e.g., Flashbots, MEV-Share) to avoid front-running. The trade-off (dependency on the private relay) MUST be documented.

### BC-039 — Swap Deadlines

**MUST**

Every swap MUST have a deadline. A swap without a deadline can be delayed indefinitely by miners/validators.

## Upgradeability

### BC-040 — Storage Layout Sanctity

**MUST**

An upgrade MUST NOT change the order or types of existing storage slots. New variables MUST be appended at the end, or a namespaced storage pattern (e.g., EIP-7201) MUST be used.

### BC-041 — Initializer Over Constructor

**MUST**

A proxy contract does not run the implementation's constructor. An `initialize` function with an `initializer` modifier MUST be used.

### BC-042 — Upgrade Authorization

**MUST**

Only a trusted address (multisig, timelock, DAO) can upgrade. An EOA MUST NOT have upgrade rights.

### BC-043 — Timelock Requirement

**SHOULD**

A timelock between proposing an upgrade and executing it SHOULD be implemented to give users time to exit. A 48-hour timelock is common for financial contracts.

### BC-044 — `selfdestruct` Prohibition

**MUST NOT**

`selfdestruct` MUST NOT be used in an implementation contract. It destroys the logic while the proxy still points to it, bricking the contract.

### BC-045 — Storage Gaps

**MUST**

For inheritance-based upgradeable contracts, a storage gap (e.g., `uint256[50] private __gap;`) MUST be left in base contracts to be consumed by future variables, preserving layout.

### BC-046 — Upgrade Fork Testing

**MUST**

Every upgrade MUST be tested against a fork of mainnet with existing state. A local test with fresh state does not catch storage collisions.

## Testing

### BC-047 — Fork Tests

**MUST**

Tests MUST run against a fork of mainnet with real state (e.g., Foundry's `--fork-url` or Hardhat's `forking`).

### BC-048 — Fuzz Testing

**MUST**

Fuzz testing (e.g., Foundry's fuzzer, Echidna) MUST be used to generate random inputs and find edge cases that hand-written tests miss.

### BC-049 — Invariant Testing

**MUST**

Invariants (e.g., "the sum of all balances equals the total supply") MUST be defined and tested against fuzzer-generated sequences.

### BC-050 — Coverage Targets

**SHOULD**

Near-100% line and branch coverage SHOULD be targeted. Every branch of every `require` and `if` MUST be tested.

### BC-051 — Static Analysis

**MUST**

Static analysis tools (e.g., Slither, Mythril) and compiler warnings MUST be run in CI.

### BC-052 — Pre-Mainnet Audit

**MUST**

A professional audit MUST be obtained for any contract holding real value. No exceptions.

### BC-053 — Bug Bounty Program

**SHOULD**

After deployment, a bug bounty (e.g., Immunefi, HackerOne) SHOULD be established. The payout MUST be high enough to exceed the attacker's expected gain.

### BC-054 — Deployed Bytecode Verification

**MUST**

The deployed bytecode MUST be verified to match the tested source. Optimizer settings or compiler versions can cause discrepancies.

## Deployment

### BC-055 — Deterministic Addresses

**SHOULD**

CREATE2 SHOULD be used for deterministic addresses across chains, allowing counterfactual deployments and cross-chain consistency.

### BC-056 — Explorer Verification

**MUST**

The source code MUST be verified on the chain's explorer (e.g., Etherscan). An unverified contract is a red flag.

### BC-057 — Public Constructor Arguments

**MUST**

Constructor arguments are public in the deployment transaction. Secrets MUST NEVER be passed as constructor arguments.

### BC-058 — Deployment Scripts as Code

**MUST**

Deployments MUST be executed via reproducible scripts (e.g., Foundry scripts, Hardhat deploy). Manual transactions in a UI are prohibited.

### BC-059 — Deployment Checklist

**MUST**

Before deployment, a strict checklist MUST be verified: tests pass on exact commit, audit findings addressed, constructor args checked, owner is multisig, contract verified, and first post-deploy action planned.

### BC-060 — Post-Deployment Verification

**MUST**

After deployment, the owner, roles, basic queries, and a small test transaction MUST be verified.

## Documentation

### BC-061 — NatSpec for Public Functions

**MUST**

Every public function MUST have NatSpec comments describing parameters, returns, and reverts. Comments are part of the contract.

### BC-062 — Owner Capabilities Documentation

**MUST**

Every privileged action the owner can perform MUST be documented. Users MUST be able to evaluate the trust they are placing.

### BC-063 — Known Limitations Documentation

**MUST**

Known limitations (unaudited components, rounding errors, deliberate trade-offs) MUST be documented.

### BC-064 — Emergency Procedures Documentation

**MUST**

A documented process for pausing, upgrading, or recovering funds in an emergency MUST exist.

## Anti-Patterns

### BC-065 — Unchecked External Calls

**MUST NOT**

External calls to tokens (e.g., `token.transfer`) MUST NOT be unchecked. Some ERC-20 tokens do not revert on failure; they return `false`. `require(token.transfer(...))` or `SafeERC20` MUST be used.

### BC-066 — Block Timestamp Randomness

**MUST NOT**

`block.timestamp` or `blockhash` MUST NOT be used as a source of randomness. Validators can influence the outcome. Chainlink VRF or a commit-reveal scheme MUST be used.

### BC-067 — Block Number Time Assumptions

**MUST NOT**

`block.number` MUST NOT be used as a reliable time source. Block times vary between chains and after upgrades.

### BC-068 — Untrusted `delegatecall`

**MUST NOT**

`delegatecall` to an untrusted or user-supplied target MUST NOT be used. The target executes with the current contract's storage and address, allowing fund drainage. An allowlist of trusted targets MUST be used.

### BC-069 — String Concatenation in `require`

**MUST NOT**

String concatenation in `require` (e.g., `require(ok, string(abi.encodePacked(...)))`) costs gas and bloats bytecode. Custom errors MUST be used.

### BC-070 — Magic Numbers

**MUST NOT**

Magic numbers (e.g., `1000000000000000000`) MUST NOT be used. Named constants or Ether units (e.g., `1 ether`) MUST be used.

### BC-071 — Floating Pragma

**MUST NOT**

Floating pragmas (e.g., `pragma solidity ^0.8.0;`) MUST NOT be used. A specific compiler version (e.g., `pragma solidity 0.8.24;`) MUST be locked to avoid compiler bugs.

### BC-072 — Missing Events

**MUST NOT**

State changes without events are invisible to indexers. Events MUST be emitted for every meaningful state change.

### BC-073 — Event Indexing Discipline

**MUST**

Only fields that consumers filter on (addresses, IDs) MUST be indexed in events. Indexing non-filterable fields wastes gas.

### BC-074 — Pause Mechanism

**MUST**

A contract holding value MUST have a pause mechanism to halt operations during an exploit. It SHOULD be time-limited or multisig-controlled.

### BC-075 — Emergency Withdrawal

**MUST**

A contract MUST have an emergency exit path to recover funds if the primary logic fails.

### BC-076 — Hardcoded Addresses

**MUST NOT**

Addresses (e.g., token addresses) MUST NOT be hardcoded for a specific chain. Constructor parameters or a chain-aware config MUST be used.

### BC-077 — Ether Transfer Handling

**MUST**

A payable function MUST either accept plain ether transfers (via `receive`/`fallback`) or explicitly document the rejection.

### BC-078 — Mapping Iteration

**MUST NOT**

Mappings are not iterable. Iterating requires a parallel array that grows with writes. This pattern MUST be used with extreme caution to avoid unbounded gas costs.

### BC-079 — Chain ID in Signatures

**MUST**

Signatures MUST include `chainId` and the contract address to prevent cross-chain replay attacks.

### BC-080 — Integer Division Rounding

**MUST NOT**

Solidity integer division truncates. Calculations that accumulate rounding errors MUST use fixed-point math libraries (e.g., PRBMath, Solmate) for financial calculations.

### BC-081 — Zero-Address Check

**MUST**

Functions setting critical addresses (e.g., treasury, owner) MUST check for `address(0)` to prevent accidental burning of funds or loss of control.

### BC-082 — `ecrecover` Return Check

**MUST**

`ecrecover` returns `address(0)` on invalid signatures. The return value MUST be checked against `address(0)` before comparing to the expected signer. OpenZeppelin's ECDSA library SHOULD be used.

### BC-083 — Malleable Signatures

**MUST NOT**

`ecrecover` accepts two valid `(s, v)` pairs for the same signature. Malleability MUST be prevented using OpenZeppelin's ECDSA with `s` range checks, or a scheme without malleability.

### BC-084 — `delegatecall` Failure Check

**MUST**

`delegatecall` returns a boolean. Ignoring it hides failures. The return value MUST be checked and required to be true.

### BC-085 — Unbounded `approve` Allowance

**SHOULD NOT**

An `approve` with `type(uint256).max` SHOULD NOT be used if the spender is not fully trusted. Limited allowances SHOULD be preferred.

### BC-086 — Signature Deadlines

**MUST**

Signed messages MUST include and check a deadline. A signature without a deadline can be executed at any future time.

### BC-087 — Testnet-Only Testing

**MUST NOT**

Testing only on a testnet without fork-testing on the target chain with real state is prohibited. Testnet conditions differ.

### BC-088 — Chain-Specific Behavior

**MUST**

Different EVM chains have different gas costs, precompiles, and opcode availability. Contracts MUST be tested on the target chain.

### BC-089 — Post-Deployment Monitoring

**MUST**

A contract in production MUST be monitored (events, balances, anomalies). An exploit MUST NOT be discovered by users before the team.

### BC-090 — `blockhash` 256 Block Limit

**MUST NOT**

`blockhash(n)` returns `0` for blocks older than 256. Trusting `blockhash` beyond this boundary fails silently and MUST NOT be used.

## AI-Specific Blockchain Discipline

### BC-091 — Smart Contract API Verification

**MUST**

Before using a smart contract standard interface (e.g., ERC-20, ERC-721) or a library function (e.g., OpenZeppelin, Solmate), the assistant MUST verify the method signature and behavior in the installed version. Invented methods or incorrect signatures lead to permanent loss of funds or bricked contracts.

See MAS-036 in `_universal/00-master-anti-slop.md`.

### BC-092 — Existing Contract Discovery

**MUST**

Before deploying a new smart contract or token, the assistant MUST search the project's registry or deployment scripts for an existing equivalent. Inventing parallel tokens or vaults fragments liquidity and confuses users.

See MAS-035 in `_universal/00-master-anti-slop.md`.

### BC-093 — Cryptographic Primitive Verification

**MUST**

Before implementing custom cryptographic checks (e.g., signature verification, hash preimages), the assistant MUST verify that a battle-tested library (e.g., OpenZeppelin ECDSA) does not already provide it. Custom cryptography in smart contracts is a primary source of critical exploits.

See MAS-038 in `_universal/00-master-anti-slop.md`.

## Response to Violation

When a rule in this file is violated, report:

Violation: BC-{NNN}
Reason: {one-line reason}
Correction: {smallest fix}

For multiple violations, report each rule ID separately.

Do not replace a technical correction with a generic explanation.