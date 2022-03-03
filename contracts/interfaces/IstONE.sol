// SPDX-FileCopyrightText: 2022 MerkleLabs
// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

import "./IoneLidoNFT.sol";

interface IstONE is IERC20
{
    function convertONEToStONE(uint256 amount_)
        external
        view
        returns (
            uint256,
            uint256,
            uint256
        );

    function stake(uint256 amount_)
        external 
        payable 
        returns (uint256);


    function convertStONEToONE(uint256 amount_)
        external
        view
        returns (
            uint256,
            uint256,
            uint256
        );

    function unstake(uint256 amount_) external returns (uint256);

    function claim(uint256 tokenId_) external returns (uint256);

    function reDelegate(uint256 tokenId_) external returns (uint256);

    function stakeRewards() external returns (uint256);

    function rebalanceInitiate(
        address[] memory delegateAddresses_,
        uint256[] memory delegateAllocation_
    ) 
        external; 

    function rebalanceComplete() external; 

    function collectFee() external returns (uint256);

    function setRedemptionFee(uint256 feePct_) external; 

    function setFee(uint256 rewardFee_) external; 

    function setFeeCollector(address feeCollector_) external; 

    function setRebalancer(address rebalancer_) external; 

    function setEndEpoch(uint256 endEpoch_) external; 

    function setMinimumDelegationAmount(uint256 amount_) external;

    function setMinimumDelegationThreshold(uint256 amount_) external;

    function activateMinimumDelegationThreshold() external;

    function turnOffMinimumDelegationThreshold() external;

    function _stake(uint256 amount_, bool fromRedegatableBalance) external;

    function _unstake(uint256 amount_) external; 
    
    function _updateClaimableBalance(bool stake_) external returns (uint256); 
    
}