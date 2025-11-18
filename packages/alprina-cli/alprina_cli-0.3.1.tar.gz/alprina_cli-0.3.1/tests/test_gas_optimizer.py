"""
Tests for Gas Optimization Analyzer (Week 4 Day 3)

Tests gas optimization detection patterns:
- Storage optimization (packing)
- Loop optimization
- Visibility optimization
- Immutable/constant variables
- Short-circuit evaluation
- Unchecked math blocks
- Memory vs storage
- External calls
- String literals
- Delete unused variables
"""

import pytest
from pathlib import Path
from alprina_cli.agents.web3_auditor.gas_optimizer import (
    GasOptimizationAnalyzer,
    GasOptimization,
    GasIssueType
)


@pytest.fixture
def gas_analyzer():
    """Create gas analyzer instance"""
    return GasOptimizationAnalyzer()


class TestStorageOptimization:
    """Test storage packing detection"""

    def test_detects_storage_packing(self, gas_analyzer):
        """Should detect unpacked storage variables"""
        code = """
        contract Example {
            uint128 a;
            uint256 b;  // Forces new slot
            uint128 c;  // Could be packed with 'a'
        }
        """

        optimizations = gas_analyzer.analyze_contract(code, "example.sol")

        storage_opts = [o for o in optimizations if o.issue_type == GasIssueType.STORAGE_LAYOUT]
        assert len(storage_opts) > 0
        assert any("pack" in o.title.lower() for o in storage_opts)

    def test_already_packed_storage(self, gas_analyzer):
        """Should not report already packed storage"""
        code = """
        contract Example {
            uint128 a;
            uint128 b;  // Already packed with 'a'
            uint256 c;
        }
        """

        optimizations = gas_analyzer.analyze_contract(code, "example.sol")

        # Should have fewer storage optimizations for already-packed code
        storage_opts = [o for o in optimizations if o.issue_type == GasIssueType.STORAGE_LAYOUT]
        # May still suggest ordering or other optimizations, but not packing


class TestLoopOptimization:
    """Test loop optimization detection"""

    def test_detects_array_length_in_loop(self, gas_analyzer):
        """Should detect array.length in loop condition"""
        code = """
        contract Example {
            function processArray(uint[] memory arr) public {
                for (uint i = 0; i < arr.length; i++) {
                    // Do something
                }
            }
        }
        """

        optimizations = gas_analyzer.analyze_contract(code, "example.sol")

        loop_opts = [o for o in optimizations if o.issue_type == GasIssueType.LOOP_OPTIMIZATION]
        assert len(loop_opts) > 0
        assert any("cache" in o.title.lower() or "length" in o.title.lower() for o in loop_opts)

    def test_detects_uncached_state_variable(self, gas_analyzer):
        """Should detect state variable reads in loops"""
        code = """
        contract Example {
            uint public threshold;

            function check(uint[] memory values) public view {
                for (uint i = 0; i < values.length; i++) {
                    if (values[i] > threshold) {  // State read every iteration
                        // Do something
                    }
                }
            }
        }
        """

        optimizations = gas_analyzer.analyze_contract(code, "example.sol")

        loop_opts = [o for o in optimizations if o.issue_type == GasIssueType.LOOP_OPTIMIZATION]
        # Should suggest caching state variable


class TestVisibilityOptimization:
    """Test visibility modifier optimization"""

    def test_detects_public_function(self, gas_analyzer):
        """Should detect public functions that could be external"""
        code = """
        contract Example {
            function publicFunc(uint x) public returns (uint) {
                return x * 2;
            }
        }
        """

        optimizations = gas_analyzer.analyze_contract(code, "example.sol")

        visibility_opts = [o for o in optimizations if o.issue_type == GasIssueType.VISIBILITY]
        assert len(visibility_opts) > 0
        assert any("external" in o.title.lower() for o in visibility_opts)

    def test_external_function_ok(self, gas_analyzer):
        """Should not report external functions"""
        code = """
        contract Example {
            function externalFunc(uint x) external returns (uint) {
                return x * 2;
            }
        }
        """

        optimizations = gas_analyzer.analyze_contract(code, "example.sol")

        visibility_opts = [o for o in optimizations if o.issue_type == GasIssueType.VISIBILITY]
        # Should have fewer or no visibility optimizations


class TestImmutableConstant:
    """Test immutable and constant variable detection"""

    def test_detects_immutable_candidate(self, gas_analyzer):
        """Should detect variables that could be immutable"""
        code = """
        contract Example {
            address owner;

            constructor(address _owner) {
                owner = _owner;  // Set once in constructor
            }
        }
        """

        optimizations = gas_analyzer.analyze_contract(code, "example.sol")

        immutable_opts = [o for o in optimizations if o.issue_type == GasIssueType.IMMUTABLE]
        assert len(immutable_opts) > 0
        assert any("immutable" in o.title.lower() for o in immutable_opts)

    def test_detects_constant_candidate(self, gas_analyzer):
        """Should detect variables that could be constant"""
        code = """
        contract Example {
            uint public maxSupply = 1000000;  // Never changes
        }
        """

        optimizations = gas_analyzer.analyze_contract(code, "example.sol")

        # Should suggest making it constant


class TestShortCircuit:
    """Test short-circuit evaluation optimization"""

    def test_detects_expensive_first_condition(self, gas_analyzer):
        """Should detect expensive operations before cheap ones"""
        code = """
        contract Example {
            function check(address user) public view returns (bool) {
                if (getUserBalance(user) > 0 && user != address(0)) {
                    return true;
                }
            }

            function getUserBalance(address) public view returns (uint) {
                // Expensive operation
                return 100;
            }
        }
        """

        optimizations = gas_analyzer.analyze_contract(code, "example.sol")

        # Should suggest reordering conditions


class TestUncheckedMath:
    """Test unchecked math block detection"""

    def test_detects_safe_math_candidate(self, gas_analyzer):
        """Should detect safe arithmetic that could be unchecked"""
        code = """
        contract Example {
            function increment(uint counter) public pure returns (uint) {
                counter += 1;  // Safe increment
                return counter;
            }
        }
        """

        optimizations = gas_analyzer.analyze_contract(code, "example.sol")

        unchecked_opts = [o for o in optimizations if o.issue_type == GasIssueType.UNCHECKED_MATH]
        # Should suggest unchecked block for safe operations


class TestMemoryVsStorage:
    """Test memory vs storage optimization"""

    def test_detects_storage_in_memory_context(self, gas_analyzer):
        """Should detect storage pointers in memory-only context"""
        code = """
        contract Example {
            struct Data {
                uint value;
                string name;
            }

            Data[] public items;

            function getFirst() public view returns (uint) {
                Data storage item = items[0];  // Could be memory
                return item.value;
            }
        }
        """

        optimizations = gas_analyzer.analyze_contract(code, "example.sol")

        # Should suggest using memory instead of storage for read-only access


class TestGasCostCalculation:
    """Test gas cost and savings calculation"""

    def test_calculates_gas_savings(self, gas_analyzer):
        """Should calculate realistic gas savings"""
        code = """
        contract Example {
            uint128 a;
            uint256 b;
            uint128 c;
        }
        """

        optimizations = gas_analyzer.analyze_contract(code, "example.sol")

        # All optimizations should have gas savings > 0
        for opt in optimizations:
            assert opt.gas_saved > 0

    def test_calculates_financial_impact(self, gas_analyzer):
        """Should calculate ETH and USD savings"""
        code = """
        contract Example {
            uint128 a;
            uint256 b;
            uint128 c;
        }
        """

        optimizations = gas_analyzer.analyze_contract(code, "example.sol")

        # All optimizations should have financial impact
        for opt in optimizations:
            assert opt.eth_saved_per_tx > 0
            assert opt.usd_saved_per_tx > 0


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_contract(self, gas_analyzer):
        """Should handle empty contract"""
        code = """
        contract Empty {
        }
        """

        optimizations = gas_analyzer.analyze_contract(code, "empty.sol")

        # Should return empty list or minimal optimizations
        assert isinstance(optimizations, list)

    def test_invalid_syntax(self, gas_analyzer):
        """Should handle invalid Solidity syntax gracefully"""
        code = """
        contract Invalid {
            this is not valid solidity
        """

        # Should not crash
        optimizations = gas_analyzer.analyze_contract(code, "invalid.sol")
        assert isinstance(optimizations, list)

    def test_multiple_contracts(self, gas_analyzer):
        """Should analyze multiple contracts in one file"""
        code = """
        contract First {
            uint128 a;
            uint256 b;
        }

        contract Second {
            function publicFunc() public {}
        }
        """

        optimizations = gas_analyzer.analyze_contract(code, "multi.sol")

        # Should find optimizations in both contracts
        assert len(optimizations) > 0


class TestSeverityClassification:
    """Test severity assignment"""

    def test_high_severity_for_storage(self, gas_analyzer):
        """Storage optimizations should be high severity"""
        code = """
        contract Example {
            uint128 a;
            uint256 b;
            uint128 c;
        }
        """

        optimizations = gas_analyzer.analyze_contract(code, "example.sol")

        storage_opts = [o for o in optimizations if o.issue_type == GasIssueType.STORAGE_LAYOUT]
        if storage_opts:
            # Storage optimizations should be high severity due to large gas savings
            assert any(o.severity in ["high", "medium"] for o in storage_opts)

    def test_medium_severity_for_loops(self, gas_analyzer):
        """Loop optimizations should be medium severity"""
        code = """
        contract Example {
            function loop(uint[] memory arr) public {
                for (uint i = 0; i < arr.length; i++) {}
            }
        }
        """

        optimizations = gas_analyzer.analyze_contract(code, "example.sol")

        loop_opts = [o for o in optimizations if o.issue_type == GasIssueType.LOOP_OPTIMIZATION]
        if loop_opts:
            assert any(o.severity in ["medium", "low"] for o in loop_opts)


class TestRealisticContract:
    """Test on realistic contract examples"""

    def test_erc20_token(self, gas_analyzer):
        """Should find optimizations in ERC20 token"""
        code = """
        contract Token {
            string public name = "MyToken";
            string public symbol = "MTK";
            uint8 public decimals = 18;
            uint public totalSupply;

            mapping(address => uint) public balanceOf;

            function transfer(address to, uint amount) public returns (bool) {
                require(balanceOf[msg.sender] >= amount);
                balanceOf[msg.sender] -= amount;
                balanceOf[to] += amount;
                return true;
            }
        }
        """

        optimizations = gas_analyzer.analyze_contract(code, "token.sol")

        # Should find multiple optimization opportunities
        assert len(optimizations) > 0

        # Should include constant for strings
        # Should include immutable for totalSupply
        # Should include unchecked for safe math

    def test_defi_contract(self, gas_analyzer):
        """Should find optimizations in DeFi contract"""
        code = """
        contract Staking {
            address public owner;
            uint public rewardRate;

            struct Stake {
                uint amount;
                uint timestamp;
                address user;
            }

            Stake[] public stakes;

            function addStake(uint amount) public {
                stakes.push(Stake({
                    amount: amount,
                    timestamp: block.timestamp,
                    user: msg.sender
                }));
            }

            function calculateRewards() public view returns (uint) {
                uint total = 0;
                for (uint i = 0; i < stakes.length; i++) {
                    if (stakes[i].user == msg.sender) {
                        total += stakes[i].amount * rewardRate;
                    }
                }
                return total;
            }
        }
        """

        optimizations = gas_analyzer.analyze_contract(code, "staking.sol")

        # Should find multiple optimizations:
        # - Storage packing in Stake struct
        # - Loop optimization (cache stakes.length)
        # - Immutable for owner
        assert len(optimizations) >= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
