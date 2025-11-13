# Copyright (C) 2025 Embedl AB

"""Test the CLI for quantizing models using the Embedl Hub SDK."""

from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from embedl_hub.cli.quantize import quantize_cli

runner = CliRunner()


@pytest.fixture
def empty_ctx_obj():
    """Provide an empty context object with config and state."""
    return {"config": {}, "state": {}}


def test_quantize_cli_uses_default_config(empty_ctx_obj):
    """
    Test the CLI with default configuration.

    The test should fail due to lacking config settings.
    """
    result = runner.invoke(quantize_cli, obj=empty_ctx_obj)
    assert result.exit_code == 2
    assert isinstance(result.exception, SystemExit)


def test_quantize_cli_overrides_with_flags(monkeypatch, empty_ctx_obj):
    """Test the CLI with command-line flags to override default configuration."""

    captured = {}

    # pylint: disable-next=unused-argument
    def fake_quantize_model(config, project_name, experiment_name):
        """Fake quantize_model function to capture the config."""
        captured["cfg"] = config

    monkeypatch.setattr(
        "embedl_hub.core.quantization.quantize.quantize_model",
        fake_quantize_model,
    )
    monkeypatch.setattr('embedl_hub.cli.utils.assert_api_config', lambda: None)

    args = [
        "--model",
        "my-model",
        "--data",
        "/other/data",
    ]
    empty_ctx_obj["config"]["project_name"] = "test_project"
    empty_ctx_obj["config"]["experiment_name"] = "test_experiment"
    result = runner.invoke(quantize_cli, args, obj=empty_ctx_obj)
    assert result.exit_code == 0

    cfg = captured["cfg"]
    assert cfg.model == Path("my-model")
    assert cfg.data_path == Path("/other/data")
    assert cfg.num_samples == 500  # default


def test_quantize_cli_with_custom_config_file(tmp_path, monkeypatch, empty_ctx_obj):
    """Test the CLI with a custom YAML configuration file."""

    # Create a custom YAML and pass via --config
    custom = {
        "data_path": "/mnt/x",
        "num_samples": 128,
    }
    custom_path = tmp_path / "custom.yaml"
    custom_path.write_text(yaml.dump(custom))

    captured = {}

    # pylint: disable-next=unused-argument
    def fake_quantize_model(config, project_name, experiment_name):
        """Fake quantize_model function to capture the config."""
        captured["cfg"] = config

    monkeypatch.setattr(
        "embedl_hub.core.quantization.quantize.quantize_model",
        fake_quantize_model,
    )
    monkeypatch.setattr('embedl_hub.cli.utils.assert_api_config', lambda: None)

    empty_ctx_obj["config"]["project_name"] = "test_project"
    empty_ctx_obj["config"]["experiment_name"] = "test_experiment"
    result = runner.invoke(
        quantize_cli,
        ["--model", "from-cli", "--config", str(custom_path)],
        obj=empty_ctx_obj,
    )
    assert result.exit_code == 0

    cfg = captured["cfg"]
    assert cfg.model == Path("from-cli")
    assert cfg.data_path == Path("/mnt/x")
    assert cfg.num_samples == 128


if __name__ == "__main__":
    pytest.main([__file__])
