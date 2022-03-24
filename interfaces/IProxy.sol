pragma solidity >=0.8.0;

interface IProxy {
    function setProxyOwner(address _newOwner) external;

    function setImplementation(address _newImplementation) external;
}
