"""
Friendly error messages for Alprina CLI.

All errors are user-friendly with clear solutions.
"""

from rich.console import Console
from rich.panel import Panel
from rich import box

console = Console()


class AlprinaError(Exception):
    """Base class for all Alprina CLI errors."""
    
    def __init__(self, message: str, solution: str = None, title: str = "Error"):
        self.message = message
        self.solution = solution
        self.title = title
        super().__init__(message)
    
    def display(self):
        """Display error with solution in a nice panel."""
        error_text = f"[bold red]❌ {self.message}[/bold red]"
        
        if self.solution:
            error_text += f"\n\n[yellow]💡 Solution:[/yellow]\n{self.solution}"
        
        console.print(Panel.fit(
            error_text,
            title=self.title,
            border_style="red",
            box=box.ROUNDED
        ))


class AuthenticationError(AlprinaError):
    """Raised when user is not authenticated."""
    
    def __init__(self):
        super().__init__(
            message="You're not signed in",
            solution="Run: [bold]alprina auth login[/bold]\n\n"
                     "Or get your API key from: https://platform.alprina.com/api-keys",
            title="Authentication Required"
        )


class RateLimitError(AlprinaError):
    """Raised when user hits rate limit."""
    
    def __init__(self, limit: int, reset_time: str = "in 1 hour"):
        super().__init__(
            message=f"You've reached your scan limit ({limit} scans)",
            solution=f"Your limit resets {reset_time}\n\n"
                     f"Or upgrade for more scans: [bold]https://alprina.com/pricing[/bold]",
            title="Rate Limit Reached"
        )


class APIError(AlprinaError):
    """Raised when API request fails."""
    
    def __init__(self, status_code: int, message: str = None):
        solutions = {
            400: "Check your request parameters",
            401: "Your API key is invalid or expired\nRun: [bold]alprina auth login[/bold]",
            403: "You don't have permission for this action\nUpgrade at: https://alprina.com/pricing",
            404: "The requested resource was not found",
            429: "Too many requests. Please wait a moment and try again",
            500: "Alprina server error. Please try again later\nIf this persists, contact support@alprina.com",
            503: "Alprina service is temporarily unavailable\nCheck status: https://status.alprina.com"
        }
        
        default_message = message or f"API request failed with status {status_code}"
        solution = solutions.get(status_code, "Please try again later\nIf this persists, contact support@alprina.com")
        
        super().__init__(
            message=default_message,
            solution=solution,
            title=f"API Error ({status_code})"
        )


class FileNotFoundError(AlprinaError):
    """Raised when target file/directory doesn't exist."""
    
    def __init__(self, path: str):
        super().__init__(
            message=f"File or directory not found: {path}",
            solution="Check the path and try again\n\n"
                     "Examples:\n"
                     "  [bold]alprina scan ./[/bold]     - Scan current directory\n"
                     "  [bold]alprina scan app.py[/bold] - Scan single file\n"
                     "  [bold]alprina scan src/[/bold]   - Scan src directory",
            title="File Not Found"
        )


class NetworkError(AlprinaError):
    """Raised when network request fails."""
    
    def __init__(self, details: str = None):
        message = "Cannot connect to Alprina API"
        if details:
            message += f": {details}"
        
        super().__init__(
            message=message,
            solution="Check your internet connection\n\n"
                     "If you're behind a proxy, set these environment variables:\n"
                     "  [bold]HTTP_PROXY=http://proxy:port[/bold]\n"
                     "  [bold]HTTPS_PROXY=https://proxy:port[/bold]\n\n"
                     "Still having issues? support@alprina.com",
            title="Network Error"
        )


class InvalidTierError(AlprinaError):
    """Raised when user's tier doesn't support a feature."""
    
    def __init__(self, feature: str, required_tier: str):
        super().__init__(
            message=f"This feature requires {required_tier} tier",
            solution=f"Upgrade to unlock {feature}:\n"
                     f"[bold]https://alprina.com/pricing[/bold]\n\n"
                     f"Or contact sales for custom plans:\n"
                     f"sales@alprina.com",
            title="Upgrade Required"
        )


class ScanError(AlprinaError):
    """Raised when scan fails."""
    
    def __init__(self, reason: str = None):
        message = "Security scan failed"
        if reason:
            message += f": {reason}"
        
        super().__init__(
            message=message,
            solution="Try again with verbose mode for more details:\n"
                     "[bold]alprina scan ./ --verbose[/bold]\n\n"
                     "Or check logs at:\n"
                     "~/.alprina/logs/alprina.log",
            title="Scan Failed"
        )


def handle_error(error: Exception, verbose: bool = False):
    """
    Handle any error and display it nicely.
    
    Args:
        error: The exception to handle
        verbose: Show full traceback
    """
    if isinstance(error, AlprinaError):
        error.display()
    elif isinstance(error, KeyboardInterrupt):
        console.print("\n[yellow]⚠️  Operation cancelled by user[/yellow]")
    elif isinstance(error, FileNotFoundError):
        FileNotFoundError(str(error)).display()
    else:
        # Generic error
        console.print(Panel.fit(
            f"[bold red]❌ Unexpected error:[/bold red]\n\n"
            f"{str(error)}\n\n"
            f"[yellow]💡 What to do:[/yellow]\n"
            f"1. Try running with [bold]--verbose[/bold] for more details\n"
            f"2. Check logs at [bold]~/.alprina/logs/alprina.log[/bold]\n"
            f"3. Report this bug: [bold]https://github.com/alprina/issues[/bold]",
            title="Error",
            border_style="red",
            box=box.ROUNDED
        ))
        
        if verbose:
            import traceback
            console.print("\n[dim]Full traceback:[/dim]")
            console.print(traceback.format_exc())
