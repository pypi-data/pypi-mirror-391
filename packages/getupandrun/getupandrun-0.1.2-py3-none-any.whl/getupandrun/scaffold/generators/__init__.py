"""Generator module for scaffolding - re-exports all generators."""

from .backend import BackendGenerator
from .compose import ComposeGenerator
from .database import DatabaseGenerator
from .dockerfile import DockerfileGenerator
from .frontend import FrontendGenerator

# Backward compatibility wrapper
class ServiceFileGenerator:
    """Backward compatibility wrapper for ServiceFileGenerator."""

    @staticmethod
    def generate_frontend(service_dir, service, framework):
        """Generate frontend service files."""
        return FrontendGenerator.generate(service_dir, service, framework)

    @staticmethod
    def generate_backend(service_dir, service, framework, config=None):
        """Generate backend service files."""
        return BackendGenerator.generate(service_dir, service, framework, config)

    @staticmethod
    def generate_database(service_dir, service, framework):
        """Generate database service files."""
        return DatabaseGenerator.generate(service_dir, service, framework)

__all__ = [
    "DockerfileGenerator",
    "FrontendGenerator",
    "BackendGenerator",
    "DatabaseGenerator",
    "ComposeGenerator",
    "ServiceFileGenerator",  # For backward compatibility
]

