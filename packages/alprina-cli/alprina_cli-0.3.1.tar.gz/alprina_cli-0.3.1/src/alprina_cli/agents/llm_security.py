"""
LLM Security Agent - Protect AI/LLM applications from security threats.

Inspired by Noma Security's AI security platform.
Detects: Prompt injection, jailbreaking, model poisoning, data leakage.
"""

from typing import Dict, List, Any, Optional
from loguru import logger
import re
import json


class LLMSecurityAgent:
    """
    Security agent for Large Language Model (LLM) applications.
    
    Capabilities:
    - Prompt injection detection
    - Jailbreak attempt detection
    - PII/sensitive data leakage detection
    - Output validation
    - Token usage monitoring
    - Model behavior analysis
    """
    
    def __init__(self):
        """Initialize LLM Security Agent."""
        self.name = "LLM Security Agent"
        self.agent_type = "llm-security"
        logger.debug(f"{self.name} initialized")
        
        # Known prompt injection patterns
        self.injection_patterns = [
            # System prompt override attempts
            r"(?i)ignore (all )?previous (instructions?|prompts?|commands?)",
            r"(?i)disregard (all )?(previous|above|prior) (instructions?|prompts?)",
            r"(?i)forget (all )?(previous|above) (instructions?|prompts?)",
            r"(?i)new (instructions?|prompts?|system)",
            
            # Jailbreak attempts
            r"(?i)(you are|act as|pretend to be|roleplay as) (dan|a? ?jailbreak|evil|malicious)",
            r"(?i)developer mode",
            r"(?i)sudo mode",
            r"(?i)god mode",
            r"(?i)unrestricted mode",
            
            # Prompt leakage attempts
            r"(?i)show (me )?(your|the) (system|initial|original) prompt",
            r"(?i)print (your|the) (instructions?|prompts?)",
            r"(?i)reveal (your|the) (system|hidden) (prompt|instructions?)",
            r"(?i)what (are|were) you told",
            
            # Command injection
            r"(?i)execute|eval|system|subprocess|os\.|shell",
            r"(?i)__import__|importlib",
            
            # Multi-turn attacks
            r"(?i)(step|part|phase) (\d+|one|two|three).*?(final|last) step",
            r"(?i)first.*?then.*?finally",
        ]
        
        # PII patterns
        self.pii_patterns = {
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
            "credit_card": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
            "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
            "api_key": r"(api[_-]?key|apikey|api[_-]?token)[\s:=]+['\"]?([a-zA-Z0-9_\-]{20,})['\"]?",
            "password": r"(password|passwd|pwd)[\s:=]+['\"]?([^\s\"']{8,})['\"]?",
        }
        
        # Toxic/harmful content patterns
        self.harmful_patterns = [
            r"(?i)(how to|guide to|instructions for) (hack|crack|break into|bypass)",
            r"(?i)(build|create|make) (a )?(bomb|weapon|malware|virus)",
            r"(?i)(illegal|illicit) (activities?|drugs|substances)",
        ]
    
    def scan_prompt(self, prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Scan a user prompt for security issues before sending to LLM.
        
        Args:
            prompt: User's input prompt
            context: Optional context (conversation history, etc.)
        
        Returns:
            Security analysis results
        """
        logger.debug(f"Scanning prompt: {prompt[:100]}...")
        
        findings = []
        risk_score = 0
        
        # Check for prompt injection
        injection_results = self._detect_prompt_injection(prompt)
        if injection_results["detected"]:
            findings.append({
                "type": "prompt_injection",
                "severity": "HIGH",
                "title": "Prompt Injection Attempt Detected",
                "description": "User prompt contains patterns attempting to override system instructions",
                "details": injection_results["matches"],
                "recommendation": "Block this prompt and log the attempt"
            })
            risk_score += 80
        
        # Check for jailbreak attempts
        jailbreak_results = self._detect_jailbreak(prompt)
        if jailbreak_results["detected"]:
            findings.append({
                "type": "jailbreak_attempt",
                "severity": "HIGH",
                "title": "Jailbreak Attempt Detected",
                "description": "User trying to bypass model safety constraints",
                "details": jailbreak_results["matches"],
                "recommendation": "Block this prompt and monitor user"
            })
            risk_score += 85
        
        # Check for PII in prompt
        pii_results = self._detect_pii(prompt)
        if pii_results["detected"]:
            findings.append({
                "type": "pii_detected",
                "severity": "MEDIUM",
                "title": "PII Detected in Prompt",
                "description": "Prompt contains personally identifiable information",
                "details": pii_results["pii_types"],
                "recommendation": "Redact PII before sending to LLM"
            })
            risk_score += 40
        
        # Check for harmful content requests
        harmful_results = self._detect_harmful_content(prompt)
        if harmful_results["detected"]:
            findings.append({
                "type": "harmful_request",
                "severity": "HIGH",
                "title": "Harmful Content Request",
                "description": "User requesting harmful or illegal information",
                "details": harmful_results["matches"],
                "recommendation": "Block this prompt and log for review"
            })
            risk_score += 90
        
        # Calculate final risk level
        if risk_score >= 70:
            risk_level = "CRITICAL"
        elif risk_score >= 40:
            risk_level = "HIGH"
        elif risk_score >= 20:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            "safe": len(findings) == 0,
            "risk_level": risk_level,
            "risk_score": min(risk_score, 100),
            "findings": findings,
            "prompt": prompt,
            "timestamp": self._get_timestamp()
        }
    
    def scan_output(self, output: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Scan LLM output for security issues before returning to user.
        
        Args:
            output: LLM's generated output
            context: Optional context
        
        Returns:
            Security analysis results
        """
        logger.debug(f"Scanning LLM output: {output[:100]}...")
        
        findings = []
        risk_score = 0
        
        # Check for leaked PII
        pii_results = self._detect_pii(output)
        if pii_results["detected"]:
            findings.append({
                "type": "pii_leakage",
                "severity": "HIGH",
                "title": "PII Leaked in Output",
                "description": "LLM output contains personally identifiable information",
                "details": pii_results["pii_types"],
                "recommendation": "Redact PII before showing to user"
            })
            risk_score += 70
        
        # Check for sensitive data exposure
        sensitive_results = self._detect_sensitive_data(output)
        if sensitive_results["detected"]:
            findings.append({
                "type": "sensitive_data_exposure",
                "severity": "MEDIUM",
                "title": "Sensitive Data in Output",
                "description": "Output may contain sensitive information",
                "details": sensitive_results["types"],
                "recommendation": "Review and redact sensitive data"
            })
            risk_score += 50
        
        # Check for hallucination indicators
        hallucination_results = self._detect_hallucination_indicators(output)
        if hallucination_results["likely"]:
            findings.append({
                "type": "potential_hallucination",
                "severity": "LOW",
                "title": "Potential Hallucination Detected",
                "description": "Output may contain fabricated information",
                "details": hallucination_results["indicators"],
                "recommendation": "Verify information before trusting"
            })
            risk_score += 20
        
        return {
            "safe": len(findings) == 0,
            "risk_score": min(risk_score, 100),
            "findings": findings,
            "output": output,
            "timestamp": self._get_timestamp()
        }
    
    def _detect_prompt_injection(self, text: str) -> Dict[str, Any]:
        """Detect prompt injection patterns."""
        matches = []
        for pattern in self.injection_patterns:
            found = re.findall(pattern, text)
            if found:
                matches.append({
                    "pattern": pattern,
                    "matches": found
                })
        
        return {
            "detected": len(matches) > 0,
            "matches": matches
        }
    
    def _detect_jailbreak(self, text: str) -> Dict[str, Any]:
        """Detect jailbreak attempt patterns."""
        jailbreak_keywords = [
            "dan", "jailbreak", "developer mode", "god mode",
            "unrestricted", "bypass", "ignore rules", "evil mode"
        ]
        
        matches = []
        text_lower = text.lower()
        for keyword in jailbreak_keywords:
            if keyword in text_lower:
                matches.append(keyword)
        
        return {
            "detected": len(matches) > 0,
            "matches": matches
        }
    
    def _detect_pii(self, text: str) -> Dict[str, Any]:
        """Detect personally identifiable information."""
        pii_found = {}
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Redact matched PII
                pii_found[pii_type] = [self._redact(m) for m in matches]
        
        return {
            "detected": len(pii_found) > 0,
            "pii_types": pii_found
        }
    
    def _detect_harmful_content(self, text: str) -> Dict[str, Any]:
        """Detect requests for harmful or illegal content."""
        matches = []
        for pattern in self.harmful_patterns:
            found = re.findall(pattern, text)
            if found:
                matches.append({
                    "pattern": pattern,
                    "matches": found
                })
        
        return {
            "detected": len(matches) > 0,
            "matches": matches
        }
    
    def _detect_sensitive_data(self, text: str) -> Dict[str, Any]:
        """Detect sensitive data in output."""
        sensitive_types = []
        
        # Check for API keys, tokens, secrets
        if re.search(r"(api[_-]?key|token|secret|password)[\s:=]", text, re.IGNORECASE):
            sensitive_types.append("credentials")
        
        # Check for internal URLs/IPs
        if re.search(r"(192\.168\.|10\.|172\.(1[6-9]|2[0-9]|3[0-1])\.)", text):
            sensitive_types.append("internal_ip")
        
        # Check for file paths
        if re.search(r"(/etc/|/home/|/root/|C:\\|/var/)", text):
            sensitive_types.append("file_paths")
        
        return {
            "detected": len(sensitive_types) > 0,
            "types": sensitive_types
        }
    
    def _detect_hallucination_indicators(self, text: str) -> Dict[str, Any]:
        """Detect potential hallucination indicators in output."""
        indicators = []
        
        # Check for uncertainty markers
        uncertainty_phrases = [
            "i'm not sure", "i think", "maybe", "possibly",
            "i don't know", "unclear", "uncertain"
        ]
        
        text_lower = text.lower()
        for phrase in uncertainty_phrases:
            if phrase in text_lower:
                indicators.append(f"Uncertainty: '{phrase}'")
        
        # Check for inconsistencies
        if "however" in text_lower and "but" in text_lower:
            indicators.append("Contradictory statements")
        
        return {
            "likely": len(indicators) > 0,
            "indicators": indicators
        }
    
    def _redact(self, text: str) -> str:
        """Redact sensitive information."""
        if isinstance(text, tuple):
            text = text[0] if text else ""
        return f"***REDACTED ({len(str(text))} chars)***"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    def get_recommendations(self) -> List[str]:
        """Get general security recommendations for LLM applications."""
        return [
            "Always validate and sanitize user inputs before sending to LLM",
            "Implement rate limiting to prevent abuse",
            "Monitor for unusual patterns in user prompts",
            "Use separate system prompts that users cannot override",
            "Implement output filtering to prevent PII leakage",
            "Log all suspicious prompts for security review",
            "Use prompt templates with fixed structure",
            "Implement content moderation on both input and output",
            "Monitor token usage for anomalies",
            "Keep model and framework dependencies updated"
        ]


# CLI entry point
def run_llm_security_scan(target: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run LLM security scan.
    
    Args:
        target: Text to scan (prompt or output)
        options: Scan options
    
    Returns:
        Scan results
    """
    agent = LLMSecurityAgent()
    
    scan_type = options.get("type", "prompt")  # "prompt" or "output"
    
    if scan_type == "prompt":
        results = agent.scan_prompt(target)
    else:
        results = agent.scan_output(target)
    
    return {
        "agent": "LLM Security Agent",
        "scan_type": scan_type,
        "results": results,
        "recommendations": agent.get_recommendations() if not results["safe"] else []
    }
