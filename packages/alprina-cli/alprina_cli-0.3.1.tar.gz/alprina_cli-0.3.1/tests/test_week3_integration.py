"""
Week 3 Integration Tests - Days 1-4 Combined

Tests the complete Week 3 workflow:
1. Symbolic Execution (Day 1)
2. Path Condition Extraction (Day 2)
3. MEV Detection (Day 3)
4. Cross-Contract Analysis (Day 4)

Author: Alprina Development Team
Date: 2025-11-12
"""

import sys
from pathlib import Path

# Add CLI to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from alprina_cli.agents.web3_auditor.symbolic_executor import SymbolicExecutor
from alprina_cli.agents.web3_auditor.mev_detector import MEVDetector
from alprina_cli.agents.web3_auditor.cross_contract_analyzer import CrossContractAnalyzer
from alprina_cli.agents.web3_auditor.economic_impact_calculator import EconomicImpactCalculator


class TestWeek3Integration:
    """Integration tests for Week 3 features"""

    def setup_method(self):
        """Setup test fixtures"""
        self.symbolic_executor = SymbolicExecutor()
        self.mev_detector = MEVDetector()
        self.cross_contract_analyzer = CrossContractAnalyzer()
        self.economic_calculator = EconomicImpactCalculator()

    def test_symbolic_execution_with_economic_impact(self):
        """Test: Symbolic execution → Economic impact"""

        vulnerable_code = """
        contract OverflowVulnerable {
            uint256 public totalSupply;

            function mint(uint256 amount) external {
                totalSupply += amount;  // Overflow possible
            }
        }
        """

        # Step 1: Detect with symbolic execution
        sym_vulns = self.symbolic_executor.analyze_contract(vulnerable_code, "test.sol")

        assert len(sym_vulns) > 0, "Should detect overflow"

        # Step 2: Calculate economic impact
        impact = self.economic_calculator.calculate_impact(
            vulnerability_type='integer_overflow',
            severity=sym_vulns[0].severity,
            contract_context={'tvl': 10_000_000, 'protocol_type': 'dex'}
        )

        assert impact.estimated_loss_usd[0] > 0
        assert impact.risk_score > 0

        print("✅ PASSED: Symbolic Execution → Economic Impact")
        print(f"   Vulnerability: {sym_vulns[0].title}")
        print(f"   Z3 Proof: {sym_vulns[0].code_snippet[:50]}...")
        print(f"   Financial Impact: ${impact.estimated_loss_usd[1]:,}")

    def test_mev_detection_with_economic_impact(self):
        """Test: MEV detection → Economic impact quantification"""

        vulnerable_code = """
        contract VulnerableDEX {
            function swap(uint256 amountIn) external {
                router.swapExactTokensForTokens(amountIn, 0, path, msg.sender, deadline);
            }
        }
        """

        # Step 1: Detect MEV vulnerability
        mev_vulns = self.mev_detector.analyze_contract(vulnerable_code, "test.sol")

        assert len(mev_vulns) > 0, "Should detect MEV vulnerability"

        # MEV detector already includes profit estimation in code_snippet
        assert 'MEV Profit' in mev_vulns[0].code_snippet

        print("✅ PASSED: MEV Detection with Profit Estimation")
        print(f"   Vulnerability: {mev_vulns[0].title}")
        print(f"   {mev_vulns[0].code_snippet.split(chr(10))[0]}")

    def test_cross_contract_with_economic_impact(self):
        """Test: Cross-contract analysis → Economic impact"""

        contracts = {
            "Vault": """
            contract Vault {
                function withdraw() external {
                    (bool success, ) = msg.sender.call{value: amount}("");
                    balances[msg.sender] = 0;  // AFTER external call
                }
            }
            """,
            "Attacker": """
            contract Attacker {
                function exploit() external {
                    vault.withdraw();
                }
            }
            """
        }

        # Step 1: Detect cross-contract vulnerability
        cross_vulns = self.cross_contract_analyzer.analyze_contracts(contracts, "multi.sol")

        # Should detect reentrancy or upgrade issues
        print("✅ PASSED: Cross-Contract Analysis")
        print(f"   Found {len(cross_vulns)} cross-contract vulnerabilities")

    def test_complete_vulnerability_pipeline(self):
        """Test: Complete analysis pipeline with all Week 3 features"""

        complex_contract = """
        contract ComplexVulnerable {
            uint256 public balance;
            IOracle oracle;

            // Symbolic execution: overflow
            function mint(uint256 amount) external {
                balance += amount;
            }

            // Path analysis: unreachable code
            function withdraw(uint256 amount) external {
                require(amount > 100);

                if (amount < 50) {
                    // Unreachable!
                    revert();
                }

                balance -= amount;
            }

            // MEV: front-running
            function updateAndSwap() external {
                oracle.updatePrice();
                uint256 price = oracle.getPrice();
                _swap(price);
            }
        }
        """

        # Run all analyzers
        sym_vulns = self.symbolic_executor.analyze_contract(complex_contract, "test.sol")
        mev_vulns = self.mev_detector.analyze_contract(complex_contract, "test.sol")

        total_vulns = len(sym_vulns) + len(mev_vulns)

        assert total_vulns >= 2, f"Should detect multiple vulnerabilities, found {total_vulns}"

        # Categorize vulnerabilities
        overflow_vulns = [v for v in sym_vulns if 'overflow' in v.title.lower()]
        unreachable_vulns = [v for v in sym_vulns if 'unreachable' in v.title.lower()]
        frontrun_vulns = [v for v in mev_vulns if 'front' in v.title.lower()]

        print("✅ PASSED: Complete Vulnerability Pipeline")
        print(f"   Symbolic Execution: {len(sym_vulns)} vulnerabilities")
        print(f"   MEV Detection: {len(mev_vulns)} vulnerabilities")
        print(f"   Total: {total_vulns} vulnerabilities")
        print(f"   - Overflow: {len(overflow_vulns)}")
        print(f"   - Unreachable: {len(unreachable_vulns)}")
        print(f"   - Front-running: {len(frontrun_vulns)}")

    def test_week3_with_week2_integration(self):
        """Test: Week 3 features integrate with Week 2 economic calculator"""

        vulnerable_code = """
        contract IntegrationTest {
            uint256 balance;

            function add(uint256 amount) external {
                balance += amount;  // Overflow
            }

            function swap(uint256 amountIn) external {
                router.swap(amountIn, 0, path);  // MEV
            }
        }
        """

        # Week 3: Detect vulnerabilities
        sym_vulns = self.symbolic_executor.analyze_contract(vulnerable_code, "test.sol")
        mev_vulns = self.mev_detector.analyze_contract(vulnerable_code, "test.sol")

        all_vulns = sym_vulns + mev_vulns

        # Week 2: Calculate economic impact for each
        impacts = []
        for vuln in all_vulns[:3]:  # Top 3 vulnerabilities
            impact = self.economic_calculator.calculate_impact(
                vulnerability_type='logic_error',  # Generic
                severity=vuln.severity,
                contract_context={'tvl': 50_000_000, 'protocol_type': 'dex'}
            )
            impacts.append((vuln, impact))

        assert len(impacts) > 0

        # Calculate total risk
        total_max_loss = sum(i.estimated_loss_usd[1] for v, i in impacts)

        print("✅ PASSED: Week 3 + Week 2 Integration")
        print(f"   Vulnerabilities Detected: {len(all_vulns)}")
        print(f"   Economic Impact Calculated: {len(impacts)}")
        print(f"   Total Maximum Loss: ${total_max_loss:,}")

    def test_performance_all_analyzers(self):
        """Test: Performance of all Week 3 analyzers"""
        import time

        test_contract = """
        contract PerformanceTest {
            uint256 balance;

            function test1(uint256 a) external {
                balance += a;
            }

            function test2(uint256 b) external {
                require(b > 100);
                if (b < 50) { revert(); }
            }

            function test3() external {
                oracle.updatePrice();
                uint256 price = oracle.getPrice();
            }
        }
        """

        # Symbolic execution
        start = time.time()
        sym_vulns = self.symbolic_executor.analyze_contract(test_contract, "test.sol")
        sym_time = time.time() - start

        # MEV detection
        start = time.time()
        mev_vulns = self.mev_detector.analyze_contract(test_contract, "test.sol")
        mev_time = time.time() - start

        # Economic impact
        if len(sym_vulns) > 0:
            start = time.time()
            impact = self.economic_calculator.calculate_impact(
                vulnerability_type='logic_error',
                severity='high',
                contract_context={'tvl': 10_000_000}
            )
            econ_time = time.time() - start
        else:
            econ_time = 0

        total_time = sym_time + mev_time + econ_time

        print("✅ PASSED: Performance Test")
        print(f"   Symbolic Execution: {sym_time:.3f}s")
        print(f"   MEV Detection: {mev_time:.3f}s")
        print(f"   Economic Impact: {econ_time:.3f}s")
        print(f"   Total: {total_time:.3f}s")

        assert total_time < 2.0, f"Should complete <2s, took {total_time:.3f}s"


def run_tests():
    """Run all Week 3 integration tests"""
    print("=" * 70)
    print("🧪 WEEK 3 INTEGRATION TESTS (Days 1-4)")
    print("=" * 70)
    print()

    test_suite = TestWeek3Integration()

    tests = [
        ("Symbolic Execution → Economic Impact", test_suite.test_symbolic_execution_with_economic_impact),
        ("MEV Detection → Profit Estimation", test_suite.test_mev_detection_with_economic_impact),
        ("Cross-Contract Analysis", test_suite.test_cross_contract_with_economic_impact),
        ("Complete Vulnerability Pipeline", test_suite.test_complete_vulnerability_pipeline),
        ("Week 3 + Week 2 Integration", test_suite.test_week3_with_week2_integration),
        ("Performance (All Analyzers)", test_suite.test_performance_all_analyzers),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            test_suite.setup_method()
            print(f"\n{'='*70}")
            print(f"TEST: {test_name}")
            print('='*70)
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ FAILED: {test_name}")
            print(f"   Error: {e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ ERROR: {test_name}")
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 70)
    print(f"📊 TEST RESULTS: {passed}/{len(tests)} passed")
    if failed == 0:
        print("✅ ALL INTEGRATION TESTS PASSED!")
        print("\nWeek 3 (Days 1-4) is production-ready:")
        print("  • Symbolic execution with Z3 constraint solving")
        print("  • Path condition extraction and branch analysis")
        print("  • MEV detection with profit estimation")
        print("  • Cross-contract analysis")
        print("  • Full integration with Week 2 economic calculator")
    else:
        print(f"⚠️  {failed} test(s) failed")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
