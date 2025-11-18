"""
Scanner module for Alprina CLI.
Handles remote and local security scanning using Alprina security agents.
"""

from pathlib import Path
from typing import Optional
import httpx
import os
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table

from .auth import is_authenticated, get_auth_headers, get_backend_url
from .policy import validate_target
from .security_engine import run_remote_scan, run_local_scan
from .reporting import write_event
from .report_generator import generate_security_reports
from .services.cve_service import enrich_findings
from .services.container_scanner import get_container_scanner

console = Console()


def scan_command(
    target: str,
    profile: str = "default",
    safe_only: bool = True,
    output: Optional[Path] = None,
    quick: bool = False,
    container: bool = False,
    agent: Optional[list[str]] = None,
    verbose: bool = False,
    # Week 4: Unified scanner parameters
    all_analyzers: bool = False,
    symbolic: bool = False,
    mev: bool = False,
    cross_contract: bool = False,
    gas: bool = False,  # Week 4 Day 3
    tvl: Optional[float] = None,
    protocol_type: Optional[str] = None,
    output_format: str = "json"
):
    """
    Execute a security scan on a target (remote, local, or container).

    Args:
        target: Target to scan (URL, IP, local path, or Docker image)
        profile: Scan profile to use
        safe_only: Only run safe, non-intrusive scans
        output: Output file path
        quick: Run quick 5-second scan for critical issues only
        container: Scan as Docker container image
        agent: Specific agent(s) to use
        verbose: Show detailed output
        all_analyzers: Run all security analyzers (Week 4)
        symbolic: Run symbolic execution (Week 4)
        mev: Run MEV detection (Week 4)
        cross_contract: Run cross-contract analysis (Week 4)
        tvl: Protocol TVL for economic impact (Week 4)
        protocol_type: Protocol type (Week 4)
        output_format: Output format (Week 4)
    """
    # Week 4: Smart contract unified scanner mode
    if all_analyzers or symbolic or mev or cross_contract or gas:
        _run_unified_scanner(
            target, all_analyzers, symbolic, mev, cross_contract, gas,
            tvl, protocol_type, output, output_format, verbose
        )
        return

    # NEW: Container scan mode
    if container:
        _run_container_scan(target, output)
        return

    # NEW: Quick scan mode
    if quick:
        from .quick_scanner import quick_scan
        _run_quick_scan(target)
        return
    
    # Check if target is local or remote first
    target_path = Path(target)
    is_local = target_path.exists()

    # Only require auth for remote scans
    if not is_local and not is_authenticated():
        console.print(Panel(
            "[bold red]🔒 Authentication Required[/bold red]\n\n"
            "To use Alprina CLI, you need to authenticate first.\n\n"
            "[bold cyan]Quick Start:[/bold cyan]\n"
            "  1. Run: [bold]alprina auth login[/bold]\n"
            "  2. Browser opens → Sign in with GitHub\n"
            "  3. Authorize device → Done!\n\n"
            "[dim]Don't have an account? Visit:[/dim]\n"
            "[bold cyan]https://www.alprina.com[/bold cyan]\n\n"
            "[yellow]💡 Tip:[/yellow] Local scans work without authentication!",
            title="Welcome to Alprina CLI",
            border_style="red"
        ))
        return

    # Show warning if not authenticated for local scan
    if is_local and not is_authenticated():
        console.print("[yellow]⚠️  Running in offline mode (not authenticated)[/yellow]")

    console.print(Panel(
        f"🔍 Starting scan on: [bold]{target}[/bold]\n"
        f"Profile: [cyan]{profile}[/cyan]\n"
        f"Mode: {'[green]Safe only[/green]' if safe_only else '[yellow]Full scan[/yellow]'}",
        title="Alprina Security Scan"
    ))

    scan_id = None
    try:
        # Create scan entry in database (if authenticated)
        if is_authenticated():
            scan_id = _create_scan_entry(target, "local" if is_local else "remote", profile)
            if scan_id:
                console.print(f"[dim]Scan ID: {scan_id}[/dim]")

        # Execute scan with specific agents if requested
        if agent:
            console.print(f"[cyan]→[/cyan] Using specific agents: {', '.join(agent)}")
            results = _scan_with_agents(target, agent, verbose)
        elif is_local:
            console.print(f"[cyan]→[/cyan] Detected local target: {target}")
            results = _scan_local(target, profile, safe_only)
        else:
            console.print(f"[cyan]→[/cyan] Detected remote target: {target}")
            validate_target(target)  # Check against policy
            results = _scan_remote(target, profile, safe_only)

        # Enrich findings with CVE/CWE/CVSS data
        if results.get("findings"):
            console.print("[dim]→ Enriching findings with CVE/CWE/CVSS data...[/dim]")
            results["findings"] = enrich_findings(results["findings"])

        # Save results to database (if authenticated and scan was created)
        if is_authenticated() and scan_id:
            _save_scan_results(scan_id, results)
            console.print(f"[dim]✓ Scan saved to your account[/dim]")

        # Log the scan event locally
        write_event({
            "type": "scan",
            "target": target,
            "profile": profile,
            "mode": "local" if is_local else "remote",
            "safe_only": safe_only,
            "findings_count": len(results.get("findings", []))
        })

        # Display results
        _display_results(results)

        # Generate markdown security reports in .alprina/ folder
        if is_local and results.get("findings", []):
            try:
                report_dir = generate_security_reports(results, target)
                console.print(f"\n[green]✓[/green] Security reports generated in: [cyan]{report_dir}[/cyan]")
                console.print("[dim]Files created:[/dim]")
                console.print("[dim]  • SECURITY-REPORT.md - Full vulnerability analysis[/dim]")
                console.print("[dim]  • FINDINGS.md - Detailed findings with code context[/dim]")
                console.print("[dim]  • REMEDIATION.md - Step-by-step fix instructions[/dim]")
                console.print("[dim]  • EXECUTIVE-SUMMARY.md - Non-technical overview[/dim]")
            except Exception as report_error:
                console.print(f"[yellow]⚠️  Could not generate reports: {report_error}[/yellow]")

        if output:
            _save_results(results, output)

    except Exception as e:
        console.print(f"[red]Scan failed: {e}[/red]")


def _scan_local(target: str, profile: str, safe_only: bool) -> dict:
    """Execute local file/directory scan."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Scanning local files...", total=None)

        results = run_local_scan(target, profile, safe_only)

        progress.update(task, completed=True)

    return results


def _scan_remote(target: str, profile: str, safe_only: bool) -> dict:
    """Execute remote target scan."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Scanning remote target...", total=None)

        results = run_remote_scan(target, profile, safe_only)

        progress.update(task, completed=True)

    return results


def _run_quick_scan(target: str):
    """Execute quick security scan."""
    from .quick_scanner import quick_scan
    
    console.print(Panel(
        f"⚡ Quick Health Check on: [bold]{target}[/bold]\n"
        f"Scanning for top 10 critical patterns...\n"
        f"[dim]This takes ~5 seconds[/dim]",
        title="Alprina Quick Scan",
        style="cyan"
    ))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Scanning files...", total=None)
        results = quick_scan(target)
        progress.update(task, completed=True)
    
    _display_quick_results(results)


def _display_quick_results(results: dict):
    """Display quick scan results."""
    duration = results['duration_ms'] / 1000
    
    console.print(f"\n⚡ Quick scan completed in [bold cyan]{duration:.1f}s[/bold cyan]")
    console.print(f"   Scanned [bold]{results['summary']['total_files_scanned']}[/bold] files")
    
    critical = results['summary']['critical']
    
    if critical == 0:
        console.print("\n✅ [bold green]No critical issues found![/bold green]")
        console.print("\n💡 [dim]Run full scan for comprehensive analysis:[/dim]")
        console.print("   [bold cyan]alprina scan ./ [/bold cyan]")
    else:
        console.print(f"\n🚨 [bold red]Found {critical} critical issue{'s' if critical != 1 else ''}[/bold red]")
        
        # Show first 5 findings
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Issue", style="red", width=30)
        table.add_column("File", style="cyan", width=25)
        table.add_column("Line", justify="right", style="yellow", width=6)
        
        for finding in results['findings'][:5]:
            file_name = Path(finding['file']).name
            table.add_row(
                finding['title'],
                file_name,
                str(finding['line'])
            )
        
        console.print(table)
        
        if len(results['findings']) > 5:
            console.print(f"\n[dim]+ {len(results['findings']) - 5} more issues...[/dim]")
        
        console.print("\n⚠️  [yellow]Quick scan only checks critical patterns[/yellow]")
        console.print("   Run full scan to find all vulnerabilities:")
        console.print("   [bold cyan]alprina scan ./[/bold cyan]")


def _display_results(results: dict):
    """Display scan results in a formatted table with CVE/CWE/CVSS data."""
    findings = results.get("findings", [])

    if not findings:
        console.print("\n[green]✓ No security issues found![/green]")
        return

    console.print(f"\n[yellow]⚠ Found {len(findings)} issues[/yellow]\n")

    table = Table(title="Security Findings", show_header=True, header_style="bold cyan")
    table.add_column("Severity", style="bold", width=10)
    table.add_column("Type", width=25)
    table.add_column("CVSS", justify="right", width=6)
    table.add_column("CWE", width=12)
    table.add_column("Description", width=40)
    table.add_column("Location", width=25)

    severity_colors = {
        "CRITICAL": "bold red",
        "HIGH": "red",
        "MEDIUM": "yellow",
        "LOW": "blue",
        "INFO": "dim"
    }

    for finding in findings:
        severity = finding.get("severity", "INFO")
        color = severity_colors.get(severity, "white")

        # Get CVSS score
        cvss = finding.get("cvss_score")
        cvss_str = f"{cvss:.1f}" if cvss else "N/A"

        # Get CWE
        cwe = finding.get("cwe", "")
        cwe_num = cwe.split("-")[1] if cwe and "-" in cwe else ""

        table.add_row(
            f"[{color}]{severity}[/{color}]",
            finding.get("type", "Unknown"),
            f"[{color}]{cvss_str}[/{color}]",
            f"[cyan]{cwe_num}[/cyan]" if cwe_num else "[dim]N/A[/dim]",
            finding.get("description", "N/A"),
            finding.get("location", "N/A")
        )

    console.print(table)

    # Show enhanced details for top 3 findings
    console.print("\n[bold cyan]📋 Detailed Analysis (Top 3)[/bold cyan]\n")

    for i, finding in enumerate(findings[:3], 1):
        severity = finding.get("severity", "INFO")
        color = severity_colors.get(severity, "white")

        console.print(f"[bold]{i}. [{color}]{severity}[/{color}]: {finding.get('type', 'Issue')}[/bold]")
        console.print(f"   📍 {finding.get('location', 'N/A')}")

        if finding.get("cvss_score"):
            console.print(f"   📊 CVSS: {finding['cvss_score']:.1f}/10.0 ({finding.get('cvss_severity', 'N/A')})")

        if finding.get("cwe"):
            cwe_name = finding.get("cwe_name", finding["cwe"])
            console.print(f"   🔖 {finding['cwe']}: {cwe_name}")

        if finding.get("owasp"):
            console.print(f"   ⚡ OWASP: {finding['owasp']}")

        if finding.get("references"):
            console.print("   🔗 References:")
            for ref in finding["references"][:3]:
                console.print(f"      • {ref['name']}: [link={ref['url']}]{ref['url']}[/link]")

        console.print()


def _save_results(results: dict, output: Path):
    """Save scan results to file."""
    import json

    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w") as f:
        json.dump(results, f, indent=2)

    console.print(f"\n[green]✓[/green] Results saved to: {output}")


def recon_command(target: str, passive: bool = True):
    """
    Perform reconnaissance on a target.
    """
    if not is_authenticated():
        console.print("[red]Please login first: alprina auth login[/red]")
        return

    console.print(Panel(
        f"🕵️  Reconnaissance: [bold]{target}[/bold]\n"
        f"Mode: {'[green]Passive[/green]' if passive else '[yellow]Active[/yellow]'}",
        title="Alprina Recon"
    ))

    try:
        validate_target(target)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Gathering intelligence...", total=None)

            # Use Alprina security agent for reconnaissance
            from .security_engine import run_agent

            results = run_agent(
                task="web-recon",
                input_data=target,
                metadata={"passive": passive}
            )

            progress.update(task, completed=True)

        # Log event
        write_event({
            "type": "recon",
            "target": target,
            "passive": passive,
            "findings_count": len(results.get("findings", []))
        })

        console.print("\n[green]✓ Reconnaissance complete[/green]")
        _display_results(results)

    except Exception as e:
        console.print(f"[red]Recon failed: {e}[/red]")


def _create_scan_entry(target: str, scan_type: str, profile: str) -> Optional[str]:
    """Create a scan entry in the database before execution."""
    try:
        headers = get_auth_headers()
        backend_url = get_backend_url()

        response = httpx.post(
            f"{backend_url}/scans",
            headers=headers,
            json={
                "target": target,
                "scan_type": scan_type,
                "profile": profile
            },
            timeout=10.0
        )

        if response.status_code == 201:
            data = response.json()
            return data.get("scan_id")
        else:
            console.print(f"[yellow]⚠️  Could not create scan entry: {response.status_code}[/yellow]")
            return None

    except Exception as e:
        console.print(f"[yellow]⚠️  Could not create scan entry: {e}[/yellow]")
        return None


def _save_scan_results(scan_id: str, results: dict):
    """Save scan results to the database after completion."""
    try:
        headers = get_auth_headers()
        backend_url = get_backend_url()

        response = httpx.patch(
            f"{backend_url}/scans/{scan_id}",
            headers=headers,
            json={"results": results},
            timeout=30.0
        )

        if response.status_code != 200:
            console.print(f"[yellow]⚠️  Could not save scan results: {response.status_code}[/yellow]")

    except Exception as e:
        console.print(f"[yellow]⚠️  Could not save scan results: {e}[/yellow]")


def _scan_with_agents(target: str, agents: list[str], verbose: bool = False) -> dict:
    """Execute scan with specific agents."""
    from .utils.agent_loader import get_local_agent
    
    console.print(Panel(
        f"🔧 Agent-Specific Security Scan\n\n"
        f"Target: [bold]{target}[/bold]\n"
        f"Agents: [cyan]{', '.join(agents)}[/cyan]",
        title="Alprina Agent Scan",
        style="cyan"
    ))
    
    all_results = []
    
    for agent_name in agents:
        try:
            # Get the agent instance
            agent = get_local_agent(agent_name)
            if not agent:
                console.print(f"[yellow]⚠️  Agent '{agent_name}' not available, skipping...[/yellow]")
                continue
            
            console.print(f"[cyan]→[/cyan] Running {agent_name}...")
            
            # Run the agent
            result = agent.analyze(target)
            all_results.append(result)
            
            if verbose:
                console.print(f"[green]✓[/green] {agent_name} completed: {len(result.get('vulnerabilities', []))} findings")
            
        except Exception as e:
            console.print(f"[red]✗[/red] {agent_name} failed: {e}")
    
    # Combine results from all agents
    combined_results = {
        "mode": "agent-specific",
        "target": target,
        "agents_used": agents,
        "findings": [],
        "agent_results": all_results
    }
    
    # Aggregate findings from all agents
    for result in all_results:
        if result.get('status') == 'success':
            combined_results["findings"].extend(result.get('vulnerabilities', []))
    
    return combined_results


def _run_container_scan(image: str, output: Optional[Path] = None):
    """Execute container security scan with Trivy."""
    console.print(Panel(
        f"🐳 Container Security Scan\n\n"
        f"Image: [bold]{image}[/bold]\n"
        f"Scanner: [cyan]Trivy (Aqua Security)[/cyan]",
        title="Alprina Container Scan",
        style="cyan"
    ))

    scanner = get_container_scanner()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Scanning container image...", total=None)

        # Scan the image
        results = scanner.scan_image(image)

        progress.update(task, completed=True)

    if not results["success"]:
        console.print(f"[red]✗ Container scan failed: {results.get('error')}[/red]")

        if "not installed" in results.get("error", ""):
            console.print("\n[yellow]📦 Installation Required:[/yellow]")
            console.print(f"  {results.get('install_command', '')}")
            console.print(f"\nDocumentation: {results.get('install_url', '')}")

        return

    console.print("[green]✓ Container scan complete![/green]\n")

    # Display summary
    _display_container_results(results)

    # Save results if output specified
    if output:
        import json
        output.parent.mkdir(parents=True, exist_ok=True)
        with open(output, 'w') as f:
            json.dump(results, f, indent=2)
        console.print(f"\n[green]✓[/green] Results saved to: {output}")


def _display_container_results(results: dict):
    """Display container scan results."""
    summary = results.get("summary", {})
    image = results.get("image", "unknown")

    # Summary table
    table = Table(title=f"Scan Results: {image}", show_header=False, box=None)

    table.add_row("📦 Image:", f"[bold]{image}[/bold]")
    table.add_row("🔍 Vulnerabilities:", f"[bold]{summary.get('total_vulnerabilities', 0)}[/bold]")

    # Severity breakdown
    by_severity = summary.get("by_severity", {})
    critical = by_severity.get("CRITICAL", 0)
    high = by_severity.get("HIGH", 0)
    medium = by_severity.get("MEDIUM", 0)
    low = by_severity.get("LOW", 0)

    if critical > 0:
        table.add_row("  🔴 Critical:", f"[red bold]{critical}[/red bold]")
    if high > 0:
        table.add_row("  🟠 High:", f"[red]{high}[/red]")
    if medium > 0:
        table.add_row("  🟡 Medium:", f"[yellow]{medium}[/yellow]")
    if low > 0:
        table.add_row("  🔵 Low:", f"[blue]{low}[/blue]")

    if summary.get("secrets_found", 0) > 0:
        table.add_row("🔐 Secrets Found:", f"[red bold]{summary['secrets_found']}[/red bold]")

    if summary.get("packages_scanned", 0) > 0:
        table.add_row("📦 Packages Scanned:", str(summary["packages_scanned"]))

    if summary.get("layers", 0) > 0:
        table.add_row("🗂️  Image Layers:", str(summary["layers"]))

    console.print(table)

    # Recommendations
    recommendations = results.get("recommendations", [])
    if recommendations:
        console.print("\n[bold cyan]💡 Recommendations:[/bold cyan]")
        for rec in recommendations:
            console.print(f"  {rec}")

    # Risk assessment
    if critical > 0 or high > 0:
        console.print("\n[bold red]⚠️  HIGH RISK[/bold red]")
        console.print("This image has critical security issues. Update immediately.")
    elif medium > 0:
        console.print("\n[bold yellow]⚠️  MEDIUM RISK[/bold yellow]")
        console.print("Plan security updates within 1-2 weeks.")
    else:
        console.print("\n[bold green]✅ LOW RISK[/bold green]")
        console.print("No critical issues found. Continue monitoring.")


def _run_unified_scanner(
    target: str,
    all_analyzers: bool,
    symbolic: bool,
    mev: bool,
    cross_contract: bool,
    gas: bool,
    tvl: Optional[float],
    protocol_type: Optional[str],
    output: Optional[Path],
    output_format: str,
    verbose: bool
):
    """
    Run unified scanner for smart contract security analysis (Week 4)

    Args:
        target: Path to Solidity contract file or directory
        all_analyzers: Run all analyzers
        symbolic: Run symbolic execution
        mev: Run MEV detection
        cross_contract: Run cross-contract analysis
        gas: Run gas optimization analysis
        tvl: Protocol TVL for economic impact
        protocol_type: Protocol type (dex, lending, etc.)
        output: Output file path
        output_format: Output format (json, markdown, html, text)
        verbose: Show detailed output
    """
    from .unified_scanner import UnifiedScanner, ScanOptions

    target_path = Path(target)

    if not target_path.exists():
        console.print(f"[bold red]Error:[/bold red] Target not found: {target}")
        return

    # Determine if single file or directory
    if target_path.is_file():
        if not target_path.suffix == '.sol':
            console.print(f"[bold yellow]Warning:[/bold yellow] Target is not a Solidity file (.sol)")
            console.print("Unified scanner is optimized for smart contract analysis.")
            return

        # Single file scan
        contract_code = target_path.read_text()
        file_name = target_path.name

        # Create scan options
        options = ScanOptions(
            run_all=all_analyzers,
            symbolic=symbolic,
            mev=mev,
            cross_contract=False,  # Single file can't do cross-contract
            gas_optimization=gas,
            calculate_economic_impact=(tvl is not None),
            tvl=tvl,
            protocol_type=protocol_type,
            output_file=str(output) if output else None,
            output_format=output_format,
            verbose=verbose,
            parallel=True
        )

        # Run scan
        scanner = UnifiedScanner()

        if verbose:
            console.print(f"\n🔍 [bold]Alprina Unified Security Scanner[/bold]")
            console.print(f"{'='*60}")
            console.print(f"Contract: [cyan]{file_name}[/cyan]")
            if tvl:
                console.print(f"Protocol: [cyan]{protocol_type or 'generic'}[/cyan] (TVL: ${tvl:,.0f})")
            console.print()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Running security analysis...", total=None)

            report = scanner.scan(contract_code, str(target_path), options)

            progress.update(task, completed=True)

        # Display results
        _display_unified_results(report, verbose)

    elif target_path.is_dir():
        # Directory scan - find all .sol files
        sol_files = list(target_path.glob("**/*.sol"))

        if not sol_files:
            console.print(f"[bold yellow]Warning:[/bold yellow] No Solidity files found in {target}")
            return

        console.print(f"[cyan]→[/cyan] Found {len(sol_files)} Solidity files")

        if cross_contract and len(sol_files) > 1:
            # Multi-contract analysis
            contracts = {}
            for sol_file in sol_files:
                contract_name = sol_file.stem
                contract_code = sol_file.read_text()
                contracts[contract_name] = contract_code

            options = ScanOptions(
                run_all=all_analyzers,
                symbolic=symbolic,
                mev=mev,
                cross_contract=True,
                gas_optimization=gas,
                calculate_economic_impact=(tvl is not None),
                tvl=tvl,
                protocol_type=protocol_type,
                output_file=str(output) if output else None,
                output_format=output_format,
                verbose=verbose,
                parallel=True
            )

            scanner = UnifiedScanner()

            if verbose:
                console.print(f"\n🔍 [bold]Alprina Unified Security Scanner[/bold]")
                console.print(f"{'='*60}")
                console.print(f"Contracts: [cyan]{len(contracts)}[/cyan]")
                console.print(f"Cross-contract analysis: [green]enabled[/green]")
                if tvl:
                    console.print(f"Protocol: [cyan]{protocol_type or 'generic'}[/cyan] (TVL: ${tvl:,.0f})")
                console.print()

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Running cross-contract analysis...", total=None)

                report = scanner.scan_multi_contract(contracts, str(target_path), options)

                progress.update(task, completed=True)

            _display_unified_results(report, verbose)

        else:
            # Scan each file individually
            console.print(f"[cyan]→[/cyan] Scanning {len(sol_files)} contracts individually...")

            all_reports = []

            for sol_file in sol_files:
                contract_code = sol_file.read_text()

                options = ScanOptions(
                    run_all=all_analyzers,
                    symbolic=symbolic,
                    mev=mev,
                    cross_contract=False,
                    calculate_economic_impact=(tvl is not None),
                    tvl=tvl,
                    protocol_type=protocol_type,
                    output_file=None,  # Don't save individual reports
                    output_format=output_format,
                    verbose=False,
                    parallel=True
                )

                scanner = UnifiedScanner()
                report = scanner.scan(contract_code, str(sol_file), options)
                all_reports.append(report)

                if verbose:
                    console.print(f"\n[cyan]{sol_file.name}:[/cyan] {report.total_vulnerabilities} findings")

            # Aggregate results
            total_vulns = sum(r.total_vulnerabilities for r in all_reports)
            console.print(f"\n[bold]Total vulnerabilities across all contracts:[/bold] {total_vulns}")

            # Display summary
            if total_vulns > 0 and verbose:
                console.print("\n[bold cyan]Top Vulnerabilities:[/bold cyan]")
                all_vulns = []
                for report in all_reports:
                    all_vulns.extend(report.vulnerabilities)

                # Sort by severity and risk score
                all_vulns.sort(key=lambda v: (
                    {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}.get(v.severity, 999),
                    -(v.risk_score or 0)
                ))

                for i, vuln in enumerate(all_vulns[:10], 1):  # Top 10
                    icon = "🔴" if vuln.severity == "critical" else "🟠" if vuln.severity == "high" else "🟡"
                    console.print(f"{i}. {icon} {vuln.title} ({vuln.file_path})")

    else:
        console.print(f"[bold red]Error:[/bold red] Invalid target: {target}")


def _display_unified_results(report, verbose: bool):
    """Display results from unified scanner"""
    from rich.table import Table

    console.print(f"\n{'='*60}")
    console.print(f"[bold]📊 Scan Results[/bold]")
    console.print(f"{'='*60}\n")

    # Summary table
    summary_table = Table(show_header=False, box=None)
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="bold")

    summary_table.add_row("Scan ID", report.scan_id)
    summary_table.add_row("Scan Time", f"{report.total_scan_time:.2f}s")
    summary_table.add_row("Total Vulnerabilities", str(report.total_vulnerabilities))
    summary_table.add_row("  - Critical", str(report.vulnerabilities_by_severity['critical']))
    summary_table.add_row("  - High", str(report.vulnerabilities_by_severity['high']))
    summary_table.add_row("  - Medium", str(report.vulnerabilities_by_severity['medium']))
    summary_table.add_row("  - Low", str(report.vulnerabilities_by_severity['low']))

    if report.total_max_loss > 0:
        summary_table.add_row("Estimated Max Loss", f"${report.total_max_loss:,.0f}")
        summary_table.add_row("Average Risk Score", f"{report.average_risk_score:.1f}/100")

    console.print(summary_table)

    # Vulnerabilities by analyzer
    if report.vulnerabilities_by_analyzer:
        console.print(f"\n[bold cyan]Vulnerabilities by Analyzer:[/bold cyan]")
        for analyzer, count in report.vulnerabilities_by_analyzer.items():
            console.print(f"  • {analyzer}: {count}")

    # List vulnerabilities
    if report.total_vulnerabilities > 0:
        console.print(f"\n[bold cyan]Vulnerabilities:[/bold cyan]\n")

        for i, vuln in enumerate(report.vulnerabilities, 1):
            icon = "🔴" if vuln.severity == "critical" else "🟠" if vuln.severity == "high" else "🟡" if vuln.severity == "medium" else "⚪"

            console.print(f"{i}. {icon} [bold]{vuln.title}[/bold] [{vuln.severity.upper()}]")
            console.print(f"   File: {vuln.file_path}:{vuln.line_number or '?'}")
            console.print(f"   Analyzer: {vuln.analyzer_type.value}")

            if vuln.estimated_loss_max:
                console.print(f"   Financial Impact: ${vuln.estimated_loss_min:,.0f} - ${vuln.estimated_loss_max:,.0f}")

            if verbose:
                console.print(f"   {vuln.description}")
                console.print(f"   [dim]Recommendation: {vuln.recommendation}[/dim]")

            console.print()

    else:
        console.print("\n[bold green]✅ No vulnerabilities found![/bold green]\n")

    # Performance metrics
    if verbose and report.analyzer_times:
        console.print(f"[bold cyan]Analyzer Performance:[/bold cyan]")
        for analyzer, time in report.analyzer_times.items():
            console.print(f"  • {analyzer}: {time:.3f}s")

    # Errors
    if report.errors:
        console.print(f"\n[bold yellow]⚠️  Warnings:[/bold yellow]")
        for error in report.errors:
            console.print(f"  • {error}")

    # Output file notification
    if report.scan_options.output_file:
        console.print(f"\n[green]✓[/green] Report saved to: [cyan]{report.scan_options.output_file}[/cyan]")

    console.print(f"\n{'='*60}\n")
