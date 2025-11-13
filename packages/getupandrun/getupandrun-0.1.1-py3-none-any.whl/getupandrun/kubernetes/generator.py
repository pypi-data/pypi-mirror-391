"""Generate Kubernetes manifests from stack configuration."""

from pathlib import Path
from typing import Any

from getupandrun.gpt.integration import StackConfig


class KubernetesGenerator:
    """Generator for Kubernetes manifests."""

    @staticmethod
    def generate(project_path: Path, config: StackConfig, project_name: str) -> None:
        """
        Generate Kubernetes manifests for all services.

        Args:
            project_path: Project root directory
            config: Stack configuration
            project_name: Project name
        """
        k8s_dir = project_path / "k8s"
        k8s_dir.mkdir(exist_ok=True)

        # Generate namespace
        namespace_content = KubernetesGenerator._generate_namespace(project_name)
        (k8s_dir / "namespace.yaml").write_text(namespace_content)

        # Generate manifests for each service
        for service in config.services:
            service_name = service.get("name", "service")
            service_type = service.get("type", "other")
            framework = service.get("framework", "")

            # Skip SQLite as separate service
            if service_type == "database" and "sqlite" in framework.lower():
                continue

            # Generate Deployment
            deployment_content = KubernetesGenerator._generate_deployment(
                service, config, project_name
            )
            (k8s_dir / f"{service_name}-deployment.yaml").write_text(deployment_content)

            # Generate Service
            service_content = KubernetesGenerator._generate_service(
                service, config, project_name
            )
            (k8s_dir / f"{service_name}-service.yaml").write_text(service_content)

            # Generate ConfigMap if needed
            configmap_content = KubernetesGenerator._generate_configmap(
                service, config, project_name
            )
            if configmap_content:
                (k8s_dir / f"{service_name}-configmap.yaml").write_text(configmap_content)

            # Generate PersistentVolumeClaim for databases
            if service_type == "database":
                pvc_content = KubernetesGenerator._generate_pvc(
                    service, project_name
                )
                if pvc_content:
                    (k8s_dir / f"{service_name}-pvc.yaml").write_text(pvc_content)

    @staticmethod
    def _generate_namespace(project_name: str) -> str:
        """Generate Kubernetes namespace manifest."""
        return f"""apiVersion: v1
kind: Namespace
metadata:
  name: {project_name}
  labels:
    app: {project_name}
"""

    @staticmethod
    def _generate_deployment(
        service: dict[str, Any], config: StackConfig, project_name: str
    ) -> str:
        """Generate Kubernetes Deployment manifest."""
        service_name = service.get("name", "service")
        service_type = service.get("type", "other")
        framework = service.get("framework", "")
        port = config.ports.get(service_name, KubernetesGenerator._get_default_port(service_type, framework))

        # Container image (using local build context)
        image = f"{project_name}-{service_name}:latest"

        # Environment variables
        env_vars = KubernetesGenerator._get_env_vars(service, config)
        env_content = ""
        for key, value in env_vars.items():
            env_content += f"        - name: {key}\n"
            env_content += f"          value: \"{value}\"\n"

        # Volume mounts for databases
        volume_mounts = ""
        volumes = ""
        if service_type == "database":
            framework_lower = framework.lower()
            if "mongodb" in framework_lower or "mongo" in framework_lower:
                volume_mounts = f"""        volumeMounts:
        - name: data
          mountPath: /data/db"""
                volumes = f"""      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: {service_name}-data"""
            elif "mysql" in framework_lower:
                volume_mounts = f"""        volumeMounts:
        - name: data
          mountPath: /var/lib/mysql"""
                volumes = f"""      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: {service_name}-data"""
            elif "postgres" in framework_lower or "postgresql" in framework_lower:
                volume_mounts = f"""        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data"""
                volumes = f"""      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: {service_name}-data"""

        # Resource requests/limits (basic defaults)
        resources = """        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
"""

        deployment = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {service_name}
  namespace: {project_name}
  labels:
    app: {project_name}
    service: {service_name}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {project_name}
      service: {service_name}
  template:
    metadata:
      labels:
        app: {project_name}
        service: {service_name}
    spec:
      containers:
      - name: {service_name}
        image: {image}
        ports:
        - containerPort: {port}
          name: http
        env:
{env_content}{resources}{volume_mounts}
{volumes}
"""
        return deployment

    @staticmethod
    def _generate_service(
        service: dict[str, Any], config: StackConfig, project_name: str
    ) -> str:
        """Generate Kubernetes Service manifest."""
        service_name = service.get("name", "service")
        service_type = service.get("type", "other")
        framework = service.get("framework", "")
        port = config.ports.get(service_name, KubernetesGenerator._get_default_port(service_type, framework))

        # Determine service type
        service_type_k8s = "ClusterIP"
        if service_type == "frontend":
            service_type_k8s = "LoadBalancer"  # Frontend typically needs external access

        service_manifest = f"""apiVersion: v1
kind: Service
metadata:
  name: {service_name}
  namespace: {project_name}
  labels:
    app: {project_name}
    service: {service_name}
spec:
  type: {service_type_k8s}
  selector:
    app: {project_name}
    service: {service_name}
  ports:
  - port: {port}
    targetPort: {port}
    protocol: TCP
    name: http
"""
        return service_manifest

    @staticmethod
    def _generate_configmap(
        service: dict[str, Any], config: StackConfig, project_name: str
    ) -> str:
        """Generate Kubernetes ConfigMap manifest if needed."""
        service_name = service.get("name", "service")
        service_type = service.get("type", "other")

        # Only generate ConfigMap for services that need it
        # Most config is handled via environment variables
        return ""

    @staticmethod
    def _generate_pvc(service: dict[str, Any], project_name: str) -> str:
        """Generate PersistentVolumeClaim for database services."""
        service_name = service.get("name", "service")
        framework = service.get("framework", "").lower()

        # Only for databases that need persistent storage
        if "sqlite" in framework:
            return ""

        pvc = f"""apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: {service_name}-data
  namespace: {project_name}
  labels:
    app: {project_name}
    service: {service_name}
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
"""
        return pvc

    @staticmethod
    def _get_default_port(service_type: str, framework: str = "") -> int:
        """Get default port for service type."""
        framework_lower = framework.lower()
        service_type_lower = service_type.lower()

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
    def _get_env_vars(service: dict[str, Any], config: StackConfig) -> dict[str, str]:
        """Get environment variables for service."""
        env = {}
        service_type = service.get("type", "").lower()
        framework = service.get("framework", "").lower()
        service_name = service.get("name", "service")

        if service_type == "database":
            if "mysql" in framework:
                env["MYSQL_DATABASE"] = "app"
                env["MYSQL_USER"] = "user"
                env["MYSQL_PASSWORD"] = "password"
                env["MYSQL_ROOT_PASSWORD"] = "rootpassword"
            elif "mongodb" in framework or "mongo" in framework:
                env["MONGO_INITDB_DATABASE"] = "app"
                env["MONGO_INITDB_ROOT_USERNAME"] = "admin"
                env["MONGO_INITDB_ROOT_PASSWORD"] = "password"
            else:  # PostgreSQL
                env["POSTGRES_DB"] = "app"
                env["POSTGRES_USER"] = "user"
                env["POSTGRES_PASSWORD"] = "password"
        elif service_type == "cache":
            if "redis" in framework:
                env["REDIS_PASSWORD"] = ""
        elif "rabbitmq" in framework:
            env["RABBITMQ_DEFAULT_USER"] = "admin"
            env["RABBITMQ_DEFAULT_PASS"] = "password"
        elif "kafka" in framework:
            env["KAFKA_BROKER_ID"] = "1"
            env["KAFKA_ZOOKEEPER_CONNECT"] = "zookeeper:2181"
            env["KAFKA_ADVERTISED_LISTENERS"] = "PLAINTEXT://kafka:9092"

        # Add service discovery via environment variables
        for other_service in config.services:
            other_name = other_service.get("name", "service")
            other_type = other_service.get("type", "other")
            if other_name != service_name:
                if other_type == "database":
                    db_framework = other_service.get("framework", "").lower()
                    if "postgres" in db_framework or "postgresql" in db_framework:
                        env["DB_HOST"] = other_name
                        env["DB_PORT"] = "5432"
                    elif "mysql" in db_framework:
                        env["DB_HOST"] = other_name
                        env["DB_PORT"] = "3306"
                    elif "mongodb" in db_framework or "mongo" in db_framework:
                        env["MONGO_HOST"] = other_name
                        env["MONGO_PORT"] = "27017"
                elif other_type == "cache":
                    cache_framework = other_service.get("framework", "").lower()
                    if "redis" in cache_framework:
                        env["REDIS_HOST"] = other_name
                        env["REDIS_PORT"] = "6379"

        return env

