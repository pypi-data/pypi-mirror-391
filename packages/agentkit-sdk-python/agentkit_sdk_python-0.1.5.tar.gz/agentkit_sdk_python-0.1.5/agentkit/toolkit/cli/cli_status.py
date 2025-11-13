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

"""AgentKit CLI - Status command implementation."""

from pathlib import Path
import typer
from rich.console import Console
from agentkit.toolkit.config import get_config

# Note: 不要在文件开头导很重的包，不然会导致命令很卡(import包很慢)

console = Console()


def status_command(
    config_file: Path = typer.Option("agentkit.yaml", help="Configuration file"),
):
    """Show current status of the agent runtime."""
    from agentkit.toolkit.workflows import WORKFLOW_REGISTRY
    try:
        config = get_config(config_path=config_file)
        common_config = config.get_common_config()
        workflow_type = common_config.launch_type

        if workflow_type not in WORKFLOW_REGISTRY:
            console.print(f"[red]Error: Unknown workflow type '{workflow_type}'[/red]")
            raise typer.Exit(1)

        workflow = WORKFLOW_REGISTRY[workflow_type]()
        workflow_config = config.get_workflow_config(workflow_type)
        status_result = workflow.status(workflow_config)

        if isinstance(status_result, dict) and status_result.get('error'):
            console.print(f"[red]Status query failed: {status_result['error']}[/red]")
            raise typer.Exit(1)

        console.print(status_result)

    except Exception as e:
        console.print(f"[red]Status query failed: {e}[/red]")
        raise typer.Exit(1)
