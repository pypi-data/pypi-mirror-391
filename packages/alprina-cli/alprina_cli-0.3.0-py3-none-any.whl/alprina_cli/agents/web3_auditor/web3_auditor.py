"""
Web3/DeFi Security Auditor Agent

Enterprise-grade smart contract security analysis combining:
1. Static vulnerability detection (OWASP Smart Contract Top 10)
2. Economic risk assessment (AI-enhanced)
3. Multi-chain support (Ethereum, Solana, Polygon, BSC)
4. Flash loan attack vector analysis
5. Real-time DeFi protocol monitoring
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from .solidity_analyzer import SolidityStaticAnalyzer, SolidityVulnerability
from .defi_risk_assessor import DeFiRiskAssessor, EconomicRisk, EconomicRiskType
from .multi_chain_scanner import MultiChainScanner, BlockchainType

# LLM Enhancement (optional)
try:
    from ..llm_enhancer import LLMEnhancer
    from ..llm_config import LLMConfig
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

class VulnerabilitySeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high" 
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class Web3SecurityReport:
    """Comprehensive Web3 security report"""
    agent: str
    status: str
    blockchain_type: str
    contracts_scanned: List[str]
    vulnerabilities: List[Dict[str, Any]]
    economic_risks: List[Dict[str, Any]] 
    risk_score: int
    exploit_simulation: List[Dict[str, Any]]
    recommendations: List[str]
    summary: Dict[str, int]
    confidence_score: float

class Web3AuditorAgent:
    """
    Web3/DeFi Security Auditor - Startup-focused blockchain security analysis
    
    Comprehensive security testing for smart contracts and DeFi protocols
    """
    
    def __init__(self):
        self.name = "Web3/DeFi Security Auditor"
        self.agent_type = "web3-security"
        self.description = "Enterprise-grade Web3 smart contract security analysis with AI-enhanced economic risk assessment"
        
        # Core analysis engines
        self.solidity_analyzer = SolidityStaticAnalyzer()
        self.defi_assessor = DeFiRiskAssessor()
        self.multi_chain_scanner = MultiChainScanner()
        
        # Vulnerability databases
        self.exploit_database = self._initialize_exploit_database()
        self.owasp_patterns = self._load_owasp_smart_contract_patterns()
        
        # Supported blockchain platforms
        self.supported_chains = [
            BlockchainType.ETHEREUM,
            BlockchainType.POLYGON,
            BlockchainType.BSC,
            BlockchainType.AVALANCHE,
            BlockchainType.ARBITRUM,
            BlockchainType.OPTIMISM
        ]
    
    def analyze_directory(self, directory_path: str) -> Web3SecurityReport:
        """
        Analyze a directory of smart contracts
        
        Args:
            directory_path: Path to directory containing smart contracts
            
        Returns:
            Comprehensive Web3 security report
        """
        directory = Path(directory_path)
        
        if not directory.exists():
            return self._error_report(f"Directory not found: {directory_path}")
        
        # Discover smart contracts
        contract_files = self._discover_contract_files(directory)
        
        if not contract_files:
            return self._error_report(f"No smart contracts found in {directory_path}")
        
        all_vulnerabilities = []
        all_economic_risks = []
        contracts_scanned = []
        
        # Analyze each contract file
        for contract_file in contract_files:
            try:
                contract_report = self.analyze_contract_file(contract_file)
                
                all_vulnerabilities.extend(contract_report.get('vulnerabilities', []))
                all_economic_risks.extend(contract_report.get('economic_risks', []))
                
                if contract_report.get('contracts'):
                    contracts_scanned.extend(contract_report['contracts'])
                    
            except Exception as e:
                error_vuln = {
                    'severity': 'low',
                    'type': 'Analysis Error',
                    'title': f'Failed to analyze {contract_file}',
                    'description': str(e),
                    'file_path': str(contract_file),
                    'confidence': 20
                }
                all_vulnerabilities.append(error_vuln)
        
        # Calculate risk scores
        overall_risk_score = self._calculate_overall_risk_score(all_vulnerabilities, all_economic_risks)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(all_vulnerabilities, all_economic_risks)
        
        # Mock exploit simulation results
        exploit_simulation = self._simulate_exploit_scenarios(all_vulnerabilities, all_economic_risks)
        
        return Web3SecurityReport(
            agent=self.name,
            status="success",
            blockchain_type="multi-chain",
            contracts_scanned=list(set(contracts_scanned)),
            vulnerabilities=self._format_vulnerabilities(all_vulnerabilities),
            economic_risks=self._format_economic_risks(all_economic_risks),
            risk_score=overall_risk_score,
            exploit_simulation=exploit_simulation,
            recommendations=recommendations,
            summary= self._generate_summary(all_vulnerabilities, all_economic_risks),
            confidence_score=self._calculate_confidence_score(all_vulnerabilities, all_economic_risks)
        )
    
    def analyze_contract_file(self, file_path: str, blockchain_type: str = "ethereum") -> Dict[str, Any]:
        """
        Analyze a single smart contract file
        
        Args:
            file_path: Path to contract file
            blockchain_type: Target blockchain platform
            
        Returns:
            Analysis results for the contract
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {
                'status': 'error',
                'error': f'File not found: {file_path}',
                'vulnerabilities': [],
                'economic_risks': [],
                'contracts': []
            }
        
        try:
            contract_code = file_path.read_text(encoding='utf-8')
            
            # Detect contract language
            contract_language = self._detect_contract_language(file_path, contract_code)
            
            if contract_language == "solidity":
                return self._analyze_solidity_contract(contract_code, str(file_path))
            elif contract_language == "solana":
                return self._analyze_solana_contract(contract_code, str(file_path))
            else:
                return self._analyze_generic_contract(contract_code, str(file_path))
                
        except Exception as e:
            return {
                'status': 'error',
                'error': f'Failed to analyze {file_path}: {str(e)}',
                'vulnerabilities': [],
                'economic_risks': [],
                'contracts': []
            }
    
    def _analyze_solidity_contract(self, contract_code: str, file_path: str) -> Dict[str, Any]:
        """Analyze Solidity smart contract"""
        
        # Static analysis
        static_vulnerabilities = self.solidity_analyzer.analyze_contract(contract_code, file_path)
        
        # Economic risk assessment
        protocol_context = {
            'file_path': file_path,
            'language': 'solidity',
            'protocol_type': self._infer_protocol_type(contract_code)
        }
        economic_risks = self.defi_assessor.assess_economic_risks(contract_code, protocol_context)
        
        # Extract contract names
        contract_names = self._extract_contract_names(contract_code)
        
        return {
            'status': 'success',
            'language': 'solidity',
            'contracts': contract_names,
            'vulnerabilities': static_vulnerabilities,
            'economic_risks': economic_risks
        }
    
    def _analyze_solana_contract(self, contract_code: str, file_path: str) -> Dict[str, Any]:
        """Analyze Solana program (Rust)"""
        
        # Placeholder for Solana analysis - would implement Rust static analysis
        vulnerabilities = []
        economic_risks = []
        
        # Basic Solana-specific checks
        rust_patterns = [
            ('unsafe', 'code', 'high', 'Unsafe block detected - potential security risk'),
            ('vec', 'memory', 'medium', 'Vector usage may cause memory issues'),
            ('unwrap', 'error', 'medium', 'unwrap() calls may panic on error'),
        ]
        
        lines = contract_code.split('\n')
        for i, line in enumerate(lines):
            for pattern, vuln_type, severity, description in rust_patterns:
                if pattern in line:
                    vulnerabilities.append({
                        'vulnerability_type': vuln_type,
                        'severity': severity,
                        'title': f'{vuln_type.title()} Risk',
                        'description': description,
                        'file_path': file_path,
                        'line_number': i + 1,
                        'contract_name': 'solana_program',
                        'code_snippet': line.strip(),
                        'confidence': 70
                    })
        
        program_names = self._extract_rust_program_names(contract_code)
        
        return {
            'status': 'success',
            'language': 'rust',
            'contracts': program_names,
            'vulnerabilities': vulnerabilities,
            'economic_risks': economic_risks
        }
    
    def _analyze_generic_contract(self, contract_code: str, file_path: str) -> Dict[str, Any]:
        """Analyze generic smart contract (fallback logic)"""
        
        vulnerabilities = []
        economic_risks = []
        
        # Basic pattern matching for common contract patterns
        suspicious_patterns = [
            ('transfer', 'security', 'medium', 'Transfer function detected - manual audit recommended'),
            ('balance', 'security', 'medium', 'Balance manipulation detected'),
            ('owner', 'access', 'medium', 'Owner function - verify access controls'),
        ]
        
        lines = contract_code.split('\n')
        for i, line in enumerate(lines):
            for pattern, category, severity, description in suspicious_patterns:
                if pattern in line.lower():
                    vulnerabilities.append({
                        'vulnerability_type': category,
                        'severity': severity,
                        'title': f'{category.title()} Pattern',
                        'description': description,
                        'file_path': file_path,
                        'line_number': i + 1,
                        'contract_name': 'unknown',
                        'code_snippet': line.strip(),
                        'confidence': 50
                    })
        
        return {
            'status': 'success',
            'language': 'unknown',
            'contracts': ['generic_contract'],
            'vulnerabilities': vulnerabilities,
            'economic_risks': economic_risks
        }
    
    def _discover_contract_files(self, directory: Path) -> List[Path]:
        """Discover smart contract files in directory"""
        contract_files = []
        
        # Solidity files
        sol_patterns = list(directory.rglob("*.sol"))
        contract_files.extend(sol_patterns)

        # Solana/Rust files
        rs_patterns = []
        for rust_file in directory.rglob("*.rs"):
            # Check if it's likely a Solana program
            rust_content = rust_file.read_text(encoding='utf-8', errors='ignore')
            if any(solana_keyword in rust_content for solana_keyword in ['sol_program', 'account_info', 'pubkey']):
                rs_patterns.append(rust_file)
        contract_files.extend(rs_patterns)

        # Move files
        move_patterns = list(directory.rglob("*.move"))
        contract_files.extend(move_patterns)
        
        return contract_files
    
    def _detect_contract_language(self, file_path: Path, contract_code: str) -> str:
        """Detect smart contract programming language"""
        
        file_extension = file_path.suffix.lower()
        
        if file_extension == '.sol':
            return 'solidity'
        elif file_extension == '.rs':
            if 'sol_program' in contract_code or 'account_info' in contract_code:
                return 'solana'
            else:
                return 'rust'
        elif file_extension == '.move':
            return 'move'
        else:
            # Try to detect from content
            if any(keyword in contract_code for keyword in ['contract', 'function', 'modifier']):
                return 'solidity'
            elif any(keyword in contract_code for keyword in ['program', 'account_info', 'pubkey']):
                return 'solana'
            else:
                return 'unknown'
    
    def _extract_contract_names(self, contract_code: str) -> List[str]:
        """Extract contract names from Solidity code"""
        import re
        contract_pattern = r'(abstract\s+)?contract\s+(\w+)'
        contracts = re.findall(contract_pattern, contract_code)
        return [name for _, name in contracts]
    
    def _extract_rust_program_names(self, contract_code: str) -> List[str]:
        """Extract program names from Solana Rust code"""
        import re
        program_pattern = r'sol_program!\s*\[(.*?)\]\s*fn\s*(\w+)'
        programs = re.findall(program_pattern, contract_code)
        return [name for _, name in programs]
    
    def _infer_protocol_type(self, contract_code: str) -> str:
        """Infer DeFi protocol type from contract code"""
        contract_lower = contract_code.lower()
        
        if any(token in contract_lower for token in ['uniswap', 'swap', 'liquidity']):
            return 'Decentralized Exchange (DEX)'
        elif any(token in contract_lower for token in ['lending', 'borrow', 'interest']):
            return 'Lending Protocol'
        elif any(token in contract_lower for token in ['price', 'oracle', 'feed']):
            return 'Price Oracle'
        elif any(token in contract_lower for token in ['governance', 'vote', 'propose']):
            return 'Governance Protocol'
        elif any(token in contract_lower for token in ['token', 'mint', 'burn']):
            return 'Token Contract'
        else:
            return 'General DeFi Protocol'
    
    def _calculate_overall_risk_score(self, vulnerabilities: List, economic_risks: List) -> int:
        """Calculate overall risk score 0-100"""
        if not vulnerabilities and not economic_risks:
            return 0
        
        severity_weights = {
            'critical': 25,
            'high': 15,
            'medium': 8,
            'low': 3
        }
        
        # Calculate vulnerability score
        vulnerability_score = sum(
            severity_weights.get(vuln.get('severity', 'low'), 3)
            for vuln in vulnerabilities
        )
        
        # Economic risks are weighted higher as they typically have bigger impact
        economic_risk_score = sum(
            severity_weights.get(risk.get('severity', 'medium'), 8) * 1.2
            for risk in economic_risks
        )
        
        total_score = vulnerability_score + economic_risk_score
        return min(100, int(total_score))
    
    def _generate_recommendations(self, vulnerabilities: List, economic_risks: List) -> List[str]:
        """Generate actionable security recommendations"""
        recommendations = []
        
        # Based on vulnerability types
        vuln_types = {v.get('vulnerability_type') for v in vulnerabilities}
        
        if 'reentrancy' in vuln_types:
            recommendations.append("Implement ReentrancyGuard modifier and follow checks-effects-interactions pattern")
        
        if 'access_control' in vuln_types:
            recommendations.append("Review and implement proper access control for all critical functions")
        
        if 'integer_overflow_underflow' in vuln_types:
            recommendations.append("Use SafeMath library or Solidity 0.8+ which has built-in overflow protection")
        
        # Based on economic risk types  
        economic_types = {r.get('risk_type') for r in economic_risks}
        
        if EconomicRiskType.FLASH_LOAN_ATTACK.value in economic_types:
            recommendations.append("Implement flash loan protection and validate price calculations")
        
        if EconomicRiskType.PRICE_ORACLE_MANIPULATION.value in economic_types:
            recommendations.append("Use multiple oracle sources and implement price deviation checks")
        
        if EconomicRiskType.LIQUIDITY_DRAIN.value in economic_types:
            recommendations.append("Add withdrawal limits and implement emergency pause mechanisms")
        
        # General recommendations
        recommendations.extend([
            "Consider professional security audit before mainnet deployment",
            "Implement comprehensive testing including fuzzing and property-based testing",
            "Set up monitoring and alerting for suspicious activities"
        ])
        
        return list(set(recommendations))  # Remove duplicates
    
    def _simulate_exploit_scenarios(self, vulnerabilities: List, economic_risks: List) -> List[Dict[str, Any]]:
        """Simulate potential exploit scenarios"""
        scenarios = []
        
        # Flash loan attack simulation
        flash_loan_vulns = [v for v in vulnerabilities if v.get('vulnerability_type') == 'reentrancy']
        if flash_loan_vulns:
            scenarios.append({
                'attack_type': 'Flash Loan Manipulation',
                'probability': 'High',
                'potential_loss': 'Complete fund drain',
                'description': 'Attacker uses flash loan to manipulate prices and exploit reentrancy',
                'prevention': 'Add reentrancy protection and price validation'
            })
        
        # Governance attack simulation
        governance_vulns = [v for v in vulnerabilities if v.get('vulnerability_type') == 'access_control']
        if governance_vulns:
            scenarios.append({
                'attack_type': 'Governance Takeover',
                'probability': 'Medium',
                'potential_loss': 'Protocol control loss',
                'description': 'Attaker gains voting power and passes malicious proposals',
                'prevention': 'Implement voting time-locks and access controls'
            })
        
        return scenarios
    
    def _generate_summary(self, vulnerabilities: List, economic_risks: List) -> Dict[str, int]:
        """Generate summary statistics"""
        summary = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        }
        
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'low')
            summary[severity] = summary.get(severity, 0) + 1
        
        for risk in economic_risks:
            severity = risk.get('severity', 'medium')
            summary[severity] = summary.get(severity, 0) + 1
        
        return summary
    
    def _calculate_confidence_score(self, vulnerabilities: List, economic_risks: List) -> float:
        """Calculate confidence score for analysis accuracy"""
        if not vulnerabilities and not economic_risks:
            return 100.0  # High confidence if no issues found
        
        total_findings = len(vulnerabilities) + len(economic_risks)
        confidence_sum = sum(v.get('confidence', 70) for v in vulnerabilities) + \
                       sum(r.get('confidence', 80) for r in economic_risks)
        
        return min(100.0, round(confidence_sum / total_findings, 1))
    
    def _format_vulnerabilities(self, vulnerabilities: List) -> List[Dict[str, Any]]:
        """Format vulnerabilities for JSON serialization"""
        return [v if isinstance(v, dict) else asdict(v) for v in vulnerabilities]
    
    def _format_economic_risks(self, economic_risks: List) -> List[Dict[str, Any]]:
        """Format economic risks for JSON serialization"""
        return [r if isinstance(r, dict) else asdict(r) for r in economic_risks]
    
    def _error_report(self, error_message: str) -> Web3SecurityReport:
        """Generate error report"""
        return Web3SecurityReport(
            agent=self.name,
            status="error", 
            blockchain_type="unknown",
            contracts_scanned=[],
            vulnerabilities=[],
            economic_risks=[],
            risk_score=0,
            exploit_simulation=[],
            recommendations=["Verify file path and ensure smart contracts are present"],
            summary={'error': 1},
            confidence_score=0.0
        )
    
    def _initialize_exploit_database(self) -> Dict[str, Any]:
        """Initialize historical exploit database"""
        return {
            'flash_loan_attacks': {
                "bzx_exploit_2020": "Attacker used flash loan to manipulate BZX price oracles",
                "harvest_finance_2020": "Flash loan manipulation exploited pricing mechanism",
                "pancakebunny_2022": "Flash loan attack on PancakeBunny liquidity pool"
            },
            'access_control_breaches': {
                "parsec_finance_2022": "Access control bug allowed unlimited minting",
                "iron_finance_2021": "Access control vulnerability in token contract"
            },
            'oracle_manipulation': {
                "cream_finance_2021": "Oracle manipulation led to financial losses"
            }
        }
    
    def _load_owasp_smart_contract_patterns(self) -> Dict[str, List[str]]:
        """Load OWASP Smart Contract Top 10 patterns"""
        return {
            "reentrancy": ["call", "send", "transfer"],
            "access_control": ["onlyOwner", "require", "if"],
            "arithmetic": ["+", "-", "*", "/"],
            "unchecked_calls": [".call(", ".delegatecall("],
            "logic_errors": ["require", "revert", "assert"],
            "oracles": ["uniswap", "chainlink", "price"],
            "gas": ["gas", "block.gaslimit"]
        }

# Integration wrapper for existing agent system
class Web3AuditorAgentWrapper:
    """Integration wrapper for Web3/DeFi Security Auditor Agent"""
    
    def __init__(self):
        self.name = "Web3/DeFi Security Auditor"
        self.agent_type = "web3-security"
        self.description = "Enterprise-grade Web3 smart contract security analysis with AI-enhanced economic risk assessment"
        self.auditor = Web3AuditorAgent()

        # LLM enhancer (optional)
        self.llm_enhancer = None
        self.llm_enabled = False

        if LLM_AVAILABLE:
            try:
                from loguru import logger
                self.llm_enhancer = LLMEnhancer()
                self.llm_enabled = True
                logger.info("✅ LLM enhancement enabled (Claude AI)")
            except Exception as e:
                from loguru import logger
                logger.info(f"LLM enhancement disabled: {e}")
    
    def analyze(self, target: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze target for Web3 security vulnerabilities
        
        Args:
            target: Path to directory or file to analyze
            options: Additional analysis options
            
        Returns:
            Dict containing analysis results
        """
        try:
            target_path = Path(target)
            
            if target_path.is_file():
                # Single file analysis
                blockchain_type = options.get('blockchain', 'ethereum') if options else 'ethereum'
                result = self.auditor.analyze_contract_file(target, blockchain_type)

                # Convert single file result to full report format
                contracts = result.get('contracts', ['unknown'])
                vulnerabilities = [v if isinstance(v, dict) else asdict(v)
                                 for v in result.get('vulnerabilities', [])]
                economic_risks = [r if isinstance(r, dict) else asdict(r)
                                for r in result.get('economic_risks', [])]

                # ENHANCE with LLM if enabled
                if self.llm_enabled and vulnerabilities:
                    vulnerabilities = self._enhance_vulnerabilities_with_llm(
                        vulnerabilities,
                        target_path.read_text(encoding='utf-8')
                    )
                
                # Count LLM-enhanced vulnerabilities
                llm_enhanced_count = sum(
                    1 for v in vulnerabilities if v.get('llm_enhanced', False)
                )

                return {
                    'agent': self.name,
                    'status': result.get('status', 'error'),
                    'blockchain_type': blockchain_type,
                    'contracts_scanned': contracts,
                    'risk_score': self._calculate_single_file_risk_score(vulnerabilities, economic_risks),
                    'vulnerabilities_count': len(vulnerabilities),
                    'economic_risks_count': len(economic_risks),
                    'vulnerabilities': vulnerabilities,
                    'economic_risks': economic_risks,
                    'summary': self._generate_single_file_summary(vulnerabilities, economic_risks),
                    'recommendations': self._generate_recommendations(vulnerabilities, economic_risks),
                    'llm_enhanced': self.llm_enabled,
                    'llm_enhanced_count': llm_enhanced_count
                }
                
            else:
                # Directory analysis
                report = self.auditor.analyze_directory(target)
                
                return {
                    'agent': self.name,
                    'status': report.status,
                    'blockchain_type': report.blockchain_type,
                    'contracts_scanned': report.contracts_scanned,
                    'risk_score': report.risk_score,
                    'vulnerabilities_count': len(report.vulnerabilities),
                    'economic_risks_count': len(report.economic_risks),
                    'vulnerabilities': report.vulnerabilities,
                    'economic_risks': report.economic_risks,
                    'summary': report.summary,
                    'recommendations': report.recommendations,
                    'confidence_score': report.confidence_score,
                    'exploit_simulation': report.exploit_simulation
                }
                
        except Exception as e:
            return {
                'agent': self.name,
                'status': 'error',
                'error': str(e),
                'vulnerabilities_count': 0,
                'economic_risks_count': 0,
                'risk_score': 0
            }
    
    def _calculate_single_file_risk_score(self, vulnerabilities: List, economic_risks: List) -> int:
        """Calculate risk score for single file analysis"""
        if not vulnerabilities and not economic_risks:
            return 0
        
        weights = {'critical': 25, 'high': 15, 'medium': 8, 'low': 3}
        vuln_score = sum(weights.get(v.get('severity', 'low'), 3) for v in vulnerabilities)
        econ_score = sum(weights.get(r.get('severity', 'medium'), 8) * 1.2 for r in economic_risks)
        
        return min(100, int(vuln_score + econ_score))
    
    def _generate_single_file_summary(self, vulnerabilities: List, economic_risks: List) -> Dict[str, int]:
        """Generate summary for single file analysis"""
        summary = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'low')
            summary[severity] = summary.get(severity, 0) + 1
            
        for risk in economic_risks:
            severity = risk.get('severity', 'medium')
            summary[severity] = summary.get(severity, 0) + 1
        
        return summary
    
    def _generate_recommendations(self, vulnerabilities: List, economic_risks: List) -> List[str]:
        """Generate recommendations for single file analysis"""
        recommendations = []

        if any(v.get('vulnerability_type') == 'reentrancy' for v in vulnerabilities):
            recommendations.append("Implement ReentrancyGuard modifier")

        if any(v.get('vulnerability_type') == 'access_control' for v in vulnerabilities):
            recommendations.append("Review and fix access control mechanisms")

        if any(r.get('risk_type') in ['flash_loan_attack', 'price_oracle_manipulation'] for r in economic_risks):
            recommendations.append("Implement flash loan protection and oracle validation")

        recommendations.extend([
            "Consider professional security audit",
            "Add comprehensive testing",
            "Implement monitoring and alerting"
        ])

        return list(set(recommendations))

    def _enhance_vulnerabilities_with_llm(
        self,
        vulnerabilities: List[Dict[str, Any]],
        contract_code: str
    ) -> List[Dict[str, Any]]:
        """
        Enhance vulnerabilities with LLM analysis

        Args:
            vulnerabilities: List of vulnerability dictionaries
            contract_code: Full contract source code

        Returns:
            Enhanced vulnerability list
        """
        from loguru import logger

        if not self.llm_enhancer or not vulnerabilities:
            return vulnerabilities

        # Sort vulnerabilities by severity (critical/high first)
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        sorted_vulns = sorted(
            vulnerabilities,
            key=lambda v: severity_order.get(v.get('severity', 'low'), 4)
        )

        enhanced_vulns = []
        enhanced_count = 0

        for vuln in vulnerabilities:
            # Only enhance top 5 critical/high vulnerabilities (cost optimization)
            should_enhance = (
                vuln in sorted_vulns[:LLMConfig.MAX_VULNS_TO_ENHANCE] and
                vuln.get('severity', '').lower() in ['critical', 'high', 'medium']
            )

            if should_enhance and enhanced_count < LLMConfig.MAX_VULNS_TO_ENHANCE:
                try:
                    # Enhance with LLM
                    enhanced = self.llm_enhancer.enhance_vulnerability(vuln, contract_code)
                    enhanced_dict = enhanced.to_dict()
                    enhanced_vulns.append(enhanced_dict)
                    enhanced_count += 1
                    logger.debug(f"✅ Enhanced: {vuln.get('title', 'Unknown')}")
                except Exception as e:
                    logger.warning(f"LLM enhancement failed for {vuln.get('title', 'Unknown')}: {e}")
                    enhanced_vulns.append(vuln)
            else:
                # Keep original vulnerability without enhancement
                enhanced_vulns.append(vuln)

        logger.info(f"LLM enhanced {enhanced_count}/{len(vulnerabilities)} vulnerabilities")
        return enhanced_vulns
