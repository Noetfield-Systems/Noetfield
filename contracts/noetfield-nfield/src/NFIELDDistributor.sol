// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {MerkleProof} from "@openzeppelin/contracts/utils/cryptography/MerkleProof.sol";
import {Ownable2Step} from "@openzeppelin/contracts/access/Ownable2Step.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/// @title NFIELD Epoch Distributor — proposed implementation, NOT DEPLOYED
/// @notice Each published Merkle root is immutable. Only claims proven under
///         that root transfer actual funded ERC-20s. No owner ability to
///         fabricate claims or retroactively change a published allocation.
/// @dev Leaf: keccak256(bytes.concat(keccak256(abi.encode(account,amount,epoch)))).
///      This contract must be pre-funded by the treasury. No token-minting role.
contract NFIELDDistributor is Ownable2Step, ReentrancyGuard {
    using SafeERC20 for IERC20;

    IERC20 public immutable token;
    mapping(uint256 => bytes32) public epochRoots;
    mapping(uint256 => mapping(address => bool)) public claimed;

    event EpochPublished(uint256 indexed epoch, bytes32 root);
    event Claimed(uint256 indexed epoch, address indexed account, uint256 amount);

    error InvalidToken();
    error ZeroRoot();
    error EpochAlreadyPublished();
    error MissingEpoch();
    error AlreadyClaimed();
    error InvalidClaim();

    constructor(address tokenAddress, address manager) Ownable(manager) {
        if (tokenAddress == address(0)) revert InvalidToken();
        token = IERC20(tokenAddress);
    }

    /// @notice Publish exactly once; operator cannot replace a published root.
    function publishEpoch(uint256 epoch, bytes32 root) external onlyOwner {
        if (root == bytes32(0)) revert ZeroRoot();
        if (epochRoots[epoch] != bytes32(0)) revert EpochAlreadyPublished();
        epochRoots[epoch] = root;
        emit EpochPublished(epoch, root);
    }

    function leaf(address account, uint256 amount, uint256 epoch) public pure returns (bytes32) {
        return keccak256(bytes.concat(keccak256(abi.encode(account, amount, epoch))));
    }

    /// @notice Transfers actual funded NFIELD from this distributor, never XP.
    function claim(uint256 epoch, uint256 amount, bytes32[] calldata proof) external nonReentrant {
        bytes32 root = epochRoots[epoch];
        if (root == bytes32(0)) revert MissingEpoch();
        if (claimed[epoch][msg.sender]) revert AlreadyClaimed();
        if (amount == 0 || !MerkleProof.verify(proof, root, leaf(msg.sender, amount, epoch))) {
            revert InvalidClaim();
        }
        claimed[epoch][msg.sender] = true;
        token.safeTransfer(msg.sender, amount);
        emit Claimed(epoch, msg.sender, amount);
    }
}
