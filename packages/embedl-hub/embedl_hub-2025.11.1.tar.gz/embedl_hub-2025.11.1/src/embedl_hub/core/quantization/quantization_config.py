# Copyright (C) 2025 Embedl AB

"""Configuration for quantizing models."""

from pathlib import Path

from embedl_hub.core.config import ExperimentConfig


class QuantizationConfig(ExperimentConfig):
    """Class for quantization configuration."""

    # User specific parameters
    model: Path
    data_path: Path | None
    output_file: Path
    num_samples: int
