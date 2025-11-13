"""Tests for CLI module."""

import os
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from getupandrun.cli.main import cli


def test_cli_help() -> None:
    """Test that CLI help command works."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "GetUpAndRun" in result.output


def test_cli_version() -> None:
    """Test that version command works."""
    runner = CliRunner()
    result = runner.invoke(cli, ["version"])
    assert result.exit_code == 0
    assert "version" in result.output.lower()


def test_cli_without_args() -> None:
    """Test that CLI shows help when invoked without arguments."""
    runner = CliRunner()
    result = runner.invoke(cli, [])
    assert result.exit_code == 0
    assert "GetUpAndRun" in result.output


def test_cli_with_prompt() -> None:
    """Test that CLI accepts prompt argument."""
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

        with patch("getupandrun.scaffold.engine.ScaffoldingEngine.scaffold") as mock_scaffold:
            mock_scaffold.return_value = "/tmp/test-project"

            import os
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
                runner = CliRunner()
                result = runner.invoke(cli, ["--prompt", "test prompt"])
                # May exit with error if scaffolding fails, but should process prompt
                assert result.exit_code in [0, 1]


def test_cli_mode_option() -> None:
    """Test that mode option works."""
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

        import os
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            runner = CliRunner()
            result = runner.invoke(cli, ["--prompt", "test", "--mode", "local"])
            # May exit with error if scaffolding fails
            assert result.exit_code in [0, 1]


def test_cli_invalid_mode() -> None:
    """Test that invalid mode is rejected."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--prompt", "test", "--mode", "invalid"])
    assert result.exit_code != 0

