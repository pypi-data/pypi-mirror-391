"""Crash logging utilities for GetUpAndRun."""

import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional

from getupandrun.utils.logger import print_warning


class CrashLogger:
    """Logs crashes and errors to file."""

    LOG_DIR = Path.home() / ".getupandrun" / "logs"
    LOG_FILE = LOG_DIR / f"crash-{datetime.now().strftime('%Y%m%d')}.log"

    def __init__(self) -> None:
        """Initialize crash logger."""
        self.log_dir = CrashLogger.LOG_DIR
        self.log_file = CrashLogger.LOG_FILE
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def log_error(
        self,
        error: Exception,
        context: Optional[dict[str, str]] = None,
    ) -> None:
        """
        Log an error to file.

        Args:
            error: Exception that occurred
            context: Optional context information
        """
        try:
            timestamp = datetime.now().isoformat()
            error_type = type(error).__name__
            error_message = str(error)
            traceback_str = "".join(traceback.format_exception(type(error), error, error.__traceback__))

            log_entry = f"""
{'='*80}
CRASH LOG - {timestamp}
{'='*80}
Error Type: {error_type}
Error Message: {error_message}

Context:
{self._format_context(context) if context else 'None'}

Traceback:
{traceback_str}
{'='*80}

"""

            with open(self.log_file, "a") as f:
                f.write(log_entry)

            print_warning(f"Error logged to: {self.log_file}")
        except Exception as e:
            # Don't fail if logging fails
            print_warning(f"Failed to write crash log: {e}")

    def _format_context(self, context: Optional[dict[str, str]]) -> str:
        """
        Format context dictionary for logging.

        Args:
            context: Context dictionary

        Returns:
            Formatted context string
        """
        if not context:
            return "None"

        return "\n".join(f"  {key}: {value}" for key, value in context.items())

    def get_recent_logs(self, limit: int = 5) -> list[str]:
        """
        Get recent log entries.

        Args:
            limit: Number of entries to return

        Returns:
            List of log entry strings
        """
        try:
            if not self.log_file.exists():
                return []

            with open(self.log_file, "r") as f:
                content = f.read()

            # Split by separator
            entries = content.split("=" * 80)
            # Filter empty entries and return last N
            entries = [e.strip() for e in entries if e.strip()]
            return entries[-limit:] if len(entries) > limit else entries
        except Exception:
            return []

