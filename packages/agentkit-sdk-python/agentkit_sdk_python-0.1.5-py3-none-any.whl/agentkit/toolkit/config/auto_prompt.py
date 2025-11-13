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

import inspect
import readline
from typing import Any, Dict, Optional, List, Union, get_type_hints, get_origin, get_args
from dataclasses import fields, is_dataclass, dataclass, MISSING
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.align import Align
from rich.layout import Layout
from rich import box

console = Console()

# 现代化的图标和样式配置
ICONS = {
    "agent": "🤖",
    "app": "📱",
    "file": "📄",
    "deploy": "🚀",
    "python": "🐍",
    "package": "📦",
    "port": "🔌",
    "config": "⚙️",
    "success": "✅",
    "error": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    "input": "🔤",
    "select": "🔘",
    "description": "✨",
    "list": "📝",
    "dict": "📋",
    "number": "🔢",
    "boolean": "🔲",
    "string": "🔤",
    "rocket": "🚀",
}

# 颜色配置
COLORS = {
    "primary": "#2196F3",      # 科技蓝
    "success": "#4CAF50",    # 活力绿
    "warning": "#FF9800",    # 橙色
    "error": "#F44336",      # 红色
    "border": "#37474F",     # 边框灰
    "muted": "#78909C",      # 柔和灰
    "label": "#64B5F6",      # 浅蓝
    "description": "#90A4AE" # 描述灰
}

# 样式配置
STYLES = {
    "title": "bold #2196F3",
    "subtitle": "bold #64B5F6",
    "success": "bold #4CAF50",
    "warning": "bold #FF9800",
    "error": "bold #F44336",
    "label": "bold #64B5F6",
    "value": "#4CAF50",
    "description": "#78909C",
    "muted": "#78909C"
}

class AutoPromptGenerator:
    def __init__(self):
        self.type_handlers = {
            str: self._handle_string,
            int: self._handle_int,
            float: self._handle_float,
            bool: self._handle_bool,
            list: self._handle_list,
            List: self._handle_list,
            dict: self._handle_dict,
            Dict: self._handle_dict,
        }

    def _safe_input(self, prompt_text, default: str = "") -> str:
        """安全的输入方法，保护提示文本不被Backspace删除

        Args:
            prompt_text: 提示文本(Rich Text对象或字符串)
            default: 默认值

        Returns:
            用户输入的字符串
        """
        # 将Rich Text转换为带ANSI转义码的字符串
        # 使用Console的内部方法将样式渲染为ANSI码
        from io import StringIO
        string_io = StringIO()
        # 使用全局console的is_terminal属性来判断是否应该启用终端特性
        # 这样可以根据实际终端环境自动适配，避免在不支持ANSI的终端中显示乱码
        temp_console = Console(file=string_io, force_terminal=console.is_terminal, width=200)
        temp_console.print(prompt_text, end="")
        rendered_prompt = string_io.getvalue()

        # 如果有默认值，尝试使用readline的pre_input_hook预填充
        # 增加兼容性处理，因为某些系统(如macOS的libedit)可能不支持这些功能
        if default:
            def prefill():
                try:
                    readline.insert_text(default)
                    readline.redisplay()
                except (AttributeError, OSError):
                    # 某些readline实现(如libedit)可能不支持insert_text或redisplay
                    # 在这种情况下，我们将在prompt中显示默认值作为fallback
                    pass
            try:
                readline.set_pre_input_hook(prefill)
            except (AttributeError, OSError):
                # 如果set_pre_input_hook不可用，在prompt中显示默认值
                if console.is_terminal:
                    rendered_prompt += f" \033[2m[默认: {default}]\033[0m"
                else:
                    rendered_prompt += f" [默认: {default}]"

        try:
            # 使用input()的prompt参数，Python会自动保护这个prompt不被Backspace删除
            # prompt中包含了ANSI转义码，所以会显示Rich样式
            user_input = input(rendered_prompt)

            # 如果用户没有输入任何内容且有默认值，返回默认值
            if not user_input and default:
                return default

            return user_input
        finally:
            # 清理hook，使用try-except防止某些系统不支持
            try:
                readline.set_pre_input_hook()
            except (AttributeError, OSError):
                pass

    def generate_config(self, dataclass_type: type, existing_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not is_dataclass(dataclass_type):
            raise ValueError(f"{dataclass_type} must be a dataclass")

        config = {}
        existing_config = existing_config or {}

        # 获取数据类的元数据
        # 尝试从类属性获取，如果不存在则创建实例来获取字段值
        config_metadata = {}
        if hasattr(dataclass_type, '_config_metadata'):
            # 如果是类属性
            config_metadata = getattr(dataclass_type, '_config_metadata', {})
        else:
            # 如果是字段，需要创建实例来获取默认值
            try:
                # 获取字段的默认值工厂函数或默认值
                for field in fields(dataclass_type):
                    if field.name == '_config_metadata':
                        if field.default_factory is not None and field.default_factory != MISSING:
                            config_metadata = field.default_factory()
                        elif field.default != MISSING:
                            config_metadata = field.default
                        break
            except Exception:
                pass

        config_name = config_metadata.get('name', dataclass_type.__name__)

        # 获取自定义消息
        welcome_message = config_metadata.get('welcome_message')
        next_step_hint = config_metadata.get('next_step_hint')
        completion_message = config_metadata.get('completion_message')
        next_action_hint = config_metadata.get('next_action_hint')

        # 显示现代化的欢迎界面
        self._show_welcome_panel(config_name, welcome_message, next_step_hint)

        # 获取字段列表并显示进度
        visible_fields = [f for f in fields(dataclass_type)
                         if not f.metadata.get("hidden", False) and not f.metadata.get("system", False) and f.name != "_config_metadata"]
        total_fields = len(visible_fields)

        for idx, field in enumerate(visible_fields, 1):
            field_name = field.name
            field_type = get_type_hints(dataclass_type).get(field_name, str)
            existing_value = existing_config.get(field_name)
            default_value = existing_value if existing_value is not None else field.default
            description = field.metadata.get("description") or field.name.replace("_", " ").title()

            # 传递进度信息到字段处理
            value = self._prompt_for_field(field_name, field_type, description, default_value, field.metadata, idx, total_fields)

            if value is not None:
                config[field_name] = value

        # 显示完成界面
        self._show_completion_panel(config, completion_message, next_action_hint)

        # 处理隐藏和系统字段
        for field in fields(dataclass_type):
            field_name = field.name
            if field.metadata.get("hidden", False) or field.metadata.get("system", False):
                if field_name in existing_config:
                    config[field_name] = existing_config[field_name]

        # 过滤掉MISSING值
        filtered_config = {}
        for key, value in config.items():
            if not isinstance(value, type(MISSING)):
                filtered_config[key] = value

        return filtered_config

    def _prompt_for_field(self, name: str, field_type: type, description: str, default: Any, metadata: Dict[str, Any] = None, current: int = 1, total: int = 1) -> Any:
        metadata = metadata or {}

        if get_origin(field_type) is not None:
            if get_origin(field_type) is Union:
                args = get_args(field_type)
                if len(args) == 2 and type(None) in args:
                    field_type = args[0]

        if get_origin(field_type) is list or field_type is List:
            return self._handle_list(description, default, metadata, current, total)

        if get_origin(field_type) is dict or field_type is Dict:
            return self._handle_dict(description, default, metadata, current, total)

        if default is MISSING or isinstance(default, type(MISSING)):
            default = None

        choices = metadata.get("choices")
        if choices:
            return self._handle_choice_selection(description, default, choices, metadata, current, total)

        handler = self.type_handlers.get(field_type)
        if handler:
            return handler(description, default, metadata, current, total)

        return self._handle_string(description, default, metadata, current, total)

    def _handle_choice_selection(self, description: str, default: Any, choices: List[Any], field_metadata: Dict[str, Any] = None, current: int = 1, total: int = 1) -> str:
        # 处理不同类型的选择数据
        if isinstance(choices, list) and len(choices) > 0 and isinstance(choices[0], dict):
            # 处理字典格式的选择项
            if not default or (default and default not in [choice['value'] for choice in choices]):
                default = choices[0]['value'] if choices else None
        else:
            # 处理简单列表格式的选择项
            if not default or (default and default not in choices):
                default = choices[0] if choices else None

        # 获取字段图标(支持metadata指定)
        icon = self._get_field_icon(description, field_metadata) if field_metadata else ICONS['select']

        # 创建选择面板标题，集成进度信息
        console.print(f"\n[{current}/{total}] {icon} {description}")

        # 处理选择项数据
        choice_descriptions = {}
        if isinstance(choices, dict):
            choice_descriptions = choices
            choices = list(choices.keys())
        elif isinstance(choices, list) and len(choices) > 0 and isinstance(choices[0], dict):
            choice_descriptions = {item["value"]: item.get("description", "") for item in choices}
            choices = [item["value"] for item in choices]

        # 创建现代化的选择菜单
        table = Table(show_header=False, box=box.ROUNDED, padding=(0, 1))

        for i, choice in enumerate(choices, 1):
            desc = choice_descriptions.get(choice, "")

            # 标记默认选项
            is_default = choice == default
            default_marker = f" (当前)" if is_default else ""

            # 格式化选择项
            choice_text = Text()
            choice_text.append(f"{i}. ")
            choice_text.append(f"{choice}")
            if desc:
                choice_text.append(f" - {desc}")
            choice_text.append(default_marker)

            table.add_row(choice_text)

        # 显示选择表格
        console.print(table)
        console.print()

        while True:
            # 创建输入提示
            prompt_str = "请选择 (输入编号或名称): "

            # 使用input()的prompt参数
            try:
                user_input = input(prompt_str)
            except KeyboardInterrupt:
                raise
            except EOFError:
                console.print(f"\n{ICONS['warning']} 选择已取消，使用默认值")
                return str(default) if default else str(choices[0]) if choices else ""

            if user_input.isdigit():
                choice_num = int(user_input)
                if 1 <= choice_num <= len(choices):
                    selected = choices[choice_num - 1]
                    # 显示选择确认
                    console.print(f"\n{ICONS['success']} 已选择: {selected}\n")
                    return selected
                else:
                    console.print(f"{ICONS['error']} 请输入 1-{len(choices)} 之间的数字")
                    continue

            if user_input in choices:
                # 显示选择确认
                console.print(f"\n{ICONS['success']} 已选择: {user_input}\n")
                return user_input
            else:
                valid_choices = ", ".join(choices)
                console.print(f"{ICONS['error']} 无效选择，请选择: {valid_choices}")

    def _handle_string(self, description: str, default: Any, field_metadata: Dict[str, Any] = None, current: int = 1, total: int = 1) -> str:
        # 获取字段图标(支持metadata指定)
        icon = self._get_field_icon(description, field_metadata) if field_metadata else ICONS['input']

        # 获取验证规则
        validation_rules = field_metadata.get('validation', {}) if field_metadata else {}

        while True:
            # 构建完整的提示信息
            if default:
                prompt_str = f"\n[{current}/{total}] {icon} {description}(当前值：{default}{'' if not ('{{' in default and '}}' in default) else ', 花括号内容为动态渲染的占位符，无需手动填写'}): "
            else:
                prompt_str = f"\n[{current}/{total}] {icon} {description}: "

            # 使用input()的prompt参数，Python会保护这个prompt不被Backspace删除
            try:
                result = input(prompt_str)
            except KeyboardInterrupt:
                raise
            except EOFError:
                result = ""

            # 如果没有输入且有默认值，使用默认值
            if not result and default:
                result = str(default)

            # 应用验证规则
            if validation_rules:
                # 检查必填
                if validation_rules.get('required') and (not result or result.strip() == ''):
                    console.print(f"{ICONS['error']} 此字段不能为空")
                    continue

                # 检查正则表达式模式
                pattern = validation_rules.get('pattern')
                if pattern and result:
                    import re
                    if not re.match(pattern, result):
                        error_msg = validation_rules.get('message', '输入格式不符合要求')
                        console.print(f"{ICONS['error']} {error_msg}")
                        continue

            console.print(f"{ICONS['success']} 已输入: {result}\n")
            return result

    def _handle_int(self, description: str, default: Any, field_metadata: Dict[str, Any] = None, current: int = 1, total: int = 1) -> int:
        while True:
            try:
                # 获取字段图标(支持metadata指定)
                icon = self._get_field_icon(description, field_metadata) if field_metadata else ICONS['input']

                # 构建完整的提示信息
                if default is not None:
                    prompt_str = f"\n[{current}/{total}] {icon} {description}(当前值：{default})(数字): "
                else:
                    prompt_str = f"\n[{current}/{total}] {icon} {description}(数字): "

                # 使用input()的prompt参数
                try:
                    value = input(prompt_str)
                except KeyboardInterrupt:
                    raise
                except EOFError:
                    value = ""

                # 如果没有输入且有默认值，使用默认值
                if not value and default is not None:
                    value = str(default)
                elif not value:
                    value = "0"

                result = int(value)
                console.print(f"{ICONS['success']} 已输入: {result}\n")
                return result
            except ValueError:
                console.print(f"{ICONS['error']} 请输入有效的整数")
            except KeyboardInterrupt:
                raise

    def _handle_float(self, description: str, default: Any, field_metadata: Dict[str, Any] = None, current: int = 1, total: int = 1) -> float:
        while True:
            try:
                # 获取字段图标(支持metadata指定)
                icon = self._get_field_icon(description, field_metadata) if field_metadata else ICONS['input']

                # 构建完整的提示信息
                if default is not None:
                    prompt_str = f"\n[{current}/{total}] {icon} {description}(当前值：{default})(数字): "
                else:
                    prompt_str = f"\n[{current}/{total}] {icon} {description}(数字): "

                # 使用input()的prompt参数
                try:
                    value = input(prompt_str)
                except KeyboardInterrupt:
                    raise
                except EOFError:
                    value = ""

                # 如果没有输入且有默认值，使用默认值
                if not value and default is not None:
                    value = str(default)
                elif not value:
                    value = "0.0"

                result = float(value)
                console.print(f"{ICONS['success']} 已输入: {result}\n")
                return result
            except ValueError:
                console.print(f"{ICONS['error']} 请输入有效的数字")
            except KeyboardInterrupt:
                raise

    def _handle_bool(self, description: str, default: Any, field_metadata: Dict[str, Any] = None, current: int = 1, total: int = 1) -> bool:
        # 获取字段图标(支持metadata指定)
        icon = self._get_field_icon(description, field_metadata) if field_metadata else ICONS['select']

        # 使用console.print显示进度信息
        console.print(f"\n[{current}/{total}] {icon} {description}")

        result = Confirm.ask("", default=bool(default))
        result_text = "是" if result else "否"
        console.print(f"{ICONS['success']} 已选择: {result_text}\n")
        return result

    def _handle_list(self, description: str, default: Any, field_metadata: Dict[str, Any] = None, current: int = 1, total: int = 1) -> List[str]:
        # 获取字段图标(支持metadata指定)
        icon = self._get_field_icon(description, field_metadata) if field_metadata else ICONS['list']

        # 使用console.print显示进度信息
        console.print(f"\n[{current}/{total}] {icon} {description}")
        console.print("输入每个项目后按回车，输入空行结束\n")

        items = []
        counter = 1

        while True:
            # 创建列表项输入提示
            prompt_str = f"  [{current}/{total}] [{counter}] 项目: "
            
            try:
                item = input(prompt_str)
            except KeyboardInterrupt:
                raise
            except EOFError:
                item = ""
            if not item.strip():
                break
            items.append(item.strip())
            console.print(f"  {ICONS['success']} 已添加: {item.strip()}")
            counter += 1

        if items:
            console.print(f"\n{ICONS['list']} 共添加 {len(items)} 个项目\n")
        else:
            console.print(f"\n{ICONS['info']} 未添加任何项目\n")

        return items if items else (default if default is not None else [])

    def _handle_dict(self, description: str, default: Any, field_metadata: Dict[str, Any] = None, current: int = 1, total: int = 1) -> Dict[str, str]:
        # 获取字段图标(支持metadata指定)
        icon = self._get_field_icon(description, field_metadata) if field_metadata else ICONS['dict']

        # 使用console.print显示进度信息
        console.print(f"\n[{current}/{total}] {icon} {description}")

        # 添加环境变量提示(如果描述中包含env)
        if "env" in description.lower():
            console.print("常用环境变量:")
            console.print("  - MODEL_AGENT_API_KEY=your_api_key")
            console.print("  - DEBUG=true")
            console.print("  - LOG_LEVEL=info")

        console.print("输入格式: KEY=VALUE")
        console.print("命令: 'del KEY' 删除, 'list' 查看, 'clear' 清空所有, 空行结束\n")

        result_dict = {}
        if isinstance(default, dict):
            result_dict.update(default)

        while True:
            # 创建字典输入提示
            prompt_str = f"\n[{current}/{total}] {icon} 变量: "
            
            try:
                user_input = input(prompt_str)
            except KeyboardInterrupt:
                raise
            except EOFError:
                user_input = ""

            if not user_input.strip():
                break

            if user_input == "list":
                if result_dict:
                    console.print("\n当前变量:")
                    for key, value in result_dict.items():
                        console.print(f"  {key}={value}")
                else:
                    console.print("未设置变量")
                continue

            if user_input == "clear":
                result_dict.clear()
                console.print("所有变量已清空")
                continue

            if user_input.startswith("del "):
                key_to_delete = user_input[4:].strip()
                if key_to_delete in result_dict:
                    del result_dict[key_to_delete]
                    console.print(f"已删除: {key_to_delete}")
                else:
                    console.print(f"变量未找到: {key_to_delete}")
                continue

            if "=" not in user_input:
                console.print("无效格式, 请使用 KEY=VALUE")
                continue

            key, value = user_input.split("=", 1)
            key = key.strip()
            value = value.strip()
            
            # Strip surrounding quotes (both single and double quotes)
            if len(value) >= 2:
                if (value[0] == '"' and value[-1] == '"') or (value[0] == "'" and value[-1] == "'"):
                    value = value[1:-1]

            if not key:
                console.print("键名不能为空")
                continue

            if not key.replace("_", "").isalnum():
                console.print("键名只能包含字母、数字和下划线")
                continue

            old_value = result_dict.get(key)
            result_dict[key] = value

            if old_value is not None:
                console.print(f"已更新: {key}={value} (原值: {old_value})")
            else:
                console.print(f"已添加: {key}={value}")

        if result_dict:
            console.print(f"\n{ICONS['dict']} 共配置 {len(result_dict)} 个变量\n")
        else:
            console.print(f"\n{ICONS['info']} 未配置任何变量\n")

        return result_dict if result_dict else (default if default is not None else {})

    def _show_welcome_panel(self, config_name: str, welcome_message: Optional[str] = None,
                           next_step_hint: Optional[str] = None):
        """显示欢迎面板"""
        # 创建标题文本
        title_text = Text(f"{ICONS['config']} {config_name}", style=STYLES["title"])

        # 创建内容
        content = Text()
        content.append(f"{ICONS['info']} ", style=STYLES["label"])

        # 使用自定义欢迎信息或默认信息
        if welcome_message:
            content.append(f"{welcome_message}", style="bold white")
        else:
            content.append("欢迎使用 AgentKit 配置向导\n\n", style="bold white")
            content.append("本向导将帮助您完成应用配置，请根据提示输入相关信息。\n", style=COLORS["description"])

        # 添加下一步提示
        if next_step_hint:
            content.append(f"\n{next_step_hint}\n", style=f"dim {COLORS['description']}")

        content.append("\n您可以随时按 Ctrl+C 退出配置。\n", style="dim")

        # 创建面板
        panel = Panel(
            content,
            title=title_text,
            border_style=COLORS["muted"],
            box=box.DOUBLE,
            padding=(1, 2),
            expand=False
        )

        console.print(panel)
        console.print()

    def _show_progress(self, current: int, total: int, field_name: str, description: str):
        """显示进度指示器"""
        # 获取字段图标(支持metadata指定)
        icon = self._get_field_icon(field_name)

        # 创建进度条
        progress_width = 30
        filled_width = int((current / total) * progress_width)
        progress_bar = f"[{'█' * filled_width}{'░' * (progress_width - filled_width)}]"

        # 创建进度信息
        progress_text = Text()
        progress_text.append(f"{icon} ", style=STYLES["label"])
        progress_text.append(f"{description}", style="bold white")
        progress_text.append(f"  [{current}/{total}]\n", style=STYLES["description"])
        progress_text.append(f"    {progress_bar} {current/total*100:.0f}%", style=COLORS["label"])

        console.print(progress_text)
        console.print()

    def _show_progress_clean(self, current: int, total: int, field_name: str, description: str):
        """显示清理的进度指示器(不重复显示进度条)"""
        # 获取字段图标(支持metadata指定)
        icon = self._get_field_icon(field_name)

        # 只在第一个字段或字段变更时显示进度条
        if current == 1 or current != getattr(self, '_last_progress', 0):
            # 创建进度条
            progress_width = 30
            filled_width = int((current / total) * progress_width)
            progress_bar = f"[{'█' * filled_width}{'░' * (progress_width - filled_width)}]"

            # 创建进度信息
            progress_text = Text()
            progress_text.append(f"{icon} ", style=STYLES["label"])
            progress_text.append(f"{description}", style="bold white")
            progress_text.append(f"  [{current}/{total}]\n", style=STYLES["description"])
            progress_text.append(f"    {progress_bar} {current/total*100:.0f}%", style=COLORS["label"])

            console.print(progress_text)
            console.print()

            # 记录当前进度
            self._last_progress = current

    def _get_field_icon(self, field_name: str, field_metadata: Dict[str, Any] = None) -> str:
        """根据字段metadata或字段名获取对应的图标"""
        # 优先使用metadata中指定的图标
        if field_metadata and "icon" in field_metadata:
            return field_metadata["icon"]

        # 回退到硬编码映射(保持向后兼容)
        icon_map = {
            "agent_name": ICONS["agent"],
            "entry_point": ICONS["file"],
            "launch_type": ICONS["deploy"],
            "description": ICONS["description"],
            "python_version": ICONS["python"],
            "dependencies_file": ICONS["package"],
            "entry_port": ICONS["port"],
        }
        return icon_map.get(field_name, ICONS["config"])

    def _show_completion_panel(self, config: Dict[str, Any], completion_message: Optional[str] = None,
                             next_action_hint: Optional[str] = None):
        """显示配置完成界面"""
        # 创建标题文本
        title_text = Text(f"{ICONS['success']} 配置完成", style=STYLES["success"])

        # 创建配置总结表格
        table = Table(show_header=True, header_style=f"bold {COLORS['primary']}",
                     border_style=COLORS["muted"], box=box.ROUNDED,
                     padding=(0, 2))
        table.add_column("配置项", style=STYLES["label"], width=28)
        table.add_column("值", style=STYLES["value"], width=50)

        # 添加配置项到表格
        for key, value in config.items():
            if not key.startswith('_'):  # 跳过内部字段
                formatted_key = self._format_field_name(key)
                if isinstance(value, type(MISSING)):
                    formatted_value = "未设置"
                elif value is None:
                    formatted_value = "未设置"
                else:
                    formatted_value = str(value)
                table.add_row(formatted_key, formatted_value)

        # 创建完成面板
        completion_panel = Panel(
            Align.center(table),
            title=title_text,
            border_style=COLORS["success"],
            box=box.ROUNDED,
            padding=(1, 2)
        )

        console.print("\n")
        console.print(completion_panel)

        # 显示自定义完成消息或默认消息
        if completion_message:
            console.print(f"\n{ICONS['success']} {completion_message}\n")
        else:
            console.print(f"\n{ICONS['rocket']} 配置已保存，现在可以使用 agentkit build 构建应用了！\n")

        # 显示下一步操作提示
        if next_action_hint:
            console.print(f"{ICONS['info']} {next_action_hint}\n", style=COLORS["description"])

    def _format_field_name(self, field_name: str) -> str:
        """格式化字段名称"""
        name_map = {
            "agent_name": "应用名称",
            "entry_point": "入口文件",
            "launch_type": "部署模式",
            "description": "应用描述",
            "python_version": "Python版本",
            "dependencies_file": "依赖文件",
            "entry_port": "端口",
            "ve_cr_instance_name": "Cr Instance Name",
            "ve_cr_namespace_name": "Cr Namespace",
            "ve_cr_repo_name": "Cr Repo",
        }
        return name_map.get(field_name, field_name.replace("_", " ").title())

auto_prompt = AutoPromptGenerator()

def generate_config_from_dataclass(dataclass_type: type, existing_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return auto_prompt.generate_config(dataclass_type, existing_config)