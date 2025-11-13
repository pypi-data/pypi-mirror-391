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

"""统一的日志配置模块

提供标准化的日志配置接口，支持：
- 多种日志级别控制
- 多种日志格式（simple, detailed, json）
- 多种输出目标（console, file）
- 环境变量配置
- 上下文追踪支持
"""

import logging
import os
import sys
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path
import contextvars

# 上下文变量用于请求追踪
request_id_var = contextvars.ContextVar('request_id', default=None)
session_id_var = contextvars.ContextVar('session_id', default=None)
user_id_var = contextvars.ContextVar('user_id', default=None)

# 日志格式常量
LOG_FORMAT_SIMPLE = "simple"
LOG_FORMAT_DETAILED = "detailed"
LOG_FORMAT_JSON = "json"

# 默认配置
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FORMAT = LOG_FORMAT_SIMPLE
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 环境变量名称
ENV_LOG_LEVEL = "AGENTKIT_LOG_LEVEL"
ENV_LOG_FORMAT = "AGENTKIT_LOG_FORMAT"
ENV_LOG_FILE = "AGENTKIT_LOG_FILE"
ENV_LOG_CONSOLE = "AGENTKIT_LOG_CONSOLE"
ENV_LOG_JSON_INDENT = "AGENTKIT_LOG_JSON_INDENT"


class ContextFilter(logging.Filter):
    """为日志记录添加上下文信息的过滤器"""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """向日志记录添加上下文变量"""
        record.request_id = request_id_var.get()
        record.session_id = session_id_var.get()
        record.user_id = user_id_var.get()
        return True


class JSONFormatter(logging.Formatter):
    """JSON格式的日志格式化器"""
    
    def __init__(self, indent: Optional[int] = None):
        super().__init__()
        self.indent = indent
    
    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录为JSON字符串"""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # 添加上下文信息（如果存在）
        if hasattr(record, 'request_id') and record.request_id:
            log_data["request_id"] = record.request_id
        if hasattr(record, 'session_id') and record.session_id:
            log_data["session_id"] = record.session_id
        if hasattr(record, 'user_id') and record.user_id:
            log_data["user_id"] = record.user_id
        
        # 添加额外的字段
        if hasattr(record, 'extra') and record.extra:
            log_data.update(record.extra)
        
        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False, indent=self.indent)


def get_log_level_from_env() -> str:
    """从环境变量获取日志级别"""
    return os.getenv(ENV_LOG_LEVEL, DEFAULT_LOG_LEVEL).upper()


def get_log_format_from_env() -> str:
    """从环境变量获取日志格式"""
    return os.getenv(ENV_LOG_FORMAT, DEFAULT_LOG_FORMAT).lower()


def get_log_file_from_env() -> Optional[str]:
    """从环境变量获取日志文件路径"""
    return os.getenv(ENV_LOG_FILE)


def get_console_enabled_from_env() -> bool:
    """从环境变量获取是否启用控制台输出"""
    console_enabled = os.getenv(ENV_LOG_CONSOLE, "true").lower()
    return console_enabled in ("true", "1", "yes", "on")


def create_formatter(format_type: str = DEFAULT_LOG_FORMAT) -> logging.Formatter:
    """创建日志格式化器
    
    Args:
        format_type: 日志格式类型（simple, detailed, json）
    
    Returns:
        日志格式化器实例
    """
    if format_type == LOG_FORMAT_JSON:
        indent = None
        if os.getenv(ENV_LOG_JSON_INDENT):
            try:
                indent = int(os.getenv(ENV_LOG_JSON_INDENT))
            except ValueError:
                pass
        return JSONFormatter(indent=indent)
    
    elif format_type == LOG_FORMAT_DETAILED:
        fmt = (
            "[%(asctime)s] [%(levelname)s] [%(name)s:%(funcName)s:%(lineno)d] "
            "%(message)s"
        )
        if request_id_var.get():
            fmt = f"[%(request_id)s] {fmt}"
        return logging.Formatter(fmt, datefmt=DEFAULT_DATE_FORMAT)
    
    else:  # simple format
        fmt = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
        return logging.Formatter(fmt, datefmt=DEFAULT_DATE_FORMAT)


def setup_logging(
    level: Optional[str] = None,
    format_type: Optional[str] = None,
    log_file: Optional[str] = None,
    console_enabled: Optional[bool] = None,
    force: bool = False
) -> None:
    """配置全局日志系统
    
    Args:
        level: 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
        format_type: 日志格式（simple, detailed, json）
        log_file: 日志文件路径（可选）
        console_enabled: 是否启用控制台输出
        force: 是否强制重新配置（即使已配置过）
    
    Example:
        >>> from agentkit.utils.logging_config import setup_logging
        >>> setup_logging(level="INFO", format_type="detailed")
        >>> logger = logging.getLogger(__name__)
        >>> logger.info("Application started")
    """
    # 获取配置（优先使用参数，其次使用环境变量）
    log_level = (level or get_log_level_from_env()).upper()
    log_format = (format_type or get_log_format_from_env()).lower()
    log_file_path = log_file or get_log_file_from_env()
    console_out = console_enabled if console_enabled is not None else get_console_enabled_from_env()
    
    # 验证日志级别
    numeric_level = getattr(logging, log_level, None)
    if not isinstance(numeric_level, int):
        print(f"Warning: Invalid log level '{log_level}', using INFO", file=sys.stderr)
        numeric_level = logging.INFO
    
    # 获取根日志记录器
    root_logger = logging.getLogger()
    
    # 如果已经配置过，且不强制重新配置，则跳过
    if root_logger.handlers and not force:
        return
    
    # 清除现有的处理器
    if force:
        root_logger.handlers.clear()
    
    # 设置日志级别
    root_logger.setLevel(numeric_level)
    
    # 创建格式化器
    formatter = create_formatter(log_format)
    
    # 创建上下文过滤器
    context_filter = ContextFilter()
    
    # 配置控制台处理器
    if console_out:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        console_handler.addFilter(context_filter)
        root_logger.addHandler(console_handler)
    
    # 配置文件处理器
    if log_file_path:
        try:
            # 确保日志目录存在
            log_dir = Path(log_file_path).parent
            log_dir.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
            file_handler.setLevel(numeric_level)
            file_handler.setFormatter(formatter)
            file_handler.addFilter(context_filter)
            root_logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Failed to create log file handler: {e}", file=sys.stderr)


def get_logger(name: str) -> logging.Logger:
    """获取标准化的日志记录器
    
    Args:
        name: 日志记录器名称（通常使用 __name__）
    
    Returns:
        配置好的日志记录器实例
    
    Example:
        >>> from agentkit.utils.logging_config import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing request")
    """
    # 确保名称以 agentkit 开头，便于统一管理
    if not name.startswith("agentkit"):
        name = f"agentkit.{name}"
    
    return logging.getLogger(name)


def set_context(
    request_id: Optional[str] = None,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None
) -> None:
    """设置日志上下文信息
    
    Args:
        request_id: 请求ID
        session_id: 会话ID
        user_id: 用户ID
    
    Example:
        >>> from agentkit.utils.logging_config import set_context
        >>> set_context(request_id="req-123", user_id="user-456")
    """
    if request_id is not None:
        request_id_var.set(request_id)
    if session_id is not None:
        session_id_var.set(session_id)
    if user_id is not None:
        user_id_var.set(user_id)


def clear_context() -> None:
    """清除日志上下文信息
    
    Example:
        >>> from agentkit.utils.logging_config import clear_context
        >>> clear_context()
    """
    request_id_var.set(None)
    session_id_var.set(None)
    user_id_var.set(None)


def get_context() -> Dict[str, Optional[str]]:
    """获取当前日志上下文信息
    
    Returns:
        包含上下文信息的字典
    
    Example:
        >>> from agentkit.utils.logging_config import get_context
        >>> context = get_context()
        >>> print(context)
    """
    return {
        "request_id": request_id_var.get(),
        "session_id": session_id_var.get(),
        "user_id": user_id_var.get(),
    }


# 便捷函数：配置特定场景的日志
def setup_sdk_logging(level: str = "INFO") -> None:
    """为SDK库配置日志（适用于被集成使用的场景）
    
    Args:
        level: 日志级别
    """
    setup_logging(
        level=level,
        format_type=LOG_FORMAT_SIMPLE,
        console_enabled=False  # SDK默认不输出到控制台
    )


def setup_cli_logging(verbose: bool = False, quiet: bool = False) -> None:
    """为CLI工具配置日志
    
    Args:
        verbose: 是否启用详细输出
        quiet: 是否静默模式
    """
    if quiet:
        level = "ERROR"
    elif verbose:
        level = "DEBUG"
    else:
        level = "INFO"
    
    setup_logging(
        level=level,
        format_type=LOG_FORMAT_SIMPLE,
        console_enabled=True
    )


def setup_server_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    json_format: bool = False
) -> None:
    """为服务器应用配置日志
    
    Args:
        level: 日志级别
        log_file: 日志文件路径
        json_format: 是否使用JSON格式
    """
    format_type = LOG_FORMAT_JSON if json_format else LOG_FORMAT_DETAILED
    
    setup_logging(
        level=level,
        format_type=format_type,
        log_file=log_file,
        console_enabled=True
    )
