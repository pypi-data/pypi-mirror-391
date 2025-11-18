#!/usr/bin/env python3
"""
Integration Test Suite for Gas Optimizer and Unified Scanner
Tests on real-world contract patterns
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from alprina_cli.agents.web3_auditor.gas_optimizer import GasOptimizationAnalyzer
from alprina_cli.unified_scanner import UnifiedScanner, ScanOptions


def load_contract(filename):
    """Load a contract file"""
    contract_path = Path(__file__).parent / filename
    with open(contract_path, 'r') as f:
        return f.read()


def test_gas_optimizer_erc20():
    """Test gas optimizer on ERC20 contract"""
    print("\n" + "="*70)
    print("TEST 1: Gas Optimizer on SimpleERC20")
    print("="*70)

    contract_code = load_contract("SimpleERC20.sol")
    analyzer = GasOptimizationAnalyzer()

    optimizations = analyzer.analyze_contract(contract_code, "SimpleERC20.sol")

    print(f"\n✅ Found {len(optimizations)} gas optimizations")

    # Group by severity
    high = [o for o in optimizations if o.severity == "high"]
    medium = [o for o in optimizations if o.severity == "medium"]
    low = [o for o in optimizations if o.severity == "low"]

    print(f"   - High: {len(high)}")
    print(f"   - Medium: {len(medium)}")
    print(f"   - Low: {len(low)}")

    # Calculate total savings
    total_gas_saved = sum(o.gas_saved for o in optimizations)
    total_usd_saved = sum(o.usd_saved_per_tx for o in optimizations)

    print(f"\n💰 Potential Savings:")
    print(f"   - Gas: {total_gas_saved:,}")
    print(f"   - USD per tx: ${total_usd_saved:.2f}")

    # Show top 3 optimizations
    print(f"\n📋 Top 3 Optimizations:")
    sorted_opts = sorted(optimizations, key=lambda o: o.gas_saved, reverse=True)

    for i, opt in enumerate(sorted_opts[:3], 1):
        print(f"\n   {i}. {opt.title} ({opt.severity})")
        print(f"      Line: {opt.line_number}")
        print(f"      Gas Saved: {opt.gas_saved:,}")
        print(f"      Recommendation: {opt.recommendation[:100]}...")

    # Validate expected optimizations
    expected_optimizations = {
        "constant": False,  # name, symbol, decimals could be constant
        "immutable": False,  # owner could be immutable
        "external": False,  # public functions could be external
        "loop": False,      # loop optimization in batchMint
    }

    for opt in optimizations:
        if "constant" in opt.title.lower():
            expected_optimizations["constant"] = True
        if "immutable" in opt.title.lower():
            expected_optimizations["immutable"] = True
        if "external" in opt.title.lower():
            expected_optimizations["external"] = True
        if "loop" in opt.title.lower():
            expected_optimizations["loop"] = True

    print(f"\n🔍 Expected Optimizations Found:")
    for opt_type, found in expected_optimizations.items():
        status = "✅" if found else "⚠️"
        print(f"   {status} {opt_type}: {found}")

    return len(optimizations) > 0


def test_gas_optimizer_swap():
    """Test gas optimizer on AMM/Swap contract"""
    print("\n" + "="*70)
    print("TEST 2: Gas Optimizer on SimpleSwap")
    print("="*70)

    contract_code = load_contract("SimpleSwap.sol")
    analyzer = GasOptimizationAnalyzer()

    optimizations = analyzer.analyze_contract(contract_code, "SimpleSwap.sol")

    print(f"\n✅ Found {len(optimizations)} gas optimizations")

    high = [o for o in optimizations if o.severity == "high"]
    medium = [o for o in optimizations if o.severity == "medium"]
    low = [o for o in optimizations if o.severity == "low"]

    print(f"   - High: {len(high)}")
    print(f"   - Medium: {len(medium)}")
    print(f"   - Low: {len(low)}")

    total_gas_saved = sum(o.gas_saved for o in optimizations)
    total_usd_saved = sum(o.usd_saved_per_tx for o in optimizations)

    print(f"\n💰 Potential Savings:")
    print(f"   - Gas: {total_gas_saved:,}")
    print(f"   - USD per tx: ${total_usd_saved:.2f}")

    # Check for immutable token addresses
    has_immutable = any("immutable" in opt.title.lower() and "token" in opt.title.lower()
                        for opt in optimizations)

    print(f"\n🔍 Key Checks:")
    print(f"   {'✅' if has_immutable else '⚠️'} Immutable token addresses: {has_immutable}")

    return len(optimizations) > 0


def test_gas_optimizer_staking():
    """Test gas optimizer on Staking contract"""
    print("\n" + "="*70)
    print("TEST 3: Gas Optimizer on SimpleStaking")
    print("="*70)

    contract_code = load_contract("SimpleStaking.sol")
    analyzer = GasOptimizationAnalyzer()

    optimizations = analyzer.analyze_contract(contract_code, "SimpleStaking.sol")

    print(f"\n✅ Found {len(optimizations)} gas optimizations")

    high = [o for o in optimizations if o.severity == "high"]
    medium = [o for o in optimizations if o.severity == "medium"]
    low = [o for o in optimizations if o.severity == "low"]

    print(f"   - High: {len(high)}")
    print(f"   - Medium: {len(medium)}")
    print(f"   - Low: {len(low)}")

    total_gas_saved = sum(o.gas_saved for o in optimizations)
    total_usd_saved = sum(o.usd_saved_per_tx for o in optimizations)

    print(f"\n💰 Potential Savings:")
    print(f"   - Gas: {total_gas_saved:,}")
    print(f"   - USD per tx: ${total_usd_saved:.2f}")

    # Look for loop optimizations (very important for distributeRewardsToAll)
    loop_opts = [o for o in optimizations if "loop" in o.title.lower()]

    print(f"\n🔍 Critical Optimizations:")
    print(f"   Loop optimizations found: {len(loop_opts)}")

    for opt in loop_opts:
        print(f"   - {opt.title}: saves {opt.gas_saved:,} gas")

    return len(optimizations) > 0


def test_unified_scanner_all():
    """Test unified scanner with --all flag"""
    print("\n" + "="*70)
    print("TEST 4: Unified Scanner with --all on SimpleERC20")
    print("="*70)

    contract_code = load_contract("SimpleERC20.sol")
    scanner = UnifiedScanner()

    options = ScanOptions(
        run_all=True,
        calculate_economic_impact=False,
        parallel=True,
        verbose=True
    )

    report = scanner.scan(contract_code, "SimpleERC20.sol", options)

    print(f"\n✅ Scan completed in {report.total_scan_time:.2f}s")
    print(f"\n📊 Results:")
    print(f"   Total vulnerabilities: {report.total_vulnerabilities}")
    print(f"   By severity:")
    for severity, count in report.vulnerabilities_by_severity.items():
        if count > 0:
            print(f"     - {severity}: {count}")

    print(f"\n   By analyzer:")
    for analyzer, count in report.vulnerabilities_by_analyzer.items():
        print(f"     - {analyzer}: {count}")

    print(f"\n⏱️  Analyzer Performance:")
    for analyzer, time_taken in report.analyzer_times.items():
        print(f"     - {analyzer}: {time_taken:.3f}s")

    if report.errors:
        print(f"\n⚠️  Errors:")
        for error in report.errors:
            print(f"     - {error}")

    return report.success


def test_report_generation():
    """Test report generation in different formats"""
    print("\n" + "="*70)
    print("TEST 5: Report Generation (JSON, Markdown, Text)")
    print("="*70)

    contract_code = load_contract("SimpleERC20.sol")
    scanner = UnifiedScanner()

    output_dir = Path(__file__).parent / "test_reports"
    output_dir.mkdir(exist_ok=True)

    # Test JSON report
    print("\n📄 Generating JSON report...")
    options = ScanOptions(
        run_all=True,
        calculate_economic_impact=False,
        output_file=str(output_dir / "report.json"),
        output_format="json",
        verbose=False
    )
    report = scanner.scan(contract_code, "SimpleERC20.sol", options)
    json_exists = (output_dir / "report.json").exists()
    print(f"   {'✅' if json_exists else '❌'} JSON report created")

    # Test Markdown report
    print("\n📄 Generating Markdown report...")
    options.output_file = str(output_dir / "report.md")
    options.output_format = "markdown"
    report = scanner.scan(contract_code, "SimpleERC20.sol", options)
    md_exists = (output_dir / "report.md").exists()
    print(f"   {'✅' if md_exists else '❌'} Markdown report created")

    # Test Text report
    print("\n📄 Generating Text report...")
    options.output_file = str(output_dir / "report.txt")
    options.output_format = "text"
    report = scanner.scan(contract_code, "SimpleERC20.sol", options)
    txt_exists = (output_dir / "report.txt").exists()
    print(f"   {'✅' if txt_exists else '❌'} Text report created")

    # Show file sizes
    if json_exists:
        size = (output_dir / "report.json").stat().st_size
        print(f"\n   JSON size: {size:,} bytes")
    if md_exists:
        size = (output_dir / "report.md").stat().st_size
        print(f"   Markdown size: {size:,} bytes")
    if txt_exists:
        size = (output_dir / "report.txt").stat().st_size
        print(f"   Text size: {size:,} bytes")

    return json_exists and md_exists and txt_exists


def test_multi_contract_scanning():
    """Test scanning multiple contracts"""
    print("\n" + "="*70)
    print("TEST 6: Multi-Contract Scanning")
    print("="*70)

    # Load all contracts
    contracts = {
        "SimpleERC20": load_contract("SimpleERC20.sol"),
        "SimpleSwap": load_contract("SimpleSwap.sol"),
        "SimpleStaking": load_contract("SimpleStaking.sol")
    }

    scanner = UnifiedScanner()

    options = ScanOptions(
        static_analysis=True,
        gas_optimization=True,
        cross_contract=True,
        calculate_economic_impact=False,
        parallel=False,
        verbose=True
    )

    print(f"\n🔍 Scanning {len(contracts)} contracts...")

    report = scanner.scan_multi_contract(contracts, "test_contracts", options)

    print(f"\n✅ Scan completed in {report.total_scan_time:.2f}s")
    print(f"\n📊 Results:")
    print(f"   Total vulnerabilities: {report.total_vulnerabilities}")
    print(f"   By severity:")
    for severity, count in report.vulnerabilities_by_severity.items():
        if count > 0:
            print(f"     - {severity}: {count}")

    # Show vulnerabilities per contract
    contract_vulns = {}
    for vuln in report.vulnerabilities:
        contract = vuln.file_path.split(":")[-1] if ":" in vuln.file_path else "unknown"
        contract_vulns[contract] = contract_vulns.get(contract, 0) + 1

    print(f"\n   By contract:")
    for contract, count in contract_vulns.items():
        print(f"     - {contract}: {count}")

    return report.success


def run_all_tests():
    """Run all integration tests"""
    print("\n" + "🚀 "*35)
    print("ALPRINA GAS OPTIMIZER & UNIFIED SCANNER")
    print("Integration Test Suite")
    print("🚀 "*35)

    results = {}

    try:
        results["gas_erc20"] = test_gas_optimizer_erc20()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        results["gas_erc20"] = False

    try:
        results["gas_swap"] = test_gas_optimizer_swap()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        results["gas_swap"] = False

    try:
        results["gas_staking"] = test_gas_optimizer_staking()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        results["gas_staking"] = False

    try:
        results["unified_all"] = test_unified_scanner_all()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        results["unified_all"] = False

    try:
        results["report_gen"] = test_report_generation()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        results["report_gen"] = False

    try:
        results["multi_contract"] = test_multi_contract_scanning()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        results["multi_contract"] = False

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")

    total = len(results)
    passed = sum(1 for p in results.values() if p)

    print(f"\n📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Ready for deployment.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Fix before deployment.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
