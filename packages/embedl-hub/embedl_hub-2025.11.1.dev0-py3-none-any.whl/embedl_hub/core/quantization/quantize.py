# Copyright (C) 2025 Embedl AB

"""Module for quantizing ONNX models using Qualcomm AI Hub."""

from __future__ import annotations

import zipfile
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import qai_hub as hub

from embedl_hub.core.hub_logging import console
from embedl_hub.core.quantization.psnr import measure_psnr_between_models
from embedl_hub.core.quantization.quantization_config import QuantizationConfig
from embedl_hub.core.utils.onnx_utils import (
    load_onnx_model,
    maybe_package_onnx_folder_to_file,
)
from embedl_hub.core.utils.tracking_utils import experiment_context
from embedl_hub.tracking import (
    Metric,
    Parameter,
    RunType,
    log_param,
    update_run,
)


class QuantizationError(RuntimeError):
    """Raised when Qualcomm AI Hub quantization job fails or times out."""


@dataclass
class QuantizationResult:
    """Result of a quantization job."""

    model_path: Path
    job_id: str


def get_input_shapes(model_path: Path) -> dict[str, tuple[int, ...]]:
    """
    Get the input shape of the ONNX model.

    Args:
        model_path: Path to the ONNX model.

    Returns:
        Dictionary with input names and their shapes.
    """

    onnx_model = load_onnx_model(model_path)
    input_shapes = {}
    for model_input in onnx_model.graph.input:
        shape = []
        for dim in model_input.type.tensor_type.shape.dim:
            if dim.dim_value > 0:
                shape.append(dim.dim_value)
            else:
                shape.append(1)  # Use 1 for dynamic dimensions
        input_shapes[model_input.name] = tuple(shape)
    return input_shapes


def _generate_random_data(
    config: QuantizationConfig,
) -> dict[str, list[np.ndarray]]:
    """
    Generate random calibration data for quantization.

    Args:
        config: QuantizationConfig.

    Returns:
        Dictionary with random calibration data.
    """
    config.num_samples = 1

    def _make_random_sample(shape: tuple[int, ...]) -> np.ndarray:
        """Generate a random sample with the given shape."""
        return np.random.rand(*shape).astype(np.float32)

    inputs_and_shapes = get_input_shapes(config.model)

    return {
        input_name: [_make_random_sample(shape)]
        for input_name, shape in inputs_and_shapes.items()
    }


def make_calibration_dataset(
    config: QuantizationConfig,
) -> dict[str, list[np.ndarray]]:
    """
    Create a Dataset for calibration data.

    Args:
        config: QuantizationConfig containing data_path.

    If single input, data path should contain numpy files (.npy).
    If multiple inputs, data path should contain subdirectories named after
    the input names, each containing numpy files (.npy).

    Returns:
        Dataset for calibration data.
    """
    data_path = config.data_path
    if not data_path or not data_path.is_dir():
        raise ValueError(f"Invalid data path: {data_path}")

    onnx_model = load_onnx_model(config.model)
    input_names = [i.name for i in onnx_model.graph.input]

    if len(input_names) == 1:
        # Single input model
        input_name = input_names[0]
        npy_files = sorted(data_path.glob("*.npy"))
        if not npy_files:
            raise FileNotFoundError(f"No .npy files found in {data_path}")
        return {input_name: [np.load(f) for f in npy_files]}

    # Multiple input model
    datasets = {}
    num_input_samples = set()
    for input_name in input_names:
        input_dir = data_path / input_name
        if not input_dir.is_dir():
            raise FileNotFoundError(
                f"Input directory not found for input '{input_name}': {input_dir}"
            )
        npy_files = sorted(input_dir.glob("*.npy"))
        if not npy_files:
            raise FileNotFoundError(f"No .npy files found in {input_dir}")
        datasets[input_name] = [np.load(f) for f in npy_files]
        num_input_samples.add(len(datasets[input_name]))

    if len(num_input_samples) != 1:
        raise ValueError("All inputs must have the same number of samples.")
    return datasets


def _load_calibration_data(
    config: QuantizationConfig,
) -> dict[str, list[np.ndarray]]:
    """
    Load calibration data from the specified path.

    Args:
        config: QuantizationConfig containing data_path and transforms.

    Returns:
        Dictionary with calibration data.
    """

    dataset = make_calibration_dataset(config)
    for input_name, input_samples in dataset.items():
        dataset[input_name] = input_samples[: config.num_samples]
        config.num_samples = min(config.num_samples, len(dataset[input_name]))

    return dataset


def collect_calibration_data(
    config: QuantizationConfig,
) -> dict[str, list[np.ndarray]]:
    """
    Collect calibration data for quantization.

    Args:
        config: QuantizationConfig containing data_path and transforms.

    Returns:
        Dictionary with calibration data.
    """
    if config.data_path is None:
        console.print(
            "[yellow]No data path specified, generating random calibration data.[/]"
        )
        return _generate_random_data(config)
    return _load_calibration_data(config)


def _save_quantized(quantized: hub.Model, output_file: Path) -> Path:
    """
    Save the quantized artifact to a user-specified location or to the root
    directory with the name provided by Qualcomm AI Hub.

    Returns:
        Path to the saved model file.
    """
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file = Path(quantized.download(str(output_file)))
    return output_file


def log_config_params(config: QuantizationConfig) -> None:
    """Log the configuration parameters for tracking."""

    def _format_img_size(value: int | list[int]) -> str:
        """Format image size for logging."""
        return str(value).strip("[]").replace(", ", "x").strip()

    log_param("num samples", str(config.num_samples))

    def _find_input_sizes(
        config: QuantizationConfig,
    ) -> list[tuple[str, list[int]]]:
        """Find input sizes from the model."""
        onnx_model = load_onnx_model(config.model)
        input_sizes = []
        for model_input in onnx_model.graph.input:
            shape = []
            for dim in model_input.type.tensor_type.shape.dim:
                if dim.dim_value > 0:
                    shape.append(dim.dim_value)
                else:
                    shape.append(1)  # Use 1 for dynamic dimensions
            input_sizes.append((model_input.name, shape))
        return input_sizes

    for input_name, shape in _find_input_sizes(config):
        log_param(f"{input_name} input shape", _format_img_size(shape))


def _log_psnr_results(layer_psnr: list[dict], output_psnr: list[dict]) -> None:
    """Log PSNR results to the tracking system."""
    params_to_log: list[Parameter] = []
    metrics_to_log: list[Metric] = []
    for idx, layer in enumerate(layer_psnr):
        layer_name = Parameter(name=f"$layer_name_{idx}", value=layer["layer"])
        per_layer_psnr = Metric(
            name="$psnr_per_layer",
            value=layer["psnr"],
            step=idx,
        )
        layer_shape = " ".join(str(x) for x in layer["shape"]) or "1"
        layer_shape = Parameter(name=f"$layer_shape_{idx}", value=layer_shape)
        params_to_log.extend([layer_name, layer_shape])
        metrics_to_log.append(per_layer_psnr)
        if "notes" in layer:
            layer_notes = Parameter(
                name=f"$layer_notes_{idx}", value=layer["notes"]
            )
            params_to_log.append(layer_notes)

    for idx, output in enumerate(output_psnr):
        output_name = Parameter(
            name=f"$output_name_{idx}", value=output["layer"]
        )
        output_psnr = Metric(name=f"$output_psnr_{idx}", value=output["psnr"])
        output_shape = " ".join(str(x) for x in output["shape"]) or "1"
        output_shape = Parameter(
            name=f"$output_shape_{idx}", value=output_shape
        )
        params_to_log.extend([output_name, output_shape])
        metrics_to_log.append(output_psnr)
        if "notes" in output:
            output_notes = Parameter(
                name=f"$output_notes_{idx}", value=output["notes"]
            )
            params_to_log.append(output_notes)
    update_run(
        metrics=metrics_to_log,
        params=params_to_log,
    )


def _maybe_unzip_model(model_path: Path, tmp_folder: Path) -> Path:
    """Unzip the model if it is a zip file and return the ONNX file path."""
    if model_path.suffix == ".zip":
        with zipfile.ZipFile(model_path, "r") as zip_ref:
            extract_path = tmp_folder / model_path.stem
            zip_ref.extractall(extract_path)
            subfolders = [f for f in extract_path.iterdir() if f.is_dir()]
            if len(subfolders) != 1:
                raise RuntimeError(
                    f"Expected exactly one folder in the zip, found: {len(subfolders)}"
                )
            only_folder = subfolders[0]
            onnx_files = list(only_folder.rglob("*.onnx"))
            if len(onnx_files) != 1:
                raise RuntimeError(
                    f"Expected exactly one .onnx file, found: {len(onnx_files)}"
                )
            return onnx_files[0]
    return model_path


def quantize_model(
    config: QuantizationConfig,
    project_name: str,
    experiment_name: str,
) -> None:
    """
    Submit an ONNX model to Qualcomm AI Hub and retrieve the compiled artifact.

    Args:
        config: QuantizationConfig containing model_path, data_path, and transforms.

    Returns:
        QuantizationResult with local path to compiled model.

    """

    with experiment_context(project_name, experiment_name, RunType.QUANTIZE):
        if not config.model.exists():
            raise ValueError(f"Model not found: {config.model}")

        calibration_data = collect_calibration_data(config)
        log_config_params(config)

        with TemporaryDirectory() as tmpdir:
            config.model = maybe_package_onnx_folder_to_file(
                config.model, tmpdir
            )
            try:
                job = hub.submit_quantize_job(
                    model=config.model.as_posix(),
                    weights_dtype=hub.QuantizeDtype.INT8,
                    activations_dtype=hub.QuantizeDtype.INT8,
                    calibration_data=calibration_data,
                )
            except Exception as error:
                raise QuantizationError(
                    "Failed to submit quantization job."
                ) from error

            log_param("$qai_hub_job_id", job.job_id)

            try:
                quantized = job.get_target_model()
            except Exception as error:
                raise QuantizationError(
                    "Failed to download quantized model from Qualcomm AI Hub."
                ) from error
            if quantized is None:
                raise QuantizationError(
                    "Quantized model returned by Qualcomm AI Hub is None."
                )

            layer_psnr = []
            output_psnr = []

            local_path = _save_quantized(quantized, config.output_file)
            try:
                with TemporaryDirectory() as tmpdir:
                    tmpdir_path = Path(tmpdir)
                    layer_psnr, output_psnr = measure_psnr_between_models(
                        config.model,
                        _maybe_unzip_model(local_path, tmpdir_path),
                        calibration_data,
                    )
            except Exception as error:
                pass  # PSNR measurement is optional, ignore errors

        _log_psnr_results(layer_psnr, output_psnr)

        console.print(f"[green]✓ Quantized model saved to {local_path}[/]")
