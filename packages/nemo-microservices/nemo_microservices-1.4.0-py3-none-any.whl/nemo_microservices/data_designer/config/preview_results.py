# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

from typing import Optional

import pandas as pd

from .analysis.dataset_profiler import DatasetProfilerResults
from .config_builder import DataDesignerConfigBuilder
from .utils.visualization import WithRecordSamplerMixin


class PreviewResults(WithRecordSamplerMixin):
    def __init__(
        self,
        *,
        config_builder: DataDesignerConfigBuilder,
        dataset: Optional[pd.DataFrame] = None,
        analysis: Optional[DatasetProfilerResults] = None,
    ):
        """Creates a new instance with results from a Data Designer preview run.

        Args:
            config_builder: Data Designer configuration builder.
            dataset: Dataset of the preview run.
            analysis: Analysis of the preview run.
        """
        self.dataset: pd.DataFrame | None = dataset
        self.analysis: DatasetProfilerResults | None = analysis
        self._config_builder = config_builder
