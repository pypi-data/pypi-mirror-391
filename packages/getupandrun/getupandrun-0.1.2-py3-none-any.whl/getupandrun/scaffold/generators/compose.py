"""Docker Compose generator for scaffolding."""

from pathlib import Path
from typing import Any

from getupandrun.gpt.integration import StackConfig


class ComposeGenerator:
    """Generator for docker-compose.yml."""

    @staticmethod
    def generate(project_path: Path, config: StackConfig, project_name: str) -> str:
        """
        Generate docker-compose.yml content.

        Args:
            project_path: Project root directory
            config: Stack configuration
            project_name: Project name

        Returns:
            docker-compose.yml content
        """
        services_yaml = []
        volumes = []

        for service in config.services:
            service_name = service.get("name", "service")
            service_type = service.get("type", "other")
            framework = service.get("framework", "")
            
            # Skip SQLite as separate service - it's embedded in backend
            if service_type == "database" and "sqlite" in framework.lower():
                continue
                
            port = config.ports.get(service_name, ComposeGenerator._get_default_port(service_type, framework))

            service_yaml = {
                "build": {"context": f"./{service_name}", "dockerfile": "Dockerfile"},
                "container_name": f"{project_name}-{service_name}",
                "ports": [f"{port}:{port}"],
                "environment": ComposeGenerator._get_service_env(service, config),
                "volumes": [f"./{service_name}:/app"],
            }

            # Add hot-reload support for development services
            if service_type in ["frontend", "backend"]:
                framework_lower = framework.lower()
                if "python" in framework_lower or "fastapi" in framework_lower or "django" in framework_lower or "flask" in framework_lower:
                    # Python hot-reload
                    service_yaml["environment"]["PYTHONUNBUFFERED"] = "1"
                    service_yaml["environment"]["FLASK_ENV"] = "development"
                    # For Django, set DB_HOST if Postgres is in the stack
                    if "django" in framework_lower:
                        for db_service in config.services:
                            db_type = db_service.get("type", "").lower()
                            db_framework = db_service.get("framework", "").lower()
                            if db_type == "database" and ("postgres" in db_framework or "postgresql" in db_framework):
                                db_service_name = db_service.get("name", "postgres-database")
                                service_yaml["environment"]["DB_HOST"] = db_service_name
                                service_yaml["environment"]["DB_PORT"] = "5432"
                                break
                elif "node" in framework_lower or "react" in framework_lower or "nextjs" in framework_lower or "next.js" in framework_lower or "next" in framework_lower or "nuxtjs" in framework_lower or "nuxt.js" in framework_lower or "nuxt" in framework_lower or "nestjs" in framework_lower or "nest.js" in framework_lower or "nest" in framework_lower:
                    # Node hot-reload
                    service_yaml["volumes"].append(f"./{service_name}/node_modules:/app/node_modules")
                    service_yaml["environment"]["CHOKIDAR_USEPOLLING"] = "true"

            if service_type == "database":
                framework_lower = framework.lower()
                # SQLite doesn't need a separate service or volumes
                if "sqlite" not in framework_lower:
                    # Add volume for database data persistence
                    if "mongodb" in framework_lower or "mongo" in framework_lower:
                        volumes.append(f"{service_name}-data:/data/db")
                        service_yaml["volumes"].append(f"{service_name}-data:/data/db")
                    elif "mysql" in framework_lower:
                        volumes.append(f"{service_name}-data:/var/lib/mysql")
                        service_yaml["volumes"].append(f"{service_name}-data:/var/lib/mysql")
                    else:  # PostgreSQL
                        volumes.append(f"{service_name}-data:/var/lib/postgresql/data")
                        service_yaml["volumes"].append(f"{service_name}-data:/var/lib/postgresql/data")
                else:
                    # Skip SQLite as a separate service - it's embedded
                    continue

            services_yaml.append((service_name, service_yaml))

        compose_content = "version: '3.8'\n\nservices:\n"
        for service_name, service_config in services_yaml:
            compose_content += f"  {service_name}:\n"
            for key, value in service_config.items():
                if key == "ports":
                    compose_content += f"    {key}:\n"
                    for port in value:
                        compose_content += f"      - \"{port}\"\n"
                elif key == "volumes":
                    compose_content += f"    {key}:\n"
                    for vol in value:
                        compose_content += f"      - {vol}\n"
                elif key == "environment":
                    compose_content += f"    {key}:\n"
                    for env_key, env_val in value.items():
                        compose_content += f"      {env_key}: {env_val}\n"
                elif key == "build":
                    compose_content += f"    {key}:\n"
                    compose_content += f"      context: {value['context']}\n"
                    compose_content += f"      dockerfile: {value['dockerfile']}\n"
                else:
                    compose_content += f"    {key}: {value}\n"

        if volumes:
            compose_content += "\nvolumes:\n"
            for vol in set(volumes):
                vol_name = vol.split(":")[0]
                compose_content += f"  {vol_name}:\n"

        return compose_content

    @staticmethod
    def _get_default_port(service_type: str, framework: str = "") -> int:
        """Get default port for service type."""
        framework_lower = framework.lower()
        service_type_lower = service_type.lower()
        
        # Framework-specific ports
        if "angular" in framework_lower and service_type_lower == "frontend":
            return 4200
        if "nestjs" in framework_lower or "nest.js" in framework_lower or "nest" in framework_lower:
            return 3000
        if "mysql" in framework_lower and service_type_lower == "database":
            return 3306
        if "mongodb" in framework_lower or "mongo" in framework_lower:
            return 27017
        if "memcached" in framework_lower:
            return 11211
        if "rabbitmq" in framework_lower:
            return 5672
        if "kafka" in framework_lower:
            return 9092
        
        defaults = {
            "frontend": 3000,
            "backend": 8000,
            "database": 5432,
            "cache": 6379,
            "queue": 5672,
        }
        return defaults.get(service_type_lower, 8080)

    @staticmethod
    def _get_service_env(service: dict[str, Any], config: StackConfig) -> dict[str, str]:
        """Get environment variables for service."""
        env = {}
        service_type = service.get("type", "").lower()
        framework = service.get("framework", "").lower()

        if service_type == "database":
            if "mysql" in framework:
                env["MYSQL_DATABASE"] = "${MYSQL_DATABASE:-app}"
                env["MYSQL_USER"] = "${MYSQL_USER:-user}"
                env["MYSQL_PASSWORD"] = "${MYSQL_PASSWORD:-password}"
                env["MYSQL_ROOT_PASSWORD"] = "${MYSQL_ROOT_PASSWORD:-rootpassword}"
            elif "mongodb" in framework or "mongo" in framework:
                env["MONGO_INITDB_DATABASE"] = "${MONGO_INITDB_DATABASE:-app}"
                env["MONGO_INITDB_ROOT_USERNAME"] = "${MONGO_INITDB_ROOT_USERNAME:-admin}"
                env["MONGO_INITDB_ROOT_PASSWORD"] = "${MONGO_INITDB_ROOT_PASSWORD:-password}"
            else:  # PostgreSQL
                env["POSTGRES_DB"] = "${POSTGRES_DB:-app}"
                env["POSTGRES_USER"] = "${POSTGRES_USER:-user}"
                env["POSTGRES_PASSWORD"] = "${POSTGRES_PASSWORD:-password}"
        elif service_type == "cache":
            if "redis" in framework:
                env["REDIS_PASSWORD"] = "${REDIS_PASSWORD:-}"
            # Memcached doesn't need env vars
        elif "rabbitmq" in framework:
            env["RABBITMQ_DEFAULT_USER"] = "${RABBITMQ_DEFAULT_USER:-admin}"
            env["RABBITMQ_DEFAULT_PASS"] = "${RABBITMQ_DEFAULT_PASS:-password}"
        elif "kafka" in framework:
            env["KAFKA_BROKER_ID"] = "${KAFKA_BROKER_ID:-1}"
            env["KAFKA_ZOOKEEPER_CONNECT"] = "${KAFKA_ZOOKEEPER_CONNECT:-zookeeper:2181}"
            env["KAFKA_ADVERTISED_LISTENERS"] = "${KAFKA_ADVERTISED_LISTENERS:-PLAINTEXT://kafka:9092}"

        return env

