"""
Alprina services package.
Contains utility services for CVE/CWE/CVSS enrichment, AI fix generation, SBOM, and container scanning.
"""

from .cve_service import CVEService, get_cve_service, enrich_finding, enrich_findings
from .fix_generator import FixGenerator, get_fix_generator, generate_fix, apply_fix_to_file
from .sbom_generator import SBOMGenerator, get_sbom_generator, generate_sbom
from .container_scanner import ContainerScanner, get_container_scanner, scan_docker_image, scan_k8s_manifest

__all__ = [
    "CVEService",
    "get_cve_service",
    "enrich_finding",
    "enrich_findings",
    "FixGenerator",
    "get_fix_generator",
    "generate_fix",
    "apply_fix_to_file",
    "SBOMGenerator",
    "get_sbom_generator",
    "generate_sbom",
    "ContainerScanner",
    "get_container_scanner",
    "scan_docker_image",
    "scan_k8s_manifest",
]
