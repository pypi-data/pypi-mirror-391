"""
MEV (Miner Extractable Value) Detection Engine

WEEK 3 DAY 3: MEV Detection
============================

Detects vulnerabilities that allow miners/validators to extract value by:
- Front-running transactions
- Sandwich attacks on DEX swaps
- Liquidation manipulation
- Timestamp manipulation

Background:
- 2024 MEV Stats: $500M+ extracted, $100M+ from malicious MEV
- Common attack vectors: DEX arbitrage, liquidations, oracle updates

Author: Alprina Development Team
Date: 2025-11-12

References:
- Flashbots: MEV research and data
- MEV-Explore: Historical MEV extraction data
- DAIAN et al.: "Flash Boys 2.0" (2019)
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    from .solidity_analyzer import SolidityVulnerability, VulnerabilityType
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from solidity_analyzer import SolidityVulnerability, VulnerabilityType


class MEVType(Enum):
    """Types of MEV vulnerabilities"""
    FRONTRUNNING = "frontrunning"
    SANDWICH_ATTACK = "sandwich_attack"
    LIQUIDATION_MEV = "liquidation_mev"
    TIMESTAMP_MANIPULATION = "timestamp_manipulation"
    ORACLE_MEV = "oracle_mev"


@dataclass
class MEVVulnerability:
    """MEV vulnerability with profit estimation"""
    mev_type: MEVType
    severity: str
    title: str
    description: str
    line_number: int
    function_name: str
    estimated_mev_profit: Tuple[float, float]  # Min, max profit in USD
    user_loss_per_tx: Tuple[float, float]  # Min, max loss per transaction
    attack_complexity: str  # "low", "medium", "high"
    time_to_exploit: str  # "immediate", "hours", "days"
    historical_examples: List[str]
    confidence: int = 90


class MEVDetector:
    """
    Detect MEV vulnerabilities in smart contracts

    Week 3 Day 3 Implementation:
    1. Front-running detection (oracle updates, approvals, etc.)
    2. Sandwich attack detection (DEX swaps without slippage)
    3. Liquidation MEV detection (public liquidations)
    4. Timestamp manipulation detection

    MEV Categories:
    - Front-running: $200M+ in 2024
    - Sandwich attacks: $150M+ in 2024
    - Liquidation MEV: $100M+ in 2024
    """

    def __init__(self):
        self.vulnerabilities: List[MEVVulnerability] = []

        # Historical MEV data for context
        self.mev_historical = {
            "frontrunning": {
                "examples": [
                    "Bancor front-running (2020): $500K+",
                    "Uniswap V2 front-runs (2021): $2M+",
                    "NFT mint front-runs (2021-2022): $10M+"
                ],
                "avg_profit_per_tx": (100, 5000),
                "total_2024": 200_000_000
            },
            "sandwich": {
                "examples": [
                    "jaredfromsubway.eth: $40M+ (2023-2024)",
                    "MEV bot 0x000: $20M+ (2024)",
                    "Various sandwich bots: $100M+ (2024)"
                ],
                "avg_profit_per_tx": (50, 2000),
                "total_2024": 150_000_000
            },
            "liquidation": {
                "examples": [
                    "Aave liquidations: $50M+ MEV (2024)",
                    "Compound liquidations: $30M+ MEV (2024)",
                    "MakerDAO liquidations: $20M+ MEV (2024)"
                ],
                "avg_profit_per_tx": (500, 50000),
                "total_2024": 100_000_000
            }
        }

    def analyze_contract(self, contract_code: str, file_path: str) -> List[SolidityVulnerability]:
        """
        Analyze contract for MEV vulnerabilities

        Returns standard SolidityVulnerability objects for integration
        """
        self.vulnerabilities = []

        # Extract functions
        functions = self._extract_functions(contract_code)

        for func in functions:
            # Detect front-running vulnerabilities
            self._detect_frontrunning(func, contract_code)

            # Detect sandwich attack vulnerabilities
            self._detect_sandwich_attacks(func, contract_code)

            # Detect liquidation MEV
            self._detect_liquidation_mev(func, contract_code)

            # Detect timestamp manipulation
            self._detect_timestamp_manipulation(func, contract_code)

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

    def _detect_frontrunning(self, func: Dict[str, Any], contract_code: str):
        """
        Detect front-running vulnerabilities

        Patterns:
        1. Oracle price update + immediate use
        2. Approval + transferFrom in same tx
        3. Public state changes used in price calculations
        4. Order placement without commitment scheme
        """
        func_name = func['name']
        body = func['body']
        start_line = func['start_line']

        # Pattern 1: Oracle update + price usage
        if self._has_oracle_update_and_use(body):
            self.vulnerabilities.append(MEVVulnerability(
                mev_type=MEVType.FRONTRUNNING,
                severity="critical",
                title=f"Front-Running: Oracle Price Update in {func_name}",
                description=(
                    f"Function {func_name} updates oracle price and immediately uses it. "
                    f"Attackers can front-run this transaction to profit from the price change."
                ),
                line_number=start_line,
                function_name=func_name,
                estimated_mev_profit=(10_000, 100_000),
                user_loss_per_tx=(1_000, 50_000),
                attack_complexity="low",
                time_to_exploit="immediate",
                historical_examples=self.mev_historical["frontrunning"]["examples"],
                confidence=95
            ))

        # Pattern 2: Approval pattern (approve + action)
        if 'approve(' in body and ('transfer' in body or 'swap' in body):
            self.vulnerabilities.append(MEVVulnerability(
                mev_type=MEVType.FRONTRUNNING,
                severity="high",
                title=f"Front-Running: Approval Pattern in {func_name}",
                description=(
                    f"Function {func_name} contains approval followed by action. "
                    f"Attackers can front-run the approval to gain advantage."
                ),
                line_number=start_line,
                function_name=func_name,
                estimated_mev_profit=(100, 5_000),
                user_loss_per_tx=(50, 1_000),
                attack_complexity="medium",
                time_to_exploit="immediate",
                historical_examples=["ERC20 approval races: $5M+ (2020-2024)"],
                confidence=85
            ))

        # Pattern 3: Public state change affecting price
        if self._has_price_affecting_public_change(body, func):
            self.vulnerabilities.append(MEVVulnerability(
                mev_type=MEVType.FRONTRUNNING,
                severity="high",
                title=f"Front-Running: Public Price-Affecting Change in {func_name}",
                description=(
                    f"Function {func_name} makes public state changes that affect prices. "
                    f"MEV bots can front-run to profit from predictable price impact."
                ),
                line_number=start_line,
                function_name=func_name,
                estimated_mev_profit=(1_000, 50_000),
                user_loss_per_tx=(500, 10_000),
                attack_complexity="medium",
                time_to_exploit="immediate",
                historical_examples=["DEX arbitrage front-runs: $200M+ (2024)"],
                confidence=80
            ))

    def _detect_sandwich_attacks(self, func: Dict[str, Any], contract_code: str):
        """
        Detect sandwich attack vulnerabilities

        Patterns:
        1. Swap without slippage protection
        2. Missing deadline parameter
        3. Predictable swap routing
        4. Large swap without price impact protection
        """
        func_name = func['name']
        body = func['body']
        start_line = func['start_line']

        # Pattern 1: Swap without slippage protection
        has_swap = any(keyword in body.lower() for keyword in ['swap', 'exchange', 'trade'])

        if has_swap:
            has_slippage = any(keyword in body.lower() for keyword in [
                'minamount', 'min_amount', 'slippage', 'amountoutmin'
            ])

            if not has_slippage:
                self.vulnerabilities.append(MEVVulnerability(
                    mev_type=MEVType.SANDWICH_ATTACK,
                    severity="critical",
                    title=f"Sandwich Attack: No Slippage Protection in {func_name}",
                    description=(
                        f"Function {func_name} performs swap without slippage protection. "
                        f"MEV bots can sandwich attack: buy before (front-run), "
                        f"user swap at worse price, sell after (back-run) for profit."
                    ),
                    line_number=start_line,
                    function_name=func_name,
                    estimated_mev_profit=(50, 5_000),
                    user_loss_per_tx=(25, 2_000),
                    attack_complexity="low",
                    time_to_exploit="immediate",
                    historical_examples=self.mev_historical["sandwich"]["examples"],
                    confidence=95
                ))

        # Pattern 2: Missing deadline protection
        if has_swap:
            has_deadline = 'deadline' in body.lower()

            if not has_deadline:
                self.vulnerabilities.append(MEVVulnerability(
                    mev_type=MEVType.SANDWICH_ATTACK,
                    severity="high",
                    title=f"Sandwich Attack: Missing Deadline in {func_name}",
                    description=(
                        f"Function {func_name} performs swap without deadline parameter. "
                        f"Transaction can be held in mempool and executed at worst price."
                    ),
                    line_number=start_line,
                    function_name=func_name,
                    estimated_mev_profit=(100, 10_000),
                    user_loss_per_tx=(50, 5_000),
                    attack_complexity="low",
                    time_to_exploit="immediate",
                    historical_examples=["Delayed execution attacks: $10M+ (2023-2024)"],
                    confidence=90
                ))

        # Pattern 3: getAmountsOut without TWAP (spot price vulnerability)
        if 'getamountsout' in body.lower() or 'getamountout' in body.lower():
            has_twap = 'twap' in body.lower() or 'observe' in body.lower()

            if not has_twap:
                self.vulnerabilities.append(MEVVulnerability(
                    mev_type=MEVType.SANDWICH_ATTACK,
                    severity="critical",
                    title=f"Sandwich Attack: Spot Price Usage in {func_name}",
                    description=(
                        f"Function {func_name} uses spot price (getAmountsOut) without TWAP. "
                        f"Highly vulnerable to sandwich attacks and price manipulation."
                    ),
                    line_number=start_line,
                    function_name=func_name,
                    estimated_mev_profit=(1_000, 50_000),
                    user_loss_per_tx=(500, 20_000),
                    attack_complexity="low",
                    time_to_exploit="immediate",
                    historical_examples=["Spot price manipulation: $100M+ (2024)"],
                    confidence=95
                ))

    def _detect_liquidation_mev(self, func: Dict[str, Any], contract_code: str):
        """
        Detect liquidation MEV vulnerabilities

        Patterns:
        1. Public liquidation function without priority queue
        2. Missing liquidation delay
        3. First-come-first-serve liquidation rewards
        4. Full liquidation without gradual approach
        """
        func_name = func['name']
        body = func['body']
        start_line = func['start_line']
        visibility = func['visibility']

        # Pattern 1: Public liquidation function
        is_liquidation = 'liquidat' in func_name.lower() or 'liquidat' in body.lower()

        if is_liquidation and visibility in ['public', 'external']:
            has_priority = any(keyword in body.lower() for keyword in [
                'priority', 'queue', 'delay', 'timelock'
            ])

            if not has_priority:
                self.vulnerabilities.append(MEVVulnerability(
                    mev_type=MEVType.LIQUIDATION_MEV,
                    severity="high",
                    title=f"Liquidation MEV: No Priority Protection in {func_name}",
                    description=(
                        f"Function {func_name} allows public liquidation without priority mechanism. "
                        f"MEV bots with better infrastructure will always win liquidations, "
                        f"extracting maximum value."
                    ),
                    line_number=start_line,
                    function_name=func_name,
                    estimated_mev_profit=(500, 100_000),
                    user_loss_per_tx=(0, 10_000),  # Borrower loss
                    attack_complexity="medium",
                    time_to_exploit="hours",
                    historical_examples=self.mev_historical["liquidation"]["examples"],
                    confidence=90
                ))

        # Pattern 2: Full liquidation (100% at once)
        if is_liquidation:
            has_partial = any(keyword in body.lower() for keyword in [
                'partial', 'percentage', 'ratio', 'closefactor'
            ])

            if not has_partial:
                self.vulnerabilities.append(MEVVulnerability(
                    mev_type=MEVType.LIQUIDATION_MEV,
                    severity="medium",
                    title=f"Liquidation MEV: Full Liquidation in {func_name}",
                    description=(
                        f"Function {func_name} allows full (100%) liquidation. "
                        f"This incentivizes MEV bots to race for maximum profit, "
                        f"potentially causing unfair borrower losses."
                    ),
                    line_number=start_line,
                    function_name=func_name,
                    estimated_mev_profit=(1_000, 50_000),
                    user_loss_per_tx=(500, 20_000),
                    attack_complexity="low",
                    time_to_exploit="hours",
                    historical_examples=["Full liquidation races: $50M+ (2024)"],
                    confidence=80
                ))

    def _detect_timestamp_manipulation(self, func: Dict[str, Any], contract_code: str):
        """
        Detect timestamp manipulation vulnerabilities

        Patterns:
        1. block.timestamp used in critical logic
        2. Randomness based on timestamp
        3. Time-based rewards without protection
        """
        func_name = func['name']
        body = func['body']
        start_line = func['start_line']

        # Pattern 1: block.timestamp in conditional
        if 'block.timestamp' in body:
            # Check if used in critical operations
            has_critical_use = any(keyword in body.lower() for keyword in [
                'reward', 'mint', 'claim', 'unlock', 'vesting'
            ])

            if has_critical_use:
                self.vulnerabilities.append(MEVVulnerability(
                    mev_type=MEVType.TIMESTAMP_MANIPULATION,
                    severity="medium",
                    title=f"Timestamp Manipulation: Critical Use in {func_name}",
                    description=(
                        f"Function {func_name} uses block.timestamp in critical logic. "
                        f"Miners can manipulate timestamp by ~15 seconds, "
                        f"potentially affecting rewards or access control."
                    ),
                    line_number=start_line,
                    function_name=func_name,
                    estimated_mev_profit=(100, 10_000),
                    user_loss_per_tx=(0, 5_000),
                    attack_complexity="high",
                    time_to_exploit="hours",
                    historical_examples=["Timestamp manipulation: $5M+ (2020-2024)"],
                    confidence=75
                ))

        # Pattern 2: Randomness from timestamp
        if 'block.timestamp' in body and any(keyword in body.lower() for keyword in [
            'random', 'seed', 'keccak', 'hash'
        ]):
            self.vulnerabilities.append(MEVVulnerability(
                mev_type=MEVType.TIMESTAMP_MANIPULATION,
                severity="high",
                title=f"Timestamp Manipulation: Weak Randomness in {func_name}",
                description=(
                    f"Function {func_name} uses block.timestamp for randomness. "
                    f"Miners can manipulate this to predict or influence outcomes."
                ),
                line_number=start_line,
                function_name=func_name,
                estimated_mev_profit=(1_000, 100_000),
                user_loss_per_tx=(500, 50_000),
                attack_complexity="medium",
                time_to_exploit="immediate",
                historical_examples=["Weak randomness exploits: $20M+ (2020-2024)"],
                confidence=90
            ))

    def _has_oracle_update_and_use(self, body: str) -> bool:
        """Check if function updates oracle and uses price"""
        has_update = any(keyword in body.lower() for keyword in [
            'updateprice', 'setprice', 'oracle.update', 'pricefeed.update'
        ])

        has_use = any(keyword in body.lower() for keyword in [
            'getprice', 'price()', 'swap', 'trade', 'exchange'
        ])

        return has_update and has_use

    def _has_price_affecting_public_change(self, body: str, func: Dict[str, Any]) -> bool:
        """Check if public function affects prices"""
        is_public = func['visibility'] in ['public', 'external']

        affects_price = any(keyword in body.lower() for keyword in [
            'reserves', 'liquidity', 'balance', 'supply', 'mint', 'burn'
        ])

        return is_public and affects_price

    def _convert_to_standard_format(self, file_path: str) -> List[SolidityVulnerability]:
        """Convert MEV vulnerabilities to standard format"""
        standard_vulns = []

        for vuln in self.vulnerabilities:
            # Map MEV types to standard vulnerability types
            vuln_type_map = {
                MEVType.FRONTRUNNING: VulnerabilityType.LOGIC_ERROR,
                MEVType.SANDWICH_ATTACK: VulnerabilityType.ORACLE_MANIPULATION,
                MEVType.LIQUIDATION_MEV: VulnerabilityType.ACCESS_CONTROL,
                MEVType.TIMESTAMP_MANIPULATION: VulnerabilityType.TIMESTAMP_DEPENDENCE,
                MEVType.ORACLE_MEV: VulnerabilityType.ORACLE_MANIPULATION,
            }

            vuln_type = vuln_type_map.get(vuln.mev_type, VulnerabilityType.LOGIC_ERROR)

            # Create code snippet with MEV details
            mev_details = (
                f"MEV Profit Potential: ${vuln.estimated_mev_profit[0]:,} - ${vuln.estimated_mev_profit[1]:,}\n"
                f"User Loss Per TX: ${vuln.user_loss_per_tx[0]:,} - ${vuln.user_loss_per_tx[1]:,}\n"
                f"Attack Complexity: {vuln.attack_complexity}\n"
                f"Time to Exploit: {vuln.time_to_exploit}\n"
                f"Historical Examples: {', '.join(vuln.historical_examples[:2])}"
            )

            # Create remediation advice
            remediation = self._get_remediation(vuln.mev_type)

            standard_vuln = SolidityVulnerability(
                vulnerability_type=vuln_type,
                severity=vuln.severity,
                title=f"[MEV] {vuln.title}",
                description=vuln.description,
                file_path=file_path,
                line_number=vuln.line_number,
                function_name=vuln.function_name,
                contract_name="unknown",
                code_snippet=mev_details,
                remediation=remediation,
                confidence=vuln.confidence
            )

            standard_vulns.append(standard_vuln)

        return standard_vulns

    def _get_remediation(self, mev_type: MEVType) -> str:
        """Get remediation advice for MEV vulnerability"""
        remediation_map = {
            MEVType.FRONTRUNNING: (
                "Use commit-reveal schemes or time-locks for sensitive operations. "
                "Consider using private mempools (e.g., Flashbots Protect) or "
                "submarine sends to hide transactions from front-runners."
            ),
            MEVType.SANDWICH_ATTACK: (
                "Add slippage protection with amountOutMin parameter. "
                "Include deadline parameter to prevent delayed execution. "
                "Use TWAP (Time-Weighted Average Price) instead of spot prices. "
                "Consider using MEV-aware DEX designs (e.g., CoWSwap, 1inch Fusion)."
            ),
            MEVType.LIQUIDATION_MEV: (
                "Implement liquidation priority queue or Dutch auction mechanism. "
                "Use partial liquidations with close factor < 100%. "
                "Add liquidation delay to allow borrowers to self-liquidate. "
                "Consider keeper-based liquidation systems."
            ),
            MEVType.TIMESTAMP_MANIPULATION: (
                "Avoid using block.timestamp for critical logic. "
                "Use block.number with estimated block times for time-based logic. "
                "Never use block.timestamp for randomness (use Chainlink VRF instead)."
            ),
            MEVType.ORACLE_MEV: (
                "Separate oracle updates from price usage across transactions. "
                "Use commit-reveal for oracle updates. "
                "Implement TWAP or median prices to prevent manipulation."
            )
        }

        return remediation_map.get(mev_type, "Review MEV implications carefully.")


# Example usage and testing
if __name__ == "__main__":
    detector = MEVDetector()

    # Test case: DEX with multiple MEV vulnerabilities
    test_contract = """
    contract VulnerableDEX {
        IUniswapV2Router router;
        IPriceOracle oracle;

        // VULNERABLE: Oracle update + immediate use (front-running)
        function updateAndSwap(uint256 amountIn) external {
            oracle.updatePrice();
            uint256 price = oracle.getPrice();
            _swap(amountIn, price);
        }

        // VULNERABLE: Swap without slippage protection (sandwich attack)
        function swapTokens(uint256 amountIn) external {
            address[] memory path = new address[](2);
            path[0] = address(tokenA);
            path[1] = address(tokenB);

            router.swapExactTokensForTokens(
                amountIn,
                0,  // NO SLIPPAGE PROTECTION!
                path,
                msg.sender,
                block.timestamp + 3600
            );
        }

        // VULNERABLE: Public liquidation without priority (liquidation MEV)
        function liquidate(address user) external {
            require(isLiquidatable(user), "Not liquidatable");

            uint256 debt = getDebt(user);
            _liquidate(user, debt);  // Full liquidation, MEV race!
        }

        // VULNERABLE: Timestamp used for rewards (timestamp manipulation)
        function claimRewards() external {
            uint256 timeElapsed = block.timestamp - lastClaim[msg.sender];
            uint256 reward = timeElapsed * rewardRate;

            _mint(msg.sender, reward);
        }
    }
    """

    vulns = detector.analyze_contract(test_contract, "test.sol")

    print(f"Found {len(vulns)} MEV vulnerabilities:\n")
    for vuln in vulns:
        print(f"{vuln.severity.upper()}: {vuln.title}")
        print(f"  {vuln.description}")
        print(f"  {vuln.code_snippet}")
        print()
