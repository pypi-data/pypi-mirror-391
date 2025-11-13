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


def ui_command(port: int) -> None:
    """Start the Next.js web UI."""
    print_header("Starting GetUpAndRun Web UI")
    ui_dir = Path(__file__).parent.parent.parent.parent / "ui"

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

