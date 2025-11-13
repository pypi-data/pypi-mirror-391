"""Diagnostic utilities for GetUpAndRun."""

import os
import platform
import subprocess
from pathlib import Path
from typing import Any, Optional

from getupandrun.utils.logger import (
    print_error,
    print_info,
    print_success,
    print_table,
    print_warning,
)


class Diagnostics:
    """System diagnostics for GetUpAndRun."""

    def __init__(self) -> None:
        """Initialize diagnostics."""
        self.issues: list[dict[str, str]] = []
        self.info: list[dict[str, str]] = []

    def check_python_version(self) -> bool:
        """
        Check Python version.

        Returns:
            True if version is acceptable
        """
        version = platform.python_version()
        major, minor = map(int, version.split(".")[:2])

        if major < 3 or (major == 3 and minor < 9):
            self.issues.append(
                {
                    "Component": "Python",
                    "Status": "❌",
                    "Issue": f"Python {version} is too old. Requires Python 3.9+",
                }
            )
            return False

        self.info.append(
            {"Component": "Python", "Status": "✅", "Version": version}
        )
        return True

    def check_docker(self) -> bool:
        """
        Check Docker installation and status.

        Returns:
            True if Docker is available
        """
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                self.info.append(
                    {"Component": "Docker", "Status": "✅", "Version": version}
                )

                # Check if Docker daemon is running
                result = subprocess.run(
                    ["docker", "ps"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode != 0:
                    self.issues.append(
                        {
                            "Component": "Docker",
                            "Status": "⚠️",
                            "Issue": "Docker is installed but daemon is not running",
                        }
                    )
                    return False

                return True
            else:
                self.issues.append(
                    {
                        "Component": "Docker",
                        "Status": "❌",
                        "Issue": "Docker is not installed or not in PATH",
                    }
                )
                return False
        except FileNotFoundError:
            self.issues.append(
                {
                    "Component": "Docker",
                    "Status": "❌",
                    "Issue": "Docker command not found",
                }
            )
            return False
        except subprocess.TimeoutExpired:
            self.issues.append(
                {
                    "Component": "Docker",
                    "Status": "⚠️",
                    "Issue": "Docker command timed out",
                }
            )
            return False
        except Exception as e:
            self.issues.append(
                {
                    "Component": "Docker",
                    "Status": "❌",
                    "Issue": f"Error checking Docker: {e}",
                }
            )
            return False

    def check_docker_compose(self) -> bool:
        """
        Check Docker Compose availability.

        Returns:
            True if Docker Compose is available
        """
        try:
            # Try docker compose (v2)
            result = subprocess.run(
                ["docker", "compose", "version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                self.info.append(
                    {
                        "Component": "Docker Compose",
                        "Status": "✅",
                        "Version": version,
                    }
                )
                return True

            # Try docker-compose (v1)
            result = subprocess.run(
                ["docker-compose", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                self.info.append(
                    {
                        "Component": "Docker Compose",
                        "Status": "✅",
                        "Version": version,
                    }
                )
                return True

            self.issues.append(
                {
                    "Component": "Docker Compose",
                    "Status": "❌",
                    "Issue": "Docker Compose not found",
                }
            )
            return False
        except FileNotFoundError:
            self.issues.append(
                {
                    "Component": "Docker Compose",
                    "Status": "❌",
                    "Issue": "Docker Compose command not found",
                }
            )
            return False
        except Exception as e:
            self.issues.append(
                {
                    "Component": "Docker Compose",
                    "Status": "❌",
                    "Issue": f"Error checking Docker Compose: {e}",
                }
            )
            return False

    def check_openai_key(self) -> bool:
        """
        Check OpenAI API key.

        Returns:
            True if API key is set
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            self.issues.append(
                {
                    "Component": "OpenAI API Key",
                    "Status": "❌",
                    "Issue": "OPENAI_API_KEY environment variable not set",
                }
            )
            return False

        if len(api_key) < 20:  # Basic validation
            self.issues.append(
                {
                    "Component": "OpenAI API Key",
                    "Status": "⚠️",
                    "Issue": "OPENAI_API_KEY appears to be invalid (too short)",
                }
            )
            return False

        # Mask the key for display
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        self.info.append(
            {
                "Component": "OpenAI API Key",
                "Status": "✅",
                "Value": masked_key,
            }
        )
        return True

    def check_disk_space(self, path: Path = Path.cwd()) -> bool:
        """
        Check available disk space.

        Args:
            path: Path to check

        Returns:
            True if sufficient disk space
        """
        try:
            import shutil

            total, used, free = shutil.disk_usage(path)
            free_gb = free / (1024**3)

            if free_gb < 1.0:  # Less than 1GB free
                self.issues.append(
                    {
                        "Component": "Disk Space",
                        "Status": "⚠️",
                        "Issue": f"Low disk space: {free_gb:.2f} GB free",
                    }
                )
                return False

            self.info.append(
                {
                    "Component": "Disk Space",
                    "Status": "✅",
                    "Free": f"{free_gb:.2f} GB",
                }
            )
            return True
        except Exception as e:
            self.issues.append(
                {
                    "Component": "Disk Space",
                    "Status": "⚠️",
                    "Issue": f"Could not check disk space: {e}",
                }
            )
            return False

    def check_git(self) -> bool:
        """
        Check Git installation.

        Returns:
            True if Git is available
        """
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                self.info.append(
                    {"Component": "Git", "Status": "✅", "Version": version}
                )
                return True
            else:
                self.issues.append(
                    {
                        "Component": "Git",
                        "Status": "⚠️",
                        "Issue": "Git is not installed (optional)",
                    }
                )
                return False
        except FileNotFoundError:
            self.info.append(
                {
                    "Component": "Git",
                    "Status": "⚠️",
                    "Note": "Git not found (optional for GetUpAndRun)",
                }
            )
            return False
        except Exception as e:
            self.info.append(
                {
                    "Component": "Git",
                    "Status": "⚠️",
                    "Note": f"Could not check Git: {e}",
                }
            )
            return False

    def run_all_checks(self) -> dict[str, Any]:
        """
        Run all diagnostic checks.

        Returns:
            Dictionary with check results
        """
        print_info("Running diagnostic checks...")

        self.check_python_version()
        self.check_docker()
        self.check_docker_compose()
        self.check_openai_key()
        self.check_disk_space()
        self.check_git()

        return {
            "issues": self.issues,
            "info": self.info,
            "all_ok": len(self.issues) == 0,
        }

    def print_report(self) -> None:
        """Print diagnostic report."""
        if self.info:
            print_info("\n✅ System Information:")
            headers = ["Component", "Status"]
            rows = []
            for item in self.info:
                status = item.get("Status", "")
                component = item.get("Component", "")
                version = item.get("Version") or item.get("Value") or item.get("Free") or item.get("Note", "")
                rows.append([component, f"{status} {version}"])

            print_table(headers, rows)

        if self.issues:
            print_warning("\n⚠️ Issues Found:")
            headers = ["Component", "Status", "Issue"]
            rows = []
            for issue in self.issues:
                rows.append(
                    [
                        issue.get("Component", ""),
                        issue.get("Status", ""),
                        issue.get("Issue", ""),
                    ]
                )
            print_table(headers, rows)
        else:
            print_success("\n✅ All checks passed! System is ready.")

