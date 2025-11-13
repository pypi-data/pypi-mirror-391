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
from typing import Dict

from agentkit.client import BaseAgentkitClient
from agentkit.utils import get_logger

from agentkit.runtime.types import (
    CreateAgentkitRuntimeRequest,
    CreateAgentkitRuntimeResponse,
)

# 导入自动生成的类型（强类型版本）
from agentkit.runtime.runtime_all_types import (
    GetAgentKitRuntimeRequest,
    GetAgentKitRuntimeResponse,
    ListAgentKitRuntimesRequest,
    ListAgentKitRuntimesResponse,
    UpdateAgentKitRuntimeRequest,
    UpdateAgentKitRuntimeResponse,
    DeleteAgentKitRuntimeRequest,
    DeleteAgentKitRuntimeResponse,
    ReleaseAgentKitRuntimeRequest,
    ReleaseAgentKitRuntimeResponse,
    GetAgentKitRuntimeVersionRequest,
    GetAgentKitRuntimeVersionResponse,
    ListAgentKitRuntimeVersionsRequest,
    ListAgentKitRuntimeVersionsResponse,
    GetAgentKitRuntimeCozeTokenRequest,
    GetAgentKitRuntimeCozeTokenResponse,
)

logger = get_logger(__name__)


class AgentkitRuntime(BaseAgentkitClient):
    """AgentKit Runtime Management Service"""
    
    # Define all API actions for this service
    API_ACTIONS: Dict[str, str] = {
        "CreateAgentKitRuntime": "CreateRuntime",
        "GetAgentKitRuntime": "GetRuntime",
        "UpdateAgentKitRuntime": "UpdateRuntime",
        "DeleteAgentKitRuntime": "DeleteRuntime",
        "ListAgentKitRuntimes": "ListRuntimes",
        "ReleaseAgentKitRuntime": "ReleaseRuntime",
        "GetAgentKitRuntimeVersion": "GetRuntimeVersion",
        "ListAgentKitRuntimeVersions": "ListRuntimeVersions",
        "GetAgentKitRuntimeCozeToken": "GetRuntimeCozeToken",
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
            service_name="runtime",
        )

    def create(
        self, request: CreateAgentkitRuntimeRequest, params: dict
    ) -> CreateAgentkitRuntimeResponse:
        """Create a new AgentKit Runtime on Volcengine."""
        res = self.json(
            api="CreateAgentKitRuntime", params=params, body=request.model_dump()
        )
        if not res:
            raise Exception("Empty response from create agentkit runtime request.")

        response_data = json.loads(res)
        return CreateAgentkitRuntimeResponse(**response_data.get('Result', {}))

    def get(self, request: GetAgentKitRuntimeRequest) -> GetAgentKitRuntimeResponse:
        """Get details of a specific AgentKit Runtime from Volcengine."""
        logger.debug("Get runtime request: %s", json.dumps(request.model_dump(by_alias=True)))
        try:
            resp = self._invoke_api(
                api_action="GetAgentKitRuntime",
                request=request,
                response_type=GetAgentKitRuntimeResponse,
            )
        except Exception as e:
            if "InvalidAgentKitRuntime.NotFound" in str(e):
                return None
            raise Exception(f"Failed to get agentkit runtime: {str(e)}")
        return resp

    def update(
        self, request: UpdateAgentKitRuntimeRequest
    ) -> UpdateAgentKitRuntimeResponse:
        """Update an existing AgentKit Runtime on Volcengine."""
        logger.debug("Update runtime request: %s", json.dumps(request.model_dump(by_alias=True, exclude_none=True)))
        return self._invoke_api(
            api_action="UpdateAgentKitRuntime",
            request=request,
            response_type=UpdateAgentKitRuntimeResponse,
        )

    def delete(
        self, request: DeleteAgentKitRuntimeRequest
    ) -> DeleteAgentKitRuntimeResponse:
        """Delete an AgentKit Runtime on Volcengine."""
        return self._invoke_api(
            api_action="DeleteAgentKitRuntime",
            request=request,
            response_type=DeleteAgentKitRuntimeResponse,
        )

    def list(
        self, request: ListAgentKitRuntimesRequest
    ) -> ListAgentKitRuntimesResponse:
        """List all AgentKit Runtimes from Volcengine."""
        return self._invoke_api(
            api_action="ListAgentKitRuntimes",
            request=request,
            response_type=ListAgentKitRuntimesResponse,
        )

    def release(
        self, request: ReleaseAgentKitRuntimeRequest
    ) -> ReleaseAgentKitRuntimeResponse:
        """Release an AgentKit Runtime on Volcengine."""
        return self._invoke_api(
            api_action="ReleaseAgentKitRuntime",
            request=request,
            response_type=ReleaseAgentKitRuntimeResponse,
        )

    def get_version(
        self, request: GetAgentKitRuntimeVersionRequest
    ) -> GetAgentKitRuntimeVersionResponse:
        """Get the version of a specific AgentKit Runtime."""
        return self._invoke_api(
            api_action="GetAgentKitRuntimeVersion",
            request=request,
            response_type=GetAgentKitRuntimeVersionResponse,
        )

    def list_versions(
        self, request: ListAgentKitRuntimeVersionsRequest
    ) -> ListAgentKitRuntimeVersionsResponse:
        """List all versions of a specific AgentKit Runtime."""
        return self._invoke_api(
            api_action="ListAgentKitRuntimeVersions",
            request=request,
            response_type=ListAgentKitRuntimeVersionsResponse,
        )

    def get_coze_token(
        self, request: GetAgentKitRuntimeCozeTokenRequest
    ) -> GetAgentKitRuntimeCozeTokenResponse:
        """Get Coze JWT token for a specific AgentKit Runtime."""
        return self._invoke_api(
            api_action="GetAgentKitRuntimeCozeToken",
            request=request,
            response_type=GetAgentKitRuntimeCozeTokenResponse,
        )

