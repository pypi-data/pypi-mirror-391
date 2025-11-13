"""Detect available cloud CLI tools."""

import shutil
from typing import Optional


class CloudDetector:
    """Detect available cloud CLI tools on the system."""

    def __init__(self) -> None:
        """Initialize cloud detector."""
        self._aws_available: Optional[bool] = None
        self._gcp_available: Optional[bool] = None
        self._docker_hub_available: Optional[bool] = None

    def detect_aws(self) -> bool:
        """
        Check if AWS CLI is available.

        Returns:
            True if AWS CLI is installed and available
        """
        if self._aws_available is None:
            self._aws_available = shutil.which("aws") is not None
        return self._aws_available

    def detect_gcp(self) -> bool:
        """
        Check if GCP CLI (gcloud) is available.

        Returns:
            True if GCP CLI is installed and available
        """
        if self._gcp_available is None:
            self._gcp_available = shutil.which("gcloud") is not None
        return self._gcp_available

    def detect_docker_hub(self) -> bool:
        """
        Check if Docker Hub CLI (docker) is available.

        Returns:
            True if Docker CLI is installed and available
        """
        if self._docker_hub_available is None:
            self._docker_hub_available = shutil.which("docker") is not None
        return self._docker_hub_available

    def get_available_platforms(self) -> list[str]:
        """
        Get list of available cloud platforms.

        Returns:
            List of available platform names
        """
        platforms = []
        if self.detect_aws():
            platforms.append("AWS")
        if self.detect_gcp():
            platforms.append("GCP")
        if self.detect_docker_hub():
            platforms.append("Docker Hub")
        return platforms

    def get_all_platforms(self) -> list[str]:
        """
        Get list of all supported cloud platforms (regardless of availability).

        Returns:
            List of all supported platform names
        """
        return ["AWS", "GCP", "Docker Hub"]

