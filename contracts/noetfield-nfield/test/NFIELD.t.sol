// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Test} from "forge-std/Test.sol";
import {NFIELD} from "../src/NFIELD.sol";
import {NFIELDDistributor} from "../src/NFIELDDistributor.sol";

contract NFIELDTest is Test {
    NFIELD internal token;
    NFIELDDistributor internal distributor;
    address internal treasury;
    address internal builder;

    function setUp() public {
        treasury = makeAddr("noetfieldTreasury");
        builder = makeAddr("builder");
        token = new NFIELD(treasury);
        distributor = new NFIELDDistributor(address(token), treasury);
    }

    function testFixedSupplyAndTreasuryOwnership() public {
        assertEq(token.totalSupply(), 1_000_000_000 ether);
        assertEq(token.balanceOf(treasury), token.totalSupply());
        assertEq(token.decimals(), 18);
        assertEq(token.symbol(), "NFIELD");
    }

    function testNoZeroTreasury() public {
        vm.expectRevert(NFIELD.ZeroTreasury.selector);
        new NFIELD(address(0));
    }

    function testSimpleTransferAndBurnUnavailable() public {
        vm.prank(treasury);
        token.transfer(builder, 42 ether);
        assertEq(token.balanceOf(builder), 42 ether);
        assertEq(token.totalSupply(), token.MAX_SUPPLY());
    }

    function testFundedEpochClaim() public {
        uint256 epoch = 0;
        uint256 amount = 100 ether;
        bytes32 root = distributor.leaf(builder, amount, epoch);
        vm.prank(treasury);
        distributor.publishEpoch(epoch, root);
        vm.prank(treasury);
        token.transfer(address(distributor), amount);
        vm.prank(builder);
        distributor.claim(epoch, amount, new bytes32[](0));
        assertEq(token.balanceOf(builder), amount);
        assertTrue(distributor.claimed(epoch, builder));
        assertEq(token.balanceOf(address(distributor)), 0);
    }

    function testDuplicateClaimRejected() public {
        uint256 amount = 50 ether;
        bytes32 root = distributor.leaf(builder, amount, 7);
        vm.prank(treasury);
        distributor.publishEpoch(7, root);
        vm.prank(treasury);
        token.transfer(address(distributor), amount * 2);
        vm.prank(builder);
        distributor.claim(7, amount, new bytes32[](0));
        vm.expectRevert(NFIELDDistributor.AlreadyClaimed.selector);
        vm.prank(builder);
        distributor.claim(7, amount, new bytes32[](0));
        assertEq(token.balanceOf(builder), amount);
    }

    function testWrongAmountOrWalletRejected() public {
        bytes32 root = distributor.leaf(builder, 10 ether, 1);
        vm.prank(treasury);
        distributor.publishEpoch(1, root);
        vm.expectRevert(NFIELDDistributor.InvalidClaim.selector);
        vm.prank(builder);
        distributor.claim(1, 11 ether, new bytes32[](0));
        vm.expectRevert(NFIELDDistributor.InvalidClaim.selector);
        vm.prank(makeAddr("wrong-wallet"));
        distributor.claim(1, 10 ether, new bytes32[](0));
    }

    function testEpochRootImmutable() public {
        bytes32 root = distributor.leaf(builder, 12 ether, 3);
        vm.prank(treasury);
        distributor.publishEpoch(3, root);
        vm.expectRevert(NFIELDDistributor.EpochAlreadyPublished.selector);
        vm.prank(treasury);
        distributor.publishEpoch(3, bytes32(uint256(123)));
        assertEq(distributor.epochRoots(3), root);
    }

    function testOnlyTreasuryCanPublish() public {
        bytes32 root = distributor.leaf(builder, 20 ether, 3);
        vm.expectRevert();
        vm.prank(builder);
        distributor.publishEpoch(3, root);
    }

    function testUnfundedClaimCannotAwardTokens() public {
        bytes32 root = distributor.leaf(builder, 10 ether, 9);
        vm.prank(treasury);
        distributor.publishEpoch(9, root);
        vm.expectRevert();
        vm.prank(builder);
        distributor.claim(9, 10 ether, new bytes32[](0));
        assertFalse(distributor.claimed(9, builder));
        assertEq(token.balanceOf(builder), 0);
    }

    function testNotPublishedCannotClaim() public {
        vm.expectRevert(NFIELDDistributor.MissingEpoch.selector);
        vm.prank(builder);
        distributor.claim(10, 10 ether, new bytes32[](0));
    }
}
