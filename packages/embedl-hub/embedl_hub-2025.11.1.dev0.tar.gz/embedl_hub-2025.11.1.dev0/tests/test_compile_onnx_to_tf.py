# Copyright (C) 2025 Embedl AB

"""
Tests for compilation of ONNX models to TensorFlow/TFLite format.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from embedl_hub.core.compile.onnx_to_tf import compile_onnx_to_tflite


@patch('embedl_hub.core.compile.onnx_to_tf.onnx2tf')
@patch('pathlib.Path.mkdir')
def test_compile_onnx_to_tflite_with_output_folder(mock_mkdir, mock_onnx2tf):
    """Test conversion with specified output folder."""
    mock_onnx2tf.convert = Mock()

    onnx_path = Path("/path/to/model.onnx")
    output_folder = Path("/path/to/output")

    compile_onnx_to_tflite(onnx_path, output_folder)

    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    mock_onnx2tf.convert.assert_called_once_with(
        input_onnx_file_path=onnx_path,
        output_folder_path=output_folder,
    )


@patch('embedl_hub.core.compile.onnx_to_tf.onnx2tf')
@patch('pathlib.Path.mkdir')
def test_compile_onnx_to_tflite_without_output_folder(
    mock_mkdir, mock_onnx2tf
):
    """Test conversion without specified output folder."""
    mock_onnx2tf.convert = Mock()

    onnx_path = Path("/path/to/model.onnx")
    expected_output_path = onnx_path.parent / (onnx_path.stem + "_tf")

    compile_onnx_to_tflite(onnx_path)

    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    mock_onnx2tf.convert.assert_called_once_with(
        input_onnx_file_path=onnx_path,
        output_folder_path=expected_output_path,
    )


@patch('embedl_hub.core.compile.onnx_to_tf.onnx2tf')
@patch('pathlib.Path.mkdir')
def test_compile_onnx_to_tflite_with_none_output_folder(
    mock_mkdir, mock_onnx2tf
):
    """Test conversion with explicitly None output folder."""
    mock_onnx2tf.convert = Mock()

    onnx_path = Path("/path/to/model.onnx")
    expected_output_path = onnx_path.parent / (onnx_path.stem + "_tf")

    compile_onnx_to_tflite(onnx_path, None)

    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    mock_onnx2tf.convert.assert_called_once_with(
        input_onnx_file_path=onnx_path,
        output_folder_path=expected_output_path,
    )


if __name__ == "__main__":
    pytest.main([__file__])
