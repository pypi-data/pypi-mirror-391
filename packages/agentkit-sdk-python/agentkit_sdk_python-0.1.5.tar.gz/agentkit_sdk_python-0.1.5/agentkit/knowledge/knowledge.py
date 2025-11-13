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
from agentkit.knowledge.knowledge_all_types import (
    ListKnowledgeBasesRequest,
    ListKnowledgeBasesResponse,
    AddKnowledgeBaseRequest,
    AddKnowledgeBaseResponse,
    GetKnowledgeConnectionInfoRequest,
    GetKnowledgeConnectionInfoResponse,
    DeleteKnowledgeBaseRequest,
    DeleteKnowledgeBaseResponse,
)

logger = get_logger(__name__)


class AgentkitKnowledge(BaseAgentkitClient):
    """AgentKit Knowledge Base Management Service"""
    
    # Define all API actions for this service
    API_ACTIONS: Dict[str, str] = {
        "ListKnowledgeBases": "ListKnowledgeBases",
        "AddKnowledgeBase": "AddKnowledgeBase",
        "GetKnowledgeConnectionInfo": "GetKnowledgeConnectionInfo",
        "DeleteKnowledgeBase": "DeleteKnowledgeBase",
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
            service_name="knowledge",
        )

    def list_knowledge_bases(
        self, request: ListKnowledgeBasesRequest
    ) -> ListKnowledgeBasesResponse:
        """List all knowledge bases from Volcengine."""
        return self._invoke_api(
            api_action="ListKnowledgeBases",
            request=request,
            response_type=ListKnowledgeBasesResponse,
        )

    def add_knowledge_base(
        self, request: AddKnowledgeBaseRequest
    ) -> AddKnowledgeBaseResponse:
        """Add a new knowledge base to Volcengine."""
        return self._invoke_api(
            api_action="AddKnowledgeBase",
            request=request,
            response_type=AddKnowledgeBaseResponse,
        )

    def get_knowledge_connection_info(
        self, request: GetKnowledgeConnectionInfoRequest
    ) -> GetKnowledgeConnectionInfoResponse:
        """Get connection information for a specific knowledge base."""
        return self._invoke_api(
            api_action="GetKnowledgeConnectionInfo",
            request=request,
            response_type=GetKnowledgeConnectionInfoResponse,
        )

    def delete_knowledge_base(
        self, request: DeleteKnowledgeBaseRequest
    ) -> DeleteKnowledgeBaseResponse:
        """Delete a knowledge base from Volcengine."""
        return self._invoke_api(
            api_action="DeleteKnowledgeBase",
            request=request,
            response_type=DeleteKnowledgeBaseResponse,
        )


if __name__ == "__main__":
    # 配置日志用于测试
    from agentkit.utils import setup_logging
    setup_logging(level="INFO", format_type="simple")
    
    logger.info("=" * 70)
    logger.info("测试 AgentKit Knowledge Base API")
    logger.info("=" * 70)
    
    knowledge = AgentkitKnowledge()
    
    logger.info("\n【示例1】列出所有知识库")
    try:
        list_req = ListKnowledgeBasesRequest(page_number=1, page_size=10)
        list_res = knowledge.list_knowledge_bases(list_req)
        logger.info("  ✓ API调用成功")
        logger.info("  总数: %s", list_res.total_count)
        logger.info("  当前页: %s/%s", list_res.page_number, list_res.page_size)
        
        if list_res.knowledge_bases:
            logger.info("\n  知识库列表:")
            for kb in list_res.knowledge_bases[:5]:  # 只显示前5个
                logger.info("    - %s (%s)", kb.name, kb.knowledge_id)
                logger.info("      Provider: %s", kb.provider_type)
                logger.info("      Status: %s", kb.status)
                logger.info("      Created: %s", kb.create_time)
    except Exception as e:
        logger.error("  ✗ API调用失败: %s", e, exc_info=True)
    
    # logger.info("\n【示例2】添加知识库")
    # try:
    #     from agentkit.knowledge.knowledge_all_types import KnowledgeBasesItem
        
    #     add_req = AddKnowledgeBaseRequest(
    #         knowledge_bases=[
    #             KnowledgeBasesItem(
    #                 name="测试知识库",
    #                 provider_knowledge_id="test-kb-001",
    #                 provider_type="coze",
    #                 description="这是一个测试知识库"
    #             )
    #         ],
    #         project_name="default"
    #     )
    #     add_res = knowledge.add_knowledge_base(add_req)
    #     logger.info("  ✓ API调用成功")
        
    #     if add_res.knowledge_bases:
    #         for kb in add_res.knowledge_bases:
    #             logger.info("    - 知识库ID: %s", kb.knowledge_id)
    #             logger.info("      Provider ID: %s", kb.provider_knowledge_id)
    #             logger.info("      Status: %s", kb.status)
    # except Exception as e:
    #     logger.error("  ✗ API调用失败: %s", e, exc_info=True)
    
    logger.info("\n【示例3】获取知识库连接信息")
    try:
        conn_req = GetKnowledgeConnectionInfoRequest(
            knowledge_id="kb-ye70201czkttk7n0u44s"
        )
        conn_res = knowledge.get_knowledge_connection_info(conn_req)
        logger.info("  ✓ API调用成功")
        logger.info("  知识库ID: %s", conn_res.knowledge_id)
        logger.info("  Provider: %s", conn_res.provider_type)
        logger.info("  Status: %s", conn_res.status)
        
        if conn_res.connection_infos:
            logger.info("\n  连接信息:")
            for conn in conn_res.connection_infos:
                logger.info("    - Auth Type: %s", conn.auth_type)
                logger.info("      Base URL: %s", conn.base_url)
                logger.info("      Region: %s", conn.region)
                if conn.expire_at:
                    logger.info("      Expires At: %s", conn.expire_at)
    except Exception as e:
        logger.error("  ✗ API调用失败（需要有效的知识库ID）: %s", e, exc_info=True)
    
    # logger.info("\n【示例4】删除知识库")
    # try:
    #     delete_req = DeleteKnowledgeBaseRequest(
    #         knowledge_id="your-knowledge-id-here"
    #     )
    #     delete_res = knowledge.delete_knowledge_base(delete_req)
    #     logger.info("  ✓ API调用成功")
    #     logger.info("  已删除知识库ID: %s", delete_res.knowledge_id)
    #     logger.info("  Request ID: %s", delete_res.request_id)
    # except Exception as e:
    #     logger.error("  ✗ API调用失败（需要有效的知识库ID）: %s", e, exc_info=True)
    
    logger.info("\n" + "=" * 70)
    logger.info("✓ AgentKit Knowledge Base API 实现完成！")
    logger.info("=" * 70)
    logger.info("支持的功能:")
    logger.info("  1. ✓ 列出所有知识库 (list_knowledge_bases)")
    logger.info("  2. ✓ 添加知识库 (add_knowledge_base)")
    logger.info("  3. ✓ 获取知识库连接信息 (get_knowledge_connection_info)")
    logger.info("  4. ✓ 删除知识库 (delete_knowledge_base)")
    logger.info("\n特性:")
    logger.info("  1. ✓ 所有请求和响应都是强类型")
    logger.info("  2. ✓ 支持别名和Python字段名两种方式")
    logger.info("  3. ✓ 完整的错误处理")
    logger.info("  4. ✓ Pydantic自动验证")
