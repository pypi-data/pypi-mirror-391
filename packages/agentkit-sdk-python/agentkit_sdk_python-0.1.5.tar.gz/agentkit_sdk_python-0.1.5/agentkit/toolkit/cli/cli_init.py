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

"""AgentKit CLI - Init command for project initialization."""

import random
import re
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from agentkit.toolkit.config import (
    get_config, 
    DEFAULT_IMAGE_TAG,
    LocalDockerConfig_v1,
    VeAgentkitConfig
)

# Note: 不要在文件开头导很重的包，不然会导致命令很卡(import包很慢)

try:
    from pyfiglet import Figlet
    HAS_PYFIGLET = True
except ImportError:
    HAS_PYFIGLET = False

console = Console()

def show_logo():
    """Display AgentKit logo"""
    console.print()
    
    if HAS_PYFIGLET:
        # Try different fonts in order of preference
        fonts_to_try = ['slant', 'speed', 'banner3', 'big', 'standard']
        figlet = None
        
        for font in fonts_to_try:
            try:
                figlet = Figlet(font=font)
                break
            except:
                continue
        
        if figlet is None:
            figlet = Figlet()  # Use default font
        
        logo_text = figlet.renderText('AgentKit')
        
        # Apply gradient color effect - more vibrant colors
        lines = logo_text.split('\n')
        colors = ["bright_magenta", "magenta", "bright_blue", "cyan", "bright_cyan"]
        
        for i, line in enumerate(lines):
            if line.strip():  # Skip empty lines
                # Create a gradient effect
                color_idx = int((i / max(len(lines) - 1, 1)) * (len(colors) - 1))
                color = colors[color_idx]
                console.print(Text(line, style=f"bold {color}"))
    else:
        # Fallback: beautiful box logo if pyfiglet is not installed
        console.print(Text("  ╔══════════════════════════════════════╗", style="bold bright_cyan"))
        console.print(Text("  ║                                      ║", style="bold bright_cyan"))
        console.print(Text("  ║   ", style="bold bright_cyan") + 
                     Text("🚀  A G E N T K I T  🤖", style="bold bright_magenta") +
                     Text("   ║", style="bold bright_cyan"))
        console.print(Text("  ║                                      ║", style="bold bright_cyan"))
        console.print(Text("  ╚══════════════════════════════════════╝", style="bold bright_cyan"))
    
    # Add tagline with emoji
    console.print(Text("     ✨ Build AI Agents with Ease ✨", style="bold yellow"))
    console.print()

# 模板元数据配置
TEMPLATES = {
    "basic": {
        "file": "basic.py",
        "name": "Basic Agent App",
        "description": "最简单的Agent应用，快速上手",
        "type": "Basic App",
    },
    # "simple_app": {
    #     "file": "simple_app_veadk.py",
    #     "name": "Simple Agent App",
    #     "description": "基础的Agent应用，包含可观测配置",
    #     "type": "Simple App",
    # },
    "basic_stream": {
        "file": "basic_stream.py",
        "name": "Basic Stream Agent App",
        "description": "支持流式输出的Agent应用",
        "type": "Stream App",
        "extra_requirements": ["google-adk"],
    },
    # "mcp": {
    #     "file": "simple_mcp_veadk.py",
    #     "name": "MCP Agent App",
    #     "description": "Model Context Protocol (MCP) Agent应用",
    #     "type": "MCP App",
    # },
    # "a2a": {
    #     "file": "simple_a2a_veadk.py",
    #     "name": "Agent-to-Agent App",
    #     "description": "Agent间通信(A2A)应用，使用Google ADK",
    #     "type": "A2A App",
    # },
    # Temporarily disabled - will be enabled later
    # "financial_analyst": {
    #     "file": "financial_analyst.py",
    #     "name": "Financial Analyst",
    #     "description": "金融分析师Agent示例",
    #     "type": "Domain App",
    # },
    # "customer_support": {
    #     "file": "customer_support_assistant.py",
    #     "name": "Customer Support Assistant",
    #     "description": "客服助手Agent示例",
    #     "type": "Domain App",
    # },
}


def display_templates():
    """显示可用的模板列表"""
    table = Table(title="Available Templates", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan", width=6)
    table.add_column("Name", style="green", width=25)
    table.add_column("Type", style="yellow", width=15)
    table.add_column("Description", style="white")

    for idx, (key, template) in enumerate(TEMPLATES.items(), 1):
        table.add_row(
            str(idx),
            template["name"],
            template["type"],
            template["description"]
        )

    console.print(table)


def select_template(template_key: Optional[str] = None) -> str:
    """选择模板，支持交互式和命令行参数两种方式"""
    if template_key:
        # 通过命令行参数指定模板
        if template_key in TEMPLATES:
            return template_key
        else:
            console.print(f"[red]Error: Unknown template '{template_key}'[/red]")
            console.print(f"[yellow]Available templates: {', '.join(TEMPLATES.keys())}[/yellow]")
            raise typer.Exit(1)
    
    # 交互式选择
    display_templates()
    console.print(f"\n[bold cyan]Please select a template by entering the ID (1-{len(TEMPLATES)}):[/bold cyan]")
    
    while True:
        try:
            choice = input("Template ID:")
            choice_idx = int(choice) - 1
            
            if 0 <= choice_idx < len(TEMPLATES):
                selected_key = list(TEMPLATES.keys())[choice_idx]
                console.print(f"[green]Selected: {TEMPLATES[selected_key]['name']}[/green]")
                return selected_key
            else:
                console.print(f"[red]Invalid choice. Please enter a number between 1 and {len(TEMPLATES)}[/red]")
        except ValueError:
            console.print("[red]Invalid input. Please enter a number[/red]")
        except typer.Abort:
            console.print("[yellow]Cancelled[/yellow]")
            raise typer.Exit(0)


def init_command(
    project_name: Optional[str] = typer.Argument(None, help="Project name"),
    template: Optional[str] = typer.Option(None, "--template", "-t", help="Project template (basic, basic_stream)"),
    directory: Optional[str] = typer.Option(".", help="Target directory"),
    agent_name: Optional[str] = typer.Option(None, "--agent-name", help="Agent name (default: 'Agent')"),
    description: Optional[str] = typer.Option(None, "--description", help="Agent description (uses a common default description if not provided), this will be helpful in A2A scenario."),
    system_prompt: Optional[str] = typer.Option(None, "--system-prompt", help="Agent system prompt (uses a common default system prompt if not provided)"),
    model_name: Optional[str] = typer.Option(None, "--model-name", help="Model name in volcengine ARK platform (default: 'doubao-seed-1-6-250615')"),
    tools: Optional[str] = typer.Option(None, "--tools", help="Comma-separated list of tools to include (e.g., web_search,run_code)"),
):
    """Initialize a new Agent project with templates."""
    # Display logo
    show_logo()
    
    target_dir = Path(directory)
    project_name = project_name or "simple_agent"
    
    # project_name格式：只能包含数字、字母、中划线、下划线
    if not re.match(r'^[a-zA-Z0-9_-]+$', project_name):
        console.print(f"[red]Error: Project name '{project_name}' contains invalid characters. Only letters, numbers, hyphens, and underscores are allowed.[/red]")
        raise typer.Exit(1)
    
    # 检查目标目录是否存在，如果不存在则创建
    if not target_dir.exists():
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            console.print(f"[blue]Created directory: {target_dir}[/blue]")
        except Exception as e:
            console.print(f"[red]Error: Failed to create directory '{target_dir}': {e}[/red]")
            raise typer.Exit(1)
    elif not target_dir.is_dir():
        console.print(f"[red]Error: '{target_dir}' exists but is not a directory[/red]")
        raise typer.Exit(1)
    
    # 选择模板
    template_key = select_template(template)
    template_info = TEMPLATES[template_key]
    
    console.print(f"[bold green]Creating project: {project_name}[/bold green]")
    console.print(f"[bold blue]Using template: {template_info['name']}[/bold blue]")
    
    file_name = f"{project_name}.py"
    agent_file_path = target_dir / file_name
    requirements_file_path = target_dir / "requirements.txt"
    config_file_path = target_dir / "agentkit.yaml"
    
    if agent_file_path.exists():
        console.print(f"[yellow]File {file_name} already exists, skipping creation[/yellow]")
        return
    
    try:
        # 从模板文件复制内容
        source_path = Path(__file__).parent.parent / "resources" / "samples" / template_info["file"]
        
        if not source_path.exists():
            console.print(f"[red]Error: Template file not found: {source_path}[/red]")
            raise typer.Exit(1)
        
        with open(source_path, 'r', encoding='utf-8') as source_file:
            template_content = source_file.read()
        
        # 使用 jinja2 渲染模板
        import jinja2
        template = jinja2.Template(template_content)
        # 只传递非 None 的参数，让 jinja2 的 default 过滤器正常工作
        render_context = {}
        if agent_name is not None:
            render_context['agent_name'] = agent_name
        if description is not None:
            render_context['description'] = description
        if system_prompt is not None:
            render_context['system_prompt'] = system_prompt
        if model_name is not None:
            render_context['model_name'] = model_name
        if tools is not None:
            # 将逗号分隔的工具字符串转换为列表
            tools_list = [tool.strip() for tool in tools.split(',') if tool.strip()]
            render_context['tools'] = tools_list
        rendered_content = template.render(**render_context)
        
        with open(agent_file_path, 'w', encoding='utf-8') as agent_file:
            agent_file.write(rendered_content)
        
        console.print(f"[bold green]Successfully created file: {file_name}[/bold green]")
        
        # 创建 requirements.txt 文件
        if not requirements_file_path.exists():
            with open(requirements_file_path, 'w', encoding='utf-8') as req_file:
                req_file.write("veadk-python\nveadk-python[extensions]\n")
                # 添加模板特定的依赖
                if "extra_requirements" in template_info:
                    for requirement in template_info["extra_requirements"]:
                        req_file.write(f"{requirement}\n")
            console.print(f"[bold green]Successfully created file: requirements.txt[/bold green]")
        else:
            console.print(f"[yellow]File requirements.txt already exists, skipping creation[/yellow]")

        # 生成一份默认的local模式的config
        if not config_file_path.exists():
            configManager = get_config(config_path=config_file_path)
            common_config = configManager.get_common_config()
            common_config.launch_type = 'cloud'
            common_config.agent_name = project_name
            common_config.description = f"AgentKit project {project_name} - {template_info['name']}"
            common_config.entry_point = file_name
            configManager.update_common_config(common_config)

            if common_config.launch_type == 'local':
                local_config = LocalDockerConfig_v1.from_dict(configManager.get_workflow_config(common_config.launch_type))
                random_port = random.randint(1024, 49151)
                local_config.invoke_port = random_port
                local_config.ports = [f"{random_port}:8000"]
                configManager.update_workflow_config(common_config.launch_type, local_config.to_dict())
            elif common_config.launch_type == 'cloud':
                cloud_config = VeAgentkitConfig.from_dict(configManager.get_workflow_config(common_config.launch_type))
                from agentkit.toolkit.integrations.services.tos_service import TOSService
                from agentkit.toolkit.integrations.services.cr_service import CRService
                cloud_config.tos_bucket = TOSService.default_bucket_name_template()
                cloud_config.cr_instance_name = CRService.default_cr_instance_name_template()
                cloud_config.cr_repo_name = common_config.agent_name
                cloud_config.image_tag = DEFAULT_IMAGE_TAG
                configManager.update_workflow_config(common_config.launch_type, cloud_config.to_dict())
            console.print(f"[bold green]Successfully created file: agentkit.yaml[/bold green]")
        else:
            console.print(f"[yellow]File agentkit.yaml already exists, skipping creation[/yellow]")
        
        # 创建 .dockerignore 文件
        dockerignore_file_path = target_dir / ".dockerignore"
        if not dockerignore_file_path.exists():
            dockerignore_content = """# AgentKit configuration
agentkit.yaml
agentkit*.yaml

# Python cache
__pycache__/
*.py[cod]
*$py.class

# Virtual environments
.venv/
venv/
ENV/
env/

# IDE
.vscode/
.idea/
.windsurf/

# Git
.git/
.gitignore

# Docker
Dockerfile*
.dockerignore
"""
            with open(dockerignore_file_path, 'w', encoding='utf-8') as dockerignore_file:
                dockerignore_file.write(dockerignore_content)
            console.print(f"[bold green]Successfully created file: .dockerignore[/bold green]")
        else:
            console.print(f"[yellow]File .dockerignore already exists, skipping creation[/yellow]")
        
        console.print("\n[bold blue]✨ Project initialized successfully![/bold blue]")
        console.print(f"[blue]Template: {template_info['name']}[/blue]")
        console.print(f"[blue]Entry point: {file_name}[/blue]")
        console.print("\n[bold cyan]Next steps:[/bold cyan]")
        console.print("  1. Review and modify the generated files")
        console.print("  2. Use 'agentkit config' to configure your agent")
        console.print("  3. Use 'agentkit launch' to build and deploy")
        
    except Exception as e:
        console.print(f"[red]Failed to create project: {e}[/red]")
        raise typer.Exit(1)
