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

"""模板字符串渲染工具

提供统一的模板变量渲染功能，支持以下变量：
- {{account_id}}: 火山引擎账号ID
- {{timestamp}}: 当前时间戳（格式：YYYYMMDDHHMMSS）
- {{date}}: 当前日期（格式：YYYYMMDD）
- {{random_id}}: 随机ID（8位十六进制）

使用示例：
    >>> from agentkit.utils.template_utils import render_template
    >>> result = render_template("agentkit-cli-{{account_id}}")
    >>> # 返回: "agentkit-cli-2107625663"
"""

import re
import logging
from datetime import datetime
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

# 全局缓存，用于存储已获取的账号信息
_ACCOUNT_CACHE: Dict[str, Any] = {}


def render_template(template_str: str, extra_vars: Optional[Dict[str, str]] = None) -> str:
    """渲染模板字符串
    
    Args:
        template_str: 模板字符串，如 "agentkit-cli-{{account_id}}"
        extra_vars: 额外的变量字典，用于自定义变量替换
        
    Returns:
        渲染后的字符串
        
    Raises:
        ValueError: 当获取账号信息失败时
        
    Examples:
        >>> render_template("bucket-{{account_id}}")
        "bucket-2107625663"
        
        >>> render_template("app-{{date}}-{{random_id}}")
        "app-20250127-a1b2c3d4"
        
        >>> render_template("custom-{{name}}", extra_vars={"name": "test"})
        "custom-test"
    """
    # 如果不包含模板变量，直接返回
    if not template_str or '{{' not in template_str:
        return template_str
    
    # 构建内置变量字典
    builtin_vars = _get_builtin_variables()
    
    # 合并额外变量
    variables = {**builtin_vars, **(extra_vars or {})}
    
    # 使用正则表达式渲染所有模板变量
    def replace_var(match):
        var_name = match.group(1).strip()
        if var_name in variables:
            return str(variables[var_name])
        else:
            logger.warning(f"未知的模板变量: {{{{{var_name}}}}}")
            return match.group(0)  # 保持原样
    
    rendered = re.sub(r'\{\{([^}]+)\}\}', replace_var, template_str)
    
    logger.debug(f"模板渲染: '{template_str}' -> '{rendered}'")
    return rendered


def _get_builtin_variables() -> Dict[str, str]:
    """获取内置模板变量
    
    Returns:
        包含所有内置变量的字典
    """
    import uuid
    
    now = datetime.now()
    
    variables = {
        'timestamp': now.strftime('%Y%m%d%H%M%S'),
        'date': now.strftime('%Y%m%d'),
        'random_id': uuid.uuid4().hex[:8],
    }
    
    # 延迟获取 account_id（仅在需要时才调用）
    # 这里不直接调用，而是在需要时才获取
    return variables


def get_account_id() -> str:
    """获取火山引擎账号ID（带缓存）
    
    Returns:
        账号ID字符串
        
    Raises:
        ValueError: 当无法获取账号信息时
        
    Note:
        此函数会缓存账号ID，避免重复调用 IAM API
    """
    # 检查缓存
    if 'account_id' in _ACCOUNT_CACHE:
        logger.debug(f"从缓存获取 account_id: {_ACCOUNT_CACHE['account_id']}")
        return _ACCOUNT_CACHE['account_id']
    
    try:
        # 调用 IAM API 获取用户信息
        from agentkit.toolkit.integrations.ve_iam import VeIAM
        
        logger.debug("正在通过 IAM API 获取账号信息...")
        iam = VeIAM()
        user_response = iam.get_user_by_access_key_id()
        
        # 从响应中提取 account_id
        # 响应格式: {'user': {'account_id': 2107625663, ...}}
        if hasattr(user_response, 'user') and hasattr(user_response.user, 'account_id'):
            account_id = str(user_response.user.account_id)
        elif isinstance(user_response, dict) and 'user' in user_response:
            account_id = str(user_response['user']['account_id'])
        else:
            raise ValueError(f"无法从 IAM 响应中提取 account_id: {user_response}")
        
        # 缓存结果
        _ACCOUNT_CACHE['account_id'] = account_id
        logger.info(f"成功获取账号ID: {account_id}")
        
        return account_id
        
    except Exception as e:
        error_msg = f"获取账号ID失败: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg) from e


def clear_cache() -> None:
    """清除账号信息缓存
    
    用于测试或需要重新获取账号信息的场景
    """
    global _ACCOUNT_CACHE
    _ACCOUNT_CACHE.clear()
    logger.debug("账号信息缓存已清除")


def render_template_safe(template_str: str, 
                         fallback: Optional[str] = None,
                         extra_vars: Optional[Dict[str, str]] = None) -> str:
    """安全地渲染模板字符串，失败时返回fallback值
    
    Args:
        template_str: 模板字符串
        fallback: 当渲染失败时返回的值，默认为原始模板字符串
        extra_vars: 额外的变量字典
        
    Returns:
        渲染后的字符串，失败时返回fallback或原字符串
        
    Examples:
        >>> render_template_safe("bucket-{{account_id}}", fallback="bucket-default")
        # 成功时: "bucket-2107625663"
        # 失败时: "bucket-default"
    """
    try:
        return render_template(template_str, extra_vars)
    except Exception as e:
        logger.warning(f"模板渲染失败，使用fallback值: {e}")
        return fallback if fallback is not None else template_str


# 扩展：支持懒加载的变量获取
def _get_all_variables(extra_vars: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """获取所有可用的模板变量（包括需要懒加载的变量）
    
    Args:
        extra_vars: 额外的变量字典
        
    Returns:
        包含所有变量的字典
    """
    variables = _get_builtin_variables()
    
    # 如果模板中需要 account_id，才去获取
    variables['account_id'] = get_account_id()
    
    # 合并额外变量
    if extra_vars:
        variables.update(extra_vars)
    
    return variables


# 优化版本：只在需要时获取 account_id
def render_template(template_str: str, extra_vars: Optional[Dict[str, str]] = None) -> str:
    """渲染模板字符串（优化版）
    
    Args:
        template_str: 模板字符串，如 "agentkit-cli-{{account_id}}"
        extra_vars: 额外的变量字典，用于自定义变量替换
        
    Returns:
        渲染后的字符串
        
    Raises:
        ValueError: 当获取账号信息失败时
    """
    # 如果不包含模板变量，直接返回
    if not template_str or '{{' not in template_str:
        return template_str
    
    # 检查是否需要 account_id
    needs_account_id = '{{account_id}}' in template_str or '{{ account_id }}' in template_str
    
    # 构建变量字典
    variables = _get_builtin_variables()
    
    # 只在需要时获取 account_id
    if needs_account_id:
        variables['account_id'] = get_account_id()
    
    # 合并额外变量
    if extra_vars:
        variables.update(extra_vars)
    
    # 使用正则表达式渲染所有模板变量
    def replace_var(match):
        var_name = match.group(1).strip()
        if var_name in variables:
            return str(variables[var_name])
        else:
            logger.warning(f"未知的模板变量: {{{{{var_name}}}}}")
            return match.group(0)  # 保持原样
    
    rendered = re.sub(r'\{\{([^}]+)\}\}', replace_var, template_str)
    
    logger.debug(f"模板渲染: '{template_str}' -> '{rendered}'")
    return rendered
