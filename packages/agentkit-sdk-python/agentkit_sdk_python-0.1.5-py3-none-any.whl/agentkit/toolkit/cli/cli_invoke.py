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

"""AgentKit CLI - Invoke command implementation."""

from pathlib import Path
from typing import Optional, Any
import json
import typer
from rich.console import Console
from agentkit.toolkit.config import get_config

# Note: 不要在文件开头导很重的包，不然会导致命令很卡(import包很慢)

console = Console()


def invoke_command(
    config_file: Path = typer.Option("agentkit.yaml", help="Configuration file"),
    message: str = typer.Argument(None, help="Simple message to send to agent"),
    payload: str = typer.Option(
        None, "--payload", "-p", help="JSON payload to send (advanced option)"
    ),
    headers: str = typer.Option(
        None, "--headers", "-h", help="JSON headers for request (advanced option)"
    ),
    apikey: str = typer.Option(
        None, "--apikey", "-ak", help="API key for authentication"
    ),
) -> Any:
    """Send a test request to deployed Agent.
    
    Examples:
        # Simple message
        agentkit invoke "今天天气如何？"
        
        # Custom payload
        agentkit invoke --payload '{"prompt": "杭州天气?"}'
        
        # With custom headers
        agentkit invoke --payload '{"prompt": "杭州天气?"}' --headers '{"user_id": "test123"}'
    """
    from agentkit.toolkit.workflows import WORKFLOW_REGISTRY, Workflow
    console.print("[cyan]Invoking agent...[/cyan]")
    
    # 验证参数：message和payload不能同时提供
    if message and payload:
        console.print("[red]Error: Cannot specify both message and payload. Use either message or --payload.[/red]")
        raise typer.Exit(1)
    
    # 验证参数：必须提供message或payload
    if not message and not payload:
        console.print("[red]Error: Must provide either a message or --payload option.[/red]")
        raise typer.Exit(1)
    
    # 处理payload
    if message:
        # 简单消息模式：自动组织为payload
        final_payload = {"prompt": message}
        console.print(f"[blue]Using simple message mode: {message}[/blue]")
    else:
        # 高级模式：使用用户提供的payload
        try:
            final_payload = json.loads(payload) if isinstance(payload, str) else payload
            console.print(f"[blue]Using custom payload: {final_payload}[/blue]")
        except json.JSONDecodeError as e:
            console.print(f"[red]Error: Invalid JSON payload: {e}[/red]")
            raise typer.Exit(1)
    
    # 处理headers
    final_headers = {"user_id": "agentkit_user", "session_id": "agentkit_sample_session"}
    if headers:
        try:
            final_headers = json.loads(headers) if isinstance(headers, str) else headers
            console.print(f"[blue]Using custom headers: {final_headers}[/blue]")
        except json.JSONDecodeError as e:
            console.print(f"[red]Error: Invalid JSON headers: {e}[/red]")
            raise typer.Exit(1)
    else:
        console.print(f"[blue]Using default headers: {final_headers}[/blue]")
    
    config = get_config(config_path=config_file)
    common_config = config.get_common_config()
    
    workflow_name = common_config.launch_type
    if workflow_name not in WORKFLOW_REGISTRY:
        console.print(f"[red]Error: Unknown workflow type '{workflow_name}'[/red]")
        raise typer.Exit(1)
    
    workflow_config = config.get_workflow_config(workflow_name)
    
    workflow: Workflow = WORKFLOW_REGISTRY[workflow_name]()
    success, response = workflow.invoke(workflow_config, {
        "payload": final_payload, 
        "headers": final_headers, 
        "apikey": apikey
    })
    if not success:
        raise typer.Exit(1)
    
    console.print("[green]✅ Invocation successful[/green]")
    
    # 处理流式响应（生成器）
    if hasattr(response, '__iter__') and not isinstance(response, (dict, str, list)):
        console.print("[cyan]📡 Streaming response detected...[/cyan]\n")
        result_list = []
        complete_text = []
        
        for event in response:
            result_list.append(event)
            
            # 如果是字符串且以 "data: " 开头，尝试解析（fallback处理）
            if isinstance(event, str):
                if event.strip().startswith("data: "):
                    try:
                        json_str = event.strip()[6:].strip()  # 移除 "data: " 前缀
                        event = json.loads(json_str)
                    except json.JSONDecodeError:
                        # 解析失败，跳过此事件
                        continue
                else:
                    # 不是 SSE 格式的字符串，跳过
                    continue
            
            # 解析事件内容
            if isinstance(event, dict):
                # 提取文本内容
                content = event.get("content", {})
                part = event.get("partial", False)
                if part and isinstance(content, dict):
                    parts = content.get("parts", [])
                    for part in parts:
                        if isinstance(part, dict) and "text" in part:
                            text = part["text"]
                            complete_text.append(text)
                            console.print(text, end="", style="green")
                            
                    
                # 显示错误信息
                if "error" in event:
                    console.print(f"\n[red]Error: {event['error']}[/red]")
        
        # 显示完整响应
        if complete_text:
            console.print("\n\n[cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/cyan]")
            console.print(f"[cyan]📝 Complete response:[/cyan] {''.join(complete_text)}")
        
        return str(result_list)
    
    # 处理非流式响应
    console.print("[cyan]📝 Response:[/cyan]")
    if isinstance(response, dict):
        console.print(json.dumps(response, indent=2, ensure_ascii=False))
    else:
        console.print(response)
    
    return str(response)
