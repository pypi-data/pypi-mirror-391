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

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple
import logging
from pathlib import Path
from agentkit.toolkit.config.config import get_global_config_file_path

logger = logging.getLogger(__name__)


class Builder(ABC):
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        # 设置工作目录：根据GLOBAL_CONFIG_FILE_PATH解析
        self.workdir = self._get_workdir_from_config()
    
    def _get_workdir_from_config(self) -> Path:
        """从全局配置文件路径解析工作目录"""
        config_path = get_global_config_file_path()
        
        if config_path:
            # 提取GLOBAL_CONFIG_FILE_PATH的文件夹路径
            path_obj = Path(config_path).expanduser()
            if path_obj.is_file():
                # 如果是文件路径，提取父目录
                return path_obj.parent
            else:
                # 如果是目录路径，直接使用
                return path_obj
        else:
            # 如果GLOBAL_CONFIG_FILE_PATH为空，使用当前工作目录
            return Path.cwd()
    
    @abstractmethod
    def build(self, config: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        pass
    
    @abstractmethod
    def check_artifact_exists(self, config: Dict[str, Any]) -> bool:
        pass
    
    @abstractmethod
    def remove_artifact(self, config: Dict[str, Any]) -> bool:
        pass