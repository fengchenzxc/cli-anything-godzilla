"""
Unified REPL skin for cli-anything-godzilla.

A minimal prompt_toolkit-based REPL skin that provides branded startup box,
formatted help listing, messages, and progress bar, and styled goodbye message.
"""

import sys
import os
from typing import Optional, Dict, Any, List

try:
    from prompt_toolkit import PromptSession, print_formatted_text, prompt
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.formatted_text import HTML
    HAS_PROMPT_TOOLKIT = True
except ImportError:
    HAS_PROMPT_TOOLKIT = False
    PromptSession = None
    print_formatted_text = print
    FileHistory = None
    AutoSuggestFromHistory = None


class ReplSkin:
    """Unified REPL skin with branded interface for cli-anything."""

    def __init__(self, app_name: str, version: str = "1.0.0"):
        self.app_name = app_name
        self.version = version
        self.session: Optional[Any] = None
        self.history_file: Optional[str] = None
        self._setup_history()

    def _setup_history(self) -> None:
        """Setup command history."""
        if not HAS_PROMPT_TOOLKIT:
            return

        history_dir = os.path.expanduser("~/.cli_anything/history")
        os.makedirs(history_dir, exist_ok=True)
        self.history_file = os.path.join(history_dir, f"{self.app_name}.history")

    def create_prompt_session(self) -> Optional[Any]:
        """Create a prompt session with history."""
        if not HAS_PROMPT_TOOLKIT:
            return None

        history = None
        if self.history_file and FileHistory:
            history = FileHistory(self.history_file)

        self.session = PromptSession(
            history=history,
            auto_suggest=AutoSuggestFromHistory() if AutoSuggestFromHistory else None,
        )
        return self.session

    def get_input(
        self,
        session: Optional[Any] = None,
        project_name: Optional[str] = None,
        modified: bool = False,
    ) -> str:
        """Get user input with styled prompt."""
        if not HAS_PROMPT_TOOLKIT:
            try:
                return input(f"{self.app_name}> ")
            except EOFError:
                return "exit"

        prompt_text = f"{self.app_name}"
        if project_name:
            prompt_text += f":{project_name}"
        if modified:
            prompt_text += "*"
        prompt_text += "> "

        try:
            return session.prompt(prompt_text) if session else input(prompt_text)
        except EOFError:
            return "exit"
        except KeyboardInterrupt:
            return ""

    def print_banner(self) -> None:
        """Print the branded startup box."""
        banner = f"""
╔══════════════════════════════════════════════════════════════╗
║  {self.app_name.upper():^54}  ║
║  {"Version: " + self.version:^54}  ║
║  {"CLI Harness for Godzilla Security Testing Tool":^54}  ║
╚══════════════════════════════════════════════════════════════╝
"""
        print(f"\033[36m{banner}\033[0m")

    def print_goodbye(self) -> None:
        """Print styled goodbye message."""
        print(f"\n\033[36mGoodbye from {self.app_name}!\033[0m\n")

    def help(self, commands: Dict[str, str]) -> None:
        """Print formatted help listing."""
        print(f"\n\033[33mAvailable Commands:\033[0m")
        print("-" * 50)
        for cmd, desc in commands.items():
            print(f"  \033[32m{cmd:<25}\033[0m {desc}")
        print("-" * 50)

    def success(self, message: str) -> None:
        """Print green success message."""
        print(f"\033[32m✓\033[0m {message}")

    def error(self, message: str) -> None:
        """Print red error message."""
        print(f"\033[31m✗\033[0m {message}", file=sys.stderr)

    def warning(self, message: str) -> None:
        """Print yellow warning message."""
        print(f"\033[33m⚠\033[0m {message}")

    def info(self, message: str) -> None:
        """Print blue info message."""
        print(f"\033[34m●\033[0m {message}")

    def status(self, key: str, value: str) -> None:
        """Print key-value status line."""
        print(f"  \033[36m{key}:\033[0m {value}")

    def table(self, headers: List[str], rows: List[List[str]]) -> None:
        """Print formatted table."""
        if not rows:
            self.info("No data")
            return

        # Calculate column widths
        widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(widths):
                    widths[i] = max(widths[i], len(str(cell)))

        # Print header
        header_str = " | ".join(h.ljust(w) for h, w in zip(headers, widths))
        print(f"\033[33m{header_str}\033[0m")
        print("-" * len(header_str))

        # Print rows
        for row in rows:
            row_str = " | ".join(str(cell).ljust(w) for cell, w in zip(row, widths))
            print(row_str)

    def progress(self, current: int, total: int, message: str = "") -> None:
        """Print progress bar."""
        percent = int(current / total * 100)
        bar_length = 30
        filled = int(bar_length * percent / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"\r  [{bar}] {percent}% {message}", end="", flush=True)
        if current >= total:
            print()  # New line when complete

    def print_result(self, data: Dict[str, Any]) -> None:
        """Print formatted result dictionary."""
        import json
        print(json.dumps(data, indent=2))


# Convenience function
def get_skin(app_name: str = "godzilla", version: str = "1.0.0") -> ReplSkin:
    """Get a ReplSkin instance."""
    return ReplSkin(app_name, version)
