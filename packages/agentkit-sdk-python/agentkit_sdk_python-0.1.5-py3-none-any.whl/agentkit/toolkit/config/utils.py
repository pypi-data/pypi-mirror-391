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

"""Configuration utility functions."""

from typing import Dict, Any

from .constants import AUTO_CREATE_VE


def is_invalid_config(s: str) -> bool:
    return s == None or s == "" or s == AUTO_CREATE_VE


def is_valid_config(s: str) -> bool:
    return not is_invalid_config(s)


def merge_runtime_envs(common_config: Any, workflow_config: Dict[str, Any]) -> Dict[str, str]:
    """合并应用级和 Workflow 级的环境变量
    
    合并规则：
    1. 先加载应用级环境变量（common_config.runtime_envs）
    2. 再加载 Workflow 级环境变量（workflow_config.runtime_envs）
    3. 同名变量：Workflow 级覆盖应用级
    
    Args:
        common_config: CommonConfig 实例
        workflow_config: Workflow 配置字典
        
    Returns:
        合并后的环境变量字典
    """
    merged_envs = {}
    
    # 1. 加载应用级环境变量
    app_level_envs = getattr(common_config, 'runtime_envs', {})
    if isinstance(app_level_envs, dict):
        merged_envs.update(app_level_envs)
    
    # 2. 加载 Workflow 级环境变量（会覆盖同名的应用级变量）
    workflow_level_envs = workflow_config.get('runtime_envs', {})
    if isinstance(workflow_level_envs, dict):
        merged_envs.update(workflow_level_envs)
    
    return merged_envs