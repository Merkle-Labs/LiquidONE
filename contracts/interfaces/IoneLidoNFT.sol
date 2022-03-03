// SPDX-FileCopyrightText: 2022 MerkleLabs
// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/extensions/IERC721Enumerable.sol";

interface IoneLidoNFT is IERC721Enumerable{

    struct NonFungibleONE {
        uint256 mintedAtEpoch;
        uint256 amount;
        uint256 claimableAtEpoch;
    }

    function mint(
        address user_,
        uint256 epoch_,
        uint256 endEpoch_,
        uint256 amount_
    ) 
        external; 

    function burn(uint256 tokenId_) external; 

    function getMintedEpochOfTokenByIndex(uint256 tokenId) external view returns (uint256); 

    function getClaimableEpochOfTokenByIndex(uint256 tokenId) external view returns (uint256);

    function getAmountOfTokenByIndex(uint256 tokenId) external view returns (uint256); 

    function adjustAmountOfTokenByIndex(uint256 tokenId, uint256 amount_) external; 

    function addNFO(uint256 tokenId, NonFungibleONE memory nfo_) external; 

    function checkOwnerOrApproved(address sender_, uint256 tokenId_) 
        external 
        view 
        returns(bool);
}