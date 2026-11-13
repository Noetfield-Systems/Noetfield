# NFIELD Base Token + Distribution Contracts

**Status:** code candidate / NOT DEPLOYED / NOT ISSUED / NOT AN ACTIVE AIRDROP.

Noetfield Systems Inc. proposes NFIELD as an independent Base (chain ID 8453) EVM ERC-20 utility asset for verifiable AI Agent, RWA and policy-to-code ecosystems. This is a proposed contract package, not a token offering, investor solicitation or an approval to spend treasury assets.

## Contracts
- src/NFIELD.sol — OpenZeppelin 5.4.0 fixed-supply ERC-20, EIP-2612 permit. 1,000,000,000 NFIELD (18 decimals) minted exactly once to a selected owner-controlled treasury at deployment. No owner mint, upgrade proxy, freeze or fee-on-transfer functionality.
- src/NFIELDDistributor.sol — pre-funded immutable Merkle epoch distributor. Every claim must prove address, amount and epoch; one claim per address/epoch. No fake balance or unrestricted public mint.
- test/NFIELD.t.sol — Foundry tests for supply, transfers, authentication of publisher, immutable roots, funded claims, invalid proofs, double-claim prevention, unfunded transfer rejection.

## Dependency pins

OpenZeppelin contracts tag v5.4.0 and forge-std tag v1.9.7. Compile/test in CI. Do not deploy unreviewed code with treasury funds solely because tests pass.

## Distribution model

A draft (NOT finalized) allocation scenario is detailed in /onchain/whitepaper/#token-design. For any distribution, generate an explicit Merkle tree with publicly recorded epoch, address, amount, and evidence-driven eligibility. A signed offchain daily XP entry is never directly a token or promise of future token rights. Airdrop epochs activate only after the distributor is deployed and funded with actual NFIELD.

## Deployment inputs (currently absent)
- Explicit Base treasury owner/multisig address.
- Contract deployer wallet that signs and pays chain gas; there is no deployer key in Git.
- Final supply/distribution authorization and treasury funding record.
- Onchain transaction receipts, verified Base contract addresses and executable liquidity before enabling any trade or claim UI.

Noetfield does not share this token or treasury with BuildRelay ($RELAY) or Cairn (CRN).

## Tests

Run from contracts/noetfield-nfield after pinned dependencies are present:

    forge test -vvv

The GitHub CI workflow installs the pinned dependencies and runs the contract tests automatically. A green build proves compilation/tests, not deployment or external token liquidity.
