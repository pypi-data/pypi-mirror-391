# Copyright (C) 2025 Embedl AB
"""
Utilities for working with Hugging Face models.
"""

from pathlib import Path

from optimum.exporters.onnx import main_export


def export_huggingface_model_to_onnx(
    huggingface_id: str,
    output_path: Path,
    input_size: tuple[int, ...],
    skip_weights: bool = False,
):
    """
    Loads a model from Hugging Face, and exports it to an ONNX file.

    Args:
        huggingface_id: The ID of the model on Hugging Face Hub.
        output_path: The path to save the ONNX model.
        input_size: The input size for the model, e.g. (1, 128).
        skip_weights: If True, download model without weights.
    """
    main_export(
        model_name_or_path=huggingface_id,
        output=output_path,
        task="text-generation",
        do_validation=False,  # Validation can be slow and is not needed here
        no_post_process=True,  # We just want the raw ONNX model
    )
