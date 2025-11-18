"""
Gas Optimization Analyzer - Week 4 Day 3

Analyzes Solidity smart contracts for gas efficiency and provides
optimization recommendations to reduce deployment and execution costs.

Features:
- Pattern-based gas inefficiency detection
- Gas cost estimation for common operations
- Storage optimization suggestions
- Function optimization recommendations
- Dollar cost calculations based on gas prices

Author: Alprina Development Team
Date: 2025-11-13
"""

import re
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple
from enum import Enum


class GasIssueType(Enum):
    """Types of gas optimization issues"""
    STORAGE_LAYOUT = "storage_layout"
    REDUNDANT_OPERATIONS = "redundant_operations"
    LOOP_OPTIMIZATION = "loop_optimization"
    VISIBILITY = "visibility"
    DATA_TYPES = "data_types"
    CACHING = "caching"
    SHORT_CIRCUIT = "short_circuit"
    UNCHECKED_MATH = "unchecked_math"
    IMMUTABLE = "immutable"
    CONSTANT = "constant"


@dataclass
class GasOptimization:
    """Represents a gas optimization opportunity"""
    issue_type: GasIssueType
    severity: str  # "high", "medium", "low"
    title: str
    description: str
    file_path: str
    line_number: Optional[int]
    function_name: Optional[str]

    # Gas estimates
    current_gas_cost: int  # Estimated current cost
    optimized_gas_cost: int  # Estimated after optimization
    gas_saved: int  # Difference

    # Recommendations
    code_before: Optional[str] = None
    code_after: Optional[str] = None
    recommendation: str = ""

    # Financial impact (based on gas price)
    eth_saved_per_tx: float = 0.0  # ETH saved per transaction
    usd_saved_per_tx: float = 0.0  # USD saved per transaction (at $2000/ETH)

    # Context
    confidence: str = "high"  # high, medium, low
    references: List[str] = None

    def __post_init__(self):
        if self.references is None:
            self.references = []

        # Calculate financial impact
        # Assume 50 gwei gas price (typical)
        gwei_price = 50
        eth_price_usd = 2000

        # 1 gwei = 0.000000001 ETH
        self.eth_saved_per_tx = (self.gas_saved * gwei_price) / 1_000_000_000
        self.usd_saved_per_tx = self.eth_saved_per_tx * eth_price_usd


class GasOptimizationAnalyzer:
    """
    Gas Optimization Analyzer

    Detects gas inefficiencies and provides optimization recommendations
    for Solidity smart contracts.
    """

    # Gas costs for common operations (approximate, based on Ethereum)
    GAS_COSTS = {
        "SLOAD": 2100,  # Storage read (cold)
        "SLOAD_WARM": 100,  # Storage read (warm)
        "SSTORE": 20000,  # Storage write (cold, non-zero to non-zero)
        "SSTORE_NEW": 20000,  # Storage write (zero to non-zero)
        "SSTORE_DELETE": 5000,  # Storage write (non-zero to zero) + refund
        "MLOAD": 3,  # Memory read
        "MSTORE": 3,  # Memory write
        "CALL": 2600,  # External call (base)
        "ADD": 3,  # Addition
        "MUL": 5,  # Multiplication
        "DIV": 5,  # Division
        "LOG": 375,  # Event log (base)
        "CREATE": 32000,  # Contract creation
        "JUMPDEST": 1,  # Jump destination
    }

    def __init__(self):
        self.optimizations: List[GasOptimization] = []

    def analyze_contract(self, source_code: str, file_path: str) -> List[GasOptimization]:
        """
        Analyze contract for gas optimization opportunities

        Args:
            source_code: Solidity source code
            file_path: Path to contract file

        Returns:
            List of gas optimization opportunities
        """
        self.optimizations = []

        # Parse contract structure
        lines = source_code.split('\n')

        # Detect patterns
        self._detect_storage_optimization(lines, file_path)
        self._detect_redundant_operations(lines, file_path)
        self._detect_loop_optimization(lines, file_path)
        self._detect_visibility_optimization(lines, file_path)
        self._detect_data_type_optimization(lines, file_path)
        self._detect_caching_opportunities(lines, file_path)
        self._detect_short_circuit_optimization(lines, file_path)
        self._detect_unchecked_math(lines, file_path)
        self._detect_immutable_optimization(lines, file_path)
        self._detect_constant_optimization(lines, file_path)

        return self.optimizations

    def _detect_storage_optimization(self, lines: List[str], file_path: str):
        """Detect storage layout inefficiencies"""

        # Pattern: Multiple small variables that could be packed
        storage_vars = []

        for i, line in enumerate(lines):
            # Match storage variable declarations
            match = re.search(r'(uint8|uint16|uint32|uint64|uint128|bool|address)\s+(?:public\s+|private\s+)?(\w+);', line)
            if match:
                var_type = match.group(1)
                var_name = match.group(2)
                storage_vars.append((i + 1, var_type, var_name))

        # Check if variables can be packed better
        if len(storage_vars) >= 2:
            # Simple heuristic: if we have multiple uint8/uint16/bool, they could be packed
            small_types = [v for v in storage_vars if v[1] in ['uint8', 'uint16', 'uint32', 'uint64', 'uint128', 'bool']]

            if len(small_types) >= 2:
                # Calculate potential savings
                # Each storage slot costs ~20,000 gas to write (cold)
                # Packing can save multiple slots
                slots_before = len(small_types)
                slots_after = (sum(self._get_type_size(v[1]) for v in small_types) + 255) // 256
                slots_saved = slots_before - slots_after

                if slots_saved > 0:
                    gas_saved = slots_saved * self.GAS_COSTS["SSTORE"]

                    self.optimizations.append(GasOptimization(
                        issue_type=GasIssueType.STORAGE_LAYOUT,
                        severity="high" if gas_saved > 40000 else "medium",
                        title="Storage Packing Optimization",
                        description=f"Multiple small storage variables detected that could be packed into fewer storage slots. Currently using ~{slots_before} slots, could be optimized to ~{slots_after} slots.",
                        file_path=file_path,
                        line_number=small_types[0][0],
                        function_name=None,
                        current_gas_cost=slots_before * self.GAS_COSTS["SSTORE"],
                        optimized_gas_cost=slots_after * self.GAS_COSTS["SSTORE"],
                        gas_saved=gas_saved,
                        code_before=f"// Current: {len(small_types)} separate declarations",
                        code_after=f"// Optimized: Pack into {slots_after} storage slots by declaring sequentially",
                        recommendation="Declare storage variables of smaller types sequentially to pack them into the same storage slots. Each storage slot is 32 bytes (256 bits).",
                        references=[
                            "https://docs.soliditylang.org/en/latest/internals/layout_in_storage.html"
                        ]
                    ))

    def _detect_redundant_operations(self, lines: List[str], file_path: str):
        """Detect redundant calculations and operations"""

        for i, line in enumerate(lines):
            # Pattern: Same expression calculated multiple times
            # Example: x + y appears multiple times in same function

            # Pattern: Reading same storage variable multiple times
            storage_reads = re.findall(r'(\w+)\[', line)
            if len(storage_reads) > len(set(storage_reads)):
                # Duplicate array/mapping access
                self.optimizations.append(GasOptimization(
                    issue_type=GasIssueType.REDUNDANT_OPERATIONS,
                    severity="medium",
                    title="Redundant Storage Access",
                    description="Same storage location accessed multiple times in a single expression. Consider caching in memory.",
                    file_path=file_path,
                    line_number=i + 1,
                    function_name=self._extract_function_name(lines, i),
                    current_gas_cost=len(storage_reads) * self.GAS_COSTS["SLOAD"],
                    optimized_gas_cost=self.GAS_COSTS["SLOAD"] + (len(storage_reads) - 1) * self.GAS_COSTS["MLOAD"],
                    gas_saved=(len(storage_reads) - 1) * (self.GAS_COSTS["SLOAD"] - self.GAS_COSTS["MLOAD"]),
                    code_before=line.strip(),
                    code_after="// Cache storage value in memory variable first",
                    recommendation="Cache the storage value in a memory variable and reuse it."
                ))

    def _detect_loop_optimization(self, lines: List[str], file_path: str):
        """Detect loop inefficiencies"""

        for i, line in enumerate(lines):
            # Pattern: for (uint i = 0; i < array.length; i++)
            if 'for' in line and '.length' in line and '++' in line:
                # Reading array.length in every iteration
                self.optimizations.append(GasOptimization(
                    issue_type=GasIssueType.LOOP_OPTIMIZATION,
                    severity="high",
                    title="Loop Length Not Cached",
                    description="Array length is read from storage in every loop iteration. Cache it in a local variable.",
                    file_path=file_path,
                    line_number=i + 1,
                    function_name=self._extract_function_name(lines, i),
                    current_gas_cost=100 * self.GAS_COSTS["SLOAD"],  # Assume 100 iterations
                    optimized_gas_cost=self.GAS_COSTS["SLOAD"] + 100 * self.GAS_COSTS["MLOAD"],
                    gas_saved=100 * (self.GAS_COSTS["SLOAD"] - self.GAS_COSTS["MLOAD"]),
                    code_before=line.strip(),
                    code_after="uint256 length = array.length; for (uint256 i = 0; i < length; ++i)",
                    recommendation="Cache array.length in a local variable before the loop. Use ++i instead of i++ for slightly lower gas.",
                    references=[
                        "https://github.com/crytic/slither/wiki/Detector-Documentation#costly-operations-inside-a-loop"
                    ]
                ))

            # Pattern: i++ vs ++i
            if re.search(r'for\s*\([^;]+;[^;]+;\s*\w+\+\+\s*\)', line):
                self.optimizations.append(GasOptimization(
                    issue_type=GasIssueType.LOOP_OPTIMIZATION,
                    severity="low",
                    title="Use Prefix Increment (++i) Instead of Postfix (i++)",
                    description="Prefix increment (++i) is slightly cheaper than postfix (i++) in loops.",
                    file_path=file_path,
                    line_number=i + 1,
                    function_name=self._extract_function_name(lines, i),
                    current_gas_cost=100 * 8,  # Approximate difference per iteration
                    optimized_gas_cost=100 * 5,
                    gas_saved=100 * 3,
                    code_before=re.search(r'(for\s*\([^)]+\))', line).group(1) if re.search(r'(for\s*\([^)]+\))', line) else line.strip(),
                    code_after="for (uint256 i = 0; i < length; ++i)",
                    recommendation="Use ++i instead of i++ in loops to save gas."
                ))

    def _detect_visibility_optimization(self, lines: List[str], file_path: str):
        """Detect functions that could have more restrictive visibility"""

        for i, line in enumerate(lines):
            # Pattern: public function not called internally
            if 'function' in line and 'public' in line and 'view' not in line and 'pure' not in line:
                func_match = re.search(r'function\s+(\w+)\s*\(', line)
                if func_match:
                    func_name = func_match.group(1)

                    # Simple heuristic: if function name doesn't appear elsewhere, could be external
                    occurrences = sum(1 for l in lines if func_name in l)
                    if occurrences == 1:  # Only the declaration
                        self.optimizations.append(GasOptimization(
                            issue_type=GasIssueType.VISIBILITY,
                            severity="low",
                            title=f"Function '{func_name}' Can Be External",
                            description="Function is marked 'public' but appears to never be called internally. Use 'external' to save gas.",
                            file_path=file_path,
                            line_number=i + 1,
                            function_name=func_name,
                            current_gas_cost=1000,  # Approximate overhead for public
                            optimized_gas_cost=600,
                            gas_saved=400,
                            code_before=line.strip(),
                            code_after=line.strip().replace('public', 'external'),
                            recommendation="Change 'public' to 'external' for functions not called internally. External functions can read arguments from calldata instead of copying to memory."
                        ))

    def _detect_data_type_optimization(self, lines: List[str], file_path: str):
        """Detect suboptimal data type choices"""

        for i, line in enumerate(lines):
            # Pattern: Using uint8 in memory/function params (inefficient)
            if re.search(r'(uint8|uint16)\s+memory\s+\w+', line):
                self.optimizations.append(GasOptimization(
                    issue_type=GasIssueType.DATA_TYPES,
                    severity="low",
                    title="Use uint256 for Memory Variables",
                    description="Using uint8/uint16 for memory variables is less efficient than uint256. The EVM operates on 256-bit words.",
                    file_path=file_path,
                    line_number=i + 1,
                    function_name=self._extract_function_name(lines, i),
                    current_gas_cost=50,
                    optimized_gas_cost=30,
                    gas_saved=20,
                    code_before=line.strip(),
                    code_after=line.strip().replace('uint8', 'uint256').replace('uint16', 'uint256'),
                    recommendation="Use uint256 for memory variables and function parameters unless you need storage packing."
                ))

    def _detect_caching_opportunities(self, lines: List[str], file_path: str):
        """Detect values that should be cached"""

        for i, line in enumerate(lines):
            # Pattern: msg.sender used multiple times
            sender_count = line.count('msg.sender')
            if sender_count > 1:
                gas_saved = (sender_count - 1) * 100  # Approximate
                self.optimizations.append(GasOptimization(
                    issue_type=GasIssueType.CACHING,
                    severity="low",
                    title="Cache msg.sender",
                    description=f"msg.sender is accessed {sender_count} times. Cache it in a local variable.",
                    file_path=file_path,
                    line_number=i + 1,
                    function_name=self._extract_function_name(lines, i),
                    current_gas_cost=sender_count * 100,
                    optimized_gas_cost=100 + (sender_count - 1) * 3,
                    gas_saved=gas_saved,
                    code_before=line.strip(),
                    code_after="address sender = msg.sender; // Cache and reuse",
                    recommendation="Cache msg.sender in a local variable at the start of the function."
                ))

    def _detect_short_circuit_optimization(self, lines: List[str], file_path: str):
        """Detect conditions that could benefit from short-circuiting"""

        for i, line in enumerate(lines):
            # Pattern: require(expensive_check() && cheap_check())
            # Should be: require(cheap_check() && expensive_check())
            if 'require' in line and '&&' in line:
                # This is a heuristic - we can't determine which is cheaper without deeper analysis
                self.optimizations.append(GasOptimization(
                    issue_type=GasIssueType.SHORT_CIRCUIT,
                    severity="low",
                    title="Optimize Condition Order",
                    description="Order conditions from cheapest to most expensive in boolean expressions. Short-circuiting will skip expensive operations.",
                    file_path=file_path,
                    line_number=i + 1,
                    function_name=self._extract_function_name(lines, i),
                    current_gas_cost=1000,
                    optimized_gas_cost=500,
                    gas_saved=500,
                    code_before=line.strip(),
                    code_after="// Order: cheap check && expensive check",
                    recommendation="Put the cheapest condition first in && expressions to take advantage of short-circuit evaluation.",
                    confidence="medium"
                ))

    def _detect_unchecked_math(self, lines: List[str], file_path: str):
        """Detect arithmetic that could use unchecked blocks (Solidity 0.8+)"""

        for i, line in enumerate(lines):
            # Pattern: i++ in loops (Solidity 0.8+ has overflow checks)
            if 'for' in line and ('++' in line or '+=' in line):
                self.optimizations.append(GasOptimization(
                    issue_type=GasIssueType.UNCHECKED_MATH,
                    severity="medium",
                    title="Use Unchecked Block for Loop Counter",
                    description="Loop counters in Solidity 0.8+ have overflow checks. Use unchecked{} block for loop increments to save gas.",
                    file_path=file_path,
                    line_number=i + 1,
                    function_name=self._extract_function_name(lines, i),
                    current_gas_cost=100 * 50,  # Assume 100 iterations
                    optimized_gas_cost=100 * 30,
                    gas_saved=100 * 20,
                    code_before=line.strip(),
                    code_after="for (uint256 i; i < length;) { ... unchecked { ++i; } }",
                    recommendation="Wrap loop increments in unchecked{} blocks. Loop counters will never realistically overflow.",
                    references=[
                        "https://docs.soliditylang.org/en/latest/control-structures.html#checked-or-unchecked-arithmetic"
                    ]
                ))

    def _detect_immutable_optimization(self, lines: List[str], file_path: str):
        """Detect variables that could be immutable"""

        for i, line in enumerate(lines):
            # Pattern: Variable declared but only assigned in constructor
            if re.search(r'(address|uint256)\s+(?:public\s+|private\s+)?(\w+);', line):
                var_match = re.search(r'(address|uint256)\s+(?:public\s+|private\s+)?(\w+);', line)
                if var_match and 'immutable' not in line and 'constant' not in line:
                    var_type = var_match.group(1)
                    var_name = var_match.group(2)

                    # Check if it's assigned in constructor
                    constructor_assignment = False
                    other_assignments = 0

                    in_constructor = False
                    for j, l in enumerate(lines):
                        if 'constructor' in l:
                            in_constructor = True
                        if in_constructor and f'{var_name} =' in l:
                            constructor_assignment = True
                        if not in_constructor and f'{var_name} =' in l and j != i:
                            other_assignments += 1
                        if in_constructor and '}' in l:
                            in_constructor = False

                    if constructor_assignment and other_assignments == 0:
                        self.optimizations.append(GasOptimization(
                            issue_type=GasIssueType.IMMUTABLE,
                            severity="medium",
                            title=f"Variable '{var_name}' Can Be Immutable",
                            description="Variable is only assigned in constructor. Mark it as immutable to save gas.",
                            file_path=file_path,
                            line_number=i + 1,
                            function_name=None,
                            current_gas_cost=self.GAS_COSTS["SLOAD"],
                            optimized_gas_cost=3,  # Immutable is copied directly into bytecode
                            gas_saved=self.GAS_COSTS["SLOAD"] - 3,
                            code_before=line.strip(),
                            code_after=line.strip().replace(';', ' immutable;'),
                            recommendation="Mark as 'immutable' to embed value in contract bytecode. Saves 2100 gas per read."
                        ))

    def _detect_constant_optimization(self, lines: List[str], file_path: str):
        """Detect variables that could be constant"""

        for i, line in enumerate(lines):
            # Pattern: Variable with literal value that never changes
            if re.search(r'(uint256|string)\s+(?:public\s+|private\s+)?(\w+)\s*=\s*["\d]', line):
                if 'constant' not in line and 'immutable' not in line:
                    var_match = re.search(r'(uint256|string)\s+(?:public\s+|private\s+)?(\w+)', line)
                    if var_match:
                        var_name = var_match.group(2)

                        # Check if variable is never reassigned
                        reassigned = any(f'{var_name} =' in l and i != j for j, l in enumerate(lines))

                        if not reassigned:
                            self.optimizations.append(GasOptimization(
                                issue_type=GasIssueType.CONSTANT,
                                severity="medium",
                                title=f"Variable '{var_name}' Can Be Constant",
                                description="Variable has a fixed value and is never reassigned. Mark it as constant.",
                                file_path=file_path,
                                line_number=i + 1,
                                function_name=None,
                                current_gas_cost=self.GAS_COSTS["SLOAD"],
                                optimized_gas_cost=0,  # Constants are free
                                gas_saved=self.GAS_COSTS["SLOAD"],
                                code_before=line.strip(),
                                code_after=line.strip().replace('=', 'constant ='),
                                recommendation="Mark as 'constant' to replace storage access with direct value substitution. Saves 2100 gas per read."
                            ))

    def _get_type_size(self, type_name: str) -> int:
        """Get size of type in bits"""
        if 'uint8' in type_name or 'int8' in type_name or type_name == 'bool':
            return 8
        elif 'uint16' in type_name or 'int16' in type_name:
            return 16
        elif 'uint32' in type_name or 'int32' in type_name:
            return 32
        elif 'uint64' in type_name or 'int64' in type_name:
            return 64
        elif 'uint128' in type_name or 'int128' in type_name:
            return 128
        elif 'address' in type_name:
            return 160
        else:
            return 256

    def _extract_function_name(self, lines: List[str], current_line: int) -> Optional[str]:
        """Extract function name for a given line"""
        # Look backwards to find function declaration
        for i in range(current_line, -1, -1):
            if 'function' in lines[i]:
                match = re.search(r'function\s+(\w+)\s*\(', lines[i])
                if match:
                    return match.group(1)
        return None

    def generate_report(self) -> Dict:
        """Generate comprehensive gas optimization report"""
        total_gas_saved = sum(opt.gas_saved for opt in self.optimizations)
        total_eth_saved = sum(opt.eth_saved_per_tx for opt in self.optimizations)
        total_usd_saved = sum(opt.usd_saved_per_tx for opt in self.optimizations)

        by_severity = {
            'high': [o for o in self.optimizations if o.severity == 'high'],
            'medium': [o for o in self.optimizations if o.severity == 'medium'],
            'low': [o for o in self.optimizations if o.severity == 'low']
        }

        by_type = {}
        for opt in self.optimizations:
            type_name = opt.issue_type.value
            if type_name not in by_type:
                by_type[type_name] = []
            by_type[type_name].append(opt)

        return {
            'total_optimizations': len(self.optimizations),
            'total_gas_saved': total_gas_saved,
            'total_eth_saved_per_tx': total_eth_saved,
            'total_usd_saved_per_tx': total_usd_saved,
            'by_severity': {k: len(v) for k, v in by_severity.items()},
            'by_type': {k: len(v) for k, v in by_type.items()},
            'optimizations': self.optimizations
        }
