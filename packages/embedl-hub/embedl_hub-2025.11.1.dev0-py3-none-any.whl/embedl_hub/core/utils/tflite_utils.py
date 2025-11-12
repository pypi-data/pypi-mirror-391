# Copyright (C) 2025 Embedl AB
"""
Utility functions for working with TFLite models.
"""

import tensorflow as tf


def instantiate_tflite_interpreter(
    model_path: str, experimental_preserve_all_tensors: bool = False
) -> tf.lite.Interpreter:
    """Instantiate a TFLite interpreter and allocate tensors."""
    interpreter = tf.lite.Interpreter(
        model_path=model_path,
        experimental_preserve_all_tensors=experimental_preserve_all_tensors,
    )
    interpreter.allocate_tensors()
    return interpreter


def get_tflite_model_input_names(model_path: str) -> list[str]:
    """Get the input tensor names of a TFLite model.

    Args:
        model_path: Path to the TFLite model file.

    Returns:
        A list of input tensor names.
    """
    interpreter = instantiate_tflite_interpreter(model_path)

    signatures: dict[str, dict[str, list[str]]] = (
        interpreter.get_signature_list()
    )
    signature_key = list(signatures.keys())[0]
    return signatures[signature_key]['inputs']
