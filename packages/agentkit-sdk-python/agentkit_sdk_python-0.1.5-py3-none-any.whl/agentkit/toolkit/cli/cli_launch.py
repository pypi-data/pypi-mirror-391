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

"""AgentKit CLI - Launch command implementation."""

from pathlib import Path
import typer
from rich.console import Console
from agentkit.toolkit.cli.cli_build import build_command
from agentkit.toolkit.cli.cli_deploy import deploy_command

# Note: 不要在文件开头导很重的包，不然会导致命令很卡(import包很慢)

console = Console()


def launch_command(
    config_file: Path = typer.Option("agentkit.yaml", help="Configuration file"),
):
    """Build and deploy in one command."""
    console.print("[green]Launching agent...[/green]")
    build_command(config_file=config_file)
    deploy_command(config_file=config_file)
