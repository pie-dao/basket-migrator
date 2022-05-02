// SPDX-License-Identifier: MIT
pragma solidity >=0.8.0;

interface ILendingManager {
    /// @notice Move underlying to a lending protocol
    /// @param _underlying Address of the underlying token
    /// @param _amount Amount of underlying to lend
    /// @param _protocol Bytes32 protocol key to lend to
    function lend(
        address _underlying,
        uint256 _amount,
        bytes32 _protocol
    ) external;

    /// @notice Unlend wrapped token from its lending protocol
    /// @param _wrapped Address of the wrapped token
    /// @param _amount Amount of the wrapped token to unlend
    function unlend(address _wrapped, uint256 _amount) external;

    /// @notice Unlend and immediately lend in a different protocol
    /// @param _wrapped Address of the wrapped token to bounce to another protocol
    /// @param _amount Amount of the wrapped token to bounce to the other protocol
    /// @param _toProtocol Protocol to deposit bounced tokens in
    /// @dev Uses reentrency protection of unlend() and lend()
    function bounce(
        address _wrapped,
        uint256 _amount,
        bytes32 _toProtocol
    ) external;
}
