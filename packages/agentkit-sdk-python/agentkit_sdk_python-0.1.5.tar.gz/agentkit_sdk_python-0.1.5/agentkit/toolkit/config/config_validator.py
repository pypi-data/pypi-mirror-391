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

"""Configuration validation utilities."""

import re
from typing import List, Any
from dataclasses import fields

from agentkit.toolkit.config.config import CommonConfig


class ConfigValidator:
    """配置验证器"""
    
    @staticmethod
    def validate_common_config(config: CommonConfig) -> List[str]:
        """验证通用配置，返回错误列表
        
        Args:
            config: CommonConfig 实例
            
        Returns:
            错误消息列表，如果为空则验证通过
        """
        errors = []
        
        # 遍历所有字段并应用验证规则
        for field in fields(CommonConfig):
            # 跳过内部字段
            if field.name.startswith('_'):
                continue
                
            validation = field.metadata.get('validation', {})
            value = getattr(config, field.name)
            
            # 检查必填项
            if validation.get('required') and (not value or (isinstance(value, str) and not value.strip())):
                desc = field.metadata.get('description', field.name)
                errors.append(f"{desc} 是必填项")
                continue
            
            # 检查正则表达式模式
            pattern = validation.get('pattern')
            if pattern and value and isinstance(value, str):
                if not re.match(pattern, value):
                    desc = field.metadata.get('description', field.name)
                    msg = validation.get('message', '格式不正确')
                    errors.append(f"{desc}: {msg}")
            
            # 检查选项约束
            choices = field.metadata.get('choices')
            if choices and value:
                valid_values = []
                if isinstance(choices, list):
                    if choices and isinstance(choices[0], dict):
                        valid_values = [c['value'] for c in choices]
                    else:
                        valid_values = choices
                
                if valid_values and value not in valid_values:
                    desc = field.metadata.get('description', field.name)
                    errors.append(f"{desc} 的值必须是以下之一: {', '.join(map(str, valid_values))}")
        
        return errors
    
    @staticmethod
    def validate_field_value(field_name: str, value: Any, field_metadata: dict) -> List[str]:
        """验证单个字段的值
        
        Args:
            field_name: 字段名称
            value: 字段值
            field_metadata: 字段的元数据
            
        Returns:
            错误消息列表
        """
        errors = []
        validation = field_metadata.get('validation', {})
        
        # 检查必填项
        if validation.get('required') and (not value or (isinstance(value, str) and not value.strip())):
            desc = field_metadata.get('description', field_name)
            errors.append(f"{desc} 是必填项")
            return errors
        
        # 检查正则表达式模式
        pattern = validation.get('pattern')
        if pattern and value and isinstance(value, str):
            if not re.match(pattern, value):
                desc = field_metadata.get('description', field_name)
                msg = validation.get('message', '格式不正确')
                errors.append(f"{desc}: {msg}")
        
        # 检查选项约束
        choices = field_metadata.get('choices')
        if choices and value:
            valid_values = []
            if isinstance(choices, list):
                if choices and isinstance(choices[0], dict):
                    valid_values = [c['value'] for c in choices]
                else:
                    valid_values = choices
            
            if valid_values and value not in valid_values:
                desc = field_metadata.get('description', field_name)
                errors.append(f"{desc} 的值必须是以下之一: {', '.join(map(str, valid_values))}")
        
        return errors
