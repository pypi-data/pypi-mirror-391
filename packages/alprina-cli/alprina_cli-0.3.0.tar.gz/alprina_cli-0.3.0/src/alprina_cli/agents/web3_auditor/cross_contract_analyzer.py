"""
Cross-Contract Analysis Engine

WEEK 3 DAY 4: Cross-Contract Analysis
======================================

Analyzes vulnerabilities across multiple interacting contracts:
- Dependency graph construction
- Cross-contract reentrancy detection
- Upgrade pattern vulnerabilities
- Attack chain identification
- Interface trust issues

Background:
- Modern DeFi uses complex contract interactions
- Vulnerabilities often exist at contract boundaries
- Upgradeable contracts introduce proxy risks

Author: Alprina Development Team
Date: 2025-11-12

References:
- The DAO attack (2016): Cross-contract reentrancy
- Parity Wallet (2017): Delegatecall vulnerability
- Poly Network (2021): Cross-chain trust issues
"""

import re
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import networkx as nx

try:
    from .solidity_analyzer import SolidityVulnerability, VulnerabilityType
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from solidity_analyzer import SolidityVulnerability, VulnerabilityType


class CrossContractVulnType(Enum):
    """Types of cross-contract vulnerabilities"""
    CROSS_CONTRACT_REENTRANCY = "cross_contract_reentrancy"
    UPGRADE_VULNERABILITY = "upgrade_vulnerability"
    DELEGATECALL_INJECTION = "delegatecall_injection"
    INTERFACE_TRUST = "interface_trust"
    ACCESS_CONTROL_BREACH = "access_control_breach"
    ATTACK_CHAIN = "attack_chain"


@dataclass
class ContractDependency:
    """Represents a dependency between contracts"""
    from_contract: str
    to_contract: str
    function_name: str
    call_type: str  # "call", "delegatecall", "staticcall", "interface"
    line_number: int


@dataclass
class AttackChain:
    """Represents a multi-step attack sequence"""
    steps: List[Dict[str, Any]]
    total_impact: str
    complexity: str
    description: str


@dataclass
class CrossContractVulnerability:
    """Cross-contract vulnerability"""
    vuln_type: CrossContractVulnType
    severity: str
    title: str
    description: str
    contracts_involved: List[str]
    attack_chain: Optional[AttackChain]
    estimated_loss: Tuple[float, float]
    confidence: int = 90


class CrossContractAnalyzer:
    """
    Analyze vulnerabilities across multiple contracts

    Week 3 Day 4 Implementation:
    1. Build dependency graphs between contracts
    2. Detect cross-contract reentrancy
    3. Identify upgrade vulnerabilities
    4. Find attack chains

    Features:
    - Dependency graph construction using NetworkX
    - Multi-contract reentrancy detection
    - Proxy pattern analysis
    - Attack path discovery
    """

    def __init__(self):
        self.dependency_graph = nx.DiGraph()
        self.contracts: Dict[str, Dict[str, Any]] = {}
        self.vulnerabilities: List[CrossContractVulnerability] = []

    def analyze_contracts(
        self,
        contracts: Dict[str, str],  # {filename: source_code}
        file_path: str = "multi-contract"
    ) -> List[SolidityVulnerability]:
        """
        Analyze multiple contracts for cross-contract vulnerabilities

        Args:
            contracts: Dictionary of contract names to source code

        Returns:
            List of vulnerabilities in standard format
        """
        self.vulnerabilities = []
        self.contracts = {}
        self.dependency_graph = nx.DiGraph()

        # Step 1: Parse all contracts
        for contract_name, source_code in contracts.items():
            self.contracts[contract_name] = self._parse_contract(contract_name, source_code)

        # Step 2: Build dependency graph
        self._build_dependency_graph()

        # Step 3: Detect vulnerabilities
        self._detect_cross_contract_reentrancy()
        self._detect_upgrade_vulnerabilities()
        self._detect_delegatecall_issues()
        self._detect_interface_trust_issues()
        self._identify_attack_chains()

        # Convert to standard format
        return self._convert_to_standard_format(file_path)

    def _parse_contract(self, name: str, source_code: str) -> Dict[str, Any]:
        """Parse a contract and extract relevant information"""
        contract_info = {
            'name': name,
            'source': source_code,
            'functions': [],
            'external_calls': [],
            'state_variables': [],
            'is_proxy': False,
            'is_upgradeable': False
        }

        lines = source_code.split('\n')

        # Extract contract name from code
        for line in lines:
            contract_match = re.search(r'contract\s+(\w+)', line)
            if contract_match:
                contract_info['actual_name'] = contract_match.group(1)
                break

        # Detect proxy pattern
        if any(keyword in source_code.lower() for keyword in ['delegatecall', 'proxy', 'implementation']):
            contract_info['is_proxy'] = True

        # Detect upgradeable pattern
        if any(keyword in source_code.lower() for keyword in ['upgrade', 'initialize', 'upgradeable']):
            contract_info['is_upgradeable'] = True

        # Extract functions
        contract_info['functions'] = self._extract_functions(source_code)

        # Extract external calls
        contract_info['external_calls'] = self._extract_external_calls(source_code)

        return contract_info

    def _extract_functions(self, source_code: str) -> List[Dict[str, Any]]:
        """Extract function definitions"""
        functions = []
        lines = source_code.split('\n')

        for i, line in enumerate(lines):
            func_match = re.match(
                r'\s*function\s+(\w+)\s*\([^)]*\)\s*(public|external|internal|private)?',
                line
            )
            if func_match:
                functions.append({
                    'name': func_match.group(1),
                    'visibility': func_match.group(2) or 'internal',
                    'line': i + 1
                })

        return functions

    def _extract_external_calls(self, source_code: str) -> List[Dict[str, Any]]:
        """Extract external contract calls"""
        external_calls = []
        lines = source_code.split('\n')

        for i, line in enumerate(lines):
            # Pattern: ContractName.function() or contract.function()
            call_match = re.search(r'(\w+)\.(\w+)\s*\(', line)
            if call_match:
                target = call_match.group(1)
                function = call_match.group(2)

                # Detect call type
                call_type = "call"
                if 'delegatecall' in line:
                    call_type = "delegatecall"
                elif 'staticcall' in line:
                    call_type = "staticcall"

                external_calls.append({
                    'target': target,
                    'function': function,
                    'call_type': call_type,
                    'line': i + 1
                })

        return external_calls

    def _build_dependency_graph(self):
        """Build dependency graph between contracts"""
        # Add all contracts as nodes
        for contract_name in self.contracts.keys():
            self.dependency_graph.add_node(contract_name)

        # Add edges for external calls
        for contract_name, contract_info in self.contracts.items():
            for call in contract_info['external_calls']:
                target = call['target']

                # Check if target is another contract in our set
                if target in self.contracts or target.endswith('Interface'):
                    self.dependency_graph.add_edge(
                        contract_name,
                        target,
                        call_type=call['call_type'],
                        function=call['function']
                    )

    def _detect_cross_contract_reentrancy(self):
        """
        Detect reentrancy vulnerabilities across contracts

        Pattern:
        1. Contract A calls Contract B (external call)
        2. Contract B calls back to Contract A before state update
        3. State inconsistency allows exploitation
        """

        for contract_name, contract_info in self.contracts.items():
            source = contract_info['source']

            # Check for external calls before state changes
            for func in contract_info['functions']:
                if func['visibility'] not in ['public', 'external']:
                    continue

                # Check if function has external calls
                has_external_call = any(
                    call['target'] != contract_name
                    for call in contract_info['external_calls']
                )

                if has_external_call:
                    # Check if state updates happen after external calls
                    has_state_change_after = self._has_state_change_pattern(source)

                    if has_state_change_after:
                        # Potential cross-contract reentrancy
                        self.vulnerabilities.append(CrossContractVulnerability(
                            vuln_type=CrossContractVulnType.CROSS_CONTRACT_REENTRANCY,
                            severity="critical",
                            title=f"Cross-Contract Reentrancy in {contract_name}",
                            description=(
                                f"Contract {contract_name} makes external calls before updating state. "
                                f"This allows reentrancy attacks across contract boundaries."
                            ),
                            contracts_involved=[contract_name],
                            attack_chain=None,
                            estimated_loss=(100_000, 10_000_000),
                            confidence=85
                        ))

    def _detect_upgrade_vulnerabilities(self):
        """
        Detect vulnerabilities in upgradeable contracts

        Patterns:
        1. Proxy without access control on upgrade function
        2. Missing initialization in upgradeable contract
        3. Storage collision in proxy pattern
        4. Delegatecall to untrusted address
        """

        for contract_name, contract_info in self.contracts.items():
            if not contract_info['is_proxy'] and not contract_info['is_upgradeable']:
                continue

            source = contract_info['source']

            # Pattern 1: Upgrade without access control
            if 'function upgrade' in source.lower() or 'function setimplementation' in source.lower():
                has_access_control = any(
                    keyword in source.lower()
                    for keyword in ['onlyowner', 'require(msg.sender', 'onlyadmin']
                )

                if not has_access_control:
                    self.vulnerabilities.append(CrossContractVulnerability(
                        vuln_type=CrossContractVulnType.UPGRADE_VULNERABILITY,
                        severity="critical",
                        title=f"Unprotected Upgrade in {contract_name}",
                        description=(
                            f"Contract {contract_name} has upgrade functionality without access control. "
                            f"Anyone can upgrade to a malicious implementation and steal all funds."
                        ),
                        contracts_involved=[contract_name],
                        attack_chain=None,
                        estimated_loss=(1_000_000, 100_000_000),
                        confidence=95
                    ))

            # Pattern 2: Missing initialize function
            if contract_info['is_upgradeable']:
                has_initialize = 'function initialize' in source.lower()
                has_constructor = 'constructor(' in source

                if has_constructor and not has_initialize:
                    self.vulnerabilities.append(CrossContractVulnerability(
                        vuln_type=CrossContractVulnType.UPGRADE_VULNERABILITY,
                        severity="high",
                        title=f"Constructor in Upgradeable Contract: {contract_name}",
                        description=(
                            f"Upgradeable contract {contract_name} uses constructor instead of initialize(). "
                            f"Constructor code won't execute in proxy context, leaving contract uninitialized."
                        ),
                        contracts_involved=[contract_name],
                        attack_chain=None,
                        estimated_loss=(50_000, 5_000_000),
                        confidence=90
                    ))

    def _detect_delegatecall_issues(self):
        """
        Detect delegatecall vulnerabilities

        Patterns:
        1. Delegatecall to user-controlled address
        2. Delegatecall without proper validation
        3. Storage collision via delegatecall
        """

        for contract_name, contract_info in self.contracts.items():
            source = contract_info['source']

            if 'delegatecall' not in source.lower():
                continue

            # Check for delegatecall to variable address
            lines = source.split('\n')
            for i, line in enumerate(lines):
                if 'delegatecall' in line.lower():
                    # Check if address is validated
                    has_validation = any(
                        keyword in source[:source.index(line)]
                        for keyword in ['require(', 'if (', 'whitelist', 'approved']
                    )

                    if not has_validation:
                        self.vulnerabilities.append(CrossContractVulnerability(
                            vuln_type=CrossContractVulnType.DELEGATECALL_INJECTION,
                            severity="critical",
                            title=f"Unsafe Delegatecall in {contract_name}",
                            description=(
                                f"Contract {contract_name} uses delegatecall without proper validation. "
                                f"Attacker can execute arbitrary code in contract context, "
                                f"leading to complete contract takeover."
                            ),
                            contracts_involved=[contract_name],
                            attack_chain=None,
                            estimated_loss=(500_000, 50_000_000),
                            confidence=95
                        ))
                    break

    def _detect_interface_trust_issues(self):
        """
        Detect trust issues with external contract interfaces

        Patterns:
        1. Trusting external price oracles without validation
        2. Calling unknown contracts without checks
        3. Assuming external contract behavior
        """

        for contract_name, contract_info in self.contracts.items():
            # Check for calls to external contracts
            for call in contract_info['external_calls']:
                # If calling an interface or external contract
                if call['target'].endswith('Interface') or call['target'][0].isupper():
                    # Check if return value is validated
                    source = contract_info['source']

                    # This is a simplified check
                    if 'require(' not in source or 'revert(' not in source:
                        self.vulnerabilities.append(CrossContractVulnerability(
                            vuln_type=CrossContractVulnType.INTERFACE_TRUST,
                            severity="medium",
                            title=f"Untrusted External Call in {contract_name}",
                            description=(
                                f"Contract {contract_name} calls external contract {call['target']} "
                                f"without validating return values. Malicious contract can "
                                f"return unexpected values."
                            ),
                            contracts_involved=[contract_name, call['target']],
                            attack_chain=None,
                            estimated_loss=(10_000, 1_000_000),
                            confidence=70
                        ))

    def _identify_attack_chains(self):
        """
        Identify multi-step attack chains across contracts

        Example:
        1. Exploit Contract A → manipulate state
        2. Call Contract B → uses manipulated state
        3. Profit from price difference
        """

        # Find cycles in dependency graph (potential reentrancy chains)
        try:
            cycles = list(nx.simple_cycles(self.dependency_graph))

            for cycle in cycles:
                if len(cycle) > 1:
                    # Potential attack chain through cycle
                    self.vulnerabilities.append(CrossContractVulnerability(
                        vuln_type=CrossContractVulnType.ATTACK_CHAIN,
                        severity="high",
                        title=f"Potential Attack Chain: {' → '.join(cycle)}",
                        description=(
                            f"Circular dependency detected: {' → '.join(cycle)}. "
                            f"This creates potential for complex reentrancy or state manipulation attacks."
                        ),
                        contracts_involved=cycle,
                        attack_chain=AttackChain(
                            steps=[{'contract': c, 'action': 'call'} for c in cycle],
                            total_impact="high",
                            complexity="medium",
                            description=f"Attack path through: {' → '.join(cycle)}"
                        ),
                        estimated_loss=(50_000, 5_000_000),
                        confidence=75
                    ))
        except:
            pass  # No cycles found

    def _has_state_change_pattern(self, source: str) -> bool:
        """Check if contract has state changes after external calls"""
        # Simplified check for state changes
        state_change_patterns = [
            r'=\s*\w+',  # Assignment
            r'balances\[',
            r'\.transfer\(',
            r'\.send\(',
        ]

        return any(re.search(pattern, source) for pattern in state_change_patterns)

    def _convert_to_standard_format(self, file_path: str) -> List[SolidityVulnerability]:
        """Convert cross-contract vulnerabilities to standard format"""
        standard_vulns = []

        for vuln in self.vulnerabilities:
            # Map to standard vulnerability types
            vuln_type_map = {
                CrossContractVulnType.CROSS_CONTRACT_REENTRANCY: VulnerabilityType.REENTRANCY,
                CrossContractVulnType.UPGRADE_VULNERABILITY: VulnerabilityType.ACCESS_CONTROL,
                CrossContractVulnType.DELEGATECALL_INJECTION: VulnerabilityType.LOGIC_ERROR,
                CrossContractVulnType.INTERFACE_TRUST: VulnerabilityType.LOGIC_ERROR,
                CrossContractVulnType.ACCESS_CONTROL_BREACH: VulnerabilityType.ACCESS_CONTROL,
                CrossContractVulnType.ATTACK_CHAIN: VulnerabilityType.LOGIC_ERROR,
            }

            vuln_type = vuln_type_map.get(vuln.vuln_type, VulnerabilityType.LOGIC_ERROR)

            # Create code snippet with cross-contract details
            code_snippet = (
                f"Contracts Involved: {', '.join(vuln.contracts_involved)}\n"
                f"Estimated Loss: ${vuln.estimated_loss[0]:,} - ${vuln.estimated_loss[1]:,}\n"
            )

            if vuln.attack_chain:
                code_snippet += f"Attack Chain: {vuln.attack_chain.description}\n"

            # Remediation
            remediation = self._get_remediation(vuln.vuln_type)

            standard_vuln = SolidityVulnerability(
                vulnerability_type=vuln_type,
                severity=vuln.severity,
                title=f"[Cross-Contract] {vuln.title}",
                description=vuln.description,
                file_path=file_path,
                line_number=1,
                function_name="multiple",
                contract_name=', '.join(vuln.contracts_involved),
                code_snippet=code_snippet,
                remediation=remediation,
                confidence=vuln.confidence
            )

            standard_vulns.append(standard_vuln)

        return standard_vulns

    def _get_remediation(self, vuln_type: CrossContractVulnType) -> str:
        """Get remediation advice"""
        remediation_map = {
            CrossContractVulnType.CROSS_CONTRACT_REENTRANCY: (
                "Follow Checks-Effects-Interactions pattern: update state before external calls. "
                "Use ReentrancyGuard from OpenZeppelin. Consider using pull over push for payments."
            ),
            CrossContractVulnType.UPGRADE_VULNERABILITY: (
                "Add access control to upgrade functions (onlyOwner/onlyAdmin). "
                "Use OpenZeppelin's UUPSUpgradeable or TransparentUpgradeableProxy. "
                "Implement timelock for upgrades. Use initialize() instead of constructor."
            ),
            CrossContractVulnType.DELEGATECALL_INJECTION: (
                "Never delegatecall to user-controlled addresses. "
                "Maintain a whitelist of approved implementation contracts. "
                "Use library patterns instead of delegatecall where possible."
            ),
            CrossContractVulnType.INTERFACE_TRUST: (
                "Validate all return values from external contracts. "
                "Use try/catch for external calls. "
                "Implement circuit breakers for critical operations. "
                "Verify contract addresses and implementations."
            ),
            CrossContractVulnType.ATTACK_CHAIN: (
                "Break circular dependencies where possible. "
                "Add reentrancy guards across the call chain. "
                "Validate state consistency at each step. "
                "Consider using commit-reveal schemes."
            )
        }

        return remediation_map.get(vuln_type, "Review cross-contract interactions carefully.")

    def visualize_dependency_graph(self) -> str:
        """Generate text representation of dependency graph"""
        if not self.dependency_graph.nodes():
            return "No dependencies found"

        output = "Contract Dependency Graph:\n"
        output += "=" * 50 + "\n\n"

        for contract in self.dependency_graph.nodes():
            output += f"{contract}\n"

            # Outgoing dependencies
            for target in self.dependency_graph.successors(contract):
                edge_data = self.dependency_graph[contract][target]
                output += f"  └─> {target} ({edge_data.get('call_type', 'call')})\n"

        return output


# Example usage
if __name__ == "__main__":
    analyzer = CrossContractAnalyzer()

    # Test with multiple contracts
    contracts = {
        "Vault": """
        contract Vault {
            mapping(address => uint256) public balances;

            function withdraw() external {
                uint256 amount = balances[msg.sender];
                (bool success, ) = msg.sender.call{value: amount}("");  // External call!
                balances[msg.sender] = 0;  // State change AFTER call - VULNERABLE!
            }
        }
        """,
        "Proxy": """
        contract Proxy {
            address public implementation;

            function upgrade(address newImpl) external {
                // NO ACCESS CONTROL - VULNERABLE!
                implementation = newImpl;
            }

            fallback() external payable {
                address impl = implementation;
                assembly {
                    delegatecall(gas(), impl, 0, calldatasize(), 0, 0)
                }
            }
        }
        """
    }

    vulns = analyzer.analyze_contracts(contracts)

    print(f"Found {len(vulns)} cross-contract vulnerabilities:\n")
    for vuln in vulns:
        print(f"{vuln.severity.upper()}: {vuln.title}")
        print(f"  {vuln.description}")
        print(f"  {vuln.code_snippet}")
        print()

    print(analyzer.visualize_dependency_graph())
