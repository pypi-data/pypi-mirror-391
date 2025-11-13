"""UI command implementation."""

import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

from getupandrun.utils.logger import (
    print_error,
    print_header,
    print_info,
    print_success,
    print_warning,
)


def _find_ui_directory() -> Path:
    """Find the UI directory from the installed package location."""
    import importlib.metadata
    import site
    from pathlib import Path
    
    # Get the package root directory (where this file is)
    # __file__ is in cli/ui_command.py, so:
    # parent = cli, parent.parent = getupandrun, parent.parent.parent = src
    package_root = Path(__file__).parent.parent.parent
    
    # Strategy 1: Check if UI is in the package directory (installed via pip)
    # This is the primary location when installed from PyPI
    ui_dir_in_package = package_root / "ui"
    if ui_dir_in_package.exists():
        return ui_dir_in_package
    
    # Strategy 2: Use importlib.metadata to find package location
    try:
        dist = importlib.metadata.distribution("getupandrun")
        if dist and dist.files:
            # Find the package location from metadata
            package_files = [f for f in dist.files if f.name.startswith("getupandrun/")]
            if package_files:
                # Get the first file's location
                first_file = package_files[0]
                if first_file.locate().exists():
                    # Go up from the package to find UI
                    package_location = first_file.locate().parent.parent
                    ui_dir_from_metadata = package_location / "ui"
                    if ui_dir_from_metadata.exists():
                        return ui_dir_from_metadata
    except (importlib.metadata.PackageNotFoundError, Exception):
        pass
    
    # Strategy 3: Check site-packages directory (where pip installs packages)
    site_packages_list = site.getsitepackages()
    if site_packages_list:
        site_packages = Path(site_packages_list[0])
        # Check if UI is at site-packages root
        ui_dir_in_site_packages = site_packages / "ui"
        if ui_dir_in_site_packages.exists():
            return ui_dir_in_site_packages
        
        # Check parent directory (for user installs)
        ui_dir_near_site_packages = site_packages.parent / "ui"
        if ui_dir_near_site_packages.exists():
            return ui_dir_near_site_packages
    
    # Strategy 4: Check development mode (project root)
    # Go up from package root: src/getupandrun -> src -> project root
    project_root = package_root.parent.parent
    ui_dir_at_root = project_root / "ui"
    if ui_dir_at_root.exists():
        return ui_dir_at_root
    
    # Strategy 5: Fallback to old method
    ui_dir_old = Path(__file__).parent.parent.parent.parent / "ui"
    return ui_dir_old


def ui_command(port: int) -> None:
    """Start the Next.js web UI."""
    print_header("Starting GetUpAndRun Web UI")
    ui_dir = _find_ui_directory()

    if not ui_dir.exists():
        print_error("UI directory not found. Please ensure the ui/ directory exists.")
        sys.exit(1)

    # Check if node_modules exists
    node_modules = ui_dir / "node_modules"
    if not node_modules.exists():
        print_warning("Node modules not found. Installing dependencies...")
        result = subprocess.run(
            ["npm", "install"],
            cwd=ui_dir,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print_error(f"Failed to install dependencies: {result.stderr}")
            sys.exit(1)
        print_success("Dependencies installed successfully!")

    print_info(f"Starting Next.js dev server on port {port}...")
    print_info(f"UI will be available at http://localhost:{port}")
    print_info("Press Ctrl+C to stop the server")

    # Open browser after a short delay
    def open_browser():
        time.sleep(2)  # Wait for server to start
        webbrowser.open(f"http://localhost:{port}")

    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()

    # Start Next.js dev server
    try:
        subprocess.run(
            ["npm", "run", "dev", "--", "-p", str(port)],
            cwd=ui_dir,
        )
    except KeyboardInterrupt:
        print_info("\nShutting down UI server...")
        sys.exit(0)

