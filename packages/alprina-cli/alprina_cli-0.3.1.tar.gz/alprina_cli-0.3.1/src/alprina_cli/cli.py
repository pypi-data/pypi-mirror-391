"""
Main CLI application for Alprina.
Integrates Typer for command handling with Rich for beautiful output.
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from typing import Optional
from pathlib import Path
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from . import __version__
from .auth import login_command, logout_command, status_command
from .scanner import scan_command, recon_command
from .policy import policy_test_command, policy_init_command
from .reporting import report_command
from .billing import billing_status_command
from .acp_server import run_acp
from .config import init_config_command
from .history import history_command
from .fix_command import fix_command, suggest_fixes_command

console = Console()
app = typer.Typer(
    name="alprina",
    help="🛡️  Alprina CLI - AI-powered cybersecurity tool for developers",
    add_completion=True,
    rich_markup_mode="rich",
)

# Auth commands
auth_app = typer.Typer(help="Authentication commands")
app.add_typer(auth_app, name="auth")

@auth_app.command("login")
def login(
    api_key: Optional[str] = typer.Option(None, "--api-key", help="API key for authentication"),
    oauth_provider: Optional[str] = typer.Option(None, "--provider", help="OAuth provider (github, google)"),
    code: Optional[str] = typer.Option(None, "--code", help="6-digit CLI code from dashboard"),
):
    """
    🔐 Authenticate with Alprina.

    Examples:
      alprina auth login                    # Browser OAuth (recommended)
      alprina auth login --code ABC123      # Dashboard code (reverse flow)
      alprina auth login --api-key sk_...   # Direct API key
    """
    try:
        login_command(api_key, oauth_provider, code)
    except Exception as e:
        from .utils.errors import handle_error
        handle_error(e)
        raise typer.Exit(1)

@auth_app.command("logout")
def logout():
    """
    👋 Logout from Alprina.
    """
    logout_command()

@auth_app.command("status")
def auth_status():
    """
    ℹ️  Check authentication status.
    """
    status_command()


# Scanning commands
@app.command("scan")
def scan(
    path: str = typer.Argument(
        ".",
        help="Path to scan (file or directory, defaults to current directory)"
    ),
    profile: str = typer.Option("default", "--profile", "-p", help="Scan profile to use"),
    safe_only: bool = typer.Option(True, "--safe-only", help="Only run safe, non-intrusive scans"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
    quick: bool = typer.Option(False, "--quick", "-q", help="Quick 5-second scan for critical issues"),
    container: bool = typer.Option(False, "--container", help="Scan Docker container image"),
    agent: Optional[list[str]] = typer.Option(None, "--agent", "-a", help="Specific agent(s) to use"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
    # Week 4: Unified scanner flags for smart contracts
    all_analyzers: bool = typer.Option(False, "--all", help="Run all security analyzers (symbolic, MEV, cross-contract, gas)"),
    symbolic: bool = typer.Option(False, "--symbolic", help="Run symbolic execution with Z3"),
    mev: bool = typer.Option(False, "--mev", help="Run MEV detection analysis"),
    cross_contract: bool = typer.Option(False, "--cross-contract", help="Run cross-contract analysis"),
    gas: bool = typer.Option(False, "--gas", help="Run gas optimization analysis (Week 4 Day 3)"),
    tvl: Optional[float] = typer.Option(None, "--tvl", help="Protocol TVL for economic impact calculation"),
    protocol_type: Optional[str] = typer.Option(None, "--protocol", help="Protocol type (dex, lending, bridge)"),
    output_format: str = typer.Option("json", "--format", help="Output format (json, markdown, html, text)"),
):
    """
    🔍 Run an AI-powered security scan.

    Examples:
        alprina scan                          # Scan current directory
        alprina scan ./src                    # Scan src directory
        alprina scan app.py                   # Scan single file
        alprina scan . --quick                # Quick 5-second check
        alprina scan . -a red_teamer          # Use specific agent
        alprina scan . -a cicd_guardian      # Use CI/CD Pipeline Guardian
        alprina scan . -a web3_auditor        # Use Web3/DeFi Security Auditor
        alprina scan . --profile code-audit   # Full comprehensive scan
        alprina scan nginx:latest --container # Scan Docker image

        Smart Contract Security (Week 4):
        alprina scan contract.sol --all --tvl 50000000 --protocol dex
        alprina scan contract.sol --symbolic --mev
        alprina scan contract.sol --gas  # Gas optimization (Day 3)
        alprina scan . --cross-contract --format markdown
    """
    scan_command(
        path, profile, safe_only, output, quick, container, agent, verbose,
        all_analyzers, symbolic, mev, cross_contract, gas, tvl, protocol_type, output_format
    )


@app.command("recon")
def recon(
    target: str = typer.Argument(..., help="Target for reconnaissance"),
    passive: bool = typer.Option(True, "--passive", help="Use only passive techniques"),
):
    """
    🕵️  Perform reconnaissance on a target.
    """
    recon_command(target, passive)


@app.command("history")
def history(
    scan_id: Optional[str] = typer.Option(None, "--scan-id", "-i", help="Specific scan ID to view details"),
    limit: int = typer.Option(20, "--limit", "-l", help="Number of scans to display"),
    severity: Optional[str] = typer.Option(None, "--severity", "-s", help="Filter by severity"),
    page: int = typer.Option(1, "--page", "-p", help="Page number"),
):
    """
    📜 View scan history and results.

    Examples:
        alprina history                           # List recent scans
        alprina history --scan-id abc123          # View specific scan details
        alprina history --severity high           # Filter by severity
        alprina history --page 2 --limit 10       # Pagination
    """
    history_command(scan_id, limit, severity, page)


@app.command("mitigate")
def mitigate(
    finding_id: Optional[str] = typer.Argument(None, help="Specific finding ID to mitigate"),
    report_file: Optional[Path] = typer.Option(None, "--report", "-r", help="Report file to process"),
):
    """
    🛠️  Get AI-powered mitigation suggestions for findings.
    """
    from .mitigation import mitigate_command
    mitigate_command(finding_id, report_file)


@app.command("fix")
def fix(
    target: str = typer.Argument(..., help="Path to file or directory to fix"),
    finding_id: Optional[str] = typer.Option(None, "--id", help="Specific finding ID to fix"),
    auto_fix: bool = typer.Option(False, "--auto-fix", help="Automatically apply fixes without confirmation"),
    severity: Optional[str] = typer.Option(None, "--severity", help="Fix only specific severity (critical, high, medium, low)"),
    preview: bool = typer.Option(False, "--preview", help="Preview fixes without applying"),
):
    """
    🤖 Generate AI-powered fixes for vulnerabilities.

    Examples:
        alprina fix ./app.py                      # Interactive fix for single file
        alprina fix ./src --auto-fix              # Auto-fix all findings
        alprina fix ./src --severity critical     # Fix only critical issues
        alprina fix ./src --preview               # Preview fixes without applying
    """
    fix_command(target, finding_id, auto_fix, severity, preview)


# Policy commands
policy_app = typer.Typer(help="Policy and compliance commands")
app.add_typer(policy_app, name="policy")

@policy_app.command("init")
def policy_init():
    """
    📋 Initialize a new policy configuration file.
    """
    policy_init_command()

@policy_app.command("test")
def policy_test(
    target: str = typer.Argument(..., help="Target to test against policy"),
):
    """
    ✅ Test if a target is allowed by current policy.
    """
    policy_test_command(target)


# Config commands
@app.command("config")
def config(
    init: bool = typer.Option(False, "--init", help="Initialize default configuration"),
):
    """
    ⚙️  Manage Alprina configuration.
    """
    if init:
        init_config_command()
    else:
        console.print("[yellow]Use --init to create a default configuration[/yellow]")


# Reporting commands
@app.command("report")
def report(
    format: str = typer.Option("html", "--format", "-f", help="Report format (html, pdf, json)"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
):
    """
    📊 Generate a security report from scan results.
    """
    report_command(format, output)


# Billing commands
billing_app = typer.Typer(help="Billing and subscription commands")
app.add_typer(billing_app, name="billing")

@billing_app.command("status")
def billing_status():
    """
    💳 Check billing status and usage.
    """
    billing_status_command()


# Quickstart command (tutorial for new users)
@app.command("quickstart")
def quickstart():
    """
    🎓 Interactive tutorial for first-time users.
    
    Perfect for learning how Alprina works! Runs your first security
    scan with guided explanations in plain English.
    
    Examples:
        alprina quickstart    # Start the guided tutorial
    """
    from .quickstart import quickstart_command
    quickstart_command()


# Chat command
@app.command("chat")
def chat(
    model: str = typer.Option("claude-3-5-sonnet-20241022", "--model", "-m", help="LLM model to use"),
    streaming: bool = typer.Option(True, "--streaming/--no-streaming", help="Enable streaming responses"),
    load_results: Optional[Path] = typer.Option(None, "--load", "-l", help="Load scan results for context"),
):
    """
    💬 Start interactive chat with Alprina AI assistant.

    Examples:
        alprina chat
        alprina chat --model gpt-4
        alprina chat --load ~/.alprina/out/latest-results.json
        alprina chat --no-streaming
    """
    from .chat import chat_command
    chat_command(model, streaming, load_results)


# ACP mode for IDE integration
@app.command("acp", hidden=True)
def acp_mode():
    """
    🔌 Start Alprina in ACP mode for IDE integration.
    """
    console.print(Panel("Starting Alprina in ACP mode...", title="ACP Mode"))
    run_acp()


# Version command
@app.command("version")
def version():
    """
    📌 Show Alprina CLI version.
    """
    console.print(f"[bold cyan]Alprina CLI[/bold cyan] version [bold]{__version__}[/bold]")


# Main callback for global options
@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    version_flag: bool = typer.Option(False, "--version", help="Show version and exit"),
):
    """
    🛡️  Alprina CLI - Build fast. Guard faster.

    An intelligent cybersecurity command-line tool for developers.
    
    Examples:
        alprina                     # Show welcome screen
        alprina scan ./             # Scan current directory
        alprina chat                # Interactive AI assistant
        alprina auth login          # Sign in
    """
    if version_flag:
        console.print(f"[bold cyan]Alprina CLI[/bold cyan] version [bold]{__version__}[/bold]")
        raise typer.Exit()
    
    if verbose:
        console.print("[dim]Verbose mode enabled[/dim]")
    if debug:
        console.print("[dim]Debug mode enabled[/dim]")
    
    # Show welcome screen if no command provided
    if ctx.invoked_subcommand is None:
        from .utils.welcome import show_welcome
        show_welcome(force=True)
        raise typer.Exit()


def cli_main():
    """Entry point for the CLI."""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    cli_main()
