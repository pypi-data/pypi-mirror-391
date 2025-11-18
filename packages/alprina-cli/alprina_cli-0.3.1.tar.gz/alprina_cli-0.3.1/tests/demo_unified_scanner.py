#!/usr/bin/env python3
"""
Demo: Unified Security Scanner in Action

Shows the Alprina unified scanner detecting multiple vulnerability types
across Week 1-3 features in a single scan.

Usage:
    python demo_unified_scanner.py
"""

import sys
from pathlib import Path

# Add CLI to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from alprina_cli.unified_scanner import UnifiedScanner, ScanOptions


def demo_simple_contract():
    """Demo 1: Simple contract with overflow"""
    print("\n" + "="*70)
    print("DEMO 1: Simple Token with Integer Overflow")
    print("="*70)

    contract = """
    contract SimpleToken {
        uint256 public totalSupply;

        function mint(uint256 amount) external {
            totalSupply += amount;  // Overflow vulnerability
        }
    }
    """

    scanner = UnifiedScanner()
    options = ScanOptions(
        symbolic=True,
        verbose=True
    )

    report = scanner.scan(contract, "SimpleToken.sol", options)

    print(f"\nResult: Found {report.total_vulnerabilities} vulnerabilities")
    print(f"Scan time: {report.total_scan_time:.3f}s")


def demo_mev_vulnerable():
    """Demo 2: DEX contract with MEV vulnerabilities"""
    print("\n" + "="*70)
    print("DEMO 2: DEX with MEV Vulnerabilities")
    print("="*70)

    contract = """
    contract VulnerableDEX {
        function swap(uint256 amountIn, address[] calldata path) external {
            router.swapExactTokensForTokens(
                amountIn,
                0,  // No slippage protection - SANDWICH ATTACK!
                path,
                msg.sender,
                block.timestamp + 300
            );
        }

        function updateAndSwap() external {
            oracle.updatePrice();  // FRONT-RUNNING opportunity
            uint256 price = oracle.getPrice();
            _swap(price);
        }
    }
    """

    scanner = UnifiedScanner()
    options = ScanOptions(
        mev=True,
        verbose=True
    )

    report = scanner.scan(contract, "VulnerableDEX.sol", options)

    print(f"\nResult: Found {report.total_vulnerabilities} MEV vulnerabilities")
    print(f"Scan time: {report.total_scan_time:.3f}s")


def demo_comprehensive_scan():
    """Demo 3: Comprehensive scan with all analyzers + economic impact"""
    print("\n" + "="*70)
    print("DEMO 3: Comprehensive Scan with Economic Impact")
    print("="*70)

    contract = """
    contract ComprehensiveVulnerable {
        uint256 totalSupply;
        IOracle oracle;

        function mint(uint256 amount) external {
            totalSupply += amount;  // Overflow
        }

        function swap(uint256 amountIn) external {
            router.swap(amountIn, 0, path);  // MEV
        }

        function updatePrice() external {
            oracle.updatePrice();  // Front-running
        }

        function calculate(uint256 a, uint256 b) external returns (uint256) {
            return a / b;  // Division by zero
        }
    }
    """

    scanner = UnifiedScanner()
    options = ScanOptions(
        run_all=True,
        calculate_economic_impact=True,
        tvl=50_000_000,  # $50M TVL
        protocol_type='dex',
        verbose=True
    )

    report = scanner.scan(contract, "Comprehensive.sol", options)

    print(f"\nResults:")
    print(f"  Total vulnerabilities: {report.total_vulnerabilities}")
    print(f"  - Critical: {report.vulnerabilities_by_severity['critical']}")
    print(f"  - High: {report.vulnerabilities_by_severity['high']}")
    print(f"  - Medium: {report.vulnerabilities_by_severity['medium']}")
    print(f"  - Low: {report.vulnerabilities_by_severity['low']}")
    print(f"  Estimated max loss: ${report.total_max_loss:,.0f}")
    print(f"  Average risk score: {report.average_risk_score:.1f}/100")
    print(f"  Scan time: {report.total_scan_time:.3f}s")


def demo_report_generation():
    """Demo 4: Report generation in multiple formats"""
    print("\n" + "="*70)
    print("DEMO 4: Report Generation (JSON & Markdown)")
    print("="*70)

    contract = """
    contract ReportDemo {
        uint256 balance;

        function add(uint256 x) external {
            balance += x;
        }
    }
    """

    scanner = UnifiedScanner()

    # JSON report
    json_options = ScanOptions(
        symbolic=True,
        output_file="/tmp/alprina_demo.json",
        output_format="json",
        verbose=False
    )

    report = scanner.scan(contract, "ReportDemo.sol", json_options)
    print(f"\n✓ JSON report generated: /tmp/alprina_demo.json")

    # Markdown report
    md_options = ScanOptions(
        symbolic=True,
        output_file="/tmp/alprina_demo.md",
        output_format="markdown",
        verbose=False
    )

    report = scanner.scan(contract, "ReportDemo.sol", md_options)
    print(f"✓ Markdown report generated: /tmp/alprina_demo.md")

    print(f"\nBoth reports contain {report.total_vulnerabilities} findings")


def demo_multi_contract():
    """Demo 5: Multi-contract analysis with cross-contract detection"""
    print("\n" + "="*70)
    print("DEMO 5: Multi-Contract Cross-Contract Analysis")
    print("="*70)

    contracts = {
        "Vault": """
        contract Vault {
            mapping(address => uint256) balances;

            function withdraw(uint256 amount) external {
                (bool success, ) = msg.sender.call{value: amount}("");
                balances[msg.sender] -= amount;  // After external call!
            }
        }
        """,
        "Proxy": """
        contract Proxy {
            address implementation;

            function upgrade(address newImpl) external {
                implementation = newImpl;  // No access control!
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

    scanner = UnifiedScanner()
    options = ScanOptions(
        run_all=True,
        cross_contract=True,
        verbose=True
    )

    report = scanner.scan_multi_contract(contracts, "MultiContract.sol", options)

    print(f"\nResults:")
    print(f"  Contracts analyzed: {len(contracts)}")
    print(f"  Total vulnerabilities: {report.total_vulnerabilities}")
    print(f"  Analyzers used: {len(report.vulnerabilities_by_analyzer)}")
    print(f"  Scan time: {report.total_scan_time:.3f}s")


def main():
    """Run all demos"""
    print("\n" + "="*70)
    print("🚀 ALPRINA UNIFIED SCANNER DEMO")
    print("="*70)
    print("\nWeek 4 Day 1: Unified CLI Integration")
    print("Demonstrating all-in-one security scanning with:")
    print("  • Symbolic Execution (Z3)")
    print("  • MEV Detection")
    print("  • Cross-Contract Analysis")
    print("  • Economic Impact Calculation")
    print("  • Multi-Format Reporting")

    try:
        # Run demos
        demo_simple_contract()
        demo_mev_vulnerable()
        demo_comprehensive_scan()
        demo_report_generation()
        demo_multi_contract()

        # Final summary
        print("\n" + "="*70)
        print("✅ DEMO COMPLETE")
        print("="*70)
        print("\nAll unified scanner features demonstrated!")
        print("\nTry it yourself:")
        print("  alprina scan contract.sol --all --tvl 10000000 --protocol dex")
        print("\nAvailable flags:")
        print("  --all              Run all analyzers")
        print("  --symbolic         Symbolic execution only")
        print("  --mev              MEV detection only")
        print("  --cross-contract   Cross-contract analysis")
        print("  --tvl AMOUNT       Calculate economic impact")
        print("  --protocol TYPE    Protocol type (dex, lending, bridge)")
        print("  --format FORMAT    Output format (json, markdown, text)")
        print("  --verbose          Show detailed output")

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
