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


from dataclasses import asdict, fields
from typing import Any, Dict, Type, TypeVar, get_type_hints

T = TypeVar('T')

class DataclassSerializer:
    
    @staticmethod
    def to_dict(obj: Any) -> Dict[str, Any]:
        return asdict(obj)
    
    @staticmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        from dataclasses import MISSING
        
        if not hasattr(cls, '__dataclass_fields__'):
            raise ValueError(f"{cls} must be a dataclass")
        
        field_info = {}
        for field in fields(cls):
            field_info[field.name] = field
        
        kwargs = {}
        for field_name, field in field_info.items():
            # 首先尝试使用新字段名
            if field_name in data:
                kwargs[field_name] = data[field_name]
            else:
                # 尝试从别名中查找（向后兼容）
                found_in_alias = False
                aliases = field.metadata.get('aliases', [])
                for alias in aliases:
                    if alias in data:
                        kwargs[field_name] = data[alias]
                        found_in_alias = True
                        break
                
                # 如果在别名中也没找到，使用默认值
                if not found_in_alias:
                    if field.default_factory is not MISSING:
                        kwargs[field_name] = field.default_factory()
                    elif field.default is not MISSING:
                        kwargs[field_name] = field.default
                    else:
                        kwargs[field_name] = None
        
        return cls(**kwargs)

def auto_to_dict(obj: Any) -> Dict[str, Any]:
    return DataclassSerializer.to_dict(obj)

def auto_from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
    return DataclassSerializer.from_dict(cls, data)

class AutoSerializableMixin:
    """可序列化的 Mixin 类，提供 to_dict/from_dict 和模板渲染功能"""
    
    def to_dict(self) -> Dict[str, Any]:
        return auto_to_dict(self)
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        return auto_from_dict(cls, data)
    
    def _render_template_fields(self):
        """渲染所有标记了 render_template=True 的字段
        
        此方法会遍历 dataclass 的所有字段，对标记了 render_template=True 的字段
        进行模板变量渲染（如 {{account_id}}、{{timestamp}} 等）。
        
        在渲染前，会将原始模板值保存到 _template_originals 字典中，
        以便在持久化时能够恢复原始模板值。
        
        使用方法：
            在子类的 __post_init__ 中调用：
            
            def __post_init__(self):
                self._render_template_fields()
        """
        # 只在 dataclass 中使用
        if not hasattr(self, '__dataclass_fields__'):
            return
        
        try:
            from agentkit.utils.template_utils import render_template
            from agentkit.toolkit.config import AUTO_CREATE_VE
            import logging
            
            logger = logging.getLogger(__name__)
            
            # 初始化原始值存储
            if not hasattr(self, '_template_originals'):
                self._template_originals = {}
            
            for field_info in fields(self):
                # 检查字段是否标记了需要渲染
                if field_info.metadata.get("render_template"):
                    field_value = getattr(self, field_info.name)
                    
                    # 只渲染非空且非自动创建的值
                    if field_value and field_value != AUTO_CREATE_VE:
                        # 保存原始模板值（仅当包含模板变量时）
                        if '{{' in str(field_value) and '}}' in str(field_value):
                            self._template_originals[field_info.name] = field_value
                            logger.debug(f"保存原始模板值 {field_info.name}: '{field_value}'")
                        
                        try:
                            rendered = render_template(field_value)
                            if rendered != field_value:
                                logger.debug(f"自动渲染配置字段 {field_info.name}: '{field_value}' -> '{rendered}'")
                                setattr(self, field_info.name, rendered)
                        except Exception as e:
                            logger.warning(f"渲染配置字段 {field_info.name} 失败，使用原始值: {e}")
        except ImportError:
            # 如果模板工具不可用，静默失败
            pass
    
    def to_persist_dict(self) -> Dict[str, Any]:
        """转换为用于持久化的字典，保留模板字段的原始值
        
        对于标记了 render_template=True 的字段：
        - 如果有保存的原始模板值（包含 {{}} 的值），使用原始值
        - 否则使用当前值（可能是用户直接设置的非模板值，或运行时生成的值）
        
        这样可以确保配置文件中的模板值（如 '{{timestamp}}' 或 'dev-{{timestamp}}'）
        在每次运行时都能被重新渲染，而不是固化为某次运行的具体值。
        
        Returns:
            用于持久化的字典
        """
        result = self.to_dict()
        
        # 如果有保存的原始模板值，恢复它们
        if hasattr(self, '_template_originals'):
            for field_name, original_value in self._template_originals.items():
                result[field_name] = original_value
        
        return result
