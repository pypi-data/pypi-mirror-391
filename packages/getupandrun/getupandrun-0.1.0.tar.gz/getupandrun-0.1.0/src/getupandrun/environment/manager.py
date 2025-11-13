"""Environment manager for Docker Compose orchestration."""

import socket
import subprocess
import time
from pathlib import Path
from typing import Optional

from getupandrun.utils.logger import (
    print_error,
    print_info,
    print_success,
    print_warning,
)


class EnvironmentManager:
    """Manager for Docker Compose environment orchestration."""

    def __init__(self, project_path: Path) -> None:
        """
        Initialize environment manager.

        Args:
            project_path: Path to project directory containing docker-compose.yml
        """
        self.project_path = Path(project_path)
        self.compose_file = self.project_path / "docker-compose.yml"

        if not self.compose_file.exists():
            raise FileNotFoundError(
                f"docker-compose.yml not found at {self.compose_file}"
            )

    def start(self, detach: bool = True) -> bool:
        """
        Start Docker Compose services.

        Args:
            detach: Run in detached mode (default: True)

        Returns:
            True if successful
        """
        print_info("Starting Docker Compose services...")

        # Resolve port conflicts automatically
        port_mappings = self._resolve_port_conflicts()
        if port_mappings:
            print_info(f"Resolved {len(port_mappings)} port conflict(s)")

        try:
            # Try docker compose (v2) first, fallback to docker-compose (v1)
            cmd = ["docker", "compose", "up"]
            if detach:
                cmd.append("-d")

            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=120,
            )

            # Fallback to docker-compose if docker compose fails
            if result.returncode != 0:
                cmd = ["docker-compose", "up"]
                if detach:
                    cmd.append("-d")
                result = subprocess.run(
                    cmd,
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )

            if result.returncode == 0:
                print_success("Services started successfully")
                if detach:
                    # Wait a bit for containers to initialize
                    time.sleep(2)
                    self._check_health()
                return True
            else:
                print_error(f"Failed to start services: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print_error("Start command timed out")
            return False
        except FileNotFoundError:
            print_error("docker-compose not found. Is Docker installed?")
            return False
        except Exception as e:
            print_error(f"Error starting services: {e}")
            return False

    def stop(self) -> bool:
        """
        Stop Docker Compose services.

        Returns:
            True if successful
        """
        print_info("Stopping Docker Compose services...")

        try:
            result = subprocess.run(
                ["docker-compose", "stop"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                print_success("Services stopped successfully")
                return True
            else:
                print_error(f"Failed to stop services: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print_error("Stop command timed out")
            return False
        except Exception as e:
            print_error(f"Error stopping services: {e}")
            return False

    def teardown(self, remove_volumes: bool = False) -> bool:
        """
        Tear down Docker Compose services and remove containers.

        Args:
            remove_volumes: Also remove volumes (default: False)

        Returns:
            True if successful
        """
        print_info("Tearing down Docker Compose services...")

        try:
            # Try docker compose (v2) first, fallback to docker-compose (v1)
            cmd = ["docker", "compose", "down"]
            if remove_volumes:
                cmd.append("-v")

            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=60,
            )

            # Fallback to docker-compose if docker compose fails
            if result.returncode != 0:
                cmd = ["docker-compose", "down"]
                if remove_volumes:
                    cmd.append("-v")
                result = subprocess.run(
                    cmd,
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )

            if result.returncode == 0:
                action = "removed" if remove_volumes else "stopped"
                print_success(f"Services {action} successfully")

                # Verify containers are removed
                if self._verify_containers_removed():
                    print_success("Verified: All containers removed successfully")
                else:
                    print_warning("Some containers may still exist")

                return True
            else:
                print_error(f"Failed to teardown services: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print_error("Teardown command timed out")
            return False
        except Exception as e:
            print_error(f"Error tearing down services: {e}")
            return False

    def _verify_containers_removed(self) -> bool:
        """
        Verify that all containers for this project are removed.

        Returns:
            True if all containers are removed
        """
        try:
            # Get project name from compose file or path
            project_name = self.project_path.name

            # Check for containers with project name prefix
            result = subprocess.run(
                ["docker", "ps", "-a", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                container_names = result.stdout.strip().split("\n")
                project_containers = [
                    name
                    for name in container_names
                    if name and project_name in name
                ]

                return len(project_containers) == 0

            return True  # Assume success if we can't check
        except Exception:
            return True  # Assume success if verification fails

    def restart(self) -> bool:
        """
        Restart Docker Compose services.

        Returns:
            True if successful
        """
        print_info("Restarting Docker Compose services...")

        try:
            result = subprocess.run(
                ["docker-compose", "restart"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                print_success("Services restarted successfully")
                time.sleep(2)
                self._check_health()
                return True
            else:
                print_error(f"Failed to restart services: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print_error("Restart command timed out")
            return False
        except Exception as e:
            print_error(f"Error restarting services: {e}")
            return False

    def status(self) -> dict[str, str]:
        """
        Get status of all services.

        Returns:
            Dictionary mapping service names to status
        """
        try:
            result = subprocess.run(
                ["docker-compose", "ps", "--format", "json"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                # Parse JSON output (one JSON object per line)
                services = {}
                for line in result.stdout.strip().split("\n"):
                    if line:
                        import json

                        try:
                            service_info = json.loads(line)
                            name = service_info.get("Name", "unknown")
                            state = service_info.get("State", "unknown")
                            services[name] = state
                        except json.JSONDecodeError:
                            continue
                return services
            else:
                return {}

        except Exception as e:
            print_warning(f"Error getting status: {e}")
            return {}

    def _check_port_availability(self) -> bool:
        """
        Check if required ports are available.

        Returns:
            True if all ports are available
        """
        # Read ports from docker-compose.yml
        ports = self._extract_ports()
        all_available = True

        for port in ports:
            if not self._is_port_available(port):
                print_warning(f"Port {port} is already in use")
                all_available = False

        return all_available

    def _extract_ports(self) -> list[int]:
        """
        Extract port numbers from docker-compose.yml.

        Returns:
            List of port numbers
        """
        ports = []
        try:
            import yaml

            with open(self.compose_file, "r") as f:
                compose_data = yaml.safe_load(f)

            services = compose_data.get("services", {})
            for service_name, service_config in services.items():
                service_ports = service_config.get("ports", [])
                for port_mapping in service_ports:
                    if isinstance(port_mapping, str):
                        # Format: "3000:3000" or "3000"
                        parts = port_mapping.split(":")
                        if parts:
                            try:
                                host_port = int(parts[0])
                                ports.append(host_port)
                            except ValueError:
                                continue
                    elif isinstance(port_mapping, dict):
                        # Format: {"published": 3000, "target": 3000}
                        if "published" in port_mapping:
                            ports.append(port_mapping["published"])

        except Exception as e:
            print_warning(f"Could not extract ports: {e}")

        return ports

    def _is_port_available(self, port: int) -> bool:
        """
        Check if a port is available.

        Args:
            port: Port number to check

        Returns:
            True if port is available
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(("localhost", port))
                return result != 0  # Port is available if connection fails
        except Exception:
            return True  # Assume available if check fails

    def _find_available_port(self, start_port: int, max_attempts: int = 100) -> int:
        """
        Find an available port starting from start_port.

        Args:
            start_port: Starting port number
            max_attempts: Maximum number of ports to try

        Returns:
            Available port number
        """
        for offset in range(max_attempts):
            port = start_port + offset
            if self._is_port_available(port):
                return port
        # Fallback: return a high port if all nearby ports are taken
        return start_port + max_attempts

    def _resolve_port_conflicts(self) -> dict[int, int]:
        """
        Resolve port conflicts by finding alternative ports and updating docker-compose.yml.

        Returns:
            Dictionary mapping original_port -> new_port
        """
        import yaml

        port_mappings = {}  # original_port -> new_port

        try:
            with open(self.compose_file, "r") as f:
                compose_data = yaml.safe_load(f)

            services = compose_data.get("services", {})
            updated = False

            for service_name, service_config in services.items():
                service_ports = service_config.get("ports", [])
                if not service_ports:
                    continue

                new_ports = []

                for port_mapping in service_ports:
                    if isinstance(port_mapping, str):
                        # Format: "3000:3000" or "3000"
                        parts = port_mapping.split(":")
                        if parts:
                            try:
                                host_port = int(parts[0])
                                container_port = int(parts[1]) if len(parts) > 1 else host_port

                                if not self._is_port_available(host_port):
                                    # Find alternative port
                                    new_port = self._find_available_port(host_port)
                                    port_mappings[host_port] = new_port
                                    new_ports.append(f"{new_port}:{container_port}")
                                    print_info(
                                        f"Port {host_port} in use, using {new_port} instead"
                                    )
                                    updated = True
                                else:
                                    new_ports.append(port_mapping)
                            except ValueError:
                                new_ports.append(port_mapping)
                        else:
                            new_ports.append(port_mapping)
                    elif isinstance(port_mapping, dict):
                        # Format: {"published": 3000, "target": 3000}
                        published = port_mapping.get("published")
                        target = port_mapping.get("target", published)

                        if published and not self._is_port_available(published):
                            new_port = self._find_available_port(published)
                            port_mappings[published] = new_port
                            new_ports.append({"published": new_port, "target": target})
                            print_info(
                                f"Port {published} in use, using {new_port} instead"
                            )
                            updated = True
                        else:
                            new_ports.append(port_mapping)
                    else:
                        new_ports.append(port_mapping)

                if updated:
                    service_config["ports"] = new_ports

            # Write updated compose file if changes were made
            if updated:
                with open(self.compose_file, "w") as f:
                    yaml.dump(compose_data, f, default_flow_style=False, sort_keys=False)
                print_success("Updated docker-compose.yml with available ports")

        except Exception as e:
            print_warning(f"Could not resolve port conflicts: {e}")

        return port_mappings

    def _check_health(self, max_wait: int = 30) -> None:
        """
        Check health of containers.

        Args:
            max_wait: Maximum seconds to wait for health checks
        """
        print_info("Checking container health...")

        services = self.status()
        healthy_count = 0
        total_count = len(services)

        if total_count == 0:
            print_warning("No services found")
            return

        # Wait for containers to become healthy
        start_time = time.time()
        while time.time() - start_time < max_wait:
            services = self.status()
            running_count = sum(
                1 for state in services.values() if state in ["running", "Up"]
            )

            if running_count == total_count:
                healthy_count = running_count
                break

            time.sleep(1)

        if healthy_count == total_count:
            print_success(f"All {total_count} services are healthy")
        else:
            print_warning(
                f"Only {healthy_count}/{total_count} services are running"
            )
            for name, state in services.items():
                if state not in ["running", "Up"]:
                    print_warning(f"  {name}: {state}")

    def logs(self, service: Optional[str] = None, follow: bool = False) -> None:
        """
        Show logs for services.

        Args:
            service: Specific service name (None for all)
            follow: Follow log output (default: False)
        """
        try:
            cmd = ["docker-compose", "logs"]
            if service:
                cmd.append(service)
            if follow:
                cmd.append("-f")

            subprocess.run(cmd, cwd=self.project_path, timeout=None if follow else 30)

        except subprocess.TimeoutExpired:
            print_error("Logs command timed out")
        except Exception as e:
            print_error(f"Error showing logs: {e}")

