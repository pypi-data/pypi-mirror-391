"""
LLM Configuration and Cost Controls
Manages LLM usage limits, model selection, and cost optimization
"""

from typing import Dict, Any
from enum import Enum


class ModelTier(Enum):
    """Model tiers for different use cases"""
    COMPLEX = "claude-3-5-sonnet-20241022"  # Best quality, higher cost
    SIMPLE = "claude-3-haiku-20240307"      # Fast and cheap
    BALANCED = "claude-3-5-sonnet-20241022"  # Default choice


class LLMConfig:
    """LLM cost controls and configuration"""

    # Limits
    MAX_VULNS_TO_ENHANCE = 5  # Only enhance top 5 vulnerabilities
    MAX_TOKENS = 2000  # Token limit per request
    TIMEOUT_SECONDS = 30  # API timeout

    # Model selection
    DEFAULT_MODEL = ModelTier.COMPLEX.value

    # Cost optimization flags
    USE_HAIKU_FOR_LOW_SEVERITY = True  # Use cheaper model for low/medium
    ENABLE_CACHING = True  # Cache responses (future feature)

    # Severity-based model selection
    SEVERITY_MODEL_MAP = {
        'critical': ModelTier.COMPLEX.value,
        'high': ModelTier.COMPLEX.value,
        'medium': ModelTier.SIMPLE.value if USE_HAIKU_FOR_LOW_SEVERITY else ModelTier.COMPLEX.value,
        'low': ModelTier.SIMPLE.value if USE_HAIKU_FOR_LOW_SEVERITY else ModelTier.COMPLEX.value,
    }

    # Cost estimates (as of Jan 2025)
    COST_PER_1K_TOKENS = {
        ModelTier.COMPLEX.value: {
            'input': 0.003,   # $3 per million tokens
            'output': 0.015,  # $15 per million tokens
        },
        ModelTier.SIMPLE.value: {
            'input': 0.00025,  # $0.25 per million tokens
            'output': 0.00125,  # $1.25 per million tokens
        }
    }

    @staticmethod
    def select_model(severity: str) -> str:
        """
        Select appropriate model based on vulnerability severity

        Args:
            severity: Vulnerability severity (critical, high, medium, low)

        Returns:
            Model identifier string
        """
        return LLMConfig.SEVERITY_MODEL_MAP.get(
            severity.lower(),
            LLMConfig.DEFAULT_MODEL
        )

    @staticmethod
    def estimate_cost(
        num_vulnerabilities: int,
        avg_input_tokens: int = 800,
        avg_output_tokens: int = 1500
    ) -> Dict[str, Any]:
        """
        Estimate LLM enhancement cost

        Args:
            num_vulnerabilities: Number of vulnerabilities to enhance
            avg_input_tokens: Average input tokens per request
            avg_output_tokens: Average output tokens per request

        Returns:
            Dictionary with cost breakdown
        """
        # Assume 60% critical/high (Sonnet), 40% medium/low (Haiku if enabled)
        complex_ratio = 0.6
        simple_ratio = 0.4 if LLMConfig.USE_HAIKU_FOR_LOW_SEVERITY else 0.0

        complex_count = int(num_vulnerabilities * complex_ratio)
        simple_count = num_vulnerabilities - complex_count

        # Calculate costs
        complex_cost = (
            complex_count * (
                (avg_input_tokens / 1000) * LLMConfig.COST_PER_1K_TOKENS[ModelTier.COMPLEX.value]['input'] +
                (avg_output_tokens / 1000) * LLMConfig.COST_PER_1K_TOKENS[ModelTier.COMPLEX.value]['output']
            )
        )

        simple_cost = (
            simple_count * (
                (avg_input_tokens / 1000) * LLMConfig.COST_PER_1K_TOKENS[ModelTier.SIMPLE.value]['input'] +
                (avg_output_tokens / 1000) * LLMConfig.COST_PER_1K_TOKENS[ModelTier.SIMPLE.value]['output']
            )
        )

        total_cost = complex_cost + simple_cost

        return {
            'total_cost': round(total_cost, 4),
            'complex_vulns': complex_count,
            'complex_cost': round(complex_cost, 4),
            'simple_vulns': simple_count,
            'simple_cost': round(simple_cost, 4),
            'cost_per_vuln': round(total_cost / num_vulnerabilities, 4) if num_vulnerabilities > 0 else 0,
        }

    @staticmethod
    def should_enhance(
        vulnerability: Dict[str, Any],
        current_count: int
    ) -> bool:
        """
        Determine if vulnerability should be enhanced with LLM

        Args:
            vulnerability: Vulnerability data
            current_count: Number of vulnerabilities already enhanced

        Returns:
            True if should enhance, False otherwise
        """
        # Check limit
        if current_count >= LLMConfig.MAX_VULNS_TO_ENHANCE:
            return False

        # Always enhance critical/high
        severity = vulnerability.get('severity', '').lower()
        if severity in ['critical', 'high']:
            return True

        # Enhance medium/low only if under limit
        return current_count < LLMConfig.MAX_VULNS_TO_ENHANCE


class UsageTracker:
    """Track LLM API usage for cost monitoring"""

    def __init__(self):
        self.requests = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0

    def record_request(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ):
        """Record an API request for cost tracking"""
        self.requests += 1
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens

        # Calculate cost
        cost_config = LLMConfig.COST_PER_1K_TOKENS.get(model, {})
        input_cost = (input_tokens / 1000) * cost_config.get('input', 0)
        output_cost = (output_tokens / 1000) * cost_config.get('output', 0)

        self.total_cost += (input_cost + output_cost)

    def get_summary(self) -> Dict[str, Any]:
        """Get usage summary"""
        return {
            'requests': self.requests,
            'total_input_tokens': self.total_input_tokens,
            'total_output_tokens': self.total_output_tokens,
            'total_cost': round(self.total_cost, 4),
            'avg_cost_per_request': round(
                self.total_cost / self.requests, 4
            ) if self.requests > 0 else 0,
        }

    def reset(self):
        """Reset usage tracking"""
        self.requests = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
