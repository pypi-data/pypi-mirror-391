"""
Economic Impact Calculator for Smart Contract Vulnerabilities

WEEK 2 DAY 3: Quantifies potential financial losses from detected vulnerabilities
Based on OWASP Risk Rating + DeFi TVL analysis + 2024 exploit data

Methodology:
- Risk = Likelihood × Impact × Exploitability
- TVL-adjusted loss estimates
- Historical exploit data (2024: $730M in losses)
- Severity-based impact multipliers
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re


class ImpactCategory(Enum):
    """Financial impact categories based on OWASP + DeFi standards"""
    CATASTROPHIC = "catastrophic"  # Complete protocol loss (>$10M or >80% TVL)
    CRITICAL = "critical"           # Major loss ($1M-$10M or 50-80% TVL)
    HIGH = "high"                   # Significant loss ($100K-$1M or 20-50% TVL)
    MEDIUM = "medium"               # Moderate loss ($10K-$100K or 5-20% TVL)
    LOW = "low"                     # Minor loss (<$10K or <5% TVL)


@dataclass
class EconomicImpact:
    """Quantified economic impact assessment"""
    vulnerability_type: str
    severity: str
    impact_category: ImpactCategory
    estimated_loss_usd: Tuple[int, int]  # (min, max) range
    estimated_loss_percentage: Tuple[float, float]  # (min, max) % of TVL
    likelihood_score: float  # 0.0-1.0
    exploitability_score: float  # 0.0-1.0
    risk_score: float  # 0-100 (combined)
    time_to_exploit: str  # "immediate", "hours", "days", "weeks"
    attack_complexity: str  # "low", "medium", "high"
    historical_precedent: Optional[str]  # Reference to real exploit
    remediation_cost: str  # Estimated developer hours
    confidence: int  # 0-100


class EconomicImpactCalculator:
    """
    Calculate financial impact of smart contract vulnerabilities

    WEEK 2 DAY 3: Economic Impact Assessment

    Features:
    - TVL-based loss estimation
    - Severity-impact mapping (OWASP methodology)
    - Historical exploit data integration
    - Attack complexity analysis
    - Time-to-exploit assessment
    """

    def __init__(self):
        # 2024 DeFi statistics
        self.defi_tvl_2024 = 100_000_000_000  # $100B (December 2024)
        self.total_losses_2024 = 730_000_000   # $730M in hacks (2024)

        # Historical exploit data
        self.exploit_database = self._initialize_exploit_database()

        # OWASP-based impact multipliers
        self.severity_multipliers = {
            "critical": 1.0,    # Full impact
            "high": 0.6,        # 60% of full impact
            "medium": 0.3,      # 30% of full impact
            "low": 0.1,         # 10% of full impact
            "info": 0.01        # 1% of full impact
        }

    def calculate_impact(
        self,
        vulnerability_type: str,
        severity: str,
        contract_context: Optional[Dict[str, Any]] = None
    ) -> EconomicImpact:
        """
        Calculate economic impact for a vulnerability

        Args:
            vulnerability_type: Type of vulnerability (e.g., "oracle_manipulation")
            severity: Severity level ("critical", "high", "medium", "low")
            contract_context: Optional context (TVL, protocol type, etc.)

        Returns:
            EconomicImpact assessment with loss estimates
        """
        # Extract contract context
        estimated_tvl = self._estimate_tvl(contract_context)
        protocol_type = self._get_protocol_type(contract_context)

        # Calculate base impact from vulnerability type
        base_impact = self._get_base_impact(vulnerability_type, severity)

        # Calculate likelihood of exploitation
        likelihood = self._calculate_likelihood(vulnerability_type, severity)

        # Calculate exploitability
        exploitability = self._calculate_exploitability(vulnerability_type)

        # Get time-to-exploit and attack complexity
        time_to_exploit = self._get_time_to_exploit(vulnerability_type, severity)
        attack_complexity = self._get_attack_complexity(vulnerability_type)

        # Calculate TVL-adjusted loss range
        loss_usd_range = self._calculate_loss_range(
            base_impact,
            estimated_tvl,
            severity,
            protocol_type
        )

        # Calculate percentage of TVL at risk
        loss_percentage = (
            (loss_usd_range[0] / estimated_tvl * 100) if estimated_tvl > 0 else 0,
            (loss_usd_range[1] / estimated_tvl * 100) if estimated_tvl > 0 else 0
        )

        # Calculate overall risk score (OWASP methodology)
        risk_score = self._calculate_risk_score(
            likelihood,
            base_impact,
            exploitability
        )

        # Determine impact category
        impact_category = self._categorize_impact(loss_usd_range[1], loss_percentage[1])

        # Find historical precedent
        historical_precedent = self._find_historical_exploit(vulnerability_type)

        # Estimate remediation cost
        remediation_cost = self._estimate_remediation_cost(vulnerability_type, severity)

        # Calculate confidence based on data availability
        confidence = self._calculate_confidence(
            vulnerability_type,
            contract_context,
            historical_precedent
        )

        return EconomicImpact(
            vulnerability_type=vulnerability_type,
            severity=severity,
            impact_category=impact_category,
            estimated_loss_usd=loss_usd_range,
            estimated_loss_percentage=loss_percentage,
            likelihood_score=likelihood,
            exploitability_score=exploitability,
            risk_score=risk_score,
            time_to_exploit=time_to_exploit,
            attack_complexity=attack_complexity,
            historical_precedent=historical_precedent,
            remediation_cost=remediation_cost,
            confidence=confidence
        )

    def _estimate_tvl(self, context: Optional[Dict[str, Any]]) -> int:
        """Estimate TVL for the contract"""
        if not context:
            # Default: assume small protocol
            return 1_000_000  # $1M

        # Check if TVL provided
        if 'tvl' in context:
            return int(context['tvl'])

        # Estimate based on protocol type
        protocol_type = context.get('protocol_type', 'unknown')

        tvl_estimates = {
            'dex': 50_000_000,         # $50M (average DEX)
            'lending': 100_000_000,    # $100M (average lending protocol)
            'yield': 20_000_000,       # $20M (average yield aggregator)
            'bridge': 200_000_000,     # $200M (average bridge)
            'staking': 30_000_000,     # $30M (average staking protocol)
            'nft': 5_000_000,          # $5M (average NFT platform)
            'unknown': 1_000_000       # $1M (conservative default)
        }

        return tvl_estimates.get(protocol_type, 1_000_000)

    def _get_protocol_type(self, context: Optional[Dict[str, Any]]) -> str:
        """Determine protocol type from context"""
        if not context:
            return 'unknown'

        return context.get('protocol_type', 'unknown')

    def _get_base_impact(self, vulnerability_type: str, severity: str) -> float:
        """
        Get base impact score (0.0-1.0) for vulnerability type

        Based on 2024 exploit data and OWASP methodology
        """
        # Vulnerability type impact mapping
        impact_map = {
            # Critical vulnerabilities (0.8-1.0)
            'oracle_manipulation': 0.95,      # $70M+ in 2024, 34.3% of exploits
            'flash_loan_attack': 0.90,        # $33.8M in 2024
            'pool_reserve_manipulation': 0.95, # Most common DeFi exploit
            'reentrancy': 0.85,               # $35.7M in 2024

            # High severity (0.6-0.8)
            'access_control': 0.75,           # $953.2M (but often preventable)
            'unchecked_external_call': 0.70,  # $550.7K in 2024
            'input_validation': 0.65,         # $14.6M in 2024

            # Medium severity (0.3-0.6)
            'integer_overflow': 0.50,         # Reduced in Solidity 0.8+
            'timestamp_dependence': 0.40,
            'logic_error': 0.45,              # $63.8M in 2024 (varied)

            # Low severity (0.1-0.3)
            'gas_limit': 0.15,
            'denial_of_service': 0.20,
            'uninitialized_storage': 0.25,
        }

        base = impact_map.get(vulnerability_type, 0.50)  # Default: medium

        # Apply severity multiplier
        multiplier = self.severity_multipliers.get(severity.lower(), 0.50)

        return base * multiplier

    def _calculate_likelihood(self, vulnerability_type: str, severity: str) -> float:
        """
        Calculate likelihood of exploitation (0.0-1.0)

        Based on:
        - Exploit difficulty
        - Public knowledge
        - Attacker motivation (financial gain)
        """
        # Base likelihood by vulnerability type
        likelihood_map = {
            # High likelihood (public, easy to exploit)
            'oracle_manipulation': 0.90,      # Well-known, financially motivated
            'flash_loan_attack': 0.85,        # Common attack vector
            'pool_reserve_manipulation': 0.95, # Easy to exploit
            'unchecked_external_call': 0.80,  # Simple to exploit
            'input_validation': 0.75,         # Common oversight

            # Medium likelihood
            'reentrancy': 0.70,               # Well-known but requires setup
            'access_control': 0.65,           # Depends on configuration
            'logic_error': 0.60,              # Requires analysis

            # Low likelihood
            'integer_overflow': 0.40,         # Mostly fixed in modern Solidity
            'timestamp_dependence': 0.45,
            'gas_limit': 0.30,
            'denial_of_service': 0.35,
        }

        base_likelihood = likelihood_map.get(vulnerability_type, 0.50)

        # Severity adjustment
        severity_adjustments = {
            'critical': 1.0,
            'high': 0.9,
            'medium': 0.7,
            'low': 0.5,
            'info': 0.2
        }

        adjustment = severity_adjustments.get(severity.lower(), 0.7)

        return min(base_likelihood * adjustment, 1.0)

    def _calculate_exploitability(self, vulnerability_type: str) -> float:
        """
        Calculate exploitability score (0.0-1.0)

        Factors:
        - Technical complexity
        - Required resources
        - Automation potential
        """
        exploitability_map = {
            # Easy to exploit (0.8-1.0)
            'pool_reserve_manipulation': 0.95,  # Flash loan, single tx
            'unchecked_external_call': 0.90,    # Simple call, no validation
            'input_validation': 0.85,           # Straightforward parameter manipulation
            'flash_loan_attack': 0.90,          # Well-documented, tools available

            # Moderate (0.5-0.8)
            'oracle_manipulation': 0.75,        # Requires capital or flash loan
            'reentrancy': 0.70,                 # Requires contract creation
            'access_control': 0.65,             # May need specific permissions

            # Complex (0.3-0.5)
            'logic_error': 0.50,                # Varies by specific issue
            'timestamp_dependence': 0.45,       # Limited manipulation window
            'integer_overflow': 0.40,           # Mostly prevented in 0.8+
        }

        return exploitability_map.get(vulnerability_type, 0.60)

    def _calculate_loss_range(
        self,
        base_impact: float,
        tvl: int,
        severity: str,
        protocol_type: str
    ) -> Tuple[int, int]:
        """
        Calculate realistic loss range in USD

        Returns (min_loss, max_loss) tuple
        """
        # Protocol-specific risk factors
        protocol_risk = {
            'dex': 0.60,          # High liquidity drain risk
            'lending': 0.70,      # Flash loan risk
            'bridge': 0.90,       # Full TVL at risk (critical infrastructure)
            'yield': 0.50,        # Moderate risk
            'staking': 0.40,      # Lower risk (withdrawal delays)
            'nft': 0.30,          # Limited per-item value
            'unknown': 0.50       # Default
        }

        risk_factor = protocol_risk.get(protocol_type, 0.50)

        # Calculate maximum potential loss
        max_loss = int(tvl * base_impact * risk_factor)

        # Calculate minimum loss (20-40% of max, depending on severity)
        severity_confidence = {
            'critical': 0.60,  # 60% of max (high confidence)
            'high': 0.40,      # 40% of max
            'medium': 0.25,    # 25% of max
            'low': 0.15,       # 15% of max
            'info': 0.05       # 5% of max
        }

        min_multiplier = severity_confidence.get(severity.lower(), 0.30)
        min_loss = int(max_loss * min_multiplier)

        # Floor values (at least $1K for critical, scale down)
        min_floors = {
            'critical': 10_000,
            'high': 5_000,
            'medium': 1_000,
            'low': 100,
            'info': 10
        }

        floor = min_floors.get(severity.lower(), 1_000)
        min_loss = max(min_loss, floor)
        max_loss = max(max_loss, floor * 2)

        return (min_loss, max_loss)

    def _calculate_risk_score(
        self,
        likelihood: float,
        impact: float,
        exploitability: float
    ) -> float:
        """
        Calculate overall risk score (0-100)

        OWASP Formula: Risk = Likelihood × Impact × Exploitability
        Scaled to 0-100
        """
        risk = likelihood * impact * exploitability * 100
        return min(risk, 100.0)

    def _categorize_impact(
        self,
        max_loss_usd: int,
        max_loss_percentage: float
    ) -> ImpactCategory:
        """Categorize impact based on absolute and relative loss"""
        # Catastrophic: >$10M or >80% TVL
        if max_loss_usd > 10_000_000 or max_loss_percentage > 80:
            return ImpactCategory.CATASTROPHIC

        # Critical: $1M-$10M or 50-80% TVL
        if max_loss_usd > 1_000_000 or max_loss_percentage > 50:
            return ImpactCategory.CRITICAL

        # High: $100K-$1M or 20-50% TVL
        if max_loss_usd > 100_000 or max_loss_percentage > 20:
            return ImpactCategory.HIGH

        # Medium: $10K-$100K or 5-20% TVL
        if max_loss_usd > 10_000 or max_loss_percentage > 5:
            return ImpactCategory.MEDIUM

        # Low: <$10K or <5% TVL
        return ImpactCategory.LOW

    def _get_time_to_exploit(self, vulnerability_type: str, severity: str) -> str:
        """Estimate time required to exploit"""
        # Immediate exploits (flash loan, single transaction)
        immediate = ['flash_loan_attack', 'pool_reserve_manipulation', 'unchecked_external_call']

        # Hours (requires setup, but straightforward)
        hours = ['oracle_manipulation', 'reentrancy', 'input_validation']

        # Days (requires analysis or complex setup)
        days = ['access_control', 'logic_error']

        # Weeks (requires deep analysis)
        weeks = ['timestamp_dependence', 'gas_limit', 'denial_of_service']

        if vulnerability_type in immediate:
            return "immediate" if severity in ['critical', 'high'] else "hours"
        elif vulnerability_type in hours:
            return "hours" if severity == 'critical' else "days"
        elif vulnerability_type in days:
            return "days"
        else:
            return "weeks"

    def _get_attack_complexity(self, vulnerability_type: str) -> str:
        """Assess attack complexity"""
        # Low complexity (well-documented, tools available)
        low = ['flash_loan_attack', 'unchecked_external_call', 'input_validation',
               'pool_reserve_manipulation']

        # Medium complexity (requires some expertise)
        medium = ['oracle_manipulation', 'reentrancy', 'access_control']

        # High complexity (requires deep analysis)
        high = ['logic_error', 'timestamp_dependence', 'integer_overflow']

        if vulnerability_type in low:
            return "low"
        elif vulnerability_type in medium:
            return "medium"
        else:
            return "high"

    def _find_historical_exploit(self, vulnerability_type: str) -> Optional[str]:
        """Find real-world exploit example"""
        return self.exploit_database.get(vulnerability_type)

    def _estimate_remediation_cost(self, vulnerability_type: str, severity: str) -> str:
        """Estimate developer time to fix"""
        # Base hours by type
        base_hours = {
            'oracle_manipulation': '8-16 hours',
            'flash_loan_attack': '16-24 hours',
            'reentrancy': '4-8 hours',
            'access_control': '2-4 hours',
            'unchecked_external_call': '1-2 hours',
            'input_validation': '1-2 hours',
            'logic_error': '8-40 hours',  # Highly variable
            'pool_reserve_manipulation': '16-32 hours',
        }

        return base_hours.get(vulnerability_type, '4-8 hours')

    def _calculate_confidence(
        self,
        vulnerability_type: str,
        context: Optional[Dict[str, Any]],
        historical_precedent: Optional[str]
    ) -> int:
        """Calculate confidence in impact estimate (0-100)"""
        confidence = 50  # Base confidence

        # Boost if we have historical precedent
        if historical_precedent:
            confidence += 20

        # Boost if we have TVL data
        if context and 'tvl' in context:
            confidence += 15

        # Boost for well-studied vulnerabilities
        well_studied = ['oracle_manipulation', 'flash_loan_attack', 'reentrancy',
                       'unchecked_external_call']
        if vulnerability_type in well_studied:
            confidence += 15

        return min(confidence, 95)  # Cap at 95% (never 100% certain)

    def _initialize_exploit_database(self) -> Dict[str, str]:
        """Initialize database of real exploits for reference"""
        return {
            'oracle_manipulation': 'Moby (Jan 2025, flash loan), The Vow (Aug 2024), Polter Finance (2024) - $70M+ total',
            'flash_loan_attack': 'bZx (2020), Harvest Finance (2020), Cream Finance (2021) - $33.8M in 2024',
            'pool_reserve_manipulation': 'Multiple DEX exploits - Most common DeFi attack (34.3%)',
            'reentrancy': 'The DAO (2016, $60M), Lendf.Me (2020), Uniswap V1 (2020) - $35.7M in 2024',
            'access_control': 'Poly Network (2021, $611M), Ronin Bridge (2022, $625M) - $953.2M in 2024',
            'unchecked_external_call': 'Parity Wallet (2017, $150M+) - $550.7K in 2024',
            'input_validation': 'Multiple protocols - $14.6M in 2024 (most common vulnerability)',
            'logic_error': 'Various protocols - $63.8M in 2024',
        }

    def format_impact_report(self, impact: EconomicImpact) -> str:
        """Format economic impact for human-readable display"""
        return f"""
╔══════════════════════════════════════════════════════════════════
║ 💰 ECONOMIC IMPACT ASSESSMENT
╠══════════════════════════════════════════════════════════════════
║ Vulnerability: {impact.vulnerability_type}
║ Severity: {impact.severity.upper()}
║ Impact Category: {impact.impact_category.value.upper()}
║
║ 💵 Estimated Financial Loss:
║   └─ Range: ${impact.estimated_loss_usd[0]:,} - ${impact.estimated_loss_usd[1]:,} USD
║   └─ TVL %: {impact.estimated_loss_percentage[0]:.1f}% - {impact.estimated_loss_percentage[1]:.1f}%
║
║ 📊 Risk Assessment:
║   └─ Overall Risk Score: {impact.risk_score:.1f}/100
║   └─ Likelihood: {impact.likelihood_score*100:.0f}%
║   └─ Exploitability: {impact.exploitability_score*100:.0f}%
║
║ ⚡ Attack Profile:
║   └─ Time to Exploit: {impact.time_to_exploit}
║   └─ Complexity: {impact.attack_complexity}
║
║ 🔧 Remediation:
║   └─ Est. Developer Time: {impact.remediation_cost}
║
{"║ 📚 Historical Precedent:" if impact.historical_precedent else ""}
{"║   └─ " + impact.historical_precedent if impact.historical_precedent else ""}
║
║ Confidence: {impact.confidence}%
╚══════════════════════════════════════════════════════════════════
"""
