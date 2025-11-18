"""
GitHub API Service
Handles GitHub API interactions, authentication, and PR comments.
"""

import os
import jwt
import time
import httpx
from typing import Optional, List, Dict
from loguru import logger
from datetime import datetime, timedelta


class GitHubService:
    """Service for interacting with GitHub API."""
    
    def __init__(self):
        self.app_id = os.getenv("GITHUB_APP_ID")
        self.private_key = os.getenv("GITHUB_PRIVATE_KEY", "").replace("\\n", "\n")
        self.base_url = "https://api.github.com"
        self._installation_tokens = {}  # Cache tokens
        
    def _generate_jwt(self) -> str:
        """Generate JWT for GitHub App authentication."""
        now = int(time.time())
        payload = {
            "iat": now,
            "exp": now + (10 * 60),  # 10 minutes
            "iss": self.app_id
        }
        
        return jwt.encode(payload, self.private_key, algorithm="RS256")
    
    async def get_installation_token(self, installation_id: int) -> str:
        """
        Get access token for a GitHub App installation.
        Caches tokens and refreshes when expired.
        """
        # Check cache
        if installation_id in self._installation_tokens:
            token_data = self._installation_tokens[installation_id]
            if datetime.utcnow() < token_data["expires_at"]:
                return token_data["token"]
        
        # Generate new token
        jwt_token = self._generate_jwt()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/app/installations/{installation_id}/access_tokens",
                headers={
                    "Authorization": f"Bearer {jwt_token}",
                    "Accept": "application/vnd.github+json"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            # Cache token
            self._installation_tokens[installation_id] = {
                "token": data["token"],
                "expires_at": datetime.fromisoformat(data["expires_at"].replace("Z", "+00:00"))
            }
            
            return data["token"]
    
    async def get_pr_changed_files(
        self,
        repo_full_name: str,
        pr_number: int,
        access_token: str
    ) -> List[Dict]:
        """Get list of files changed in a pull request."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/repos/{repo_full_name}/pulls/{pr_number}/files",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json"
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def get_file_content(
        self,
        repo_full_name: str,
        file_path: str,
        ref: str,
        access_token: str
    ) -> Optional[str]:
        """Get content of a file from repository."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/repos/{repo_full_name}/contents/{file_path}",
                    params={"ref": ref},
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/vnd.github.raw"
                    }
                )
                response.raise_for_status()
                return response.text
        except Exception as e:
            logger.error(f"Error fetching file {file_path}: {e}")
            return None
    
    async def post_pr_comment(
        self,
        repo_full_name: str,
        pr_number: int,
        scan_results: Dict,
        access_token: str
    ):
        """Post security scan results as PR comment."""
        comment_body = self._format_pr_comment(scan_results)
        
        # Check if we already posted a comment (to update instead of duplicate)
        existing_comment_id = await self._find_existing_comment(
            repo_full_name, pr_number, access_token
        )
        
        async with httpx.AsyncClient() as client:
            if existing_comment_id:
                # Update existing comment
                response = await client.patch(
                    f"{self.base_url}/repos/{repo_full_name}/issues/comments/{existing_comment_id}",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/vnd.github+json"
                    },
                    json={"body": comment_body}
                )
            else:
                # Create new comment
                response = await client.post(
                    f"{self.base_url}/repos/{repo_full_name}/issues/{pr_number}/comments",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/vnd.github+json"
                    },
                    json={"body": comment_body}
                )
            
            response.raise_for_status()
            logger.info(f"✅ Posted comment on PR #{pr_number}")
    
    async def _find_existing_comment(
        self,
        repo_full_name: str,
        pr_number: int,
        access_token: str
    ) -> Optional[int]:
        """Find existing Alprina comment on PR."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/repos/{repo_full_name}/issues/{pr_number}/comments",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/vnd.github+json"
                    }
                )
                response.raise_for_status()
                comments = response.json()
                
                # Look for comment containing our marker
                for comment in comments:
                    if "<!-- alprina-security-scan -->" in comment["body"]:
                        return comment["id"]
                        
                return None
        except Exception as e:
            logger.error(f"Error finding existing comment: {e}")
            return None
    
    def _format_pr_comment(self, scan_results: Dict) -> str:
        """Format scan results as beautiful GitHub markdown comment."""
        findings = scan_results.get("findings", [])
        new_findings = [f for f in findings if f.get("is_new", True)]
        critical = [f for f in new_findings if f["severity"] == "critical"]
        high = [f for f in new_findings if f["severity"] == "high"]
        medium = [f for f in new_findings if f["severity"] == "medium"]
        
        # Determine overall status
        if critical:
            status_emoji = "🚨"
            status_text = f"{len(critical)} critical issue{'s' if len(critical) != 1 else ''} found"
            status_color = "🔴"
        elif high:
            status_emoji = "⚠️"
            status_text = f"{len(high)} high severity issue{'s' if len(high) != 1 else ''} found"
            status_color = "🟠"
        elif medium:
            status_emoji = "ℹ️"
            status_text = f"{len(medium)} medium severity issue{'s' if len(medium) != 1 else ''} found"
            status_color = "🟡"
        else:
            status_emoji = "✅"
            status_text = "No new vulnerabilities introduced"
            status_color = "🟢"
        
        # Build comment
        comment = f"""<!-- alprina-security-scan -->
## {status_emoji} Alprina Security Scan

{status_color} **{status_text}**

"""
        
        # Add summary if there are findings
        if new_findings:
            total_findings = scan_results.get("summary", {})
            comment += f"""
### 📊 Security Impact
- 🚨 Critical: {total_findings.get('critical', 0)} 
- ⚠️ High: {total_findings.get('high', 0)}
- ℹ️ Medium: {total_findings.get('medium', 0)}
- ✓ Low: {total_findings.get('low', 0)}

"""
        
        # Show top 3 critical/high findings
        top_findings = (critical + high)[:3]
        if top_findings:
            comment += "### 🔍 Top Issues\n\n"
            
            for i, finding in enumerate(top_findings, 1):
                severity_emoji = "🚨" if finding["severity"] == "critical" else "⚠️"
                comment += f"""
<details>
<summary>{severity_emoji} <strong>{finding['title']}</strong> in <code>{finding['file']}</code>:{finding['line']}</summary>

**Severity:** {finding['severity'].upper()}  
**Risk:** {finding.get('risk', 'High')}

**Vulnerable Code:**
```{finding.get('language', 'python')}
{finding.get('code_snippet', 'N/A')}
```

**Why This is Dangerous:**  
{finding.get('description', 'Security vulnerability detected')}

**How to Fix:**  
{finding.get('fix_recommendation', 'Review and remediate this vulnerability')}

[📖 Learn More]({finding.get('learn_more_url', '#')}) | [🔧 View Full Report](https://alprina.com/dashboard/findings/{finding.get('id', '')})

</details>

"""
        
        # Add footer
        if new_findings:
            comment += f"\n---\n"
            comment += f"**{len(new_findings)} new issue{'s' if len(new_findings) != 1 else ''} found in this PR**  \n"
            comment += f"[📊 View Full Report](https://alprina.com/dashboard/scans/{scan_results.get('scan_id', '')}) | "
            comment += f"[🛡️ Dashboard](https://alprina.com/dashboard) | "
            comment += f"[📚 Docs](https://docs.alprina.com)\n\n"
        else:
            comment += f"\n---\n"
            comment += f"✅ **Great work!** No new security issues detected in this PR.\n\n"
        
        comment += f"<sub>Powered by [Alprina](https://alprina.com) • [Configure](https://alprina.com/dashboard/settings/github)</sub>"
        
        return comment
    
    async def create_check_run(
        self,
        repo_full_name: str,
        head_sha: str,
        scan_results: Dict,
        access_token: str
    ):
        """Create GitHub check run with scan results."""
        findings = scan_results.get("findings", [])
        critical = [f for f in findings if f["severity"] == "critical"]
        high = [f for f in findings if f["severity"] == "high"]
        
        # Determine check status
        if critical:
            conclusion = "failure"
            title = f"🚨 {len(critical)} critical security issue{'s' if len(critical) != 1 else ''} found"
        elif high:
            conclusion = "neutral"  # Warning but don't fail
            title = f"⚠️ {len(high)} high severity issue{'s' if len(high) != 1 else ''} found"
        else:
            conclusion = "success"
            title = "✅ No critical security issues found"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/repos/{repo_full_name}/check-runs",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json"
                },
                json={
                    "name": "Alprina Security Scan",
                    "head_sha": head_sha,
                    "status": "completed",
                    "conclusion": conclusion,
                    "output": {
                        "title": title,
                        "summary": f"Scanned {scan_results.get('files_scanned', 0)} files",
                        "text": self._format_check_output(scan_results)
                    }
                }
            )
            response.raise_for_status()
            logger.info(f"✅ Created check run for {head_sha}")
    
    def _format_check_output(self, scan_results: Dict) -> str:
        """Format scan results for check run output."""
        findings = scan_results.get("findings", [])
        if not findings:
            return "No security vulnerabilities detected. Great job! 🎉"
        
        output = "## Security Issues Found\n\n"
        for finding in findings[:10]:  # Show max 10
            output += f"- **{finding['title']}** in `{finding['file']}`:{finding['line']}\n"
        
        if len(findings) > 10:
            output += f"\n... and {len(findings) - 10} more\n"
        
        output += f"\n[View full report](https://alprina.com/dashboard/scans/{scan_results.get('scan_id', '')})"
        
        return output
