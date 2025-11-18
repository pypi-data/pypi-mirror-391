"""
Authentication module for Alprina CLI.
Handles OAuth, API key authentication, and token management.
"""

import os
import json
from pathlib import Path
from typing import Optional
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn

# Import our new error classes and utilities
from .utils.errors import AuthenticationError, APIError, NetworkError
from .utils.welcome import show_welcome

console = Console()

ALPRINA_DIR = Path.home() / ".alprina"
TOKEN_FILE = ALPRINA_DIR / "token"
CONFIG_FILE = ALPRINA_DIR / "config.json"


def ensure_alprina_dir():
    """Ensure the .alprina directory exists."""
    ALPRINA_DIR.mkdir(exist_ok=True)


def save_token(token: str, user_info: Optional[dict] = None):
    """Save authentication token to disk."""
    ensure_alprina_dir()

    auth_data = {
        "token": token,
        "user": user_info or {}
    }

    TOKEN_FILE.write_text(json.dumps(auth_data, indent=2))
    TOKEN_FILE.chmod(0o600)  # Restrict permissions
    console.print("[green]✓[/green] Authentication successful")


def load_token() -> Optional[dict]:
    """
    Load authentication token from environment or disk.
    
    Priority:
    1. ALPRINA_API_KEY environment variable
    2. ~/.alprina/token file
    
    Returns:
        dict with token and user info, or None if not authenticated
    """
    from .config import get_api_key
    
    # Check environment variable first
    api_key = get_api_key()
    
    if api_key:
        # Try to load user info from file if it exists
        if TOKEN_FILE.exists():
            try:
                data = json.loads(TOKEN_FILE.read_text())
                return {
                    "token": api_key,
                    "user": data.get("user", {})
                }
            except Exception:
                pass
        
        # Return just the API key if file doesn't exist
        return {
            "token": api_key,
            "user": {}
        }
    
    return None


def remove_token():
    """Remove authentication token."""
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()


def get_backend_url() -> str:
    """Get backend URL from environment or use default."""
    return os.getenv("ALPRINA_BACKEND", "https://api.alprina.com/v1")


def login_command(api_key: Optional[str] = None, oauth_provider: Optional[str] = None, code: Optional[str] = None):
    """
    Handle user login via browser-based OAuth, CLI code, or API key.
    """
    console.print(Panel("🔐 Alprina Authentication", style="bold cyan"))

    # If CLI code is provided, use the reverse flow
    if code:
        login_with_cli_code(code)
        return

    # If API key is provided directly, use it
    if api_key:
        console.print("Authenticating with API key...")
        authenticate_with_api_key(api_key)
        return

    backend_url = get_backend_url()

    # Default: Browser-based OAuth (recommended)
    console.print("\n[bold cyan]🌐 Opening browser for authentication...[/bold cyan]")
    console.print("[dim]This is the fastest way to get started![/dim]\n")
    
    try:
        login_with_browser()
        return
    except Exception as e:
        console.print(f"\n[yellow]⚠️  Browser authentication failed: {e}[/yellow]")
        console.print("\n[bold]Alternative authentication methods:[/bold]")
        console.print("  [cyan]1.[/cyan] Use dashboard code: [bold]alprina auth login --code YOUR_CODE[/bold]")
        console.print("  [cyan]2.[/cyan] Use API key: [bold]alprina auth login --api-key YOUR_KEY[/bold]")
        console.print()
        console.print("[dim]💡 Get your code from: https://www.alprina.com/dashboard[/dim]")
        
        if Prompt.ask("\nWould you like to try manual authentication now?", choices=["y", "n"], default="n") == "y":
            console.print("\n[bold]Choose method:[/bold]")
            console.print("  [cyan]1.[/cyan] Dashboard code (quick)")
            console.print("  [cyan]2.[/cyan] API key (advanced)")
            
            choice = Prompt.ask("Select option", choices=["1", "2"], default="1")
            
            if choice == "1":
                code_input = Prompt.ask("Enter your 6-digit code from dashboard")
                login_with_cli_code(code_input)
            else:
                console.print("\n[yellow]ℹ️  To get your API key:[/yellow]")
                console.print("  1. Visit: [bold cyan]https://www.alprina.com/dashboard?tab=keys[/bold cyan]")
                console.print("  2. Click 'Create New API Key'")
                console.print("  3. Copy your API key")
                console.print()
                api_key = Prompt.ask("Enter your API key")
                authenticate_with_api_key(api_key)

def authenticate_with_api_key(api_key: str):
    """Authenticate using an API key."""
    backend_url = get_backend_url()
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            progress.add_task("Verifying API key...", total=None)
            
            response = httpx.get(
                f"{backend_url}/auth/me",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10.0
            )

        if response.status_code == 200:
            data = response.json()
            user_info = data.get("user", {})

            # Save API key and user info
            save_token(api_key, user_info)

            # Show welcome screen
            console.print()
            show_welcome(force=True)

        elif response.status_code == 401:
            raise AuthenticationError()
        elif response.status_code == 403:
            from .utils.errors import InvalidTierError
            raise InvalidTierError("CLI access", "Developer")
            
        else:
            error_msg = "Authentication failed"
            try:
                error_data = response.json()
                error_msg = error_data.get('detail', error_msg)
            except:
                pass
            raise APIError(response.status_code, error_msg)

    except httpx.ConnectError:
        raise NetworkError(f"Could not connect to {backend_url}")
    except (AuthenticationError, APIError, NetworkError):
        raise  # Re-raise our custom errors
    except Exception as e:
        from .utils.errors import AlprinaError
        raise AlprinaError(
            message=f"Unexpected error: {e}",
            solution="Please try again or contact support@alprina.com"
        )


def login_with_cli_code(cli_code: str):
    """
    Login using a CLI code from the dashboard (reverse flow).
    User gets code from dashboard, enters it here.
    """
    backend_url = get_backend_url()

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            progress.add_task(f"Verifying CLI code: {cli_code}...", total=None)
            
            response = httpx.post(
                f"{backend_url}/auth/cli-verify",
                json={"cli_code": cli_code.upper()},
                timeout=10.0
            )

        if response.status_code == 200:
            auth_data = response.json()
            api_key = auth_data["api_key"]
            user = auth_data["user"]

            # Save token
            save_token(api_key, user)

            # Show welcome screen
            console.print()
            show_welcome(force=True)

        elif response.status_code == 404:
            console.print(f"\n[red]✗ Invalid or expired CLI code: {cli_code}[/red]")
            console.print("[yellow]Please get a new code from your dashboard.[/yellow]")

        elif response.status_code == 400:
            console.print(f"\n[red]✗ CLI code has already been used: {cli_code}[/red]")
            console.print("[yellow]Please generate a new code from your dashboard.[/yellow]")

        else:
            console.print(f"\n[red]✗ Failed to verify CLI code: {response.status_code}[/red]")
            try:
                error_data = response.json()
                # Handle both API response formats: {detail: ...} and {error: {message: ...}}
                error_message = (
                    error_data.get('detail') or
                    error_data.get('error', {}).get('message') or
                    'Unknown error'
                )
                console.print(f"[red]{error_message}[/red]")
            except:
                console.print(f"[red]{response.text}[/red]")

    except httpx.ConnectError:
        console.print(f"[red]✗ Could not connect to Alprina backend at {backend_url}[/red]")
        console.print("[yellow]Make sure you have internet connectivity.[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


def logout_command():
    """Handle user logout."""
    if TOKEN_FILE.exists():
        remove_token()
        console.print("[green]✓[/green] Logged out successfully")
    else:
        console.print("[yellow]You are not logged in[/yellow]")


def status_command():
    """Show current authentication status."""
    auth_data = load_token()

    if auth_data:
        user = auth_data.get("user", {})
        api_key = auth_data.get("token", "")

        # Show masked API key
        if api_key:
            masked_key = f"{api_key[:15]}...{api_key[-4:]}" if len(api_key) > 20 else "***"
        else:
            masked_key = "None"

        console.print(Panel(
            f"[green]✓ Authenticated[/green]\n\n"
            f"Name: {user.get('full_name', 'N/A')}\n"
            f"Email: {user.get('email', 'N/A')}\n"
            f"Plan: {user.get('tier', 'free').title()}\n"
            f"API Key: {masked_key}",
            title="Authentication Status"
        ))
    else:
        console.print(Panel(
            "[red]✗ Not authenticated[/red]\n\n"
            "Run [bold]alprina auth login[/bold] to authenticate",
            title="Authentication Status"
        ))


def get_auth_headers() -> dict:
    """Get authentication headers for API requests."""
    auth_data = load_token()

    if not auth_data:
        console.print("[red]Not authenticated. Run 'alprina auth login' first.[/red]")
        raise Exception("Not authenticated")

    return {"Authorization": f"Bearer {auth_data['token']}"}


def is_authenticated() -> bool:
    """Check if user is authenticated."""
    return TOKEN_FILE.exists() and load_token() is not None


def login_with_browser():
    """
    Browser-based OAuth flow (like GitHub CLI).
    Opens browser for user to authorize, polls for completion.
    """
    import webbrowser
    import time

    backend_url = get_backend_url()

    try:
        # Step 1: Request device authorization
        console.print("\n[cyan]→[/cyan] Requesting device authorization...")

        response = httpx.post(f"{backend_url}/auth/device", timeout=10.0)

        if response.status_code != 200:
            console.print(f"[red]✗ Failed to request authorization: {response.status_code}[/red]")
            return

        data = response.json()
        device_code = data["device_code"]
        user_code = data["user_code"]
        verification_url = data["verification_url"]
        expires_in = data.get("expires_in", 900)
        interval = data.get("interval", 5)

        # Step 2: Display code and open browser
        console.print()
        console.print(Panel(
            f"[bold yellow]{user_code}[/bold yellow]",
            title="🔑 Your Verification Code",
            subtitle="Enter this code in your browser"
        ))
        console.print()
        console.print(f"[cyan]→[/cyan] Opening browser to: [dim]{verification_url}[/dim]")
        console.print(f"[dim]If browser doesn't open, visit manually[/dim]")
        console.print()

        # Open browser with code pre-filled (like GitHub CLI)
        url_with_code = f"{verification_url}?user_code={user_code}"
        try:
            webbrowser.open(url_with_code)
        except:
            console.print("[yellow]⚠️  Could not open browser automatically[/yellow]")
            console.print(f"[yellow]Please visit: {url_with_code}[/yellow]")

        # Step 3: Poll for authorization with progress indicator
        max_attempts = expires_in // interval  # Usually 180 attempts (15 minutes)
        
        console.print()
        console.print("[dim]Tip: Make sure you're logged into the website first![/dim]")
        console.print("[dim]Press Ctrl+C to cancel[/dim]")
        console.print()
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=False
            ) as progress:
                task = progress.add_task("Waiting for authorization...", total=None)
                
                for attempt in range(max_attempts):
                    time.sleep(interval)

                    try:
                        poll_response = httpx.post(
                            f"{backend_url}/auth/device/token",
                            json={"device_code": device_code},
                            timeout=10.0
                        )

                        if poll_response.status_code == 200:
                            # ✓ Authorized!
                            progress.update(task, description="[green]✓ Authorization successful![/green]")
                            
                            auth_data = poll_response.json()
                            api_key = auth_data["api_key"]
                            user = auth_data["user"]

                            # Save token
                            save_token(api_key, user)

                            # Show welcome screen
                            console.print()
                            show_welcome(force=True)
                            return

                        elif poll_response.status_code == 400:
                            error_data = poll_response.json()
                            error_type = error_data.get("detail", {})

                            if isinstance(error_type, dict):
                                error_code = error_type.get("error")

                                if error_code == "authorization_pending":
                                    # Still waiting...
                                    console.print(".", end="", style="dim")
                                    continue
                                elif error_code == "expired_token":
                                    console.print("\n[red]✗ Authorization expired. Please try again.[/red]")
                                    return
                            else:
                                console.print(f"\n[red]✗ Error: {error_type}[/red]")
                                return

                    except httpx.ReadTimeout:
                        console.print(".", end="", style="dim")
                        continue
                    except httpx.ConnectError:
                        console.print(f"\n[red]✗ Could not connect to backend[/red]")
                        return
                    except Exception as e:
                        console.print(".", end="", style="dim")
                        continue

                console.print("\n[red]✗ Authorization timed out. Please try again.[/red]")
        except KeyboardInterrupt:
            console.print("\n\n[yellow]Authorization cancelled by user.[/yellow]")
            console.print("[dim]You can try again with: alprina auth login[/dim]")
            return

    except httpx.ConnectError:
        console.print(f"[red]✗ Could not connect to Alprina backend at {backend_url}[/red]")
        console.print("[yellow]Make sure the API server is running[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
