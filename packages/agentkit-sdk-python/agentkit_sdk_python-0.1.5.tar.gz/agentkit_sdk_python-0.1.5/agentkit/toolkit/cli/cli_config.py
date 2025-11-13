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

"""AgentKit CLI - Config command implementation."""

from typing import Optional, List
import typer
from rich.console import Console

from agentkit.toolkit.config import get_config, CommonConfig
from agentkit.toolkit.config.config_handler import (
    ConfigParamHandler, 
    NonInteractiveConfigHandler
)

# Note: 不要在文件开头导很重的包，不然会导致命令很卡(import包很慢)

console = Console()


def config_command(
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="配置文件路径"),
    
    # 模式控制
    interactive: bool = typer.Option(False, "--interactive", "-i", help="强制交互式模式"),
    dry_run: bool = typer.Option(False, "--dry-run", help="预览配置变更但不保存"),
    show: bool = typer.Option(False, "--show", "-s", help="显示当前配置"),
    
    # CommonConfig 参数
    agent_name: Optional[str] = typer.Option(None, "--agent_name", help="Agent应用名称"),
    entry_point: Optional[str] = typer.Option(None, "--entry_point", help="入口文件 (例如: agent.py)"),
    description: Optional[str] = typer.Option(None, "--description", help="应用描述"),
    python_version: Optional[str] = typer.Option(None, "--python_version", help="Python版本 (例如: 3.12)"),
    dependencies_file: Optional[str] = typer.Option(None, "--dependencies_file", help="依赖文件 (例如: requirements.txt)"),
    launch_type: Optional[str] = typer.Option(None, "--launch_type", help="部署模式: local/hybrid/cloud"),
    
    # 应用级环境变量（CommonConfig）
    runtime_envs: Optional[List[str]] = typer.Option(None, "--runtime_envs", "-e", help="应用级环境变量 KEY=VALUE，所有部署模式共享（可多次使用）"),
    
    # Workflow 级环境变量
    workflow_runtime_envs: Optional[List[str]] = typer.Option(None, "--workflow-runtime-envs", help="Workflow级环境变量 KEY=VALUE，仅当前部署模式使用（可多次使用）"),
    
    # Hybrid/Cloud workflow 参数
    region: Optional[str] = typer.Option(None, "--region", help="区域 (例如: cn-beijing)"),
    tos_bucket: Optional[str] = typer.Option(None, "--tos_bucket", help="TOS存储桶名称"),
    image_tag: Optional[str] = typer.Option(None, "--image_tag", help="镜像标签 (例如: 0.0.1)"),
    cr_instance_name: Optional[str] = typer.Option(None, "--cr_instance_name", "--ve_cr_instance_name", help="CR 实例名称"),
    cr_namespace_name: Optional[str] = typer.Option(None, "--cr_namespace_name", "--ve_cr_namespace_name", help="CR 命名空间"),
    cr_repo_name: Optional[str] = typer.Option(None, "--cr_repo_name", "--ve_cr_repo_name", help="CR 仓库名称"),
):
    """config AgentKit(support interactive and non-interactive mode)
    
    示例:
    
    \b
    # 交互式配置（默认）
    agentkit config
    
    \b
    # 非交互式配置（完整）
    agentkit config \\
        --agent_name myAgent \\
        --entry_point agent.py \\
        --launch_type cloud \\
        --region cn-beijing \\
        --tos_bucket agentkit \\
        --image_tag 0.0.1 \\
        --runtime_envs API_KEY=xxxxx \\
        --runtime_envs MODEL_ENDPOINT=https://api.example.com
    
    \b
    # 应用级 vs Workflow 级环境变量
    # --runtime_envs/-e: 应用级（所有部署模式共享）
    # --workflow-runtime-envs: 仅当前部署模式使用
    agentkit config \\
        -e API_KEY=shared_key \\
        --workflow-runtime-envs DEBUG=true
    
    \b
    # 增量更新（只修改部分配置）
    agentkit config --entry_point new_agent.py
    
    \b
    # 预览配置变更
    agentkit config --entry_point agent.py --dry-run
    
    \b
    # 显示当前配置
    agentkit config --show
    """
    
    try:
        # 处理 --show 选项
        if show:
            handler = NonInteractiveConfigHandler(config_path=config_file)
            handler.show_current_config()
            return
        
        # 收集 CLI 参数
        cli_params = ConfigParamHandler.collect_cli_params(
            agent_name=agent_name,
            entry_point=entry_point,
            description=description,
            python_version=python_version,
            dependencies_file=dependencies_file,
            launch_type=launch_type,
            runtime_envs=runtime_envs,
            workflow_runtime_envs=workflow_runtime_envs,
            region=region,
            tos_bucket=tos_bucket,
            image_tag=image_tag,
            cr_instance_name=cr_instance_name,
            cr_namespace_name=cr_namespace_name,
            cr_repo_name=cr_repo_name,
        )
        
        has_cli_params = ConfigParamHandler.has_cli_params(cli_params)
        
        # 决定使用哪种模式
        if interactive or (not has_cli_params and not interactive):
            # 交互式模式（保持原有行为）
            _interactive_config(config_file)
        else:
            # 非交互式模式
            handler = NonInteractiveConfigHandler(config_path=config_file)
            success = handler.update_config(
                common_params=cli_params['common'],
                workflow_params=cli_params['workflow'],
                dry_run=dry_run
            )
            
            if not success:
                raise typer.Exit(code=1)
    
    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠️  配置已取消[/yellow]")
        raise typer.Exit(code=130)  # 130 is the standard exit code for Ctrl+C


def _interactive_config(config_file: Optional[str] = None):
    """交互式配置（原有逻辑）"""
    config = get_config(config_path=config_file)
    
    common_config = CommonConfig.interactive_create(config.get_common_config().to_dict())
    config.update_common_config(common_config)
    
    workflow_name = common_config.launch_type

    from agentkit.toolkit.workflows import WORKFLOW_REGISTRY, Workflow
    
    if workflow_name in WORKFLOW_REGISTRY:
        workflow: Workflow = WORKFLOW_REGISTRY[workflow_name]()
        workflow_config = workflow.prompt_for_config(config.get_workflow_config(workflow_name))
        config.update_workflow_config(workflow_name, workflow_config)
        
        common_config.launch_type = workflow_name
        config.update_common_config(common_config)
    
    console.print("[green]✅ 配置完成![/green]")
