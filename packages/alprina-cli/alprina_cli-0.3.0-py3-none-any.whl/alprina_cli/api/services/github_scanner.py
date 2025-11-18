"""
GitHub Scanner Service
Scans PR changes and push commits for security vulnerabilities.
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional
from loguru import logger
import uuid

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ...quick_scanner import quick_scan
from .github_service import GitHubService


class GitHubScanner:
    """Scanner for GitHub repository changes."""
    
    def __init__(self):
        self.github_service = GitHubService()
    
    async def scan_pr_changes(
        self,
        repo_full_name: str,
        pr_number: int,
        changed_files: List[Dict],
        base_sha: str,
        head_sha: str,
        access_token: str
    ) -> Dict:
        """
        Scan files changed in a pull request.
        
        Args:
            repo_full_name: Full repository name (owner/repo)
            pr_number: Pull request number
            changed_files: List of changed files from GitHub API
            base_sha: Base commit SHA
            head_sha: Head commit SHA
            access_token: GitHub access token
            
        Returns:
            Dict containing scan results and findings
        """
        scan_id = str(uuid.uuid4())
        findings = []
        files_scanned = 0
        
        logger.info(f"🔍 Scanning {len(changed_files)} files in PR #{pr_number}")
        
        # Filter for scannable files (code files only)
        scannable_files = self._filter_scannable_files(changed_files)
        
        for file_info in scannable_files:
            filename = file_info.get("filename")
            status = file_info.get("status")
            
            # Skip deleted files
            if status == "removed":
                continue
            
            # Get file content from head SHA
            file_content = await self.github_service.get_file_content(
                repo_full_name=repo_full_name,
                file_path=filename,
                ref=head_sha,
                access_token=access_token
            )
            
            if not file_content:
                continue
            
            # Create temporary file for scanning
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix=self._get_file_extension(filename), delete=False) as tmp:
                tmp.write(file_content)
                tmp_path = tmp.name
            
            try:
                # Run quick scan on file
                scan_result = quick_scan(tmp_path)
                
                files_scanned += 1
                
                # Add findings with file context
                for finding in scan_result.get("findings", []):
                    findings.append({
                        **finding,
                        "id": str(uuid.uuid4()),
                        "file": filename,
                        "pr_number": pr_number,
                        "is_new": True,  # All findings in PR are considered new
                        "language": self._detect_language(filename),
                        "fix_recommendation": self._get_fix_recommendation(finding["pattern"]),
                        "learn_more_url": self._get_learn_more_url(finding["pattern"]),
                        "risk": self._assess_risk(finding["severity"])
                    })
            finally:
                # Clean up temp file
                Path(tmp_path).unlink(missing_ok=True)
        
        # Calculate summary
        summary = {
            "critical": sum(1 for f in findings if f["severity"] == "critical"),
            "high": sum(1 for f in findings if f["severity"] == "high"),
            "medium": sum(1 for f in findings if f["severity"] == "medium"),
            "low": sum(1 for f in findings if f["severity"] == "low"),
        }
        
        logger.info(f"✅ Scan complete: {len(findings)} findings in {files_scanned} files")
        
        return {
            "scan_id": scan_id,
            "pr_number": pr_number,
            "repo_full_name": repo_full_name,
            "files_scanned": files_scanned,
            "findings": findings,
            "summary": summary,
            "scanned_at": logger._core.clock.now().isoformat(),
        }
    
    async def scan_push_changes(
        self,
        repo_full_name: str,
        changed_files: List[str],
        access_token: str
    ) -> Dict:
        """
        Scan files changed in a push to main branch.
        Similar to PR scan but without PR context.
        """
        scan_id = str(uuid.uuid4())
        findings = []
        files_scanned = 0
        
        logger.info(f"🔍 Scanning {len(changed_files)} files in push to {repo_full_name}")
        
        # Filter for code files
        scannable_files = [f for f in changed_files if self._is_code_file(f)]
        
        for filename in scannable_files:
            # Get file content
            file_content = await self.github_service.get_file_content(
                repo_full_name=repo_full_name,
                file_path=filename,
                ref="main",  # or master
                access_token=access_token
            )
            
            if not file_content:
                continue
            
            # Create temporary file for scanning
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix=self._get_file_extension(filename), delete=False) as tmp:
                tmp.write(file_content)
                tmp_path = tmp.name
            
            try:
                # Run quick scan
                scan_result = quick_scan(tmp_path)
                
                files_scanned += 1
                
                # Add findings
                for finding in scan_result.get("findings", []):
                    findings.append({
                        **finding,
                        "id": str(uuid.uuid4()),
                        "file": filename,
                        "language": self._detect_language(filename),
                        "fix_recommendation": self._get_fix_recommendation(finding["pattern"]),
                        "risk": self._assess_risk(finding["severity"])
                    })
            finally:
                Path(tmp_path).unlink(missing_ok=True)
        
        # Calculate summary
        summary = {
            "critical": sum(1 for f in findings if f["severity"] == "critical"),
            "high": sum(1 for f in findings if f["severity"] == "high"),
            "medium": sum(1 for f in findings if f["severity"] == "medium"),
            "low": sum(1 for f in findings if f["severity"] == "low"),
        }
        
        return {
            "scan_id": scan_id,
            "repo_full_name": repo_full_name,
            "files_scanned": files_scanned,
            "findings": findings,
            "summary": summary
        }
    
    def _filter_scannable_files(self, changed_files: List[Dict]) -> List[Dict]:
        """Filter for scannable code files."""
        scannable = []
        for file_info in changed_files:
            filename = file_info.get("filename", "")
            if self._is_code_file(filename):
                scannable.append(file_info)
        return scannable
    
    def _is_code_file(self, filename: str) -> bool:
        """Check if file is a code file we can scan."""
        code_extensions = {
            '.py', '.js', '.ts', '.tsx', '.jsx',
            '.java', '.php', '.rb', '.go', '.rs',
            '.c', '.cpp', '.cs', '.swift', '.kt'
        }
        ext = Path(filename).suffix.lower()
        return ext in code_extensions
    
    def _get_file_extension(self, filename: str) -> str:
        """Get file extension for temporary file."""
        return Path(filename).suffix or '.txt'
    
    def _detect_language(self, filename: str) -> str:
        """Detect programming language from filename."""
        ext_to_lang = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.jsx': 'javascript',
            '.java': 'java',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.c': 'c',
            '.cpp': 'cpp',
            '.cs': 'csharp',
            '.swift': 'swift',
            '.kt': 'kotlin'
        }
        ext = Path(filename).suffix.lower()
        return ext_to_lang.get(ext, 'text')
    
    def _get_fix_recommendation(self, pattern: str) -> str:
        """Get fix recommendation for vulnerability pattern."""
        recommendations = {
            "sql_injection": "Use parameterized queries or an ORM to prevent SQL injection",
            "hardcoded_secrets": "Store secrets in environment variables, never in code",
            "xss_vulnerability": "Sanitize all user input before rendering in HTML",
            "command_injection": "Avoid shell=True, use subprocess with argument lists",
            "path_traversal": "Validate and sanitize all file paths before use",
            "weak_crypto": "Use modern algorithms like SHA-256 or bcrypt for hashing",
            "insecure_random": "Use secrets module for cryptographic random numbers",
            "missing_auth": "Add authentication middleware to protect sensitive endpoints",
            "debug_enabled": "Disable debug mode in production environments",
            "exposed_endpoints": "Add authorization checks to admin/internal endpoints"
        }
        return recommendations.get(pattern, "Review and remediate this vulnerability")
    
    def _get_learn_more_url(self, pattern: str) -> str:
        """Get learning resource URL for vulnerability."""
        urls = {
            "sql_injection": "https://owasp.org/www-community/attacks/SQL_Injection",
            "xss_vulnerability": "https://owasp.org/www-community/attacks/xss/",
            "command_injection": "https://owasp.org/www-community/attacks/Command_Injection",
            "hardcoded_secrets": "https://owasp.org/www-community/vulnerabilities/Use_of_hard-coded_password",
            "path_traversal": "https://owasp.org/www-community/attacks/Path_Traversal",
        }
        return urls.get(pattern, "https://owasp.org/www-project-top-ten/")
    
    def _assess_risk(self, severity: str) -> str:
        """Assess exploitability risk."""
        risk_mapping = {
            "critical": "High - Easily exploitable",
            "high": "Moderate - Exploitable with effort",
            "medium": "Low - Requires specific conditions",
            "low": "Minimal - Hard to exploit"
        }
        return risk_mapping.get(severity, "Unknown")
