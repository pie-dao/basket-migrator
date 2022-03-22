// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

interface IBasketFacet is IERC20 {
    function joinPool(uint256 _amount) external;

    function exitPool(uint256 _amount) external;

    function calcTokensForAmount(uint256 _amount)
        external
        view
        returns (address[] memory tokens, uint256[] memory amounts);
}
