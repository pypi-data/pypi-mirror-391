from dataclasses import dataclass, field
from typing import Dict, List
from .dataclass_utils import AutoSerializableMixin
from .constants import AUTO_CREATE_VE, DEFAULT_CR_NAMESPACE, DEFAULT_IMAGE_TAG, DEFAULT_WORKSPACE_NAME


@dataclass
class LocalDockerConfig_v1(AutoSerializableMixin):
    """Local Docker workflow configuration"""
    # User configurable fields
    image_tag: str = field(default="latest", metadata={"description": "Docker image tag", "icon": "🏷️"})
    invoke_port: int = field(default=8000, metadata={"description": "Agent application invoke port, defaults to 8000", "icon": "🌐"})

    # System internal fields (not visible to users)
    container_name: str = field(default="", metadata={"system": True, "description": "Container name, uses agent_name if empty"})
    ports: List[str] = field(default_factory=lambda: ["8000:8000"], metadata={"system": True, "description": "Port mappings in host:container format, comma-separated"})
    volumes: List[str] = field(default_factory=list, metadata={"system": True, "description": "Volume mappings in host:container format, comma-separated"})
    restart_policy: str = field(default="unless-stopped", metadata={"system": True, "description": "Restart policy"})
    memory_limit: str = field(default="1g", metadata={"system": True, "description": "Memory limit"})
    cpu_limit: str = field(default="1", metadata={"system": True, "description": "CPU limit"})
    container_id: str = field(default="", metadata={"system": True})
    image_id: str = field(default="", metadata={"system": True})
    build_timestamp: str = field(default="", metadata={"system": True})
    deploy_timestamp: str = field(default="", metadata={"system": True})
    full_image_name: str = field(default="", metadata={"system": True})
    runtime_envs: Dict[str, str] = field(
        default_factory=dict, 
        metadata={
            "system": True,
            "description": "运行时环境变量 (输入 KEY=VALUE，空行结束，del KEY 删除，list 查看)",
            "examples": "MODEL_AGENT_API_KEY=your_key_here, DEBUG=true",
            "icon": "🔧"
        }
    )
    _config_metadata = {
        'name': '本地运行配置',
        'welcome_message': ' 欢迎使用 AgentKit 本地运行模式 配置向导',
        'next_step_hint': '本向导将帮助您完成本地模式下应用部署运行相关配置，请根据提示输入相关信息，或直接按Enter键使用默认值。',
        'completion_message': '太棒了！部署运行配置已完成！',
        'next_action_hint': '可以使用agentkit launch命令一键启动应用了！'
    }


@dataclass
class HybridVeAgentkitConfig_v1(AutoSerializableMixin):
    """本地Docker工作流配置"""
    # 用户可配置字段
    image_tag: str = field(default=DEFAULT_IMAGE_TAG, metadata={"system": True, "description": "镜像标签", "icon": "🏷️", "render_template": True})
    # 系统内部字段（用户不可见）
    image_id: str = field(default="", metadata={"system": True})
    build_timestamp: str = field(default="", metadata={"system": True})
    full_image_name: str = field(default="", metadata={"system": True})

    region: str = field(default="cn-beijing", metadata={"description": "火山引擎服务区域", "icon": "🌏", "aliases": ["ve_region"]})
    
    # CR相关配置
    cr_instance_name: str = field(default=AUTO_CREATE_VE, metadata={"description": "容器镜像服务实例名称", "icon": "📦", "render_template": True, "aliases": ["ve_cr_instance_name"]})
    cr_namespace_name: str = field(default=DEFAULT_CR_NAMESPACE, metadata={"description": "容器镜像命名空间", "icon": "📁", "render_template": True, "aliases": ["ve_cr_namespace_name"]})
    cr_repo_name: str = field(default="", metadata={"description": "容器镜像仓库名称", "icon": "📋", "aliases": ["ve_cr_repo_name"]})
    cr_image_full_url: str = field(default="", metadata={"system": True, "aliases": ["ve_cr_image_full_url"]})

    # runtime相关配置
    runtime_role_name: str = field(default=AUTO_CREATE_VE, metadata={"system": True, "description": "Agentkit 授权角色", "icon": "🔐", "aliases": ["ve_runtime_role_name"]})
    runtime_name: str = field(default=AUTO_CREATE_VE, metadata={"system": True, "description": "Agentkit Runtime名称", "icon": "⚙️", "aliases": ["ve_runtime_name"]})
    runtime_id: str = field(default="", metadata={"system": True, "aliases": ["ve_runtime_id"]})
    runtime_apikey: str = field(default="", metadata={"system": True, "aliases": ["ve_runtime_apikey"]})
    runtime_apikey_name: str = field(default=AUTO_CREATE_VE, metadata={"system": True, "aliases": ["ve_runtime_apikey_name"]})
    runtime_endpoint: str = field(default="", metadata={"system": True, "description": "Agentkit Runtime应用访问入口", "aliases": ["ve_runtime_endpoint"]})
    runtime_envs: Dict[str, str] = field(
        default_factory=dict, 
        metadata={
            "system": True,
            "description": "运行时环境变量 (输入 KEY=VALUE，空行结束，del KEY 删除，list 查看)",
            "examples": "MODEL_AGENT_API_KEY=your_key_here, DEBUG=true",
            "icon": "🔧"
        }
    )
    _config_metadata = {
        'name': '混合部署运行模式配置',
        'welcome_message': ' 欢迎使用 AgentKit 混合部署运行模式 配置向导',
        'next_step_hint': '本向导将帮助您完成混合模式下应用部署运行相关配置，请根据提示输入相关信息，或直接按Enter键使用默认值。',
        'completion_message': '太棒了！部署运行配置已完成！',
        'next_action_hint': '可以使用agentkit launch命令一键启动应用了！'
    }
    
    def __post_init__(self):
        """对象创建后自动渲染标记的字段"""
        self._render_template_fields()  # 调用基类方法



@dataclass
class VeAgentkitConfig(AutoSerializableMixin):
    """VeAgentkit工作流配置"""
    region: str = field(default="cn-beijing", metadata={"description": "服务使用的区域", "icon": "🌏"})

    # TOS配置
    tos_bucket: str = field(default=AUTO_CREATE_VE, metadata={"system": True, "description": "TOS存储桶名称", "icon": "🗂️", "render_template": True})
    tos_prefix: str = field(default="agentkit-builds", metadata={"system": True, "description": "TOS对象前缀"})
    tos_region: str = field(default="cn-beijing", metadata={"system": True, "description": "TOS区域"})
    tos_object_key: str = field(default="", metadata={"system": True})
    tos_object_url: str = field(default="", metadata={"system": True})
    
    # CR配置
    image_tag: str = field(default=DEFAULT_IMAGE_TAG, metadata={"system": True, "description": "镜像标签", "icon": "🏷️", "render_template": True})
    cr_instance_name: str = field(default=AUTO_CREATE_VE, metadata={"description": "CR实例名称", "icon": "📦", "render_template": True, "aliases": ["ve_cr_instance_name"]})
    cr_namespace_name: str = field(default=DEFAULT_CR_NAMESPACE, metadata={"description": "CR命名空间", "icon": "📁", "render_template": True, "aliases": ["ve_cr_namespace_name"]})
    cr_repo_name: str = field(default="", metadata={"description": "CR仓库名称，默认使用AgentKit项目名", "icon": "📋", "aliases": ["ve_cr_repo_name"]})
    cr_region: str = field(default="cn-beijing", metadata={"system": True, "description": "CR区域", "aliases": ["ve_cr_region"]})
    cr_image_full_url: str = field(default="", metadata={"system": True, "aliases": ["ve_cr_image_full_url"]})
    build_timeout: int = field(default=3600, metadata={"system": True, "description": "构建超时时间(秒)"})

    cp_workspace_name: str = field(default=DEFAULT_WORKSPACE_NAME, metadata={"system": True, "description": "Code Pipeline工作区名称"})
    cp_pipeline_name: str = field(default=AUTO_CREATE_VE, metadata={"system": True, "description": "Code Pipeline流水线名称"})
    cp_pipeline_id: str = field(default="", metadata={"system": True})

    # Runtime配置
    runtime_id: str = field(default=AUTO_CREATE_VE, metadata={"system": True, "description": "运行时ID", "aliases": ["ve_runtime_id"]})
    runtime_name: str = field(default=AUTO_CREATE_VE, metadata={"system": True, "description": "运行时名称", "aliases": ["ve_runtime_name"]})
    runtime_role_name: str = field(default=AUTO_CREATE_VE, metadata={"system": True, "description": "运行时角色名称", "aliases": ["ve_runtime_role_name"]})
    runtime_apikey: str = field(default=AUTO_CREATE_VE, metadata={"system": True,"description": "运行时API密钥", "aliases": ["ve_runtime_apikey"]})
    runtime_apikey_name: str = field(default=AUTO_CREATE_VE, metadata={"system": True, "description": "运行时API密钥名称", "aliases": ["ve_runtime_apikey_name"]})
    runtime_endpoint: str = field(default="", metadata={"system": True, "description": "运行时访问入口，自动获取", "aliases": ["ve_runtime_endpoint"]})
    runtime_envs: Dict[str, str] = field(
        default_factory=dict, 
        metadata={
            "system": True,
            "description": "运行时环境变量 (输入 KEY=VALUE，空行结束，del KEY 删除，list 查看)",
            "examples": "MODEL_AGENT_API_KEY=your_key_here, DEBUG=true",
            "icon": "🔧"
        }
    )
    
    build_timestamp: str = field(default="", metadata={"system": True})
    deploy_timestamp: str = field(default="", metadata={"system": True})

    _config_metadata = {
        'name': '云构建与部署配置',
        'welcome_message': ' 欢迎使用 AgentKit 云构建与部署模式 配置向导',
        'next_step_hint': '本向导将帮助您完成云构建与部署模式下应用部署运行相关配置，请根据提示输入相关信息，或直接按Enter键使用默认值。',
        'completion_message': '太棒了！部署运行配置已完成！',
        'next_action_hint': '可以使用agentkit launch命令一键启动应用了！'
    }
    
    def __post_init__(self):
        """对象创建后自动渲染标记的字段"""
        self._render_template_fields()  # 调用基类方法
    

