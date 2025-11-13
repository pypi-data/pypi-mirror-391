"""Database service file generators."""

from pathlib import Path
from typing import Any


class DatabaseGenerator:
    """Generator for database service files."""

    @staticmethod
    def generate(service_dir: Path, service: dict[str, Any], framework: str) -> None:
        """
        Generate database service files.

        Args:
            service_dir: Service directory
            service: Service configuration
            framework: Framework name
        """
        (service_dir / "init").mkdir(exist_ok=True)
        (service_dir / "init" / ".gitkeep").write_text("")

