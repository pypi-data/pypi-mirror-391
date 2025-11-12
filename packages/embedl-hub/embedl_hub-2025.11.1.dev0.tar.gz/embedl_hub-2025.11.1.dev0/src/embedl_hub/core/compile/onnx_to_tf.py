# Copyright (C) 2025 Embedl AB

"""
Convert ONNX models to TensorFlow/TFLite format."""

from pathlib import Path
from tempfile import TemporaryDirectory

import onnx2tf

from embedl_hub.core.compile.abc import Compiler, CompileResult
from embedl_hub.core.utils.onnx_utils import maybe_package_onnx_folder_to_file
from embedl_hub.core.utils.tracking_utils import experiment_context
from embedl_hub.tracking import RunType


# pylint: disable-next=too-few-public-methods
class ONNXToTFCompiler(Compiler):
    """Compiler that converts ONNX models to TensorFlow/TFLite format."""

    def __init__(
        self,
        output_folder_path: Path | None = None,
    ):
        self.output_folder_path = output_folder_path

    def compile(
        self,
        project_name: str,
        experiment_name: str,
        model_path: Path,
    ) -> CompileResult:
        """
        Compile an ONNX model to TensorFlow/TFLite format.

        Args:
            project_name: Name of the project.
            experiment_name: Name of the experiment.
            model_path: Path to the input ONNX model file.
        """

        if not model_path.exists():
            raise ValueError(f"Model not found: {model_path}")

        with experiment_context(
            project_name, experiment_name, RunType.COMPILE
        ):
            with TemporaryDirectory() as tmpdir:
                model_path = maybe_package_onnx_folder_to_file(
                    model_path, tmpdir
                )
                return compile_onnx_to_tflite(
                    onnx_model_path=model_path,
                    output_folder_path=self.output_folder_path,
                )


def compile_onnx_to_tflite(
    onnx_model_path: Path,
    output_folder_path: Path | None = None,
) -> CompileResult:
    """Convert an ONNX model to TensorFlow/TFLite format.

    The result is a saved TensorFlow model and two TFLite (both float32 and float16)
    models in the specified output folder.

    Args:
        onnx_model_path: Path to the input ONNX model file.
        output_folder_path: Path to save the converted TensorFlow and TFLite models.
    """
    if output_folder_path is None:
        output_folder_path = onnx_model_path.parent / (
            onnx_model_path.stem + "_tf"
        )
    output_folder_path.mkdir(parents=True, exist_ok=True)

    onnx2tf.convert(
        input_onnx_file_path=onnx_model_path,
        output_folder_path=output_folder_path,
    )
    return CompileResult(model_path=output_folder_path)
