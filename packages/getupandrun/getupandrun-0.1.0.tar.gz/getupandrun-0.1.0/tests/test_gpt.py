"""Tests for GPT integration module."""

import json
import os
from unittest.mock import MagicMock, patch

import pytest

from getupandrun.gpt.integration import GPTClient, StackConfig


def test_stack_config_from_dict() -> None:
    """Test StackConfig creation from dictionary."""
    data = {
        "name": "test-project",
        "description": "Test description",
        "services": [{"name": "frontend", "type": "frontend"}],
        "dependencies": {"frontend": ["npm"]},
        "ports": {"frontend": 3000},
    }
    config = StackConfig.from_dict(data)
    assert config.name == "test-project"
    assert config.description == "Test description"
    assert len(config.services) == 1
    assert config.dependencies == {"frontend": ["npm"]}
    assert config.ports == {"frontend": 3000}


def test_stack_config_to_dict() -> None:
    """Test StackConfig conversion to dictionary."""
    config = StackConfig(
        name="test",
        description="desc",
        services=[{"name": "service"}],
        dependencies={},
        ports={},
    )
    data = config.to_dict()
    assert data["name"] == "test"
    assert data["description"] == "desc"
    assert len(data["services"]) == 1


def test_gpt_client_init_with_env_var() -> None:
    """Test GPTClient initialization with environment variable."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        client = GPTClient()
        assert client.api_key == "test-key"


def test_gpt_client_init_with_api_key() -> None:
    """Test GPTClient initialization with explicit API key."""
    client = GPTClient(api_key="explicit-key")
    assert client.api_key == "explicit-key"


def test_gpt_client_init_no_key() -> None:
    """Test GPTClient initialization fails without API key."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="OpenAI API key not found"):
            GPTClient()


def test_parse_response_valid_json() -> None:
    """Test parsing valid JSON response."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        client = GPTClient()
        response = '{"name": "test", "services": [{"name": "s1"}]}'
        config = client._parse_response(response)
        assert config["name"] == "test"
        assert len(config["services"]) == 1


def test_parse_response_with_markdown() -> None:
    """Test parsing JSON response wrapped in markdown code blocks."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        client = GPTClient()
        response = '```json\n{"name": "test", "services": [{"name": "s1"}]}\n```'
        config = client._parse_response(response)
        assert config["name"] == "test"


def test_parse_response_invalid_json() -> None:
    """Test parsing invalid JSON raises error."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        client = GPTClient()
        with pytest.raises(ValueError, match="Invalid JSON"):
            client._parse_response("not json")


def test_validate_config_missing_required() -> None:
    """Test validation fails for missing required keys."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        client = GPTClient()
        with pytest.raises(ValueError, match="Missing required key"):
            client._validate_config({"services": []})


def test_validate_config_empty_services() -> None:
    """Test validation fails for empty services list."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        client = GPTClient()
        with pytest.raises(ValueError, match="At least one service"):
            client._validate_config({"name": "test", "services": []})


def test_validate_config_sets_defaults() -> None:
    """Test validation sets default values for optional fields."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        client = GPTClient()
        config = {
            "name": "test",
            "services": [{"name": "service1"}],
        }
        client._validate_config(config)
        assert "description" in config
        assert "dependencies" in config
        assert "ports" in config


@patch("getupandrun.gpt.integration.OpenAI")
def test_interpret_prompt_success(mock_openai_class: MagicMock) -> None:
    """Test successful prompt interpretation."""
    # Mock OpenAI client
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client

    # Mock API response
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content=json.dumps(
                    {
                        "name": "test-project",
                        "description": "Test",
                        "services": [{"name": "frontend", "type": "frontend"}],
                        "dependencies": {},
                        "ports": {},
                    }
                )
            )
        )
    ]
    mock_client.chat.completions.create.return_value = mock_response

    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        client = GPTClient()
        config = client.interpret_prompt("test description")

        assert config.name == "test-project"
        mock_client.chat.completions.create.assert_called_once()


@patch("getupandrun.gpt.integration.OpenAI")
def test_interpret_prompt_empty_response(mock_openai_class: MagicMock) -> None:
    """Test handling of empty API response."""
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content=None))]
    mock_client.chat.completions.create.return_value = mock_response

    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        client = GPTClient()
        with pytest.raises(ValueError, match="Empty response"):
            client.interpret_prompt("test")

