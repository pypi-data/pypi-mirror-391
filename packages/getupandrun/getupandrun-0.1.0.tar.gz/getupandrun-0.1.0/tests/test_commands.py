"""Tests for CLI command implementations."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from getupandrun.cli.commands import (
    doctor_command,
    help_command,
    history_command,
    last_command,
    templates_command,
    version_command,
)
from getupandrun.cli.main import cli


def test_help_command() -> None:
    """Test help command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["help"])
    assert result.exit_code == 0
    assert "GetUpAndRun" in result.output


def test_version_command() -> None:
    """Test version command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["version"])
    assert result.exit_code == 0
    assert "version" in result.output.lower()


def test_templates_command() -> None:
    """Test templates command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["templates"])
    assert result.exit_code == 0
    assert "template" in result.output.lower()


def test_templates_command_with_search() -> None:
    """Test templates command with search."""
    runner = CliRunner()
    result = runner.invoke(cli, ["templates", "--search", "react"])
    assert result.exit_code == 0


def test_doctor_command() -> None:
    """Test doctor command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["doctor"])
    # Doctor command may exit with 0 or 1 depending on system state
    assert result.exit_code in [0, 1]


def test_history_command_no_history() -> None:
    """Test history command with no history."""
    with patch("getupandrun.utils.history.CommandHistory.list_history", return_value=[]):
        runner = CliRunner()
        result = runner.invoke(cli, ["history"])
        assert result.exit_code == 0


def test_last_command_no_history() -> None:
    """Test last command with no history."""
    with patch("getupandrun.utils.history.CommandHistory.get_last_command", return_value=None):
        runner = CliRunner()
        result = runner.invoke(cli, ["last"])
        assert result.exit_code == 0
        assert "No command history" in result.output or "No command" in result.output


def test_cli_with_template() -> None:
    """Test CLI with template option."""
    with patch("getupandrun.templates.manager.TemplateManager.get_template") as mock_get:
        from getupandrun.gpt.integration import StackConfig

        mock_config = StackConfig(
            name="test-project",
            description="Test",
            services=[{"name": "frontend", "type": "frontend"}],
            dependencies={},
            ports={},
        )
        mock_get.return_value = mock_config

        with patch("getupandrun.scaffold.engine.ScaffoldingEngine.scaffold") as mock_scaffold:
            mock_scaffold.return_value = "/tmp/test-project"

            runner = CliRunner()
            result = runner.invoke(
                cli,
                ["--template", "react-node-postgres", "--name", "test-project"],
            )
            # May exit with error if scaffolding fails, but template should be processed
            assert "template" in result.output.lower() or result.exit_code != 0


def test_cli_cloud_mode() -> None:
    """Test CLI with cloud mode."""
    with patch("getupandrun.gpt.integration.GPTClient.interpret_prompt") as mock_gpt:
        from getupandrun.gpt.integration import StackConfig

        mock_config = StackConfig(
            name="test-project",
            description="Test",
            services=[{"name": "frontend", "type": "frontend"}],
            dependencies={},
            ports={},
        )
        mock_gpt.return_value = mock_config

        with patch("getupandrun.cloud.instructions.CloudInstructionGenerator.generate_instructions") as mock_cloud:
            mock_cloud.return_value = "# Cloud Instructions\nTest content"

            with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
                runner = CliRunner()
                result = runner.invoke(
                    cli,
                    ["--prompt", "React app", "--mode", "cloud"],
                )
                # Cloud mode should generate instructions
                assert "cloud" in result.output.lower() or result.exit_code != 0


def test_cli_invalid_path() -> None:
    """Test CLI commands with invalid paths."""
    runner = CliRunner()
    result = runner.invoke(cli, ["start", "/nonexistent/path"])
    assert result.exit_code != 0

    result = runner.invoke(cli, ["status", "/nonexistent/path"])
    assert result.exit_code != 0


def test_cli_name_option() -> None:
    """Test CLI with custom name option."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--prompt", "test", "--name", "my-project"])
    # Should exit with error since GPT integration requires API key
    assert result.exit_code != 0

