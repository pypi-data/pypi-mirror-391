# Copyright (C) 2025 Embedl AB

"""
Compile PyTorch models to TFLite using AI Edge Torch.
"""

from pathlib import Path

import ai_edge_torch
import torch
from torch import nn


def compile_torch_to_tflite(
    model: nn.Module,
    float_model_path: Path,
    sample_args: tuple[torch.Tensor, ...] | None = None,
    sample_kwargs: dict[str, torch.Tensor] | None = None,
):
    """Compile a PyTorch model to TFLite format using AI Edge Torch.

    Args:
        model: The PyTorch model to convert.
        sample_args: Sample positional arguments for the model's forward method.
        sample_kwargs: Sample keyword arguments for the model's forward method.
        float_model_path: Path to save the converted TFLite model.
    """
    edge_model = ai_edge_torch.convert(
        model, sample_args=sample_args, sample_kwargs=sample_kwargs
    )
    edge_model.export(float_model_path)
