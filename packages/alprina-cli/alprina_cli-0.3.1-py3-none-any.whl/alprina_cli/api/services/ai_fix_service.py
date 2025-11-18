"""
AI Fix Service - Security-focused code fix generation using Kimi AI (primary) and OpenAI (fallback)

IMPORTANT: This service is strictly limited to security fixes only.
- Does NOT generate new features
- Does NOT refactor non-security code
- Does NOT act as a general code assistant
- Enforces token limits to control costs
"""

import os
import httpx
from typing import Dict, List, Optional, Any
from loguru import logger
from datetime import datetime


class AIFixService:
    """
    AI-powered security fix generator with strict security-only scope.
    
    Uses Kimi API (Moonshot AI) as primary provider with OpenAI as fallback.
    Enforces token limits and validates that fixes are security-related.
    """
    
    # Token limits to control costs
    MAX_INPUT_TOKENS = 2000  # Max tokens in vulnerability context
    MAX_OUTPUT_TOKENS = 1000  # Max tokens in fix response
    
    # Security-only keywords to validate fixes
    SECURITY_KEYWORDS = [
        "sql injection", "xss", "cross-site scripting", "csrf", "authentication",
        "authorization", "secret", "password", "api key", "token", "encryption",
        "sanitize", "validate", "escape", "security", "vulnerability", "exploit",
        "hardcoded", "insecure", "cve", "owasp", "unsafe", "injection"
    ]
    
    def __init__(self):
        """Initialize AI Fix Service with Kimi and OpenAI clients."""
        self.kimi_api_key = os.getenv("KIMI_API_KEY", "sk-wEPam0kfyUviFK1hsHuVn4bHlutpOsj6v9YzRiQUSJP9f8hn")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Kimi API configuration
        self.kimi_base_url = "https://api.moonshot.cn/v1"
        self.kimi_model = "moonshot-v1-8k"  # Kimi's 8K context model
        
        # OpenAI configuration (fallback)
        self.openai_model = "gpt-4o-mini"  # Cost-effective model
        
        # Usage tracking
        self.usage_stats = {
            "kimi_calls": 0,
            "openai_calls": 0,
            "tokens_used": 0,
            "errors": 0
        }
        
        logger.info("AIFixService initialized (Kimi primary, OpenAI fallback)")
    
    async def generate_security_fix(
        self,
        vulnerability: Dict[str, Any],
        code_context: str,
        file_path: str
    ) -> Dict[str, Any]:
        """
        Generate a security fix for a vulnerability.
        
        Args:
            vulnerability: Vulnerability details (type, severity, line, description)
            code_context: Code snippet around the vulnerability
            file_path: Path to the file containing the vulnerability
        
        Returns:
            Dict containing:
                - fixed_code: The corrected code
                - explanation: Why this fix addresses the vulnerability
                - diff: Unified diff of changes
                - confidence: Confidence score (0.0-1.0)
                - provider: Which AI provider was used (kimi/openai)
                - is_security_fix: Validation that this is security-related
        """
        try:
            # Validate that this is a security vulnerability
            if not self._is_security_vulnerability(vulnerability):
                return {
                    "error": "Not a security vulnerability",
                    "message": "This service only generates fixes for security vulnerabilities",
                    "is_security_fix": False
                }
            
            # Truncate context to respect token limits
            truncated_context = self._truncate_context(code_context)
            
            # Build security-focused prompt
            prompt = self._build_security_fix_prompt(
                vulnerability, truncated_context, file_path
            )
            
            # Try Kimi API first
            logger.info(f"Attempting Kimi AI fix for {vulnerability.get('type')}")
            try:
                result = await self._call_kimi_api(prompt)
                if result and result.get("fixed_code"):
                    self.usage_stats["kimi_calls"] += 1
                    result["provider"] = "kimi"
                    result["is_security_fix"] = True
                    logger.info("✅ Fix generated successfully using Kimi AI")
                    return result
            except Exception as e:
                logger.warning(f"Kimi API failed: {e}, falling back to OpenAI")
                self.usage_stats["errors"] += 1
            
            # Fallback to OpenAI
            if self.openai_api_key:
                logger.info("Falling back to OpenAI for fix generation")
                try:
                    result = await self._call_openai_api(prompt)
                    if result and result.get("fixed_code"):
                        self.usage_stats["openai_calls"] += 1
                        result["provider"] = "openai"
                        result["is_security_fix"] = True
                        logger.info("✅ Fix generated successfully using OpenAI")
                        return result
                except Exception as e:
                    logger.error(f"OpenAI API also failed: {e}")
                    self.usage_stats["errors"] += 1
            
            # Both failed
            return {
                "error": "All AI providers failed",
                "message": "Could not generate fix - please try again later",
                "is_security_fix": False
            }
            
        except Exception as e:
            logger.error(f"Error in generate_security_fix: {e}")
            return {
                "error": str(e),
                "message": "Internal error generating fix",
                "is_security_fix": False
            }
    
    def _is_security_vulnerability(self, vulnerability: Dict) -> bool:
        """
        Validate that this is a security vulnerability.
        
        We only fix security issues, not general code quality problems.
        """
        vuln_type = vulnerability.get("type", "").lower()
        vuln_desc = vulnerability.get("description", "").lower()
        vuln_title = vulnerability.get("title", "").lower()
        
        combined_text = f"{vuln_type} {vuln_desc} {vuln_title}"
        
        # Check if any security keyword is present
        return any(keyword in combined_text for keyword in self.SECURITY_KEYWORDS)
    
    def _truncate_context(self, code_context: str) -> str:
        """
        Truncate code context to respect token limits.
        
        Rough estimate: 1 token ≈ 4 characters for English
        """
        max_chars = self.MAX_INPUT_TOKENS * 4
        if len(code_context) > max_chars:
            logger.warning(f"Truncating context from {len(code_context)} to {max_chars} chars")
            return code_context[:max_chars] + "\n... (truncated)"
        return code_context
    
    def _build_security_fix_prompt(
        self,
        vulnerability: Dict,
        code_context: str,
        file_path: str
    ) -> str:
        """
        Build a security-focused prompt for AI fix generation.
        
        The prompt explicitly limits scope to security fixes only.
        """
        vuln_type = vulnerability.get("type", "Unknown")
        vuln_severity = vulnerability.get("severity", "MEDIUM")
        vuln_desc = vulnerability.get("description", "No description")
        line = vulnerability.get("line", "N/A")
        
        return f"""You are a security expert tasked with fixing a specific security vulnerability.

**CRITICAL: You must ONLY fix security vulnerabilities. Do NOT:**
- Refactor unrelated code
- Add new features
- Improve code style/formatting
- Optimize performance
- Make non-security changes

**Vulnerability Details:**
- Type: {vuln_type}
- Severity: {vuln_severity}
- Line: {line}
- Description: {vuln_desc}
- File: {file_path}

**Vulnerable Code Context:**
```
{code_context}
```

**Your Task:**
1. Identify the EXACT security issue in the code
2. Provide a MINIMAL fix that addresses ONLY this security vulnerability
3. Explain WHY your fix is secure
4. Keep all other code unchanged

**Response Format (JSON):**
```json
{{
  "fixed_code": "... only the fixed code section ...",
  "explanation": "Brief explanation of the security fix",
  "security_principle": "Which security principle this addresses (e.g., 'Input validation', 'Least privilege')",
  "confidence": 0.95
}}
```

**Remember:** Make the SMALLEST possible change to fix the security issue. Do not refactor."""
    
    async def _call_kimi_api(self, prompt: str) -> Dict[str, Any]:
        """
        Call Kimi API (Moonshot AI) for fix generation.
        
        Kimi API is OpenAI-compatible, making integration straightforward.
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.kimi_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.kimi_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.kimi_model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a security expert who fixes vulnerabilities with minimal code changes. Return responses in JSON format."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.3,  # Low temperature for consistent security fixes
                    "max_tokens": self.MAX_OUTPUT_TOKENS
                }
            )
        
        if response.status_code != 200:
            raise Exception(f"Kimi API error: {response.status_code} - {response.text}")
        
        result = response.json()
        
        # Track token usage
        usage = result.get("usage", {})
        tokens_used = usage.get("total_tokens", 0)
        self.usage_stats["tokens_used"] += tokens_used
        logger.info(f"Kimi API tokens used: {tokens_used}")
        
        # Parse response
        content = result["choices"][0]["message"]["content"]
        return self._parse_ai_response(content)
    
    async def _call_openai_api(self, prompt: str) -> Dict[str, Any]:
        """
        Call OpenAI API as fallback for fix generation.
        """
        try:
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(api_key=self.openai_api_key)
            
            response = await client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a security expert who fixes vulnerabilities with minimal code changes. Return responses in JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=self.MAX_OUTPUT_TOKENS
            )
            
            # Track token usage
            tokens_used = response.usage.total_tokens
            self.usage_stats["tokens_used"] += tokens_used
            logger.info(f"OpenAI API tokens used: {tokens_used}")
            
            content = response.choices[0].message.content
            return self._parse_ai_response(content)
            
        except ImportError:
            raise Exception("OpenAI package not installed. Install with: pip install openai")
    
    def _parse_ai_response(self, content: str) -> Dict[str, Any]:
        """
        Parse AI response and extract fix details.
        
        Handles both JSON and plain text responses.
        """
        import json
        
        try:
            # Try to parse as JSON
            if "```json" in content:
                # Extract JSON from markdown code block
                json_str = content.split("```json")[1].split("```")[0].strip()
                return json.loads(json_str)
            elif content.strip().startswith("{"):
                return json.loads(content)
            else:
                # Plain text response - try to extract relevant parts
                return {
                    "fixed_code": content,
                    "explanation": "AI provided fix in plain text format",
                    "confidence": 0.7
                }
        except Exception as e:
            logger.warning(f"Could not parse AI response as JSON: {e}")
            return {
                "fixed_code": content,
                "explanation": "Raw AI response (parsing failed)",
                "confidence": 0.5
            }
    
    def get_usage_stats(self) -> Dict[str, int]:
        """Get usage statistics for monitoring."""
        return self.usage_stats.copy()


# Global instance
ai_fix_service = AIFixService()
