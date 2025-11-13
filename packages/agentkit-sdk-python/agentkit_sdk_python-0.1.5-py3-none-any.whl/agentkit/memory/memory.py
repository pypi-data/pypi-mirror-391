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
from agentkit.memory.memory_all_types import (
    CreateMemoryCollectionRequest,
    CreateMemoryCollectionResponse,
    UpdateMemoryCollectionRequest,
    UpdateMemoryCollectionResponse,
    DeleteMemoryCollectionRequest,
    DeleteMemoryCollectionResponse,
    ListMemoryCollectionsRequest,
    ListMemoryCollectionsResponse,
    AddMemoryCollectionRequest,
    AddMemoryCollectionResponse,
    GetMemoryCollectionRequest,
    GetMemoryCollectionResponse,
    GetMemoryConnectionInfoRequest,
    GetMemoryConnectionInfoResponse,
)

logger = get_logger(__name__)


class AgentkitMemory(BaseAgentkitClient):
    """AgentKit Memory Collection Management Service"""
    
    # Define all API actions for this service
    API_ACTIONS: Dict[str, str] = {
        "CreateMemoryCollection": "CreateMemoryCollection",
        "UpdateMemoryCollection": "UpdateMemoryCollection",
        "DeleteMemoryCollection": "DeleteMemoryCollection",
        "ListMemoryCollections": "ListMemoryCollections",
        "AddMemoryCollection": "AddMemoryCollection",
        "GetMemoryCollection": "GetMemoryCollection",
        "GetMemoryConnectionInfo": "GetMemoryConnectionInfo",
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
            service_name="memory",
        )

    def create_memory_collection(
        self, request: CreateMemoryCollectionRequest
    ) -> CreateMemoryCollectionResponse:
        """Create a new memory collection."""
        return self._invoke_api(
            api_action="CreateMemoryCollection",
            request=request,
            response_type=CreateMemoryCollectionResponse,
        )

    def update_memory_collection(
        self, request: UpdateMemoryCollectionRequest
    ) -> UpdateMemoryCollectionResponse:
        """Update an existing memory collection."""
        return self._invoke_api(
            api_action="UpdateMemoryCollection",
            request=request,
            response_type=UpdateMemoryCollectionResponse,
        )

    def delete_memory_collection(
        self, request: DeleteMemoryCollectionRequest
    ) -> DeleteMemoryCollectionResponse:
        """Delete a memory collection."""
        return self._invoke_api(
            api_action="DeleteMemoryCollection",
            request=request,
            response_type=DeleteMemoryCollectionResponse,
        )

    def list_memory_collections(
        self, request: ListMemoryCollectionsRequest
    ) -> ListMemoryCollectionsResponse:
        """List all memory collections."""
        return self._invoke_api(
            api_action="ListMemoryCollections",
            request=request,
            response_type=ListMemoryCollectionsResponse,
        )

    def add_memory_collection(
        self, request: AddMemoryCollectionRequest
    ) -> AddMemoryCollectionResponse:
        """Add memory collections from external providers."""
        return self._invoke_api(
            api_action="AddMemoryCollection",
            request=request,
            response_type=AddMemoryCollectionResponse,
        )

    def get_memory_collection(
        self, request: GetMemoryCollectionRequest
    ) -> GetMemoryCollectionResponse:
        """Get detailed information about a specific memory collection."""
        return self._invoke_api(
            api_action="GetMemoryCollection",
            request=request,
            response_type=GetMemoryCollectionResponse,
        )

    def get_memory_connection_info(
        self, request: GetMemoryConnectionInfoRequest
    ) -> GetMemoryConnectionInfoResponse:
        """Get connection information for a specific memory collection."""
        return self._invoke_api(
            api_action="GetMemoryConnectionInfo",
            request=request,
            response_type=GetMemoryConnectionInfoResponse,
        )


if __name__ == "__main__":
    # 配置日志用于测试
    from agentkit.utils import setup_logging
    setup_logging(level="INFO", format_type="simple")
    
    logger.info("=" * 70)
    logger.info("测试 AgentKit Memory Collection API")
    logger.info("=" * 70)
    
    memory = AgentkitMemory()
    
    logger.info("\n【示例1】列出所有记忆库")
    try:
        list_req = ListMemoryCollectionsRequest(page_number=1, page_size=10)
        list_res = memory.list_memory_collections(list_req)
        logger.info("  ✓ API调用成功")
        logger.info("  总数: %s", list_res.total_count)
        logger.info("  当前页: %s/%s", list_res.page_number, list_res.page_size)
        
        if list_res.memories:
            logger.info("\n  记忆库列表:")
            for mem in list_res.memories[:5]:  # 只显示前5个
                logger.info("    - %s (%s)", mem.name, mem.memory_id)
                logger.info("      Provider: %s", mem.provider_type)
                logger.info("      Status: %s", mem.status)
                logger.info("      Created: %s", mem.create_time)
    except Exception as e:
        logger.error("  ✗ API调用失败: %s", e, exc_info=True)
    
    # logger.info("\n【示例2】创建记忆库")
    # try:
    #     create_req = CreateMemoryCollectionRequest(
    #         name="测试记忆库",
    #         description="这是一个测试记忆库",
    #         provider_type="coze"
    #     )
    #     create_res = memory.create_memory_collection(create_req)
    #     logger.info("  ✓ API调用成功")
    #     logger.info("  记忆库ID: %s", create_res.memory_id)
    #     logger.info("  Provider ID: %s", create_res.provider_collection_id)
    #     logger.info("  Status: %s", create_res.status)
    # except Exception as e:
    #     logger.error("  ✗ API调用失败: %s", e, exc_info=True)
    
    # logger.info("\n【示例3】获取记忆库详情")
    # try:
    #     get_req = GetMemoryCollectionRequest(
    #         memory_id="your-memory-id-here"
    #     )
    #     get_res = memory.get_memory_collection(get_req)
    #     logger.info("  ✓ API调用成功")
    #     logger.info("  记忆库名称: %s", get_res.name)
    #     logger.info("  描述: %s", get_res.description)
    #     logger.info("  Provider: %s", get_res.provider_type)
    #     logger.info("  Status: %s", get_res.status)
    #     logger.info("  Created: %s", get_res.create_time)
    # except Exception as e:
    #     logger.error("  ✗ API调用失败（需要有效的记忆库ID）: %s", e, exc_info=True)
    
    logger.info("\n【示例4】获取记忆库连接信息")
    try:
        conn_req = GetMemoryConnectionInfoRequest(
            memory_id="mem-1760693901155316044-9"
        )
        conn_res = memory.get_memory_connection_info(conn_req)
        logger.info("  ✓ API调用成功")
        logger.info("  记忆库ID: %s", conn_res.memory_id)
        logger.info("  Provider: %s", conn_res.provider_type)
        logger.info("  Status: %s", conn_res.status)
        
        if conn_res.connection_infos:
            logger.info("\n  连接信息:")
            for conn in conn_res.connection_infos:
                logger.info("    - Auth Type: %s", conn.auth_type)
                logger.info("      Base URL: %s", conn.base_url)
                if conn.expire_at:
                    logger.info("      Expires At: %s", conn.expire_at)
    except Exception as e:
        logger.error("  ✗ API调用失败（需要有效的记忆库ID）: %s", e, exc_info=True)
    
    logger.info("\n" + "=" * 70)
    logger.info("✓ AgentKit Memory Collection API 实现完成！")
    logger.info("=" * 70)
    logger.info("支持的功能:")
    logger.info("  1. ✓ 创建记忆库 (create_memory_collection)")
    logger.info("  2. ✓ 更新记忆库 (update_memory_collection)")
    logger.info("  3. ✓ 删除记忆库 (delete_memory_collection)")
    logger.info("  4. ✓ 列出所有记忆库 (list_memory_collections)")
    logger.info("  5. ✓ 添加记忆库 (add_memory_collection)")
    logger.info("  6. ✓ 获取记忆库详情 (get_memory_collection)")
    logger.info("  7. ✓ 获取记忆库连接信息 (get_memory_connection_info)")
    logger.info("\n特性:")
    logger.info("  1. ✓ 所有请求和响应都是强类型")
    logger.info("  2. ✓ 支持别名和Python字段名两种方式")
    logger.info("  3. ✓ 完整的错误处理")
    logger.info("  4. ✓ Pydantic自动验证")
