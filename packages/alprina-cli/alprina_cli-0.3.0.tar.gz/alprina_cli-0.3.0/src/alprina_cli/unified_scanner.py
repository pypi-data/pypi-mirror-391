"""
Unified Security Scanner - Week 4 Day 1

Orchestrates all Week 1-3 security analyzers:
- Week 1: PPE Detection, CVE Database
- Week 2: Oracle Manipulation, Input Validation, Economic Impact
- Week 3: Symbolic Execution, MEV Detection, Cross-Contract Analysis

Author: Alprina Development Team
Date: 2025-11-13
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple
from enum import Enum
import json
from pathlib import Path
from datetime import datetime

# Import all Week 1-4 analyzers
try:
    from .agents.web3_auditor.symbolic_executor import SymbolicExecutor
    from .agents.web3_auditor.mev_detector import MEVDetector
    from .agents.web3_auditor.cross_contract_analyzer import CrossContractAnalyzer
    from .agents.web3_auditor.economic_impact_calculator import EconomicImpactCalculator
    from .agents.web3_auditor.gas_optimizer import GasOptimizationAnalyzer  # Week 4 Day 3
    from .agents.web3_auditor.solidity_analyzer import (
        SolidityStaticAnalyzer,
        SolidityVulnerability,
        VulnerabilityType
    )
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from agents.web3_auditor.symbolic_executor import SymbolicExecutor
    from agents.web3_auditor.mev_detector import MEVDetector
    from agents.web3_auditor.cross_contract_analyzer import CrossContractAnalyzer
    from agents.web3_auditor.economic_impact_calculator import EconomicImpactCalculator
    from agents.web3_auditor.gas_optimizer import GasOptimizationAnalyzer  # Week 4 Day 3
    from agents.web3_auditor.solidity_analyzer import (
        SolidityStaticAnalyzer,
        SolidityVulnerability,
        VulnerabilityType
    )


class AnalyzerType(Enum):
    """Types of security analyzers"""
    SYMBOLIC_EXECUTION = "symbolic"
    MEV_DETECTION = "mev"
    CROSS_CONTRACT = "cross_contract"
    ORACLE_MANIPULATION = "oracle"
    INPUT_VALIDATION = "input_validation"
    ECONOMIC_IMPACT = "economic"
    STATIC_ANALYSIS = "static"
    GAS_OPTIMIZATION = "gas"  # Week 4 Day 3


@dataclass
class ScanOptions:
    """Options for unified security scan"""
    # Analyzer selection
    run_all: bool = False
    symbolic: bool = False
    mev: bool = False
    cross_contract: bool = False
    oracle: bool = False
    input_validation: bool = False
    static_analysis: bool = True  # Always run by default
    gas_optimization: bool = False  # Week 4 Day 3

    # Economic impact options
    calculate_economic_impact: bool = True
    tvl: Optional[float] = None  # Total Value Locked
    protocol_type: Optional[str] = None  # dex, lending, bridge, etc.

    # Output options
    output_file: Optional[str] = None
    output_format: str = "json"  # json, html, markdown, text
    verbose: bool = False

    # Performance options
    parallel: bool = True
    max_workers: int = 4
    timeout_per_analyzer: int = 60  # seconds


@dataclass
class VulnerabilityReport:
    """Unified vulnerability report from all analyzers"""
    # Vulnerability details
    id: str
    title: str
    severity: str  # critical, high, medium, low
    description: str
    file_path: str
    line_number: Optional[int] = None
    function_name: Optional[str] = None

    # Source analyzer
    analyzer_type: AnalyzerType = AnalyzerType.STATIC_ANALYSIS

    # Economic impact (if calculated)
    estimated_loss_min: Optional[float] = None
    estimated_loss_max: Optional[float] = None
    risk_score: Optional[float] = None

    # Evidence
    code_snippet: Optional[str] = None
    proof: Optional[str] = None  # Z3 proof, attack scenario, etc.

    # Remediation
    recommendation: str = ""
    references: List[str] = field(default_factory=list)

    # Metadata
    detection_time: float = 0.0  # seconds
    confidence: str = "high"  # high, medium, low


@dataclass
class ScanReport:
    """Complete security scan report"""
    # Scan metadata
    scan_id: str
    timestamp: datetime
    contract_files: List[str]
    scan_options: ScanOptions

    # Results
    vulnerabilities: List[VulnerabilityReport]
    total_vulnerabilities: int
    vulnerabilities_by_severity: Dict[str, int]
    vulnerabilities_by_analyzer: Dict[str, int]

    # Economic impact summary
    total_max_loss: float = 0.0
    average_risk_score: float = 0.0

    # Performance metrics
    total_scan_time: float = 0.0
    analyzer_times: Dict[str, float] = field(default_factory=dict)

    # Status
    success: bool = True
    errors: List[str] = field(default_factory=list)


class UnifiedScanner:
    """
    Unified Security Scanner

    Orchestrates all Week 1-3 security analyzers with:
    - Parallel execution for performance
    - Result aggregation and deduplication
    - Economic impact calculation
    - Multi-format report generation
    """

    def __init__(self):
        """Initialize all analyzers"""
        self.symbolic_executor = SymbolicExecutor()
        self.mev_detector = MEVDetector()
        self.cross_contract_analyzer = CrossContractAnalyzer()
        self.economic_calculator = EconomicImpactCalculator()
        self.static_analyzer = SolidityStaticAnalyzer()
        self.gas_optimizer = GasOptimizationAnalyzer()  # Week 4 Day 3

        self.scan_start_time = 0.0
        self.vulnerabilities: List[VulnerabilityReport] = []

    def scan(
        self,
        contract_code: str,
        file_path: str,
        options: ScanOptions
    ) -> ScanReport:
        """
        Run unified security scan

        Args:
            contract_code: Solidity source code
            file_path: Path to contract file
            options: Scan options

        Returns:
            ScanReport with all findings
        """
        self.scan_start_time = time.time()
        self.vulnerabilities = []
        errors = []
        analyzer_times = {}

        # Determine which analyzers to run
        analyzers_to_run = self._select_analyzers(options)

        if options.verbose:
            print(f"\n🔍 Alprina Security Scan")
            print(f"{'='*60}")
            print(f"Contract: {file_path}")
            if options.tvl:
                print(f"Protocol: {options.protocol_type or 'unknown'} (${options.tvl:,.0f} TVL)")
            print(f"Analyzers: {', '.join([a.value for a in analyzers_to_run])}")
            print(f"\n⏳ Scanning...\n")

        # Run analyzers in parallel or sequentially
        if options.parallel and len(analyzers_to_run) > 1:
            results = self._run_parallel(
                contract_code,
                file_path,
                analyzers_to_run,
                options
            )
        else:
            results = self._run_sequential(
                contract_code,
                file_path,
                analyzers_to_run,
                options
            )

        # Process results
        for analyzer_type, result in results.items():
            if result['success']:
                analyzer_times[analyzer_type.value] = result['time']
                self._process_analyzer_results(
                    result['vulnerabilities'],
                    analyzer_type,
                    file_path,
                    result['time']
                )
            else:
                errors.append(f"{analyzer_type.value}: {result['error']}")

        # Calculate economic impact if requested
        if options.calculate_economic_impact and options.tvl:
            self._calculate_economic_impact_for_all(options)

        # Deduplicate vulnerabilities
        self.vulnerabilities = self._deduplicate_vulnerabilities(self.vulnerabilities)

        # Sort by severity and risk score
        self.vulnerabilities = self._sort_vulnerabilities(self.vulnerabilities)

        # Generate report
        total_time = time.time() - self.scan_start_time

        report = self._generate_report(
            file_path,
            options,
            total_time,
            analyzer_times,
            errors
        )

        # Save report if output file specified
        if options.output_file:
            self._save_report(report, options.output_file, options.output_format)

        return report

    def scan_multi_contract(
        self,
        contracts: Dict[str, str],
        file_path: str,
        options: ScanOptions
    ) -> ScanReport:
        """
        Run unified security scan on multiple contracts

        Args:
            contracts: Dict of {contract_name: source_code}
            file_path: Base file path
            options: Scan options

        Returns:
            ScanReport with all findings
        """
        self.scan_start_time = time.time()
        self.vulnerabilities = []
        errors = []
        analyzer_times = {}

        # Run single-contract analyzers on each contract
        for contract_name, contract_code in contracts.items():
            single_options = ScanOptions(
                symbolic=options.symbolic,
                mev=options.mev,
                static_analysis=options.static_analysis,
                calculate_economic_impact=False,  # Calculate later
                parallel=False,  # Already parallelizing at top level
                verbose=False
            )

            analyzers = self._select_analyzers(single_options)

            results = self._run_sequential(
                contract_code,
                f"{file_path}:{contract_name}",
                analyzers,
                single_options
            )

            for analyzer_type, result in results.items():
                if result['success']:
                    self._process_analyzer_results(
                        result['vulnerabilities'],
                        analyzer_type,
                        f"{file_path}:{contract_name}",
                        result['time']
                    )

        # Run cross-contract analysis
        if options.cross_contract:
            start = time.time()
            try:
                cross_vulns = self.cross_contract_analyzer.analyze_contracts(
                    contracts,
                    file_path
                )
                elapsed = time.time() - start
                analyzer_times['cross_contract'] = elapsed

                self._process_analyzer_results(
                    cross_vulns,
                    AnalyzerType.CROSS_CONTRACT,
                    file_path,
                    elapsed
                )
            except Exception as e:
                errors.append(f"cross_contract: {str(e)}")

        # Calculate economic impact
        if options.calculate_economic_impact and options.tvl:
            self._calculate_economic_impact_for_all(options)

        # Deduplicate and sort
        self.vulnerabilities = self._deduplicate_vulnerabilities(self.vulnerabilities)
        self.vulnerabilities = self._sort_vulnerabilities(self.vulnerabilities)

        # Generate report
        total_time = time.time() - self.scan_start_time

        report = self._generate_report(
            file_path,
            options,
            total_time,
            analyzer_times,
            errors
        )

        if options.output_file:
            self._save_report(report, options.output_file, options.output_format)

        return report

    def _select_analyzers(self, options: ScanOptions) -> List[AnalyzerType]:
        """Determine which analyzers to run based on options"""
        analyzers = []

        if options.run_all:
            return [
                AnalyzerType.STATIC_ANALYSIS,
                AnalyzerType.SYMBOLIC_EXECUTION,
                AnalyzerType.MEV_DETECTION,
                AnalyzerType.INPUT_VALIDATION,
                AnalyzerType.ORACLE_MANIPULATION,
                AnalyzerType.GAS_OPTIMIZATION,  # Week 4 Day 3
            ]

        if options.static_analysis:
            analyzers.append(AnalyzerType.STATIC_ANALYSIS)

        if options.symbolic:
            analyzers.append(AnalyzerType.SYMBOLIC_EXECUTION)

        if options.mev:
            analyzers.append(AnalyzerType.MEV_DETECTION)

        if options.input_validation:
            analyzers.append(AnalyzerType.INPUT_VALIDATION)

        if options.oracle:
            analyzers.append(AnalyzerType.ORACLE_MANIPULATION)

        if options.gas_optimization:
            analyzers.append(AnalyzerType.GAS_OPTIMIZATION)

        return analyzers

    def _run_parallel(
        self,
        contract_code: str,
        file_path: str,
        analyzers: List[AnalyzerType],
        options: ScanOptions
    ) -> Dict[AnalyzerType, Dict]:
        """Run analyzers in parallel"""
        results = {}

        with ThreadPoolExecutor(max_workers=options.max_workers) as executor:
            futures = {}

            for analyzer_type in analyzers:
                future = executor.submit(
                    self._run_analyzer,
                    analyzer_type,
                    contract_code,
                    file_path
                )
                futures[future] = analyzer_type

            for future in as_completed(futures, timeout=options.timeout_per_analyzer * len(analyzers)):
                analyzer_type = futures[future]
                try:
                    result = future.result(timeout=options.timeout_per_analyzer)
                    results[analyzer_type] = result
                except Exception as e:
                    results[analyzer_type] = {
                        'success': False,
                        'error': str(e),
                        'time': 0.0,
                        'vulnerabilities': []
                    }

        return results

    def _run_sequential(
        self,
        contract_code: str,
        file_path: str,
        analyzers: List[AnalyzerType],
        options: ScanOptions
    ) -> Dict[AnalyzerType, Dict]:
        """Run analyzers sequentially"""
        results = {}

        for analyzer_type in analyzers:
            try:
                result = self._run_analyzer(analyzer_type, contract_code, file_path)
                results[analyzer_type] = result
            except Exception as e:
                results[analyzer_type] = {
                    'success': False,
                    'error': str(e),
                    'time': 0.0,
                    'vulnerabilities': []
                }

        return results

    def _run_analyzer(
        self,
        analyzer_type: AnalyzerType,
        contract_code: str,
        file_path: str
    ) -> Dict:
        """Run a single analyzer"""
        start = time.time()

        try:
            if analyzer_type == AnalyzerType.STATIC_ANALYSIS:
                vulns = self.static_analyzer.analyze_contract(contract_code, file_path)

            elif analyzer_type == AnalyzerType.SYMBOLIC_EXECUTION:
                vulns = self.symbolic_executor.analyze_contract(contract_code, file_path)

            elif analyzer_type == AnalyzerType.MEV_DETECTION:
                vulns = self.mev_detector.analyze_contract(contract_code, file_path)

            elif analyzer_type == AnalyzerType.INPUT_VALIDATION:
                # Use static analyzer's input validation
                all_vulns = self.static_analyzer.analyze_contract(contract_code, file_path)
                vulns = [v for v in all_vulns if 'input' in v.title.lower() or 'validation' in v.title.lower()]

            elif analyzer_type == AnalyzerType.ORACLE_MANIPULATION:
                # Use static analyzer's oracle checks
                all_vulns = self.static_analyzer.analyze_contract(contract_code, file_path)
                vulns = [v for v in all_vulns if 'oracle' in v.title.lower() or 'price' in v.title.lower()]

            elif analyzer_type == AnalyzerType.GAS_OPTIMIZATION:
                # Week 4 Day 3: Gas optimization analysis
                gas_opts = self.gas_optimizer.analyze_contract(contract_code, file_path)
                # Convert GasOptimization objects to SolidityVulnerability-like objects
                vulns = []
                for opt in gas_opts:
                    # Create a simple object that matches the expected interface
                    class GasVuln:
                        def __init__(self, opt):
                            self.title = opt.title
                            self.severity = opt.severity
                            self.description = opt.description
                            self.line_number = opt.line_number
                            self.function_name = opt.function_name
                            self.code_snippet = opt.code_before
                            self.remediation = opt.recommendation
                            self.confidence = 100
                    vulns.append(GasVuln(opt))

            else:
                vulns = []

            elapsed = time.time() - start

            return {
                'success': True,
                'time': elapsed,
                'vulnerabilities': vulns,
                'error': None
            }

        except Exception as e:
            elapsed = time.time() - start
            return {
                'success': False,
                'time': elapsed,
                'vulnerabilities': [],
                'error': str(e)
            }

    def _process_analyzer_results(
        self,
        vulnerabilities: List[SolidityVulnerability],
        analyzer_type: AnalyzerType,
        file_path: str,
        detection_time: float
    ):
        """Convert analyzer vulnerabilities to unified format"""
        for vuln in vulnerabilities:
            report = VulnerabilityReport(
                id=f"{analyzer_type.value}_{len(self.vulnerabilities)}",
                title=vuln.title,
                severity=vuln.severity,
                description=vuln.description,
                file_path=file_path,
                line_number=vuln.line_number,
                function_name=vuln.function_name,
                analyzer_type=analyzer_type,
                code_snippet=vuln.code_snippet,
                proof=vuln.code_snippet if vuln.code_snippet and 'Z3' in str(vuln.code_snippet) else None,
                recommendation=getattr(vuln, 'remediation', 'Review and fix this vulnerability'),
                references=getattr(vuln, 'references', []),
                detection_time=detection_time,
                confidence="high" if getattr(vuln, 'confidence', 100) >= 80 else "medium"
            )

            self.vulnerabilities.append(report)

    def _calculate_economic_impact_for_all(self, options: ScanOptions):
        """Calculate economic impact for all vulnerabilities"""
        contract_context = {
            'tvl': options.tvl,
            'protocol_type': options.protocol_type or 'generic'
        }

        for vuln in self.vulnerabilities:
            # Map vulnerability type
            vuln_type = self._map_vulnerability_type(vuln.title)

            try:
                impact = self.economic_calculator.calculate_impact(
                    vulnerability_type=vuln_type,
                    severity=vuln.severity,
                    contract_context=contract_context
                )

                vuln.estimated_loss_min = impact.estimated_loss_usd[0]
                vuln.estimated_loss_max = impact.estimated_loss_usd[1]
                vuln.risk_score = impact.risk_score

            except Exception:
                # Skip if economic calculation fails
                pass

    def _map_vulnerability_type(self, title: str) -> str:
        """Map vulnerability title to economic impact type"""
        title_lower = title.lower()

        if 'reentrancy' in title_lower:
            return 'reentrancy'
        elif 'overflow' in title_lower or 'underflow' in title_lower:
            return 'integer_overflow'
        elif 'oracle' in title_lower:
            return 'oracle_manipulation'
        elif 'access' in title_lower or 'authorization' in title_lower:
            return 'access_control'
        elif 'mev' in title_lower or 'front' in title_lower or 'sandwich' in title_lower:
            return 'frontrunning_mev'
        else:
            return 'logic_error'

    def _deduplicate_vulnerabilities(
        self,
        vulnerabilities: List[VulnerabilityReport]
    ) -> List[VulnerabilityReport]:
        """Remove duplicate vulnerabilities"""
        seen: Set[Tuple[str, str, Optional[int]]] = set()
        unique = []

        for vuln in vulnerabilities:
            key = (vuln.title, vuln.file_path, vuln.line_number)

            if key not in seen:
                seen.add(key)
                unique.append(vuln)

        return unique

    def _sort_vulnerabilities(
        self,
        vulnerabilities: List[VulnerabilityReport]
    ) -> List[VulnerabilityReport]:
        """Sort vulnerabilities by severity and risk score"""
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}

        return sorted(
            vulnerabilities,
            key=lambda v: (
                severity_order.get(v.severity, 999),
                -(v.risk_score or 0)
            )
        )

    def _generate_report(
        self,
        file_path: str,
        options: ScanOptions,
        total_time: float,
        analyzer_times: Dict[str, float],
        errors: List[str]
    ) -> ScanReport:
        """Generate final scan report"""
        # Count vulnerabilities by severity
        by_severity = {
            'critical': sum(1 for v in self.vulnerabilities if v.severity == 'critical'),
            'high': sum(1 for v in self.vulnerabilities if v.severity == 'high'),
            'medium': sum(1 for v in self.vulnerabilities if v.severity == 'medium'),
            'low': sum(1 for v in self.vulnerabilities if v.severity == 'low')
        }

        # Count vulnerabilities by analyzer
        by_analyzer = {}
        for vuln in self.vulnerabilities:
            analyzer = vuln.analyzer_type.value
            by_analyzer[analyzer] = by_analyzer.get(analyzer, 0) + 1

        # Calculate economic metrics
        total_max_loss = sum(
            v.estimated_loss_max or 0
            for v in self.vulnerabilities
        )

        risk_scores = [v.risk_score for v in self.vulnerabilities if v.risk_score]
        average_risk_score = sum(risk_scores) / len(risk_scores) if risk_scores else 0.0

        return ScanReport(
            scan_id=f"alprina_{int(time.time())}",
            timestamp=datetime.now(),
            contract_files=[file_path],
            scan_options=options,
            vulnerabilities=self.vulnerabilities,
            total_vulnerabilities=len(self.vulnerabilities),
            vulnerabilities_by_severity=by_severity,
            vulnerabilities_by_analyzer=by_analyzer,
            total_max_loss=total_max_loss,
            average_risk_score=average_risk_score,
            total_scan_time=total_time,
            analyzer_times=analyzer_times,
            success=len(errors) == 0,
            errors=errors
        )

    def _save_report(self, report: ScanReport, output_file: str, format: str):
        """Save report to file"""
        if format == "json":
            self._save_json_report(report, output_file)
        elif format == "html":
            self._save_html_report(report, output_file)
        elif format == "markdown":
            self._save_markdown_report(report, output_file)
        else:
            self._save_text_report(report, output_file)

    def _save_json_report(self, report: ScanReport, output_file: str):
        """Save JSON report"""
        data = {
            'scan_id': report.scan_id,
            'timestamp': report.timestamp.isoformat(),
            'contract_files': report.contract_files,
            'total_vulnerabilities': report.total_vulnerabilities,
            'by_severity': report.vulnerabilities_by_severity,
            'by_analyzer': report.vulnerabilities_by_analyzer,
            'total_max_loss': report.total_max_loss,
            'average_risk_score': report.average_risk_score,
            'scan_time': report.total_scan_time,
            'vulnerabilities': [
                {
                    'id': v.id,
                    'title': v.title,
                    'severity': v.severity,
                    'description': v.description,
                    'file_path': v.file_path,
                    'line_number': v.line_number,
                    'function_name': v.function_name,
                    'analyzer': v.analyzer_type.value,
                    'estimated_loss_min': v.estimated_loss_min,
                    'estimated_loss_max': v.estimated_loss_max,
                    'risk_score': v.risk_score,
                    'code_snippet': v.code_snippet,
                    'recommendation': v.recommendation,
                    'references': v.references
                }
                for v in report.vulnerabilities
            ]
        }

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _save_markdown_report(self, report: ScanReport, output_file: str):
        """Save Markdown report"""
        lines = [
            f"# Alprina Security Scan Report",
            f"",
            f"**Scan ID**: {report.scan_id}",
            f"**Timestamp**: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Contract**: {', '.join(report.contract_files)}",
            f"**Scan Time**: {report.total_scan_time:.2f}s",
            f"",
            f"## Summary",
            f"",
            f"- **Total Vulnerabilities**: {report.total_vulnerabilities}",
            f"- **Critical**: {report.vulnerabilities_by_severity['critical']}",
            f"- **High**: {report.vulnerabilities_by_severity['high']}",
            f"- **Medium**: {report.vulnerabilities_by_severity['medium']}",
            f"- **Low**: {report.vulnerabilities_by_severity['low']}",
            f"",
        ]

        if report.total_max_loss > 0:
            lines.extend([
                f"### Economic Impact",
                f"",
                f"- **Estimated Max Loss**: ${report.total_max_loss:,.0f}",
                f"- **Average Risk Score**: {report.average_risk_score:.1f}/100",
                f"",
            ])

        lines.append(f"## Vulnerabilities\n")

        for severity in ['critical', 'high', 'medium', 'low']:
            severity_vulns = [v for v in report.vulnerabilities if v.severity == severity]

            if severity_vulns:
                lines.append(f"### {severity.upper()} ({len(severity_vulns)})\n")

                for vuln in severity_vulns:
                    lines.extend([
                        f"#### {vuln.title}",
                        f"",
                        f"- **File**: {vuln.file_path}:{vuln.line_number or '?'}",
                        f"- **Function**: {vuln.function_name or 'N/A'}",
                        f"- **Analyzer**: {vuln.analyzer_type.value}",
                    ])

                    if vuln.estimated_loss_max:
                        lines.append(f"- **Financial Impact**: ${vuln.estimated_loss_min:,.0f} - ${vuln.estimated_loss_max:,.0f}")

                    lines.extend([
                        f"",
                        f"{vuln.description}",
                        f"",
                        f"**Recommendation**: {vuln.recommendation}",
                        f"",
                    ])

        with open(output_file, 'w') as f:
            f.write('\n'.join(lines))

    def _save_html_report(self, report: ScanReport, output_file: str):
        """Save HTML report (placeholder)"""
        # TODO: Implement HTML report generation
        self._save_markdown_report(report, output_file.replace('.html', '.md'))

    def _save_text_report(self, report: ScanReport, output_file: str):
        """Save text report"""
        lines = [
            "=" * 70,
            "ALPRINA SECURITY SCAN REPORT",
            "=" * 70,
            "",
            f"Scan ID: {report.scan_id}",
            f"Timestamp: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Contract: {', '.join(report.contract_files)}",
            f"Scan Time: {report.total_scan_time:.2f}s",
            "",
            "SUMMARY",
            "=" * 70,
            f"Total Vulnerabilities: {report.total_vulnerabilities}",
            f"  - Critical: {report.vulnerabilities_by_severity['critical']}",
            f"  - High: {report.vulnerabilities_by_severity['high']}",
            f"  - Medium: {report.vulnerabilities_by_severity['medium']}",
            f"  - Low: {report.vulnerabilities_by_severity['low']}",
            "",
        ]

        if report.total_max_loss > 0:
            lines.extend([
                "ECONOMIC IMPACT",
                "=" * 70,
                f"Estimated Max Loss: ${report.total_max_loss:,.0f}",
                f"Average Risk Score: {report.average_risk_score:.1f}/100",
                "",
            ])

        lines.append("VULNERABILITIES\n" + "=" * 70 + "\n")

        for i, vuln in enumerate(report.vulnerabilities, 1):
            icon = "🔴" if vuln.severity == "critical" else "🟠" if vuln.severity == "high" else "🟡" if vuln.severity == "medium" else "⚪"

            lines.extend([
                f"{i}. {icon} {vuln.title} [{vuln.severity.upper()}]",
                f"   File: {vuln.file_path}:{vuln.line_number or '?'}",
                f"   Analyzer: {vuln.analyzer_type.value}",
            ])

            if vuln.estimated_loss_max:
                lines.append(f"   Financial Impact: ${vuln.estimated_loss_min:,.0f} - ${vuln.estimated_loss_max:,.0f}")

            lines.append("")

        with open(output_file, 'w') as f:
            f.write('\n'.join(lines))
