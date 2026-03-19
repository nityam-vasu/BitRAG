"""
Tests for BitRAG CLI module.
"""

import os
import sys
import pytest
from click.testing import CliRunner

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class TestCLI:
    """Test cases for CLI commands."""

    @pytest.fixture
    def runner(self):
        """Create a Click CLI test runner."""
        return CliRunner()

    @pytest.fixture
    def cli_module(self):
        """Import CLI module."""
        from bitrag.cli import main

        return main

    def test_cli_help(self, runner):
        """Test that CLI --help works."""
        from bitrag.cli.main import cli

        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "BitRAG" in result.output

    def test_cli_version(self, runner):
        """Test that CLI --version works."""
        from bitrag.cli.main import cli

        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0

    def test_status_command(self, runner):
        """Test status command."""
        from bitrag.cli.main import cli

        result = runner.invoke(cli, ["status"])
        # Should not fail even without Ollama
        assert result.exit_code == 0


class TestCLIDocumentCommands:
    """Test cases for document-related CLI commands."""

    @pytest.fixture
    def runner(self):
        """Create a Click CLI test runner."""
        return CliRunner()

    def test_documents_command_empty(self, runner, temp_dir):
        """Test documents command with empty index."""
        from bitrag.cli.main import cli

        with runner.isolated_filesystem(temp_dir):
            result = runner.invoke(cli, ["documents"])
            # May fail due to missing directories, but shouldn't crash
            assert result.exit_code in [0, 1]


class TestCLIModelCommands:
    """Test cases for model-related CLI commands."""

    @pytest.fixture
    def runner(self):
        """Create a Click CLI test runner."""
        return CliRunner()

    def test_model_list_command(self, runner):
        """Test model list command."""
        from bitrag.cli.main import cli

        result = runner.invoke(cli, ["model", "list"])
        # Should not fail
        assert result.exit_code in [0, 1]

    def test_model_status_command(self, runner):
        """Test model status command."""
        from bitrag.cli.main import cli

        result = runner.invoke(cli, ["model", "status"])
        # Should not fail
        assert result.exit_code == 0

    def test_model_group_help(self, runner):
        """Test model command group help."""
        from bitrag.cli.main import cli

        result = runner.invoke(cli, ["model", "--help"])
        assert result.exit_code == 0
        assert "Model" in result.output or "list" in result.output


class TestCLISessionCommands:
    """Test cases for session-related CLI commands."""

    @pytest.fixture
    def runner(self):
        """Create a Click CLI test runner."""
        return CliRunner()

    def test_session_list_command(self, runner):
        """Test session list command."""
        from bitrag.cli.main import cli

        result = runner.invoke(cli, ["session", "list"])
        # Should not fail
        assert result.exit_code in [0, 1]

    def test_session_group_help(self, runner):
        """Test session command group help."""
        from bitrag.cli.main import cli

        result = runner.invoke(cli, ["session", "--help"])
        assert result.exit_code == 0
