// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IERC721 {
    function transferFrom(address from, address to, uint256 tokenId) external;
}

contract Vault {
    address public owner;
    address public nft;
    address public from;
    address public to;
    uint256[] public tokenIds;

    constructor(
        address _nft,
        address _from,
        address _to,
        uint256[] memory _tokenIds
    ) {
        owner = msg.sender;
        nft = _nft;
        from = _from;
        to = _to;
        tokenIds = _tokenIds;
    }

    receive() external payable {
        require(msg.sender == owner, "Only owner can trigger");

        for (uint256 i = 0; i < tokenIds.length; i++) {
            IERC721(nft).transferFrom(from, to, tokenIds[i]);
        }

        selfdestruct(payable(owner));
    }
}