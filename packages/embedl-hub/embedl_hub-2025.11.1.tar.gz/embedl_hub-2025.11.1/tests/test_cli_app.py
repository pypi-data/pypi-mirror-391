# Copyright (C) 2025 Embedl AB
"""
Test cases for the embedl-hub CLI main app module.

This module tests the main CLI entry point, including the main callback,
version handling, logging setup, and context initialization.
"""

from unittest.mock import MagicMock, patch

import pytest
import typer
from typer.testing import CliRunner

from embedl_hub.cli.app import _version_callback, app, main

runner = CliRunner()


@patch("embedl_hub.cli.app.metadata")
@patch("embedl_hub.cli.app.console")
def test_version_callback_prints_version_and_exits(
    mock_console, mock_metadata
):
    """Test that version callback prints version and exits when value is True."""
    # Arrange
    mock_metadata.version.return_value = "2025.11.1"

    # Act & Assert
    with pytest.raises(typer.Exit):
        _version_callback(True)

    mock_metadata.version.assert_called_once_with('embedl-hub')
    mock_console.print.assert_called_once_with("embedl-hub 2025.11.1")


@pytest.mark.parametrize("value", [False, None])
@patch("embedl_hub.cli.app.metadata")
@patch("embedl_hub.cli.app.console")
def test_version_callback_does_nothing_when_falsy(
    mock_console, mock_metadata, value
):
    """Test that version callback does nothing when value is falsy."""
    # Act
    _version_callback(value)

    # Assert
    mock_metadata.version.assert_not_called()
    mock_console.print.assert_not_called()


@patch("embedl_hub.core.context.load_ctx_state")
@patch("embedl_hub.core.context.load_ctx_config")
@patch("embedl_hub.core.hub_logging.setup_logging")
def test_main_callback_sets_up_logging_and_context(
    mock_setup_logging, mock_load_ctx_config, mock_load_ctx_state
):
    """Test that main callback sets up logging and context correctly."""
    # Arrange
    mock_ctx = MagicMock()
    mock_ctx.ensure_object.return_value = None
    mock_ctx.obj = {}
    mock_config = {"api_key": "test-key"}
    mock_state = {"experiment_id": "test-exp-id"}
    mock_load_ctx_config.return_value = mock_config
    mock_load_ctx_state.return_value = mock_state

    # Act
    main(mock_ctx, version=False, verbose=2)

    # Assert
    mock_setup_logging.assert_called_once_with(2)
    mock_ctx.ensure_object.assert_called_once_with(dict)
    mock_load_ctx_config.assert_called_once()
    mock_load_ctx_state.assert_called_once()
    assert mock_ctx.obj["config"] == mock_config
    assert mock_ctx.obj["state"] == mock_state


@pytest.mark.parametrize("verbose_level", [0, 1, 2, 3])
@patch("embedl_hub.core.context.load_ctx_state")
@patch("embedl_hub.core.context.load_ctx_config")
@patch("embedl_hub.core.hub_logging.setup_logging")
def test_main_callback_with_verbosity_levels(
    mock_setup_logging,
    mock_load_ctx_config,
    mock_load_ctx_state,
    verbose_level,
):
    """Test main callback with different verbosity levels."""
    # Arrange
    mock_ctx = MagicMock()
    mock_ctx.obj = {}

    # Act
    main(mock_ctx, version=None, verbose=verbose_level)

    # Assert
    mock_setup_logging.assert_called_once_with(verbose_level)


def test_app_is_typer_instance():
    """Test that app is a Typer instance with correct configuration."""
    # Assert
    assert isinstance(app, typer.Typer)


def test_app_has_correct_help_text():
    """Test that app has the correct help text."""
    # Act
    result = runner.invoke(app, ["--help"])

    # Assert
    assert result.exit_code == 0
    assert "embedl-hub" in result.stdout
    assert "end-to-end Edge-AI workflow CLI" in result.stdout


def test_app_no_args_shows_help():
    """Test that running app without arguments shows help."""
    # Act
    result = runner.invoke(app, [])

    # Assert
    # Typer exits with code 2 when no command is provided but help is shown
    assert result.exit_code == 2
    assert "Usage:" in result.stdout


@pytest.mark.parametrize("version_option", ["-V", "--version"])
@patch("embedl_hub.cli.app.metadata")
@patch("embedl_hub.cli.app.console")
def test_version_option(mock_console, mock_metadata, version_option):
    """Test version options (-V and --version)."""
    # Arrange
    mock_metadata.version.return_value = "2025.11.1"

    # Act
    result = runner.invoke(app, [version_option])

    # Assert
    assert result.exit_code == 0
    mock_console.print.assert_called_once_with("embedl-hub 2025.11.1")


@pytest.mark.parametrize(
    "verbose_option,expected_level",
    [
        ("-v", 1),
        ("-vv", 2),
        ("-vvv", 3),
        ("--verbose", 1),
    ],
)
@patch("embedl_hub.core.context.load_ctx_state")
@patch("embedl_hub.core.context.load_ctx_config")
@patch("embedl_hub.core.hub_logging.setup_logging")
def test_verbose_options(
    mock_setup_logging,
    mock_load_ctx_config,
    mock_load_ctx_state,
    verbose_option,
    expected_level,
):
    """Test verbose options with actual command execution."""
    # Act
    # Using a real subcommand to ensure callback is executed
    result = runner.invoke(app, [verbose_option, "auth", "--help"])

    # Assert
    assert result.exit_code == 0
    mock_setup_logging.assert_called_with(expected_level)


@patch("embedl_hub.core.context.load_ctx_state")
@patch("embedl_hub.core.context.load_ctx_config")
def test_context_object_initialization(
    mock_load_ctx_config, mock_load_ctx_state
):
    """Test that context object is properly initialized."""
    # Arrange
    mock_config = {
        "api_key": "test-key",
        "base_url": "https://api.test.com",
    }
    mock_state = {"experiment_id": "exp-123", "device_id": "dev-456"}
    mock_load_ctx_config.return_value = mock_config
    mock_load_ctx_state.return_value = mock_state

    # Act
    # Using a real subcommand to ensure callback is executed
    result = runner.invoke(app, ["auth", "--help"])

    # Assert
    assert result.exit_code == 0
    mock_load_ctx_config.assert_called_once()
    mock_load_ctx_state.assert_called_once()


def test_help_option_shows_all_commands():
    """Test that help shows all registered commands."""
    # Act
    result = runner.invoke(app, ["--help"])

    # Assert
    assert result.exit_code == 0
    # Check that the Commands section is shown
    assert "Commands" in result.stdout
    # Check that some of the main commands are listed
    assert "auth" in result.stdout
    assert "benchmark" in result.stdout
    assert "compile" in result.stdout
    assert "init" in result.stdout
    assert "list-devices" in result.stdout
    assert "quantize" in result.stdout


@patch("embedl_hub.core.context.load_ctx_state")
@patch("embedl_hub.core.context.load_ctx_config")
def test_context_loading_exception_handling(
    mock_load_ctx_config, mock_load_ctx_state
):
    """Test that exceptions during context loading cause the app to exit with error code."""
    # Arrange
    mock_load_ctx_config.side_effect = Exception("Config loading failed")

    # Act
    result = runner.invoke(app, ["auth", "--help"])

    # Assert
    # Typer catches exceptions and returns exit code 1
    assert result.exit_code == 1


@patch("embedl_hub.cli.app.metadata")
def test_version_callback_metadata_exception(mock_metadata):
    """Test version callback when metadata.version raises an exception."""
    # Arrange
    mock_metadata.version.side_effect = Exception("Metadata error")

    # Act & Assert
    with pytest.raises(Exception, match="Metadata error"):
        _version_callback(True)


def test_app_shows_help_when_no_args():
    """Test that no_args_is_help is properly configured."""
    # Act
    result = runner.invoke(app, [])

    # Assert
    # Typer exits with code 2 when no command is provided but shows help
    assert result.exit_code == 2
    assert "Usage:" in result.stdout
    assert "embedl-hub" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__])
