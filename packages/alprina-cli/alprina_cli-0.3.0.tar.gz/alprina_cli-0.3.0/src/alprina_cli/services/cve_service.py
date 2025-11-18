"""
CVE/CWE/CVSS Service - Enriches findings with professional vulnerability references.
Integrates with NVD API 2.0 for CVE data and maps findings to CWE/OWASP.
"""

import os
from typing import Optional, Dict
from loguru import logger
import requests
from functools import lru_cache


class CVEService:
    """
    Service for enriching security findings with CVE/CWE/CVSS data.
    Uses NVD API 2.0 for CVE lookups and local mappings for CWE/OWASP.
    """

    NVD_API_BASE = "https://services.nvd.nist.gov/rest/json/cves/2.0"

    # CWE mappings for common vulnerability types
    CWE_MAPPINGS = {
        "SQL Injection": "CWE-89",
        "SQLi": "CWE-89",
        "sql_injection": "CWE-89",

        "XSS": "CWE-79",
        "Cross-Site Scripting": "CWE-79",
        "cross_site_scripting": "CWE-79",

        "Hardcoded Secret": "CWE-798",
        "Hardcoded Password": "CWE-798",
        "Hardcoded Credential": "CWE-798",
        "hardcoded_credential": "CWE-798",

        "Path Traversal": "CWE-22",
        "Directory Traversal": "CWE-22",
        "path_traversal": "CWE-22",

        "Command Injection": "CWE-78",
        "OS Command Injection": "CWE-78",
        "command_injection": "CWE-78",

        "XXE": "CWE-611",
        "XML External Entity": "CWE-611",

        "CSRF": "CWE-352",
        "Cross-Site Request Forgery": "CWE-352",

        "SSRF": "CWE-918",
        "Server-Side Request Forgery": "CWE-918",

        "Insecure Deserialization": "CWE-502",
        "deserialization": "CWE-502",

        "Authentication Bypass": "CWE-287",
        "Broken Authentication": "CWE-287",

        "Broken Access Control": "CWE-284",
        "Authorization Bypass": "CWE-284",

        "Sensitive Data Exposure": "CWE-200",
        "Information Disclosure": "CWE-200",

        "Security Misconfiguration": "CWE-16",
        "Insecure Configuration": "CWE-16",

        "Weak Cryptography": "CWE-327",
        "Insufficient Encryption": "CWE-327",

        "Debug Mode": "CWE-489",
        "Active Debug Code": "CWE-489",

        "Insecure Randomness": "CWE-330",
        "Weak Random": "CWE-330",

        "Race Condition": "CWE-362",
        "TOCTOU": "CWE-367",

        "Buffer Overflow": "CWE-120",
        "buffer_overflow": "CWE-120",

        "Integer Overflow": "CWE-190",
        "Numeric Error": "CWE-190",
    }

    # OWASP Top 10 2021 mappings
    OWASP_MAPPINGS = {
        "CWE-89": "A03:2021 – Injection",
        "CWE-79": "A03:2021 – Injection",
        "CWE-78": "A03:2021 – Injection",
        "CWE-611": "A05:2021 – Security Misconfiguration",

        "CWE-798": "A07:2021 – Identification and Authentication Failures",
        "CWE-287": "A07:2021 – Identification and Authentication Failures",
        "CWE-327": "A02:2021 – Cryptographic Failures",
        "CWE-330": "A02:2021 – Cryptographic Failures",

        "CWE-22": "A01:2021 – Broken Access Control",
        "CWE-352": "A01:2021 – Broken Access Control",
        "CWE-284": "A01:2021 – Broken Access Control",

        "CWE-918": "A10:2021 – Server-Side Request Forgery (SSRF)",

        "CWE-502": "A08:2021 – Software and Data Integrity Failures",

        "CWE-200": "A01:2021 – Broken Access Control",
        "CWE-16": "A05:2021 – Security Misconfiguration",
        "CWE-489": "A05:2021 – Security Misconfiguration",

        "CWE-120": "A03:2021 – Injection",
        "CWE-190": "A04:2021 – Insecure Design",
        "CWE-362": "A04:2021 – Insecure Design",
        "CWE-367": "A04:2021 – Insecure Design",
    }

    # CVSS score estimates for vulnerability types (when CVE not available)
    CVSS_ESTIMATES = {
        "SQL Injection": 9.8,
        "Command Injection": 9.8,
        "Authentication Bypass": 9.1,
        "Hardcoded Secret": 7.5,
        "Path Traversal": 7.5,
        "SSRF": 8.6,
        "XXE": 8.2,
        "XSS": 6.1,
        "CSRF": 6.5,
        "Insecure Deserialization": 8.1,
        "Weak Cryptography": 7.4,
        "Debug Mode": 5.3,
        "Information Disclosure": 5.3,
    }

    def __init__(self):
        """Initialize CVE service with optional API key."""
        self.api_key = os.getenv("NVD_API_KEY")
        if self.api_key:
            logger.info("NVD API key found - enhanced rate limits available")
        else:
            logger.debug("No NVD API key - using limited rate (5 req/30sec)")

    @lru_cache(maxsize=100)
    def get_cve_details(self, cve_id: str) -> Optional[Dict]:
        """
        Fetch CVE details from NVD API 2.0.

        Args:
            cve_id: CVE identifier (e.g., "CVE-2025-1234")

        Returns:
            Dict with CVE data or None if not found/error
        """
        try:
            headers = {}
            if self.api_key:
                headers["apiKey"] = self.api_key

            response = requests.get(
                self.NVD_API_BASE,
                params={"cveId": cve_id},
                headers=headers,
                timeout=5.0
            )

            if response.status_code == 200:
                data = response.json()
                return self._parse_cve_data(data)
            else:
                logger.warning(f"NVD API returned {response.status_code} for {cve_id}")
                return None

        except Exception as e:
            logger.debug(f"Could not fetch CVE {cve_id}: {e}")
            return None

    def _parse_cve_data(self, nvd_response: Dict) -> Optional[Dict]:
        """Parse NVD API response into simplified format."""
        try:
            vulnerabilities = nvd_response.get("vulnerabilities", [])
            if not vulnerabilities:
                return None

            vuln = vulnerabilities[0]
            cve = vuln.get("cve", {})

            # Extract CVSS score (try v3.1, v3.0, then v2.0)
            cvss_data = {}
            metrics = cve.get("metrics", {})

            if "cvssMetricV31" in metrics and metrics["cvssMetricV31"]:
                cvss_data = metrics["cvssMetricV31"][0]["cvssData"]
            elif "cvssMetricV30" in metrics and metrics["cvssMetricV30"]:
                cvss_data = metrics["cvssMetricV30"][0]["cvssData"]
            elif "cvssMetricV2" in metrics and metrics["cvssMetricV2"]:
                cvss_data = metrics["cvssMetricV2"][0]["cvssData"]

            # Extract CWE
            weaknesses = cve.get("weaknesses", [])
            cwe_id = None
            if weaknesses:
                descriptions = weaknesses[0].get("description", [])
                if descriptions:
                    cwe_id = descriptions[0].get("value")

            # Extract description
            descriptions = cve.get("descriptions", [])
            description = descriptions[0].get("value", "") if descriptions else ""

            return {
                "cve_id": cve.get("id"),
                "cvss_score": cvss_data.get("baseScore"),
                "cvss_severity": cvss_data.get("baseSeverity"),
                "cvss_vector": cvss_data.get("vectorString"),
                "cwe_id": cwe_id,
                "description": description,
                "url": f"https://nvd.nist.gov/vuln/detail/{cve.get('id')}"
            }

        except Exception as e:
            logger.error(f"Error parsing CVE data: {e}")
            return None

    def enrich_finding(self, finding: Dict) -> Dict:
        """
        Enrich a security finding with CVE/CWE/CVSS data.

        Args:
            finding: Original finding dict from scanner

        Returns:
            Enhanced finding with CVE/CWE/CVSS references
        """
        try:
            # Get vulnerability type
            vuln_type = finding.get("type", "")

            # Add CWE ID and URL
            cwe_id = self._get_cwe_for_type(vuln_type)
            if cwe_id:
                finding["cwe"] = cwe_id
                finding["cwe_name"] = self._get_cwe_name(cwe_id)
                finding["cwe_url"] = f"https://cwe.mitre.org/data/definitions/{cwe_id.split('-')[1]}.html"

                # Add OWASP Top 10 mapping
                owasp = self._get_owasp_mapping(cwe_id)
                if owasp:
                    finding["owasp"] = owasp
                    finding["owasp_url"] = "https://owasp.org/Top10/"

            # Add CVSS score estimate if not present
            if "cvss_score" not in finding:
                estimated_cvss = self._estimate_cvss(vuln_type, finding.get("severity", "MEDIUM"))
                if estimated_cvss:
                    finding["cvss_score"] = estimated_cvss
                    finding["cvss_severity"] = self._cvss_to_severity(estimated_cvss)

            # If finding has a specific CVE ID, fetch detailed data
            if "cve_id" in finding:
                cve_data = self.get_cve_details(finding["cve_id"])
                if cve_data:
                    finding.update(cve_data)

            # Add reference links
            finding["references"] = self._build_references(finding)

            return finding

        except Exception as e:
            logger.error(f"Error enriching finding: {e}")
            return finding

    def _get_cwe_for_type(self, vuln_type: str) -> Optional[str]:
        """Map vulnerability type to CWE ID."""
        # Try exact match first
        if vuln_type in self.CWE_MAPPINGS:
            return self.CWE_MAPPINGS[vuln_type]

        # Try case-insensitive partial match
        vuln_type_lower = vuln_type.lower()
        for key, value in self.CWE_MAPPINGS.items():
            if key.lower() in vuln_type_lower or vuln_type_lower in key.lower():
                return value

        return None

    def _get_cwe_name(self, cwe_id: str) -> str:
        """Get human-readable name for CWE ID."""
        cwe_names = {
            "CWE-89": "SQL Injection",
            "CWE-79": "Cross-site Scripting (XSS)",
            "CWE-798": "Use of Hard-coded Credentials",
            "CWE-22": "Path Traversal",
            "CWE-78": "OS Command Injection",
            "CWE-611": "XML External Entity (XXE)",
            "CWE-352": "Cross-Site Request Forgery (CSRF)",
            "CWE-918": "Server-Side Request Forgery (SSRF)",
            "CWE-502": "Insecure Deserialization",
            "CWE-287": "Improper Authentication",
            "CWE-284": "Improper Access Control",
            "CWE-200": "Information Exposure",
            "CWE-16": "Configuration Issues",
            "CWE-327": "Weak Cryptography",
            "CWE-489": "Active Debug Code",
            "CWE-330": "Insufficient Entropy",
            "CWE-362": "Race Condition",
            "CWE-120": "Buffer Overflow",
            "CWE-190": "Integer Overflow",
        }
        return cwe_names.get(cwe_id, cwe_id)

    def _get_owasp_mapping(self, cwe_id: str) -> Optional[str]:
        """Map CWE ID to OWASP Top 10 2021 category."""
        return self.OWASP_MAPPINGS.get(cwe_id)

    def _estimate_cvss(self, vuln_type: str, severity: str) -> Optional[float]:
        """
        Estimate CVSS score based on vulnerability type and severity.

        Args:
            vuln_type: Type of vulnerability
            severity: CRITICAL/HIGH/MEDIUM/LOW

        Returns:
            Estimated CVSS score (0.0-10.0)
        """
        # Try to get base estimate from vulnerability type
        base_score = None
        for key, score in self.CVSS_ESTIMATES.items():
            if key.lower() in vuln_type.lower():
                base_score = score
                break

        # If no type match, use severity
        if base_score is None:
            severity_scores = {
                "CRITICAL": 9.0,
                "HIGH": 7.5,
                "MEDIUM": 5.5,
                "LOW": 3.5,
                "INFO": 0.0
            }
            base_score = severity_scores.get(severity.upper(), 5.0)

        return base_score

    def _cvss_to_severity(self, cvss_score: float) -> str:
        """Convert CVSS score to severity rating."""
        if cvss_score >= 9.0:
            return "CRITICAL"
        elif cvss_score >= 7.0:
            return "HIGH"
        elif cvss_score >= 4.0:
            return "MEDIUM"
        elif cvss_score > 0.0:
            return "LOW"
        else:
            return "NONE"

    def _build_references(self, finding: Dict) -> list:
        """Build list of reference URLs for finding."""
        references = []

        # CWE reference
        if "cwe_url" in finding:
            references.append({
                "type": "CWE",
                "name": f"{finding.get('cwe', 'CWE')}: {finding.get('cwe_name', 'Weakness')}",
                "url": finding["cwe_url"]
            })

        # OWASP reference
        if "owasp_url" in finding:
            references.append({
                "type": "OWASP",
                "name": finding.get("owasp", "OWASP Top 10"),
                "url": finding["owasp_url"]
            })

        # CVE reference (if specific CVE)
        if "cve_id" in finding:
            references.append({
                "type": "CVE",
                "name": finding["cve_id"],
                "url": f"https://nvd.nist.gov/vuln/detail/{finding['cve_id']}"
            })
        else:
            # Generic NVD search
            references.append({
                "type": "NVD",
                "name": "CVE Database Search",
                "url": "https://nvd.nist.gov/vuln/search"
            })

        return references


# Global CVE service instance
_cve_service = None


def get_cve_service() -> CVEService:
    """Get or create global CVE service instance."""
    global _cve_service
    if _cve_service is None:
        _cve_service = CVEService()
    return _cve_service


# Convenience function for quick enrichment
def enrich_finding(finding: Dict) -> Dict:
    """
    Convenience function to enrich a finding with CVE/CWE/CVSS data.

    Args:
        finding: Finding dict from scanner

    Returns:
        Enriched finding with professional references
    """
    service = get_cve_service()
    return service.enrich_finding(finding)


# Batch enrichment
def enrich_findings(findings: list) -> list:
    """
    Enrich multiple findings with CVE/CWE/CVSS data.

    Args:
        findings: List of finding dicts

    Returns:
        List of enriched findings
    """
    service = get_cve_service()
    return [service.enrich_finding(f) for f in findings]
