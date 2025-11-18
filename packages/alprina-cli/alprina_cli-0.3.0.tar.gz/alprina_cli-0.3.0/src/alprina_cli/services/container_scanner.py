"""
Container Scanner - Docker image and Kubernetes security scanning.
Uses Trivy (Aqua Security) for comprehensive container vulnerability detection.
"""

import subprocess
import json
import os
from pathlib import Path
from typing import Dict, Optional, List
from loguru import logger


class ContainerScanner:
    """
    Scan Docker images and Kubernetes manifests for vulnerabilities.
    
    Uses Trivy for:
    - OS package vulnerabilities
    - Language-specific dependencies
    - Secrets in images
    - Misconfigurations
    - IaC security issues
    """

    def __init__(self):
        """Initialize container scanner."""
        self.has_trivy = self._check_trivy()
        if not self.has_trivy:
            logger.warning("Trivy not installed. Install for container scanning.")
            logger.info("Install: curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh")

    def _check_trivy(self) -> bool:
        """Check if Trivy is installed."""
        try:
            result = subprocess.run(
                ["trivy", "--version"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def scan_image(
        self,
        image: str,
        severity: List[str] = None,
        output_format: str = "json",
        include_secrets: bool = True
    ) -> Dict:
        """
        Scan a Docker image for vulnerabilities.

        Args:
            image: Docker image name (e.g., 'nginx:latest', 'myapp:1.0')
            severity: List of severities to report (CRITICAL, HIGH, MEDIUM, LOW)
            output_format: json, table, or sarif
            include_secrets: Whether to scan for secrets

        Returns:
            Dict with scan results and vulnerability summary
        """
        if not self.has_trivy:
            return self._install_guide()

        logger.info(f"Scanning Docker image: {image}")

        if severity is None:
            severity = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

        try:
            # Build Trivy command
            cmd = [
                "trivy", "image",
                "--format", output_format,
                "--severity", ",".join(severity),
                "--scanners", "vuln,secret" if include_secrets else "vuln",
                image
            ]

            # Run Trivy
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode != 0 and not result.stdout:
                logger.error(f"Trivy scan failed: {result.stderr}")
                return {
                    "success": False,
                    "error": result.stderr,
                    "image": image
                }

            # Parse results
            if output_format == "json":
                scan_data = json.loads(result.stdout) if result.stdout else {}
            else:
                scan_data = {"raw_output": result.stdout}

            # Analyze results
            summary = self._analyze_image_results(scan_data)

            logger.info(f"Scan complete. Found {summary['total_vulnerabilities']} vulnerabilities")

            return {
                "success": True,
                "image": image,
                "scan_type": "docker_image",
                "summary": summary,
                "scan_data": scan_data,
                "recommendations": self._generate_recommendations(summary, image)
            }

        except subprocess.TimeoutExpired:
            logger.error("Container scan timed out")
            return {
                "success": False,
                "error": "Scan timed out (>5 minutes)",
                "image": image
            }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Trivy output: {e}")
            return {
                "success": False,
                "error": f"Invalid JSON from Trivy: {e}",
                "image": image
            }
        except Exception as e:
            logger.error(f"Error scanning image: {e}")
            return {
                "success": False,
                "error": str(e),
                "image": image
            }

    def scan_kubernetes(
        self,
        manifest_path: str,
        severity: List[str] = None
    ) -> Dict:
        """
        Scan Kubernetes manifests for misconfigurations.

        Args:
            manifest_path: Path to K8s YAML file or directory
            severity: List of severities to report

        Returns:
            Dict with scan results
        """
        if not self.has_trivy:
            return self._install_guide()

        logger.info(f"Scanning Kubernetes manifest: {manifest_path}")

        if severity is None:
            severity = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

        try:
            # Build Trivy command
            cmd = [
                "trivy", "config",
                "--format", "json",
                "--severity", ",".join(severity),
                manifest_path
            ]

            # Run Trivy
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode != 0 and not result.stdout:
                logger.error(f"Trivy config scan failed: {result.stderr}")
                return {
                    "success": False,
                    "error": result.stderr,
                    "manifest": manifest_path
                }

            # Parse results
            scan_data = json.loads(result.stdout) if result.stdout else {}

            # Analyze results
            summary = self._analyze_config_results(scan_data)

            logger.info(f"K8s scan complete. Found {summary['total_misconfigurations']} issues")

            return {
                "success": True,
                "manifest": manifest_path,
                "scan_type": "kubernetes",
                "summary": summary,
                "scan_data": scan_data
            }

        except subprocess.TimeoutExpired:
            logger.error("Kubernetes scan timed out")
            return {
                "success": False,
                "error": "Scan timed out (>2 minutes)",
                "manifest": manifest_path
            }
        except Exception as e:
            logger.error(f"Error scanning Kubernetes manifest: {e}")
            return {
                "success": False,
                "error": str(e),
                "manifest": manifest_path
            }

    def scan_filesystem(
        self,
        path: str,
        severity: List[str] = None
    ) -> Dict:
        """
        Scan a filesystem or directory for vulnerabilities.

        Args:
            path: Path to scan
            severity: List of severities to report

        Returns:
            Dict with scan results
        """
        if not self.has_trivy:
            return self._install_guide()

        logger.info(f"Scanning filesystem: {path}")

        if severity is None:
            severity = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

        try:
            cmd = [
                "trivy", "fs",
                "--format", "json",
                "--severity", ",".join(severity),
                "--scanners", "vuln,secret,misconfig",
                path
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode != 0 and not result.stdout:
                return {
                    "success": False,
                    "error": result.stderr,
                    "path": path
                }

            scan_data = json.loads(result.stdout) if result.stdout else {}
            summary = self._analyze_filesystem_results(scan_data)

            return {
                "success": True,
                "path": path,
                "scan_type": "filesystem",
                "summary": summary,
                "scan_data": scan_data
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Scan timed out",
                "path": path
            }
        except Exception as e:
            logger.error(f"Error scanning filesystem: {e}")
            return {
                "success": False,
                "error": str(e),
                "path": path
            }

    def generate_sbom(
        self,
        image: str,
        output_file: Optional[str] = None
    ) -> Dict:
        """
        Generate SBOM for a container image.

        Args:
            image: Docker image name
            output_file: Output file path (optional)

        Returns:
            Dict with SBOM generation results
        """
        if not self.has_trivy:
            return self._install_guide()

        logger.info(f"Generating SBOM for image: {image}")

        try:
            cmd = [
                "trivy", "image",
                "--format", "cyclonedx",
                image
            ]

            if output_file:
                cmd.extend(["--output", output_file])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode != 0:
                return {
                    "success": False,
                    "error": result.stderr,
                    "image": image
                }

            sbom_data = result.stdout if not output_file else None

            return {
                "success": True,
                "image": image,
                "format": "CycloneDX",
                "output_file": output_file,
                "sbom_data": sbom_data
            }

        except Exception as e:
            logger.error(f"Error generating SBOM: {e}")
            return {
                "success": False,
                "error": str(e),
                "image": image
            }

    def _analyze_image_results(self, scan_data: Dict) -> Dict:
        """Analyze Trivy image scan results."""
        summary = {
            "total_vulnerabilities": 0,
            "by_severity": {
                "CRITICAL": 0,
                "HIGH": 0,
                "MEDIUM": 0,
                "LOW": 0,
                "UNKNOWN": 0
            },
            "secrets_found": 0,
            "packages_scanned": 0,
            "layers": 0
        }

        results = scan_data.get("Results", [])

        for result in results:
            # Count vulnerabilities
            vulnerabilities = result.get("Vulnerabilities", [])
            summary["total_vulnerabilities"] += len(vulnerabilities)

            for vuln in vulnerabilities:
                severity = vuln.get("Severity", "UNKNOWN")
                if severity in summary["by_severity"]:
                    summary["by_severity"][severity] += 1

            # Count secrets
            secrets = result.get("Secrets", [])
            summary["secrets_found"] += len(secrets)

            # Count packages
            if "Packages" in result:
                summary["packages_scanned"] += len(result["Packages"])

        # Get image metadata
        metadata = scan_data.get("Metadata", {})
        if "ImageConfig" in metadata:
            image_config = metadata["ImageConfig"]
            if "history" in image_config:
                summary["layers"] = len(image_config["history"])

        return summary

    def _analyze_config_results(self, scan_data: Dict) -> Dict:
        """Analyze Trivy config scan results."""
        summary = {
            "total_misconfigurations": 0,
            "by_severity": {
                "CRITICAL": 0,
                "HIGH": 0,
                "MEDIUM": 0,
                "LOW": 0
            },
            "files_scanned": 0
        }

        results = scan_data.get("Results", [])
        summary["files_scanned"] = len(results)

        for result in results:
            misconfigs = result.get("Misconfigurations", [])
            summary["total_misconfigurations"] += len(misconfigs)

            for misconfig in misconfigs:
                severity = misconfig.get("Severity", "UNKNOWN")
                if severity in summary["by_severity"]:
                    summary["by_severity"][severity] += 1

        return summary

    def _analyze_filesystem_results(self, scan_data: Dict) -> Dict:
        """Analyze Trivy filesystem scan results."""
        summary = {
            "total_vulnerabilities": 0,
            "total_secrets": 0,
            "total_misconfigurations": 0,
            "by_severity": {
                "CRITICAL": 0,
                "HIGH": 0,
                "MEDIUM": 0,
                "LOW": 0
            }
        }

        results = scan_data.get("Results", [])

        for result in results:
            # Vulnerabilities
            vulns = result.get("Vulnerabilities", [])
            summary["total_vulnerabilities"] += len(vulns)

            for vuln in vulns:
                severity = vuln.get("Severity", "UNKNOWN")
                if severity in summary["by_severity"]:
                    summary["by_severity"][severity] += 1

            # Secrets
            secrets = result.get("Secrets", [])
            summary["total_secrets"] += len(secrets)

            # Misconfigurations
            misconfigs = result.get("Misconfigurations", [])
            summary["total_misconfigurations"] += len(misconfigs)

        return summary

    def _generate_recommendations(self, summary: Dict, image: str) -> List[str]:
        """Generate recommendations based on scan results."""
        recommendations = []

        # Check for critical issues
        critical = summary["by_severity"].get("CRITICAL", 0)
        high = summary["by_severity"].get("HIGH", 0)

        if critical > 0:
            recommendations.append(
                f"🚨 URGENT: {critical} CRITICAL vulnerabilities found. Update image immediately."
            )

        if high > 0:
            recommendations.append(
                f"⚠️  {high} HIGH severity vulnerabilities. Plan updates within 1 week."
            )

        # Base image recommendations
        if ":" in image:
            base, tag = image.rsplit(":", 1)
            if tag == "latest":
                recommendations.append(
                    "💡 Avoid 'latest' tag. Use specific versions for reproducibility."
                )

        # Secrets found
        if summary.get("secrets_found", 0) > 0:
            recommendations.append(
                "🔐 Secrets detected in image. Remove hardcoded credentials immediately."
            )

        # General recommendations
        if summary["total_vulnerabilities"] > 50:
            recommendations.append(
                "📦 Consider using a minimal base image (alpine, distroless) to reduce attack surface."
            )

        if not recommendations:
            recommendations.append(
                "✅ No critical issues found. Continue monitoring for new vulnerabilities."
            )

        return recommendations

    def _install_guide(self) -> Dict:
        """Return installation guide for Trivy."""
        return {
            "success": False,
            "error": "Trivy not installed",
            "install_command": "curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh",
            "install_url": "https://github.com/aquasecurity/trivy",
            "description": "Trivy - comprehensive container security scanner by Aqua Security"
        }


# Global container scanner instance
_container_scanner = None


def get_container_scanner() -> ContainerScanner:
    """Get or create global container scanner instance."""
    global _container_scanner
    if _container_scanner is None:
        _container_scanner = ContainerScanner()
    return _container_scanner


# Convenience functions
def scan_docker_image(image: str, severity: List[str] = None) -> Dict:
    """
    Convenience function to scan a Docker image.

    Args:
        image: Docker image name
        severity: List of severities to report

    Returns:
        Dict with scan results
    """
    scanner = get_container_scanner()
    return scanner.scan_image(image, severity)


def scan_k8s_manifest(manifest_path: str) -> Dict:
    """
    Convenience function to scan Kubernetes manifest.

    Args:
        manifest_path: Path to K8s YAML

    Returns:
        Dict with scan results
    """
    scanner = get_container_scanner()
    return scanner.scan_kubernetes(manifest_path)
