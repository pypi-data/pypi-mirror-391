"""
Solidity Smart Contract Static Analyzer

Inspired by Slither but enhanced for startup Web3 security needs.
Focuses on OWASP Smart Contract Top 10 detection with economic context.
"""

import re
import ast
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class VulnerabilityType(Enum):
    REENTRANCY = "reentrancy"
    ACCESS_CONTROL = "access_control"
    INTEGER_OVERFLOW_UNDERFLOW = "integer_overflow"
    UNCHECKED_LOW_LEVEL_CALL = "unchecked_call"
    LOGIC_ERROR = "logic_error"
    TIMESTAMP_DEPENDENCE = "timestamp_dependence"
    UNINITIALIZED_STORAGE = "uninitialized_storage"
    ORACLE_MANIPULATION = "oracle_manipulation"
    GAS_LIMIT_ISSUE = "gas_limit"
    DENIAL_OF_SERVICE = "denial_of_service"

@dataclass
class SolidityVulnerability:
    """Represents a smart contract vulnerability"""
    vulnerability_type: VulnerabilityType
    severity: str  # "critical", "high", "medium", "low"
    title: str
    description: str
    file_path: str
    line_number: Optional[int]
    function_name: Optional[str]
    contract_name: str
    code_snippet: Optional[str] = None
    remediation: Optional[str] = None
    confidence: int = 100  # 0-100

class SolidityStaticAnalyzer:
    """
    Enhanced Solidity analyzer focused on Web3 startup security needs
    """
    
    def __init__(self):
        self.vulnerability_patterns = self._initialize_patterns()
        self.contract_structure = None
        self.functions = []
        self.state_variables = []
    
    def analyze_contract(self, contract_code: str, file_path: str) -> List[SolidityVulnerability]:
        """
        Comprehensive smart contract vulnerability analysis
        
        Args:
            contract_code: Solidity source code
            file_path: Path to the contract file
            
        Returns:
            List of detected vulnerabilities
        """
        vulnerabilities = []
        
        try:
            # Parse contract structure
            self._parse_contract_structure(contract_code)
            
            # Run comprehensive vulnerability detection
            reentrancy_vulns = self._detect_reentrancy_vulnerabilities(contract_code, file_path)
            access_control_vulns = self._detect_access_control_vulnerabilities(contract_code, file_path)
            overflow_vulns = self._detect_integer_vulnerabilities(contract_code, file_path)
            call_vulns = self._detect_unchecked_calls(contract_code, file_path)
            logic_vulns = self._detect_logic_errors(contract_code, file_path)
            oracle_vulns = self._detect_oracle_manipulation(contract_code, file_path)
            input_vulns = self._detect_input_validation_issues(contract_code, file_path)

            vulnerabilities.extend(reentrancy_vulns)
            vulnerabilities.extend(access_control_vulns)
            vulnerabilities.extend(overflow_vulns)
            vulnerabilities.extend(call_vulns)
            vulnerabilities.extend(logic_vulns)
            vulnerabilities.extend(oracle_vulns)
            vulnerabilities.extend(input_vulns)
            
        except Exception as e:
            # Add parsing error as info-level vulnerability
            vulnerabilities.append(SolidityVulnerability(
                vulnerability_type=VulnerabilityType.LOGIC_ERROR,
                severity="low",
                title="Analysis Error",
                description=f"Could not fully analyze contract: {str(e)}",
                file_path=file_path,
                line_number=None,
                    function_name=None,
                contract_name="unknown",
                confidence=20
            ))
        
        return vulnerabilities
    
    def _parse_contract_structure(self, contract_code: str):
        """Parse contract structure to identify functions and state variables"""
        lines = contract_code.split('\n')
        
        # Find contracts
        self.contract_structure = {
            'contracts': [],
            'functions': [],
            'state_variables': []
        }
        
        current_contract = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('//') or line.startswith('/*'):
                continue
            
            # Find contract definitions
            if line.startswith('contract ') or line.startswith('abstract contract '):
                contract_match = re.search(r'(abstract )?contract\s+(\w+)', line)
                if contract_match:
                    current_contract = contract_match.group(2)
                    self.contract_structure['contracts'].append({
                        'name': current_contract,
                        'line': i + 1
                    })
                continue
            
            # Find function definitions
            if current_contract and ('function ' in line or 'modifier ' in line):
                func_match = re.search(r'(function|modifier)\s+(\w+)', line)
                if func_match:
                    func_type = func_match.group(1)
                    func_name = func_match.group(2)
                    function_info = {
                        'name': func_name,
                        'type': func_type,
                        'contract': current_contract,
                        'line': i + 1,
                        'visibility': 'internal'  # Default
                    }
                    
                    # Check visibility modifiers
                    if 'public' in line:
                        function_info['visibility'] = 'public'
                    elif 'external' in line:
                        function_info['visibility'] = 'external'
                    elif 'internal' in line:
                        function_info['visibility'] = 'internal'
                    elif 'private' in line:
                        function_info['visibility'] = 'private'
                    
                    # Check for payable
                    if 'payable' in line:
                        function_info['payable'] = True
                    
                    self.contract_structure['functions'].append(function_info)
                continue
            
            # Find state variables
            if current_contract and ('uint256 ' in line or 'address ' in line or 'mapping(' in line):
                # Extract variable name
                var_match = re.search(r'(uint256|address|mapping)\s+(?:\(.*?\))?\s*(\w+)', line)
                if var_match:
                    var_type = var_match.group(1)
                    var_name = var_match.group(2)
                    self.contract_structure['state_variables'].append({
                        'name': var_name,
                        'type': var_type,
                        'contract': current_contract,
                        'line': i + 1
                    })
    
    def _detect_reentrancy_vulnerabilities(self, contract_code: str, file_path: str) -> List[SolidityVulnerability]:
        """Detect reentrancy attack vulnerabilities"""
        vulnerabilities = []
        lines = contract_code.split('\n')
        
        for i, line in enumerate(lines):
            line_content = line.strip()
            if not line_content or line_content.startswith('//'):
                continue
            
            # Pattern 1: Call to external address before state change
            if ('.call(' in line_content or '.transfer(' in line_content or '.send(' in line_content):
                # Check if this happens before state update in same function
                vuln = SolidityVulnerability(
                    vulnerability_type=VulnerabilityType.REENTRANCY,
                    severity="high",
                    title="Potential Reentrancy",
                    description=f"External call detected: {line_content[:80]}... Reentrancy vulnerability if state changes happen after this call.",
                    file_path=file_path,
                    line_number=i + 1,
                    function_name=None,
                    contract_name=self._get_current_function_contract(i, lines),
                    code_snippet=line_content.strip(),
                    remediation="Implement checks-effects-interactions pattern or use ReentrancyGuard modifier",
                    confidence=75
                )
                vulnerabilities.append(vuln)
            
            # Pattern 2: Low-level calls without checks
            if '.call.value(' in line_content and 'return' not in line_content:
                vuln = SolidityVulnerability(
                    vulnerability_type=VulnerabilityType.UNCHECKED_LOW_LEVEL_CALL,
                    severity="medium",
                    title="Unchecked Low-Level Call", 
                    description=f"Unverified low-level call: {line_content[:80]}...",
                    file_path=file_path,
                    line_number=i + 1,
                    function_name=None,
                    contract_name=self._get_current_function_contract(i, lines),
                    code_snippet=line_content.strip(),
                    remediation="Always check return values of low-level calls",
                    confidence=85
                )
                vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def _detect_access_control_vulnerabilities(self, contract_code: str, file_path: str) -> List[SolidityVulnerability]:
        """Detect access control vulnerabilities"""
        vulnerabilities = []
        lines = contract_code.split('\n')
        
        critical_functions = ['withdraw', 'transferOwnership', 'mint', 'burn', 'pause', 'unpause']
        
        for i, line in enumerate(lines):
            line_content = line.strip()
            if not line_content or line_content.startswith('//'):
                continue
            
            # Check for critical functions without access controls
            for func_name in critical_functions:
                if f'function {func_name}' in line_content and 'public' in line_content:
                    # Look for modifiers in the same line
                    if not any(mod in line_content for mod in ['onlyOwner', 'require', 'if', 'modifier']):
                        vuln = SolidityVulnerability(
                            vulnerability_type=VulnerabilityType.ACCESS_CONTROL,
                            severity="critical",
                            title="Missing Access Control",
                            description=f"Critical function {func_name} lacks proper access control modifier",
                            file_path=file_path,
                            line_number=i + 1,
                            function_name=func_name,
                            contract_name=self._get_current_function_contract(i, lines),
                            code_snippet=line_content.strip(),
                            remediation=f"Add access control modifier (e.g., onlyOwner) to {func_name} function",
                            confidence=90
                        )
                        vulnerabilities.append(vuln)
        
        # Pattern: owner() function that returns hardcoded address
        for i, line in enumerate(lines):
            line_content = line.strip()
            if 'return' in line_content and '0x' in line_content:
                if 'owner()' in ''.join(lines[max(0, i-2):i+2]):
                    vuln = SolidityVulnerability(
                        vulnerability_type=VulnerabilityType.ACCESS_CONTROL,
                        severity="medium",
                        title="Hardcoded Owner Address",
                        description="Owner function returns hardcoded address instead of dynamic storage",
                        file_path=file_path,
                        line_number=i + 1,
                    function_name=None,
                        contract_name=self._get_current_function_contract(i, lines),
                        code_snippet=line_content.strip(),
                        remediation="Use address storage variable for owner instead of hardcoded value",
                        confidence=70
                    )
                    vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def _detect_integer_vulnerabilities(self, contract_code: str, file_path: str) -> List[SolidityVulnerability]:
        """Detect integer overflow/underflow vulnerabilities"""
        vulnerabilities = []
        lines = contract_code.split('\n')
        
        arithmetic_operations = ['+', '-', '*', '/']
        
        for i, line in enumerate(lines):
            line_content = line.strip()
            if not line_content or line_content.startswith('//'):
                continue
            
            # Look for arithmetic operations without SafeMath
            for op in arithmetic_operations:
                if op in line_content and 'SafeMath' not in ''.join(lines[max(0, i-5):i+5]):
                    # Check if this is a critical operation (balance, amount, etc.)
                    context_words = ['balance', 'amount', 'total', 'supply', 'price', 'value']
                    if any(word in line_content.lower() for word in context_words):
                        vuln = SolidityVulnerability(
                            vulnerability_type=VulnerabilityType.INTEGER_OVERFLOW_UNDERFLOW,
                            severity="medium",
                            title="Potential Integer Overflow/Underflow",
                            description=f"Arithmetic operation without overflow protection: {line_content[:80]}...",
                            file_path=file_path,
                            line_number=i + 1,
                    function_name=None,
                            contract_name=self._get_current_function_contract(i, lines),
                            code_snippet=line_content.strip(),
                            remediation="Use SafeMath library or Solidity 0.8+ which has built-in overflow protection",
                            confidence=65
                        )
                        vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def _detect_unchecked_calls(self, contract_code: str, file_path: str) -> List[SolidityVulnerability]:
        """Detect unchecked external calls"""
        vulnerabilities = []
        lines = contract_code.split('\n')
        
        for i, line in enumerate(lines):
            line_content = line.strip()
            if not line_content or line_content.startswith('//'):
                continue
            
            # External call patterns
            external_calls = ['.call(', '.delegatecall(', '.transfer(', '.send(']
            
            for pattern in external_calls:
                if pattern in line_content:
                    # Check if return value is being used or verified
                    next_lines = lines[i+1:i+3]  # Look at next 2-3 lines
                    has_check = any('require(' in next_line or 'if (' in next_line 
                                   for next_line in next_lines if next_line.strip())
                    
                    if not has_check:
                        vuln = SolidityVulnerability(
                            vulnerability_type=VulnerabilityType.UNCHECKED_LOW_LEVEL_CALL,
                            severity="high",
                            title="Unchecked External Call",
                            description=f"External call {pattern} without return value verification",
                            file_path=file_path,
                            line_number=i + 1,
                    function_name=None,
                            contract_name=self._get_current_function_contract(i, lines),
                            code_snippet=line_content.strip(),
                            remediation="Always verify return values of external calls",
                            confidence=80
                        )
                        vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def _detect_logic_errors(self, contract_code: str, file_path: str) -> List[SolidityVulnerability]:
        """Detect logic errors and bad practices"""
        vulnerabilities = []
        lines = contract_code.split('\n')
        
        # Pattern 1: Using block.timestamp for critical operations
        for i, line in enumerate(lines):
            line_content = line.strip()
            if 'block.timestamp' in line_content:
                # Check if timestamp is used for something critical
                critical_contexts = ['deadline', 'expiration', 'unlock', 'vest']
                if any(context in ''.join(lines[max(0, i-3):i+3]).lower() for context in critical_contexts):
                    vuln = SolidityVulnerability(
                        vulnerability_type=VulnerabilityType.TIMESTAMP_DEPENDENCE,
                        severity="medium",
                        title="Block Timestamp Manipulation Risk",
                        description="Using block.timestamp for critical logic that miners can manipulate",
                        file_path=file_path,
                        line_number=i + 1,
                    function_name=None,
                        contract_name=self._get_current_function_contract(i, lines),
                        code_snippet=line_content.strip(),
                        remediation="Use block.number or external oracle for time-dependent logic",
                        confidence=75
                    )
                    vulnerabilities.append(vuln)
        
        # Pattern 2: Uninitialized storage pointers
        for i, line in enumerate(lines):
            line_content = line.strip()
            if 'Storage(' in line_content and 'new' in line_content:
                vuln = SolidityVulnerability(
                    vulnerability_type=VulnerabilityType.UNINITIALIZED_STORAGE,
                    severity="medium",
                    title="Potential Uninitialized Storage Pointer",
                    description="Creating struct or array storage without proper initialization",
                    file_path=file_path,
                    line_number=i + 1,
                    function_name=None,
                    contract_name=self._get_current_function_contract(i, lines),
                    code_snippet=line_content.strip(),
                    remediation="Initialize storage variables properly before use",
                    confidence=60
                )
                vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def _detect_oracle_manipulation(self, contract_code: str, file_path: str) -> List[SolidityVulnerability]:
        """
        Detect price oracle manipulation vulnerabilities

        WEEK 2 DAY 1: Enhanced Oracle Manipulation Detection
        Based on OWASP SC02:2025 and 2024-2025 exploit research

        Detection Patterns:
        1. Chainlink oracle staleness (no updatedAt check)
        2. Single oracle source (no aggregation)
        3. Missing price bounds validation
        4. UniswapV2 spot price usage (flash loan vulnerable)
        5. Missing TWAP implementation
        6. No oracle failure handling (try/catch)
        7. Direct pool reserve usage
        """
        vulnerabilities = []
        lines = contract_code.split('\n')

        # Track oracle usage per function for contextual analysis
        function_contexts = self._extract_function_contexts(lines)

        # Pattern 1: Chainlink oracle without staleness checks
        chainlink_vulns = self._detect_chainlink_staleness(lines, file_path, function_contexts)
        vulnerabilities.extend(chainlink_vulns)

        # Pattern 2: Single oracle source without aggregation
        single_oracle_vulns = self._detect_single_oracle_usage(lines, file_path, function_contexts)
        vulnerabilities.extend(single_oracle_vulns)

        # Pattern 3: Missing price bounds validation
        bounds_vulns = self._detect_missing_price_bounds(lines, file_path, function_contexts)
        vulnerabilities.extend(bounds_vulns)

        # Pattern 4: UniswapV2 spot price vulnerability
        uniswap_vulns = self._detect_uniswap_spot_price(lines, file_path, function_contexts)
        vulnerabilities.extend(uniswap_vulns)

        # Pattern 5: Pool reserve manipulation
        reserve_vulns = self._detect_pool_reserve_manipulation(lines, file_path, function_contexts)
        vulnerabilities.extend(reserve_vulns)

        # Pattern 6: Missing oracle failure handling
        failure_vulns = self._detect_missing_oracle_failure_handling(lines, file_path, function_contexts)
        vulnerabilities.extend(failure_vulns)

        return vulnerabilities

    def _extract_function_contexts(self, lines: List[str]) -> Dict[int, Dict[str, Any]]:
        """Extract function contexts for contextual analysis"""
        contexts = {}
        current_function = None
        current_contract = None
        brace_count = 0

        for i, line in enumerate(lines):
            line_stripped = line.strip()

            # Track contract
            if line_stripped.startswith('contract ') or line_stripped.startswith('abstract contract '):
                match = re.search(r'contract\s+(\w+)', line_stripped)
                if match:
                    current_contract = match.group(1)

            # Track function
            if line_stripped.startswith('function '):
                match = re.search(r'function\s+(\w+)', line_stripped)
                if match:
                    current_function = match.group(1)
                    brace_count = 0

            # Track braces for function scope
            brace_count += line_stripped.count('{') - line_stripped.count('}')

            # Store context
            contexts[i] = {
                'function': current_function,
                'contract': current_contract,
                'in_function': brace_count > 0 and current_function is not None
            }

            # Reset function when it ends
            if brace_count == 0 and current_function is not None:
                current_function = None

        return contexts

    def _detect_chainlink_staleness(
        self,
        lines: List[str],
        file_path: str,
        contexts: Dict[int, Dict[str, Any]]
    ) -> List[SolidityVulnerability]:
        """
        Detect Chainlink oracle usage without staleness checks

        CVE Pattern: Missing updatedAt validation
        Real Exploits: Polter Finance, BonqDAO Protocol
        """
        vulnerabilities = []

        # Pattern: latestRoundData() without updatedAt check
        chainlink_patterns = [
            r'latestRoundData\s*\(',
            r'AggregatorV3Interface',
            r'getRoundData\s*\(',
        ]

        for i, line in enumerate(lines):
            line_content = line.strip()

            # Check if line contains Chainlink oracle call
            if any(re.search(pattern, line_content) for pattern in chainlink_patterns):
                context = contexts.get(i, {})
                function_name = context.get('function', 'unknown')
                contract_name = context.get('contract', 'unknown')

                # Check next 15 lines for staleness validation
                check_window = lines[i:i+15]
                has_staleness_check = any(
                    'updatedAt' in check_line and
                    ('block.timestamp' in check_line or 'now' in check_line)
                    for check_line in check_window
                )

                has_price_validation = any(
                    'price' in check_line and
                    ('require' in check_line or 'revert' in check_line) and
                    ('>' in check_line or '<' in check_line)
                    for check_line in check_window
                )

                if not has_staleness_check:
                    vulnerabilities.append(SolidityVulnerability(
                        vulnerability_type=VulnerabilityType.ORACLE_MANIPULATION,
                        severity="high",
                        title="Chainlink Oracle Staleness Not Checked",
                        description=(
                            f"Function '{function_name}' uses Chainlink oracle without validating "
                            f"data freshness. Stale price data can be exploited for profit. "
                            f"OWASP SC02:2025 - Price Oracle Manipulation. "
                            f"Similar to Polter Finance exploit (2024)."
                        ),
                        file_path=file_path,
                        line_number=i + 1,
                        function_name=function_name,
                        contract_name=contract_name,
                        code_snippet=line_content,
                        remediation=(
                            "Add staleness validation:\n"
                            "require(block.timestamp - updatedAt < 3600, 'Stale price');\n"
                            "Also validate: updatedAt > 0, answeredInRound >= roundId, price > 0"
                        ),
                        confidence=90
                    ))

                if not has_price_validation:
                    vulnerabilities.append(SolidityVulnerability(
                        vulnerability_type=VulnerabilityType.ORACLE_MANIPULATION,
                        severity="medium",
                        title="Missing Chainlink Price Validation",
                        description=(
                            f"Function '{function_name}' doesn't validate price from Chainlink. "
                            f"Price should be checked for: price > 0, within bounds."
                        ),
                        file_path=file_path,
                        line_number=i + 1,
                        function_name=function_name,
                        contract_name=contract_name,
                        code_snippet=line_content,
                        remediation=(
                            "Add price validation:\n"
                            "require(price > 0, 'Invalid price');\n"
                            "require(price >= minPrice && price <= maxPrice, 'Price out of bounds');"
                        ),
                        confidence=85
                    ))

        return vulnerabilities

    def _detect_single_oracle_usage(
        self,
        lines: List[str],
        file_path: str,
        contexts: Dict[int, Dict[str, Any]]
    ) -> List[SolidityVulnerability]:
        """
        Detect single oracle source without aggregation

        OWASP Recommendation: Use multiple independent oracle sources
        """
        vulnerabilities = []

        # Track oracle sources per function
        function_oracle_counts = {}

        oracle_source_patterns = [
            r'latestRoundData\s*\(',  # Chainlink
            r'getAmountsOut\s*\(',     # Uniswap
            r'consult\s*\(',           # TWAP
            r'\.price\s*\(',           # Generic price getter
        ]

        for i, line in enumerate(lines):
            line_content = line.strip()
            context = contexts.get(i, {})
            function_name = context.get('function')

            if not function_name or not context.get('in_function'):
                continue

            # Count oracle sources
            for pattern in oracle_source_patterns:
                if re.search(pattern, line_content):
                    if function_name not in function_oracle_counts:
                        function_oracle_counts[function_name] = {
                            'count': 0,
                            'line': i + 1,
                            'contract': context.get('contract', 'unknown')
                        }
                    function_oracle_counts[function_name]['count'] += 1

        # Report functions with single oracle source
        for func_name, data in function_oracle_counts.items():
            if data['count'] == 1:
                vulnerabilities.append(SolidityVulnerability(
                    vulnerability_type=VulnerabilityType.ORACLE_MANIPULATION,
                    severity="medium",
                    title="Single Oracle Source - No Aggregation",
                    description=(
                        f"Function '{func_name}' relies on single oracle source. "
                        f"OWASP SC02:2025 recommends multiple independent oracles "
                        f"to prevent single-point manipulation. "
                        f"$70M+ lost to oracle manipulation in 2024."
                    ),
                    file_path=file_path,
                    line_number=data['line'],
                    function_name=func_name,
                    contract_name=data['contract'],
                    code_snippet=None,
                    remediation=(
                        "Implement multi-oracle strategy:\n"
                        "1. Use Chainlink + UniswapV3 TWAP\n"
                        "2. Compare prices and revert if deviation > 10%\n"
                        "3. Take median of 3+ oracle sources"
                    ),
                    confidence=80
                ))

        return vulnerabilities

    def _detect_missing_price_bounds(
        self,
        lines: List[str],
        file_path: str,
        contexts: Dict[int, Dict[str, Any]]
    ) -> List[SolidityVulnerability]:
        """
        Detect missing MIN_PRICE and MAX_PRICE validation

        OWASP Mitigation: Implement price boundaries
        """
        vulnerabilities = []

        price_usage_pattern = r'(price|amount|value)\s*[=:]'

        for i, line in enumerate(lines):
            line_content = line.strip()
            context = contexts.get(i, {})

            if not context.get('in_function'):
                continue

            # Check if line assigns/uses price
            if re.search(price_usage_pattern, line_content):
                # Look for oracle calls in previous 5 lines
                prev_lines = lines[max(0, i-5):i+1]
                has_oracle_call = any(
                    'latestRoundData' in prev or
                    'getAmountOut' in prev or
                    'consult' in prev
                    for prev in prev_lines
                )

                if not has_oracle_call:
                    continue

                # Check for bounds validation in next 10 lines
                next_lines = lines[i+1:i+10]
                has_min_check = any('MIN' in next_line.upper() or 'minPrice' in next_line for next_line in next_lines)
                has_max_check = any('MAX' in next_line.upper() or 'maxPrice' in next_line for next_line in next_lines)

                if not (has_min_check and has_max_check):
                    vulnerabilities.append(SolidityVulnerability(
                        vulnerability_type=VulnerabilityType.ORACLE_MANIPULATION,
                        severity="medium",
                        title="Missing Price Bounds Validation",
                        description=(
                            f"Price usage at line {i+1} lacks MIN/MAX bounds validation. "
                            f"OWASP SC02:2025 recommends price thresholds to detect anomalies. "
                            f"Without bounds, extreme price manipulation goes undetected."
                        ),
                        file_path=file_path,
                        line_number=i + 1,
                        function_name=context.get('function', 'unknown'),
                        contract_name=context.get('contract', 'unknown'),
                        code_snippet=line_content,
                        remediation=(
                            "Add price bounds:\n"
                            "uint256 constant MIN_PRICE = 1e6;  // Adjust for token\n"
                            "uint256 constant MAX_PRICE = 1e12;\n"
                            "require(price >= MIN_PRICE && price <= MAX_PRICE, 'Price anomaly');"
                        ),
                        confidence=75
                    ))

        return vulnerabilities

    def _detect_uniswap_spot_price(
        self,
        lines: List[str],
        file_path: str,
        contexts: Dict[int, Dict[str, Any]]
    ) -> List[SolidityVulnerability]:
        """
        Detect UniswapV2 spot price usage (flash loan vulnerable)

        Critical: Spot prices can be manipulated within single transaction
        Real Exploits: Moby (Jan 2025), The Vow (Aug 2024)
        """
        vulnerabilities = []

        # Patterns indicating spot price usage
        spot_price_patterns = [
            r'getAmountsOut\s*\(',
            r'getAmountOut\s*\(',
            r'getReserves\s*\(',
            r'\.reserves\(',
            r'pair\.getReserves',
        ]

        twap_patterns = [
            r'consult\s*\(',
            r'TWAP',
            r'timeWeighted',
            r'observe\s*\(',  # UniswapV3
        ]

        for i, line in enumerate(lines):
            line_content = line.strip()
            context = contexts.get(i, {})

            # Check if using spot price
            is_spot_price = any(re.search(pattern, line_content) for pattern in spot_price_patterns)

            if not is_spot_price:
                continue

            # Check if TWAP is also used (good)
            check_window = lines[max(0, i-10):i+10]
            has_twap = any(
                any(re.search(twap_pattern, check_line) for twap_pattern in twap_patterns)
                for check_line in check_window
            )

            if not has_twap:
                vulnerabilities.append(SolidityVulnerability(
                    vulnerability_type=VulnerabilityType.ORACLE_MANIPULATION,
                    severity="critical",
                    title="UniswapV2 Spot Price Flash Loan Vulnerability",
                    description=(
                        f"Line {i+1} uses Uniswap spot price without TWAP protection. "
                        f"CRITICAL: Spot prices can be manipulated within single transaction. "
                        f"Recent Exploits: Moby (Jan 2025), The Vow (Aug 2024). "
                        f"Attackers use flash loans to manipulate pool reserves. "
                        f"OWASP SC02:2025 - Most common DeFi exploit pattern (34.3%)."
                    ),
                    file_path=file_path,
                    line_number=i + 1,
                    function_name=context.get('function', 'unknown'),
                    contract_name=context.get('contract', 'unknown'),
                    code_snippet=line_content,
                    remediation=(
                        "CRITICAL FIX REQUIRED:\n"
                        "1. Use UniswapV3 TWAP with observe() for time-weighted prices\n"
                        "2. OR use Chainlink as primary oracle with Uniswap as backup\n"
                        "3. Never rely on spot prices for critical logic\n"
                        "4. Implement price deviation checks between oracles"
                    ),
                    confidence=95
                ))

        return vulnerabilities

    def _detect_pool_reserve_manipulation(
        self,
        lines: List[str],
        file_path: str,
        contexts: Dict[int, Dict[str, Any]]
    ) -> List[SolidityVulnerability]:
        """
        Detect direct pool reserve usage for pricing

        Using pool reserves directly is extremely vulnerable to manipulation
        """
        vulnerabilities = []

        reserve_patterns = [
            r'reserve0',
            r'reserve1',
            r'\.reserves\s*\(',
            r'balanceOf\(address\(this\)\)',
            r'token\.balanceOf\(pool\)',
        ]

        for i, line in enumerate(lines):
            line_content = line.strip()
            context = contexts.get(i, {})

            if not context.get('in_function'):
                continue

            # Check if using reserves for calculation
            uses_reserves = any(re.search(pattern, line_content) for pattern in reserve_patterns)

            if uses_reserves and ('*' in line_content or '/' in line_content or '=' in line_content):
                # Check if it's in a price calculation context
                next_lines = lines[i:i+5]
                looks_like_price_calc = any(
                    'price' in next_line.lower() or
                    'value' in next_line.lower() or
                    'amount' in next_line.lower()
                    for next_line in next_lines
                )

                if looks_like_price_calc:
                    vulnerabilities.append(SolidityVulnerability(
                        vulnerability_type=VulnerabilityType.ORACLE_MANIPULATION,
                        severity="critical",
                        title="Pool Reserve Direct Usage - Flash Loan Vulnerability",
                        description=(
                            f"Line {i+1} uses pool reserves directly for pricing. "
                            f"CRITICAL: Reserves can be manipulated within single transaction. "
                            f"This is the #1 DeFi exploit pattern. "
                            f"Using pool balances as price oracle is NEVER safe."
                        ),
                        file_path=file_path,
                        line_number=i + 1,
                        function_name=context.get('function', 'unknown'),
                        contract_name=context.get('contract', 'unknown'),
                        code_snippet=line_content,
                        remediation=(
                            "CRITICAL FIX:\n"
                            "1. Never use pool reserves directly for pricing\n"
                            "2. Use Chainlink Price Feeds for external prices\n"
                            "3. Use UniswapV3 TWAP with sufficient time window (30+ min)\n"
                            "4. Implement multi-oracle aggregation"
                        ),
                        confidence=95
                    ))

        return vulnerabilities

    def _detect_missing_oracle_failure_handling(
        self,
        lines: List[str],
        file_path: str,
        contexts: Dict[int, Dict[str, Any]]
    ) -> List[SolidityVulnerability]:
        """
        Detect oracle calls without try/catch blocks

        Oracle failures can DOS contracts if not handled properly
        """
        vulnerabilities = []

        oracle_call_patterns = [
            r'latestRoundData\s*\(',
            r'getRoundData\s*\(',
        ]

        for i, line in enumerate(lines):
            line_content = line.strip()
            context = contexts.get(i, {})

            # Check if making oracle call
            is_oracle_call = any(re.search(pattern, line_content) for pattern in oracle_call_patterns)

            if not is_oracle_call:
                continue

            # Check if wrapped in try/catch
            prev_lines = lines[max(0, i-3):i]
            has_try = any('try' in prev_line for prev_line in prev_lines)

            next_lines = lines[i+1:i+5]
            has_catch = any('catch' in next_line for next_line in next_lines)

            if not (has_try and has_catch):
                vulnerabilities.append(SolidityVulnerability(
                    vulnerability_type=VulnerabilityType.ORACLE_MANIPULATION,
                    severity="medium",
                    title="Missing Oracle Failure Handling",
                    description=(
                        f"Oracle call at line {i+1} lacks try/catch error handling. "
                        f"Oracle failures can cause contract DOS. "
                        f"Best practice: wrap oracle calls in try/catch with fallback logic."
                    ),
                    file_path=file_path,
                    line_number=i + 1,
                    function_name=context.get('function', 'unknown'),
                    contract_name=context.get('contract', 'unknown'),
                    code_snippet=line_content,
                    remediation=(
                        "Add error handling:\n"
                        "try oracle.latestRoundData() returns (...) {\n"
                        "    // use data\n"
                        "} catch {\n"
                        "    // fallback logic or revert gracefully\n"
                        "}"
                    ),
                    confidence=70
                ))

        return vulnerabilities

    def _detect_input_validation_issues(self, contract_code: str, file_path: str) -> List[SolidityVulnerability]:
        """
        Detect input validation vulnerabilities

        WEEK 2 DAY 2: Enhanced Input Validation Detection
        Based on OWASP Smart Contract Top 10 2025 - $14.6M in losses

        Detection Patterns:
        1. Missing address(0) checks for address parameters
        2. Missing zero/negative amount checks
        3. Missing array bounds validation
        4. Unchecked low-level call return values (enhanced)
        5. Missing parameter validation in critical functions
        6. Unsafe type conversions
        """
        vulnerabilities = []
        lines = contract_code.split('\n')

        # Extract function contexts for analysis
        function_contexts = self._extract_function_contexts(lines)

        # Pattern 1: Missing address(0) validation
        address_vulns = self._detect_missing_address_validation(lines, file_path, function_contexts)
        vulnerabilities.extend(address_vulns)

        # Pattern 2: Missing amount/value validation
        amount_vulns = self._detect_missing_amount_validation(lines, file_path, function_contexts)
        vulnerabilities.extend(amount_vulns)

        # Pattern 3: Missing array bounds validation
        array_vulns = self._detect_missing_array_bounds(lines, file_path, function_contexts)
        vulnerabilities.extend(array_vulns)

        # Pattern 4: Enhanced unchecked external calls
        external_call_vulns = self._detect_unchecked_external_calls(lines, file_path, function_contexts)
        vulnerabilities.extend(external_call_vulns)

        # Pattern 5: Unsafe type conversions
        conversion_vulns = self._detect_unsafe_type_conversions(lines, file_path, function_contexts)
        vulnerabilities.extend(conversion_vulns)

        return vulnerabilities

    def _detect_missing_address_validation(
        self,
        lines: List[str],
        file_path: str,
        contexts: Dict[int, Dict[str, Any]]
    ) -> List[SolidityVulnerability]:
        """
        Detect missing address(0) validation

        OWASP: Lack of Input Validation ($14.6M in losses)
        Critical Pattern: Sending funds to address(0) = permanent loss
        """
        vulnerabilities = []

        # Track function parameters
        for i, line in enumerate(lines):
            line_content = line.strip()
            context = contexts.get(i, {})

            # Check if it's a function definition with address parameter
            if line_content.startswith('function '):
                # Extract parameters
                if '(' in line_content and ')' in line_content:
                    params_match = re.search(r'\((.*?)\)', line_content)
                    if params_match:
                        params_str = params_match.group(1)

                        # Find address parameters
                        address_params = re.findall(r'address\s+(\w+)', params_str)

                        if address_params:
                            function_name = context.get('function', 'unknown')

                            # Check next 20 lines for address(0) validation
                            check_window = lines[i+1:i+20]

                            for addr_param in address_params:
                                has_validation = any(
                                    f'{addr_param}' in check_line and
                                    ('address(0)' in check_line or '0x0' in check_line) and
                                    ('require' in check_line or 'revert' in check_line or 'if' in check_line)
                                    for check_line in check_window
                                )

                                # Check if it's used in critical operations
                                is_critical = any(
                                    f'{addr_param}' in check_line and
                                    any(op in check_line for op in ['transfer', 'send', 'call', 'delegatecall', '='])
                                    for check_line in check_window
                                )

                                if not has_validation and is_critical:
                                    vulnerabilities.append(SolidityVulnerability(
                                        vulnerability_type=VulnerabilityType.LOGIC_ERROR,
                                        severity="high",
                                        title="Missing Address Zero Validation",
                                        description=(
                                            f"Parameter '{addr_param}' in function '{function_name}' lacks address(0) check. "
                                            f"OWASP 2025: Lack of Input Validation ($14.6M in losses). "
                                            f"Funds sent to address(0) are permanently lost - no private key exists. "
                                            f"This is a common attack vector in 2024-2025."
                                        ),
                                        file_path=file_path,
                                        line_number=i + 1,
                                        function_name=function_name,
                                        contract_name=context.get('contract', 'unknown'),
                                        code_snippet=line_content,
                                        remediation=(
                                            f"Add validation:\n"
                                            f"require({addr_param} != address(0), 'Zero address not allowed');"
                                        ),
                                        confidence=85
                                    ))

        return vulnerabilities

    def _detect_missing_amount_validation(
        self,
        lines: List[str],
        file_path: str,
        contexts: Dict[int, Dict[str, Any]]
    ) -> List[SolidityVulnerability]:
        """
        Detect missing amount/value validation (zero or negative)

        Common Pattern: Functions accepting amounts without validation
        """
        vulnerabilities = []

        for i, line in enumerate(lines):
            line_content = line.strip()
            context = contexts.get(i, {})

            # Check if it's a function with amount/value parameter
            if line_content.startswith('function '):
                if '(' in line_content and ')' in line_content:
                    params_match = re.search(r'\((.*?)\)', line_content)
                    if params_match:
                        params_str = params_match.group(1)

                        # Find amount/value parameters (uint256, uint, int)
                        amount_params = re.findall(
                            r'(?:uint256|uint|int256|int)\s+(\w*(?:amount|value|quantity|balance|size)\w*)',
                            params_str,
                            re.IGNORECASE
                        )

                        if amount_params:
                            function_name = context.get('function', 'unknown')

                            # Check next 15 lines for validation
                            check_window = lines[i+1:i+15]

                            for amount_param in amount_params:
                                has_validation = any(
                                    f'{amount_param}' in check_line and
                                    ('> 0' in check_line or '!= 0' in check_line or '>=' in check_line) and
                                    ('require' in check_line or 'revert' in check_line)
                                    for check_line in check_window
                                )

                                if not has_validation:
                                    vulnerabilities.append(SolidityVulnerability(
                                        vulnerability_type=VulnerabilityType.LOGIC_ERROR,
                                        severity="medium",
                                        title="Missing Amount Validation",
                                        description=(
                                            f"Parameter '{amount_param}' in function '{function_name}' lacks validation. "
                                            f"Should check: amount > 0 to prevent zero-value operations. "
                                            f"OWASP 2025: Input Validation ($14.6M in losses)."
                                        ),
                                        file_path=file_path,
                                        line_number=i + 1,
                                        function_name=function_name,
                                        contract_name=context.get('contract', 'unknown'),
                                        code_snippet=line_content,
                                        remediation=(
                                            f"Add validation:\n"
                                            f"require({amount_param} > 0, 'Amount must be greater than zero');"
                                        ),
                                        confidence=75
                                    ))

        return vulnerabilities

    def _detect_missing_array_bounds(
        self,
        lines: List[str],
        file_path: str,
        contexts: Dict[int, Dict[str, Any]]
    ) -> List[SolidityVulnerability]:
        """
        Detect missing array bounds validation

        Pattern: Array access without length check
        """
        vulnerabilities = []

        for i, line in enumerate(lines):
            line_content = line.strip()
            context = contexts.get(i, {})

            if not context.get('in_function'):
                continue

            # Check for array access patterns
            array_access_pattern = r'(\w+)\[(\w+|\d+)\]'
            matches = re.findall(array_access_pattern, line_content)

            for array_name, index in matches:
                # Skip if index is a number
                if index.isdigit():
                    continue

                # Check if there's a bounds check before this line
                prev_lines = lines[max(0, i-5):i]
                has_bounds_check = any(
                    f'{index}' in prev_line and
                    (f'{array_name}.length' in prev_line or 'length' in prev_line) and
                    ('require' in prev_line or 'if' in prev_line or '<' in prev_line)
                    for prev_line in prev_lines
                )

                if not has_bounds_check:
                    vulnerabilities.append(SolidityVulnerability(
                        vulnerability_type=VulnerabilityType.LOGIC_ERROR,
                        severity="medium",
                        title="Missing Array Bounds Validation",
                        description=(
                            f"Array access '{array_name}[{index}]' lacks bounds checking. "
                            f"Out-of-bounds access causes revert but wastes gas. "
                            f"OWASP 2025: Input Validation."
                        ),
                        file_path=file_path,
                        line_number=i + 1,
                        function_name=context.get('function', 'unknown'),
                        contract_name=context.get('contract', 'unknown'),
                        code_snippet=line_content,
                        remediation=(
                            f"Add bounds check:\n"
                            f"require({index} < {array_name}.length, 'Index out of bounds');"
                        ),
                        confidence=70
                    ))

        return vulnerabilities

    def _detect_unchecked_external_calls(
        self,
        lines: List[str],
        file_path: str,
        contexts: Dict[int, Dict[str, Any]]
    ) -> List[SolidityVulnerability]:
        """
        Detect unchecked external calls (enhanced)

        OWASP 2025: Unchecked External Calls ($550.7K in losses)
        Climbed from #10 to #6 in 2025 rankings

        Pattern: Low-level calls (.call, .delegatecall) without return value check
        """
        vulnerabilities = []

        low_level_calls = [
            r'\.call\s*\(',
            r'\.delegatecall\s*\(',
            r'\.staticcall\s*\(',
        ]

        for i, line in enumerate(lines):
            line_content = line.strip()
            context = contexts.get(i, {})

            if not context.get('in_function'):
                continue

            # Check for low-level calls
            for pattern in low_level_calls:
                if re.search(pattern, line_content):
                    # Check if return value is captured
                    captures_return = re.search(r'(?:bool\s+\w+|[\(\w]+)\s*=.*\.(?:call|delegatecall|staticcall)', line_content)

                    if captures_return:
                        # Check if the captured value is validated
                        # Extract the variable name
                        var_match = re.search(r'(?:bool\s+(\w+)|[\(](\w+))', line_content)
                        if var_match:
                            var_name = var_match.group(1) or var_match.group(2)

                            # Check next 5 lines for require/if with this variable
                            check_window = lines[i+1:i+5]
                            has_validation = any(
                                var_name in check_line and
                                ('require' in check_line or 'if' in check_line or 'assert' in check_line)
                                for check_line in check_window
                            )

                            if not has_validation:
                                vulnerabilities.append(SolidityVulnerability(
                                    vulnerability_type=VulnerabilityType.UNCHECKED_LOW_LEVEL_CALL,
                                    severity="high",
                                    title="Unchecked External Call Return Value",
                                    description=(
                                        f"Low-level call return value '{var_name}' captured but not validated. "
                                        f"OWASP 2025 #6: Unchecked External Calls ($550.7K in losses). "
                                        f"Climbed from #10 to #6 in 2025 rankings. "
                                        f"Failed external calls can cause unexpected behavior if not handled."
                                    ),
                                    file_path=file_path,
                                    line_number=i + 1,
                                    function_name=context.get('function', 'unknown'),
                                    contract_name=context.get('contract', 'unknown'),
                                    code_snippet=line_content,
                                    remediation=(
                                        f"Add validation:\n"
                                        f"require({var_name}, 'External call failed');\n"
                                        f"// OR use try/catch for better error handling"
                                    ),
                                    confidence=90
                                ))
                    else:
                        # Return value not even captured!
                        vulnerabilities.append(SolidityVulnerability(
                            vulnerability_type=VulnerabilityType.UNCHECKED_LOW_LEVEL_CALL,
                            severity="critical",
                            title="External Call Return Value Ignored",
                            description=(
                                f"Low-level call return value completely ignored. "
                                f"CRITICAL: OWASP 2025 #6 ($550.7K in losses). "
                                f"The call may fail silently causing logic errors or fund loss. "
                                f"Always capture and validate external call results."
                            ),
                            file_path=file_path,
                            line_number=i + 1,
                            function_name=context.get('function', 'unknown'),
                            contract_name=context.get('contract', 'unknown'),
                            code_snippet=line_content,
                            remediation=(
                                "Capture and validate return value:\n"
                                "(bool success, ) = target.call(...);\n"
                                "require(success, 'External call failed');"
                            ),
                            confidence=95
                        ))

        return vulnerabilities

    def _detect_unsafe_type_conversions(
        self,
        lines: List[str],
        file_path: str,
        contexts: Dict[int, Dict[str, Any]]
    ) -> List[SolidityVulnerability]:
        """
        Detect unsafe type conversions

        Pattern: Converting between types without validation
        """
        vulnerabilities = []

        conversion_patterns = [
            r'uint256\s*\(\s*int',  # int to uint
            r'uint\s*\(\s*int',
            r'int\s*\(\s*uint',      # uint to int
            r'address\s*\(\s*uint',  # uint to address
        ]

        for i, line in enumerate(lines):
            line_content = line.strip()
            context = contexts.get(i, {})

            if not context.get('in_function'):
                continue

            for pattern in conversion_patterns:
                if re.search(pattern, line_content):
                    # Check if there's validation nearby
                    check_window = lines[max(0, i-2):i+3]
                    has_validation = any(
                        'require' in check_line or 'assert' in check_line
                        for check_line in check_window
                    )

                    if not has_validation:
                        vulnerabilities.append(SolidityVulnerability(
                            vulnerability_type=VulnerabilityType.LOGIC_ERROR,
                            severity="medium",
                            title="Unsafe Type Conversion",
                            description=(
                                f"Type conversion without validation at line {i+1}. "
                                f"Converting between signed/unsigned or numeric/address types can cause unexpected behavior. "
                                f"OWASP 2025: Input Validation."
                            ),
                            file_path=file_path,
                            line_number=i + 1,
                            function_name=context.get('function', 'unknown'),
                            contract_name=context.get('contract', 'unknown'),
                            code_snippet=line_content,
                            remediation=(
                                "Add validation before conversion:\n"
                                "require(value >= 0, 'Invalid conversion');\n"
                                "// OR use SafeCast library for safe conversions"
                            ),
                            confidence=70
                        ))

        return vulnerabilities

    def _get_current_function_contract(self, line_index: int, lines: List[str]) -> str:
        """Helper to determine current contract context"""
        current_contract = "unknown"
        
        # Look backwards to find most recent contract
        for i in range(line_index, -1, -1):
            line = lines[i].strip()
            if line.startswith('contract ') or line.startswith('abstract contract '):
                match = re.search(r'contract\s+(\w+)', line)
                if match:
                    current_contract = match.group(1)
                    break
            # Stop looking if we hit another contract boundary
            if line.startswith('contract ') and i < line_index:
                break
        
        return current_contract
    
    def _initialize_patterns(self) -> Dict[str, List[str]]:
        """Initialize vulnerability pattern detectors"""
        return {
            'reentrancy': [
                r'\.call\(',
                r'\.transfer\(',
                r'\.send\('
            ],
            'access_control': [
                r'function\s+\w+\s*public',
                r'missing.*modifier',
                r'no.*access.*control'
            ],
            'integer_overflow': [
                r'[\+\-\*\/]',
                r'(balance|amount|total|supply).*[\+\-\*\/]'
            ],
            'unchecked_call': [
                r'\.call\(',
                r'\.delegatecall\('
            ],
            'oracle_manipulation': [
                r'uniswap.*router',
                r'price.*oracle',
                r'getAmountOut'
            ]
        }
