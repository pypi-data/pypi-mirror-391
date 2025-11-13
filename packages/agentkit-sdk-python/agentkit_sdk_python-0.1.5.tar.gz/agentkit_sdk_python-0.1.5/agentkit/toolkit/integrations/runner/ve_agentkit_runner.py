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

import logging
import requests
import time
import json
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass, field
from datetime import datetime
from urllib.parse import urljoin
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn, TimeRemainingColumn

from agentkit.toolkit.config import CommonConfig, AUTO_CREATE_VE, is_valid_config
from agentkit.toolkit.config.dataclass_utils import AutoSerializableMixin
from agentkit.utils.misc import generate_random_id, generate_runtime_name, generate_runtime_role_name, generate_apikey_name, generate_client_token
from agentkit.runtime.runtime import AgentkitRuntime, ARTIFACT_TYPE_DOCKER_IMAGE, PROJECT_NAME_DEFAULT, API_KEY_LOCATION, RUNTIME_STATUS_READY, RUNTIME_STATUS_ERROR, RUNTIME_STATUS_UPDATING, RUNTIME_STATUS_UNRELEASED, GetAgentkitRuntimeRequest
from agentkit.runtime.runtime_v1 import AgentkitRuntime as AgentkitRuntimeV1
from agentkit.runtime.types import CreateAgentkitRuntimeRequest, CreateAgentkitRuntimeResponse, DeleteAgentkitRuntimeRequest, AuthorizerConfiguration, KeyAuth_
from agentkit.toolkit.integrations.ve_iam import VeIAM
import agentkit.runtime.runtime_all_types as runtime_all_types



from .base import Runner

logger = logging.getLogger(__name__)

console = Console()

@dataclass
class VeAgentkitRunnerConfig(AutoSerializableMixin):
    """VeAgentkit Runner配置"""
    common_config: Optional[CommonConfig] = field(default=None, metadata={"system": True, "description": "公共配置"})
    
    # Runtime配置
    runtime_id: str = field(default=AUTO_CREATE_VE, metadata={"description": "Runtime ID，Auto表示自动创建"})
    runtime_name: str = field(default=AUTO_CREATE_VE, metadata={"description": "Runtime名称，Auto表示自动生成"})
    runtime_role_name: str = field(default=AUTO_CREATE_VE, metadata={"description": "Runtime角色名称，Auto表示自动创建"})
    runtime_apikey: str = field(default="", metadata={"description": "Runtime API密钥"})
    runtime_apikey_name: str = field(default=AUTO_CREATE_VE, metadata={"description": "Runtime API密钥名称，Auto表示自动生成"})
    runtime_endpoint: str = field(default="", metadata={"description": "Runtime访问端点"})
    runtime_envs: Dict[str, str] = field(default_factory=dict, metadata={"description": "Runtime环境变量"})
    
    # 镜像配置
    image_url: str = field(default="", metadata={"description": "容器镜像完整URL"})


@dataclass
class VeAgentkitDeployResult(AutoSerializableMixin):
    """部署结果"""
    success: bool = field(default=False)
    runtime_id: str = field(default="")
    runtime_name: str = field(default="")
    runtime_endpoint: str = field(default="")
    runtime_apikey: str = field(default="")
    message: str = field(default="")
    error: str = field(default="")


class VeAgentkitRuntimeRunner(Runner):
    """VeAgentkit Runtime Runner
    
    负责管理云上Runtime的生命周期，包括：
    - 创建和管理Runtime实例
    - 部署和更新Runtime配置
    - 调用Runtime服务
    - 监控Runtime状态
    - 清理Runtime资源
    """
    
    def __init__(self):
        self.agentkit_runtime = AgentkitRuntime()
        self.agentkit_runtime_v1 = AgentkitRuntimeV1()
    
    def deploy(self, config: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """部署Runtime
        
        Args:
            config: 部署配置，包含Runtime相关配置
            
        Returns:
            (成功标志, 部署结果字典)
        """
        try:
            runner_config = VeAgentkitRunnerConfig.from_dict(config)
            runner_config.common_config = CommonConfig.from_dict(runner_config.common_config)
            
            if not runner_config.image_url:
                return False, {"error": "镜像URL不能为空，请先构建镜像"}
            
            # 准备Runtime配置
            if not self._prepare_runtime_config(runner_config):
                return False, {"error": "Runtime配置准备失败"}
            
            # ensure_role_for_agentkit
            ve_iam = VeIAM()
            if not ve_iam.ensure_role_for_agentkit(runner_config.runtime_role_name):
                return False, {"error": "创建Runtime角色失败"}

            # 部署Runtime
            if runner_config.runtime_id == AUTO_CREATE_VE:
                return self._create_new_runtime(runner_config)
            else:
                return self._update_existing_runtime(runner_config)
                
        except Exception as e:
            logger.error(f"Runtime部署失败: {str(e)}")
            return False, {"error": str(e)}
    
    def destroy(self, config: Dict[str, Any]) -> bool:
        """销毁Runtime
        
        Args:
            config: 销毁配置，包含Runtime ID
            
        Returns:
            是否成功
        """
        try:
            runner_config = VeAgentkitRunnerConfig.from_dict(config)
            
            if not runner_config.runtime_id or runner_config.runtime_id == AUTO_CREATE_VE:
                console.print("未配置Runtime ID，跳过销毁")
                return True
            
            # 删除Runtime
            delete_request = DeleteAgentkitRuntimeRequest(
                RuntimeId=runner_config.runtime_id
            )
            
            self.agentkit_runtime.delete(delete_request)
            console.print(f"[green]✅ Runtime销毁成功: {runner_config.runtime_id}[/green]")
            return True
            
        except Exception as e:
            logger.error(f"Runtime销毁失败: {str(e)}")
            return False

    def status(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """获取Runtime状态
        
        Args:
            config: 状态查询配置，包含Runtime ID
            
        Returns:
            Runtime状态信息
        """
        try:
            runner_config = VeAgentkitRunnerConfig.from_dict(config)
            
            if not runner_config.runtime_id or runner_config.runtime_id == AUTO_CREATE_VE:
                return {"status": "not_deployed", "message": "未部署Runtime"}
            
            # 获取Runtime信息
            runtime = self.agentkit_runtime.get(
                GetAgentkitRuntimeRequest(RuntimeId=runner_config.runtime_id)
            )
            if runner_config.runtime_apikey == "":
                runner_config.runtime_apikey = runtime.authorizer_configuration.KeyAuth.ApiKey
            # 检查Endpoint连通性
            ping_status = None
            if runtime.status == RUNTIME_STATUS_READY and runtime.endpoint:
                try:
                    ping_response = requests.get(
                        urljoin(runtime.endpoint, "ping"), 
                        headers={"Authorization": f"Bearer {runner_config.runtime_apikey}"},
                        timeout=10
                    )
                    ping_status = ping_response.status_code == 200
                except Exception as e:
                    logger.error(f"检查Endpoint连通性失败: {str(e)}")
                    ping_status = False
            
            return {
                "runtime_id": runner_config.runtime_id,
                "runtime_name": runtime.name if hasattr(runtime, 'name') else runner_config.runtime_name,
                "status": runtime.status,
                "endpoint": runtime.endpoint if hasattr(runtime, 'endpoint') else "",
                "image_url": runtime.artifact_url if hasattr(runtime, 'artifact_url') else "",
                "ping_status": ping_status,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取Runtime状态失败: {str(e)}")
            if "InvalidAgentKitRuntime.NotFound" in str(e):
                return {"status": "not found", "message": f"Runtime未找到，可能已经被删除，请检查Runtime ID: {runner_config.runtime_id} 是否正确"}
            return {"status": "error", "error": str(e)}

    def invoke(self, config: Dict[str, Any], payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None, stream: Optional[bool] = None) -> Tuple[bool, Any]:
        """调用Runtime服务
        
        Args:
            config: 调用配置，包含Runtime端点和API密钥
            payload: 请求负载
            headers: 请求头
            stream: 是否使用流式调用。None=自动检测(默认), True=强制流式, False=强制非流式
            
        Returns:
            如果 stream=False: (成功标志, 响应数据字典)
            如果 stream=True: (成功标志, 生成器对象) - 可通过 for 循环迭代事件
        """
        try:
            runner_config = VeAgentkitRunnerConfig.from_dict(config)
            
            # 获取Runtime端点和API密钥
            endpoint = runner_config.runtime_endpoint
            api_key = runner_config.runtime_apikey
            if not endpoint or not api_key:
                if not runner_config.runtime_id or runner_config.runtime_id == AUTO_CREATE_VE:
                    return False, {"error": "Runtime未部署"}
                
                # 自动获取Runtime信息
                try:
                    runtime = self.agentkit_runtime.get(
                        GetAgentkitRuntimeRequest(RuntimeId=runner_config.runtime_id)
                    )
                except Exception as e:
                    if "NotFound" in str(e):
                        return False, {"error": "配置的Runtime已被外部操作删除，请重新部署"}
                    raise e
                endpoint = runtime.endpoint
                api_key = runtime.authorizer_configuration.KeyAuth.ApiKey
                
                if not endpoint or not api_key:
                    return False, {"error": f"无法获取Runtime端点或API密钥, runtime: {runtime}"}
            
            # 构造调用URL
            invoke_endpoint = urljoin(endpoint, "invoke")
            
            # 准备请求头
            if headers is None:
                headers = {}
            
            if not headers.get("Authorization"):
                headers["Authorization"] = f"Bearer {api_key}"
            
            # 使用基类的通用 HTTP 调用方法
            return self._http_post_invoke(
                endpoint=invoke_endpoint,
                payload=payload,
                headers=headers,
                stream=stream,
                timeout=60
            )
            
        except Exception as e:
            logger.error(f"Runtime调用失败: {str(e)}")
            return False, {"error": str(e)}
    
    def _prepare_runtime_config(self, config: VeAgentkitRunnerConfig) -> bool:
        """准备Runtime配置
        
        Args:
            config: Runner配置
            
        Returns:
            是否成功
        """
        try:
            # 检查并创建Runtime名称
            if config.runtime_name == AUTO_CREATE_VE or not config.runtime_name:
                config.runtime_name = generate_runtime_name(config.common_config.agent_name)
                console.print(f"✅ 生成Runtime名称: {config.runtime_name}")
            
            # 检查并创建角色名称
            if config.runtime_role_name == AUTO_CREATE_VE or not config.runtime_role_name:
                # config.runtime_role_name = "TestRoleForAgentKit" #
                config.runtime_role_name = generate_runtime_role_name()
                console.print(f"✅ 生成角色名称: {config.runtime_role_name}")
            
            # 检查并创建API密钥名称
            if config.runtime_apikey_name == AUTO_CREATE_VE or not config.runtime_apikey_name:
                config.runtime_apikey_name = generate_apikey_name()
                console.print(f"✅ 生成API密钥名称: {config.runtime_apikey_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Runtime配置准备失败: {str(e)}")
            return False
    
    def _create_new_runtime(self, config: VeAgentkitRunnerConfig) -> Tuple[bool, Dict[str, Any]]:
        """创建新Runtime
        
        Args:
            config: Runner配置
            
        Returns:
            (成功标志, 部署结果字典)
        """
        try:
            console.print(f"[blue]正在创建Runtime: {config.runtime_name}[/blue]")
            
            # 构建创建请求
            envs = [{"Key": str(k), "Value": str(v)} for k, v in config.runtime_envs.items()]
            
            create_request = CreateAgentkitRuntimeRequest(
                Name=config.runtime_name,
                Description= config.common_config.description if is_valid_config(config.common_config.description) else f"Auto created by AgentKit CLI for agent project {config.common_config.agent_name}",
                ArtifactType=ARTIFACT_TYPE_DOCKER_IMAGE,
                ArtifactUrl=config.image_url,
                RoleName=config.runtime_role_name,
                Envs=envs,
                ProjectName=PROJECT_NAME_DEFAULT,
                AuthorizerConfiguration=AuthorizerConfiguration(
                    KeyAuth=KeyAuth_(
                        ApiKey=config.runtime_apikey,
                        ApiKeyName=config.runtime_apikey_name,
                        ApiKeyLocation=API_KEY_LOCATION
                    ),
                ),
                ClientToken=generate_client_token(),
                Tags=[{"Key": "environment", "Value": "test"}],
                ApmplusEnable=True,
            )
            
            # console.print("创建请求:")
            # console.print(json.dumps(create_request.model_dump(by_alias=True), indent=2))
            
            # 创建Runtime
            runtime_resp, request_id = self.agentkit_runtime.create(create_request)
            config.runtime_id = runtime_resp.id
            
            console.print(f"✅ [green]创建Runtime成功: {runtime_resp.id}, request_id: {request_id}[/green]")
            console.print("[blue]等待Runtime状态为Ready...[/blue]")
            console.print("[blue]💡 提示：Runtime初始化中，请耐心等待，不要中断进程[/blue]")
            
            # 等待Runtime就绪
            success, runtime, error = self._wait_for_runtime_status(
                runtime_id=config.runtime_id,
                target_status=RUNTIME_STATUS_READY,
                task_description="等待Runtime就绪...",
                timeout=None,  # 创建时不设超时
                error_message="初始化失败"
            )
            
            if not success:
                console.print(f"[yellow]⚠️  Runtime未成功初始化: {config.runtime_id}[/yellow]")
                console.print(f"[yellow]错误信息: {error}[/yellow]")
                
                # 交互式询问用户是否清理
                user_input = input("\n是否清理失败的Runtime? (y/n): ").strip().lower()
                
                if user_input in ['y', 'yes', '是']:
                    console.print(f"[blue]正在清理失败的Runtime: {config.runtime_id}[/blue]")
                    try:
                        delete_request = DeleteAgentkitRuntimeRequest(
                            RuntimeId=config.runtime_id
                        )
                        self.agentkit_runtime.delete(delete_request)
                        console.print(f"[green]✅ Runtime清理成功[/green]")
                    except Exception as e:
                        if not "InvalidAgentKitRuntime.NotFound" in str(e):
                            console.print(f"[red]清理Runtime失败: {str(e)}[/red]")
                else:
                    console.print(f"[yellow]已跳过清理，Runtime保留: {config.runtime_id}[/yellow]")
                
                return False, {"error": error}
            
            console.print(f"Endpoint: {runtime.endpoint}")
            config.runtime_endpoint = runtime.endpoint
            config.runtime_apikey = runtime.authorizer_configuration.KeyAuth.ApiKey
            
            return True, {
                "runtime_id": config.runtime_id,
                "runtime_name": config.runtime_name,
                "runtime_endpoint": runtime.endpoint,
                "runtime_apikey": config.runtime_apikey,
                "runtime_apikey_name": config.runtime_apikey_name,
                "runtime_role_name": config.runtime_role_name,
                "message": "Runtime创建成功"
            }
                
        except Exception as e:
            logger.error(f"创建Runtime失败: {str(e)}")
            return False, {"error": str(e)}
    
    def _wait_for_runtime_status(
        self,
        runtime_id: str,
        target_status: str,
        task_description: str,
        timeout: Optional[int] = None,
        error_message: str = "等待Runtime状态变化失败"
    ) -> Tuple[bool, Optional[Any], Optional[str]]:
        """等待Runtime达到目标状态（单状态版本）
        
        Args:
            runtime_id: Runtime ID
            target_status: 目标状态
            task_description: 进度条任务描述
            timeout: 超时时间（秒），None表示不超时
            error_message: 失败时的错误消息
            
        Returns:
            (是否成功, Runtime对象或None, 错误信息或None)
        """
        # 调用多状态版本，传入单个状态作为列表
        return self._wait_for_runtime_status_multiple(
            runtime_id=runtime_id,
            target_statuses=[target_status],
            task_description=task_description,
            timeout=timeout,
            error_message=error_message
        )
    
    def _wait_for_runtime_status_multiple(
        self,
        runtime_id: str,
        target_statuses: List[str],
        task_description: str,
        timeout: Optional[int] = None,
        error_message: str = "等待Runtime状态变化失败"
    ) -> Tuple[bool, Optional[Any], Optional[str]]:
        """等待Runtime达到多个目标状态之一
        
        Args:
            runtime_id: Runtime ID
            target_statuses: 目标状态列表
            task_description: 进度条任务描述
            timeout: 超时时间（秒），None表示不超时
            error_message: 失败时的错误消息
            
        Returns:
            (是否成功, Runtime对象或None, 错误信息或None)
        """
        last_status = None
        start_time = time.time()
        total_time = timeout if timeout else 300  # 用于进度条显示
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            task = progress.add_task(task_description, total=total_time)
            
            while True:
                runtime = self.agentkit_runtime.get(
                    GetAgentkitRuntimeRequest(RuntimeId=runtime_id)
                )
                
                # 检查是否达到任一目标状态
                if runtime.status in target_statuses:
                    progress.update(task, completed=1, total=1)
                    console.print(f"✅ Runtime状态为{runtime.status}")
                    return True, runtime, None
                
                # 检查是否出错
                if runtime.status == RUNTIME_STATUS_ERROR:
                    progress.update(task, description="[red]Runtime操作失败[/red]")
                    return False, None, f"Runtime状态为Error，{error_message}"
                
                # 计算已用时间
                elapsed_time = time.time() - start_time
                
                # 检查超时
                if timeout and elapsed_time > timeout:
                    progress.update(task, description="[red]等待超时[/red]")
                    return False, None, f"{error_message}（超时{timeout}秒）"
                
                # 状态变化时更新进度条描述
                if runtime.status != last_status:
                    progress.update(task, description=f"Runtime状态: {runtime.status}")
                    last_status = runtime.status
                
                # 更新进度
                progress.update(task, completed=min(elapsed_time, total_time))
                
                time.sleep(3)
    
    def _needs_runtime_update(self, runtime: runtime_all_types.GetAgentKitRuntimeResponse, config: VeAgentkitRunnerConfig) -> Tuple[bool, str]:
        """检查Runtime是否需要更新
        
        Args:
            runtime: 现有Runtime对象
            config: 新的Runner配置
            
        Returns:
            (是否需要更新, 更新原因描述)
        """

        update_reasons = []
        
        # 检查镜像URL是否变化
        if runtime.artifact_url != config.image_url:
            update_reasons.append(f"镜像URL变化: {runtime.artifact_url} -> {config.image_url}")
        
        # 检查环境变量是否变化
        # 系统自动注入的环境变量前缀，这些不应该被用户修改
        SYSTEM_ENV_PREFIXES = ('OTEL_', 'ENABLE_APMPLUS', 'APMPLUS_')
        
        # 将runtime的envs转换为字典进行比较（过滤系统环境变量）
        runtime_envs = {}
        if hasattr(runtime, 'envs') and runtime.envs:
            for env in runtime.envs:
                key = None
                value = None
                
                # 尝试小写属性名（runtime_all_types返回的对象）
                if hasattr(env, 'key') and hasattr(env, 'value'):
                    key, value = env.key, env.value
                # 尝试大写属性名（兼容其他类型）
                elif hasattr(env, 'Key') and hasattr(env, 'Value'):
                    key, value = env.Key, env.Value
                # 如果是字典类型
                elif isinstance(env, dict):
                    key = env.get('key') or env.get('Key', '')
                    value = env.get('value') or env.get('Value', '')
                
                # 过滤掉系统环境变量
                if key and not key.startswith(SYSTEM_ENV_PREFIXES):
                    runtime_envs[key] = value
        
        # 比较环境变量（只比较用户自定义的）
        if runtime_envs != config.runtime_envs:
            # 找出具体差异
            added_keys = set(config.runtime_envs.keys()) - set(runtime_envs.keys())
            removed_keys = set(runtime_envs.keys()) - set(config.runtime_envs.keys())
            changed_keys = {k for k in set(runtime_envs.keys()) & set(config.runtime_envs.keys()) 
                          if runtime_envs[k] != config.runtime_envs.get(k)}
            
            env_changes = []
            if added_keys:
                env_changes.append(f"新增环境变量: {', '.join(added_keys)}")
            if removed_keys:
                env_changes.append(f"删除环境变量: {', '.join(removed_keys)}")
            if changed_keys:
                env_changes.append(f"修改环境变量: {', '.join(changed_keys)}")
            
            if env_changes:
                update_reasons.append("环境变量变化: " + "; ".join(env_changes))
        
        needs_update = len(update_reasons) > 0
        reason = " | ".join(update_reasons) if needs_update else "配置无变化"
        
        return needs_update, reason
    
    def _update_existing_runtime(self, config: VeAgentkitRunnerConfig) -> Tuple[bool, Dict[str, Any]]:
        """更新现有Runtime
        
        Args:
            config: Runner配置
            
        Returns:
            (成功标志, 更新结果字典)
        """
        try:
            console.print("[red]当前功能正在测试，因此会打印较多日志，以供调试[/red]")
            console.print(f"正在更新Runtime: {config.runtime_id}")
            
            # 获取现有Runtime信息
            runtime = self.agentkit_runtime_v1.get(
                runtime_all_types.GetAgentKitRuntimeRequest(runtime_id=config.runtime_id)
            )
            
            if not runtime:
                return False, {"error": f"未找到Runtime: {config.runtime_id}，无法更新Runtime，请检查Runtime状态"}
            
            if runtime.artifact_type != ARTIFACT_TYPE_DOCKER_IMAGE:
                return False, {"error": f"不支持的Runtime类型: {runtime.artifact_type}"}
            
            # 检查是否需要更新
            # needs_update, update_reason = self._needs_runtime_update(runtime, config)
            needs_update = True # 现在总是更新

            if not needs_update:
                console.print(f"✅ Runtime配置已是最新，无需更新")
                config.runtime_endpoint = runtime.endpoint
                config.runtime_apikey = runtime.authorizer_configuration.key_auth.api_key
                
                return True, {
                    "runtime_id": config.runtime_id,
                    "runtime_name": runtime.name if hasattr(runtime, 'name') else config.runtime_name,
                    "runtime_endpoint": runtime.endpoint,
                    "runtime_apikey": config.runtime_apikey,
                    "message": "Runtime配置已是最新"
                }
            
            console.print(f"开始更新Runtime...")
            
            envs = [{"Key": str(k), "Value": str(v)} for k, v in config.runtime_envs.items()]
            self.agentkit_runtime_v1.update(runtime_all_types.UpdateAgentKitRuntimeRequest(
                runtime_id=config.runtime_id,
                artifact_url=config.image_url,
                description=config.common_config.description,
                envs=envs,
                client_token=generate_client_token(),
            ))
            
            console.print("✅ Runtime更新请求已提交")
            
            # 阶段1：等待Runtime更新完成，状态可能变为UnReleased或直接变为Ready
            console.print("[blue]等待Runtime更新完成...[/blue]")
            success, updated_runtime, error = self._wait_for_runtime_status_multiple(
                runtime_id=config.runtime_id,
                target_statuses=[RUNTIME_STATUS_UNRELEASED, RUNTIME_STATUS_READY],
                task_description="等待Runtime更新完成...",
                timeout=180,
                error_message="更新失败"
            )
            
            if not success:
                return False, {"error": error}
            
            # 检查当前状态：如果已经是Ready，说明更新直接完成，无需发布
            if updated_runtime.status == RUNTIME_STATUS_READY:
                console.print("[green]✅ Runtime已直接更新至Ready状态，无需发布步骤[/green]")
            else:
                # 阶段2：状态为UnReleased，需要发布更新
                console.print("[blue]开始发布Runtime更新...[/blue]")
                self.agentkit_runtime_v1.release(
                    runtime_all_types.ReleaseAgentKitRuntimeRequest(
                        runtime_id=config.runtime_id,
                    )
                )
                
                # 等待发布完成
                console.print("[blue]等待Runtime发布完成，状态变为Ready...[/blue]")
                console.print("[blue]💡 提示：Runtime发布中，请耐心等待，不要中断进程[/blue]")
                
                success, updated_runtime, error = self._wait_for_runtime_status(
                    runtime_id=config.runtime_id,
                    target_status=RUNTIME_STATUS_READY,
                    task_description="等待Runtime发布完成...",
                    timeout=300,
                    error_message="发布失败"
                )
                
                if not success:
                    return False, {"error": error}
            
            console.print(f"Endpoint: {updated_runtime.endpoint}")
            config.runtime_endpoint = updated_runtime.endpoint
            config.runtime_apikey = updated_runtime.authorizer_configuration.KeyAuth.ApiKey
            
            return True, {
                "runtime_id": config.runtime_id,
                "runtime_name": runtime.name if hasattr(runtime, 'name') else config.runtime_name,
                "runtime_endpoint": runtime.endpoint,
                "runtime_apikey": config.runtime_apikey,
                "message": "Runtime更新完成"
            }
            
        except Exception as e:
            logger.error(f"更新Runtime失败: {str(e)}")
            return False, {"error": str(e)}