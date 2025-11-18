"""
Symbolic Execution Engine for Solidity Smart Contracts

WEEK 3 DAY 1: Symbolic Execution
=================================

Implements symbolic execution to detect vulnerabilities through path analysis
and constraint solving. Uses Z3 theorem prover for constraint satisfaction.

Author: Alprina Development Team
Date: 2025-11-12

References:
- OYENTE: Symbolic execution for Ethereum (2016)
- Mythril: Constraint-based vulnerability detection
- Manticore: Dynamic symbolic execution
"""

import re
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Optional z3 dependency for symbolic execution
try:
    import z3
    Z3_AVAILABLE = True
except ImportError:
    Z3_AVAILABLE = False
    # Mock z3 types for when it's not available
    class z3:
        ExprRef = Any
        Solver = Any

try:
    from .solidity_analyzer import SolidityVulnerability, VulnerabilityType
except ImportError:
    # For standalone testing
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from solidity_analyzer import SolidityVulnerability, VulnerabilityType


class SymbolicType(Enum):
    """Types in symbolic execution"""
    UINT256 = "uint256"
    INT256 = "int256"
    ADDRESS = "address"
    BOOL = "bool"
    BYTES32 = "bytes32"
    UNKNOWN = "unknown"


@dataclass
class SymbolicVariable:
    """Represents a symbolic variable during execution"""
    name: str
    sym_type: SymbolicType
    z3_var: z3.ExprRef
    is_tainted: bool = False  # From user input
    source_line: Optional[int] = None


@dataclass
class PathConstraint:
    """Represents a constraint along an execution path"""
    condition: str
    z3_constraint: z3.BoolRef
    line_number: int
    is_true_branch: bool  # True if we took the "true" branch


@dataclass
class SymbolicState:
    """State during symbolic execution"""
    variables: Dict[str, SymbolicVariable] = field(default_factory=dict)
    constraints: List[PathConstraint] = field(default_factory=list)
    storage: Dict[str, SymbolicVariable] = field(default_factory=dict)
    memory: Dict[str, SymbolicVariable] = field(default_factory=dict)
    execution_path: List[int] = field(default_factory=list)  # Line numbers

    def copy(self) -> 'SymbolicState':
        """Create a copy of this state for branch exploration"""
        import copy
        return copy.deepcopy(self)


@dataclass
class SymbolicVulnerability:
    """Vulnerability found via symbolic execution"""
    vulnerability_type: str
    severity: str
    title: str
    description: str
    line_number: int
    function_name: str
    proof: Optional[str] = None  # Z3 model showing exploit
    path_constraints: List[str] = field(default_factory=list)
    confidence: int = 95


class SymbolicExecutor:
    """
    Symbolic execution engine for Solidity contracts

    Capabilities:
    - Integer overflow/underflow detection via constraint solving
    - Unreachable code detection
    - Taint analysis for user inputs
    - Path feasibility analysis
    - Division by zero detection

    Week 3 Day 1 Implementation:
    - Basic symbolic execution framework
    - Integer overflow detection with Z3
    - Simple path exploration
    """

    def __init__(self):
        self.z3_available = Z3_AVAILABLE
        if Z3_AVAILABLE:
            self.solver = z3.Solver()
        else:
            self.solver = None
        self.vulnerabilities: List[SymbolicVulnerability] = []

        # Z3 constants for Solidity types
        self.MAX_UINT256 = 2**256 - 1
        self.MIN_INT256 = -(2**255)
        self.MAX_INT256 = 2**255 - 1

    def analyze_contract(self, contract_code: str, file_path: str) -> List[SolidityVulnerability]:
        """
        Analyze contract using symbolic execution

        Returns standard SolidityVulnerability objects for integration
        with existing Week 2 economic impact calculator
        """
        # If z3 is not available, return empty list with warning
        if not self.z3_available:
            return []

        self.vulnerabilities = []

        # Extract functions from contract
        functions = self._extract_functions(contract_code)

        for func in functions:
            # Symbolically execute each function
            self._execute_function(func, file_path)

        # Convert to standard format
        return self._convert_to_standard_format(file_path)

    def _extract_functions(self, contract_code: str) -> List[Dict[str, Any]]:
        """Extract function definitions from contract"""
        functions = []
        lines = contract_code.split('\n')

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Match function definition
            func_match = re.match(
                r'function\s+(\w+)\s*\([^)]*\)\s*(public|external|internal|private)?',
                line
            )

            if func_match:
                func_name = func_match.group(1)
                visibility = func_match.group(2) or 'internal'

                # Extract function body
                start_line = i
                brace_count = 0
                body_lines = []

                # Find opening brace
                while i < len(lines) and '{' not in lines[i]:
                    i += 1

                if i < len(lines):
                    brace_count = lines[i].count('{') - lines[i].count('}')
                    body_lines.append(lines[i])
                    i += 1

                    # Extract until closing brace
                    while i < len(lines) and brace_count > 0:
                        line = lines[i]
                        brace_count += line.count('{') - line.count('}')
                        body_lines.append(line)
                        i += 1

                functions.append({
                    'name': func_name,
                    'visibility': visibility,
                    'start_line': start_line + 1,
                    'body': '\n'.join(body_lines),
                    'body_lines': body_lines
                })

            i += 1

        return functions

    def _execute_function(self, func: Dict[str, Any], file_path: str):
        """
        Symbolically execute a function

        Explores all execution paths and detects vulnerabilities
        """
        func_name = func['name']
        start_line = func['start_line']
        body_lines = func['body_lines']

        # Initialize symbolic state
        initial_state = SymbolicState()

        # Create symbolic parameters (tainted input)
        params = self._extract_parameters(func['body'])
        for param_name, param_type in params.items():
            sym_var = self._create_symbolic_variable(param_name, param_type, is_tainted=True)
            initial_state.variables[param_name] = sym_var

        # Execute symbolically
        self._explore_paths(body_lines, initial_state, func_name, start_line, file_path)

    def _extract_parameters(self, func_def: str) -> Dict[str, SymbolicType]:
        """Extract function parameters and their types"""
        params = {}

        # Match parameter list
        param_match = re.search(r'\(([^)]*)\)', func_def)
        if not param_match:
            return params

        param_list = param_match.group(1)
        if not param_list.strip():
            return params

        # Parse each parameter
        for param in param_list.split(','):
            param = param.strip()
            if not param:
                continue

            parts = param.split()
            if len(parts) >= 2:
                param_type_str = parts[0]
                param_name = parts[1]

                # Map to symbolic type
                param_type = self._map_to_symbolic_type(param_type_str)
                params[param_name] = param_type

        return params

    def _map_to_symbolic_type(self, type_str: str) -> SymbolicType:
        """Map Solidity type string to SymbolicType"""
        if 'uint' in type_str:
            return SymbolicType.UINT256
        elif type_str.startswith('int'):
            return SymbolicType.INT256
        elif type_str == 'address':
            return SymbolicType.ADDRESS
        elif type_str == 'bool':
            return SymbolicType.BOOL
        elif 'bytes' in type_str:
            return SymbolicType.BYTES32
        else:
            return SymbolicType.UNKNOWN

    def _create_symbolic_variable(
        self,
        name: str,
        sym_type: SymbolicType,
        is_tainted: bool = False
    ) -> SymbolicVariable:
        """Create a symbolic variable with Z3 representation"""

        if sym_type == SymbolicType.UINT256:
            z3_var = z3.BitVec(name, 256)
        elif sym_type == SymbolicType.INT256:
            z3_var = z3.BitVec(name, 256)
        elif sym_type == SymbolicType.BOOL:
            z3_var = z3.Bool(name)
        elif sym_type == SymbolicType.ADDRESS:
            z3_var = z3.BitVec(name, 160)  # Addresses are 160 bits
        else:
            z3_var = z3.BitVec(name, 256)  # Default to 256-bit

        return SymbolicVariable(
            name=name,
            sym_type=sym_type,
            z3_var=z3_var,
            is_tainted=is_tainted
        )

    def _explore_paths(
        self,
        body_lines: List[str],
        state: SymbolicState,
        func_name: str,
        start_line: int,
        file_path: str
    ):
        """
        Explore execution paths in function body

        Day 2 Enhancement: Path condition extraction and branch analysis
        - Extract conditions from if/require/assert statements
        - Track path constraints for each branch
        - Detect unreachable code using constraint solving
        """

        i = 0
        while i < len(body_lines):
            line = body_lines[i]
            line_number = start_line + i
            line_stripped = line.strip()

            if not line_stripped or line_stripped.startswith('//'):
                i += 1
                continue

            # Track execution path
            state.execution_path.append(line_number)

            # DAY 2: Extract and analyze conditional branches
            if self._is_conditional(line_stripped):
                self._analyze_conditional_branch(
                    body_lines, i, state, func_name, start_line, file_path
                )

            # DAY 2: Detect require/assert statements
            if 'require(' in line_stripped or 'assert(' in line_stripped:
                self._analyze_requirement(line_stripped, line_number, state, func_name)

            # Day 1: Arithmetic operations
            self._analyze_arithmetic(line_stripped, line_number, state, func_name, file_path)

            # Day 1: Divisions
            self._analyze_division(line_stripped, line_number, state, func_name, file_path)

            # Day 1: Tainted data flow
            self._analyze_taint_flow(line_stripped, line_number, state, func_name, file_path)

            # DAY 2: Check for unreachable code
            if len(state.constraints) > 0:
                self._check_path_feasibility(state, line_number, func_name, file_path)

            i += 1

    def _is_conditional(self, line: str) -> bool:
        """Check if line contains a conditional statement"""
        return (
            line.strip().startswith('if ') or
            line.strip().startswith('if(') or
            'else if' in line or
            'else {' in line
        )

    def _analyze_conditional_branch(
        self,
        body_lines: List[str],
        line_index: int,
        state: SymbolicState,
        func_name: str,
        start_line: int,
        file_path: str
    ):
        """
        Analyze conditional branches (if/else)

        DAY 2: Path Condition Extraction
        - Extract condition from if statement
        - Create Z3 constraint for condition
        - Explore both true and false branches
        - Detect unreachable branches
        """
        line = body_lines[line_index]
        line_number = start_line + line_index

        # Extract condition from if statement
        if_match = re.search(r'if\s*\(([^)]+)\)', line)
        if not if_match:
            return

        condition_str = if_match.group(1).strip()

        # Parse condition into Z3 constraint
        z3_constraint = self._parse_condition_to_z3(condition_str, state)

        if z3_constraint is None:
            # Can't parse condition, skip advanced analysis
            return

        # Create path constraint for true branch
        true_constraint = PathConstraint(
            condition=condition_str,
            z3_constraint=z3_constraint,
            line_number=line_number,
            is_true_branch=True
        )

        # Create path constraint for false branch
        false_constraint = PathConstraint(
            condition=f"!({condition_str})",
            z3_constraint=z3.Not(z3_constraint),
            line_number=line_number,
            is_true_branch=False
        )

        # Check if true branch is feasible
        true_state = state.copy()
        true_state.constraints.append(true_constraint)

        if self._is_path_feasible(true_state):
            # True branch is reachable
            pass
        else:
            # True branch is unreachable!
            self.vulnerabilities.append(SymbolicVulnerability(
                vulnerability_type="unreachable_code",
                severity="low",
                title=f"Unreachable Code in {func_name}",
                description=(
                    f"The condition `{condition_str}` at line {line_number} "
                    f"can never be true given the current path constraints. "
                    f"The code inside this if-block is unreachable."
                ),
                line_number=line_number,
                function_name=func_name,
                proof=f"Z3 proved condition is always false: {condition_str}",
                confidence=95
            ))

        # Check if false branch is feasible (for else clauses)
        false_state = state.copy()
        false_state.constraints.append(false_constraint)

        if not self._is_path_feasible(false_state):
            # Condition is always true (else is unreachable)
            self.vulnerabilities.append(SymbolicVulnerability(
                vulnerability_type="unreachable_code",
                severity="info",
                title=f"Condition Always True in {func_name}",
                description=(
                    f"The condition `{condition_str}` at line {line_number} "
                    f"is always true. Consider simplifying the code."
                ),
                line_number=line_number,
                function_name=func_name,
                proof=f"Z3 proved condition is always true: {condition_str}",
                confidence=90
            ))

    def _parse_condition_to_z3(self, condition: str, state: SymbolicState) -> Optional[z3.BoolRef]:
        """
        Parse a Solidity condition into a Z3 constraint

        DAY 2: Enhanced condition parsing
        Supports:
        - Comparisons: ==, !=, <, >, <=, >=
        - Boolean operators: &&, ||, !
        - Basic arithmetic
        """

        # Simple comparison operators
        for op, z3_op in [
            ('==', lambda a, b: a == b),
            ('!=', lambda a, b: a != b),
            ('>=', lambda a, b: z3.UGE(a, b)),  # Unsigned greater or equal
            ('<=', lambda a, b: z3.ULE(a, b)),
            ('>', lambda a, b: z3.UGT(a, b)),
            ('<', lambda a, b: z3.ULT(a, b)),
        ]:
            if op in condition:
                parts = condition.split(op)
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip()

                    # Try to create Z3 expressions
                    left_z3 = self._parse_expression_to_z3(left, state)
                    right_z3 = self._parse_expression_to_z3(right, state)

                    if left_z3 is not None and right_z3 is not None:
                        return z3_op(left_z3, right_z3)

        # Boolean conditions
        if condition in state.variables:
            var = state.variables[condition]
            if var.sym_type == SymbolicType.BOOL:
                return var.z3_var

        # Negation
        if condition.startswith('!'):
            inner = condition[1:].strip()
            inner_z3 = self._parse_condition_to_z3(inner, state)
            if inner_z3 is not None:
                return z3.Not(inner_z3)

        # Can't parse
        return None

    def _parse_expression_to_z3(self, expr: str, state: SymbolicState) -> Optional[z3.ExprRef]:
        """Parse a Solidity expression into Z3"""

        # Integer literal
        if expr.isdigit():
            return z3.BitVecVal(int(expr), 256)

        # Variable reference
        if expr in state.variables:
            return state.variables[expr].z3_var

        # msg.sender, msg.value, etc.
        if expr.startswith('msg.'):
            # Create symbolic variable for msg properties
            var_name = expr.replace('.', '_')
            if var_name not in state.variables:
                z3_var = z3.BitVec(var_name, 256)
                state.variables[var_name] = SymbolicVariable(
                    name=var_name,
                    sym_type=SymbolicType.UINT256,
                    z3_var=z3_var,
                    is_tainted=True
                )
            return state.variables[var_name].z3_var

        # Can't parse
        return None

    def _is_path_feasible(self, state: SymbolicState) -> bool:
        """
        Check if execution path is feasible using Z3

        DAY 2: Constraint solving for path feasibility
        Returns True if there exists a satisfying assignment
        """
        if len(state.constraints) == 0:
            return True

        solver = z3.Solver()

        # Add all path constraints
        for constraint in state.constraints:
            solver.add(constraint.z3_constraint)

        # Check satisfiability
        result = solver.check()
        return result == z3.sat

    def _check_path_feasibility(
        self,
        state: SymbolicState,
        line_number: int,
        func_name: str,
        file_path: str
    ):
        """
        Check if current path is feasible

        If not, report unreachable code
        """
        if not self._is_path_feasible(state):
            # This path is unreachable!
            constraint_desc = ", ".join([c.condition for c in state.constraints[-3:]])

            self.vulnerabilities.append(SymbolicVulnerability(
                vulnerability_type="unreachable_code",
                severity="info",
                title=f"Unreachable Code Detected in {func_name}",
                description=(
                    f"Code at line {line_number} is unreachable due to "
                    f"contradicting path constraints: {constraint_desc}"
                ),
                line_number=line_number,
                function_name=func_name,
                proof=f"Path constraints are unsatisfiable",
                confidence=90
            ))

    def _analyze_requirement(
        self,
        line: str,
        line_number: int,
        state: SymbolicState,
        func_name: str
    ):
        """
        Analyze require/assert statements

        DAY 2: Extract constraints from require/assert
        These become path constraints for subsequent code
        """

        # Extract condition from require/assert
        req_match = re.search(r'(require|assert)\s*\(([^)]+)\)', line)
        if not req_match:
            return

        condition_str = req_match.group(2).strip()

        # Remove error message if present
        if ',' in condition_str:
            condition_str = condition_str.split(',')[0].strip()

        # Parse to Z3
        z3_constraint = self._parse_condition_to_z3(condition_str, state)

        if z3_constraint is not None:
            # Add as path constraint
            constraint = PathConstraint(
                condition=condition_str,
                z3_constraint=z3_constraint,
                line_number=line_number,
                is_true_branch=True
            )
            state.constraints.append(constraint)

            # Check if this requirement is always true
            solver = z3.Solver()
            solver.add(z3.Not(z3_constraint))  # Can it be false?

            if solver.check() == z3.unsat:
                # Requirement is always satisfied (redundant)
                self.vulnerabilities.append(SymbolicVulnerability(
                    vulnerability_type="redundant_check",
                    severity="info",
                    title=f"Redundant Check in {func_name}",
                    description=(
                        f"The requirement `{condition_str}` at line {line_number} "
                        f"is always true and can be removed."
                    ),
                    line_number=line_number,
                    function_name=func_name,
                    proof=f"Z3 proved condition is always satisfied",
                    confidence=85
                ))

    def _analyze_arithmetic(
        self,
        line: str,
        line_number: int,
        state: SymbolicState,
        func_name: str,
        file_path: str
    ):
        """
        Analyze arithmetic operations for overflow/underflow

        Detects patterns like:
        - balance += amount
        - total = a + b
        - result = value - 1
        """

        # Pattern: variable += expr
        add_assign_match = re.search(r'(\w+)\s*\+=\s*(.+?)[;\s]', line)
        if add_assign_match:
            var_name = add_assign_match.group(1)
            expr = add_assign_match.group(2).strip()

            # Check if unchecked block
            is_unchecked = 'unchecked' in line or any('unchecked' in bl for bl in state.execution_path[-5:] if isinstance(bl, str))

            if not is_unchecked:
                # Check for potential overflow
                self._check_overflow_addition(var_name, expr, line_number, state, func_name, file_path)

        # Pattern: variable = a + b
        add_match = re.search(r'(\w+)\s*=\s*(.+?)\s*\+\s*(.+?)[;\s]', line)
        if add_match:
            result_var = add_match.group(1)
            left_operand = add_match.group(2).strip()
            right_operand = add_match.group(3).strip()

            is_unchecked = 'unchecked' in line
            if not is_unchecked:
                self._check_overflow_addition_expr(
                    result_var, left_operand, right_operand,
                    line_number, state, func_name, file_path
                )

        # Pattern: variable -= expr (underflow)
        sub_assign_match = re.search(r'(\w+)\s*-=\s*(.+?)[;\s]', line)
        if sub_assign_match:
            var_name = sub_assign_match.group(1)
            expr = sub_assign_match.group(2).strip()

            is_unchecked = 'unchecked' in line
            if not is_unchecked:
                self._check_underflow_subtraction(var_name, expr, line_number, state, func_name, file_path)

    def _check_overflow_addition(
        self,
        var_name: str,
        expr: str,
        line_number: int,
        state: SymbolicState,
        func_name: str,
        file_path: str
    ):
        """
        Check if addition can overflow using Z3

        Creates constraint: var + expr > MAX_UINT256
        If satisfiable, overflow is possible
        """

        # Create Z3 variables
        var_z3 = z3.BitVec(f"{var_name}_before", 256)
        expr_z3 = z3.BitVec(f"{expr}_value", 256)
        result_z3 = var_z3 + expr_z3

        # Check if overflow possible: result < var (unsigned overflow wraps)
        overflow_constraint = z3.ULT(result_z3, var_z3)

        # Try to find a model where overflow occurs
        solver = z3.Solver()
        solver.add(overflow_constraint)

        if solver.check() == z3.sat:
            model = solver.model()

            # Extract example values
            var_value = model.eval(var_z3, model_completion=True)
            expr_value = model.eval(expr_z3, model_completion=True)

            proof = f"Overflow possible: {var_name} = {var_value}, {expr} = {expr_value}"

            self.vulnerabilities.append(SymbolicVulnerability(
                vulnerability_type="integer_overflow",
                severity="high",
                title=f"Integer Overflow in {func_name}",
                description=(
                    f"Arithmetic operation `{var_name} += {expr}` at line {line_number} "
                    f"can overflow. This can lead to incorrect balances or unauthorized access."
                ),
                line_number=line_number,
                function_name=func_name,
                proof=proof,
                confidence=90
            ))

    def _check_overflow_addition_expr(
        self,
        result_var: str,
        left: str,
        right: str,
        line_number: int,
        state: SymbolicState,
        func_name: str,
        file_path: str
    ):
        """Check if a + b can overflow"""

        left_z3 = z3.BitVec(f"{left}_value", 256)
        right_z3 = z3.BitVec(f"{right}_value", 256)
        result_z3 = left_z3 + right_z3

        # Overflow check: result < left OR result < right
        overflow_constraint = z3.Or(
            z3.ULT(result_z3, left_z3),
            z3.ULT(result_z3, right_z3)
        )

        solver = z3.Solver()
        solver.add(overflow_constraint)

        if solver.check() == z3.sat:
            model = solver.model()
            left_value = model.eval(left_z3, model_completion=True)
            right_value = model.eval(right_z3, model_completion=True)

            proof = f"Overflow: {left} = {left_value}, {right} = {right_value}"

            self.vulnerabilities.append(SymbolicVulnerability(
                vulnerability_type="integer_overflow",
                severity="medium",
                title=f"Potential Integer Overflow in {func_name}",
                description=(
                    f"Addition `{result_var} = {left} + {right}` at line {line_number} "
                    f"can overflow without `unchecked` block or overflow protection."
                ),
                line_number=line_number,
                function_name=func_name,
                proof=proof,
                confidence=85
            ))

    def _check_underflow_subtraction(
        self,
        var_name: str,
        expr: str,
        line_number: int,
        state: SymbolicState,
        func_name: str,
        file_path: str
    ):
        """Check if subtraction can underflow"""

        var_z3 = z3.BitVec(f"{var_name}_before", 256)
        expr_z3 = z3.BitVec(f"{expr}_value", 256)

        # Underflow: var < expr (for unsigned)
        underflow_constraint = z3.ULT(var_z3, expr_z3)

        solver = z3.Solver()
        solver.add(underflow_constraint)

        if solver.check() == z3.sat:
            model = solver.model()
            var_value = model.eval(var_z3, model_completion=True)
            expr_value = model.eval(expr_z3, model_completion=True)

            proof = f"Underflow: {var_name} = {var_value}, {expr} = {expr_value}"

            self.vulnerabilities.append(SymbolicVulnerability(
                vulnerability_type="integer_underflow",
                severity="high",
                title=f"Integer Underflow in {func_name}",
                description=(
                    f"Subtraction `{var_name} -= {expr}` at line {line_number} "
                    f"can underflow, wrapping to MAX_UINT256."
                ),
                line_number=line_number,
                function_name=func_name,
                proof=proof,
                confidence=90
            ))

    def _analyze_division(
        self,
        line: str,
        line_number: int,
        state: SymbolicState,
        func_name: str,
        file_path: str
    ):
        """Detect potential division by zero"""

        # Pattern: variable = a / b
        div_match = re.search(r'(\w+)\s*=\s*(.+?)\s*/\s*(.+?)[;\s]', line)
        if not div_match:
            return

        result_var = div_match.group(1)
        numerator = div_match.group(2).strip()
        denominator = div_match.group(3).strip()

        # Check if denominator can be zero
        if denominator.isdigit() and int(denominator) != 0:
            # Constant non-zero, safe
            return

        # Check if there's a require statement protecting against zero
        # This is a simplified check
        if f"require({denominator} > 0" in line or f"require({denominator} != 0" in line:
            return

        # Potential division by zero
        self.vulnerabilities.append(SymbolicVulnerability(
            vulnerability_type="division_by_zero",
            severity="medium",
            title=f"Potential Division by Zero in {func_name}",
            description=(
                f"Division operation `{result_var} = {numerator} / {denominator}` at line {line_number} "
                f"does not check if denominator is zero. This will cause transaction revert."
            ),
            line_number=line_number,
            function_name=func_name,
            proof=f"Denominator '{denominator}' not validated before division",
            confidence=75
        ))

    def _analyze_taint_flow(
        self,
        line: str,
        line_number: int,
        state: SymbolicState,
        func_name: str,
        file_path: str
    ):
        """
        Track tainted data flow from user inputs

        Simplified implementation for Day 1
        """

        # Check for external calls with tainted data
        call_match = re.search(r'\.call\s*\{', line)
        if call_match:
            # Check if any parameters are tainted
            # This is a simplified check
            for var_name, var in state.variables.items():
                if var.is_tainted and var_name in line:
                    self.vulnerabilities.append(SymbolicVulnerability(
                        vulnerability_type="tainted_call",
                        severity="high",
                        title=f"Tainted Data in External Call in {func_name}",
                        description=(
                            f"External call at line {line_number} uses tainted user input '{var_name}'. "
                            f"This can lead to arbitrary external calls or reentrancy."
                        ),
                        line_number=line_number,
                        function_name=func_name,
                        proof=f"Tainted variable '{var_name}' flows to external call",
                        confidence=80
                    ))
                    break

    def _convert_to_standard_format(self, file_path: str) -> List[SolidityVulnerability]:
        """
        Convert SymbolicVulnerability to standard SolidityVulnerability format
        for integration with Week 2 economic impact calculator
        """
        standard_vulns = []

        for vuln in self.vulnerabilities:
            # Map vulnerability types
            vuln_type_map = {
                "integer_overflow": VulnerabilityType.INTEGER_OVERFLOW_UNDERFLOW,
                "integer_underflow": VulnerabilityType.INTEGER_OVERFLOW_UNDERFLOW,
                "division_by_zero": VulnerabilityType.LOGIC_ERROR,
                "tainted_call": VulnerabilityType.UNCHECKED_LOW_LEVEL_CALL,
            }

            vuln_type = vuln_type_map.get(vuln.vulnerability_type, VulnerabilityType.LOGIC_ERROR)

            # Create remediation advice
            remediation = self._get_remediation(vuln.vulnerability_type)

            # Create code snippet with proof
            code_snippet = vuln.proof if vuln.proof else "See line number for details"

            standard_vuln = SolidityVulnerability(
                vulnerability_type=vuln_type,
                severity=vuln.severity,
                title=f"[Symbolic Execution] {vuln.title}",
                description=vuln.description,
                file_path=file_path,
                line_number=vuln.line_number,
                function_name=vuln.function_name,
                contract_name="unknown",
                code_snippet=code_snippet,
                remediation=remediation,
                confidence=vuln.confidence
            )

            standard_vulns.append(standard_vuln)

        return standard_vulns

    def _get_remediation(self, vuln_type: str) -> str:
        """Get remediation advice for vulnerability type"""
        remediation_map = {
            "integer_overflow": (
                "Use Solidity 0.8+ which has built-in overflow protection, "
                "or wrap arithmetic in `unchecked {}` only when overflow is intended. "
                "Consider using SafeMath library for Solidity <0.8."
            ),
            "integer_underflow": (
                "Use Solidity 0.8+ with built-in underflow protection. "
                "Add `require()` checks before subtraction to ensure sufficient balance."
            ),
            "division_by_zero": (
                "Add `require(denominator > 0, \"Division by zero\")` before division operations."
            ),
            "tainted_call": (
                "Validate and sanitize all user inputs before use in external calls. "
                "Consider using a whitelist of allowed call targets."
            ),
        }

        return remediation_map.get(vuln_type, "Review and validate the operation carefully.")


# Example usage and testing
if __name__ == "__main__":
    executor = SymbolicExecutor()

    # Test case: Simple overflow
    test_contract = """
    contract TestContract {
        uint256 public totalSupply;

        function mint(uint256 amount) external {
            totalSupply += amount;  // Can overflow!
        }

        function burn(uint256 amount) external {
            totalSupply -= amount;  // Can underflow!
        }

        function divide(uint256 a, uint256 b) external returns (uint256) {
            return a / b;  // Division by zero!
        }
    }
    """

    vulns = executor.analyze_contract(test_contract, "test.sol")

    print(f"Found {len(vulns)} vulnerabilities:")
    for vuln in vulns:
        print(f"\n{vuln.severity.upper()}: {vuln.title}")
        print(f"Line {vuln.line_number}: {vuln.description}")
        if vuln.code_snippet:
            print(f"Proof: {vuln.code_snippet}")
