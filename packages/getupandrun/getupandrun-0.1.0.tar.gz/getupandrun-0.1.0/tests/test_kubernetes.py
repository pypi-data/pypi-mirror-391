"""Tests for Kubernetes generation modules."""

import tempfile
from pathlib import Path

import pytest

from getupandrun.gpt.integration import StackConfig
from getupandrun.kubernetes.generator import KubernetesGenerator
from getupandrun.kubernetes.scripts import KubernetesScripts


def test_kubernetes_generator_generate() -> None:
    """Test Kubernetes manifest generation."""
    config = StackConfig(
        name="test-project",
        description="Test",
        services=[
            {"name": "frontend", "type": "frontend", "framework": "react"},
            {"name": "database", "type": "database", "framework": "postgres"},
        ],
        dependencies={},
        ports={"frontend": 3000, "database": 5432},
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        KubernetesGenerator.generate(project_path, config, "test-project")

        k8s_dir = project_path / "k8s"
        assert k8s_dir.exists()
        assert (k8s_dir / "namespace.yaml").exists()
        assert (k8s_dir / "frontend-deployment.yaml").exists()
        assert (k8s_dir / "frontend-service.yaml").exists()
        assert (k8s_dir / "database-deployment.yaml").exists()
        assert (k8s_dir / "database-service.yaml").exists()
        assert (k8s_dir / "database-pvc.yaml").exists()


def test_kubernetes_generator_namespace() -> None:
    """Test namespace generation."""
    namespace = KubernetesGenerator._generate_namespace("test-project")
    assert "kind: Namespace" in namespace
    assert "name: test-project" in namespace


def test_kubernetes_generator_deployment() -> None:
    """Test deployment generation."""
    config = StackConfig(
        name="test-project",
        description="Test",
        services=[{"name": "frontend", "type": "frontend", "framework": "react"}],
        dependencies={},
        ports={"frontend": 3000},
    )

    deployment = KubernetesGenerator._generate_deployment(
        config.services[0], config, "test-project"
    )
    assert "kind: Deployment" in deployment
    assert "name: frontend" in deployment
    assert "containerPort: 3000" in deployment


def test_kubernetes_generator_service() -> None:
    """Test service generation."""
    config = StackConfig(
        name="test-project",
        description="Test",
        services=[{"name": "frontend", "type": "frontend", "framework": "react"}],
        dependencies={},
        ports={"frontend": 3000},
    )

    service = KubernetesGenerator._generate_service(
        config.services[0], config, "test-project"
    )
    assert "kind: Service" in service
    assert "name: frontend" in service
    assert "port: 3000" in service


def test_kubernetes_generator_pvc() -> None:
    """Test PVC generation for databases."""
    service = {"name": "database", "type": "database", "framework": "postgres"}
    pvc = KubernetesGenerator._generate_pvc(service, "test-project")
    assert "kind: PersistentVolumeClaim" in pvc
    assert "name: database-data" in pvc


def test_kubernetes_generator_no_pvc_for_sqlite() -> None:
    """Test that SQLite doesn't generate PVC."""
    service = {"name": "database", "type": "database", "framework": "sqlite"}
    pvc = KubernetesGenerator._generate_pvc(service, "test-project")
    assert pvc == ""


def test_kubernetes_scripts_generate_deploy_script() -> None:
    """Test deployment script generation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        KubernetesScripts.generate_deploy_script(project_path, "test-project")

        script_path = project_path / "deploy-k8s.sh"
        assert script_path.exists()
        assert script_path.is_file()

        content = script_path.read_text()
        assert "test-project" in content
        assert "kubectl" in content


def test_kubernetes_scripts_generate_teardown_script() -> None:
    """Test teardown script generation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        KubernetesScripts.generate_teardown_script(project_path, "test-project")

        script_path = project_path / "teardown-k8s.sh"
        assert script_path.exists()
        assert script_path.is_file()

        content = script_path.read_text()
        assert "test-project" in content
        assert "kubectl" in content

