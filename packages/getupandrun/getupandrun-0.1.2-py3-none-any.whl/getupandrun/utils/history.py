"""Command history management for GetUpAndRun."""

import json
from pathlib import Path
from typing import Any, Optional

from getupandrun.utils.logger import print_error, print_info, print_warning


class CommandHistory:
    """Manages command history for re-running last command."""

    HISTORY_FILE = Path.home() / ".getupandrun" / "history.json"
    MAX_HISTORY = 10

    def __init__(self) -> None:
        """Initialize command history."""
        self.history_file = CommandHistory.HISTORY_FILE
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

    def save_command(
        self,
        prompt: str,
        mode: str = "local",
        name: Optional[str] = None,
        start: bool = False,
    ) -> None:
        """
        Save a command to history.

        Args:
            prompt: User's prompt
            mode: Mode (local/cloud)
            name: Project name
            start: Whether to start services
        """
        try:
            history = self.load_history()
            command = {
                "prompt": prompt,
                "mode": mode,
                "name": name,
                "start": start,
            }

            # Remove duplicates (same prompt)
            history = [h for h in history if h.get("prompt") != prompt]

            # Add to front
            history.insert(0, command)

            # Limit history size
            history = history[: CommandHistory.MAX_HISTORY]

            # Save to file
            with open(self.history_file, "w") as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            print_warning(f"Failed to save command history: {e}")

    def load_history(self) -> list[dict[str, Any]]:
        """
        Load command history from file.

        Returns:
            List of command dictionaries
        """
        try:
            if self.history_file.exists():
                with open(self.history_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            print_warning(f"Failed to load command history: {e}")

        return []

    def get_last_command(self) -> Optional[dict[str, Any]]:
        """
        Get the last command from history.

        Returns:
            Last command dictionary or None
        """
        history = self.load_history()
        return history[0] if history else None

    def list_history(self, limit: int = 5) -> list[dict[str, Any]]:
        """
        List recent command history.

        Args:
            limit: Number of commands to return

        Returns:
            List of command dictionaries
        """
        history = self.load_history()
        return history[:limit]

    def clear_history(self) -> None:
        """Clear command history."""
        try:
            if self.history_file.exists():
                self.history_file.unlink()
            print_info("Command history cleared.")
        except Exception as e:
            print_error(f"Failed to clear history: {e}")

