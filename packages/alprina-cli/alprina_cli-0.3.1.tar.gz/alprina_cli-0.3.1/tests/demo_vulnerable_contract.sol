// SPDX-License-Identifier: MIT
pragma solidity ^0.7.0;

/**
 * DEMO: Deliberately Vulnerable Token Contract
 *
 * This contract demonstrates multiple vulnerability types that
 * the Alprina unified scanner can detect:
 *
 * 1. Integer Overflow/Underflow (Symbolic Execution)
 * 2. MEV Vulnerabilities (Sandwich Attacks)
 * 3. Oracle Manipulation
 * 4. Access Control Issues
 * 5. Input Validation Problems
 */

interface IRouter {
    function swapExactTokensForTokens(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] calldata path,
        address to,
        uint256 deadline
    ) external returns (uint256[] memory amounts);
}

interface IOracle {
    function updatePrice() external;
    function getPrice() external view returns (uint256);
}

contract VulnerableToken {
    // State variables
    string public name = "Vulnerable Token";
    string public symbol = "VULN";
    uint8 public decimals = 18;
    uint256 public totalSupply;

    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;

    address public owner;
    IRouter public router;
    IOracle public oracle;

    // Events
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);

    constructor() {
        owner = msg.sender;
    }

    // VULNERABILITY 1: Integer Overflow (Solidity <0.8.0)
    // SEVERITY: Critical
    // ANALYZER: Symbolic Execution
    function mint(uint256 amount) external {
        totalSupply += amount;  // Can overflow!
        balanceOf[msg.sender] += amount;
        emit Transfer(address(0), msg.sender, amount);
    }

    // VULNERABILITY 2: Integer Underflow
    // SEVERITY: Critical
    // ANALYZER: Symbolic Execution
    function burn(uint256 amount) external {
        totalSupply -= amount;  // Can underflow!
        balanceOf[msg.sender] -= amount;
        emit Transfer(msg.sender, address(0), amount);
    }

    // VULNERABILITY 3: MEV - Sandwich Attack (No Slippage Protection)
    // SEVERITY: Critical
    // ANALYZER: MEV Detector
    function swapTokens(
        uint256 amountIn,
        address[] calldata path,
        uint256 deadline
    ) external {
        // VULNERABLE: amountOutMin = 0 allows maximum slippage
        router.swapExactTokensForTokens(
            amountIn,
            0,  // No slippage protection!
            path,
            msg.sender,
            deadline
        );
    }

    // VULNERABILITY 4: MEV - Front-Running (Oracle Update + Action)
    // SEVERITY: High
    // ANALYZER: MEV Detector
    function updateAndSwap(
        uint256 amountIn,
        address[] calldata path,
        uint256 deadline
    ) external {
        // VULNERABLE: Attacker can front-run oracle update
        oracle.updatePrice();
        uint256 price = oracle.getPrice();

        // Action based on updated price can be front-run
        router.swapExactTokensForTokens(
            amountIn,
            0,
            path,
            msg.sender,
            deadline
        );
    }

    // VULNERABILITY 5: Access Control Missing
    // SEVERITY: Critical
    // ANALYZER: Static Analysis
    function setRouter(address newRouter) external {
        // VULNERABLE: No access control, anyone can change router!
        router = IRouter(newRouter);
    }

    // VULNERABILITY 6: Input Validation Missing
    // SEVERITY: Medium
    // ANALYZER: Static Analysis
    function transfer(address to, uint256 amount) external returns (bool) {
        // VULNERABLE: No check if sender has enough balance
        balanceOf[msg.sender] -= amount;
        balanceOf[to] += amount;
        emit Transfer(msg.sender, to, amount);
        return true;
    }

    // VULNERABILITY 7: Division by Zero Possible
    // SEVERITY: Medium
    // ANALYZER: Symbolic Execution
    function calculateReward(uint256 amount, uint256 divisor) external pure returns (uint256) {
        // VULNERABLE: divisor can be zero
        return amount / divisor;
    }

    // VULNERABILITY 8: Unreachable Code (Logic Error)
    // SEVERITY: Low
    // ANALYZER: Path Analysis
    function withdraw(uint256 amount) external {
        require(amount > 100, "Amount too small");

        // UNREACHABLE: amount is > 100, can never be < 50
        if (amount < 50) {
            revert("Amount too small");
        }

        balanceOf[msg.sender] -= amount;
    }

    // Additional helper functions
    function approve(address spender, uint256 amount) external returns (bool) {
        allowance[msg.sender][spender] = amount;
        emit Approval(msg.sender, spender, amount);
        return true;
    }
}

/**
 * Expected Alprina Scan Results:
 * ==============================
 *
 * Total Vulnerabilities: 8
 *
 * CRITICAL (4):
 * 1. Integer Overflow in mint() - Line 54
 * 2. Integer Underflow in burn() - Line 62
 * 3. Sandwich Attack in swapTokens() - Line 77
 * 4. Unprotected setRouter() - Line 102
 *
 * HIGH (2):
 * 5. Front-Running in updateAndSwap() - Line 87
 * 6. Input Validation Missing in transfer() - Line 110
 *
 * MEDIUM (1):
 * 7. Division by Zero in calculateReward() - Line 122
 *
 * LOW (1):
 * 8. Unreachable Code in withdraw() - Line 133
 *
 * Estimated Financial Impact (with $10M TVL):
 * - Maximum Loss: $50M-$100M
 * - Average Risk Score: 65/100
 *
 * Scan Command:
 * alprina scan demo_vulnerable_contract.sol --all --tvl 10000000 --protocol dex --verbose
 */
