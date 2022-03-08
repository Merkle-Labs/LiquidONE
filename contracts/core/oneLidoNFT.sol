// SPDX-FileCopyrightText: 2022 MerkleLabs
// SPDX-License-Identifier: GPL-3.0

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/IERC721Enumerable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title ERC721 ticket generated on unStake from Lido's Harmony Liquid
 * Staking protocol.
 */

contract oneLidoNFT is
    ERC721Enumerable,
    Ownable
{
    // This keeps track of the tokenID of the generated ERC721-ticket
    uint256 private _tokenCounter;

    // TODO: Handle slashing by exchange rate (#1)
    // Ticket - representing the claim
    struct NonFungibleONE {
        uint256 mintedAtEpoch;
        uint256 amount;
        uint256 claimableAtEpoch;
    }

    // maps tokenId to Ticket
    mapping(uint256 => NonFungibleONE) internal _tokenIdToNonFungibleONE;

    constructor() ERC721("oneLidoNFT", "nftONE")
    {
        _tokenCounter = 0;
    }
    
    /**
     * @notice Mints a new token to a user who has come to unStake. If the
     *  user already has a token for that epoch then the amount will be added
     * to the existing amount of that ticket
     * Requirements:
     *
     * - the caller must have a balance of at least `amount_`.
     * - the contract must not be paused.
     */

    function mint(
        address user_,
        uint256 epoch_,
        uint256 endEpoch_,
        uint256 amount_
    )
        external
        onlyOwner
    {
        uint256 newTokenId = _tokenCounter;

        bool flag = false;

        uint256 length = this.balanceOf(user_);

        for (uint256 index = 0; index < length; index++) {

            uint256 userTokenID = tokenOfOwnerByIndex(user_, index);
            if (
                getMintedEpochOfTokenByIndex(userTokenID) == epoch_ &&
                getClaimableEpochOfTokenByIndex(userTokenID) == endEpoch_
            ) {
                adjustAmountOfTokenByIndex(userTokenID, amount_);
                flag = true;
                return;
            }
        }
        if (!flag) {
            NonFungibleONE memory nfo =
                NonFungibleONE(epoch_, amount_, endEpoch_);

            addNFO(newTokenId, nfo);
            _mint(user_, newTokenId);
            _tokenCounter = _tokenCounter + 1;
        }
    }

    /**
     * @notice Burns the tokenId when user comes to claim his ticket
     * Requirements:
     *
     * - Must be a valid user ( already checked on stONE contarct side )
     */
    function burn(uint256 tokenId_)
        external
        onlyOwner
    {
        _burn(tokenId_);
        delete _tokenIdToNonFungibleONE[tokenId_];
    }


    /**
     * @return the epoch when the tokenId was minted
     * Requirements:
     *
     * - 'tokenId_' must be a valid tokenId .
     */
    function getMintedEpochOfTokenByIndex(uint256 tokenId_)
        public
        view
        returns (uint256)
    {
        require(
            _tokenIdToNonFungibleONE[tokenId_].mintedAtEpoch != 0,
             "TokenID doesnt exist"
        );
        return _tokenIdToNonFungibleONE[tokenId_].mintedAtEpoch;
    }

    /**
     * @return the epoch when the tokenId can be claimed
     * Requirements:
     *
     * - 'tokenId_' must be a valid tokenId .
     */
    function getClaimableEpochOfTokenByIndex(uint256 tokenId_)
        public
        view
        returns (uint256)
    {
        require(
            _tokenIdToNonFungibleONE[tokenId_].mintedAtEpoch != 0,
             "TokenID doesnt exist"
        );

        return _tokenIdToNonFungibleONE[tokenId_].claimableAtEpoch;
    }

    /**
     * @return the amount which can be claimed
     * Requirements:
     *
     * - 'tokenId_' must be a valid tokenId .
     */
    function getAmountOfTokenByIndex(uint256 tokenId_)
        public
        view
        returns (uint256)
    {
        require(
            _tokenIdToNonFungibleONE[tokenId_].mintedAtEpoch != 0,
             "TokenID doesnt exist"
        );

        return _tokenIdToNonFungibleONE[tokenId_].amount;
    }

    /**
     * @notice update the claimable amount of a ticket - only when the          * ticket owner unstakes on the same epoch
     * Requirements:
     *
     * - 'tokenId_' must be a valid tokenId .
     */
    function adjustAmountOfTokenByIndex(uint256 tokenId_, uint256 amount_)
        private
    {
        require(
            _tokenIdToNonFungibleONE[tokenId_].mintedAtEpoch != 0,
             "TokenID doesnt exist"
        );

        _tokenIdToNonFungibleONE[tokenId_].amount += amount_;
    }

    /**
     * @notice assigns a ticket to a tokenID
     * Requirements:
     *
     * - 'tokenId_' must not be used before
     */
    function addNFO(uint256 tokenId_, NonFungibleONE memory nfo_)
        private
    {
        require(
            _tokenIdToNonFungibleONE[tokenId_].mintedAtEpoch == 0,
            "TokenID already exist"
        );

        _tokenIdToNonFungibleONE[tokenId_] = nfo_;
    }

    /**
     * @return If the 'sender_' is the owner/approved to spend the 'tokenId_'
     */
    function checkOwnerOrApproved(address sender_, uint256 tokenId_)
        public
        view
        returns(bool)
    {
      return _isApprovedOrOwner(sender_, tokenId_);
    }
}
