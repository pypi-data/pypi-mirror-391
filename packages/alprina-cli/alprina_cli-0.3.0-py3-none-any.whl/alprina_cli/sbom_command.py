"""
SBOM Command - Software Bill of Materials generation.
Generates SBOMs in CycloneDX and/or SPDX formats.
"""

from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from loguru import logger

from .services.sbom_generator import get_sbom_generator

console = Console()


def sbom_command(
    project_path: str,
    format: str = "cyclonedx",
    output: str = None,
    output_format: str = "json"
):
    """
    Generate Software Bill of Materials (SBOM).

    Args:
        project_path: Path to project directory
        format: cyclonedx, spdx, or both
        output: Output file path (optional)
        output_format: json, xml, yaml, or tag-value
    """
    console.print(Panel(
        f"📦 Software Bill of Materials Generator\n\n"
        f"Project: [bold]{project_path}[/bold]\n"
        f"Format: [cyan]{format.upper()}[/cyan]\n"
        f"Output Format: [cyan]{output_format}[/cyan]",
        title="Alprina SBOM",
        border_style="cyan"
    ))

    generator = get_sbom_generator()

    try:
        if format.lower() == "cyclonedx":
            _generate_cyclonedx(generator, project_path, output, output_format)
        elif format.lower() == "spdx":
            _generate_spdx(generator, project_path, output, output_format)
        elif format.lower() == "both":
            _generate_both(generator, project_path)
        else:
            console.print(f"[red]Unknown format: {format}[/red]")
            console.print("Valid formats: cyclonedx, spdx, both")
            return

    except Exception as e:
        console.print(f"[red]SBOM generation failed: {e}[/red]")
        logger.error(f"SBOM error: {e}", exc_info=True)


def _generate_cyclonedx(generator, project_path: str, output: str, output_format: str):
    """Generate CycloneDX SBOM."""
    console.print("\n[bold]🔄 Generating CycloneDX SBOM...[/bold]")
    console.print("[dim]This may take a minute for large projects...[/dim]\n")

    result = generator.generate_cyclonedx(project_path, output, output_format)

    if not result["success"]:
        _handle_error(result)
        return

    console.print("[green]✓ CycloneDX SBOM generated successfully![/green]\n")

    # Show summary
    _display_summary("CycloneDX 1.5 (OWASP Security-Focused)", result)


def _generate_spdx(generator, project_path: str, output: str, output_format: str):
    """Generate SPDX SBOM."""
    console.print("\n[bold]🔄 Generating SPDX SBOM...[/bold]")
    console.print("[dim]This may take a minute for large projects...[/dim]\n")

    result = generator.generate_spdx(project_path, output, output_format)

    if not result["success"]:
        _handle_error(result)
        return

    console.print("[green]✓ SPDX SBOM generated successfully![/green]\n")

    # Show summary
    _display_summary("SPDX 2.3 (ISO/IEC 5962:2021)", result)


def _generate_both(generator, project_path: str):
    """Generate both CycloneDX and SPDX SBOMs."""
    console.print("\n[bold]🔄 Generating both CycloneDX and SPDX SBOMs...[/bold]")
    console.print("[dim]This may take a few minutes...[/dim]\n")

    results = generator.generate_both(project_path)

    if not results["success"]:
        console.print("[yellow]⚠️  Some SBOMs failed to generate[/yellow]\n")

    # Show results for each format
    for format_result in results["formats"]:
        format_name = format_result.get("format", "Unknown")

        if format_result["success"]:
            console.print(f"[green]✓ {format_name} SBOM generated![/green]")
            _display_summary(format_name, format_result)
            console.print()
        else:
            console.print(f"[red]✗ {format_name} SBOM failed[/red]")
            console.print(f"   Error: {format_result.get('error', 'Unknown error')}\n")


def _display_summary(format_name: str, result: dict):
    """Display SBOM summary table."""
    summary = result.get("summary", {})

    table = Table(title=f"{format_name} Summary", show_header=False, box=None)

    table.add_row("📄 Output File:", f"[cyan]{result.get('output_file')}[/cyan]")
    table.add_row("📊 Format:", f"[cyan]{result.get('output_format', 'json')}[/cyan]")

    if "iso_standard" in result:
        table.add_row("🏆 Standard:", f"[cyan]{result['iso_standard']}[/cyan]")

    # Format-specific metrics
    if "total_components" in summary:
        table.add_row("📦 Components:", f"[bold]{summary['total_components']}[/bold]")
        if summary.get("direct_dependencies"):
            table.add_row("   Direct Dependencies:", str(summary["direct_dependencies"]))
        if summary.get("transitive_dependencies"):
            table.add_row("   Transitive Dependencies:", str(summary["transitive_dependencies"]))

    if "total_packages" in summary:
        table.add_row("📦 Packages:", f"[bold]{summary['total_packages']}[/bold]")

    if summary.get("files_analyzed"):
        table.add_row("📁 Files Analyzed:", str(summary["files_analyzed"]))

    if summary.get("vulnerabilities"):
        vuln_color = "red" if summary["vulnerabilities"] > 0 else "green"
        table.add_row(
            "🚨 Vulnerabilities:",
            f"[{vuln_color}]{summary['vulnerabilities']}[/{vuln_color}]"
        )

    if summary.get("unique_licenses"):
        table.add_row("📜 Unique Licenses:", str(summary["unique_licenses"]))

    console.print(table)

    # Show top licenses
    if summary.get("licenses"):
        console.print("\n[bold]📜 Top Licenses:[/bold]")
        for i, license in enumerate(summary["licenses"][:5], 1):
            console.print(f"   {i}. {license}")

        if len(summary["licenses"]) > 5:
            console.print(f"   ... and {len(summary['licenses']) - 5} more")


def _handle_error(result: dict):
    """Handle SBOM generation errors."""
    error = result.get("error", "Unknown error")
    tool = result.get("tool", "tool")

    console.print(f"[red]✗ SBOM generation failed[/red]")
    console.print(f"[red]Error: {error}[/red]\n")

    if "not installed" in error.lower():
        console.print("[yellow]🔧 Installation Required[/yellow]\n")

        if "install_command" in result:
            console.print(f"Install {tool}:")
            console.print(f"  [cyan]{result['install_command']}[/cyan]\n")

        if "install_url" in result:
            console.print(f"Documentation: {result['install_url']}")

        if result.get("description"):
            console.print(f"\n{result['description']}")
