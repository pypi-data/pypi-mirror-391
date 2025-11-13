# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd. and/or its affiliates.
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

import json

import yaml
from pydantic import BaseModel

from agentkit.toolkit.config.build_config import BuildConfig
from agentkit.toolkit.config.deploy_config import DeployConfig
from agentkit.toolkit.consts import DEFAULT_CONFIG_FILENAME


# class ConfigManager(BaseModel):
#     """Config manager for AgentKit-related configurations."""

#     build_config: BuildConfig

#     deploy_config: DeployConfig

#     def dump(self, filename: str = DEFAULT_CONFIG_FILENAME):
#         """Dump self attributes to a `.yaml` file."""
#         data = self.model_dump()
#         yaml_str = yaml.dump(data=data)

#         with open(filename, "w", encoding="utf-8") as f:
#             f.write(yaml_str)

#     @staticmethod
#     def load(filename: str = DEFAULT_CONFIG_FILENAME) -> "ConfigManager":
#         with open(filename, "r", encoding="utf-8") as f:
#             data = f.read()

#         if data:
#             return ConfigManager(**json.loads(data))
#         else:
#             raise ValueError("Empty config file content!")
