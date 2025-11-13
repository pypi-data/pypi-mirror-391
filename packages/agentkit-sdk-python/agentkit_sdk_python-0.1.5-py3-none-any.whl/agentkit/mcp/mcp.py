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

from typing import Dict

from agentkit.client import BaseAgentkitClient
from agentkit.utils import get_logger

# 导入自动生成的类型
from agentkit.mcp.mcp_all_types import (
    CreateMCPServiceRequest,
    CreateMCPServiceResponse,
    UpdateMCPServiceRequest,
    UpdateMCPServiceResponse,
    DeleteMCPServiceRequest,
    DeleteMCPServiceResponse,
    GetMCPServiceRequest,
    GetMCPServiceResponse,
    ListMCPServicesRequest,
    ListMCPServicesResponse,
    CreateMCPToolsetRequest,
    CreateMCPToolsetResponse,
    UpdateMCPToolsetRequest,
    UpdateMCPToolsetResponse,
    DeleteMCPToolsetRequest,
    DeleteMCPToolsetResponse,
    GetMCPToolsetRequest,
    GetMCPToolsetResponse,
    ListMCPToolsetsRequest,
    ListMCPToolsetsResponse,
    UpdateMCPToolsRequest,
    UpdateMCPToolsResponse,
    GetMCPToolsRequest,
    GetMCPToolsResponse,
    ListMCPToolsRequest,
    ListMCPToolsResponse,
)

logger = get_logger(__name__)


class AgentkitMCP(BaseAgentkitClient):
    """AgentKit MCP (Model Context Protocol) Management Service"""
    
    # Define all API actions for this service
    API_ACTIONS: Dict[str, str] = {
        "CreateMCPService": "CreateMCPService",
        "UpdateMCPService": "UpdateMCPService",
        "DeleteMCPService": "DeleteMCPService",
        "GetMCPService": "GetMCPService",
        "ListMCPServices": "ListMCPServices",
        "CreateMCPToolset": "CreateMCPToolset",
        "UpdateMCPToolset": "UpdateMCPToolset",
        "DeleteMCPToolset": "DeleteMCPToolset",
        "GetMCPToolset": "GetMCPToolset",
        "ListMCPToolsets": "ListMCPToolsets",
        "UpdateMCPTools": "UpdateMCPTools",
        "GetMCPTools": "GetMCPTools",
        "ListMCPTools": "ListMCPTools",
    }
    
    def __init__(
        self,
        access_key: str = "",
        secret_key: str = "",
        region: str = "",
        session_token: str = "",
    ) -> None:
        super().__init__(
            access_key=access_key,
            secret_key=secret_key,
            region=region,
            session_token=session_token,
            service_name="mcp",
        )

    # ==================== MCP Service APIs ====================
    
    def create_mcp_service(
        self, request: CreateMCPServiceRequest
    ) -> CreateMCPServiceResponse:
        """Create a new MCP service."""
        return self._invoke_api(
            api_action="CreateMCPService",
            request=request,
            response_type=CreateMCPServiceResponse,
        )

    def update_mcp_service(
        self, request: UpdateMCPServiceRequest
    ) -> UpdateMCPServiceResponse:
        """Update an existing MCP service."""
        return self._invoke_api(
            api_action="UpdateMCPService",
            request=request,
            response_type=UpdateMCPServiceResponse,
        )

    def delete_mcp_service(
        self, request: DeleteMCPServiceRequest
    ) -> DeleteMCPServiceResponse:
        """Delete an MCP service."""
        return self._invoke_api(
            api_action="DeleteMCPService",
            request=request,
            response_type=DeleteMCPServiceResponse,
        )

    def get_mcp_service(
        self, request: GetMCPServiceRequest
    ) -> GetMCPServiceResponse:
        """Get details of a specific MCP service."""
        return self._invoke_api(
            api_action="GetMCPService",
            request=request,
            response_type=GetMCPServiceResponse,
        )

    def list_mcp_services(
        self, request: ListMCPServicesRequest
    ) -> ListMCPServicesResponse:
        """List all MCP services."""
        return self._invoke_api(
            api_action="ListMCPServices",
            request=request,
            response_type=ListMCPServicesResponse,
        )

    # ==================== MCP Toolset APIs ====================

    def create_mcp_toolset(
        self, request: CreateMCPToolsetRequest
    ) -> CreateMCPToolsetResponse:
        """Create a new MCP toolset."""
        return self._invoke_api(
            api_action="CreateMCPToolset",
            request=request,
            response_type=CreateMCPToolsetResponse,
        )

    def update_mcp_toolset(
        self, request: UpdateMCPToolsetRequest
    ) -> UpdateMCPToolsetResponse:
        """Update an existing MCP toolset."""
        return self._invoke_api(
            api_action="UpdateMCPToolset",
            request=request,
            response_type=UpdateMCPToolsetResponse,
        )

    def delete_mcp_toolset(
        self, request: DeleteMCPToolsetRequest
    ) -> DeleteMCPToolsetResponse:
        """Delete an MCP toolset."""
        return self._invoke_api(
            api_action="DeleteMCPToolset",
            request=request,
            response_type=DeleteMCPToolsetResponse,
        )

    def get_mcp_toolset(
        self, request: GetMCPToolsetRequest
    ) -> GetMCPToolsetResponse:
        """Get details of a specific MCP toolset."""
        return self._invoke_api(
            api_action="GetMCPToolset",
            request=request,
            response_type=GetMCPToolsetResponse,
        )

    def list_mcp_toolsets(
        self, request: ListMCPToolsetsRequest
    ) -> ListMCPToolsetsResponse:
        """List all MCP toolsets."""
        return self._invoke_api(
            api_action="ListMCPToolsets",
            request=request,
            response_type=ListMCPToolsetsResponse,
        )

    # ==================== MCP Tools APIs ====================

    def update_mcp_tools(
        self, request: UpdateMCPToolsRequest
    ) -> UpdateMCPToolsResponse:
        """Update tools for an MCP service."""
        return self._invoke_api(
            api_action="UpdateMCPTools",
            request=request,
            response_type=UpdateMCPToolsResponse,
        )

    def get_mcp_tools(
        self, request: GetMCPToolsRequest
    ) -> GetMCPToolsResponse:
        """Get tools from an MCP toolset."""
        return self._invoke_api(
            api_action="GetMCPTools",
            request=request,
            response_type=GetMCPToolsResponse,
        )

    def list_mcp_tools(
        self, request: ListMCPToolsRequest
    ) -> ListMCPToolsResponse:
        """List all MCP tools from specified toolsets."""
        return self._invoke_api(
            api_action="ListMCPTools",
            request=request,
            response_type=ListMCPToolsResponse,
        )


if __name__ == "__main__":
    # 配置日志用于测试
    from agentkit.utils import setup_logging
    setup_logging(level="INFO", format_type="simple")
    
    logger.info("=" * 70)
    logger.info("测试 AgentKit MCP API")
    logger.info("=" * 70)
    
    mcp = AgentkitMCP()
    
    logger.info("\n【示例1】列出所有MCP服务")
    try:
        list_req = ListMCPServicesRequest(page_number=1, page_size=10)
        list_res = mcp.list_mcp_services(list_req)
        logger.info("  ✓ API调用成功")
        logger.info("  总数: %s", list_res.total_count)
        logger.info("  当前页: %s/%s", list_res.page_number, list_res.page_size)
        
        if list_res.m_c_p_services:
            logger.info("\n  MCP服务列表:")
            for service in list_res.m_c_p_services[:5]:  # 只显示前5个
                logger.info("    - 服务ID: %s", service.m_c_p_service_id)
                logger.info("      名称: %s", service.name)
                logger.info("      状态: %s", service.status)
    except Exception as e:
        logger.error("  ✗ API调用失败: %s", e, exc_info=True)
    
    logger.info("\n【示例2】列出所有MCP工具集")
    try:
        list_req = ListMCPToolsetsRequest(page_number=1, page_size=10)
        list_res = mcp.list_mcp_toolsets(list_req)
        logger.info("  ✓ API调用成功")
        logger.info("  总数: %s", list_res.total_count)
        logger.info("  当前页: %s/%s", list_res.page_number, list_res.page_size)
        
        if list_res.m_c_p_toolsets:
            logger.info("\n  MCP工具集列表:")
            for toolset in list_res.m_c_p_toolsets[:5]:  # 只显示前5个
                logger.info("    - 工具集ID: %s", toolset.m_c_p_toolset_id)
                logger.info("      名称: %s", toolset.name)
                logger.info("      状态: %s", toolset.status)
    except Exception as e:
        logger.error("  ✗ API调用失败: %s", e, exc_info=True)
    
    logger.info("\n" + "=" * 70)
    logger.info("✓ AgentKit MCP API 实现完成！")
    logger.info("=" * 70)
    logger.info("支持的功能:")
    logger.info("  MCP Service (服务管理):")
    logger.info("    1. ✓ 创建MCP服务 (create_mcp_service)")
    logger.info("    2. ✓ 更新MCP服务 (update_mcp_service)")
    logger.info("    3. ✓ 删除MCP服务 (delete_mcp_service)")
    logger.info("    4. ✓ 获取MCP服务 (get_mcp_service)")
    logger.info("    5. ✓ 列出MCP服务 (list_mcp_services)")
    logger.info("  MCP Toolset (工具集管理):")
    logger.info("    6. ✓ 创建MCP工具集 (create_mcp_toolset)")
    logger.info("    7. ✓ 更新MCP工具集 (update_mcp_toolset)")
    logger.info("    8. ✓ 删除MCP工具集 (delete_mcp_toolset)")
    logger.info("    9. ✓ 获取MCP工具集 (get_mcp_toolset)")
    logger.info("   10. ✓ 列出MCP工具集 (list_mcp_toolsets)")
    logger.info("  MCP Tools (工具管理):")
    logger.info("   11. ✓ 更新MCP工具 (update_mcp_tools)")
    logger.info("   12. ✓ 获取MCP工具 (get_mcp_tools)")
    logger.info("   13. ✓ 列出MCP工具 (list_mcp_tools)")
    logger.info("\n特性:")
    logger.info("  1. ✓ 所有请求和响应都是强类型")
    logger.info("  2. ✓ 支持别名和Python字段名两种方式")
    logger.info("  3. ✓ 完整的错误处理")
    logger.info("  4. ✓ Pydantic自动验证")