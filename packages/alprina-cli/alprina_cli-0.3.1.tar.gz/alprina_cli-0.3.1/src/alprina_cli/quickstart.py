"""
Interactive quickstart tutorial for new users.
Guides users through their first security scan with explanations.
"""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.markdown import Markdown
from pathlib import Path
import shutil
import time

console = Console()

class QuickstartTutorial:
    """Interactive tutorial for first-time users."""
    
    def __init__(self):
        self.demo_app_path = None
        
    def run(self):
        """Run the complete tutorial."""
        self._show_welcome()
        
        choice = self._choose_scan_type()
        
        if choice == "4":  # Demo app
            self._run_demo_scan()
        elif choice == "1":  # Website
            self._run_website_scan()
        elif choice == "2":  # Local directory
            self._run_directory_scan()
        elif choice == "3":  # Single file
            self._run_file_scan()
            
        self._show_next_steps()
    
    def _show_welcome(self):
        """Show welcome message."""
        console.print(Panel(
            "[bold cyan]🎓 Alprina Quick Start Tutorial[/bold cyan]\n\n"
            "Welcome! Let's run your first security scan together.\n\n"
            "This tutorial will:\n"
            "  • Show you how Alprina finds vulnerabilities\n"
            "  • Explain security issues in plain English\n"
            "  • Teach you how to fix common problems\n\n"
            "[dim]Takes ~3 minutes[/dim]",
            border_style="cyan",
            title="Welcome to Alprina"
        ))
        console.print()
    
    def _choose_scan_type(self) -> str:
        """Let user choose what to scan."""
        console.print("[bold]What would you like to scan?[/bold]\n")
        console.print("  [cyan]1.[/cyan] 🌐 A website or API (example: https://example.com)")
        console.print("  [cyan]2.[/cyan] 📁 A local directory (example: ./my-project)")
        console.print("  [cyan]3.[/cyan] 📄 A single file (example: app.py)")
        console.print("  [cyan]4.[/cyan] 🎯 Use a demo vulnerable app [bold cyan](recommended for learning)[/bold cyan]")
        console.print()
        
        choice = Prompt.ask(
            "Choice",
            choices=["1", "2", "3", "4"],
            default="4"
        )
        return choice
    
    def _run_demo_scan(self):
        """Run scan on demo vulnerable app."""
        console.print("\n[cyan]✓ Great choice! We'll scan a demo app to show you what Alprina can find.[/cyan]\n")
        
        # Extract demo app to temp location
        demo_dir = Path.home() / ".alprina" / "demo"
        demo_dir.mkdir(parents=True, exist_ok=True)
        
        demo_file = demo_dir / "vulnerable_app.py"
        
        # Copy demo app
        import alprina_cli.demo_app as demo_app_module
        demo_app_source = Path(demo_app_module.__file__).parent / "vulnerable_app.py"
        shutil.copy(demo_app_source, demo_file)
        
        self.demo_app_path = demo_file
        
        console.print(f"[dim]Demo app created at: {demo_file}[/dim]\n")
        
        # Run quick scan
        console.print("🔍 [bold]Scanning demo app for vulnerabilities...[/bold]")
        
        from .quick_scanner import quick_scan
        
        # Show fake progress for better UX
        with console.status("[cyan]Analyzing code with AI agents...", spinner="dots") as status:
            time.sleep(0.5)  # Dramatic pause
            results = quick_scan(str(demo_file))
            time.sleep(0.5)  # Let them see "complete"
        
        console.print("✓ [bold green]Scan complete![/bold green]\n")
        
        # Display results with explanations
        self._explain_demo_results(results)
    
    def _explain_demo_results(self, results: dict):
        """Explain the demo scan results interactively."""
        duration = results['duration_ms'] / 1000
        critical_count = results['summary']['critical']
        
        console.print(Panel(
            f"[bold]🎉 Scan Complete in {duration:.1f}s![/bold]\n\n"
            f"Found [bold red]{critical_count}[/bold red] critical vulnerabilities\n"
            f"in the demo app. Let's look at them together:",
            style="green",
            border_style="green"
        ))
        console.print()
        
        # Show each finding with detailed explanation
        findings_to_show = min(3, len(results['findings']))
        
        for i, finding in enumerate(results['findings'][:findings_to_show], 1):
            console.print(f"[bold cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold cyan]")
            console.print(f"[bold yellow]Finding #{i}: {finding['title']}[/bold yellow]")
            console.print(f"[dim]Location:[/dim] Line {finding['line']}")
            console.print(f"[dim]Vulnerable code:[/dim]")
            console.print(f"  [red]{finding['code_snippet']}[/red]\n")
            
            # Get simple explanation
            explanation = self._get_simple_explanation(finding['pattern'])
            console.print(explanation)
            console.print()
            
            if i < findings_to_show:
                if not Confirm.ask("[dim]Continue to next finding?[/dim]", default=True):
                    break
                console.print()
        
        # Show summary
        if len(results['findings']) > findings_to_show:
            remaining = len(results['findings']) - findings_to_show
            console.print(f"[dim]+ {remaining} more vulnerabilities found (shown in full scan)[/dim]\n")
    
    def _get_simple_explanation(self, pattern: str) -> str:
        """Get beginner-friendly explanation with analogies."""
        explanations = {
            "sql_injection": (
                "[bold]🤔 What is SQL Injection?[/bold]\n\n"
                "Imagine your code is like a waiter taking orders at a restaurant.\n"
                "A SQL injection is when a malicious customer tricks the waiter into\n"
                "changing the order to steal food from the kitchen!\n\n"
                "In this code, user input goes directly into the database query.\n"
                "An attacker could type: [yellow]admin' OR '1'='1[/yellow] as the username\n"
                "to log in without knowing the password.\n\n"
                "[bold]⚡ How to Fix:[/bold]\n"
                "Use 'prepared statements' (like a menu the kitchen knows):\n"
                "  [green]query = \"SELECT * FROM users WHERE name=%s\"[/green]\n"
                "  [green]cursor.execute(query, (username,))[/green]\n\n"
                "[dim]This tells the database: \"This is DATA, not COMMANDS\"[/dim]"
            ),
            "hardcoded_secrets": (
                "[bold]🤔 What are Hardcoded Secrets?[/bold]\n\n"
                "It's like writing your password on a sticky note and leaving it\n"
                "on your desk where anyone can see it. If someone sees your code\n"
                "(on GitHub, or if they hack in), they can steal your secrets!\n\n"
                "This code has a JWT secret key right in the source code.\n"
                "Anyone with access to the code can impersonate any user.\n\n"
                "[bold]⚡ How to Fix:[/bold]\n"
                "Store secrets in environment variables:\n"
                "  [green]JWT_SECRET = os.getenv('JWT_SECRET')[/green]\n\n"
                "[dim]Keep secrets out of your code, in .env files (never commit these!)[/dim]"
            ),
            "xss_vulnerability": (
                "[bold]🤔 What is XSS (Cross-Site Scripting)?[/bold]\n\n"
                "It's like letting a stranger write graffiti on your whiteboard.\n"
                "They could write something malicious that tricks your visitors!\n\n"
                "This code takes user comments and displays them directly in HTML.\n"
                "An attacker could submit: [yellow]<script>stealPasswords()</script>[/yellow]\n"
                "and it would run on everyone's browser.\n\n"
                "[bold]⚡ How to Fix:[/bold]\n"
                "Sanitize user input before displaying:\n"
                "  [green]from markupsafe import escape[/green]\n"
                "  [green]safe_comment = escape(user_comment)[/green]\n\n"
                "[dim]Or use a template engine that auto-escapes (like Jinja2)[/dim]"
            ),
            "command_injection": (
                "[bold]🤔 What is Command Injection?[/bold]\n\n"
                "It's like giving a stranger the keys to your car and saying\n"
                "\"just drive to the store\". They could go anywhere!\n\n"
                "This code runs system commands with user input. An attacker\n"
                "could type: [yellow]google.com; rm -rf /[/yellow] to delete everything.\n\n"
                "[bold]⚡ How to Fix:[/bold]\n"
                "Use safe libraries instead of shell commands:\n"
                "  [green]import subprocess[/green]\n"
                "  [green]subprocess.run(['ping', '-c', '1', host], shell=False)[/green]\n\n"
                "[dim]Never use shell=True with user input![/dim]"
            ),
            "path_traversal": (
                "[bold]🤔 What is Path Traversal?[/bold]\n\n"
                "It's like asking someone to get a book from your bedroom,\n"
                "but they sneak into your neighbor's house instead!\n\n"
                "This code lets users specify file names. An attacker could use\n"
                "[yellow]../../../etc/passwd[/yellow] to read system files.\n\n"
                "[bold]⚡ How to Fix:[/bold]\n"
                "Validate and sanitize file paths:\n"
                "  [green]from pathlib import Path[/green]\n"
                "  [green]safe_path = Path('data').resolve() / filename[/green]\n"
                "  [green]if not safe_path.is_relative_to(Path('data').resolve()):[/green]\n"
                "  [green]    raise ValueError('Invalid path')[/green]"
            ),
        }
        return explanations.get(pattern, f"[yellow]Pattern: {pattern}[/yellow]")
    
    def _run_website_scan(self):
        """Guide user through website scan."""
        console.print("\n[cyan]Let's scan a website or API.[/cyan]\n")
        target = Prompt.ask("Enter the URL", default="https://example.com")
        
        console.print(f"\n[dim]You can scan this later with:[/dim]")
        console.print(f"[bold cyan]alprina scan {target}[/bold cyan]\n")
        
        self._show_next_steps()
    
    def _run_directory_scan(self):
        """Guide user through directory scan."""
        console.print("\n[cyan]Let's scan a local directory.[/cyan]\n")
        target = Prompt.ask("Enter the directory path", default="./")
        
        console.print(f"\n[dim]You can scan this with:[/dim]")
        console.print(f"[bold cyan]alprina scan {target}[/bold cyan]\n")
        
        self._show_next_steps()
    
    def _run_file_scan(self):
        """Guide user through single file scan."""
        console.print("\n[cyan]Let's scan a single file.[/cyan]\n")
        target = Prompt.ask("Enter the file path", default="app.py")
        
        console.print(f"\n[dim]You can scan this with:[/dim]")
        console.print(f"[bold cyan]alprina scan {target}[/bold cyan]\n")
        
        self._show_next_steps()
    
    def _show_next_steps(self):
        """Show what user should do next."""
        console.print(Panel(
            "[bold cyan]🎯 What's Next?[/bold cyan]\n\n"
            "Now that you've seen how Alprina works, here's what to do:\n\n"
            "[bold]1️⃣  Scan your own project:[/bold]\n"
            "   [cyan]alprina scan ./your-project[/cyan]\n\n"
            "[bold]2️⃣  Try a quick health check (5 seconds):[/bold]\n"
            "   [cyan]alprina scan ./your-project --quick[/cyan]\n\n"
            "[bold]3️⃣  Chat with Alprina AI for help:[/bold]\n"
            "   [cyan]alprina chat[/cyan]\n\n"
            "[bold]4️⃣  View your dashboard:[/bold]\n"
            "   [cyan]https://alprina.com/dashboard[/cyan]\n\n"
            "[bold]5️⃣  Get help anytime:[/bold]\n"
            "   [cyan]alprina --help[/cyan]\n\n"
            "[dim]💡 Pro tip: Run scans before deploying to catch issues early![/dim]",
            border_style="cyan",
            title="You're All Set!"
        ))
        
        # Optionally mark tutorial as complete
        self._mark_tutorial_complete()
    
    def _mark_tutorial_complete(self):
        """Mark tutorial as completed (fire and forget)."""
        try:
            # Could call API to track tutorial completion
            # from .api_client import api_request
            # api_request("POST", "/api/v1/users/tutorial/complete", {"step": "quickstart"})
            pass
        except:
            pass  # Fail silently if offline or error


def quickstart_command():
    """Run the quickstart tutorial."""
    tutorial = QuickstartTutorial()
    tutorial.run()
