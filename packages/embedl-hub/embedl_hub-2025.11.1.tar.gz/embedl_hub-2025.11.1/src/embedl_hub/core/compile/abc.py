# Copyright (C) 2025 Embedl AB

"""
Abstract base classes for model compilers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


# TODO: Change wording when other compilers than Qualcomm AI Hub are added
class CompileError(RuntimeError):
    """Raised when Qualcomm AI Hub compile job fails or times out."""


# TODO: Maybe make job_id optional if not all compilers have job ids
# TODO: Maybe make device optional if not all compilers target specific devices
@dataclass
class CompileResult:
    """Result of a successful compile job."""

    model_path: Path  # local .tflite, .bin, or .onnx after compile
    job_id: str | None = None
    device: str | None = None


# pylint: disable-next=too-few-public-methods
class Compiler(ABC):
    """Abstract base class for model compilers."""

    @abstractmethod
    def compile(
        self, project_name: str, experiment_name: str, model_path: Path
    ) -> CompileResult:
        """
        Compile the model.

        A compiler is responsible for taking a model and compiling it for a specific device
        and/or runtime. The specifics of the compilation process will depend on the
        implementation.

        Args:
            project_name: Name of the project.
            experiment_name: Name of the experiment.
            model_path: Path to the input model file.

        Returns:
            CompileResult: The result of the compilation.

        Raises:
            CompileError: If the compilation fails.
        """
        raise NotImplementedError("Subclasses must implement this method.")
