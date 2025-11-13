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

"""Non-interactive configuration handler."""

from typing import Dict, List, Any, Optional
from dataclasses import fields
from rich.console import Console
from rich.table import Table
from rich import box

from agentkit.toolkit.config.config import CommonConfig, AgentkitConfigManager, get_config
from agentkit.toolkit.config.config_validator import ConfigValidator

console = Console()


class ConfigParamHandler:
    """处理配置参数的工具类"""
    
    @staticmethod
    def parse_runtime_envs(env_list: Optional[List[str]]) -> Dict[str, str]:
        """解析 KEY=VALUE 格式的环境变量
        
        Args:
            env_list: 环境变量列表，格式为 ["KEY1=VALUE1", "KEY2=VALUE2"]
            
        Returns:
            解析后的字典
        """
        if not env_list:
            return {}
            
        result = {}
        for env in env_list:
            if '=' not in env:
                console.print(f"[yellow]警告: 忽略无效的环境变量格式 '{env}' (应为 KEY=VALUE)[/yellow]")
                continue
            
            key, value = env.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            if not key:
                console.print(f"[yellow]警告: 忽略空键名的环境变量 '{env}'[/yellow]")
                continue
            
            result[key] = value
        
        return result
    
    @staticmethod
    def collect_cli_params(
        agent_name: Optional[str],
        entry_point: Optional[str],
        description: Optional[str],
        python_version: Optional[str],
        dependencies_file: Optional[str],
        launch_type: Optional[str],
        runtime_envs: Optional[List[str]],
        workflow_runtime_envs: Optional[List[str]],
        region: Optional[str],
        tos_bucket: Optional[str],
        image_tag: Optional[str],
        cr_instance_name: Optional[str],
        cr_namespace_name: Optional[str],
        cr_repo_name: Optional[str],
    ) -> Dict[str, Any]:
        """收集所有 CLI 参数
        
        Returns:
            {
                'common': {...},  # CommonConfig 参数（包括应用级 runtime_envs）
                'workflow': {...}  # Workflow 特定参数（包括 workflow 级 runtime_envs）
            }
        """
        common_params = {}
        workflow_params = {}
        
        # 收集 common 参数
        if agent_name is not None:
            common_params['agent_name'] = agent_name
        if entry_point is not None:
            common_params['entry_point'] = entry_point
        if description is not None:
            common_params['description'] = description
        if python_version is not None:
            common_params['python_version'] = python_version
        if dependencies_file is not None:
            common_params['dependencies_file'] = dependencies_file
        if launch_type is not None:
            common_params['launch_type'] = launch_type
        
        # 应用级环境变量（添加到 common）
        if runtime_envs is not None:
            common_params['runtime_envs'] = ConfigParamHandler.parse_runtime_envs(runtime_envs)
        
        # 收集 workflow 参数
        # Workflow 级环境变量
        if workflow_runtime_envs is not None:
            workflow_params['runtime_envs'] = ConfigParamHandler.parse_runtime_envs(workflow_runtime_envs)
        if region is not None:
            workflow_params['region'] = region
        if tos_bucket is not None:
            workflow_params['tos_bucket'] = tos_bucket
        if image_tag is not None:
            workflow_params['image_tag'] = image_tag
        if cr_instance_name is not None:
            workflow_params['cr_instance_name'] = cr_instance_name
        if cr_namespace_name is not None:
            workflow_params['cr_namespace_name'] = cr_namespace_name
        if cr_repo_name is not None:
            workflow_params['cr_repo_name'] = cr_repo_name
        
        return {
            'common': common_params,
            'workflow': workflow_params
        }
    
    @staticmethod
    def has_cli_params(params: Dict[str, Any]) -> bool:
        """检查是否有 CLI 参数"""
        return bool(params['common']) or bool(params['workflow'])


class NonInteractiveConfigHandler:
    """非交互式配置处理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_manager = get_config(config_path=config_path)
        self.validator = ConfigValidator()
    
    def update_config(
        self,
        common_params: Dict[str, Any],
        workflow_params: Dict[str, Any],
        dry_run: bool = False
    ) -> bool:
        """更新配置
        
        Args:
            common_params: CommonConfig 参数
            workflow_params: Workflow 特定参数
            dry_run: 是否为预览模式（不保存）
            
        Returns:
            是否成功
        """
        # 读取现有配置
        common_config = self.config_manager.get_common_config()
        old_config_dict = common_config.to_dict()
        
        # 应用 common 参数
        for key, value in common_params.items():
            if hasattr(common_config, key):
                # 特殊处理 runtime_envs（合并而非替换）
                if key == 'runtime_envs' and isinstance(value, dict):
                    existing_envs = getattr(common_config, key, {})
                    if isinstance(existing_envs, dict):
                        existing_envs.update(value)
                        setattr(common_config, key, existing_envs)
                    else:
                        setattr(common_config, key, value)
                else:
                    setattr(common_config, key, value)
            else:
                console.print(f"[yellow]警告: 未知的配置项 '{key}'[/yellow]")
        
        # 验证配置
        errors = self.validator.validate_common_config(common_config)
        if errors:
            console.print("[red]配置验证失败:[/red]")
            for error in errors:
                console.print(f"  [red]✗[/red] {error}")
            return False
        
        # 显示配置变更
        new_config_dict = common_config.to_dict()
        self._show_config_changes(old_config_dict, new_config_dict, "通用配置")
        
        if dry_run:
            console.print("\n[yellow]预览模式: 配置未保存[/yellow]")
            return True
        
        # 保存 common config
        self.config_manager.update_common_config(common_config)
        
        # 处理 workflow config
        if workflow_params:
            workflow_name = common_config.launch_type
            old_workflow_config = self.config_manager.get_workflow_config(workflow_name)
            new_workflow_config = old_workflow_config.copy()
            
            # 应用 workflow 参数
            for key, value in workflow_params.items():
                # 特殊处理 runtime_envs（合并而非替换）
                if key == 'runtime_envs' and isinstance(value, dict):
                    existing_envs = new_workflow_config.get('runtime_envs', {})
                    if isinstance(existing_envs, dict):
                        existing_envs.update(value)
                        new_workflow_config['runtime_envs'] = existing_envs
                    else:
                        new_workflow_config['runtime_envs'] = value
                else:
                    new_workflow_config[key] = value
            
            # 显示 workflow 配置变更
            self._show_config_changes(old_workflow_config, new_workflow_config, f"{workflow_name} 模式配置")
            
            # 保存 workflow config
            self.config_manager.update_workflow_config(workflow_name, new_workflow_config)
        
        console.print("\n[green]✅ 配置更新完成![/green]")
        console.print(f"配置文件: {self.config_manager.get_config_path()}")
        
        return True
    
    def _show_config_changes(self, old_config: Dict[str, Any], new_config: Dict[str, Any], title: str):
        """显示配置变更
        
        Args:
            old_config: 旧配置
            new_config: 新配置
            title: 标题
        """
        # 找出变更的项
        changes = []
        all_keys = set(old_config.keys()) | set(new_config.keys())
        
        for key in all_keys:
            if key.startswith('_'):  # 跳过内部字段
                continue
            
            old_value = old_config.get(key)
            new_value = new_config.get(key)
            
            if old_value != new_value:
                changes.append((key, old_value, new_value))
        
        if not changes:
            return
        
        # 创建变更表格
        console.print(f"\n[bold cyan]{title} - 变更项:[/bold cyan]")
        table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
        table.add_column("配置项", style="cyan", width=25)
        table.add_column("原值", style="yellow", width=30)
        table.add_column("新值", style="green", width=30)
        
        for key, old_value, new_value in changes:
            # 格式化显示值
            old_str = self._format_value(old_value)
            new_str = self._format_value(new_value)
            
            # 标记新增或删除
            if old_value is None or old_value == '':
                old_str = "[dim](未设置)[/dim]"
            if new_value is None or new_value == '':
                new_str = "[dim](未设置)[/dim]"
            
            table.add_row(key, old_str, new_str)
        
        console.print(table)
    
    def _format_value(self, value: Any) -> str:
        """格式化值用于显示"""
        if value is None:
            return ""
        if isinstance(value, dict):
            if not value:
                return "{}"
            # 显示字典的前几项
            items = list(value.items())[:3]
            result = ", ".join(f"{k}={v}" for k, v in items)
            if len(value) > 3:
                result += f" ... (共{len(value)}项)"
            return result
        if isinstance(value, list):
            if not value:
                return "[]"
            result = ", ".join(str(v) for v in value[:3])
            if len(value) > 3:
                result += f" ... (共{len(value)}项)"
            return result
        return str(value)
    
    def show_current_config(self):
        """显示当前配置"""
        common_config = self.config_manager.get_common_config()
        
        console.print("\n[bold cyan]当前配置:[/bold cyan]")
        
        # 创建通用配置表格
        table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
        table.add_column("配置项", style="cyan", width=25)
        table.add_column("值", style="green", width=50)
        
        config_dict = common_config.to_dict()
        for key, value in config_dict.items():
            if not key.startswith('_'):
                table.add_row(key, self._format_value(value))
        
        console.print(table)
        
        # 显示 workflow 配置
        workflow_name = common_config.launch_type
        if workflow_name:
            workflow_config = self.config_manager.get_workflow_config(workflow_name)
            if workflow_config:
                console.print(f"\n[bold cyan]{workflow_name} 模式配置:[/bold cyan]")
                
                wf_table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
                wf_table.add_column("配置项", style="cyan", width=25)
                wf_table.add_column("值", style="green", width=50)
                
                for key, value in workflow_config.items():
                    if not key.startswith('_'):
                        wf_table.add_row(key, self._format_value(value))
                
                console.print(wf_table)
