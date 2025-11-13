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

# 导入自动生成的类型
from agentkit.tools.tools_all_types import (
    CreateToolRequest,
    CreateToolResponse,
    GetToolRequest,
    GetToolResponse,
    UpdateToolRequest,
    UpdateToolResponse,
    DeleteToolRequest,
    DeleteToolResponse,
    ListToolsRequest,
    ListToolsResponse,
)


class AgentkitTools(BaseAgentkitClient):
    """AgentKit Tools Management Service"""
    
    # Define all API actions for this service
    API_ACTIONS: Dict[str, str] = {
        "CreateTool": "CreateTool",
        "GetTool": "GetTool",
        "UpdateTool": "UpdateTool",
        "DeleteTool": "DeleteTool",
        "ListTools": "ListTools",
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
            service_name="tools",
        )

    def create(self, request: CreateToolRequest) -> CreateToolResponse:
        """Create a new Tool on Volcengine."""
        return self._invoke_api(
            api_action="CreateTool",
            request=request,
            response_type=CreateToolResponse,
        )

    def get(self, request: GetToolRequest) -> GetToolResponse:
        """Get details of a specific Tool from Volcengine."""
        return self._invoke_api(
            api_action="GetTool",
            request=request,
            response_type=GetToolResponse,
        )

    def update(self, request: UpdateToolRequest) -> UpdateToolResponse:
        """Update an existing Tool on Volcengine."""
        return self._invoke_api(
            api_action="UpdateTool",
            request=request,
            response_type=UpdateToolResponse,
        )

    def delete(self, request: DeleteToolRequest) -> DeleteToolResponse:
        """Delete a Tool on Volcengine."""
        return self._invoke_api(
            api_action="DeleteTool",
            request=request,
            response_type=DeleteToolResponse,
        )

    def list(self, request: ListToolsRequest) -> ListToolsResponse:
        """List all Tools from Volcengine."""
        return self._invoke_api(
            api_action="ListTools",
            request=request,
            response_type=ListToolsResponse,
        )


if __name__ == "__main__":
    tool = AgentkitTools()
    list_res = tool.list(ListToolsRequest())
    for tool in list_res.tools:
        print(tool)
