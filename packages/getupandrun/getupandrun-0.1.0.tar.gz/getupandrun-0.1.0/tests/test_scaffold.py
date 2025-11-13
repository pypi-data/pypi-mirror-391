"""Tests for scaffolding engine."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from getupandrun.gpt.integration import StackConfig
from getupandrun.scaffold.engine import ScaffoldingEngine


def test_scaffolding_engine_init() -> None:
    """Test ScaffoldingEngine initialization."""
    engine = ScaffoldingEngine()
    assert engine.project_name is None

    engine = ScaffoldingEngine(project_name="test-project")
    assert engine.project_name == "test-project"


def test_scaffold_basic_project() -> None:
    """Test scaffolding a basic project."""
    config = StackConfig(
        name="test-project",
        description="Test project",
        services=[
            {
                "name": "frontend",
                "type": "frontend",
                "framework": "react",
                "dockerfile": True,
            }
        ],
        dependencies={"frontend": ["npm"]},
        ports={"frontend": 3000},
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        engine = ScaffoldingEngine()
        project_path = engine.scaffold(config, output_dir=tmpdir)

        assert Path(project_path).exists()
        assert Path(project_path) / "docker-compose.yml"
        assert Path(project_path) / "Makefile"
        assert Path(project_path) / "README.md"
        assert Path(project_path) / ".env"
        assert Path(project_path) / "k8s"


def test_scaffold_with_custom_name() -> None:
    """Test scaffolding with custom project name."""
    config = StackConfig(
        name="original-name",
        description="Test",
        services=[{"name": "frontend", "type": "frontend"}],
        dependencies={},
        ports={},
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        engine = ScaffoldingEngine(project_name="custom-name")
        project_path = engine.scaffold(config, output_dir=tmpdir)

        assert "custom-name" in project_path
        assert Path(project_path).exists()


def test_scaffold_generates_kubernetes() -> None:
    """Test that scaffolding generates Kubernetes manifests."""
    config = StackConfig(
        name="test-project",
        description="Test",
        services=[{"name": "frontend", "type": "frontend"}],
        dependencies={},
        ports={},
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        engine = ScaffoldingEngine()
        project_path = engine.scaffold(config, output_dir=tmpdir)

        k8s_dir = Path(project_path) / "k8s"
        assert k8s_dir.exists()
        assert (k8s_dir / "namespace.yaml").exists()
        assert (k8s_dir / "frontend-deployment.yaml").exists()
        assert (k8s_dir / "frontend-service.yaml").exists()


def test_scaffold_generates_deployment_scripts() -> None:
    """Test that scaffolding generates deployment scripts."""
    config = StackConfig(
        name="test-project",
        description="Test",
        services=[{"name": "frontend", "type": "frontend"}],
        dependencies={},
        ports={},
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        engine = ScaffoldingEngine()
        project_path = engine.scaffold(config, output_dir=tmpdir)

        assert Path(project_path) / "deploy-k8s.sh"
        assert Path(project_path) / "teardown-k8s.sh"


def test_scaffold_multiple_services() -> None:
    """Test scaffolding with multiple services."""
    config = StackConfig(
        name="test-project",
        description="Test",
        services=[
            {"name": "frontend", "type": "frontend", "framework": "react"},
            {"name": "backend", "type": "backend", "framework": "node"},
            {"name": "database", "type": "database", "framework": "postgres"},
        ],
        dependencies={"frontend": ["npm"], "backend": ["npm"]},
        ports={"frontend": 3000, "backend": 8000, "database": 5432},
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        engine = ScaffoldingEngine()
        project_path = engine.scaffold(config, output_dir=tmpdir)

        assert Path(project_path) / "frontend"
        assert Path(project_path) / "backend"
        assert Path(project_path) / "database"

