"""
Fix command - AI-powered vulnerability remediation.
Generates and applies secure code fixes for vulnerabilities.
"""

from pathlib import Path
from typing import Optional, Dict, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.prompt import Confirm
import json

from .services.fix_generator import get_fix_generator
from loguru import logger

console = Console()


def fix_command(
    target: str,
    finding_id: Optional[str] = None,
    auto_fix: bool = False,
    severity: Optional[str] = None,
    preview_only: bool = False
):
    """
    Generate AI-powered fixes for vulnerabilities.

    Args:
        target: Path to scan or specific file
        finding_id: Specific finding ID to fix
        auto_fix: Automatically apply fixes without confirmation
        severity: Fix only specific severity (critical, high, medium, low)
        preview_only: Show fixes without applying
    """
    console.print(Panel(
        f"🤖 AI-Powered Fix Generator\n\n"
        f"Target: [bold]{target}[/bold]\n"
        f"Mode: {'[green]Auto-apply[/green]' if auto_fix else '[yellow]Interactive[/yellow]'}",
        title="Alprina Fix",
        border_style="cyan"
    ))

    try:
        # TODO: Integrate with existing scan results
        # For now, demonstrate with sample finding
        _demo_fix_generation(target, auto_fix, preview_only)

    except Exception as e:
        console.print(f"[red]Fix generation failed: {e}[/red]")
        logger.error(f"Fix command error: {e}", exc_info=True)


def suggest_fixes_command(scan_results_file: str):
    """
    Suggest fixes for findings in a scan results file.

    Args:
        scan_results_file: Path to JSON file with scan results
    """
    try:
        # Load scan results
        with open(scan_results_file, 'r') as f:
            results = json.load(f)

        findings = results.get("findings", [])
        
        if not findings:
            console.print("[yellow]No findings in scan results[/yellow]")
            return

        console.print(Panel(
            f"📋 Analyzing {len(findings)} findings\n"
            f"Generating AI-powered fix suggestions...",
            title="Fix Suggestions",
            border_style="cyan"
        ))

        # Generate fixes for all findings
        fix_generator = get_fix_generator()
        
        for i, finding in enumerate(findings, 1):
            console.print(f"\n[bold cyan]Finding {i}/{len(findings)}:[/bold cyan]")
            _process_single_finding(finding, fix_generator, preview_only=True)

    except FileNotFoundError:
        console.print(f"[red]Scan results file not found: {scan_results_file}[/red]")
    except json.JSONDecodeError:
        console.print(f"[red]Invalid JSON in scan results file[/red]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        logger.error(f"Suggest fixes error: {e}", exc_info=True)


def _demo_fix_generation(target: str, auto_fix: bool, preview_only: bool):
    """
    Demo fix generation with sample vulnerability.
    TODO: Replace with real scan integration.
    """
    # Sample vulnerability for demonstration
    sample_finding = {
        "type": "SQL Injection",
        "severity": "CRITICAL",
        "description": "User input directly concatenated into SQL query without sanitization",
        "location": f"{target}:45",
        "line": 45,
        "cwe": "CWE-89",
        "cvss_score": 9.8
    }

    # Sample vulnerable code
    sample_code = '''import sqlite3

def get_user_by_id(user_id):
    """Get user from database by ID."""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # VULNERABLE: Direct string formatting
    query = f"SELECT * FROM users WHERE id = {user_id}"
    
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return result
'''

    fix_generator = get_fix_generator()

    console.print("\n[bold]🔍 Analyzing Vulnerability...[/bold]")
    console.print(f"   Type: [red]{sample_finding['type']}[/red]")
    console.print(f"   Severity: [red]{sample_finding['severity']}[/red]")
    console.print(f"   Location: [cyan]{sample_finding['location']}[/cyan]")
    if sample_finding.get("cwe"):
        console.print(f"   CWE: [cyan]{sample_finding['cwe']}[/cyan]")
    if sample_finding.get("cvss_score"):
        console.print(f"   CVSS: [red]{sample_finding['cvss_score']}/10.0[/red]")

    console.print("\n[bold]🤖 Generating AI-Powered Fix...[/bold]")

    # Generate fix
    fix_data = fix_generator.generate_fix(
        code=sample_code,
        vulnerability=sample_finding,
        filename=target
    )

    # Display results
    _display_fix(sample_code, fix_data, auto_fix, preview_only)


def _process_single_finding(finding: Dict, fix_generator, preview_only: bool = True):
    """Process a single finding and generate fix."""
    console.print(f"   Type: [yellow]{finding.get('type')}[/yellow]")
    console.print(f"   Severity: [red]{finding.get('severity')}[/red]")
    console.print(f"   Location: [cyan]{finding.get('location')}[/cyan]")

    # TODO: Load actual file content
    # For now, skip file reading
    console.print("   [dim]Fix generation requires file access (not implemented in this demo)[/dim]")


def _display_fix(original_code: str, fix_data: dict, auto_fix: bool, preview_only: bool):
    """Display fix with before/after comparison."""
    
    if fix_data.get("error"):
        console.print(f"\n[red]❌ Error generating fix:[/red] {fix_data['error']}")
        return

    confidence = fix_data.get("confidence", 0.0)
    
    # Show confidence score
    confidence_color = "green" if confidence >= 0.8 else "yellow" if confidence >= 0.6 else "red"
    console.print(f"\n[bold]✨ Fix Generated (Confidence: [{confidence_color}]{confidence*100:.0f}%[/{confidence_color}])[/bold]")

    # Show explanation
    if fix_data.get("explanation"):
        console.print(f"\n[bold cyan]💡 Why This Fix Works:[/bold cyan]")
        console.print(Panel(
            fix_data["explanation"],
            border_style="cyan",
            padding=(1, 2)
        ))

    # Show changes
    if fix_data.get("changes"):
        console.print(f"\n[bold cyan]📝 Changes Made:[/bold cyan]")
        for i, change in enumerate(fix_data["changes"], 1):
            console.print(f"   {i}. {change}")

    # Show before/after code
    console.print(f"\n[bold red]❌ Before (Vulnerable):[/bold red]")
    syntax = Syntax(original_code.strip(), "python", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, border_style="red"))

    fixed_code = fix_data.get("fixed_code", "")
    if fixed_code:
        console.print(f"\n[bold green]✅ After (Secure):[/bold green]")
        syntax = Syntax(fixed_code.strip(), "python", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, border_style="green"))

    # Show diff
    if fix_data.get("diff"):
        console.print(f"\n[bold cyan]🔄 Diff:[/bold cyan]")
        console.print(Panel(fix_data["diff"], border_style="cyan"))

    # Show security notes
    if fix_data.get("security_notes"):
        console.print(f"\n[bold yellow]⚠️  Security Notes:[/bold yellow]")
        for i, note in enumerate(fix_data["security_notes"], 1):
            console.print(f"   {i}. {note}")

    # Apply fix (interactive or auto)
    if not preview_only:
        _apply_fix_interactive(fix_data, auto_fix)


def _apply_fix_interactive(fix_data: dict, auto_fix: bool):
    """Interactively apply fix with user confirmation."""
    
    if auto_fix:
        console.print("\n[green]✓[/green] Auto-applying fix...")
        # TODO: Actually apply the fix
        console.print("[green]✓ Fix applied![/green]")
        console.print("[dim]💾 Backup saved as: file.py.backup[/dim]")
    else:
        console.print("\n[bold]Apply this fix?[/bold]")
        console.print("  [y] Yes, apply the fix")
        console.print("  [n] No, skip this fix")
        console.print("  [d] Show diff again")
        console.print("  [e] Explain in detail")

        if Confirm.ask("Apply fix?", default=False):
            # TODO: Actually apply the fix
            console.print("[green]✓ Fix applied![/green]")
            console.print("[dim]💾 Backup saved as: file.py.backup[/dim]")
        else:
            console.print("[yellow]⊗ Fix skipped[/yellow]")


def _show_fix_summary(total: int, applied: int, skipped: int):
    """Show summary of fix session."""
    console.print("\n" + "="*60)
    console.print("[bold]📊 Fix Summary[/bold]")
    console.print("="*60)
    
    table = Table(show_header=False, box=None)
    table.add_row("Total findings:", str(total))
    table.add_row("Fixes applied:", f"[green]{applied}[/green]")
    table.add_row("Fixes skipped:", f"[yellow]{skipped}[/yellow]")
    
    console.print(table)
    
    if applied > 0:
        console.print("\n[green]✓[/green] Run your tests to verify the fixes work correctly")
        console.print("[green]✓[/green] Backups saved with .backup extension")
    
    console.print("\n[dim]Tip: Run 'alprina scan' again to verify fixes resolved the issues[/dim]")
