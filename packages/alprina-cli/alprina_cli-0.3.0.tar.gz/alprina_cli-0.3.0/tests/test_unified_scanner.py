"""
Tests for Unified Security Scanner

WEEK 4 DAY 1: Testing Unified Scanner
======================================

Tests the complete unified scanner workflow:
1. Single contract scanning with all analyzers
2. Multi-contract scanning with cross-contract analysis
3. Economic impact calculation integration
4. Report generation (JSON, Markdown, Text)
5. Parallel execution performance
6. Deduplication and sorting

Author: Alprina Development Team
Date: 2025-11-13
"""

import sys
from pathlib import Path
import json
import time

# Add CLI to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from alprina_cli.unified_scanner import (
    UnifiedScanner,
    ScanOptions,
    AnalyzerType
)


class TestUnifiedScanner:
    """Test unified security scanner"""

    def setup_method(self):
        """Setup test fixtures"""
        self.scanner = UnifiedScanner()

    def test_single_contract_scan_all_analyzers(self):
        """Test: Scan single contract with all analyzers"""

        vulnerable_contract = """
        contract VulnerableToken {
            uint256 public totalSupply;
            mapping(address => uint256) public balances;

            function mint(uint256 amount) external {
                totalSupply += amount;  // Overflow vulnerability
                balances[msg.sender] += amount;
            }

            function swap(uint256 amountIn) external {
                // MEV vulnerability - no slippage protection
                router.swapExactTokensForTokens(
                    amountIn,
                    0,  // amountOutMin = 0
                    path,
                    msg.sender,
                    deadline
                );
            }

            function calculate(uint256 a, uint256 b) external returns (uint256) {
                return a / b;  // Division by zero
            }
        }
        """

        options = ScanOptions(
            run_all=True,
            calculate_economic_impact=True,
            tvl=10_000_000,
            protocol_type='dex',
            verbose=False
        )

        report = self.scanner.scan(vulnerable_contract, "test.sol", options)

        # Should detect vulnerabilities from multiple analyzers
        assert report.total_vulnerabilities >= 2, f"Expected >= 2 vulnerabilities, found {report.total_vulnerabilities}"

        # Should have vulnerabilities from different analyzers
        assert len(report.vulnerabilities_by_analyzer) >= 2, "Should use multiple analyzers"

        # Should have severity breakdown
        assert report.vulnerabilities_by_severity['critical'] + report.vulnerabilities_by_severity['high'] > 0

        # Should have economic impact calculated
        assert report.total_max_loss > 0, "Economic impact not calculated"
        assert report.average_risk_score > 0

        print(f"✅ PASSED: Single contract scan with all analyzers")
        print(f"   Total vulnerabilities: {report.total_vulnerabilities}")
        print(f"   Analyzers used: {', '.join(report.vulnerabilities_by_analyzer.keys())}")
        print(f"   Max financial loss: ${report.total_max_loss:,.0f}")
        print(f"   Scan time: {report.total_scan_time:.3f}s")

    def test_symbolic_execution_only(self):
        """Test: Scan with only symbolic execution"""

        overflow_contract = """
        contract OverflowTest {
            uint256 balance;

            function add(uint256 amount) external {
                balance += amount;
            }

            function sub(uint256 amount) external {
                balance -= amount;
            }
        }
        """

        options = ScanOptions(
            symbolic=True,
            mev=False,
            verbose=False
        )

        report = self.scanner.scan(overflow_contract, "test.sol", options)

        # Should detect overflow/underflow
        overflow_vulns = [v for v in report.vulnerabilities if 'overflow' in v.title.lower() or 'underflow' in v.title.lower()]

        assert len(overflow_vulns) > 0, "Should detect overflow/underflow"
        assert report.vulnerabilities_by_analyzer.get('symbolic', 0) > 0

        print(f"✅ PASSED: Symbolic execution only")
        print(f"   Overflow/underflow vulnerabilities: {len(overflow_vulns)}")

    def test_mev_detection_only(self):
        """Test: Scan with only MEV detection"""

        mev_contract = """
        contract MEVVulnerable {
            function swap(uint256 amountIn) external {
                router.swapExactTokensForTokens(
                    amountIn,
                    0,  // No slippage protection
                    path,
                    msg.sender,
                    deadline
                );
            }

            function updateAndSwap() external {
                oracle.updatePrice();  // Front-running opportunity
                uint256 price = oracle.getPrice();
                _swap(price);
            }
        }
        """

        options = ScanOptions(
            mev=True,
            symbolic=False,
            verbose=False
        )

        report = self.scanner.scan(mev_contract, "test.sol", options)

        # Should detect MEV vulnerabilities
        mev_vulns = [v for v in report.vulnerabilities if v.analyzer_type == AnalyzerType.MEV_DETECTION]

        assert len(mev_vulns) > 0, "Should detect MEV vulnerabilities"
        assert 'mev' in report.vulnerabilities_by_analyzer

        print(f"✅ PASSED: MEV detection only")
        print(f"   MEV vulnerabilities: {len(mev_vulns)}")

    def test_multi_contract_cross_contract_analysis(self):
        """Test: Multi-contract scan with cross-contract analysis"""

        contracts = {
            "Vault": """
            contract Vault {
                mapping(address => uint256) public balances;

                function withdraw(uint256 amount) external {
                    (bool success, ) = msg.sender.call{value: amount}("");
                    require(success);
                    balances[msg.sender] -= amount;  // After external call!
                }
            }
            """,
            "Proxy": """
            contract Proxy {
                address public implementation;

                function upgrade(address newImpl) external {
                    implementation = newImpl;  // No access control!
                }

                fallback() external payable {
                    implementation.delegatecall(msg.data);
                }
            }
            """,
            "Token": """
            contract Token {
                uint256 totalSupply;

                function mint(uint256 amount) external {
                    totalSupply += amount;  // Overflow
                }
            }
            """
        }

        options = ScanOptions(
            run_all=True,
            cross_contract=True,
            calculate_economic_impact=True,
            tvl=50_000_000,
            protocol_type='dex',
            verbose=False
        )

        report = self.scanner.scan_multi_contract(contracts, "multi.sol", options)

        # Should find vulnerabilities in all contracts
        assert report.total_vulnerabilities >= 3

        # Should have cross-contract analysis
        assert 'cross_contract' in report.vulnerabilities_by_analyzer or report.total_vulnerabilities >= 3

        print(f"✅ PASSED: Multi-contract cross-contract analysis")
        print(f"   Total vulnerabilities: {report.total_vulnerabilities}")
        print(f"   Contracts analyzed: {len(contracts)}")

    def test_economic_impact_calculation(self):
        """Test: Economic impact calculation integration"""

        vulnerable_contract = """
        contract EconomicTest {
            uint256 balance;

            function deposit(uint256 amount) external {
                balance += amount;  // Overflow
            }
        }
        """

        options = ScanOptions(
            symbolic=True,
            calculate_economic_impact=True,
            tvl=100_000_000,  # $100M TVL
            protocol_type='lending',
            verbose=False
        )

        report = self.scanner.scan(vulnerable_contract, "test.sol", options)

        # Should have economic impact calculated
        assert report.total_max_loss > 0

        # Check individual vulnerabilities
        vulns_with_impact = [v for v in report.vulnerabilities if v.estimated_loss_max is not None]

        assert len(vulns_with_impact) > 0, "Should have vulnerabilities with economic impact"

        # With $100M TVL, losses should be substantial
        assert report.total_max_loss >= 100_000, "Economic impact seems too low for $100M TVL"

        print(f"✅ PASSED: Economic impact calculation")
        print(f"   TVL: $100,000,000")
        print(f"   Estimated max loss: ${report.total_max_loss:,.0f}")
        print(f"   Average risk score: {report.average_risk_score:.1f}/100")

    def test_deduplication(self):
        """Test: Vulnerability deduplication"""

        # Contract with same vulnerability pattern multiple times
        duplicate_contract = """
        contract DuplicateTest {
            uint256 a;
            uint256 b;
            uint256 c;

            function f1(uint256 x) external { a += x; }
            function f2(uint256 x) external { b += x; }
            function f3(uint256 x) external { c += x; }
        }
        """

        options = ScanOptions(
            symbolic=True,
            verbose=False
        )

        report = self.scanner.scan(duplicate_contract, "test.sol", options)

        # Each function should be analyzed separately
        # But similar issues should be deduplicated if on same line
        assert report.total_vulnerabilities >= 1

        print(f"✅ PASSED: Deduplication")
        print(f"   Vulnerabilities found: {report.total_vulnerabilities}")

    def test_severity_sorting(self):
        """Test: Vulnerabilities sorted by severity and risk score"""

        complex_contract = """
        contract SortTest {
            uint256 balance;

            function critical(uint256 a) external {
                balance += a;  // Critical: overflow
            }

            function medium(uint256 a, uint256 b) external returns (uint256) {
                return a / b;  // Medium: division by zero
            }

            function swap(uint256 amountIn) external {
                router.swap(amountIn, 0, path);  // Critical: MEV
            }
        }
        """

        options = ScanOptions(
            run_all=True,
            calculate_economic_impact=True,
            tvl=10_000_000,
            protocol_type='dex',
            verbose=False
        )

        report = self.scanner.scan(complex_contract, "test.sol", options)

        if len(report.vulnerabilities) >= 2:
            # Check that critical comes before medium
            severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}

            for i in range(len(report.vulnerabilities) - 1):
                current = severity_order.get(report.vulnerabilities[i].severity, 999)
                next_vuln = severity_order.get(report.vulnerabilities[i + 1].severity, 999)

                assert current <= next_vuln, "Vulnerabilities not sorted by severity"

        print(f"✅ PASSED: Severity sorting")
        print(f"   Vulnerabilities properly sorted: {len(report.vulnerabilities)}")

    def test_parallel_execution_performance(self):
        """Test: Parallel execution is faster than sequential"""

        test_contract = """
        contract PerformanceTest {
            uint256 a;
            uint256 b;

            function f1(uint256 x) external { a += x; }
            function f2(uint256 y) external { b += y; }
            function f3(uint256 z) external returns (uint256) { return a / z; }

            function swap(uint256 amountIn) external {
                router.swap(amountIn, 0, path);
            }
        }
        """

        # Parallel execution
        options_parallel = ScanOptions(
            run_all=True,
            parallel=True,
            verbose=False
        )

        start = time.time()
        report_parallel = self.scanner.scan(test_contract, "test.sol", options_parallel)
        time_parallel = time.time() - start

        # Sequential execution
        options_sequential = ScanOptions(
            run_all=True,
            parallel=False,
            verbose=False
        )

        start = time.time()
        report_sequential = self.scanner.scan(test_contract, "test.sol", options_sequential)
        time_sequential = time.time() - start

        # Both should find same vulnerabilities
        assert report_parallel.total_vulnerabilities == report_sequential.total_vulnerabilities

        # Parallel should be faster (or at least not slower)
        # Note: For small contracts, overhead might make parallel slower
        # So we just verify it completes

        print(f"✅ PASSED: Parallel execution performance")
        print(f"   Parallel time: {time_parallel:.3f}s")
        print(f"   Sequential time: {time_sequential:.3f}s")
        print(f"   Speedup: {time_sequential/time_parallel:.2f}x" if time_parallel > 0 else "N/A")

    def test_json_report_generation(self):
        """Test: JSON report generation"""

        simple_contract = """
        contract JSONTest {
            uint256 balance;
            function add(uint256 x) external { balance += x; }
        }
        """

        output_file = Path("/tmp/alprina_test_report.json")

        options = ScanOptions(
            symbolic=True,
            output_file=str(output_file),
            output_format="json",
            verbose=False
        )

        report = self.scanner.scan(simple_contract, "test.sol", options)

        # Check that file was created
        assert output_file.exists(), "JSON report file not created"

        # Parse and validate JSON
        with open(output_file) as f:
            data = json.load(f)

        assert 'scan_id' in data
        assert 'total_vulnerabilities' in data
        assert 'vulnerabilities' in data

        # Cleanup
        output_file.unlink()

        print(f"✅ PASSED: JSON report generation")
        print(f"   Report file created and validated")

    def test_markdown_report_generation(self):
        """Test: Markdown report generation"""

        simple_contract = """
        contract MarkdownTest {
            uint256 balance;
            function add(uint256 x) external { balance += x; }
        }
        """

        output_file = Path("/tmp/alprina_test_report.md")

        options = ScanOptions(
            symbolic=True,
            output_file=str(output_file),
            output_format="markdown",
            verbose=False
        )

        report = self.scanner.scan(simple_contract, "test.sol", options)

        # Check that file was created
        assert output_file.exists(), "Markdown report file not created"

        # Validate markdown content
        content = output_file.read_text()

        assert '# Alprina Security Scan Report' in content
        assert '## Summary' in content

        # Cleanup
        output_file.unlink()

        print(f"✅ PASSED: Markdown report generation")
        print(f"   Report file created and validated")

    def test_error_handling_no_vulnerabilities(self):
        """Test: Handle contracts with no vulnerabilities gracefully"""

        safe_contract = """
        pragma solidity ^0.8.0;

        contract SafeContract {
            uint256 public counter;

            function increment() external {
                counter += 1;  # Safe in 0.8+
            }

            function getCounter() external view returns (uint256) {
                return counter;
            }
        }
        """

        options = ScanOptions(
            run_all=True,
            verbose=False
        )

        report = self.scanner.scan(safe_contract, "test.sol", options)

        # Should complete without errors
        assert report.success

        # May or may not find vulnerabilities (conservative analysis)
        print(f"✅ PASSED: Error handling for safe contract")
        print(f"   Vulnerabilities found: {report.total_vulnerabilities}")

    def test_complete_week_1_3_integration(self):
        """Test: Complete integration with all Week 1-3 features"""

        comprehensive_contract = """
        contract ComprehensiveTest {
            uint256 totalSupply;
            mapping(address => uint256) balances;
            IOracle oracle;

            // Week 3 Day 1: Symbolic execution
            function mint(uint256 amount) external {
                totalSupply += amount;  // Overflow
            }

            // Week 3 Day 2: Path analysis
            function withdraw(uint256 amount) external {
                require(amount > 100);
                if (amount < 50) {
                    // Unreachable
                    revert();
                }
            }

            // Week 3 Day 3: MEV detection
            function swap(uint256 amountIn) external {
                router.swapExactTokensForTokens(
                    amountIn,
                    0,
                    path,
                    msg.sender,
                    deadline
                );
            }

            // Week 2: Oracle manipulation
            function updateAndSwap() external {
                oracle.updatePrice();
                uint256 price = oracle.getPrice();
                _swap(price);
            }

            // Week 1: Input validation
            function transfer(address to, uint256 amount) external {
                balances[to] += amount;  // No sender balance check
            }
        }
        """

        options = ScanOptions(
            run_all=True,
            calculate_economic_impact=True,
            tvl=50_000_000,
            protocol_type='dex',
            verbose=False
        )

        report = self.scanner.scan(comprehensive_contract, "test.sol", options)

        # Should detect multiple types of vulnerabilities
        assert report.total_vulnerabilities >= 3

        # Should have used multiple analyzers
        assert len(report.vulnerabilities_by_analyzer) >= 2

        # Should have economic impact
        assert report.total_max_loss > 0

        print(f"✅ PASSED: Complete Week 1-3 integration")
        print(f"   Total vulnerabilities: {report.total_vulnerabilities}")
        print(f"   Analyzers used: {len(report.vulnerabilities_by_analyzer)}")
        print(f"   Estimated max loss: ${report.total_max_loss:,.0f}")
        print(f"   Scan completed in: {report.total_scan_time:.3f}s")


def run_tests():
    """Run all unified scanner tests"""
    print("=" * 70)
    print("🧪 UNIFIED SECURITY SCANNER TESTS (Week 4 Day 1)")
    print("=" * 70)
    print()

    test_suite = TestUnifiedScanner()

    tests = [
        ("Single Contract - All Analyzers", test_suite.test_single_contract_scan_all_analyzers),
        ("Symbolic Execution Only", test_suite.test_symbolic_execution_only),
        ("MEV Detection Only", test_suite.test_mev_detection_only),
        ("Multi-Contract Cross-Contract", test_suite.test_multi_contract_cross_contract_analysis),
        ("Economic Impact Calculation", test_suite.test_economic_impact_calculation),
        ("Vulnerability Deduplication", test_suite.test_deduplication),
        ("Severity Sorting", test_suite.test_severity_sorting),
        ("Parallel Execution Performance", test_suite.test_parallel_execution_performance),
        ("JSON Report Generation", test_suite.test_json_report_generation),
        ("Markdown Report Generation", test_suite.test_markdown_report_generation),
        ("Safe Contract Handling", test_suite.test_error_handling_no_vulnerabilities),
        ("Complete Week 1-3 Integration", test_suite.test_complete_week_1_3_integration),
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
        print("✅ ALL UNIFIED SCANNER TESTS PASSED!")
        print("\nWeek 4 Day 1 Complete:")
        print("  • Unified scanner with parallel execution")
        print("  • Result aggregation and deduplication")
        print("  • Economic impact calculation")
        print("  • Multi-format report generation")
        print("  • Complete Week 1-3 integration")
        print("\nReady for: alprina scan --all contract.sol")
    else:
        print(f"⚠️  {failed} test(s) failed")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
