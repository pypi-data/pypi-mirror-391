// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title SimpleERC20
 * @dev Basic ERC20 token with intentional gas inefficiencies for testing
 * Based on OpenZeppelin ERC20 but with optimization opportunities
 */
contract SimpleERC20 {
    string public name = "Test Token";  // Could be constant
    string public symbol = "TEST";      // Could be constant
    uint8 public decimals = 18;         // Could be constant

    uint256 public totalSupply;
    address public owner;  // Could be immutable

    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;

    // Events
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);

    constructor(uint256 initialSupply) {
        owner = msg.sender;
        totalSupply = initialSupply;
        balanceOf[msg.sender] = initialSupply;
    }

    // Public function that could be external
    function transfer(address to, uint256 amount) public returns (bool) {
        require(balanceOf[msg.sender] >= amount, "Insufficient balance");
        require(to != address(0), "Invalid recipient");

        // Inefficient: accessing balanceOf[msg.sender] multiple times
        balanceOf[msg.sender] = balanceOf[msg.sender] - amount;
        balanceOf[to] = balanceOf[to] + amount;

        emit Transfer(msg.sender, to, amount);
        return true;
    }

    // Public function that could be external
    function approve(address spender, uint256 amount) public returns (bool) {
        require(spender != address(0), "Invalid spender");

        // Using msg.sender multiple times - could cache
        allowance[msg.sender][spender] = amount;
        emit Approval(msg.sender, spender, amount);
        return true;
    }

    // Public function that could be external
    function transferFrom(address from, address to, uint256 amount) public returns (bool) {
        require(balanceOf[from] >= amount, "Insufficient balance");
        require(allowance[from][msg.sender] >= amount, "Insufficient allowance");
        require(to != address(0), "Invalid recipient");

        // Multiple storage reads - could cache
        balanceOf[from] = balanceOf[from] - amount;
        balanceOf[to] = balanceOf[to] + amount;
        allowance[from][msg.sender] = allowance[from][msg.sender] - amount;

        emit Transfer(from, to, amount);
        return true;
    }

    // Mint function with loop inefficiency
    function batchMint(address[] memory recipients, uint256[] memory amounts) public {
        require(msg.sender == owner, "Only owner");
        require(recipients.length == amounts.length, "Length mismatch");

        // Inefficient: reading array.length in every iteration
        for (uint i = 0; i < recipients.length; i++) {
            balanceOf[recipients[i]] = balanceOf[recipients[i]] + amounts[i];
            totalSupply = totalSupply + amounts[i];
            emit Transfer(address(0), recipients[i], amounts[i]);
        }
    }

    // Burn function
    function burn(uint256 amount) public {
        require(balanceOf[msg.sender] >= amount, "Insufficient balance");

        balanceOf[msg.sender] = balanceOf[msg.sender] - amount;
        totalSupply = totalSupply - amount;

        emit Transfer(msg.sender, address(0), amount);
    }
}
