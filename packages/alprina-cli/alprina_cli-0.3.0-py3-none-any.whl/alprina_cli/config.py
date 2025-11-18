"""
Configuration management for Alprina CLI.
"""

import yaml
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

console = Console()

ALPRINA_DIR = Path.home() / ".alprina"
CONFIG_FILE = ALPRINA_DIR / "config.json"

DEFAULT_CONFIG = {
    "version": "0.1.0",
    "backend_url": "https://api.alprina.ai",
    "timeout": 30,
    "max_retries": 3,
    "log_level": "INFO",
    "theme": "dark",
    "memory": {
        "enabled": True,
        "api_key": "",  # Set via environment variable MEM0_API_KEY
        "user_id": "default"
    }
}


def load_config() -> dict:
    """Load configuration from file."""
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, "r") as f:
            import json
            config = json.load(f)
        return {**DEFAULT_CONFIG, **config}
    except Exception as e:
        console.print(f"[yellow]Warning: Could not load config: {e}[/yellow]")
        return DEFAULT_CONFIG.copy()


def save_config(config: dict):
    """Save configuration to file."""
    ALPRINA_DIR.mkdir(exist_ok=True)

    import json
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def get_api_key() -> str:
    """
    Get API key from environment variable or auth file.
    
    Returns:
        API key string or None if not found
    """
    # Check environment variable first
    api_key = os.getenv("ALPRINA_API_KEY")
    if api_key:
        return api_key
    
    # Check auth file
    auth_file = ALPRINA_DIR / "auth.json"
    if auth_file.exists():
        try:
            import json
            with open(auth_file, "r") as f:
                auth_data = json.load(f)
            return auth_data.get("api_key")
        except Exception:
            pass
    
    return None


def init_config_command():
    """Initialize default configuration."""
    if CONFIG_FILE.exists():
        from rich.prompt import Confirm
        if not Confirm.ask("Config file already exists. Overwrite?", default=False):
            return

    save_config(DEFAULT_CONFIG)

    console.print(Panel(
        f"[green]✓ Configuration initialized[/green]\n\n"
        f"Location: {CONFIG_FILE}\n\n"
        f"Edit this file to customize Alprina settings.",
        title="Config Initialized"
    ))
