---
id: 02-blockchain-anti-slop
title: "Blockchain Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: delivery
version: 2
---

# Blockchain Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
generic security, dependency addition, output format) are NOT
repeated here.

This file covers rules specific to blockchain systems: smart
contract security, gas discipline, upgradeability, oracle use,
testing methodology, and deployment. It does NOT cover generic web
security (see `02-security-critical-anti-slop.md`), language rules
for Solidity or Rust (see the language files), or frontend rules for
dApps (see `02-frontend-anti-slop.md`).

A deployed smart contract is immutable. A bug is permanent and, if
exploitable, is exploited within hours. The adversary is anonymous,
funded, and automated. The rules below reflect that reality.

## 1. Stack Assumptions

This file applies to:

- EVM chains (Ethereum, Polygon, Arbitrum, Optimism, Base, BNB
  Chain, Avalanche C-Chain).
- Solana (Rust, Anchor).
- Move-based chains (Aptos, Sui).
- Cosmos SDK chains.
- Bitcoin script (limited scope).

The examples use Solidity and Rust. The principles are
platform-agnostic. Solidity-specific rules (storage layout,
`delegatecall` semantics) are covered here because they are part of
the protocol, not the language. Language rules for Solidity itself
(style, comments, naming) live in the language files.

## 2. Delivery Contracts

A blockchain system commits to eight contracts. Every section below
enforces one or more of these.

### 2.1 Immutability After Deploy

Once deployed, a contract's bytecode cannot be changed unless it
was explicitly designed for upgradeability. Every bug is permanent.

### 2.2 Value Preservation

Funds held by the contract are not lost, drained, or locked by
unintended behavior. Every external call has a defined failure
mode.

### 2.3 Access Control

Every state-changing function that should be restricted has an
explicit check. The default is deny.

### 2.4 Gas Predictability

Users can predict the gas cost of an action within a reasonable
range. Unbounded loops and state explosion are not acceptable.

### 2.5 Upgrade Safety

If upgradeable, the upgrade path cannot brick the contract. Storage
layout is preserved across upgrades.

### 2.6 Oracle Integrity

Price and external data come from sources that resist manipulation.
A single-source oracle is a vulnerability.

### 2.7 Reentrancy Safety

Every external call is analyzed for reentrancy. The pattern is
either non-reentrant by design or explicitly guarded.

### 2.8 Public Auditability

The source code is verified on the chain's explorer. The owner's
authority and the contract's behavior are visible to any user.

## 3. Reentrancy

### 3.1 Checks-Effects-Interactions

State is updated before any external call.

BAD:
```solidity
function withdraw() external {
    uint256 amount = balances[msg.sender];
    (bool ok, ) = msg.sender.call{value: amount}("");
    require(ok);
    balances[msg.sender] = 0;  // state updated after external call
}
```

An attacker's fallback function calls `withdraw` again before
`balances[msg.sender]` is zeroed. Funds are drained.

GOOD:
```solidity
function withdraw() external nonReentrant {
    uint256 amount = balances[msg.sender];
    balances[msg.sender] = 0;  // state updated first
    (bool ok, ) = msg.sender.call{value: amount}("");
    require(ok);
}
```

### 3.2 `nonReentrant` Modifier as Defense in Depth

Even with Checks-Effects-Interactions, add a `nonReentrant` guard
to functions that make external calls. The modifier protects
against future modifications that break the pattern.

### 3.3 Cross-Function Reentrancy

An attacker can call a different function during the callback, not
just the same one. The guard applies to every function that shares
state with an external-calling function.

### 3.4 Read-Only Reentrancy

A view function called during an external callback returns
inconsistent state. Lending protocols and DEXs have been drained by
this pattern. Update state before the call.

### 3.5 `transfer` vs `call`

`transfer` and `send` forward a fixed 2,300 gas. A recipient with
a fallback consuming more than that reverts the transfer. Use
`call` with a reentrancy guard.

### 3.6 ERC-777 and ERC-1155 Callbacks

Some token standards invoke callbacks on transfer. A contract that
assumes ERC-20 semantics is reentrant through these tokens. Check
the token's standard before integrating.

### 3.7 Reentrancy Through the Fallback Function

A contract's `receive` or `fallback` function that modifies state is
a reentrancy entry point. Keep them minimal.

## 4. Access Control

### 4.1 `msg.sender`, Never `tx.origin`

BAD:
```solidity
require(tx.origin == owner, "not owner");
```

An attacker tricks the owner into calling a malicious contract that
calls back into the victim contract. `tx.origin` is the owner, so
the check passes.

GOOD:
```solidity
require(msg.sender == owner, "not owner");
```

### 4.2 Explicit Modifiers

Every restricted function has a modifier. No implicit trust.

BAD:
```solidity
function mint(address to, uint256 amount) external {
    _mint(to, amount);
}
```

GOOD:
```solidity
function mint(address to, uint256 amount) external onlyRole(MINTER_ROLE) {
    _mint(to, amount);
}
```

### 4.3 Role-Based Access Control

Use OpenZeppelin's `AccessControl` for contracts with multiple
roles. Each role is a `bytes32` constant. Roles are granted and
revoked, not hardcoded.

### 4.4 Ownership as a Multisig

A contract's owner is a multisig (Safe, Gnosis). A single EOA is a
single point of failure and compromise.

BAD: An EOA owns the contract.

GOOD: A 3-of-5 multisig owns the contract. At least three keys are
in hardware wallets, geographically distributed.

### 4.5 Renounce Ownership Carefully

Renouncing ownership removes the ability to fix bugs. Do it only
when the contract is intended to be immutable and the logic is
audited.

### 4.6 No Hidden Owner

A contract with a backdoored admin function (mint without limit,
pause, self-destruct). Users cannot see the risk without reading
the code. Hidden owners are exit scams.

## 5. Gas and Storage

### 5.1 Storage Is Expensive

Writing a new storage slot costs 20,000 gas. Reading costs 2,100.
Minimize writes.

### 5.2 Pack Struct Fields

Solidity packs fields into 32-byte slots.

BAD:
```solidity
struct User {
    uint256 id;      // slot 0
    uint8 status;    // slot 1 (31 bytes wasted)
    uint256 balance; // slot 2
}
```

GOOD:
```solidity
struct User {
    uint256 id;      // slot 0
    uint256 balance; // slot 1
    uint8 status;    // slot 2
    uint8 flags;     // packed with status
}
```

### 5.3 `calldata` Over `memory` for External Parameters

BAD: `function foo(uint256[] memory arr) external`.

GOOD: `function foo(uint256[] calldata arr) external`.

`calldata` avoids a copy.

### 5.4 `immutable` and `constant`

`immutable` and `constant` values are not stored in storage. Use
them for values that do not change.

BAD:
```solidity
address public owner; // storage slot
```

GOOD:
```solidity
address public immutable owner;
```

Set once in the constructor.

### 5.5 Custom Errors

BAD: `require(condition, "Insufficient balance")`.

GOOD:
```solidity
error InsufficientBalance(uint256 available, uint256 required);
if (balance < amount) revert InsufficientBalance(balance, amount);
```

Custom errors are cheaper and more informative.

### 5.6 Unbounded Loops

BAD:
```solidity
for (uint256 i = 0; i < users.length; i++) { /* ... */ }
```

A loop over a growing array eventually exceeds the block gas limit.
The function is bricked.

GOOD: Pagination or a pull-based pattern.

### 5.7 `unchecked` Only When Proven

`unchecked { ++i; }` saves gas when overflow is impossible. Only
when proven. In Solidity 0.8+, arithmetic is checked by default.

### 5.8 Storage Layout Is Documented

For upgradeable contracts, the storage layout is documented and
tested. A reordering breaks all existing data.

## 6. Oracles

### 6.1 No Single-Source Price

BAD:
```solidity
uint256 price = pair.getReserves().token0Price;
```

A flash loan can move the reserve and the price in one transaction.

GOOD: A decentralized oracle (Chainlink) or a TWAP with a
reasonable window.

### 6.2 TWAP With a Long Window

A TWAP is manipulable if the window is short. Use a window long
enough that an attacker cannot sustain manipulation.

### 6.3 Stale Price Checks

Check the timestamp of the oracle response. A price older than the
configured maximum is rejected.

BAD:
```solidity
(, int256 price, , , ) = priceFeed.latestRoundData();
```

GOOD:
```solidity
(uint80 roundId, int256 price, , uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();
require(updatedAt > block.timestamp - MAX_STALENESS, "stale price");
require(answeredInRound >= roundId, "stale round");
require(price > 0, "invalid price");
```

### 6.4 Decimal Normalization

Different oracles use different decimals (8, 18). Normalize before
arithmetic.

### 6.5 Circuit Breakers

If the oracle reports a price beyond a configurable deviation from
the last price, pause the contract. A sudden 90% move is either a
real event (pause is correct) or an attack (pause saves funds).

## 7. Flash Loans and MEV

### 7.1 Assume the Adversary Has Infinite Capital

A flash loan provides millions in a single transaction. Any
protocol that depends on an instantaneous balance or reserve
without a time-weighted check is vulnerable.

### 7.2 Slippage Protection

Every swap has a `minAmountOut` or `maxAmountIn`. A swap without
slippage protection is sandwiched.

BAD:
```solidity
router.swapExactTokensForTokens(amountIn, 0, path, to, deadline);
```

The `0` means "accept any output", including near-zero.

GOOD:
```solidity
router.swapExactTokensForTokens(amountIn, minAmountOut, path, to, deadline);
```

### 7.3 Commit-Reveal for Sensitive Operations

An auction or a game that reveals bids on-chain is front-runnable.
Use commit-reveal with a delay.

### 7.4 Private Mempool When Necessary

For critical operations, submit through a private mempool
(Flashbots, MEV-Share) to avoid front-running. Document the trade-
off: private submission reduces MEV exposure but adds a
dependency.

### 7.5 Deadline on Every Swap

A swap without a deadline can be delayed indefinitely by miners.
Always set a deadline.

## 8. Upgradeability

### 8.1 Storage Layout Is Sacred

An upgrade cannot change the order or types of existing storage
slots.

BAD: Inserting a new variable at the top of a state declaration.

GOOD: Appending new variables at the end, or using a namespaced
storage pattern (EIP-7201) that isolates each upgrade's storage.

### 8.2 Initializer, Not Constructor

A proxy contract does not run the implementation's constructor.
Use an `initialize` function with an `initializer` modifier.

BAD:
```solidity
contract Impl {
    address public owner;
    constructor() { owner = msg.sender; } // never runs on proxy
}
```

GOOD:
```solidity
contract Impl {
    address public owner;
    function initialize(address _owner) external initializer {
        owner = _owner;
    }
}
```

### 8.3 Upgrade Authorization

Only a trusted address (multisig, timelock, DAO) can upgrade.
Never an EOA.

### 8.4 Timelock

A timelock between proposing an upgrade and executing it gives
users time to exit if they disagree. A 48-hour timelock is common
for financial contracts.

### 8.5 No `selfdestruct` in Implementation

`selfdestruct` in an implementation contract destroys the logic
while the proxy still points to it. The contract is bricked.

### 8.6 Storage Gaps

For inheritance-based upgradeable contracts, leave a storage gap
in base contracts:

```solidity
contract Base {
    uint256[50] private __gap;
}
```

The gap is consumed by future variables, preserving layout.

### 8.7 Upgrade Testing

Every upgrade is tested against a fork of mainnet with existing
state. A local test with fresh state does not catch storage
collisions.

## 9. Testing

### 9.1 Fork Tests

Test against a fork of mainnet with real state. Foundry's
`--fork-url` or Hardhat's `forking` makes this easy.

### 9.2 Fuzz Testing

Foundry's fuzzer or Echidna generates random inputs. Fuzzing finds
edge cases that hand-written tests miss.

### 9.3 Invariant Testing

Define invariants (for example, "the sum of all balances equals
the total supply") and let the fuzzer try to break them.

BAD: A test that checks a specific sequence.

GOOD: An invariant that holds across all sequences the fuzzer
generates.

### 9.4 Coverage Targets

Aim for near-100% line and branch coverage. Every branch of every
`require` and `if` is tested.

### 9.5 Static Analysis

Slither, Mythril, and the compiler's own warnings. Run in CI.

### 9.6 Audit Before Mainnet

A professional audit for any contract holding real value. No
exceptions. Audits are not a guarantee, but the absence of one is a
red flag.

### 9.7 Bug Bounty

After deployment, a bug bounty (Immunefi, HackerOne) incentivizes
white-hat disclosure. The payout must be high enough to exceed the
attacker's expected gain.

### 9.8 Test the Deployed Bytecode

A test that passes on source but fails on deployed bytecode (due to
optimizer settings or compiler version) is a false sense of
security. Verify the deployed bytecode matches the tested source.

## 10. Deployment

### 10.1 Deterministic Addresses

Use CREATE2 for deterministic addresses across chains. This allows
counterfactual deployments and cross-chain consistency.

### 10.2 Verify on the Explorer

The source code is verified on Etherscan (or the chain's
equivalent). Users can read what they are interacting with. An
unverified contract is a red flag.

### 10.3 Constructor Arguments Are Public

They are in the deployment transaction. Never pass secrets as
constructor arguments.

### 10.4 Deployment Scripts Are Code

Use Foundry scripts or Hardhat deploy. Not manual transactions in
a UI. A deployment is reproducible.

### 10.5 Multisig for Ownership

Covered in 4.4.

### 10.6 Deployment Checklist

Before deployment:

- [ ] Tests pass on the exact commit.
- [ ] Audit findings addressed.
- [ ] Constructor arguments double-checked.
- [ ] Owner is the multisig, not the deployer EOA.
- [ ] The contract is verified on the explorer.
- [ ] The first action after deploy is a role transfer or a
      renounce, per the plan.

### 10.7 Post-Deployment Verification

After deployment, verify:

- The owner and roles are as intended.
- The contract responds to basic queries.
- A small transaction succeeds.

## 11. Documentation

### 11.1 NatSpec for Public Functions

Every public function has NatSpec comments describing parameters,
returns, and reverts. Users read the source; comments are part of
the contract.

### 11.2 Owner Capabilities

A README or a section in the docs lists every privileged action
the owner can perform. Users can evaluate the trust they are
placing.

### 11.3 Known Limitations

Documented. An unaudited component, a known rounding error, a
deliberate trade-off. Users evaluate their exposure.

### 11.4 Emergency Procedures

A documented process for pausing the contract, upgrading it, or
recovering funds in an emergency. Who can act, how, and with what
notice.

## 12. Anti-Patterns

### 12.1 Unchecked External Calls

BAD:
```solidity
token.transfer(to, amount);
```

Some ERC-20 tokens do not revert on failure; they return `false`.
The call silently fails.

GOOD:
```solidity
require(token.transfer(to, amount), "transfer failed");
// Or use SafeERC20
```

### 12.2 Unbounded Loops

Covered in 5.6.

### 12.3 `transfer` and `send`

Covered in 3.5.

### 12.4 `tx.origin` for Auth

Covered in 4.1.

### 12.5 Block Timestamp as Randomness

`block.timestamp` is manipulable by miners/validators within a
window. Never the source of randomness.

BAD:
```solidity
uint256 winner = uint256(blockhash(block.number - 1)) % players.length;
```

A validator can influence the outcome.

GOOD: Chainlink VRF or a commit-reveal scheme.

### 12.6 Block Number Assumptions

`block.number` is not a reliable time source. Block times vary
between chains and after upgrades.

### 12.7 Single Oracle

Covered in 6.1.

### 12.8 `delegatecall` to Untrusted

BAD:
```solidity
target.delegatecall(data); // target from user input
```

The target executes with the current contract's storage and
address. A malicious target drains funds or takes ownership.

GOOD: An allowlist of trusted targets.

### 12.9 No Reentrancy Guard

Covered in 3.1.

### 12.10 Ignoring Return Values

Covered in 12.1.

### 12.11 `require` With Concatenated Strings

BAD:
```solidity
require(ok, string(abi.encodePacked("failed for ", user)));
```

String concatenation costs gas and bloats the bytecode.

GOOD:
```solidity
if (!ok) revert FailedFor(user);
```

### 12.12 Magic Numbers

BAD:
```solidity
if (amount > 1000000000000000000) { /* ... */ }
```

GOOD:
```solidity
if (amount > 1 ether) { /* ... */ }
```

### 12.13 Floating Pragma

BAD:
```solidity
pragma solidity ^0.8.0;
```

A floating pragma compiles with different compiler versions, some
of which may have bugs.

GOOD:
```solidity
pragma solidity 0.8.24;
```

### 12.14 No Slippage Protection

Covered in 7.2.

### 12.15 Front-Run-Friendly Auctions

Covered in 7.3.

### 12.16 Upgrade Without Timelock

Covered in 8.4.

### 12.17 Missing Events

A state change without an event is invisible to indexers and
users. Emit events for every meaningful change.

BAD:
```solidity
function setFee(uint256 newFee) external onlyOwner {
    fee = newFee;
}
```

GOOD:
```solidity
event FeeUpdated(uint256 oldFee, uint256 newFee);

function setFee(uint256 newFee) external onlyOwner {
    uint256 oldFee = fee;
    fee = newFee;
    emit FeeUpdated(oldFee, newFee);
}
```

### 12.18 Wrong Indexed Fields

An event that indexes a non-address, non-ID field wastes gas and
prevents filtering. Index the fields consumers filter on.

### 12.19 No Pause Mechanism

A contract that cannot be paused during an exploit loses
everything. A pause is a response tool. It should be time-limited
or multisig-controlled.

### 12.20 Centralized Control

A single admin key that can mint, pause, or upgrade. If it is
compromised, everything is lost.

### 12.21 No Emergency Withdrawal

A contract without an emergency exit traps funds if something
goes wrong.

### 12.22 Hardcoded Addresses

BAD: A token address hardcoded for one chain.

GOOD: Constructor parameters or a chain-aware config.

### 12.23 No Minimum Receive Check

A payable function without a `receive` or `fallback` rejects plain
ether transfers. Either accept them or document the rejection.

### 12.24 Loop Over Mappings

Mappings are not iterable. Iterating requires a parallel array that
grows with writes. Use with caution.

### 12.25 Storage Collision in Proxy

Covered in 8.1.

### 12.26 Reentrancy Through ERC-777 or ERC-1155

Covered in 3.6.

### 12.27 No Chain ID in Signatures

A signature valid on one chain is replayed on another (fork replay).
Include `chainId` and the contract address in the signed payload.

BAD:
```solidity
bytes32 hash = keccak256(abi.encodePacked(message));
```

GOOD:
```solidity
bytes32 hash = keccak256(abi.encodePacked(
    message,
    block.chainid,
    address(this)
));
```

### 12.28 Integer Division Rounding

Solidity integer division truncates. A calculation that rounds
down can accumulate error. Use fixed-point math (PRBMath, Solmate)
for financial calculations.

### 12.29 Missing Zero-Address Check

BAD:
```solidity
function setTreasury(address _treasury) external onlyOwner {
    treasury = _treasury;
}
```

If `_treasury` is `address(0)`, funds sent to the treasury are
burned.

GOOD:
```solidity
require(_treasury != address(0), "zero address");
treasury = _treasury;
```

### 12.30 Unchecked `ecrecover` Return

`ecrecover` returns `address(0)` on invalid signatures.

BAD:
```solidity
address signer = ecrecover(hash, v, r, s);
require(signer == expected);
```

GOOD:
```solidity
address signer = ecrecover(hash, v, r, s);
require(signer != address(0), "invalid signature");
require(signer == expected, "wrong signer");
```

Or use OpenZeppelin's ECDSA library.

### 12.31 Malleable Signatures

`ecrecover` accepts two valid `(s, v)` pairs for the same signature.
Use OpenZeppelin's ECDSA with `s` range checks, or a scheme without
malleability.

### 12.32 Silent `delegatecall` Failure

`delegatecall` returns a boolean. Ignoring it hides the failure.

BAD:
```solidity
target.delegatecall(data);
```

GOOD:
```solidity
(bool ok, ) = target.delegatecall(data);
require(ok, "delegatecall failed");
```

### 12.33 Unbounded `approve` Allowance

An `approve` with `type(uint256).max` is a risk if the spender is
compromised. Use limited allowances where possible.

### 12.34 No Deadline on Signature-Based Actions

A signed message without a deadline can be executed at any future
time. Include and check a deadline.

### 12.35 Unverified Contracts

A deployed contract without verified source cannot be audited by
users. Always verify.

### 12.36 Testnet-Only Testing

A contract that passes on a testnet but was never tested on a fork
of the target chain with real state. Testnet conditions differ.

### 12.37 Ignoring Chain-Specific Behavior

Different EVM chains have different gas costs, precompiles, and
opcode availability. Test on the target chain.

### 12.38 No Monitoring After Deploy

A contract in production without monitoring of its events and
balances. An exploit is discovered by users, not the team.

### 12.39 Trusting `blockhash` for Anything After 256 Blocks

`blockhash(n)` returns `0` for blocks older than 256. A check
against `blockhash` fails silently at that boundary.

### 12.40 No Minimum Deposit

A contract that accepts any deposit amount allows dust attacks and
griefing. Enforce a minimum where appropriate.

## 13. Response to Violation

If a previous response violated a rule here:

```
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

No justification. No apology paragraph. Fix and move on.
