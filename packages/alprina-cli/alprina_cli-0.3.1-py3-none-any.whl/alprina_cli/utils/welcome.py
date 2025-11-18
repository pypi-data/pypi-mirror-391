"""
Welcome screen and first-run experience for Alprina CLI.
"""

from rich.console import Console
from rich.panel import Panel
from rich import box
from typing import Optional
from pathlib import Path
import os

console = Console()


def get_auth_status() -> dict:
    """
    Check if user is authenticated.
    
    Returns:
        dict with is_authenticated, email, tier, scans_remaining
    """
    # Check for API key in environment or config
    from ..config import get_api_key
    
    api_key = get_api_key()
    
    if not api_key:
        return {
            "is_authenticated": False,
            "email": None,
            "tier": None,
            "scans_remaining": None,
            "api_key": None
        }
    
    # TODO: Call API to get user info
    # For now, just return that they're authenticated
    return {
        "is_authenticated": True,
        "email": "user@example.com",  # TODO: Get from API
        "tier": "free",
        "scans_remaining": 10,
        "api_key": api_key
    }


def show_welcome(force: bool = False) -> bool:
    """
    Show welcome message on first run or if not authenticated.
    
    Args:
        force: Force show welcome even if authenticated
        
    Returns:
        True if user is authenticated, False otherwise
    """
    auth_status = get_auth_status()
    
    if not auth_status["is_authenticated"]:
        console.print(Panel.fit(
            "[bold cyan]🛡️  Welcome to Alprina![/bold cyan]\n\n"
            "Alprina is your AI security testing assistant.\n\n"
            "[yellow]You're not signed in yet.[/yellow]\n\n"
            "To get started:\n"
            "  1. Sign in:  [bold]alprina auth login[/bold]\n"
            "  2. Run scan: [bold]alprina scan ./[/bold]\n"
            "  3. Chat:     [bold]alprina chat[/bold]\n\n"
            "Need help? Run: [bold]alprina --help[/bold]",
            title="🛡️  Alprina Security CLI",
            border_style="cyan",
            box=box.DOUBLE
        ))
        return False
    
    elif force:
        console.print(Panel.fit(
            f"[bold green]✅ Welcome back![/bold green]\n\n"
            f"[dim]Tier: {auth_status['tier']} | Scans: {auth_status['scans_remaining']} remaining[/dim]\n\n"
            "What would you like to do?\n"
            "  • [bold]alprina scan ./[/bold] - Scan for vulnerabilities\n"
            "  • [bold]alprina chat[/bold] - Interactive AI assistant\n"
            "  • [bold]alprina fix ./[/bold] - Auto-fix vulnerabilities\n\n"
            "Type [bold]alprina --help[/bold] for more commands",
            title="🛡️  Alprina",
            border_style="green",
            box=box.ROUNDED
        ))
        return True
    
    return True


def show_not_authenticated_error():
    """Show friendly error when command requires auth."""
    console.print(Panel.fit(
        "[bold red]❌ Not signed in[/bold red]\n\n"
        "This command requires authentication.\n\n"
        "[yellow]💡 Solution:[/yellow]\n"
        "Run: [bold]alprina auth login[/bold]\n\n"
        "Need help? Visit: https://alprina.com/docs/cli/auth",
        title="Authentication Required",
        border_style="red",
        box=box.ROUNDED
    ))
