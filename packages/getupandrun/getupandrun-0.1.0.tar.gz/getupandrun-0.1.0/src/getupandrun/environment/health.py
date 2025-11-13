"""Health check utilities for containers."""

import subprocess
import time
from typing import Optional

from getupandrun.utils.logger import print_info, print_success, print_warning


class HealthChecker:
    """Health checker for Docker containers."""

    @staticmethod
    def check_service_health(
        container_name: str, max_attempts: int = 10, delay: int = 2
    ) -> bool:
        """
        Check if a container is healthy.

        Args:
            container_name: Name of the container
            max_attempts: Maximum number of health check attempts
            delay: Delay between attempts in seconds

        Returns:
            True if container is healthy
        """
        for attempt in range(1, max_attempts + 1):
            try:
                result = subprocess.run(
                    [
                        "docker",
                        "inspect",
                        "--format",
                        "{{.State.Health.Status}}",
                        container_name,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                if result.returncode == 0:
                    status = result.stdout.strip()
                    if status == "healthy":
                        print_success(f"Container {container_name} is healthy")
                        return True
                    elif status == "unhealthy":
                        print_warning(
                            f"Container {container_name} is unhealthy (attempt {attempt}/{max_attempts})"
                        )
                    else:
                        print_info(
                            f"Container {container_name} status: {status} (attempt {attempt}/{max_attempts})"
                        )

            except Exception as e:
                print_warning(f"Health check error: {e}")

            if attempt < max_attempts:
                time.sleep(delay)

        print_warning(f"Container {container_name} did not become healthy")
        return False

    @staticmethod
    def check_container_running(container_name: str) -> bool:
        """
        Check if a container is running.

        Args:
            container_name: Name of the container

        Returns:
            True if container is running
        """
        try:
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "--filter",
                    f"name={container_name}",
                    "--format",
                    "{{.Names}}",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            return container_name in result.stdout

        except Exception:
            return False

    @staticmethod
    def wait_for_service(
        container_name: str,
        endpoint: Optional[str] = None,
        max_wait: int = 60,
        check_interval: int = 2,
    ) -> bool:
        """
        Wait for a service to become available.

        Args:
            container_name: Name of the container
            endpoint: Optional HTTP endpoint to check (e.g., "http://localhost:3000/health")
            max_wait: Maximum seconds to wait
            check_interval: Seconds between checks

        Returns:
            True if service becomes available
        """
        import requests

        start_time = time.time()
        while time.time() - start_time < max_wait:
            if HealthChecker.check_container_running(container_name):
                if endpoint:
                    try:
                        response = requests.get(endpoint, timeout=2)
                        if response.status_code == 200:
                            print_success(f"Service at {endpoint} is available")
                            return True
                    except Exception:
                        pass
                else:
                    print_success(f"Container {container_name} is running")
                    return True

            time.sleep(check_interval)

        print_warning(f"Service {container_name} did not become available")
        return False

