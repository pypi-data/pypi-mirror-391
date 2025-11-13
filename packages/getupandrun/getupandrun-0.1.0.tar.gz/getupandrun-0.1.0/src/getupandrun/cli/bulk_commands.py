"""Bulk operations for managing multiple GetUpAndRun projects."""

import json
import sys
from pathlib import Path

from getupandrun.environment.manager import EnvironmentManager
from getupandrun.utils.logger import (
    print_header,
    print_info,
    print_success,
    print_warning,
)


def stop_all_command() -> None:
    """Stop all GetUpAndRun projects."""
    print_header("Stopping All GetUpAndRun Projects")

    # Get base directory from UI config or use default
    config_file = Path.home() / ".getupandrun" / "ui-config.json"
    base_dir = Path.home() / "getupandrun-projects"

    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
                base_dir_str = config.get("baseDirectory", str(base_dir))
                # Expand ~ in path
                base_dir = Path(base_dir_str.replace("~", str(Path.home())))
        except Exception:
            pass  # Use default if config read fails

    if not base_dir.exists():
        print_warning(f"Base directory not found: {base_dir}")
        print_info("No projects to stop.")
        sys.exit(0)

    # Find all projects (directories with docker-compose.yml)
    projects = []
    for item in base_dir.iterdir():
        if item.is_dir():
            compose_file = item / "docker-compose.yml"
            if compose_file.exists():
                projects.append(item)

    if not projects:
        print_info("No GetUpAndRun projects found.")
        sys.exit(0)

    print_info(f"Found {len(projects)} project(s)")
    print_info("")

    stopped_count = 0
    failed_count = 0

    for project_path in projects:
        project_name = project_path.name
        print_info(f"Stopping {project_name}...")
        env_manager = EnvironmentManager(project_path)
        if env_manager.stop():
            print_success(f"  ✓ {project_name} stopped")
            stopped_count += 1
        else:
            print_warning(f"  ✗ {project_name} failed to stop")
            failed_count += 1

    print_info("")
    print_success(f"Stopped {stopped_count} project(s)")
    if failed_count > 0:
        print_warning(f"Failed to stop {failed_count} project(s)")

    sys.exit(0 if failed_count == 0 else 1)

