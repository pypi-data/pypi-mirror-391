# Copyright (C) 2025 Embedl AB
"""
Test cases for the embedl-hub CLI init command.

"""

import itertools

import pytest
import yaml
from typer.testing import CliRunner

from embedl_hub.cli.init import init_cli

CTX_CONFIG_FILENAME = "embedl_hub_config.yaml"
CTX_STATE_FILENAME = "embedl_hub_state.yaml"


class DummyCtx:
    def __init__(self, id, name):
        self.id = id
        self.name = name


def _load_yaml_from_path(path):
    """Load YAML content from the given file path."""
    return yaml.safe_load(path.read_text(encoding="utf-8"))


@pytest.fixture()
def temp_ctx_config_file(monkeypatch, tmp_path):
    """Use a temporary path for the context config file."""
    temp_ctx_config_file = tmp_path / CTX_CONFIG_FILENAME
    monkeypatch.setattr("embedl_hub.core.context.CONFIG_FILE", temp_ctx_config_file)
    return temp_ctx_config_file


@pytest.fixture()
def temp_ctx_state_file(monkeypatch, tmp_path):
    """Use a temporary path for the context state file."""
    temp_ctx_state_file = tmp_path / CTX_STATE_FILENAME
    monkeypatch.setattr("embedl_hub.core.context.STATE_FILE", temp_ctx_state_file)
    return temp_ctx_state_file


@pytest.fixture()
def ctx_obj():
    """Provide an empty CLI context object with config and state."""
    return {"config": {}, "state": {}}


@pytest.fixture(autouse=True)
def mock_tracking_and_ctx(monkeypatch):
    """
    Pytest fixture to mock tracking functions and redirect the context file
    to a temporary path. This prevents tests from making real API calls and
    from interfering with the user's actual context file.
    """
    # Mock tracking functions
    monkeypatch.setattr(
        "embedl_hub.core.utils.tracking_utils.set_project",
        lambda name: DummyCtx(f"dummy_project_id_{name}", name),
    )
    monkeypatch.setattr(
        "embedl_hub.core.utils.tracking_utils.set_experiment",
        lambda name: DummyCtx(f"dummy_experiment_id_{name}", name),
    )
    monkeypatch.setattr("embedl_hub.cli.utils.assert_api_config", lambda: None)


runner = CliRunner()


def test_init_new_project(ctx_obj, temp_ctx_config_file, temp_ctx_state_file):
    """Test creating a new project with the -p flag."""
    result = runner.invoke(init_cli, ["init", "-p", "MyProject"], obj=ctx_obj)

    assert result.exit_code == 0
    assert "✓ Project:" in result.output
    assert "✓ Experiment:" in result.output

    ctx_config_from_file = _load_yaml_from_path(temp_ctx_config_file)
    assert ctx_config_from_file["project_name"] == "MyProject"
    assert (
        ctx_config_from_file["experiment_name"].startswith("experiment_")
        or ctx_config_from_file["experiment_name"]
    )

    ctx_state_from_file = _load_yaml_from_path(temp_ctx_state_file)
    assert ctx_state_from_file["project_id"] == "dummy_project_id_MyProject"
    assert ctx_state_from_file["experiment_id"].startswith("dummy_experiment_id_")


def test_init_new_experiment(ctx_obj, temp_ctx_config_file, temp_ctx_state_file):
    """Test creating a new experiment with the -e flag in an existing project."""
    ctx_obj["config"]["project_name"] = "MyProject"
    ctx_obj["state"]["project_id"] = "dummy_project_id_MyProject"
    result = runner.invoke(init_cli, ["init", "-e", "MyExperiment"], obj=ctx_obj)

    assert result.exit_code == 0
    assert "✓ Experiment:" in result.output

    ctx_config_from_file = _load_yaml_from_path(temp_ctx_config_file)
    assert ctx_config_from_file["experiment_name"] == "MyExperiment"

    ctx_state_from_file = _load_yaml_from_path(temp_ctx_state_file)
    assert ctx_state_from_file["experiment_id"] == "dummy_experiment_id_MyExperiment"


def test_init_no_project_error(ctx_obj):
    """Test when creating an experiment without an initialized project leads to a new experiment."""
    result = runner.invoke(init_cli, ["init", "-e", "MyExperiment"], obj=ctx_obj)
    assert result.exit_code == 0
    assert "No active project, creating a new one" in result.output


def test_init_default_project_and_experiment(ctx_obj, temp_ctx_config_file, temp_ctx_state_file):
    """Test creating a default project and experiment with no flags."""
    result = runner.invoke(init_cli, ["init"], obj=ctx_obj)
    assert result.exit_code == 0
    assert "✓ Project:" in result.output
    assert "✓ Experiment:" in result.output

    ctx_config_from_file = _load_yaml_from_path(temp_ctx_config_file)
    assert ctx_config_from_file["project_name"].startswith("project_")
    assert ctx_config_from_file["experiment_name"].startswith("experiment_")

    ctx_state_from_file = _load_yaml_from_path(temp_ctx_state_file)
    assert ctx_state_from_file["project_id"].startswith("dummy_project_id_project_")
    assert ctx_state_from_file["experiment_id"].startswith("dummy_experiment_id_experiment_")


def test_init_switch_project_resets_experiment(ctx_obj, temp_ctx_config_file, temp_ctx_state_file):
    """Switching project should reset experiment context."""
    runner.invoke(init_cli, ["init", "-p", "Proj1", "-e", "Exp1"], obj=ctx_obj)
    ctx_state_from_file1 = _load_yaml_from_path(temp_ctx_state_file)
    runner.invoke(init_cli, ["init", "-p", "Proj2"], obj=ctx_obj)
    ctx_config_from_file2 = _load_yaml_from_path(temp_ctx_config_file)
    ctx_state_from_file2 = _load_yaml_from_path(temp_ctx_state_file)
    assert ctx_config_from_file2["project_name"] == "Proj2"
    assert ctx_state_from_file2["project_id"] == "dummy_project_id_Proj2"
    assert ctx_state_from_file2["project_id"] != ctx_state_from_file1["project_id"]
    assert ctx_state_from_file2["experiment_id"] != ctx_state_from_file1["experiment_id"]


def test_show_command_outputs_context(ctx_obj):
    """Test the show command prints the current context."""
    runner.invoke(init_cli, ["init", "-p", "ShowProj", "-e", "ShowExp"], obj=ctx_obj)
    result = runner.invoke(init_cli, ["show"], obj=ctx_obj)
    assert result.exit_code == 0
    assert "ShowProj" in result.output
    assert "ShowExp" in result.output


def test_ctx_config_file_created_and_updated(ctx_obj, temp_ctx_config_file):
    """Test that the ctx config file is created and updated as expected."""
    assert not temp_ctx_config_file.exists()
    runner.invoke(init_cli, ["init", "-p", "FileTestProj"], obj=ctx_obj)
    assert temp_ctx_config_file.exists()
    ctx_config_from_file1 = _load_yaml_from_path(temp_ctx_config_file)
    assert ctx_config_from_file1["project_name"] == "FileTestProj"
    runner.invoke(init_cli, ["init", "-e", "FileTestExp"], obj=ctx_obj)
    ctx_config_from_file2 = _load_yaml_from_path(temp_ctx_config_file)
    assert ctx_config_from_file2["experiment_name"] == "FileTestExp"


def test_ctx_state_file_created_and_updated(ctx_obj, temp_ctx_state_file):
    """Test that the ctx state file is created and updated as expected."""
    assert not temp_ctx_state_file.exists()
    runner.invoke(init_cli, ["init", "-p", "FileTestProj"], obj=ctx_obj)
    assert temp_ctx_state_file.exists()
    ctx_state_from_file1 = _load_yaml_from_path(temp_ctx_state_file)
    assert ctx_state_from_file1["project_id"] == "dummy_project_id_FileTestProj"
    runner.invoke(init_cli, ["init", "-e", "FileTestExp"], obj=ctx_obj)
    ctx_state_from_file2 = _load_yaml_from_path(temp_ctx_state_file)
    assert ctx_state_from_file2["experiment_id"] == "dummy_experiment_id_FileTestExp"


def test_init_always_creates_new_project_and_experiment(monkeypatch, ctx_obj, temp_ctx_state_file):
    """Test that running 'init' with no flags always creates a new project and experiment."""

    project_counter = itertools.count()
    experiment_counter = itertools.count()

    monkeypatch.setattr(
        "embedl_hub.core.utils.tracking_utils.set_project",
        lambda name: DummyCtx(
            f"dummy_project_id_{next(project_counter)}", name
        ),
    )
    monkeypatch.setattr(
        "embedl_hub.core.utils.tracking_utils.set_experiment",
        lambda name: DummyCtx(
            f"dummy_experiment_id_{next(experiment_counter)}", name
        ),
    )
    # First run: create initial context
    result1 = runner.invoke(init_cli, ["init"], obj=ctx_obj)
    assert result1.exit_code == 0
    ctx_state_from_file1 = _load_yaml_from_path(temp_ctx_state_file)
    project_id_1 = ctx_state_from_file1["project_id"]
    experiment_id_1 = ctx_state_from_file1["experiment_id"]
    # Second run: should create a new project and experiment, not reuse the old ones
    result2 = runner.invoke(init_cli, ["init"], obj=ctx_obj)
    assert result2.exit_code == 0
    ctx_state_from_file2 = _load_yaml_from_path(temp_ctx_state_file)
    project_id_2 = ctx_state_from_file2["project_id"]
    experiment_id_2 = ctx_state_from_file2["experiment_id"]
    assert project_id_2 != project_id_1, (
        "Project ID should change on each init with no flags"
    )
    assert experiment_id_2 != experiment_id_1, (
        "Experiment ID should change on each init with no flags"
    )


if __name__ == "__main__":
    pytest.main([__file__])
