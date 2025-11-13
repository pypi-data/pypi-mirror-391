"""Tests for cloud deployment modules."""

import os
from unittest.mock import patch

import pytest

from getupandrun.cloud.detector import CloudDetector
from getupandrun.cloud.instructions import CloudInstructionGenerator
from getupandrun.gpt.integration import StackConfig


def test_cloud_detector_init() -> None:
    """Test CloudDetector initialization."""
    detector = CloudDetector()
    assert detector is not None


def test_cloud_detector_detect_aws() -> None:
    """Test AWS CLI detection."""
    detector = CloudDetector()
    # Just test that the method exists and returns a boolean
    result = detector.detect_aws()
    assert isinstance(result, bool)


def test_cloud_detector_detect_gcp() -> None:
    """Test GCP CLI detection."""
    detector = CloudDetector()
    result = detector.detect_gcp()
    assert isinstance(result, bool)


def test_cloud_detector_detect_docker_hub() -> None:
    """Test Docker Hub detection."""
    detector = CloudDetector()
    result = detector.detect_docker_hub()
    assert isinstance(result, bool)


def test_cloud_detector_get_available_platforms() -> None:
    """Test getting available platforms."""
    detector = CloudDetector()
    platforms = detector.get_available_platforms()
    assert isinstance(platforms, list)
    assert all(isinstance(p, str) for p in platforms)


def test_cloud_detector_get_all_platforms() -> None:
    """Test getting all supported platforms."""
    detector = CloudDetector()
    platforms = detector.get_all_platforms()
    assert isinstance(platforms, list)
    assert len(platforms) > 0
    assert "AWS" in platforms
    assert "GCP" in platforms
    assert "Docker Hub" in platforms


def test_cloud_instruction_generator_init() -> None:
    """Test CloudInstructionGenerator initialization."""
    generator = CloudInstructionGenerator()
    assert generator is not None
    assert generator.detector is not None


def test_cloud_instruction_generator_generate_instructions() -> None:
    """Test generating cloud deployment instructions."""
    config = StackConfig(
        name="test-project",
        description="Test project",
        services=[
            {"name": "frontend", "type": "frontend", "framework": "react"},
            {"name": "backend", "type": "backend", "framework": "node"},
        ],
        dependencies={},
        ports={"frontend": 3000, "backend": 8000},
    )

    generator = CloudInstructionGenerator()
    instructions = generator.generate_instructions(config)

    assert isinstance(instructions, str)
    assert "test-project" in instructions
    assert "AWS" in instructions or "GCP" in instructions or "Docker Hub" in instructions
    assert "frontend" in instructions
    assert "backend" in instructions


def test_cloud_instruction_generator_with_available_platforms() -> None:
    """Test generating instructions with specific platforms."""
    config = StackConfig(
        name="test-project",
        description="Test",
        services=[{"name": "frontend", "type": "frontend"}],
        dependencies={},
        ports={},
    )

    generator = CloudInstructionGenerator()
    instructions = generator.generate_instructions(config, available_platforms=["AWS"])

    assert "AWS" in instructions


def test_cloud_instruction_generator_aws_section() -> None:
    """Test AWS instructions generation."""
    config = StackConfig(
        name="test-project",
        description="Test",
        services=[{"name": "frontend", "type": "frontend"}],
        dependencies={},
        ports={},
    )

    generator = CloudInstructionGenerator()
    instructions = generator.generate_instructions(config, available_platforms=["AWS"])

    assert "AWS Deployment" in instructions
    assert "ECS" in instructions or "Elastic Beanstalk" in instructions


def test_cloud_instruction_generator_gcp_section() -> None:
    """Test GCP instructions generation."""
    config = StackConfig(
        name="test-project",
        description="Test",
        services=[{"name": "frontend", "type": "frontend"}],
        dependencies={},
        ports={},
    )

    generator = CloudInstructionGenerator()
    instructions = generator.generate_instructions(config, available_platforms=["GCP"])

    assert "GCP Deployment" in instructions
    assert "Cloud Run" in instructions or "GKE" in instructions

