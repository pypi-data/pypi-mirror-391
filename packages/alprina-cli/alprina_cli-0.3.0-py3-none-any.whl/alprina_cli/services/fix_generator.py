"""
AI-Powered Fix Generator - Generates secure code fixes for vulnerabilities.
Uses GPT-4/Claude to create context-aware security fixes with explanations.
"""

import os
import difflib
from typing import Dict, List, Optional
from pathlib import Path
from loguru import logger

from ..llm_provider import get_llm_client


class FixGenerator:
    """
    Generate AI-powered fixes for security vulnerabilities.
    
    Uses existing LLM integration (GPT-4/Claude) to generate secure
    code alternatives with explanations and confidence scoring.
    """

    def __init__(self):
        """Initialize fix generator with LLM client."""
        self.llm = get_llm_client()
        logger.info(f"FixGenerator initialized with LLM provider: {self.llm.provider}")

    def generate_fix(
        self,
        code: str,
        vulnerability: Dict,
        filename: str,
        context_lines: int = 10
    ) -> Dict:
        """
        Generate AI-powered fix for a vulnerability.

        Args:
            code: Full source code of the file
            vulnerability: Vulnerability details (type, severity, line, etc.)
            filename: Name of the file being fixed
            context_lines: Lines of context around vulnerability (default: 10)

        Returns:
            Dict with:
                - fixed_code: Complete fixed code
                - explanation: Why this fix works
                - changes: List of specific changes made
                - diff: Unified diff showing changes
                - confidence: Confidence score (0.0-1.0)
                - security_notes: Important security considerations
        """
        try:
            logger.info(f"Generating fix for {vulnerability.get('type')} in {filename}")

            # Extract relevant code context
            vuln_line = vulnerability.get("line", 0)
            code_lines = code.split("\n")
            
            # Get context around vulnerability
            start_line = max(0, vuln_line - context_lines)
            end_line = min(len(code_lines), vuln_line + context_lines)
            context = "\n".join(code_lines[start_line:end_line])

            # Build fix generation prompt
            prompt = self._build_fix_prompt(
                context=context,
                vulnerability=vulnerability,
                filename=filename,
                full_code_length=len(code_lines)
            )

            # Generate fix using LLM
            logger.debug("Calling LLM for fix generation...")
            response = self.llm.chat(
                messages=[{"role": "user", "content": prompt}],
                system_prompt=self._get_system_prompt(),
                temperature=0.3,  # Lower temperature for more deterministic fixes
                max_tokens=2000
            )

            # Parse LLM response
            fix_data = self._parse_fix_response(response)

            # Generate diff
            fix_data["diff"] = self._generate_diff(context, fix_data.get("fixed_code", context))

            # Calculate confidence score
            fix_data["confidence"] = self._calculate_confidence(vulnerability, fix_data)

            # Add metadata
            fix_data["vulnerability_type"] = vulnerability.get("type")
            fix_data["severity"] = vulnerability.get("severity")
            fix_data["filename"] = filename
            fix_data["line"] = vuln_line

            logger.info(f"Fix generated with confidence: {fix_data['confidence']:.2f}")
            return fix_data

        except Exception as e:
            logger.error(f"Error generating fix: {e}")
            return {
                "error": str(e),
                "fixed_code": code,
                "explanation": "Could not generate fix due to error",
                "confidence": 0.0
            }

    def generate_multiple_fixes(
        self,
        findings: List[Dict],
        file_contents: Dict[str, str]
    ) -> Dict[str, List[Dict]]:
        """
        Generate fixes for multiple vulnerabilities across files.

        Args:
            findings: List of vulnerability findings
            file_contents: Dict mapping file paths to their content

        Returns:
            Dict mapping file paths to list of fix suggestions
        """
        fixes_by_file = {}

        for finding in findings:
            file_path = finding.get("location", "").split(":")[0]
            
            if file_path not in file_contents:
                logger.warning(f"File not found: {file_path}")
                continue

            code = file_contents[file_path]
            fix = self.generate_fix(code, finding, file_path)

            if file_path not in fixes_by_file:
                fixes_by_file[file_path] = []
            
            fixes_by_file[file_path].append(fix)

        return fixes_by_file

    def _build_fix_prompt(
        self,
        context: str,
        vulnerability: Dict,
        filename: str,
        full_code_length: int
    ) -> str:
        """Build detailed prompt for fix generation."""
        
        vuln_type = vulnerability.get("type", "Security Issue")
        severity = vulnerability.get("severity", "MEDIUM")
        description = vulnerability.get("description", "")
        cwe = vulnerability.get("cwe", "")
        cvss = vulnerability.get("cvss_score", "")

        prompt = f"""You are a security expert fixing code vulnerabilities.

**VULNERABILITY DETAILS:**
- Type: {vuln_type}
- Severity: {severity}
- File: {filename}
- Line: {vulnerability.get('line', 'unknown')}
{f"- CWE: {cwe}" if cwe else ""}
{f"- CVSS Score: {cvss}/10.0" if cvss else ""}

**ISSUE DESCRIPTION:**
{description}

**VULNERABLE CODE:**
```{self._get_language_from_filename(filename)}
{context}
```

**YOUR TASK:**
Generate a secure fix that:
1. ✅ COMPLETELY resolves the {vuln_type} vulnerability
2. ✅ Maintains ALL original functionality
3. ✅ Follows security best practices
4. ✅ Preserves exact indentation and code style
5. ✅ Includes inline comments explaining the fix
6. ✅ Works with the existing codebase structure

**IMPORTANT:**
- Return ONLY the fixed code section (same lines as shown above)
- Preserve exact indentation (spaces/tabs)
- Don't remove unrelated code
- Add security-focused comments
- Make minimal changes (only fix the vulnerability)

**RETURN FORMAT:**
Return a JSON object with these fields:

{{
  "fixed_code": "complete fixed code with exact indentation",
  "explanation": "detailed explanation of why this fix is secure and how it works",
  "changes": ["specific change 1", "specific change 2", ...],
  "security_notes": ["important security consideration 1", "consideration 2", ...]
}}

**EXAMPLES OF GOOD FIXES:**

SQL Injection:
❌ query = f"SELECT * FROM users WHERE id = {{user_id}}"
✅ query = "SELECT * FROM users WHERE id = ?"
✅ cursor.execute(query, (user_id,))

XSS:
❌ return f"<div>{{user_input}}</div>"
✅ from html import escape
✅ return f"<div>{{escape(user_input)}}</div>"

Hardcoded Secret:
❌ API_KEY = "sk_live_abc123"
✅ import os
✅ API_KEY = os.getenv("API_KEY")
✅ if not API_KEY: raise ValueError("API_KEY not set")

Now generate the secure fix:
"""
        return prompt

    def _get_system_prompt(self) -> str:
        """Get system prompt for LLM."""
        return """You are an expert security engineer specializing in secure code remediation.

Your expertise includes:
- OWASP Top 10 vulnerabilities
- CWE (Common Weakness Enumeration)
- Secure coding practices for all major languages
- Defense-in-depth security principles
- Zero-trust architecture

When generating fixes:
✅ Prioritize security without breaking functionality
✅ Use well-established security libraries and patterns
✅ Add clear comments explaining security rationale
✅ Preserve code style and indentation exactly
✅ Return valid JSON format

Return ONLY valid JSON. No markdown formatting, no explanatory text outside JSON."""

    def _parse_fix_response(self, response: str) -> Dict:
        """Parse LLM response into structured fix data."""
        import json
        import re

        try:
            # Remove markdown code blocks if present
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                response = json_match.group(1)

            # Parse JSON
            fix_data = json.loads(response)

            # Validate required fields
            if "fixed_code" not in fix_data:
                logger.warning("LLM response missing 'fixed_code' field")
                fix_data["fixed_code"] = ""

            # Ensure all expected fields exist
            fix_data.setdefault("explanation", "Fix generated by AI")
            fix_data.setdefault("changes", [])
            fix_data.setdefault("security_notes", [])

            return fix_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.debug(f"Response content: {response[:500]}")

            # Fallback: try to extract code from response
            return {
                "fixed_code": self._extract_code_from_text(response),
                "explanation": "Fix generated, but response format was unexpected",
                "changes": ["Security improvement applied"],
                "security_notes": ["Please verify this fix manually"]
            }

    def _extract_code_from_text(self, text: str) -> str:
        """Extract code from unstructured text response."""
        import re

        # Try to find code blocks
        code_match = re.search(r'```[\w]*\n(.*?)\n```', text, re.DOTALL)
        if code_match:
            return code_match.group(1)

        # If no code blocks, look for fixed_code field
        fixed_match = re.search(r'"fixed_code"\s*:\s*"(.*?)"', text, re.DOTALL)
        if fixed_match:
            return fixed_match.group(1).replace('\\n', '\n')

        # Return original text as fallback
        return text

    def _generate_diff(self, original: str, fixed: str) -> str:
        """Generate unified diff between original and fixed code."""
        original_lines = original.splitlines(keepends=True)
        fixed_lines = fixed.splitlines(keepends=True)

        diff = difflib.unified_diff(
            original_lines,
            fixed_lines,
            fromfile="original",
            tofile="fixed",
            lineterm=""
        )

        return "".join(diff)

    def _calculate_confidence(self, vulnerability: Dict, fix_data: Dict) -> float:
        """
        Calculate confidence score for the generated fix (0.0-1.0).

        Based on:
        - Vulnerability type (some are easier to fix)
        - Fix completeness
        - Explanation quality
        - Security considerations included
        """
        confidence = 0.7  # Base confidence

        vuln_type = vulnerability.get("type", "")

        # High confidence for well-known patterns
        high_confidence_types = [
            "SQL Injection",
            "Hardcoded Secret",
            "XSS",
            "Command Injection",
            "Path Traversal"
        ]
        if any(t.lower() in vuln_type.lower() for t in high_confidence_types):
            confidence += 0.15

        # Lower confidence for complex vulnerabilities
        low_confidence_types = [
            "Race Condition",
            "Business Logic",
            "Authentication Flow",
            "Complex Authorization"
        ]
        if any(t.lower() in vuln_type.lower() for t in low_confidence_types):
            confidence -= 0.2

        # Increase confidence if fix has good explanation
        explanation = fix_data.get("explanation", "")
        if len(explanation) > 100 and "secure" in explanation.lower():
            confidence += 0.05

        # Increase if security notes provided
        if fix_data.get("security_notes") and len(fix_data["security_notes"]) > 0:
            confidence += 0.05

        # Increase if specific changes listed
        if fix_data.get("changes") and len(fix_data["changes"]) > 0:
            confidence += 0.05

        # Cap at 0.95 (never 100% certain)
        return min(0.95, max(0.0, confidence))

    def _get_language_from_filename(self, filename: str) -> str:
        """Determine programming language from filename."""
        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".go": "go",
            ".rb": "ruby",
            ".php": "php",
            ".cs": "csharp",
            ".cpp": "cpp",
            ".c": "c",
            ".rs": "rust",
            ".swift": "swift",
            ".kt": "kotlin",
        }

        ext = Path(filename).suffix.lower()
        return ext_map.get(ext, "")

    def apply_fix(
        self,
        filepath: str,
        fix_data: Dict,
        backup: bool = True
    ) -> bool:
        """
        Apply a generated fix to a file.

        Args:
            filepath: Path to file to fix
            fix_data: Fix data from generate_fix()
            backup: Create .backup file before modifying

        Returns:
            True if successful, False otherwise
        """
        try:
            filepath = Path(filepath)

            # Read current file
            with open(filepath, 'r', encoding='utf-8') as f:
                current_code = f.read()

            # Create backup if requested
            if backup:
                backup_path = filepath.with_suffix(filepath.suffix + ".backup")
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(current_code)
                logger.info(f"Backup created: {backup_path}")

            # Apply fix (write fixed code)
            fixed_code = fix_data.get("fixed_code", "")
            if not fixed_code:
                logger.error("No fixed code in fix_data")
                return False

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_code)

            logger.info(f"Fix applied to: {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to apply fix to {filepath}: {e}")
            return False


# Global fix generator instance
_fix_generator = None


def get_fix_generator() -> FixGenerator:
    """Get or create global fix generator instance."""
    global _fix_generator
    if _fix_generator is None:
        _fix_generator = FixGenerator()
    return _fix_generator


# Convenience functions
def generate_fix(code: str, vulnerability: Dict, filename: str) -> Dict:
    """
    Convenience function to generate a fix.

    Args:
        code: Source code
        vulnerability: Vulnerability details
        filename: File name

    Returns:
        Fix data dict
    """
    generator = get_fix_generator()
    return generator.generate_fix(code, vulnerability, filename)


def apply_fix_to_file(filepath: str, fix_data: Dict, backup: bool = True) -> bool:
    """
    Convenience function to apply a fix to a file.

    Args:
        filepath: Path to file
        fix_data: Fix data from generate_fix()
        backup: Create backup file

    Returns:
        True if successful
    """
    generator = get_fix_generator()
    return generator.apply_fix(filepath, fix_data, backup)
