"""
SBOM Generator - Software Bill of Materials generation.
Supports CycloneDX (security-focused) and SPDX (compliance-focused) formats.
"""

import subprocess
import json
import os
from pathlib import Path
from typing import Dict, Optional, List
from loguru import logger


class SBOMGenerator:
    """
    Generate Software Bill of Materials in multiple formats.
    
    Supports:
    - CycloneDX 1.5 (OWASP, security-focused)
    - SPDX 2.3 (ISO/IEC 5962:2021, compliance-focused)
    """

    def __init__(self):
        """Initialize SBOM generator."""
        self._check_tools()

    def _check_tools(self):
        """Check if required tools are installed."""
        self.has_cdxgen = self._check_command("cdxgen")
        self.has_syft = self._check_command("syft")
        
        if not self.has_cdxgen and not self.has_syft:
            logger.warning("No SBOM tools found. Install cdxgen or syft for SBOM generation")
            logger.info("Install cdxgen: npm install -g @cyclonedx/cdxgen")
            logger.info("Install syft: curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh")

    def _check_command(self, command: str) -> bool:
        """Check if a command is available."""
        try:
            result = subprocess.run(
                ["which", command],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False

    def generate_cyclonedx(
        self,
        project_path: str,
        output_path: Optional[str] = None,
        output_format: str = "json"
    ) -> Dict:
        """
        Generate CycloneDX SBOM (security-focused).

        Args:
            project_path: Path to project directory
            output_path: Output file path (optional)
            output_format: json or xml

        Returns:
            Dict with SBOM data and metadata
        """
        if not self.has_cdxgen:
            return self._install_guide_cyclonedx()

        project_path = Path(project_path).resolve()
        
        if output_path is None:
            output_path = project_path / f"sbom-cyclonedx.{output_format}"
        
        logger.info(f"Generating CycloneDX SBOM for: {project_path}")
        
        try:
            # Build cdxgen command
            cmd = [
                "cdxgen",
                str(project_path),
                "--output", str(output_path),
                "--spec-version", "1.5"
            ]
            
            if output_format == "xml":
                cmd.append("--output-format")
                cmd.append("xml")
            
            # Run cdxgen
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                logger.error(f"cdxgen failed: {result.stderr}")
                return {
                    "success": False,
                    "error": result.stderr,
                    "tool": "cdxgen"
                }
            
            # Read generated SBOM
            sbom_data = self._read_sbom(output_path, output_format)
            
            # Extract summary
            summary = self._analyze_cyclonedx(sbom_data)
            
            logger.info(f"CycloneDX SBOM generated: {output_path}")
            
            return {
                "success": True,
                "format": "CycloneDX",
                "version": "1.5",
                "output_file": str(output_path),
                "output_format": output_format,
                "summary": summary,
                "sbom_data": sbom_data
            }
            
        except subprocess.TimeoutExpired:
            logger.error("SBOM generation timed out")
            return {
                "success": False,
                "error": "Generation timed out (>5 minutes)",
                "tool": "cdxgen"
            }
        except Exception as e:
            logger.error(f"Error generating CycloneDX SBOM: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "cdxgen"
            }

    def generate_spdx(
        self,
        project_path: str,
        output_path: Optional[str] = None,
        output_format: str = "json"
    ) -> Dict:
        """
        Generate SPDX SBOM (compliance-focused, ISO standard).

        Args:
            project_path: Path to project directory
            output_path: Output file path (optional)
            output_format: json, yaml, or tag-value

        Returns:
            Dict with SBOM data and metadata
        """
        if not self.has_syft:
            return self._install_guide_spdx()

        project_path = Path(project_path).resolve()
        
        if output_path is None:
            ext = "json" if output_format == "json" else "spdx"
            output_path = project_path / f"sbom-spdx.{ext}"
        
        logger.info(f"Generating SPDX SBOM for: {project_path}")
        
        try:
            # Build syft command
            format_map = {
                "json": "spdx-json",
                "yaml": "spdx",
                "tag-value": "spdx-tag-value"
            }
            
            syft_format = format_map.get(output_format, "spdx-json")
            
            cmd = [
                "syft",
                f"dir:{project_path}",
                "--output", f"{syft_format}={output_path}"
            ]
            
            # Run syft
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                logger.error(f"syft failed: {result.stderr}")
                return {
                    "success": False,
                    "error": result.stderr,
                    "tool": "syft"
                }
            
            # Read generated SBOM
            sbom_data = self._read_sbom(output_path, output_format)
            
            # Extract summary
            summary = self._analyze_spdx(sbom_data)
            
            logger.info(f"SPDX SBOM generated: {output_path}")
            
            return {
                "success": True,
                "format": "SPDX",
                "version": "2.3",
                "output_file": str(output_path),
                "output_format": output_format,
                "summary": summary,
                "sbom_data": sbom_data,
                "iso_standard": "ISO/IEC 5962:2021"
            }
            
        except subprocess.TimeoutExpired:
            logger.error("SBOM generation timed out")
            return {
                "success": False,
                "error": "Generation timed out (>5 minutes)",
                "tool": "syft"
            }
        except Exception as e:
            logger.error(f"Error generating SPDX SBOM: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": "syft"
            }

    def generate_both(
        self,
        project_path: str,
        output_dir: Optional[str] = None
    ) -> Dict:
        """
        Generate both CycloneDX and SPDX SBOMs.

        Args:
            project_path: Path to project directory
            output_dir: Output directory (optional)

        Returns:
            Dict with results for both formats
        """
        project_path = Path(project_path).resolve()
        
        if output_dir is None:
            output_dir = project_path
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Generating both CycloneDX and SPDX SBOMs...")
        
        results = {
            "success": True,
            "formats": []
        }
        
        # Generate CycloneDX
        if self.has_cdxgen:
            cyclonedx_output = output_dir / "sbom-cyclonedx.json"
            cyclonedx_result = self.generate_cyclonedx(
                project_path,
                str(cyclonedx_output)
            )
            results["formats"].append(cyclonedx_result)
            if not cyclonedx_result["success"]:
                results["success"] = False
        else:
            logger.warning("Skipping CycloneDX (cdxgen not installed)")
            results["formats"].append({
                "success": False,
                "format": "CycloneDX",
                "error": "cdxgen not installed"
            })
        
        # Generate SPDX
        if self.has_syft:
            spdx_output = output_dir / "sbom-spdx.json"
            spdx_result = self.generate_spdx(
                project_path,
                str(spdx_output)
            )
            results["formats"].append(spdx_result)
            if not spdx_result["success"]:
                results["success"] = False
        else:
            logger.warning("Skipping SPDX (syft not installed)")
            results["formats"].append({
                "success": False,
                "format": "SPDX",
                "error": "syft not installed"
            })
        
        return results

    def _read_sbom(self, file_path: str, format: str) -> Dict:
        """Read SBOM file and return data."""
        try:
            if format == "json":
                with open(file_path, 'r') as f:
                    return json.load(f)
            else:
                # For XML/YAML, just return file path
                return {"file": str(file_path)}
        except Exception as e:
            logger.error(f"Error reading SBOM file: {e}")
            return {}

    def _analyze_cyclonedx(self, sbom_data: Dict) -> Dict:
        """Analyze CycloneDX SBOM and extract summary."""
        summary = {
            "total_components": 0,
            "direct_dependencies": 0,
            "transitive_dependencies": 0,
            "vulnerabilities": 0,
            "licenses": set()
        }
        
        if not sbom_data:
            return summary
        
        components = sbom_data.get("components", [])
        summary["total_components"] = len(components)
        
        # Count dependencies
        dependencies = sbom_data.get("dependencies", [])
        for dep in dependencies:
            if dep.get("dependsOn"):
                summary["direct_dependencies"] += 1
            else:
                summary["transitive_dependencies"] += 1
        
        # Count vulnerabilities
        if "vulnerabilities" in sbom_data:
            summary["vulnerabilities"] = len(sbom_data["vulnerabilities"])
        
        # Collect licenses
        for component in components:
            licenses = component.get("licenses", [])
            for lic in licenses:
                if "license" in lic:
                    lic_data = lic["license"]
                    if "id" in lic_data:
                        summary["licenses"].add(lic_data["id"])
                    elif "name" in lic_data:
                        summary["licenses"].add(lic_data["name"])
        
        summary["licenses"] = list(summary["licenses"])
        summary["unique_licenses"] = len(summary["licenses"])
        
        return summary

    def _analyze_spdx(self, sbom_data: Dict) -> Dict:
        """Analyze SPDX SBOM and extract summary."""
        summary = {
            "total_packages": 0,
            "files_analyzed": 0,
            "licenses": set(),
            "relationships": 0
        }
        
        if not sbom_data:
            return summary
        
        packages = sbom_data.get("packages", [])
        summary["total_packages"] = len(packages)
        
        # Count files
        files = sbom_data.get("files", [])
        summary["files_analyzed"] = len(files)
        
        # Count relationships
        relationships = sbom_data.get("relationships", [])
        summary["relationships"] = len(relationships)
        
        # Collect licenses
        for package in packages:
            lic_concluded = package.get("licenseConcluded")
            if lic_concluded and lic_concluded != "NOASSERTION":
                summary["licenses"].add(lic_concluded)
            
            lic_declared = package.get("licenseDeclared")
            if lic_declared and lic_declared != "NOASSERTION":
                summary["licenses"].add(lic_declared)
        
        summary["licenses"] = list(summary["licenses"])
        summary["unique_licenses"] = len(summary["licenses"])
        
        return summary

    def _install_guide_cyclonedx(self) -> Dict:
        """Return installation guide for CycloneDX tools."""
        return {
            "success": False,
            "error": "cdxgen not installed",
            "install_command": "npm install -g @cyclonedx/cdxgen",
            "install_url": "https://github.com/CycloneDX/cdxgen",
            "description": "CycloneDX generator for OWASP security-focused SBOMs"
        }

    def _install_guide_spdx(self) -> Dict:
        """Return installation guide for SPDX tools."""
        return {
            "success": False,
            "error": "syft not installed",
            "install_command": "curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh",
            "install_url": "https://github.com/anchore/syft",
            "description": "Syft for ISO-standard SPDX SBOMs"
        }


# Global SBOM generator instance
_sbom_generator = None


def get_sbom_generator() -> SBOMGenerator:
    """Get or create global SBOM generator instance."""
    global _sbom_generator
    if _sbom_generator is None:
        _sbom_generator = SBOMGenerator()
    return _sbom_generator


# Convenience functions
def generate_sbom(
    project_path: str,
    format: str = "cyclonedx",
    output_path: Optional[str] = None
) -> Dict:
    """
    Convenience function to generate SBOM.

    Args:
        project_path: Path to project
        format: cyclonedx, spdx, or both
        output_path: Output file path

    Returns:
        Dict with SBOM data and metadata
    """
    generator = get_sbom_generator()
    
    if format.lower() == "cyclonedx":
        return generator.generate_cyclonedx(project_path, output_path)
    elif format.lower() == "spdx":
        return generator.generate_spdx(project_path, output_path)
    elif format.lower() == "both":
        return generator.generate_both(project_path)
    else:
        return {
            "success": False,
            "error": f"Unknown format: {format}. Use 'cyclonedx', 'spdx', or 'both'"
        }
