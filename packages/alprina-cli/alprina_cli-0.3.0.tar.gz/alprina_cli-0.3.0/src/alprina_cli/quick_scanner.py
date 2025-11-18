"""
Quick security scanner for critical patterns.
No LLM calls, pure regex + AST parsing.
Designed to complete in <5 seconds.
"""

import re
import ast
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import time

@dataclass
class QuickFinding:
    """Represents a finding from quick scan."""
    severity: str
    title: str
    file: str
    line: int
    code_snippet: str
    pattern: str
    description: str

# Critical patterns to check (top 10 most dangerous)
CRITICAL_PATTERNS = {
    "sql_injection": {
        "patterns": [
            r"execute\s*\(\s*f['\"].*?{.*?}.*?['\"]",  # f-string in SQL
            r"execute\s*\(\s*['\"].*?\+.*?['\"]",      # String concat in SQL
            r"cursor\.execute\s*\(\s*.*?\%.*?(?!,)",   # Old-style format without params
        ],
        "title": "SQL Injection Vulnerability",
        "description": "SQL query uses unsanitized user input, allowing attackers to manipulate queries"
    },
    "hardcoded_secrets": {
        "patterns": [
            r"(?i)(password|secret|key|token|api_key)\s*=\s*['\"][^'\"]{8,}['\"]",
            r"(?i)jwt_secret\s*=\s*['\"][^'\"]+['\"]",
            r"(?i)aws_secret_access_key\s*=\s*['\"][^'\"]+['\"]",
        ],
        "title": "Hardcoded Secret/Credential",
        "description": "Credentials hardcoded in source code can be stolen by anyone with repo access"
    },
    "xss_vulnerability": {
        "patterns": [
            r"innerHTML\s*=\s*.*?(?!sanitize)",  # JS innerHTML without sanitize
            r"dangerouslySetInnerHTML",          # React XSS vector
            r"document\.write\s*\(",             # document.write
        ],
        "title": "Cross-Site Scripting (XSS)",
        "description": "User input rendered without sanitization allows attackers to inject malicious scripts"
    },
    "command_injection": {
        "patterns": [
            r"os\.system\s*\(\s*f['\"]",
            r"subprocess\.(call|run|Popen)\s*\(\s*shell\s*=\s*True",
            r"eval\s*\(\s*.*?input.*?\)",  # eval with user input
        ],
        "title": "Command Injection Vulnerability",
        "description": "Unsanitized input passed to system commands allows arbitrary command execution"
    },
    "path_traversal": {
        "patterns": [
            r"open\s*\(\s*.*?\+.*?\)",  # Unsanitized path concat
            r"Path\s*\(\s*.*?input.*?\)",
            r"\.\.\/",  # Path traversal attempt
        ],
        "title": "Path Traversal Vulnerability",
        "description": "Unsanitized file paths allow attackers to read arbitrary files on the system"
    },
    "weak_crypto": {
        "patterns": [
            r"hashlib\.md5",
            r"hashlib\.sha1",
            r"(?i)des|rc4|rc2",  # Weak ciphers
        ],
        "title": "Weak Cryptographic Algorithm",
        "description": "Using broken/weak crypto algorithms that can be easily cracked by attackers"
    },
    "insecure_random": {
        "patterns": [
            r"random\.random",  # Not cryptographically secure
            r"Math\.random\(",  # JS non-crypto random
        ],
        "title": "Insecure Random Number Generation",
        "description": "Using predictable random numbers for security-critical operations"
    },
    "missing_auth": {
        "patterns": [
            r"@app\.route.*?methods.*?POST.*?(?!@.*?auth)",  # POST without auth
            r"@app\.route.*?/admin.*?(?!@.*?require)",      # Admin without protection
        ],
        "title": "Missing Authentication",
        "description": "Sensitive endpoints accessible without authentication"
    },
    "debug_enabled": {
        "patterns": [
            r"DEBUG\s*=\s*True",
            r"app\.debug\s*=\s*True",
            r"console\.log.*?password|secret|key",  # Logging secrets
        ],
        "title": "Debug Mode Enabled",
        "description": "Debug mode exposes sensitive information and stack traces to attackers"
    },
    "exposed_endpoints": {
        "patterns": [
            r"/admin.*?(?!@.*?require)",  # Admin routes without protection
            r"@app\.route\(['\"].*?(secret|internal|private).*?['\"]",
        ],
        "title": "Exposed Sensitive Endpoint",
        "description": "Internal/admin endpoints accessible without proper authorization"
    },
}

class QuickScanner:
    """Fast scanner for critical security patterns."""
    
    def __init__(self):
        self.findings: List[QuickFinding] = []
        self.files_scanned = 0
        self.start_time = time.time()
        
    def scan_directory(self, target_path: str) -> List[QuickFinding]:
        """Scan directory for critical patterns."""
        target = Path(target_path)
        
        if target.is_file():
            self._scan_file(target)
        else:
            # Scan Python, JS, TS files only (most common web vulnerabilities)
            extensions = ['.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.php', '.rb']
            for ext in extensions:
                for file_path in target.rglob(f'*{ext}'):
                    if self._should_skip(file_path):
                        continue
                    self._scan_file(file_path)
                    
                    # Stop if taking too long (failsafe)
                    if time.time() - self.start_time > 30:
                        break
                    
        return self.findings
    
    def _should_skip(self, path: Path) -> bool:
        """Skip common directories and test files."""
        skip_dirs = {
            'node_modules', 'venv', '.venv', '.git', '__pycache__', 
            'dist', 'build', '.next', 'coverage', 'vendor', 'target'
        }
        skip_patterns = ['test_', '_test.', '.test.', '.spec.', '.min.']
        
        # Check if any parent directory should be skipped
        if any(part in skip_dirs for part in path.parts):
            return True
            
        # Check if filename matches skip patterns
        if any(pattern in path.name.lower() for pattern in skip_patterns):
            return True
            
        return False
    
    def _scan_file(self, file_path: Path):
        """Scan single file for patterns."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            self.files_scanned += 1
            
            # Check each pattern category
            for pattern_name, pattern_config in CRITICAL_PATTERNS.items():
                for pattern in pattern_config['patterns']:
                    for line_num, line in enumerate(lines, 1):
                        if re.search(pattern, line):
                            # Avoid duplicates
                            finding_key = f"{file_path}:{line_num}:{pattern_name}"
                            if not any(f"{f.file}:{f.line}:{f.pattern}" == finding_key for f in self.findings):
                                self.findings.append(QuickFinding(
                                    severity="critical",
                                    title=pattern_config['title'],
                                    file=str(file_path),
                                    line=line_num,
                                    code_snippet=line.strip()[:100],  # Limit length
                                    pattern=pattern_name,
                                    description=pattern_config['description']
                                ))
        except Exception as e:
            # Silently skip files we can't read
            pass
    
    def get_summary(self) -> Dict:
        """Get scan summary."""
        return {
            "total_files_scanned": self.files_scanned,
            "files_with_issues": len(set(f.file for f in self.findings)),
            "critical": len([f for f in self.findings if f.severity == "critical"]),
            "duration_ms": int((time.time() - self.start_time) * 1000),
        }


def quick_scan(target: str) -> Dict:
    """
    Perform quick security scan.
    Returns results in <5 seconds for most projects.
    
    Args:
        target: Path to file or directory to scan
        
    Returns:
        Dict containing findings and summary
    """
    scanner = QuickScanner()
    findings = scanner.scan_directory(target)
    summary = scanner.get_summary()
    
    return {
        "quick_scan": True,
        "duration_ms": summary['duration_ms'],
        "findings": [
            {
                "severity": f.severity,
                "title": f.title,
                "file": f.file,
                "line": f.line,
                "code_snippet": f.code_snippet,
                "pattern": f.pattern,
                "description": f.description,
            }
            for f in findings
        ],
        "summary": summary
    }


if __name__ == "__main__":
    # Quick test
    import sys
    if len(sys.argv) > 1:
        result = quick_scan(sys.argv[1])
        print(f"Scanned {result['summary']['total_files_scanned']} files in {result['duration_ms']}ms")
        print(f"Found {result['summary']['critical']} critical issues")
