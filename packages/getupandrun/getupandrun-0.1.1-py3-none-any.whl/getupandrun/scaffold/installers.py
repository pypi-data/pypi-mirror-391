"""Dependency installers for scaffolding."""

import subprocess
from pathlib import Path
from typing import Any, Optional

from getupandrun.utils.logger import print_error, print_info, print_success, print_warning


class DependencyInstaller:
    """Installer for service dependencies."""

    @staticmethod
    def install_dependencies(service_dir: Path, service: dict[str, Any]) -> bool:
        """
        Install dependencies for a service.

        Args:
            service_dir: Service directory
            service: Service configuration

        Returns:
            True if successful, False otherwise
        """
        dependencies = service.get("dependencies", [])
        if not dependencies:
            return True

        service_name = service.get("name", "service")
        print_info(f"  Installing dependencies for {service_name}...")

        for dep_manager in dependencies:
            dep_manager_lower = dep_manager.lower()

            if dep_manager_lower == "npm":
                success = DependencyInstaller._install_npm(service_dir)
            elif dep_manager_lower == "pip":
                success = DependencyInstaller._install_pip(service_dir)
            elif dep_manager_lower == "apt":
                print_warning(f"  apt dependencies should be in Dockerfile for {service_name}")
                success = True
            else:
                print_warning(f"  Unknown dependency manager: {dep_manager}")
                success = True

            if not success:
                print_error(f"  Failed to install {dep_manager} dependencies for {service_name}")
                return False

        print_success(f"  Dependencies installed for {service_name}")
        return True

    @staticmethod
    def _install_npm(service_dir: Path) -> bool:
        """
        Install npm dependencies.

        Args:
            service_dir: Service directory

        Returns:
            True if successful
        """
        package_json = service_dir / "package.json"
        if not package_json.exists():
            print_warning("    package.json not found, skipping npm install")
            return True

        try:
            print_info("    Running: npm install")
            result = subprocess.run(
                ["npm", "install"],
                cwd=service_dir,
                capture_output=True,
                text=True,
                timeout=300,
            )
            if result.returncode == 0:
                print_success("    npm install completed")
                return True
            else:
                print_error(f"    npm install failed: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print_error("    npm install timed out")
            return False
        except FileNotFoundError:
            print_warning("    npm not found, skipping install (will run in container)")
            return True
        except Exception as e:
            print_error(f"    Error running npm install: {e}")
            return False

    @staticmethod
    def _install_pip(service_dir: Path) -> bool:
        """
        Install pip dependencies.

        Args:
            service_dir: Service directory

        Returns:
            True if successful
        """
        requirements = service_dir / "requirements.txt"
        if not requirements.exists():
            print_warning("    requirements.txt not found, skipping pip install")
            return True

        try:
            print_info("    Running: pip install -r requirements.txt")
            result = subprocess.run(
                ["pip", "install", "-r", "requirements.txt"],
                cwd=service_dir,
                capture_output=True,
                text=True,
                timeout=300,
            )
            if result.returncode == 0:
                print_success("    pip install completed")
                return True
            else:
                print_error(f"    pip install failed: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print_error("    pip install timed out")
            return False
        except FileNotFoundError:
            print_warning("    pip not found, skipping install (will run in container)")
            return True
        except Exception as e:
            print_error(f"    Error running pip install: {e}")
            return False

