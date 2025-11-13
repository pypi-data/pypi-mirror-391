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

"""
Base client for AgentKit services.
Provides common initialization and API invocation logic.
"""

import json
from typing import Any, Dict, Type, TypeVar, TYPE_CHECKING, Union, Optional
from dataclasses import dataclass

from volcengine.ApiInfo import ApiInfo
from volcengine.base.Service import Service
from volcengine.Credentials import Credentials
from volcengine.ServiceInfo import ServiceInfo
from agentkit.utils.ve_sign import get_volc_ak_sk_region, get_volc_agentkit_host_info

if TYPE_CHECKING:
    from pydantic import BaseModel

T = TypeVar('T')


@dataclass
class ApiConfig:
    """Configuration for a single API endpoint."""
    action: str
    method: str = "POST"
    path: str = "/"
    form: Optional[Dict[str, Any]] = None
    header: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.form is None:
            self.form = {}
        if self.header is None:
            self.header = {}


class BaseAgentkitClient(Service):
    """
    Base client for all AgentKit services.
    
    This class provides:
    1. Common credential initialization
    2. Unified API invocation logic with error handling
    3. Automatic ApiInfo generation with flexible configuration
    
    Subclasses should override API_ACTIONS with either:
    - Simple dict mapping: {"ActionName": "ActionName"}
    - Detailed ApiConfig: {"ActionName": ApiConfig(action="ActionName", method="GET", path="/custom")}
    """
    
    # Subclasses should override this with their API action configurations
    API_ACTIONS: Dict[str, Union[str, ApiConfig]] = {}
    
    def __init__(
        self,
        access_key: str = "",
        secret_key: str = "",
        region: str = "",
        session_token: str = "",
        service_name: str = "",
    ) -> None:
        """
        Initialize the AgentKit client.
        
        Args:
            access_key: Volcengine access key
            secret_key: Volcengine secret key
            region: Volcengine region
            session_token: Optional session token
            service_name: Service name for logging (e.g., 'knowledge', 'memory')
        """
        # Validate and get credentials
        if not any([access_key, secret_key, region]):
            access_key, secret_key, region = get_volc_ak_sk_region('AGENTKIT')
        else:
            if not all([access_key, secret_key, region]):
                raise ValueError(
                    f"Error creating {service_name} instance: "
                    "missing access key, secret key or region"
                )
        
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.session_token = session_token
        
        # Get service configuration
        self.host, self.api_version, self.service = get_volc_agentkit_host_info()

        # Create ServiceInfo
        self.service_info = ServiceInfo(
            host=self.host,
            header={'Accept': 'application/json'},
            credentials=Credentials(
                ak=self.access_key,
                sk=self.secret_key,
                service=self.service,
                region=self.region,
                session_token=self.session_token,
            ),
            connection_timeout=5,
            socket_timeout=5,
            scheme="https",
        )
        
        # Generate ApiInfo for all actions
        self.api_info = self._build_api_info()
        
        # Initialize parent Service class
        super().__init__(service_info=self.service_info, api_info=self.api_info)
    
    def _build_api_info(self) -> Dict[str, ApiInfo]:
        """
        Build ApiInfo dictionary from API_ACTIONS.
        
        Supports two formats:
        1. Simple string: {"ListItems": "ListItems"} -> POST to / with Action query param
        2. ApiConfig: {"GetItem": ApiConfig(action="GetItem", method="GET", path="/items")}
        
        Returns:
            Dictionary mapping action names to ApiInfo objects
        """
        api_info = {}
        for action_key, action_config in self.API_ACTIONS.items():
            # If it's a simple string, use default POST configuration
            if isinstance(action_config, str):
                api_info[action_key] = ApiInfo(
                    method="POST",
                    path="/",
                    query={"Action": action_config, "Version": self.api_version},
                    form={},
                    header={},
                )
            # If it's an ApiConfig, use the detailed configuration
            elif isinstance(action_config, ApiConfig):
                api_info[action_key] = ApiInfo(
                    method=action_config.method,
                    path=action_config.path,
                    query={"Action": action_config.action, "Version": self.api_version},
                    form=action_config.form,
                    header=action_config.header,
                )
            else:
                raise ValueError(
                    f"Invalid API_ACTIONS configuration for '{action_key}': "
                    f"expected str or ApiConfig, got {type(action_config)}"
                )
        return api_info
    def _get(self, api_action: str, params: Dict[str, Any] = None) -> str:
        try:
            resp = self.get(api_action, params)
            return resp
        except Exception as e:
            raise Exception(f"Failed to {api_action}: {str(e)}")
    
    def _invoke_api(
        self,
        api_action: str,
        request: Any,
        response_type: Type[T],
        params: Dict[str, Any] = None,
    ) -> T:
        """
        Unified API invocation with error handling.
        
        Args:
            api_action: The API action name (e.g., 'ListKnowledgeBases')
            request: The request object (Pydantic model)
            response_type: The response type to parse into
            params: Additional query parameters
            
        Returns:
            Typed response object
            
        Raises:
            Exception: If API call fails or returns an error
        """
        # Make API call
        print(f"request action: {api_action}, body: {json.dumps(request.model_dump(by_alias=True, exclude_none=True))}")
        try:
            res = self.json(
                api=api_action,
                params=params or {},
                body=json.dumps(request.model_dump(by_alias=True, exclude_none=True))
            )
        except Exception as e:
            raise Exception(f"Failed to {api_action}: {str(e)}")
        
        if not res:
            raise Exception(f"Empty response from {api_action} request.")
        
        # Parse response
        response_data = json.loads(res)
        
        print("response_data:", response_data)
        # Check for errors
        metadata = response_data.get("ResponseMetadata", {})
        if metadata.get("Error"):
            error_msg = metadata.get("Error", {}).get("Message", "Unknown error")
            raise Exception(f"Failed to {api_action}: {error_msg}")
        
        # Return typed response
        # print(json.dumps(response_data, indent=2, ensure_ascii=False))
        return response_type(**response_data.get('Result', {}))
