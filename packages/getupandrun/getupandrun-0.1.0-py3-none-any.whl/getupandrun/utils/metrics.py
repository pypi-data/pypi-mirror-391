"""Metrics collection for GetUpAndRun."""

import json
import os
from pathlib import Path
from typing import Any, Optional


class MetricsCollector:
    """Collect and manage usage metrics."""

    def __init__(self) -> None:
        """Initialize metrics collector."""
        self.config_dir = Path.home() / ".getupandrun"
        self.config_file = self.config_dir / "config.json"
        self.metrics_enabled = self._load_config().get("metrics_enabled", False)

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                return json.loads(self.config_file.read_text())
            except Exception:
                return {}
        return {}

    def _save_config(self, config: dict[str, Any]) -> None:
        """Save configuration to file."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file.write_text(json.dumps(config, indent=2))

    def is_enabled(self) -> bool:
        """Check if metrics collection is enabled."""
        return self.metrics_enabled

    def enable(self) -> None:
        """Enable metrics collection."""
        config = self._load_config()
        config["metrics_enabled"] = True
        self._save_config(config)
        self.metrics_enabled = True

    def disable(self) -> None:
        """Disable metrics collection."""
        config = self._load_config()
        config["metrics_enabled"] = False
        self._save_config(config)
        self.metrics_enabled = False

    def collect(self, event: str, data: Optional[dict[str, Any]] = None) -> None:
        """
        Collect a metrics event.

        Args:
            event: Event name (e.g., "project_created", "command_run")
            data: Optional event data
        """
        if not self.metrics_enabled:
            return

        # In a real implementation, this would send metrics to a service
        # For now, we just log locally for development
        metrics_file = self.config_dir / "metrics.jsonl"
        metrics_file.parent.mkdir(parents=True, exist_ok=True)

        event_data = {
            "event": event,
            "timestamp": str(Path().stat().st_mtime) if Path().exists() else "",
            "data": data or {},
        }

        # Append to metrics log file
        with metrics_file.open("a") as f:
            f.write(json.dumps(event_data) + "\n")

