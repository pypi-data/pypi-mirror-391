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

import json

from agentkit.toolkit.workflows import Workflow
from typing import Dict, Any, Tuple
from datetime import datetime
from agentkit.toolkit.config import (
    AUTO_CREATE_VE, 
    get_config,
    VeAgentkitConfig
)
from agentkit.toolkit.integrations.runner import VeAgentkitRuntimeRunner
from agentkit.utils.misc import generate_runtime_name
from agentkit.toolkit.integrations.services.cr_service import CRService
from rich.console import Console
from agentkit.toolkit.integrations.services.tos_service import TOSService

console = Console()

class VeAgentkitWorkflow(Workflow):
    """VeAgentkit工作流实现 - 使用VeCPCRBuilder进行云上构建"""
    
    def __init__(self):
        super().__init__()
        self.console = Console()
    
    def prompt_for_config(self, current_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """生成交互式配置"""
        from agentkit.toolkit.config.auto_prompt import generate_config_from_dataclass
        
        if current_config is None:
            current_config = {}

        agent_config = get_config()
        common_config = agent_config.get_common_config()
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        # 兼容旧字段名
        if current_config.get("cr_instance_name") is None or current_config["cr_instance_name"] == AUTO_CREATE_VE or current_config["cr_instance_name"] == "":
            # 也检查旧字段名
            if current_config.get("ve_cr_instance_name"):
                current_config["cr_instance_name"] = current_config["ve_cr_instance_name"]
            else:
                current_config["cr_instance_name"] = CRService.default_cr_instance_name_template()
        if current_config.get("cr_repo_name") is None or current_config["cr_repo_name"] == AUTO_CREATE_VE or current_config["cr_repo_name"] == "":
            if current_config.get("ve_cr_repo_name"):
                current_config["cr_repo_name"] = current_config["ve_cr_repo_name"]
            else:
                current_config["cr_repo_name"] = common_config.agent_name

        #桶名称
        if current_config.get("tos_bucket") is None or current_config["tos_bucket"] == AUTO_CREATE_VE or current_config["tos_bucket"] == "":
            current_config["tos_bucket"] = TOSService.default_bucket_name_template()
            
        return generate_config_from_dataclass(VeAgentkitConfig, current_config)

    def build(self, config: Dict[str, Any]) -> bool:
        """构建代理镜像使用VeCPCRBuilder"""
        try:
            from agentkit.toolkit.integrations.builder.ve_core_pipeline_builder import (
                VeCPCRBuilder, VeCPCRBuilderConfig, VeCPCRBuilderResult
            )
        except ImportError as e:
            console.print(f"[red]错误: 缺少VeCPCRBuilder依赖 - {e}[/red]")
            return False
            
        try:
            console.print("[green]🔨 开始构建Agent镜像...[/green]")
            
            # 解析配置
            ve_config = VeAgentkitConfig.from_dict(config)
            agent_config = get_config()
            common_config = agent_config.get_common_config()

            # 特殊规则，CP名称必须和runtime名称一致
            # 1. 如果runtime名称未配置，生成一个runtime名称
            if ve_config.runtime_name == AUTO_CREATE_VE or ve_config.runtime_name == "":
                ve_config.runtime_name = generate_runtime_name(common_config.agent_name)
            # 2. 强制CP名称和runtime名称一致
            ve_config.cp_pipeline_name = ve_config.runtime_name

            
            
            # 构建VeCPCRBuilder配置
            builder_config = VeCPCRBuilderConfig(
                common_config=common_config,
                tos_bucket=ve_config.tos_bucket,
                tos_region=ve_config.tos_region,
                tos_prefix=ve_config.tos_prefix,
                cr_instance_name=ve_config.cr_instance_name,
                cr_namespace_name=ve_config.cr_namespace_name,
                cr_repo_name=ve_config.cr_repo_name,
                cr_region=ve_config.cr_region,
                cp_workspace_name=ve_config.cp_workspace_name,
                cp_pipeline_name=ve_config.cp_pipeline_name,
                cp_pipeline_id=ve_config.cp_pipeline_id,
                image_tag=ve_config.image_tag,
                build_timeout=ve_config.build_timeout
            ).to_dict()
            
            # 执行构建
            builder = VeCPCRBuilder()
            success, build_result = builder.build(builder_config)
            
            if success:
                result = VeCPCRBuilderResult.from_dict(build_result)
                
                # 更新配置
                ve_config.cr_image_full_url = result.image_url
                ve_config.cr_instance_name = result.cr_instance_name or ve_config.cr_instance_name
                ve_config.cr_namespace_name = result.cr_namespace_name or ve_config.cr_namespace_name
                ve_config.cr_repo_name = result.cr_repo_name or ve_config.cr_repo_name
                ve_config.cp_pipeline_id = result.cp_pipeline_id or ve_config.cp_pipeline_id
                ve_config.build_timestamp = result.build_timestamp or ve_config.build_timestamp
                
                
                # 回写TOS资源信息
                if result.resources:
                    ve_config.tos_object_key = result.resources.get('tos_object_key', ve_config.tos_object_key)
                    ve_config.tos_object_url = result.resources.get('tos_url', ve_config.tos_object_url) 
                    ve_config.tos_bucket = result.resources.get('tos_bucket', ve_config.tos_bucket)
                
                # 回写Pipeline名称（如果VeCPCRBuilder更新了它）
                if result.resources and result.resources.get('pipeline_name'):
                    ve_config.cp_pipeline_name = result.resources.get('pipeline_name')
                
                agent_config.update_workflow_config("cloud", ve_config.to_persist_dict())
                return True
            else:
                result = VeCPCRBuilderResult.from_dict(build_result)
                error_msg = result.error_message or "构建失败"
                
                # 构建失败时仍然回写已创建的资源信息
                if result.resources:
                    ve_config.tos_object_key = result.resources.get('tos_object_key', ve_config.tos_object_key)
                    ve_config.tos_object_url = result.resources.get('tos_url', ve_config.tos_object_url) 
                    agent_config.update_workflow_config("cloud", ve_config.to_persist_dict())
                
                console.print(f"[red]❌ 构建失败: {error_msg}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]构建错误: {str(e)}[/red]")
            return False

    def deploy(self, config: Dict[str, Any]) -> bool:
        """部署代理到云上环境 - 使用VeAgentkitRuntimeRunner"""
        try:
            console.print("[green]🚀 开始部署Agent...[/green]")
            
            # 解析配置
            ve_config = VeAgentkitConfig.from_dict(config)
            
            # 检查镜像URL
            if not ve_config.cr_image_full_url:
                console.print("[yellow]⚠️ 未找到镜像URL，请先执行构建[/yellow]")
                return False
            
            # 获取公共配置
            agent_config = get_config()
            common_config = agent_config.get_common_config()
            
            # 合并应用级和 Workflow 级环境变量
            from agentkit.toolkit.config import merge_runtime_envs
            merged_envs = merge_runtime_envs(common_config, ve_config.to_dict())
            
            # 创建Runner配置
            runner_config = {
                "common_config": common_config.to_dict(),
                "runtime_id": ve_config.runtime_id or AUTO_CREATE_VE,
                "runtime_name": ve_config.runtime_name,
                "runtime_role_name": ve_config.runtime_role_name,
                "runtime_apikey": ve_config.runtime_apikey,
                "runtime_apikey_name": ve_config.runtime_apikey_name,
                "runtime_endpoint": ve_config.runtime_endpoint,
                "runtime_envs": merged_envs,
                "image_url": ve_config.cr_image_full_url
            }
            
            # 使用Runner部署
            runner = VeAgentkitRuntimeRunner()
            success, result = runner.deploy(runner_config)
            
            if success:
                # 更新部署时间戳
                ve_config.runtime_id = result.get("runtime_id", ve_config.runtime_id)
                ve_config.runtime_name = result.get("runtime_name", ve_config.runtime_name)
                ve_config.runtime_endpoint = result.get("runtime_endpoint", ve_config.runtime_endpoint)
                ve_config.runtime_apikey = result.get("runtime_apikey", ve_config.runtime_apikey)
                ve_config.runtime_apikey_name = result.get("runtime_apikey_name", ve_config.runtime_apikey_name)
                ve_config.runtime_role_name = result.get("runtime_role_name", ve_config.runtime_role_name)
                ve_config.deploy_timestamp = datetime.now().isoformat()
                agent_config.update_workflow_config("cloud", ve_config.to_persist_dict())
                console.print(f"[green]✅ 部署完成: {ve_config.cr_image_full_url}[/green]")
                console.print(f"[green]✅ Runtime ID: {ve_config.runtime_id}[/green]")
                console.print(f"[green]✅ Runtime Endpoint: {ve_config.runtime_endpoint}[/green]")
                return True
            else:
                console.print(f"[red]❌ 部署失败: {result.get('error', '未知错误')}[/red]")
                return False
            
        except Exception as e:
            console.print(f"[red]❌ 部署失败: {str(e)}[/red]")
            return False

    def invoke(self, config: Dict[str, Any] = None, args: Dict[str, Any] = None) -> Tuple[bool, Any]:
        """调用云上Runtime - 使用VeAgentkitRuntimeRunner"""
        # 解析配置
        ve_config = VeAgentkitConfig.from_dict(config)

        # 检查配置
        if not ve_config.runtime_id:
            console.print(f"[red]❌ 未配置Runtime ID，请先执行deploy步骤[/red]")
            return False, {"error": "未配置Runtime ID"}
        
        try:
            # 创建Runner配置
            runner_config = {
                "common_config": {},
                "runtime_id": ve_config.runtime_id,
                "runtime_endpoint": ve_config.runtime_endpoint,
                "runtime_apikey": ve_config.runtime_apikey
            }
            payload = args.get("payload", {"prompt": "北京天气怎么样"})
            if isinstance(payload, str):
                payload = json.loads(payload)
            headers = args.get("headers", {"user_id": "agentkit_user", "session_id": "agentkit_sample_session"})
            if isinstance(headers, str):
                headers = json.loads(headers)
            # 使用Runner调用
            runner = VeAgentkitRuntimeRunner()
            success, result = runner.invoke(runner_config, payload, headers)
            
            if success:
                return True, result
            else:
                console.print(f"[red]❌ 云上调用失败: {result}[/red]")
                return False, {"error": result}
                
        except Exception as e:
            console.print(f"[red]❌ 云上调用异常: {str(e)}[/red]")
            return False, {"error": str(e)}


    def status(self, config: VeAgentkitConfig) -> Dict[str, Any]:
        """获取云上Runtime状态 - 使用VeAgentkitRuntimeRunner"""
        # 解析配置
        ve_config = VeAgentkitConfig.from_dict(config)

        # 检查配置
        if not ve_config.runtime_id:
            console.print(f"[yellow]⚠️ 未配置Runtime ID[/yellow]")
            return {"status": "not_deployed", "message": "未配置Runtime ID"}
        
        console.print(f"[green]✅ Runtime ID: {ve_config.runtime_id}[/green]")
        
        try:
            # 创建Runner配置
            runner_config = {
                "common_config": {},
                "runtime_id": ve_config.runtime_id,
                "runtime_endpoint": ve_config.runtime_endpoint,
                "runtime_apikey": ve_config.runtime_apikey
            }
            
            # 使用Runner获取状态
            runner = VeAgentkitRuntimeRunner()
            status_info = runner.status(runner_config)
            
            # 控制台输出
            if status_info.get("status") == "Ready":
                console.print(f"[green]✅ Runtime状态为Ready, Endpoint: {status_info.get('endpoint')}[/green]")
            else:
                console.print(f"[yellow]当前Runtime状态: {status_info.get('status')}，状态异常[/yellow]")
            
            return status_info
            
        except Exception as e:
            console.print(f"[red]❌ 获取Runtime状态失败: {str(e)}[/red]")
            return {"status": "error", "message": str(e)}

    def stop(self, config: Dict[str, Any] = None) -> bool:
        """停止工作流 - 使用VeAgentkitRuntimeRunner"""
        if config is None:
            config = get_config().get_workflow_config("cloud")
        ve_config = VeAgentkitConfig.from_dict(config)
        
        if not ve_config.runtime_id:
            console.print("[yellow]⚠️ 未配置Runtime ID，无需停止[/yellow]")
            return True
        
        try:
            console.print("[yellow]🛑 停止VeAgentkit Runtime...[/yellow]")
            
            # 创建Runner配置
            runner_config = {
                "common_config": {},
                "runtime_id": ve_config.runtime_id,
            }
            
            # 使用Runner停止
            runner = VeAgentkitRuntimeRunner()
            success = runner.stop(runner_config)
            
            if success:
                console.print("[green]✅ Runtime停止成功[/green]")
            else:
                console.print("[red]❌ Runtime停止失败[/red]")
            
            return success
            
        except Exception as e:
            console.print(f"[red]❌ Runtime停止异常: {str(e)}[/red]")
            return False

    def destroy(self, config: Dict[str, Any] = None) -> bool:
        """销毁工作流资源 - 使用VeAgentkitRuntimeRunner"""
        try:
            console.print("[red]🗑️ 销毁AgentKit相关资源...[/red]")
            
            agent_config = get_config()
            if config is None:
                config = agent_config.get_workflow_config("cloud")
            
            ve_config = VeAgentkitConfig.from_dict(config)
            
            # 销毁Runtime
            if ve_config.runtime_id:
                try:
                    runner_config = {
                        "common_config": {},
                        "runtime_id": ve_config.runtime_id
                    }
                    runner = VeAgentkitRuntimeRunner()
                    runner.destroy(runner_config)
                except Exception as e:
                    console.print(f"[yellow]⚠️ Runtime销毁失败: {str(e)}[/yellow]")
            
            # 重置配置
            ve_config.cr_image_full_url = None
            ve_config.cp_pipeline_id = None
            ve_config.build_timestamp = None
            ve_config.deploy_timestamp = None
            ve_config.tos_object_key = None
            ve_config.tos_object_url = None
            ve_config.runtime_id = ""
            ve_config.runtime_endpoint = ""
            ve_config.runtime_apikey = ""
            
            agent_config.update_workflow_config("cloud", ve_config.to_persist_dict())
            
            console.print("[green]✅ 资源已销毁[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]❌ 销毁失败: {str(e)}[/red]")
            return False