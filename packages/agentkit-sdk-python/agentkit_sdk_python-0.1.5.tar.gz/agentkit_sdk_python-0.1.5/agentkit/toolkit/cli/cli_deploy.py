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

"""AgentKit CLI - Deploy command implementation."""

from pathlib import Path
import typer
from rich.console import Console
from agentkit.toolkit.config import get_config

# Note: 不要在文件开头导很重的包，不然会导致命令很卡(import包很慢)

console = Console()


def deploy_command(
    config_file: Path = typer.Option("agentkit.yaml", help="Configuration file"),
):
    """Deploy the Agent to target environment."""
    from agentkit.toolkit.workflows import WORKFLOW_REGISTRY
    console.print(f"[green]Deploying with {config_file}[/green]")
    
    config = get_config(config_path=config_file)
    common_config = config.get_common_config()

    if not common_config.entry_point:
        console.print("[red]Entry point not configured, cannot deploy[/red]")
        raise typer.Exit(1)
    
    workflow_name = common_config.launch_type
    if workflow_name not in WORKFLOW_REGISTRY:
        console.print(f"[red]Error: Unknown workflow type '{workflow_name}'[/red]")
        raise typer.Exit(1)
    
    workflow_config = config.get_workflow_config(workflow_name)
    
    workflow = WORKFLOW_REGISTRY[workflow_name]()
    success = workflow.deploy(workflow_config)
    
    if not success:
        raise typer.Exit(1)
