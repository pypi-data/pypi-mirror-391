"""
LLM Enhancement Layer - Claude AI Integration
Enhances static analysis findings with contextual reasoning
"""

import os
import re
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from loguru import logger

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic SDK not installed. LLM enhancement unavailable.")


@dataclass
class EnhancedVulnerability:
    """Vulnerability enhanced with LLM reasoning"""
    # Original fields
    vulnerability_type: str
    severity: str
    title: str
    description: str
    file_path: str
    line_number: int

    # LLM enhancements
    business_impact: str = ""
    economic_loss: str = ""
    attack_scenario: str = ""
    historical_precedent: str = ""
    priority_reasoning: str = ""
    remediation_code: str = ""
    llm_explanation: str = ""
    llm_enhanced: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


class LLMEnhancer:
    """Enhance security findings with Claude AI"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Claude client

        Args:
            api_key: Optional API key, defaults to ANTHROPIC_API_KEY env var

        Raises:
            ValueError: If API key not provided and not in environment
            ImportError: If anthropic package not installed
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "Anthropic SDK not installed. Install with: pip install anthropic"
            )

        api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable not set. "
                "Get your API key at https://console.anthropic.com/"
            )

        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-5-20250929"  # Claude Sonnet 4.5
        logger.info("✅ LLM Enhancer initialized with Claude Sonnet 4.5")

    def enhance_vulnerability(
        self,
        vuln: Dict[str, Any],
        contract_code: str
    ) -> EnhancedVulnerability:
        """
        Enhance vulnerability with AI-powered context

        Args:
            vuln: Static analysis vulnerability dict
            contract_code: Full contract source code

        Returns:
            EnhancedVulnerability with LLM analysis
        """
        try:
            # Get code context
            code_context = self._get_code_context(
                contract_code,
                vuln.get('line_number', 1)
            )

            # Build prompt
            prompt = self._build_prompt(vuln, code_context)

            # Call Claude
            logger.debug(f"Enhancing {vuln.get('title', 'Unknown')} with Claude AI")
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0,  # Deterministic for security
                system="You are an expert smart contract security auditor with deep knowledge of historical exploits and attack patterns.",
                messages=[{"role": "user", "content": prompt}]
            )

            analysis = response.content[0].text

            # Parse response
            enhanced = EnhancedVulnerability(
                vulnerability_type=vuln.get('vulnerability_type', 'unknown'),
                severity=vuln.get('severity', 'medium'),
                title=vuln.get('title', 'Untitled'),
                description=vuln.get('description', ''),
                file_path=vuln.get('file_path', ''),
                line_number=vuln.get('line_number', 0),
                llm_explanation=analysis,
                business_impact=self._extract_section(analysis, "Business Impact"),
                economic_loss=self._extract_section(analysis, "Economic Loss"),
                attack_scenario=self._extract_section(analysis, "Attack Scenario"),
                historical_precedent=self._extract_section(analysis, "Historical Precedent"),
                priority_reasoning=self._extract_section(analysis, "Priority"),
                remediation_code=self._extract_code_block(analysis),
                llm_enhanced=True
            )

            logger.debug(f"✅ Enhanced vulnerability: {vuln.get('title', 'Unknown')}")
            return enhanced

        except Exception as e:
            logger.error(f"LLM enhancement failed: {e}")
            # Return original vuln without enhancement
            return EnhancedVulnerability(
                vulnerability_type=vuln.get('vulnerability_type', 'unknown'),
                severity=vuln.get('severity', 'medium'),
                title=vuln.get('title', 'Untitled'),
                description=vuln.get('description', ''),
                file_path=vuln.get('file_path', ''),
                line_number=vuln.get('line_number', 0),
                llm_enhanced=False
            )

    def _build_prompt(self, vuln: Dict, code_context: str) -> str:
        """Build Claude prompt for vulnerability analysis"""
        return f"""Analyze this smart contract vulnerability:

STATIC ANALYSIS FINDING:
- Type: {vuln.get('vulnerability_type', 'Unknown')}
- Severity: {vuln.get('severity', 'Unknown')}
- Title: {vuln.get('title', 'Untitled')}
- Description: {vuln.get('description', 'No description')}
- Location: Line {vuln.get('line_number', 'Unknown')}

CODE CONTEXT:
```solidity
{code_context}
```

Provide comprehensive analysis in these sections:

## Business Impact
Explain in simple terms how this vulnerability could be exploited and what the consequences would be. Focus on the "what happens" not the technical details.

## Economic Loss
Estimate potential financial loss based on 2024 DeFi exploit data:
- Reentrancy attacks: $35.7M average
- Access Control issues: $953M total (2024)
- Oracle Manipulation: $8.7M average
- Flash Loan attacks: $33.8M average

## Attack Scenario
Provide step-by-step technical breakdown of how an attacker would exploit this. Be specific about:
1. What the attacker does
2. What happens in the contract
3. How they profit
4. How long it takes

## Historical Precedent
Reference real exploits with similar patterns. Examples:
- DAO Hack (2016) - $60M reentrancy
- Cream Finance (2021) - $130M flash loan + reentrancy
- Polter Finance (2024) - $8.7M oracle manipulation
- Wormhole (2022) - $325M signature verification

## Priority
Explain why this should (or shouldn't) be fixed immediately. Consider:
- Exploitability: How easy is it to exploit?
- Impact: How much damage could it cause?
- Likelihood: Is the contract deployed? What's the TVL?

## Remediation Code
Provide secure code that fixes the vulnerability. Include:
- Complete function with fix
- Security comments explaining what changed
- Any additional imports needed (e.g., OpenZeppelin)

Format with proper Solidity syntax."""

    def _get_code_context(self, code: str, line_num: int, context_lines: int = 5) -> str:
        """Extract code context around vulnerability line"""
        lines = code.split('\n')
        start = max(0, line_num - context_lines - 1)
        end = min(len(lines), line_num + context_lines)

        context = []
        for i, line in enumerate(lines[start:end], start=start):
            marker = " --> " if i == line_num - 1 else "     "
            context.append(f"{marker}{i+1:4d} | {line}")

        return '\n'.join(context)

    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract named section from LLM response"""
        pattern = rf"## {section_name}\s*\n(.*?)(?=\n##|\Z)"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""

    def _extract_code_block(self, text: str) -> str:
        """Extract Solidity code block from markdown"""
        pattern = r"```(?:solidity)?\n(.*?)```"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""


# Convenience function for easy integration
def enhance_if_available(vuln: Dict, code: str) -> Any:
    """
    Try to enhance with LLM, fall back gracefully if unavailable

    Returns original vuln dict if LLM not available, EnhancedVulnerability otherwise
    """
    try:
        enhancer = LLMEnhancer()
        enhanced = enhancer.enhance_vulnerability(vuln, code)
        return enhanced.to_dict()
    except (ValueError, ImportError, Exception) as e:
        logger.debug(f"LLM enhancement unavailable: {e}")
        return vuln
