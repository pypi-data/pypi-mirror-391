# Copyright (C) 2025 Embedl AB
# Copyright 2024 The AI Edge Quantizer Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Python adaptation of this json:
# https://github.com/google-ai-edge/ai-edge-quantizer/blob/main/ai_edge_quantizer/recipes/default_a16w8_recipe.json

# TODO: Remove this module when we are able to upgrade ai-edge-torch to 0.6.0+
def static_wi8_ai8():
    return [
        {
            "regex": ".*",
            "operation": "*",
            "algorithm_key": "min_max_uniform_quantize",
            "op_config": {
                "activation_tensor_config": {
                    "num_bits": 8,
                    "symmetric": False,
                    "granularity": "TENSORWISE",
                    "dtype": "INT",
                    "block_size": 0,
                },
                "weight_tensor_config": {
                    "num_bits": 8,
                    "symmetric": True,
                    "granularity": "CHANNELWISE",
                    "dtype": "INT",
                    "block_size": 0,
                },
                "compute_precision": "INTEGER",
                "explicit_dequantize": False,
                "skip_checks": False,
                "min_weight_elements": 0,
            },
        }
    ]
