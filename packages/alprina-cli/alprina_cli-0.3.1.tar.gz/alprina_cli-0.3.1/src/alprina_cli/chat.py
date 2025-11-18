"""
Interactive chat interface for Alprina.
Provides conversational AI assistant for security scanning.
"""

from typing import Optional
from pathlib import Path
import re
import sys

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.key_binding import KeyBindings
from loguru import logger

from .context_manager import ConversationContext
from .llm_provider import get_llm_client
from .scanner import scan_command
from .mitigation import mitigate_command
from .main_agent import MainAlprinaAgent

console = Console()


class AlprinaChatSession:
    """Interactive chat session with Alprina AI."""

    def __init__(
        self,
        model: str = "claude-3-5-sonnet-20241022",
        streaming: bool = True,
        context_file: Optional[Path] = None
    ):
        """
        Initialize chat session.

        Args:
            model: LLM model to use
            streaming: Enable streaming responses
            context_file: Load previous scan context
        """
        self.model = model
        self.streaming = streaming
        self.context = ConversationContext()
        self.llm = get_llm_client(model=model)

        # Session statistics
        self.stats = {
            "messages": 0,
            "tokens_used": 0,
            "estimated_cost": 0.0,
            "scans_run": 0,
            "start_time": None
        }
        
        import time
        self.stats["start_time"] = time.time()

        # Initialize Main Alprina Agent (orchestrator)
        self.main_agent = MainAlprinaAgent(model=model)
        logger.info("Main Alprina Agent initialized in chat session")

        # Set up prompt session with history
        history_file = Path.home() / '.alprina' / 'chat_history.txt'
        history_file.parent.mkdir(parents=True, exist_ok=True)

        self.session = PromptSession(
            history=FileHistory(str(history_file)),
            auto_suggest=AutoSuggestFromHistory(),
            key_bindings=self._create_key_bindings()
        )

        # Load context if provided
        if context_file:
            self.context.load_scan_results(context_file)

        logger.info(f"Chat session initialized with model: {model}")

    def _create_key_bindings(self):
        """Create custom key bindings."""
        kb = KeyBindings()

        @kb.add('c-c')
        def _(event):
            """Handle Ctrl+C gracefully."""
            event.app.exit()

        return kb

    def start(self):
        """Start interactive chat loop."""
        self._show_welcome()

        while True:
            try:
                # Get user input
                user_input = self.session.prompt("\n[bold green]You:[/bold green] ")

                if not user_input.strip():
                    continue

                # Check for exit
                if user_input.lower() in ['exit', 'quit', 'q', 'bye']:
                    self._handle_exit()
                    break

                # Handle special commands
                if user_input.startswith('/'):
                    self._handle_command(user_input)
                    continue

                # Process as chat message
                self._process_message(user_input)

            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'exit' or Ctrl+D to quit[/yellow]")
                continue
            except EOFError:
                self._handle_exit()
                break
            except Exception as e:
                logger.error(f"Chat error: {e}", exc_info=True)
                console.print(f"[red]Error: {e}[/red]")

    def _show_welcome(self):
        """Show welcome message with session info."""
        # Get auth status
        from .config import get_api_key
        api_key = get_api_key()
        auth_status = "✅ Authenticated" if api_key else "⚠️  Not authenticated"
        
        console.print(Panel.fit(
            "[bold cyan]🛡️  Hey! I'm Alprina, your security expert![/bold cyan]\n\n"
            f"[dim]Model:[/dim] {self.model}\n"
            f"[dim]Status:[/dim] {auth_status}\n"
            f"[dim]Session:[/dim] {self.stats['messages']} messages\n\n"
            "[bold]💬 Chat with me naturally, like:[/bold]\n"
            '  • "Scan my Python app for vulnerabilities"\n'
            '  • "What\'s SQL injection and how do I fix it?"\n'
            '  • "Find secrets in my code"\n'
            '  • "Explain finding #3"\n\n'
            "[bold]⚡ Quick commands:[/bold]\n"
            "  [cyan]/scan <path>[/cyan]  - Run security scan\n"
            "  [cyan]/status[/cyan]       - Show auth status\n"
            "  [cyan]/stats[/cyan]        - Show session stats\n"
            "  [cyan]/help[/cyan]         - Show all commands\n"
            "  [cyan]/exit[/cyan]         - Quit chat\n\n"
            "[dim]💡 Tip: I can explain vulnerabilities, show fixes, and even\n"
            "scan your code - just ask me in plain English![/dim]",
            title="🛡️  Alprina Interactive Chat",
            border_style="cyan"
        ))

        # Show context if loaded
        if self.context.scan_results:
            console.print(f"\n[cyan]📊 Context loaded:[/cyan] {self.context.get_context_summary()}\n")

    def _process_message(self, user_input: str):
        """
        Process user message using Main Alprina Agent (orchestrator).

        Args:
            user_input: User's message
        """
        # Update stats
        self.stats["messages"] += 1
        
        # Add to context
        self.context.add_user_message(user_input)

        console.print(f"\n[bold cyan]Alprina:[/bold cyan]")

        try:
            # Route request through Main Alprina Agent (orchestrator)
            logger.info("Routing request through Main Alprina Agent")

            # Prepare context for Main Agent
            agent_context = {
                "scan_results": self.context.scan_results,
                "conversation_history": self.context.get_messages_for_llm()
            }

            # Show enhanced thinking indicator with agent transparency
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=False  # Keep visible to show thinking process
            ) as progress:
                # Step 1: Analyze intent
                task = progress.add_task("[cyan]💭 Analyzing your request...", total=None)
                
                # Get intent first (to show which agents will be used)
                intent = self.main_agent._analyze_intent(user_input, agent_context)
                progress.update(task, description="[green]✓ Request analyzed")
                
                # Step 2: Show agent selection transparency
                if intent.get("agents"):
                    agent_names = []
                    for agent_key in intent["agents"]:
                        agent_info = self.main_agent.SECURITY_AGENTS.get(agent_key, {})
                        agent_names.append(agent_info.get("name", agent_key))
                    
                    agents_str = ", ".join(agent_names)
                    progress.add_task(f"[cyan]🤖 Selected agents: {agents_str}", total=None)
                    progress.add_task(f"[cyan]🎯 Task type: {intent.get('type', 'unknown')}", total=None)
                
                # Step 3: Execute with selected agents
                progress.add_task("[cyan]⚡ Executing security analysis...", total=None)
                
                # Main Agent processes request and coordinates with security agents
                response_data = self.main_agent.process_user_request(
                    user_message=user_input,
                    context=agent_context
                )
                
                progress.add_task("[green]✓ Analysis complete!", total=None)

            # Extract response message
            response_message = response_data.get("message", "")
            response_type = response_data.get("type", "general")

            # Display response based on type
            if response_type == "scan_complete":
                # Scan was executed - display results
                console.print(Markdown(response_message))

                # Update context with scan results if available
                if response_data.get("results"):
                    self.context.scan_results = response_data["results"]

            elif response_type == "clarification_needed":
                # Main Agent needs more info
                console.print(f"[yellow]{response_message}[/yellow]")

            elif response_type == "error":
                # Error occurred
                console.print(f"[red]{response_message}[/red]")

            else:
                # General response, explanation, remediation, capabilities, etc.
                console.print(Markdown(response_message))

            # Add response to context
            self.context.add_assistant_message(response_message)

        except Exception as e:
            logger.error(f"Main Agent processing failed: {e}", exc_info=True)
            console.print(f"[red]Error: {str(e)}[/red]")
            console.print("[yellow]Falling back to direct LLM response...[/yellow]")

            # Fallback to old behavior
            if self.streaming:
                response = self._get_streaming_response(user_input)
            else:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                    transient=True
                ) as progress:
                    progress.add_task("Thinking...", total=None)
                    response = self._get_response(user_input)

                console.print(Markdown(response))

            self.context.add_assistant_message(response)

    def _get_response(self, user_input: str) -> str:
        """
        Get AI response (non-streaming).

        Args:
            user_input: User's message

        Returns:
            AI response text
        """
        try:
            system_prompt = self._build_system_prompt()
            messages = self.context.get_messages_for_llm()

            response = self.llm.chat(
                messages=messages,
                system_prompt=system_prompt,
                max_tokens=4096,
                temperature=0.7
            )

            return response
        except Exception as e:
            logger.error(f"Failed to get AI response: {e}")
            return f"I encountered an error: {e}. Please try again."

    def _get_streaming_response(self, user_input: str) -> str:
        """
        Get AI response with streaming.

        Args:
            user_input: User's message

        Returns:
            Full AI response text
        """
        try:
            system_prompt = self._build_system_prompt()
            messages = self.context.get_messages_for_llm()

            full_response = ""
            for chunk in self.llm.chat_streaming(
                messages=messages,
                system_prompt=system_prompt,
                max_tokens=4096,
                temperature=0.7
            ):
                console.print(chunk, end="")
                full_response += chunk

            console.print()  # Newline after streaming
            return full_response

        except Exception as e:
            logger.error(f"Failed to get streaming response: {e}")
            return f"\n\nI encountered an error: {e}. Please try again."

    def _build_system_prompt(self) -> str:
        """
        Build context-aware system prompt.

        Returns:
            System prompt string
        """
        base_prompt = """You are Alprina, an expert security consultant with 20+ years of cybersecurity experience.

## YOUR PERSONALITY:

You're **friendly but professional** - like a senior security engineer who:
- Gets excited about finding (and fixing) vulnerabilities 🛡️
- Explains complex security concepts simply
- Shares war stories and real-world examples
- Celebrates when users secure their code
- Never judges - everyone's learning!

You're **patient and educational** - you:
- Break down jargon into plain English
- Use analogies that developers understand
- Show code examples (not just theory)
- Encourage good security practices
- Make security feel achievable, not scary

You're **practical and actionable** - you:
- Provide copy/paste code fixes
- Prioritize high-impact issues first
- Suggest realistic security improvements
- Know when "perfect" is the enemy of "good enough"
- Focus on what matters most

## COMMUNICATION STYLE:

**Think out loud**: Share your reasoning process
- "I'm going to scan this with CodeAgent because..."
- "Looking at this code, I notice..."
- "Let me check for SQL injection first, then XSS..."

**Be conversational**: Talk like a real person
- Instead of: "SQL injection vulnerability detected"
- Say: "Uh oh, I found a SQL injection here. This is serious - an attacker could steal your entire database!"

**Show, don't just tell**: Use examples
- Instead of: "Use parameterized queries"
- Say: "Replace `query = f'SELECT * FROM users WHERE id={user_id}'` with `cursor.execute('SELECT * FROM users WHERE id=?', (user_id,))`"

**End with next steps**: Always give users options
- "Want me to scan the rest of your app?"
- "Should I explain how this attack works?"
- "Need help implementing this fix?"

## ALPRINA SECURITY AGENTS YOU COORDINATE:

### 1. CodeAgent (code-audit)
   - SAST (Static Application Security Testing)
   - Detects: SQL injection, XSS, CSRF, authentication flaws
   - Analyzes: Python, JavaScript, Java, Go, PHP, Ruby, Rust, C/C++
   - Finds: Hardcoded secrets, insecure cryptography, input validation issues
   - Scans: Dependencies for known CVEs

### 2. Web Scanner Agent (web-recon)
   - API endpoint security testing
   - Authentication bypass detection
   - Rate limiting analysis
   - CORS misconfiguration detection
   - Session management vulnerabilities
   - HTTP security headers validation

### 3. Bug Bounty Agent (vuln-scan)
   - OWASP Top 10 vulnerability detection
   - Business logic flaws
   - Authorization issues
   - Information disclosure
   - Server misconfigurations

### 4. Secret Detection Agent
   - API keys, tokens, passwords in code
   - AWS credentials, database connection strings
   - Private keys, certificates
   - Slack tokens, GitHub tokens
   - Regex-based + entropy analysis

### 5. Config Audit Agent
   - Docker security configurations
   - Kubernetes manifests
   - CI/CD pipeline security
   - Environment variable exposure
   - Cloud infrastructure misconfigurations

## VULNERABILITY CATEGORIES YOU DETECT:

**Critical:** SQL Injection, RCE, Authentication Bypass, Hardcoded Credentials, SSRF
**High:** XSS, CSRF, Insecure Deserialization, XXE, Path Traversal
**Medium:** Security Misconfiguration, Sensitive Data Exposure, Missing Headers, Weak Crypto
**Low:** Information Disclosure, Missing Rate Limiting, Verbose Errors, Outdated Dependencies

## REPORTING CAPABILITIES:

You automatically generate professional security reports in the `.alprina/` folder:
- **SECURITY-REPORT.md** - Full vulnerability report with severity breakdown
- **FINDINGS.md** - Detailed findings with code snippets and CWE references
- **REMEDIATION.md** - Step-by-step fix instructions with code examples
- **EXECUTIVE-SUMMARY.md** - Non-technical overview for stakeholders

These reports also sync to the dashboard at https://dashboard.alprina.ai

## YOUR COMMUNICATION STYLE:

**When users ask "What can you do?" or "Help":**
- Be conversational, not robotic
- Give real examples they can try immediately
- Explain capabilities in plain English
- Offer next steps

**When explaining vulnerabilities:**
- Start with "What it is" (simple explanation)
- Show "How it works" (real attack example)
- Provide "The fix" (code you can copy/paste)
- End with "Want me to scan your code?"

**When providing fixes:**
- Show vulnerable code vs. secure code side-by-side
- Explain WHY the fix works
- Include best practices
- Offer to scan after they implement the fix

## NATURAL LANGUAGE UNDERSTANDING:

You understand requests like:
- "Scan my code" → Run CodeAgent on local files
- "Check my API" → Run Web Scanner Agent
- "Find hardcoded secrets" → Run Secret Detection Agent
- "What's SQL injection?" → Educational explanation
- "How do I fix finding #3?" → Provide remediation for specific finding
- "Create a security report" → Generate markdown reports in .alprina/ folder

## REMEMBER:

- Your goal is to make security accessible to ALL developers
- Explain complex concepts in simple terms
- Provide actionable, copy/paste solutions
- Generate reports automatically in .alprina/ folder
- Save everything to dashboard for tracking
- Be patient and encouraging
- Use analogies and real-world examples
- End responses with helpful next steps

Think of yourself as a friendly security expert who's here to help, teach, and protect - not to intimidate or overwhelm."""

        # Add scan context if available
        if self.context.scan_results:
            context_info = self.context.get_detailed_context()
            base_prompt += f"\n\nCurrent Scan Context:\n{context_info}"

        return base_prompt

    def _is_scan_request(self, text: str) -> bool:
        """Check if user wants to run a scan."""
        scan_keywords = ['scan', 'analyze', 'check', 'test', 'audit']
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in scan_keywords) and \
               ('my' in text_lower or './' in text or 'http' in text_lower or 'file' in text_lower)

    def _is_mitigation_request(self, text: str) -> bool:
        """Check if user wants mitigation steps."""
        mitigation_keywords = ['fix', 'remediate', 'solve', 'patch', 'how to fix']
        return any(keyword in text.lower() for keyword in mitigation_keywords)

    def _handle_scan_request(self, user_input: str):
        """Handle scan request from natural language."""
        # Try to extract target from user input
        target = self._extract_target(user_input)

        if not target:
            console.print("[yellow]I'd be happy to run a scan! What would you like me to scan?[/yellow]")
            console.print("[dim]Example: ./src, https://api.example.com, or /path/to/file[/dim]")
            return

        console.print(f"\n[cyan]→ Running security scan on:[/cyan] {target}\n")

        # Determine profile based on target
        profile = "code-audit" if Path(target).exists() else "web-recon"

        # Run scan (this will use the existing scan_command)
        try:
            scan_command(target, profile=profile, safe_only=True, output=None)

            # The scan results would be captured here
            # For now, simulate adding to context
            console.print(f"\n[green]✓ Scan complete![/green]")
            console.print("[dim]Type 'explain' to learn about findings or 'fix' for remediation steps[/dim]\n")

        except Exception as e:
            console.print(f"[red]Scan failed: {e}[/red]")
            logger.error(f"Scan failed: {e}", exc_info=True)

    def _handle_mitigation_request(self, user_input: str):
        """Handle mitigation request."""
        console.print("\n[cyan]→ Getting remediation suggestions...[/cyan]\n")

        try:
            # Run mitigation command
            mitigate_command(finding_id=None, report_file=None)

        except Exception as e:
            console.print(f"[red]Failed to get mitigation: {e}[/red]")
            logger.error(f"Mitigation failed: {e}", exc_info=True)

    def _extract_target(self, text: str) -> Optional[str]:
        """Extract scan target from natural language."""
        # Look for file paths
        file_pattern = r'\.\/[\w\/\-\.]+'
        match = re.search(file_pattern, text)
        if match:
            return match.group(0)

        # Look for URLs
        url_pattern = r'https?://[\w\-\.\/]+'
        match = re.search(url_pattern, text)
        if match:
            return match.group(0)

        # Look for absolute paths
        path_pattern = r'/[\w\/\-\.]+'
        match = re.search(path_pattern, text)
        if match:
            return match.group(0)

        return None

    def _handle_command(self, command: str):
        """
        Handle special chat commands.

        Args:
            command: Command string starting with /
        """
        cmd_parts = command.split()
        cmd_name = cmd_parts[0].lower()

        if cmd_name == '/help':
            self._show_help()
        elif cmd_name == '/status':
            self._show_status()
        elif cmd_name == '/scan':
            if len(cmd_parts) < 2:
                console.print("[yellow]Usage: /scan <target>[/yellow]")
            else:
                target = cmd_parts[1]
                self._handle_scan_request(f"scan {target}")
        elif cmd_name == '/explain':
            if len(cmd_parts) < 2:
                self._show_findings()
            else:
                finding_id = cmd_parts[1]
                self._explain_finding(finding_id)
        elif cmd_name == '/fix':
            if len(cmd_parts) < 2:
                console.print("[yellow]Usage: /fix <finding_id>[/yellow]")
            else:
                finding_id = cmd_parts[1]
                self._fix_finding(finding_id)
        elif cmd_name == '/report':
            self._show_report()
        elif cmd_name == '/clear':
            self.context.clear()
            console.print("[green]✓ Conversation history cleared[/green]")
        elif cmd_name == '/stats':
            self._show_stats()
        elif cmd_name == '/save':
            self._save_conversation()
        elif cmd_name == '/exit' or cmd_name == '/quit':
            self._handle_exit()
            raise EOFError  # Signal to exit the chat loop
        else:
            console.print(f"[red]Unknown command: {cmd_name}[/red]")
            console.print("[dim]Type /help for available commands[/dim]")

    def _show_help(self):
        """Show help message."""
        help_table = Table(title="Available Commands", show_header=True, header_style="bold cyan", title_style="bold cyan")
        help_table.add_column("Command", style="cyan", no_wrap=True)
        help_table.add_column("Description", style="white")

        commands = [
            ("/help", "Show this help message"),
            ("/status", "Show authentication status"),
            ("/scan <path>", "Run security scan on file or directory"),
            ("/explain [id]", "Explain vulnerability finding (or list all)"),
            ("/fix <id>", "Get AI-powered fix for specific finding"),
            ("/report", "Show current scan summary report"),
            ("/clear", "Clear conversation history"),
            ("/stats", "Show session statistics (messages, tokens, cost)"),
            ("/save", "Save conversation to file"),
            ("/exit, /quit", "Exit chat session"),
            ("exit, quit, bye", "Exit chat session"),
        ]

        for cmd, desc in commands:
            help_table.add_row(cmd, desc)

        console.print(help_table)

    def _show_findings(self):
        """Show current scan findings."""
        if not self.context.current_findings:
            console.print("[yellow]No scan findings available. Run a scan first![/yellow]")
            return

        findings_table = Table(title="Current Findings", show_header=True, header_style="bold")
        findings_table.add_column("ID", style="dim")
        findings_table.add_column("Severity")
        findings_table.add_column("Title")
        findings_table.add_column("File", style="dim")

        for finding in self.context.current_findings:
            severity_style = {
                'HIGH': 'bold red',
                'MEDIUM': 'bold yellow',
                'LOW': 'bold green'
            }.get(finding.get('severity', 'UNKNOWN'), 'white')

            findings_table.add_row(
                finding.get('id', 'N/A'),
                f"[{severity_style}]{finding.get('severity', 'UNKNOWN')}[/{severity_style}]",
                finding.get('title', 'Unknown'),
                finding.get('file', 'N/A')
            )

        console.print(findings_table)

    def _explain_finding(self, finding_id: str):
        """Explain specific finding."""
        finding = self.context.get_finding(finding_id)
        if not finding:
            console.print(f"[red]Finding {finding_id} not found[/red]")
            return

        # Use AI to explain the finding
        explanation_request = f"Can you explain this security finding in detail?\n\n{finding}"
        self._process_message(explanation_request)

    def _fix_finding(self, finding_id: str):
        """Get fix for specific finding."""
        finding = self.context.get_finding(finding_id)
        if not finding:
            console.print(f"[red]Finding {finding_id} not found[/red]")
            return

        # Use AI to provide fix
        fix_request = f"How can I fix this security vulnerability?\n\n{finding}"
        self._process_message(fix_request)

    def _show_report(self):
        """Show scan report summary."""
        if not self.context.scan_results:
            console.print("[yellow]No scan results available[/yellow]")
            return

        summary = self.context.get_context_summary()
        console.print(Panel(
            f"[bold]Scan Report[/bold]\n\n{summary}",
            border_style="cyan"
        ))

    def _show_status(self):
        """Show authentication status."""
        from .auth import load_token
        
        auth_data = load_token()
        
        if auth_data:
            user = auth_data.get("user", {})
            api_key = auth_data.get("token", "")
            
            # Show masked API key
            if api_key:
                masked_key = f"{api_key[:15]}...{api_key[-4:]}" if len(api_key) > 20 else "***"
            else:
                masked_key = "None"
            
            console.print(Panel.fit(
                f"[green]✅ Authenticated[/green]\n\n"
                f"[dim]Email:[/dim] {user.get('email', 'N/A')}\n"
                f"[dim]Name:[/dim] {user.get('full_name', 'N/A')}\n"
                f"[dim]Tier:[/dim] {user.get('tier', 'free').title()}\n"
                f"[dim]API Key:[/dim] {masked_key}",
                title="Authentication Status",
                border_style="green"
            ))
        else:
            from .utils.errors import show_not_authenticated_error
            show_not_authenticated_error()
    
    def _show_stats(self):
        """Show session statistics."""
        import time
        
        # Calculate session duration
        duration = time.time() - self.stats["start_time"]
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        
        if hours > 0:
            duration_str = f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            duration_str = f"{minutes}m {seconds}s"
        else:
            duration_str = f"{seconds}s"
        
        # Get context stats
        context_stats = self.context.get_statistics()
        
        stats_table = Table(title="📊 Session Statistics", show_header=False, title_style="bold cyan")
        stats_table.add_column("Metric", style="cyan", no_wrap=True)
        stats_table.add_column("Value", style="bold white")

        stats_table.add_row("Messages", str(self.stats['messages']))
        stats_table.add_row("  └─ User", str(context_stats.get('user_messages', 0)))
        stats_table.add_row("  └─ Assistant", str(context_stats.get('assistant_messages', 0)))
        stats_table.add_row("", "")  # Spacer
        stats_table.add_row("Scans Run", str(self.stats['scans_run']))
        stats_table.add_row("Findings", str(context_stats.get('total_findings', 0)))
        stats_table.add_row("  └─ Critical/High", f"[red]{context_stats.get('high_severity', 0)}[/red]")
        stats_table.add_row("  └─ Medium", f"[yellow]{context_stats.get('medium_severity', 0)}[/yellow]")
        stats_table.add_row("  └─ Low", f"[green]{context_stats.get('low_severity', 0)}[/green]")
        stats_table.add_row("", "")  # Spacer
        stats_table.add_row("Session Duration", duration_str)
        stats_table.add_row("Model", self.model)
        
        # Estimate tokens and cost (rough estimates)
        if self.stats['tokens_used'] > 0:
            stats_table.add_row("Tokens Used", f"~{self.stats['tokens_used']:,}")
            stats_table.add_row("Estimated Cost", f"${self.stats['estimated_cost']:.4f}")

        console.print(stats_table)

    def _save_conversation(self):
        """Save conversation to file."""
        output_file = Path.home() / '.alprina' / 'conversations' / f"chat_{self.context.session_start.strftime('%Y%m%d_%H%M%S')}.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        self.context.save_conversation(output_file)
        console.print(f"[green]✓ Conversation saved to:[/green] {output_file}")

    def _handle_exit(self):
        """Handle exit gracefully."""
        stats = self.context.get_statistics()
        console.print(f"\n[cyan]Thanks for using Alprina![/cyan]")
        console.print(f"[dim]Session stats: {stats['total_messages']} messages, {stats['session_duration']:.0f}s duration[/dim]")
        console.print("[dim]💾 Use /save before exit to save your conversation[/dim]\n")


def chat_command(
    model: str = "claude-3-5-sonnet-20241022",
    streaming: bool = True,
    load_results: Optional[Path] = None
):
    """
    Start interactive chat session with Alprina AI.

    Args:
        model: LLM model to use
        streaming: Enable streaming responses
        load_results: Load previous scan results for context
    """
    try:
        session = AlprinaChatSession(
            model=model,
            streaming=streaming,
            context_file=load_results
        )
        session.start()
    except Exception as e:
        logger.error(f"Chat session error: {e}", exc_info=True)
        console.print(f"[red]Chat error: {e}[/red]")
        sys.exit(1)
