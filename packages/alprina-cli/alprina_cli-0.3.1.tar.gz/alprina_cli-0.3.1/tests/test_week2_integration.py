"""
Week 2 Integration Tests - Days 1-3 Combined
==============================================

Tests the complete Week 2 workflow:
1. Oracle Manipulation Detection (Day 1)
2. Input Validation Detection (Day 2)
3. Economic Impact Calculation (Day 3)

Author: Alprina Development Team
Date: 2025-11-12
"""

import sys
from pathlib import Path

# Add CLI to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from alprina_cli.agents.web3_auditor.solidity_analyzer import SolidityStaticAnalyzer
from alprina_cli.agents.web3_auditor.economic_impact_calculator import (
    EconomicImpactCalculator,
    ImpactCategory
)


class TestWeek2Integration:
    """Integration tests for Week 2 features"""

    def setup_method(self):
        """Setup test fixtures"""
        self.analyzer = SolidityStaticAnalyzer()
        self.calculator = EconomicImpactCalculator()

    # =========================================================================
    # END-TO-END WORKFLOW TESTS
    # =========================================================================

    def test_oracle_manipulation_to_economic_impact(self):
        """Test: Detect oracle vulnerability → Calculate economic impact"""

        # Vulnerable contract: DEX using UniswapV2 spot price
        vulnerable_code = """
        // SPDX-License-Identifier: MIT
        pragma solidity ^0.8.0;

        interface IUniswapV2Router02 {
            function getAmountsOut(uint amountIn, address[] memory path)
                external view returns (uint[] memory amounts);
        }

        contract VulnerableDEX {
            IUniswapV2Router02 public router;

            // CRITICAL: Using spot price for swaps (flash loan vulnerable)
            function swapTokens(uint256 amount) public {
                address[] memory path = new address[](2);
                path[0] = address(0x1);
                path[1] = address(0x2);

                // Get spot price - NO TWAP protection
                uint256[] memory amounts = router.getAmountsOut(amount, path);
                uint256 price = amounts[1];  // VULNERABLE!

                // Execute swap based on manipulated price
                // ... swap logic
            }
        }
        """

        # Step 1: Detect vulnerability
        vulnerabilities = self.analyzer.analyze_contract(vulnerable_code, "VulnerableDEX.sol")

        # Verify detection
        oracle_vulns = [v for v in vulnerabilities
                       if 'oracle' in v.title.lower() or 'price' in v.title.lower()]

        assert len(oracle_vulns) > 0, "Should detect oracle manipulation"
        vuln = oracle_vulns[0]

        assert vuln.severity in ['critical', 'high'], f"Should be critical/high, got {vuln.severity}"

        # Step 2: Calculate economic impact
        context = {
            'tvl': 50_000_000,  # $50M DEX
            'protocol_type': 'dex'
        }

        impact = self.calculator.calculate_impact(
            vulnerability_type='oracle_manipulation',
            severity=vuln.severity,
            contract_context=context
        )

        # Step 3: Verify economic assessment
        assert impact.impact_category in [ImpactCategory.CRITICAL, ImpactCategory.CATASTROPHIC]
        assert impact.estimated_loss_usd[1] > 10_000_000, "Should estimate >$10M max loss"
        assert impact.risk_score > 50, "Should have high risk score"
        assert impact.time_to_exploit in ['immediate', 'hours'], "Flash loan attacks are immediate"

        # Step 4: Generate report
        report = self.calculator.format_impact_report(impact)
        assert 'CATASTROPHIC' in report or 'CRITICAL' in report
        assert '$' in report
        assert 'Risk Score' in report

        print("\n✅ INTEGRATION TEST 1 PASSED: Oracle Detection → Economic Impact")
        print(f"   Detected: {vuln.title}")
        print(f"   Impact: {impact.impact_category.value}")
        print(f"   Loss Range: ${impact.estimated_loss_usd[0]:,} - ${impact.estimated_loss_usd[1]:,}")
        print(f"   Risk Score: {impact.risk_score:.1f}/100")

    def test_input_validation_to_economic_impact(self):
        """Test: Detect input validation issue → Calculate economic impact"""

        vulnerable_code = """
        // SPDX-License-Identifier: MIT
        pragma solidity ^0.8.0;

        contract VulnerableLending {
            mapping(address => uint256) public balances;

            // CRITICAL: No address(0) check, no amount validation
            function deposit(address token, uint256 amount) external {
                // Missing: require(token != address(0), "Invalid token");
                // Missing: require(amount > 0, "Invalid amount");

                balances[msg.sender] += amount;

                // Unchecked low-level call
                (bool success, ) = token.call(
                    abi.encodeWithSignature("transferFrom(address,address,uint256)",
                    msg.sender, address(this), amount)
                );
                // Missing: require(success, "Transfer failed");
            }

            function withdraw(address recipient, uint256 amount) external {
                // Missing: require(recipient != address(0));
                // Missing: require(amount > 0 && amount <= balances[msg.sender]);

                balances[msg.sender] -= amount;
                payable(recipient).transfer(amount);
            }
        }
        """

        # Step 1: Detect vulnerabilities
        vulnerabilities = self.analyzer.analyze_contract(vulnerable_code, "VulnerableLending.sol")

        # Verify detection (should find multiple issues)
        input_vulns = [v for v in vulnerabilities
                      if 'input' in v.title.lower() or 'validation' in v.title.lower()
                      or 'unchecked' in v.title.lower() or 'address' in v.title.lower()]

        assert len(input_vulns) > 0, "Should detect input validation issues"

        # Pick the most severe
        critical_vulns = [v for v in input_vulns if v.severity == 'critical']
        high_vulns = [v for v in input_vulns if v.severity == 'high']
        vuln = critical_vulns[0] if critical_vulns else (high_vulns[0] if high_vulns else input_vulns[0])

        # Step 2: Calculate economic impact
        context = {
            'tvl': 10_000_000,  # $10M lending protocol
            'protocol_type': 'lending'
        }

        impact = self.calculator.calculate_impact(
            vulnerability_type='input_validation',
            severity=vuln.severity,
            contract_context=context
        )

        # Step 3: Verify assessment
        assert impact.estimated_loss_usd[0] > 0, "Should have minimum loss estimate"
        assert impact.risk_score > 0, "Should have risk score"

        print("\n✅ INTEGRATION TEST 2 PASSED: Input Validation → Economic Impact")
        print(f"   Detected: {vuln.title}")
        print(f"   Impact: {impact.impact_category.value}")
        print(f"   Loss Range: ${impact.estimated_loss_usd[0]:,} - ${impact.estimated_loss_usd[1]:,}")

    def test_multiple_vulnerabilities_aggregate_impact(self):
        """Test: Multiple vulnerabilities → Aggregate economic impact"""

        highly_vulnerable_code = """
        // SPDX-License-Identifier: MIT
        pragma solidity ^0.8.0;

        interface IOracle {
            function latestRoundData() external view returns (
                uint80 roundId,
                int256 answer,
                uint256 startedAt,
                uint256 updatedAt,
                uint80 answeredInRound
            );
        }

        contract HighlyVulnerableProtocol {
            IOracle public oracle;
            mapping(address => uint256) public balances;

            // VULNERABILITY 1: Oracle without staleness check
            function getPrice() public view returns (uint256) {
                (, int256 price, , , ) = oracle.latestRoundData();
                // Missing: updatedAt staleness check
                return uint256(price);
            }

            // VULNERABILITY 2: Input validation issues
            function transfer(address to, uint256 amount) external {
                // Missing: require(to != address(0));
                // Missing: require(amount > 0);
                // Missing: require(balances[msg.sender] >= amount);

                balances[msg.sender] -= amount;
                balances[to] += amount;
            }

            // VULNERABILITY 3: Unchecked external call
            function executeCall(address target, bytes memory data) external {
                (bool success, ) = target.call(data);
                // Missing: require(success);
            }

            // VULNERABILITY 4: No access control
            function updateOracle(address newOracle) external {
                // Missing: require(msg.sender == owner);
                oracle = IOracle(newOracle);
            }
        }
        """

        # Step 1: Detect all vulnerabilities
        vulnerabilities = self.analyzer.analyze_contract(
            highly_vulnerable_code,
            "HighlyVulnerableProtocol.sol"
        )

        assert len(vulnerabilities) >= 3, f"Should detect multiple vulnerabilities, got {len(vulnerabilities)}"

        # Step 2: Calculate impact for each
        context = {
            'tvl': 100_000_000,  # $100M protocol
            'protocol_type': 'lending'
        }

        impacts = []
        total_max_loss = 0

        for vuln in vulnerabilities[:5]:  # Top 5 vulnerabilities
            # Map vulnerability to type
            vuln_type = self._map_vulnerability_to_type(vuln.title.lower())

            impact = self.calculator.calculate_impact(
                vulnerability_type=vuln_type,
                severity=vuln.severity,
                contract_context=context
            )
            impacts.append((vuln, impact))
            total_max_loss += impact.estimated_loss_usd[1]

        # Step 3: Aggregate analysis
        critical_count = sum(1 for v, i in impacts if i.impact_category in [
            ImpactCategory.CRITICAL, ImpactCategory.CATASTROPHIC
        ])

        highest_risk = max(impacts, key=lambda x: x[1].risk_score)

        print("\n✅ INTEGRATION TEST 3 PASSED: Multiple Vulnerabilities → Aggregate Impact")
        print(f"   Vulnerabilities Found: {len(vulnerabilities)}")
        print(f"   Critical/Catastrophic: {critical_count}")
        print(f"   Total Maximum Loss: ${total_max_loss:,}")
        print(f"   Highest Risk: {highest_risk[0].title} (Score: {highest_risk[1].risk_score:.1f})")

        assert critical_count > 0, "Should have at least one critical impact"
        assert total_max_loss > 10_000_000, "Aggregate loss should be significant"

    def test_safe_contract_no_false_positives(self):
        """Test: Safe contract → No critical economic impact"""

        safe_code = """
        // SPDX-License-Identifier: MIT
        pragma solidity ^0.8.0;

        interface IOracle {
            function latestRoundData() external view returns (
                uint80 roundId,
                int256 answer,
                uint256 startedAt,
                uint256 updatedAt,
                uint80 answeredInRound
            );
        }

        contract SafeProtocol {
            IOracle public immutable oracle;
            uint256 public constant STALENESS_THRESHOLD = 3600; // 1 hour
            address public immutable owner;

            constructor(address _oracle) {
                require(_oracle != address(0), "Invalid oracle");
                oracle = IOracle(_oracle);
                owner = msg.sender;
            }

            // SAFE: Oracle with staleness check
            function getPrice() public view returns (uint256) {
                (
                    uint80 roundId,
                    int256 price,
                    uint256 startedAt,
                    uint256 updatedAt,
                    uint80 answeredInRound
                ) = oracle.latestRoundData();

                require(price > 0, "Invalid price");
                require(updatedAt > 0, "Invalid timestamp");
                require(block.timestamp - updatedAt <= STALENESS_THRESHOLD, "Stale price");
                require(answeredInRound >= roundId, "Stale round");

                return uint256(price);
            }

            // SAFE: Proper input validation
            function transfer(address to, uint256 amount) external {
                require(to != address(0), "Invalid recipient");
                require(amount > 0, "Invalid amount");
                // ... safe transfer logic
            }

            // SAFE: Access control
            function updateSettings() external {
                require(msg.sender == owner, "Unauthorized");
                // ... update logic
            }
        }
        """

        # Step 1: Analyze safe contract
        vulnerabilities = self.analyzer.analyze_contract(safe_code, "SafeProtocol.sol")

        # Should have minimal or no critical vulnerabilities
        critical_vulns = [v for v in vulnerabilities if v.severity == 'critical']

        print("\n✅ INTEGRATION TEST 4 PASSED: Safe Contract → No False Positives")
        print(f"   Vulnerabilities Found: {len(vulnerabilities)}")
        print(f"   Critical Vulnerabilities: {len(critical_vulns)}")

        # Safe contracts should not trigger critical alerts
        assert len(critical_vulns) == 0, f"Safe contract should have no critical issues, found {len(critical_vulns)}"

    # =========================================================================
    # PERFORMANCE TESTS
    # =========================================================================

    def test_large_contract_analysis_performance(self):
        """Test: Large contract analysis completes in reasonable time"""
        import time

        # Generate large contract
        large_code = """
        // SPDX-License-Identifier: MIT
        pragma solidity ^0.8.0;

        contract LargeContract {
        """

        # Add 50 functions
        for i in range(50):
            large_code += f"""
            function function{i}(address addr, uint256 amount) external {{
                require(addr != address(0), "Invalid address");
                require(amount > 0, "Invalid amount");
                // ... logic
            }}
            """

        large_code += "}"

        # Measure analysis time
        start_time = time.time()
        vulnerabilities = self.analyzer.analyze_contract(large_code, "LargeContract.sol")
        analysis_time = time.time() - start_time

        print(f"\n✅ PERFORMANCE TEST PASSED")
        print(f"   Contract Size: 50 functions")
        print(f"   Analysis Time: {analysis_time:.2f}s")
        print(f"   Vulnerabilities Found: {len(vulnerabilities)}")

        assert analysis_time < 10.0, f"Analysis should complete in <10s, took {analysis_time:.2f}s"

    def test_economic_impact_calculation_performance(self):
        """Test: Economic impact calculation is fast"""
        import time

        start_time = time.time()

        # Calculate 100 impacts
        for i in range(100):
            self.calculator.calculate_impact(
                vulnerability_type='oracle_manipulation',
                severity='critical',
                contract_context={'tvl': 10_000_000, 'protocol_type': 'dex'}
            )

        elapsed = time.time() - start_time
        avg_time = elapsed / 100

        print(f"\n✅ PERFORMANCE TEST PASSED: Economic Impact Calculation")
        print(f"   100 calculations in {elapsed:.3f}s")
        print(f"   Average: {avg_time*1000:.2f}ms per calculation")

        assert avg_time < 0.01, f"Should average <10ms, got {avg_time*1000:.2f}ms"

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _map_vulnerability_to_type(self, title: str) -> str:
        """Map vulnerability title to economic impact type"""
        if 'oracle' in title or 'price' in title:
            return 'oracle_manipulation'
        elif 'input' in title or 'validation' in title or 'address' in title:
            return 'input_validation'
        elif 'unchecked' in title or 'call' in title:
            return 'unchecked_external_call'
        elif 'reentrancy' in title:
            return 'reentrancy'
        elif 'access' in title or 'control' in title:
            return 'access_control'
        elif 'flash' in title or 'loan' in title:
            return 'flash_loan_attack'
        else:
            return 'logic_error'


def run_integration_tests():
    """Run all integration tests"""
    print("=" * 70)
    print("🧪 WEEK 2 INTEGRATION TESTS (Days 1-3)")
    print("=" * 70)
    print()

    test_suite = TestWeek2Integration()

    tests = [
        ("Oracle Detection → Economic Impact", test_suite.test_oracle_manipulation_to_economic_impact),
        ("Input Validation → Economic Impact", test_suite.test_input_validation_to_economic_impact),
        ("Multiple Vulnerabilities → Aggregate", test_suite.test_multiple_vulnerabilities_aggregate_impact),
        ("Safe Contract → No False Positives", test_suite.test_safe_contract_no_false_positives),
        ("Large Contract Performance", test_suite.test_large_contract_analysis_performance),
        ("Economic Calculation Performance", test_suite.test_economic_impact_calculation_performance),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            test_suite.setup_method()
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ FAILED: {test_name}")
            print(f"   Error: {e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ ERROR: {test_name}")
            print(f"   Error: {e}")
            failed += 1

    print("\n" + "=" * 70)
    print(f"📊 INTEGRATION TEST RESULTS: {passed}/{len(tests)} passed")
    if failed == 0:
        print("✅ ALL INTEGRATION TESTS PASSED!")
    else:
        print(f"⚠️  {failed} test(s) failed")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    import sys
    success = run_integration_tests()
    sys.exit(0 if success else 1)
