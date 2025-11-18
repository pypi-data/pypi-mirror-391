// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title SimpleSwap
 * @dev Simplified AMM (like Uniswap) with gas inefficiencies
 */
contract SimpleSwap {
    address public token0;  // Could be immutable
    address public token1;  // Could be immutable
    address public factory; // Could be immutable

    uint112 public reserve0;
    uint112 public reserve1;
    uint32 public blockTimestampLast;

    uint public price0CumulativeLast;
    uint public price1CumulativeLast;
    uint public kLast;

    uint private unlocked = 1;

    // Events
    event Swap(
        address indexed sender,
        uint amount0In,
        uint amount1In,
        uint amount0Out,
        uint amount1Out,
        address indexed to
    );
    event Sync(uint112 reserve0, uint112 reserve1);

    modifier lock() {
        require(unlocked == 1, "Locked");
        unlocked = 0;
        _;
        unlocked = 1;
    }

    constructor(address _token0, address _token1) {
        factory = msg.sender;
        token0 = _token0;
        token1 = _token1;
    }

    // Swap function with gas inefficiencies
    function swap(uint amount0Out, uint amount1Out, address to) public lock {
        require(amount0Out > 0 || amount1Out > 0, "Insufficient output amount");
        require(to != token0 && to != token1, "Invalid to");

        // Multiple storage reads
        require(amount0Out < reserve0 && amount1Out < reserve1, "Insufficient liquidity");

        uint balance0;
        uint balance1;

        // Simulate token transfers
        if (amount0Out > 0) balance0 = reserve0 - amount0Out;
        if (amount1Out > 0) balance1 = reserve1 - amount1Out;

        // Using msg.sender multiple times
        require(balance0 * balance1 >= uint(reserve0) * uint(reserve1), "K");

        _update(uint112(balance0), uint112(balance1), reserve0, reserve1);

        emit Swap(msg.sender, 0, 0, amount0Out, amount1Out, to);
    }

    // Update reserves
    function _update(uint112 balance0, uint112 balance1, uint112 _reserve0, uint112 _reserve1) private {
        require(balance0 <= type(uint112).max && balance1 <= type(uint112).max, "Overflow");

        uint32 blockTimestamp = uint32(block.timestamp % 2**32);
        uint32 timeElapsed = blockTimestamp - blockTimestampLast;

        if (timeElapsed > 0 && _reserve0 != 0 && _reserve1 != 0) {
            // Multiple calculations without caching
            price0CumulativeLast += uint((_reserve1 * 1e18) / _reserve0) * timeElapsed;
            price1CumulativeLast += uint((_reserve0 * 1e18) / _reserve1) * timeElapsed;
        }

        reserve0 = balance0;
        reserve1 = balance1;
        blockTimestampLast = blockTimestamp;

        emit Sync(reserve0, reserve1);
    }

    // Get reserves
    function getReserves() public view returns (uint112 _reserve0, uint112 _reserve1, uint32 _blockTimestampLast) {
        _reserve0 = reserve0;
        _reserve1 = reserve1;
        _blockTimestampLast = blockTimestampLast;
    }

    // Mint liquidity with loop
    function mintBatch(address[] memory recipients, uint[] memory amounts) public {
        // Loop inefficiency
        for (uint i = 0; i < recipients.length; i++) {
            // Simulate minting
            reserve0 += uint112(amounts[i]);
        }
    }

    // Price oracle function with redundant checks
    function getPrice() public view returns (uint) {
        require(reserve0 > 0 && reserve1 > 0, "No liquidity");
        require(reserve0 > 0, "No reserve0");  // Redundant check
        require(reserve1 > 0, "No reserve1");  // Redundant check

        return (reserve1 * 1e18) / reserve0;
    }
}
