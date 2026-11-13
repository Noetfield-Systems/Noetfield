// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {ERC20Permit} from "@openzeppelin/contracts/token/ERC20/extensions/ERC20Permit.sol";

/// @title NFIELD — Noetfield Ecosystem Token (PROPOSED, NOT DEPLOYED)
/// @notice Fixed-supply, non-upgradeable ERC-20 for a proposed Base ecosystem.
/// @dev The whole supply is minted once to a separately selected treasury.
///      This contract has no admin mint, arbitrary confiscation, pause or proxy.
///      Allocations, treasury, vesting and liquidity must be publicly established
///      by the issuer BEFORE deploying a real token. No token is live at this stage.
contract NFIELD is ERC20, ERC20Permit {
    uint256 public constant MAX_SUPPLY = 1_000_000_000 ether;

    error ZeroTreasury();

    constructor(address treasury)
        ERC20("Noetfield Ecosystem Token", "NFIELD")
        ERC20Permit("Noetfield Ecosystem Token")
    {
        if (treasury == address(0)) revert ZeroTreasury();
        _mint(treasury, MAX_SUPPLY);
    }
}
